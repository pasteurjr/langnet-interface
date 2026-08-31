# Guia de Demonstração do Pipeline LangNet — projeto Uso do Solo

**Para gravar o vídeo do slide S61 (SDD na prática).** Percorre TODAS as etapas do pipeline dentro do aplicativo LangNet, cada uma com a tela real, o que ela mostra, um exemplo do documento gerado e o roteiro de fala.

**Duração sugerida do vídeo:** ~3:50 (12 etapas). Dá para comprimir para 3 min acelerando as esperas 2×–4× com o tempo real na legenda.


| # | Etapa | Entra | Dura |
|---|-------|-------|------|
| 1 | Requisitos | 0:00 | 20s |
| 2 | Especificação | 0:20 | 22s |
| 3 | Modelo de Dados | 0:42 | 20s |
| 4 | UI Spec & Protótipo | 1:02 | 20s |
| 5 | Agent-Task Spec (ATS) | 1:22 | 18s |
| 6 | Agentes (agents.yaml) | 1:40 | 16s |
| 7 | Tarefas (tasks.yaml) | 1:56 | 18s |
| 8 | Rede de Petri | 2:14 | 16s |
| 9 | Casos de Teste (CEG) | 2:30 | 20s |
| 10 | Código | 2:50 | 18s |
| 11 | Deploy (app implantado) | 3:08 | 20s |
| 12 | App em uso: cálculo E2E + resultados | 3:28 | 22s |

---

## Etapa 1 · Requisitos

**Tempo:** 0:00 → 0:20 (20 s)  ·  **Tela:** `00_requisitos.png`

**O que a tela mostra:**

A análise de requisitos gerada a partir dos documentos-fonte (legislação, briefing). Lista FR (funcionais), NFR (não-funcionais) e BR (regras de negócio), cada um com prioridade, atores, dependências e critérios de aceitação. Suporta refino por chat e versionamento (a tela mostra o diff entre versões).

**Exemplo do documento gerado:**

```
| FR-001 | Incorporar Código Florestal | Implementar restrições ambientais conforme o Código Florestal.
| FR-002 | Parâmetros Urbanísticos     | Parâmetros por zona conforme legislação local.
| FR-003 | Emissão de Laudos           | Emitir pareceres de conformidade (dep.: FR-001, FR-002).
| FR-004 | Integração COPAM/Sisema     | Integrar à base do Sisema/COPAM para validação.
```

**Roteiro de fala:**

> Abra a etapa Requisitos. Explique que o LangNet leu os documentos-fonte (inclusive a legislação) e extraiu os requisitos com rastreabilidade e critérios de aceitação — é a base de todo o resto do pipeline. Mostre um FR e seu critério; aponte o refino por chat e o versionamento.


---

## Etapa 2 · Especificação

**Tempo:** 0:20 → 0:42 (22 s)  ·  **Tela:** `01_specification.png`

**O que a tela mostra:**

A Especificação Funcional derivada dos requisitos: introdução, escopo, casos de uso, matriz de rastreabilidade FR→UC, regras de negócio e modelo conceitual. É o documento primário do SDD — o que se versiona e revisa; o resto é derivado dele.

**Exemplo do documento gerado:**

```
Especificação Funcional — Plataforma Integrada de Gestão Municipal de Uso do Solo e Cálculos Urbanísticos
  Escopo:
   • Eixo Operacional: cadastro de imóveis, licenciamento, alvarás, fiscalização, protocolos.
   • Eixo Urbanístico: zoneamento poligonal, parâmetros por zona (CA, TO, recuos), conformidade.
   • Eixo Ambiental: APP (Código Florestal), Reserva Legal, declividade, integração IDE Sisema.
   • Inteligência Artificial: extração de regras de legislação (PDF/DOCX) e geocodificação.
```

**Roteiro de fala:**

