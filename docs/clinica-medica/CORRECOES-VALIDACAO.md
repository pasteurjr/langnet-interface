# Correções encontradas na validação do ciclo completo (ClinIA)

> Este arquivo registra os **bugs do LangNet encontrados e corrigidos** durante a validação
> ponta a ponta (projeto de teste: Clínica Médica com triagem por agentes). Cada correção segue
> a regra: **commit+push de checkpoint ANTES** (com data/hora) → correção → commit da correção.
> Alimenta o relatório final.

---

## Bug #1 — Requisitos concluíam com documento VAZIO

**Etapa:** Requisitos (`generate_document`)
**Sintoma:** a geração rodava por ~18 min, o modelo local (qwen2.5-coder-32b) produzia um
documento de requisitos rico e específico da clínica (31 FRs, 17 NFRs, 9 BRs — visíveis no log),
mas o documento **salvo no banco tinha tamanho 0** e a etapa ficava presa em HTTP 404
("Requirements document not yet generated"), travando todo o pipeline logo na 1ª etapa.

**Causa raiz:** `generate_document_output_func` (backend/agents/langnetagents.py). O CrewAI devolve
o resultado embrulhado em `team_result` como uma **string JSON**. Ao serializar um markdown grande
como valor de string JSON, o modelo local não escapa perfeitamente (aspas e quebras de linha
literais, às vezes truncamento). O `json.loads` do JSON aninhado falhava e o regex de fallback
tentava `json.loads('"'+trecho+'"')`, que também falhava por causa de newline literal → resultado
**vazio**. O conteúdo existia, mas o parser não o recuperava.

**Correção:** novo `_extract_md_field_lenient()` — um extrator char-a-char que:
- localiza a chave `requirements_document_md` (aceita a chave escapada `\"...\"` do envelope);
- lê o valor tolerando **aspas não escapadas** no conteúdo (só encerra em `"` seguido de `,`/`}`),
  **newlines literais** e **truncamento** (lê até o fim se o JSON não fechar);
- desescapa `\n \t \r \" \\ \uXXXX`.
Fluxo novo: parse limpo → extrator leniente(team_result) → extrator leniente(output_json) →
dump do raw em `failed_generate_document_raw.txt` para diagnóstico se ainda vazio.
Testado em 4 casos (bem-formado / aspas não escapadas / newline literal+truncado / chave escapada).

**Commits:**
- `CHECKPOINT 2026-08-03 14:47 — ANTES de: corrigir extração de requirements_document_md`
- `FIX Requisitos: extrator leniente p/ requirements_document_md (team_result malformado)`

**Verificação (✅ CONFIRMADA):** re-execução do pipeline (projeto `a3ae2f89`, sessão de requisitos
`e160540b`) com o backend recarregado — `FINAL requirements_doc_md length: 67599` (antes: **0**),
driver: `REQUISITOS OK, 67775 chars`, artefato `01-requisitos.md` = 70 KB salvo, sem dump de falha.
A etapa que travava o pipeline inteiro na origem agora conclui e o chain seguiu automaticamente
para a Especificação.

---

## Achado #2 — Backend fica sem resposta durante geração pesada (event loop bloqueado)

**Etapa:** transição Especificação → Modelo de Dados
**Sintoma:** logo após a Especificação concluir (120 KB), o `POST /data-model/{pid}/generate` deu
**read timeout (60s)** e o driver abortou o chain. Segundos depois o backend voltou a responder
normalmente (200 em ~0,1s) — ou seja, **hang transitório**, não permanente.

**Causa provável:** as chamadas ao LLM local dentro das tasks assíncronas rodam de forma
**bloqueante** no event loop do FastAPI; enquanto uma geração longa está em curso, outras requisições
podem esperar além de 60s. Diferente do hang de pool já corrigido (aquele era esgotamento de conexão;
este é bloqueio de event loop).

**Ação (2 níveis):**
- **Imediata (resiliência do driver):** o driver de geração passará a **repetir POSTs com timeout maior
  e retry** em vez de abortar na 1ª leitura estourada — assim uma janela de backend ocupado não mata o
  ciclo. (Correção operacional, não altera o LangNet.)
- **Recomendação (LangNet, maior):** rodar as chamadas de LLM em thread pool (`run_in_executor`) para
  não bloquear o event loop — registrado como recomendação; mudança arquitetural com risco de
  regressão, a fazer com teste dedicado (não aplicada no meio desta validação para não desestabilizar).

---

## Bug #3 — Refino da Especificação estoura o contexto do modelo local (refino falha silencioso)

**Etapa:** Especificação → `POST /api/specifications/{sid}/refine`
**Sintoma:** ao enviar a rodada 1 de refino de interface (instruções de 3 KB), o refino foi aceito
(HTTP 200, assíncrono) mas **nunca gerou a v2**. No log:
`[SPEC REFINEMENT] Prompt built: 169660 chars` →
`openai.BadRequestError: 400 - n_keep: 41264 >= n_ctx: 40960 ("provide a shorter input")`.

**Causa raiz:** `execute_specification_refinement` (specification.py) monta o prompt com **a
especificação inteira (120 KB) + requisitos (até 45 KB) + histórico + instruções ≈ 41.264 tokens**,
acima do contexto de **40.960 tokens** do qwen local. Mesmo sem os requisitos, um doc de 120 KB
(~30 K tokens de entrada) mais a saída do doc inteiro (~30 K tokens) não cabe num contexto de 40 K —
**refino de documento inteiro numa tacada é fisicamente impossível no modelo local** para specs
grandes. (Limitação já conhecida, agora batida com doc maior.)

**Correção:** refino **por seção/UC (chunked)** dentro do endpoint. Quando a spec é grande, em vez de
uma chamada gigante: (1) divide o documento por seções `## N.` e a seção de Casos de Uso por blocos
`**UC-`; (2) refina **apenas as unidades relevantes à interface** (as que contêm "Wireframe" ou a
seção "Interfaces do Sistema"), passando o resto **inalterado**; (3) cada chamada leva só aquele
trecho + as instruções (cabe folgado no contexto); (4) se um trecho refinado vier suspeito
(curto/perdeu cabeçalho), mantém o original; (5) remonta o documento na ordem e salva como nova versão.

**Commits:**
- `CHECKPOINT 2026-08-03 21:40 — ANTES de: corrigir refino da Especificação p/ caber no contexto`
- `FIX Especificação: refino por seção/UC (chunked) p/ caber no contexto do modelo local`

**Verificação (✅ CONFIRMADA):** reenviada a rodada 1 de refino de interface com o backend recarregado.
Log: `Spec grande (120126 > 55000) → refino CHUNKED`, `33 unidades, 19 refináveis`, **sem
BadRequestError**. Resultado: **v2 criada** (725s, 19/19 unidades refinadas, 0 suspeitas). Wireframes
melhoraram: UC-013 (CRUD) ganhou tabela+busca+ações por linha+formulário; UC-002 (agêntica) ganhou
Entrada→Ação de IA→Resultado do agente+Encaminhar. Detalhes em `ANALISE-INTERFACE-SPEC.md`.

---
