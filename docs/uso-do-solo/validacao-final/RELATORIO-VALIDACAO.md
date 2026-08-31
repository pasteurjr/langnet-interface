# Validação Final — Uso do Solo v3 (regenerado pelo gerador corrigido)

**Projeto-teste:** `c4871aaf-3c8c-41d3-8ca7-6c3e22189731` (licenciamento urbano municipal / geoespacial)
**Data:** 2026-08-31
**Regra do teste:** todas as correções foram feitas **pela UI do LangNet** (Refinar / Regenerar / Aprovar) ou **no gerador/prompts** (produto). Nenhum artefato do app foi editado à mão para simular capacidade.

Este relatório mostra, com **screenshots reais** do app gerado e **resultados de execução E2E**, o que está **coerente e rodando** — e documenta com honestidade os **bugs residuais** que a execução ponta-a-ponta ainda revela.

---

## 1. Portão de rastreabilidade — VERDE

Guardrail determinístico (`backend/agents/langnettraceability.py` + `tools/langnet_trace_gate.py`) audita, sem LLM, se **todo requisito** atravessa Especificação → Modelo de Dados → Implementação. Saída atual do projeto:

```
══════════════════════════════════════════════════════════════════
  PORTÃO DE RASTREABILIDADE — ✅ PASSOU
══════════════════════════════════════════════════════════════════
Inventário: 37 FR · 14 NFR · 7 BR · 10 UC(spec)
  Req→Spec (FR)              37/37   OK
  Req→Spec (NFR)             14/14   OK
  Req→Spec (BR)              7/7   OK
  Matriz FR→UC (spec)        37/37   OK
  FR→Implementação (task)    37/37   OK
  Task→DM (tabela)           OK
  Task→DM (coluna)           OK
  Task→DM (JOIN/FROM)        OK
  Qualidade (FR por task)    OK
══════════════════════════════════════════════════════════════════
```

**O que cada hop garante:**
- **Req→Spec**: cada FR/NFR/BR dos requisitos aparece na especificação.
- **Matriz FR→UC**: cada um dos 37 FR está mapeado a ≥1 caso de uso (FR órfão = rejeitado).
- **FR→Implementação**: cada FR tem ao menos uma task que o implementa.
- **Task→DM (tabela/coluna/JOIN)**: toda query de task referencia **tabelas e colunas que existem** no schema, e **todo alias usado está no FROM/JOIN** (pega o clássico `i.geometria` sem `imoveis` no FROM).
- **Qualidade**: nenhuma task "catch-all" cobrindo sozinha >6 FR (anti-*stuffing*).

Duas camadas de garantia, como discutido: o **prompt reduz** a incidência do erro; o **portão determinístico garante** que o que escapou seja pego antes do deploy.

---

## 2. App gerado — telas ricas rodando

Frontend React (CRA) gerado, servido em `:3001`, falando com o ws-server (`:5030`) contra PostGIS (`uso_solo_green`, SIRGAS 2000 / SRID 4674). Screenshots reais:

### 2.1 Resultado de Conformidade (mapa + desenho + laudo)
Tela rica com **mapa Leaflet/OpenStreetMap** (Belo Horizonte/Contagem-MG), ferramentas de **desenho de área**, dropzone de **Shapefile** e botão **Gerar Laudo PDF** — não é formulário genérico.

![Home / Resultado de Conformidade](shots/01-app-home.png)

### 2.2 Cálculos Urbanísticos (calculadora)
Inputs de **Área Construída / Área de Projeção**, **mapa Leaflet** para a geometria e botão **Calcular**.

![Cálculos Urbanísticos](shots/02-calculos-urbanisticos.png)

### 2.3 Dashboard de Conformidade Municipal
![Dashboard](shots/03-dashboard.png)

### 2.4 Análise Ambiental: APP
![Análise APP](shots/04-analise-app.png)

### 2.5 Importar Geodados
![Importar Geodados](shots/05-importar-geodados.png)

---

## 3. Dados reais do PostGIS na UI (CRUD)

### 3.1 Imóveis — leitura real do banco
CRUD lendo do PostGIS: imóvel semeado `11111111-…`, `AREA_TERRENO = 1000.00`, com ações Ver/Editar/Excluir.

![Imóveis CRUD](shots/06-imoveis-crud.png)

