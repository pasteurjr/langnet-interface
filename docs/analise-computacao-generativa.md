# Análise: Computação Generativa aplicada ao LangNet-Interface

## Documentos Analisados
- `docs/content.pdf` - Artigo IBM sobre Computação Generativa (David Cox, Ruchir Puri)
- `docs/ComputacaoGenerativa.md` - Framework operacional com 16 princípios
- `docs/cgrequisitos.md` - Roteiro para geração de requisitos
- `docs/cgespec.md` - Roteiro para geração de especificações

---

## Compreensão do Conceito

### Origem (IBM Research)

**Computação Generativa** = tratar LLMs como **primitivas de programação**, não como oráculos/chatbots.

> "Engenharia de prompts não é engenharia. É brincadeira." - David Cox

> "Uma vírgula pode alterar a produção. Não se pode gerir empresa assim." - Ruchir Puri

### Problema que Resolve

- Respostas imprevisíveis
- Alucinações sem controle
- Impossibilidade de auditar/testar comportamento
- Confiança cega no "oráculo"

### Solução: Runtime de Orquestração

Em vez de 1 prompt longo → 1 resposta, usar:
- **20 prompts atômicos** com schema fixo
- **Validação em cada step**
- **Retry com estratégias diferentes**
- **Modelo guardião** que verifica saída
- **Fallback determinístico**
- **Logs completos**

---

## Os 16 Princípios do Framework

### Regra #1 (Fundamental)

**Nunca permitir que LLM responda diretamente ao usuário em única chamada.**

### 5 Camadas Obrigatórias

1. **Runtime de Orquestração** - controla fluxo, retries, fallback
2. **Agentes Especialistas** - cada um executa UMA função
3. **Guardrails/Guardiões** - validam factualidade e conformidade
4. **Ferramentas Determinísticas** - RAG, banco, regras (não "memória" do LLM)
5. **Observabilidade** - logs, testes comportamentais, versionamento

### 7 Agentes Obrigatórios

1. **RouterAgent** - classifica intenção
2. **EntityExtractorAgent** - extrai entidades
3. **RetrieverAgent** - RAG/banco
4. **ComposerAgent** - gera rascunho COM contexto
5. **VerifierAgent** - valida grounding
6. **ComplianceAgent** - verifica políticas
7. **FormatterAgent** - normaliza + fallback

### Pipeline Canônico (9 steps)

```
Classificar → Extrair → Recuperar → Compor → Verificar → Reparar → Compliance → Formatar → Entregar
```

### Princípios Finais

- O runtime manda, o LLM obedece
- Precisão vem de controle, não de criatividade
- LLMs erram; sistemas corrigem
- Engenharia > prompt engineering
- Todo comportamento deve ser auditável
- Nenhuma resposta sem validação

---

## Como Introduzir no LangNet-Interface

### Estado Atual (Violação do Princípio #1)

`specification.py` faz UMA chamada LLM com prompt gigante → viola princípio fundamental.

Resultado: truncamento, seções faltantes, sem rastreabilidade.

### Refatoração Proposta

**1. Criar módulo `backend/orchestrator/`**:

```
orchestrator/
├── runtime.py          # Sequência de steps
├── agents/
│   ├── router.py       # Classifica: criar/atualizar/validar
│   ├── extractor.py    # Extrai entidades do requisito
│   ├── retriever.py    # RAG sobre requisitos/docs
│   ├── composer.py     # Gera rascunho por seção
│   ├── verifier.py     # Valida grounding (context_ids)
│   ├── compliance.py   # Idioma, 1ª pessoa, políticas
│   └── formatter.py    # Template final + fallback
├── schemas/            # JSON schemas para cada step
└── validators/         # Validadores de formato/grounding
```

**2. Fluxo para Especificação**:

```
Input: documento de requisitos

Step 1: RouterAgent → {intent: "create", scope: "functional_spec"}
Step 2: EntityExtractorAgent → {actors: [...], systems: [...], use_cases: [...]}
Step 3: RetrieverAgent → {context_chunks: [{id, source, quote}...]}
Step 4: ComposerAgent → {sections: [...], cada item com context_ids}
Step 5: VerifierAgent → {issues: [{unsupported: [...], ambiguous: [...]}]}
Step 6: ComplianceAgent → {compliance_ok: true, violations: [], language: "pt-BR"}
Step 7: FormatterAgent → {status: "complete", document: "...", gaps: []}

Output: Especificação rastreável
```

**3. Benefícios**:

- Nenhuma seção truncada (cada step é pequeno)
- Rastreabilidade (cada item aponta para context_id)
- Retry diferenciado por tentativa
- Fallback com versão parcial + lista de lacunas
- Observabilidade total via Langfuse

---

## Conclusão

A Computação Generativa transforma LLMs de "oráculos imprevisíveis" em "funções programáveis". O LangNet-Interface pode adotar esse paradigma refatorando os pipelines de geração de documentos para usar múltiplos steps atômicos com validação, em vez de chamadas únicas com prompts gigantes.