> Abra a Especificação → Histórico → Visualizar. Mostre o documento real. Diga a frase do SDD: a spec é primária, o código é derivado. Aponte a matriz de rastreabilidade — é o que garante que todo requisito chega ao código.


---

## Etapa 3 · Modelo de Dados

**Tempo:** 0:42 → 1:02 (20 s)  ·  **Tela:** `02_data_model.png`

**O que a tela mostra:**

O modelo de dados derivado da especificação: entidades, schema SQL, models.py (SQLAlchemy+Pydantic) e migrations Alembic. Aqui é PostgreSQL/PostGIS com 17 tabelas e colunas geométricas SRID 4674. As abas provam que gera o DDL, os modelos e as migrations — não só um diagrama.

**Exemplo do documento gerado:**

```
CREATE TABLE "zoneamentos" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "municipio_id" uuid NOT NULL,
  "nome" VARCHAR(200) NOT NULL,
  "geometria" geometry(Geometry,4674) NOT NULL,   -- PostGIS, SIRGAS 2000
  FOREIGN KEY ("municipio_id") REFERENCES municipios(id) ON DELETE CASCADE);
```

**Roteiro de fala:**

> Abra o Modelo de Dados. Mostre 'Aprovado · PostgreSQL · 17 tabelas' e percorra as abas Entidades → Schema SQL → models.py → Alembic. Destaque a coluna geometry(Geometry,4674): é geoespacial de verdade, derivado da spec.


---

## Etapa 4 · UI Spec & Protótipo

**Tempo:** 1:02 → 1:22 (20 s)  ·  **Tela:** `03_ui_spec.png`

**O que a tela mostra:**

A especificação de interface e o protótipo, gerados por caso de uso a partir da spec + modelo de dados. Dez telas (Resultado de Conformidade, Cálculos Urbanísticos, Mapa de Consulta, Dashboard, Simulação…), cada uma com wireframe e um mockup interativo — refinável por chat.

**Exemplo do documento gerado:**

```
Telas geradas (10):
  UC-001  Resultado de Conformidade   (mapa + resumo CA/TO/Recuos/APP + laudo PDF)
  UC-007  Mapa de Consulta            (zoneamentos)
  UC-009  Dashboard de Conformidade   (indicadores municipais)
  UC-010  Simulação de Cenários
```

**Roteiro de fala:**

> Abra Interface & Protótipo. Mostre a lista de 10 telas à esquerda e, à direita, o protótipo do 'Resultado de Conformidade' com o mapa e o resumo de conformidade. A interface é planejada por caso de uso, antes do código.


---

## Etapa 5 · Agent-Task Spec (ATS)

**Tempo:** 1:22 → 1:40 (18 s)  ·  **Tela:** `05_agent_task.png`

**O que a tela mostra:**

A especificação de agentes e tarefas: para cada caso de uso, quais agentes existem e quais tarefas eles executam, com o vínculo ao requisito. É a ponte entre o 'o quê' (spec) e o 'como' (execução). A versão gerada aqui tem 10 agentes e 30 tarefas.

**Exemplo do documento gerado:**

```
Especificação de Agentes & Tarefas — 10 agentes · 30 tarefas
  AG-01 geodados_import_agent   · Geodados             · GPT-4o
  AG-02 zoneamento_mgmt_agent   · Zoneamento           · Claude 3.5 Sonnet (memória: sim)
  AG-04 calculo_urbano_agent    · Cálculos Urbanísticos · Claude 3.5 Sonnet
  AG-06 laudo_gen_agent         · Relatórios/Laudos    · GPT-4o
  (cada agente com suas tarefas e o UC/FR que atende)
```

**Roteiro de fala:**

> Abra a Agent-Task Spec. Explique que aqui o LangNet decide a arquitetura agêntica: quais agentes, quais tarefas, e a qual requisito cada uma responde. Mostre a lista de versões geradas (10 agentes, 30 tarefas).


---