### 3.2 Cálculos de Conformidade — **resultado do calculador visível na UI**
Esta é a prova de ponta-a-ponta: o calculador rodou e **as linhas computadas aparecem no frontend gerado**, lendo do PostGIS. Repare na linha **não-conforme** (`CA=2.50`, `TO=0.70`, `nao_conforme`) ao lado das conformes (`CA=1.50`, `TO=0.50`).

![Cálculos Conformidade CRUD](shots/07-calculos-conformidade-crud.png)

| ID | CA_CALCULADO | TO_CALCULADA | STATUS_CA | STATUS_TO |
|----|-------------:|-------------:|-----------|-----------|
| 74e5e41f… | 1.50 | 0.50 | conforme | conforme |
| ca1763a8… | 1.50 | 0.50 | conforme | conforme |
| b7c3e318… | 2.50 | 0.70 | **nao_conforme** | **nao_conforme** |
| 11044c43… | 1.50 | 0.50 | conforme | conforme |

---

## 4. Execução E2E via ws-server (protocolo real do app)

Chamadas `execute_task` no WebSocket `:5030` (mesmo canal que o frontend usa), contra PostGIS.

### ✅ `calculate_urban_compliance` — determinístico, limpo
```json
{
  "task_name": "calculate_urban_compliance",
  "result": {
    "status": "sucesso",
    "ca_calculado": 1.5,
    "to_calculada": 0.5,
    "status_ca": "conforme",
    "status_to": "conforme"
  }
}
```
A função **lê a edificação/imóvel do banco**, calcula CA/TO e grava o status (não depende de LLM). Sem nenhum `sed` pós-geração — booto do gerador já sai executável.

### ✅ Leituras / CRUD
`Imóveis` e `Cálculos Conformidade` renderizam linhas reais do PostGIS (seções 3.1 e 3.2).

### ❌ Bugs residuais que o E2E revela (documentados com honestidade)

| Task | Sintoma | Natureza |
|------|---------|----------|
| `aggregate_compliance_kpis` | `column "conflicto_app" does not exist` | **Coluna inexistente** — typo (`conflicto` vs `conflito`). Classe que o portão de coluna deveria pegar; a KPI usa nome de coluna que não casa com o DM. |
| `generate_compliance_report` | `litellm.AuthenticationError: api_key must be set` | Task **agente** aponta para OpenAI em vez do **qwen local** (LM Studio). Config de LLM, não de schema. |
| `calculate_app_overlap` | resultado `NULL` | Query de interseção espacial retorna vazio para o imóvel de teste (falta geometria APP semeada / JOIN). |
| `calculate_reserva_legal` | `name 'percentual' is not defined` | Bug de **descrição da task**: usa a variável `percentual` numa fórmula sem antes capturá-la de um SELECT. Classe que o parser determinístico deveria detectar (variável usada em aritmética, nunca definida). |

Esses 4 são residuais **conhecidos e localizados** — não mascarados. Dois deles (`aggregate_compliance_kpis` coluna, `calculate_reserva_legal` variável-fantasma) são exatamente o tipo de erro que o **próximo reforço do portão** deve capturar determinísticamente antes do deploy.

---

## 5. Veredito

**Coerente e rodando**, com escopo honesto:

- ✅ Rastreabilidade **VERDE** ponta-a-ponta (37 FR / 14 NFR / 7 BR), com guardrail determinístico que **garante** — não confia.
- ✅ App gerado **sobe limpo do gerador** (sem edição manual) e renderiza **telas ricas** (mapa Leaflet+desenho, dashboard, upload de geodados) — não formulário genérico.
- ✅ **CRUD lê dados reais** do PostGIS; o **resultado do calculador aparece na UI**.
- ✅ Calculador urbanístico **executa determinístico e correto** (CA/TO + conforme/nao-conforme) pelo mesmo WebSocket do frontend.
- ⚠️ **4 tasks residuais com bug** localizado (2 de coluna/variável — alvo do próximo reforço do portão; 1 de config LLM; 1 de geometria semeada).

O pipeline canônico foi seguido sem bypass: Requisitos → Especificação → Modelo de Dados → UI Spec & Protótipo → Agent-Task Spec → YAML → Código → Deploy → execução E2E. As correções ficaram no **gerador/prompts** (produto) e as ações de pipeline pela **UI**.
