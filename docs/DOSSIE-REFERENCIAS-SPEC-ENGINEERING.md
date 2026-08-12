# Dossiê — Referências do artigo "Specification Engineering" (leitura profunda)

**Compilado por:** Claude · **Data:** 2026-08-12
**Origem:** links citados em *"Specification Engineering: The New Skill After Prompt Engineering"* (KDnuggets, ago/2026)
**Objetivo:** resumir a fundo cada referência (com números) para embasar a Especificação v3 do pipeline do LangNet.

---

## Grupo 1 — A qualidade do requisito/processo importa mais que o truque

### 1. ROPE — *"What Should We Engineer in Prompts? Training Humans in Requirement-Driven LLM Use"*
`arxiv 2409.08775` · Qianou Ma et al. (CMU), TOCHI 2025.
- **Problema:** o ensino de prompt engineering foca em truques automatizáveis (role-play, "pense passo a passo") e negligencia **articular requisitos claros e completos**.
- **ROPE (Requirement-Oriented Prompt Engineering):** treina o humano a **gerar requisitos bem definidos**, não a otimizar redação.
- **Método:** RCT com **30 novatos**; prática deliberada + feedback gerado por LLM; tarefas como "chatbot conselheiro de viagem" exigindo specs ("comece com um TL;DR").
- **Resultados:** ROPE **+20%** vs **+1%** do treino convencional; **otimização automática de prompt NÃO fecha a diferença**; **correlação direta** entre qualidade do requisito e qualidade da saída.
- **Conclusão:** o gargalo é a articulação do requisito, não o prompt.

### 2. Google **DORA 2025**
`cloud.google.com/blog/.../announcing-the-2025-dora-report`
- **Escopo:** ~**5.000** profissionais + 100h qualitativas (23/09/2025).
- **Tese:** **IA é amplificador** — amplia forças e fraquezas existentes; não conserta times.
- **Números:** **90%** usam IA; **80%+** creem em ganho de produtividade; **~30% desconfiam** do código gerado. Relação **positiva** com throughput e desempenho de produto, **negativa** com **estabilidade** de entrega (acelera e expõe fraquezas sem salvaguardas).
- **Capacidades que fazem a IA render:** políticas claras, **conectar IA ao contexto interno**, práticas fundamentais, **redes de segurança** (testes automatizados, versionamento, feedback rápido), plataforma interna de qualidade, foco no usuário. **90%** têm alguma plataforma.
- **Frase-chave:** "IA não elimina a disciplina de engenharia — **aumenta o retorno** de tê-la."

---

## Grupo 2 — Formato de saída como CONTRATO

### 3. OpenAI **Structured Outputs**
`developers.openai.com/api/docs/guides/structured-outputs`
- **O que é:** garante que a saída **sempre obedece a um JSON Schema** — "sem se preocupar com o modelo omitir chave obrigatória ou alucinar enum inválido".
- **Diferenças:** vs **JSON mode** (só JSON sintático) → garante **conformidade com o schema**; vs **function calling** (liga a ferramentas) → aqui estrutura a **resposta**.
- **Regras do schema:** todos os campos `required`; `additionalProperties:false` obrigatório; sem `allOf/not/if-then-else`; suporta tipos básicos, `enum`, `pattern`, formatos, `anyOf`, `$ref/$defs`, aninhamento ≤10 níveis/5000 props; ≤1000 enums.
- **Campo `refusal`:** recusa por segurança vem em campo próprio, **detectável programaticamente**.
- **Boas práticas:** nomear chaves claramente; usar Pydantic/Zod; em erro, ajustar instruções, dar exemplos ou **decompor a tarefa**.

---

## Grupo 3 — Especificar o COMPORTAMENTO do modelo (normas Anthropic/OpenAI)

### 4. **OpenAI Model Spec** (2025-12-18)
`model-spec.openai.com/2025-12-18.html` (público, CC0)
- **Cadeia de comando (hierarquia de autoridade):** **Root** (regras invioláveis do Spec) > **System** (OpenAI) > **Developer** > **User** > **Guideline**. Nível maior sobrepõe o menor.
- **Estrutura:** *Rules* (nunca sobrepostas) · *Defaults* (sobrepostos explicitamente) · *Guidelines* (sobrepostos por contexto).
- **Anti prompt-injection:** conteúdo não-confiável (texto citado, saída de ferramenta, imagens) **não tem autoridade** salvo delegação superior; "IGNORE TODAS AS INSTRUÇÕES" do usuário é **dado**, não override.
- **Regras notáveis:** respeitar "letra e espírito"; **sem objetivos próprios**; **agir dentro do escopo de autonomia** (com "shutdown timer"); **minimizar efeitos colaterais irreversíveis** (deleções, gastos, credenciais) e comunicar risco antes; **exceção de transformação**; buscar a verdade sem "agenda"; **evitar bajulação**.
- **Relevância:** é *specification engineering* no nível do **comportamento do modelo**.

