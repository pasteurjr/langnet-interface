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