## Etapa 6 · Agentes (agents.yaml)

**Tempo:** 1:40 → 1:56 (16 s)  ·  **Tela:** `04_yaml_agents.png`

**O que a tela mostra:**

O agents.yaml gerado: cada agente com papel (role), objetivo (goal) e história (backstory) — o formato que o CrewAI consome. Deriva da Agent-Task Spec.

**Exemplo do documento gerado:**

```
geodados_import_agent:
  role:  Especialista em Importação e Validação de Dados Geoespaciais
  goal:  Importar, validar integridade espacial (ST_IsValid) e persistir
         camadas de zoneamento, lotes e APPs no PostGIS
  backstory: Engenheiro de dados geoespaciais com expertise em PostGIS e SRID 4674…
```

**Roteiro de fala:**

> Abra a aba Agents YAML → Visualizar. Mostre um agente real (geodados_import_agent) com role, goal e backstory. Diga que isto é gerado, não escrito à mão, e alimenta o CrewAI.


---

## Etapa 7 · Tarefas (tasks.yaml)

**Tempo:** 1:56 → 2:14 (18 s)  ·  **Tela:** `06_yaml_tasks.png`

**O que a tela mostra:**

O tasks.yaml gerado: cada tarefa com rastreabilidade (uc/fr), tipo de execução (determinística ou por agente) e a lógica — inclusive o SQL PostGIS. É o contrato executável de cada tarefa, ligado ao requisito.

**Exemplo do documento gerado:**

```
calculate_urban_compliance:
  traceability: { uc: UC-001, fr: [FR-016, FR-017, FR-018, FR-019] }
  execution: deterministic
  agent: calculo_urbano_agent
  description: SELECT z.id, p.ca_maximo, p.to_maxima FROM zoneamentos z
               JOIN parametros_urbanisticos p ON p.zona_id = z.id …  (CA/TO → conforme?)
```

**Roteiro de fala:**

> Abra a aba Tasks YAML → Visualizar. Mostre a task calculate_urban_compliance: o traceability {uc, fr}, o execution: deterministic e o SQL. Cada tarefa é rastreável até o requisito — é o coração do SDD.


---

## Etapa 8 · Rede de Petri

**Tempo:** 2:14 → 2:30 (16 s)  ·  **Tela:** `07_petri.png`

**O que a tela mostra:**

A orquestração das tarefas modelada como Rede de Petri, gerada de agents.yaml + tasks.yaml. Lugares, transições e marcações — uma estrutura que pode ser VERIFICADA formalmente (ausência de deadlock, alcançabilidade), não apenas testada.

**Exemplo do documento gerado:**

```
Rede de Petri:
  Lugar  P0: 'Início do Fluxo' (token=1)
  Transição T_start → tarefas: consultar_regramentos, gerar_dashboard, gerar_requisitos_ambientais…
  Lugar  'Fim do Fluxo'
```

**Roteiro de fala:**

> Abra a Rede de Petri. Mostre o canvas: 'Início do Fluxo' com o token, o T_start e as transições até o 'Fim do Fluxo'. Se quiser, clique Simular por 2 s para o token andar. É a orquestração verificável.


---

## Etapa 9 · Casos de Teste (CEG)

**Tempo:** 2:30 → 2:50 (20 s)  ·  **Tela:** `08_test_cases.png`

**O que a tela mostra:**

Os casos de teste gerados dos casos de uso pela técnica do Grafo de Causa-Efeito (causas = ações do ator, efeitos = respostas do sistema). Cada coluna da tabela de decisão vira um caso de teste. Aqui, o UC-001 gerou 5 causas, 6 efeitos e 6 casos. Nascem do CRITÉRIO, não do código.

**Exemplo do documento gerado:**