### 5. **Anthropic Constitutional AI / Constitution**
`anthropic.com/constitution`
- **O que é:** treinar via **constituição escrita** (princípios), não só feedback humano.
- **2 fases:** (1) fine-tuning supervisionado alinhado; (2) **RLAIF** — um avaliador de IA julga as respostas **contra a constituição** (escala a supervisão).
- **4 valores priorizados:** *Broadly Safe* > *Broadly Ethical* > *Compliant* > *Genuinely Helpful*.
- **Valores específicos:** honestidade acima do padrão humano (nem "mentiras brancas"); ponderar custo/benefício do dano (reversibilidade, alcance, consentimento); respeitar autonomia.
- **Hard constraints:** nunca dar "uplift" a bioarma; nunca CSAM.
- **Filosofia:** cultivar **julgamento** > regras rígidas — "o Claude poderia derivar as próprias regras"; valores + sabedoria **generalizam** melhor.

> **Comum (4+5):** OpenAI (regras/hierarquia) e Anthropic (princípios/julgamento) — duas filosofias de **especificação de comportamento**; ambas trocam "ajustar prompt" por "**definir o correto**".

---

## Grupo 4 — Teste/verificação como especificação de correção

### 6. **SWE-bench** (`swebench.com`)
- Benchmark: agentes resolvendo **issues reais do GitHub** editando o codebase; acerto = **testes do repositório**. Variantes: original/Lite/Verified/Multimodal/Multilingual.

### 7. **OpenAI SWE-bench Verified** (`openai.com/index/introducing-swe-bench-verified/`)
- Subconjunto **humano-validado** de **500** problemas; especialistas revisaram **1.699** (3 por problema).
- **Diagnóstico:** **38,3%** com **enunciado sub-especificado**; **61,1%** com **testes que rejeitariam soluções válidas**.
- **Reviravolta (2026):** a OpenAI **parou de reportá-lo** — auditoria: **59,4%** dos difíceis não-resolvidos tinham **testes falhos**; **35,5%** exigiam detalhes de implementação nunca mencionados; **18,8%** testavam funcionalidade **não especificada**. *(Até o benchmark de referência sofria de má especificação.)*

### 8. **SWT-Bench** (`swtbench.com`)
- Mede **gerar testes que reproduzem** a issue (Fail-to-Pass), sem ver o patch.
- **Achado:** testes gerados = **filtro de verificação** → **dobram a precisão** do SWE-Agent. Topo ~**87%** vs baseline **15,9%**.

### 9. *"Are 'Solved Issues' in SWE-bench Really Solved Correctly?"* (`arxiv 2503.15223`)
- **PatchDiff** (testes diferenciais via LLM) vs patches humanos: **29,6%** dos "plausíveis" **divergem de comportamento**; **28,6%** dos suspeitos **certamente incorretos**; inflação **~6,2–6,4 p.p.**
- **Tese:** **testes são especificação incompleta** — "passou ≠ correto" (*specification gaming* medido).

---

## Grupo 5 — Decompor em passos discretos

### 10. **OpenAI — A Practical Guide to Building AI Agents** (guia, 34 pág.)
- **Componentes:** modelo + ferramentas + instruções.
- **Instruções:** aproveitar docs/SOPs; **quebrar tarefas densas em passos menores**; definir ações claras; capturar edge cases → "reduz ambiguidade e ajuda o modelo a seguir".
- **Guardrails:** em toda etapa (filtro de entrada, uso de ferramenta, **human-in-the-loop**).
- **Orquestração:** single-agent vs multi-agent (manager vs descentralizado).

---

## Síntese — o fio condutor
A alavanca de qualidade migrou do **"como pedir" (prompt)** para o **"como definir/verificar" (especificação)**:
- **ROPE + DORA:** qualidade vem do **requisito/processo**; a IA **amplifica** o que já existe.
- **Structured Outputs:** **formato de saída vira contrato**.
- **Model Spec + Constitution:** o **comportamento do modelo** é definido por **documento-especificação** (regras vs princípios).
- **SWE-bench / Verified / SWT-Bench / PatchDiff:** **testes especificam correção** — mas testes fracos/sobre-especificados enganam ("passou ≠ correto"); a OpenAI **aposentou** o Verified por isso.
- **Practical Guide:** operacionaliza — **decompor** + **guardrails** + ferramentas claras.

## Fontes
- ROPE — https://arxiv.org/abs/2409.08775
- DORA 2025 — https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
- Structured Outputs — https://developers.openai.com/api/docs/guides/structured-outputs
- Model Spec — https://model-spec.openai.com/2025-12-18.html
- Anthropic Constitution — https://www.anthropic.com/constitution
- SWE-bench — https://www.swebench.com/
- SWE-bench Verified — https://openai.com/index/introducing-swe-bench-verified/ · deprecação: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- SWT-Bench — https://swtbench.com/
- "Are Solved Issues Really Solved" — https://arxiv.org/html/2503.15223v1
- Practical Guide to Building Agents — https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