```
Grafo de Causa-Efeito — UC-001 Consulta de Conformidade Consolidada
  Ator: Analista Urbano/Engenheiro · 5 causas · 6 efeitos · 6 casos
  CAUSAS (ações do ator):
   c1  Geometria do lote é válida
   c2  Parâmetros da zona estão cadastrados
   c3  Analista solicita geração do laudo
   c4  Analista solicita simulação de cenário
  → cada combinação vira uma coluna da tabela de decisão = um caso de teste
```

**Roteiro de fala:**

> Abra Casos de Teste. Explique a técnica: as causas são ações do ator e os efeitos são respostas do sistema; o Grafo de Causa-Efeito produz a tabela de decisão, e cada coluna é um caso. Mostre o grafo do UC-001 sendo gerado (5 causas → 6 casos). Os testes derivam do critério, não do código.


---

## Etapa 10 · Código

**Tempo:** 2:50 → 3:08 (18 s)  ·  **Tela:** `12_code_real.png`

**O que a tela mostra:**

O código gerado (backend, ws-server, banco e interface). Aqui, o calculador determinístico calculate_urban_compliance no adapters.py — nasceu da spec e da tarefa, sem edição manual.

**Exemplo do documento gerado:**

```
def calculate_urban_compliance_deterministic(input_data):
    cur.execute('SELECT z.id, p.ca_maximo, p.to_maxima FROM zoneamentos z
                 JOIN parametros_urbanisticos p ON p.zona_id=z.id
                 JOIN imoveis i ON i.id=%s WHERE ST_Contains(z.geometria,i.geometria)', [imovel_id])
    ca_calc = _safe_div(area_construida, area_terreno)
    status_ca = 'conforme' if ca_calc <= ca_maximo else 'nao_conforme'
```

**Roteiro de fala:**

> Abra o código gerado (adapters.py). Mostre o calculador: a consulta espacial (ST_Contains) e a linha do status conforme/não-conforme. É o código do repositório, rastreável até a tarefa e ao requisito FR-016.


---

## Etapa 11 · Deploy (app implantado)

**Tempo:** 3:08 → 3:28 (20 s)  ·  **Tela:** `01-app-home.png`

**O que a tela mostra:**

A aplicação gerada, implantada e rodando: frontend em :3001, ws-server em :5030, PostGIS. Interface real com mapa Leaflet, desenho de área, importação de Shapefile e geração de laudo em PDF.

**Exemplo do documento gerado:**

```
Serviços no ar:
  frontend  → http://localhost:3001   (React + Leaflet)
  ws-server → ws://localhost:5030      (15 tarefas determinísticas)
  postgres  → uso_solo_green           (PostGIS 3.4, SRID 4674)
```

**Roteiro de fala:**

> Abra o app em :3001. Mostre a tela de Resultado de Conformidade com o mapa. Diga que é o app gerado pelo pipeline, rodando contra PostGIS — a spec virou software funcionando.


---

## Etapa 12 · App em uso: cálculo E2E + resultados

**Tempo:** 3:28 → 3:50 (22 s)  ·  **Tela:** `02-calculos-urbanisticos.png`

**O que a tela mostra:**

O aplicativo em uso, ponta a ponta: preenche a área, calcula a conformidade (CA/TO) e persiste o resultado no banco. Fecha o arco: da especificação ao software rodando de verdade.

**Exemplo do documento gerado:**

```
Cálculo E2E (ws-server + PostGIS):
  Área construída 1500 / projeção 500 → CA=1,5 · TO=0,5 → conforme
  Área construída 2500                → CA=2,5          → nao_conforme
  → gravado em calculos_conformidade (CA_CALCULADO, STATUS_CA, …)
```

**Roteiro de fala:**

> Na tela Cálculos Urbanísticos, preencha e clique Calcular: CA=1,5 → conforme; depois 2500 → não-conforme. Corte para a lista Cálculos Conformidade mostrando as linhas gravadas. Feche a demo com o portão de rastreabilidade VERDE (37/37) — spec → código → verificação.


---
