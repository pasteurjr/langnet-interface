# Demonstração do SDD usando a ferramenta LangNet

**Projeto de exemplo: Uso do Solo.** Roteiro do vídeo que percorre TODAS as etapas do pipeline dentro do LangNet, mostrando onde cada uma é carregada, as funções de cada tela, as partes principais de cada documento e — o ponto central — como os documentos se **rastreiam** entre si (requisito → spec → tarefa → código). Ao final, a aplicação gerada.

**Duração:** ~4:09 (abertura 15s + 12 etapas). Para caber em 3 min, acelere as trocas de tela.


## Abertura (15s) — as funções presentes em TODA etapa

Antes de entrar nas etapas, mostre que toda etapa do pipeline tem os mesmos controles no topo:

- **📜 Histórico** — navega entre as versões geradas da etapa (cada geração/refino vira uma versão).
- **🚀 Gerar / Regenerar do zero** — gera o artefato desta etapa a partir da etapa anterior (a origem).
- **🔍 Revisar** — valida o artefato (pontuação e lista de problemas) antes de aprovar.
- **💬 Refinar com o agente** — abre um chat para ajustar o artefato em linguagem natural.
- **✓ Aprovar** — marca a versão como aprovada — é o que libera a próxima etapa do pipeline.
- **👁 Visualizar / ⬇ Exportar** — abre o documento gerado e permite baixar em Markdown ou PDF.

Diga a tese: *no SDD, a especificação é primária e o código é derivado; o LangNet gera cada artefato da etapa anterior e mantém a rastreabilidade entre eles.*


| # | Etapa | Entra | Dura |
|---|-------|-------|------|
| — | Abertura (funções comuns) | 0:00 | 15s |
| 1 | Requisitos | 0:15 | 22s |
| 2 | Especificação | 0:37 | 24s |
| 3 | Modelo de Dados | 1:01 | 20s |
| 4 | Protótipo de Interface | 1:21 | 20s |
| 5 | Agentes e Tarefas (ATS) | 1:41 | 20s |
| 6 | Agentes (agents.yaml) | 2:01 | 16s |
| 7 | Tarefas (tasks.yaml) | 2:17 | 20s |
| 8 | Sequência de Tarefas → Rede de Petri | 2:37 | 18s |
| 9 | Casos de Teste (CEG) | 2:55 | 20s |
| 10 | Código gerado | 3:15 | 20s |
| 11 | Rastreabilidade verificada (o portão) | 3:35 | 16s |
| 12 | A aplicação gerada rodando | 3:51 | 18s |

---

## Etapa 1 · Requisitos

**Tempo:** 0:15 → 0:37 (22 s)  ·  **Tela:** `00_requisitos.png`

**Como acessar:** Projeto Uso do Solo → etapa Requisitos. É a ENTRADA do pipeline: parte dos documentos-fonte (a legislação, o briefing) e extrai os requisitos.

**Funções desta tela:** Aqui o refino gera versões — a tela mostra o comparativo antes × depois do refino (versionamento). (além dos controles comuns da abertura).

**Partes principais do documento:** Documento de Requisitos v2.2. Requisitos funcionais (FR), não-funcionais (NFR) e regras de negócio (BR), cada um com prioridade, atores, dependências e critério de aceitação. Ex.: FR-016 “Coeficiente de Aproveitamento (CA = área construída / terreno)”.

**Rastreabilidade:** É a RAIZ da rastreabilidade. Cada FR daqui será seguido até o código. Guarde o FR-016 — vamos persegui-lo por todas as etapas.

**Roteiro de fala:**

> Abra Requisitos. Explique que o LangNet leu os documentos-fonte (inclusive a legislação municipal) e extraiu os requisitos com critério de aceitação. Aponte o FR-016 e diga: “este é o requisito que vamos rastrear até o código”. Mostre que a tela versiona e permite refinar por chat.


---

## Etapa 2 · Especificação

**Tempo:** 0:37 → 1:01 (24 s)  ·  **Tela:** `01_specification.png`

**Como acessar:** Etapa Especificação → Histórico → Visualizar. Deriva dos Requisitos (a origem é o documento de requisitos aprovado).

**Funções desta tela:** É o documento PRIMÁRIO do SDD: o que se versiona e revisa. O código será derivado dele. (além dos controles comuns da abertura).

**Partes principais do documento:** Especificação Funcional — Plataforma Integrada de Gestão de Uso do Solo. Introdução, escopo (eixos operacional, urbanístico, ambiental e IA), casos de uso, e a MATRIZ DE RASTREABILIDADE FR→UC.

**Rastreabilidade:** 1ª ligação: a matriz mapeia FR-016 → UC-001 (Consulta de Conformidade). Todo FR precisa de ≥1 caso de uso — FR órfão é rejeitado.

**Roteiro de fala:**

> Abra a Especificação e mostre o documento real. Diga a frase do SDD: a spec é primária, o código é derivado. Role até a matriz de rastreabilidade e mostre FR-016 ligado ao UC-001 — a primeira ponte da cadeia.


---

## Etapa 3 · Modelo de Dados

**Tempo:** 1:01 → 1:21 (20 s)  ·  **Tela:** `02_data_model.png`

**Como acessar:** Etapa Modelo de Dados. Deriva da Especificação (a origem é a Spec aprovada).

**Funções desta tela:** Tem abas: Entidades, Schema SQL, models.py e Alembic — e valida o schema (pontuação/problemas). (além dos controles comuns da abertura).

**Partes principais do documento:** PostgreSQL/PostGIS, 17 tabelas. Entidades como imoveis, zoneamentos, parametros_urbanisticos — com colunas geométricas geometry(Geometry, 4674) (SIRGAS 2000).

**Rastreabilidade:** As entidades saem dos requisitos e da spec: os parâmetros por zona (FR-002) viram a tabela parametros_urbanisticos; o CA/TO (FR-016/017) usam essas colunas.

**Roteiro de fala:**

> Abra o Modelo de Dados. Mostre “Aprovado · PostgreSQL · 17 tabelas” e percorra as abas Entidades → Schema SQL → models.py → Alembic. Aponte a coluna geométrica: o domínio geoespacial nasceu da spec, não foi improvisado.


---

## Etapa 4 · Protótipo de Interface

**Tempo:** 1:21 → 1:41 (20 s)  ·  **Tela:** `03_ui_spec.png`

**Como acessar:** Etapa Interface & Protótipo. Deriva da Especificação + Modelo de Dados.

**Funções desta tela:** Cada tela é um mockup refinável por chat; dá para verificar a coerência tela↔caso de uso↔modelo de dados. (além dos controles comuns da abertura).

**Partes principais do documento:** Dez telas geradas por caso de uso (Resultado de Conformidade, Cálculos Urbanísticos, Mapa de Consulta, Dashboard, Simulação…) e um protótipo interativo do laudo à direita.

**Rastreabilidade:** Cada tela referencia o caso de uso: o protótipo “Resultado de Conformidade” é o UC-001 — a mesma âncora do FR-016.

**Roteiro de fala:**

> Abra Interface & Protótipo. Mostre a lista de 10 telas e o protótipo do Resultado de Conformidade (mapa + resumo CA/TO/APP). Diga que a interface é planejada por caso de uso, antes do código.


---

## Etapa 5 · Agentes e Tarefas (ATS)

**Tempo:** 1:41 → 2:01 (20 s)  ·  **Tela:** `05_agent_task.png`

**Como acessar:** Etapa Agentes & Tarefas → Histórico → versão → Visualizar. Deriva da Especificação.

**Funções desta tela:** Gera o documento estruturado de agentes/tarefas e exporta em Markdown/PDF. (além dos controles comuns da abertura).

**Partes principais do documento:** Especificação de 10 agentes e 30 tarefas. Tabela: ID, nome, módulo e LLM — ex.: AG-04 calculo_urbano_agent (Cálculos Urbanísticos), AG-01 geodados_import_agent (Geodados).

**Rastreabilidade:** Cada tarefa aponta ao caso de uso e ao FR: o calculo_urbano_agent responde ao UC-001/FR-016. É a ponte entre o “o quê” (spec) e o “como” (execução).

**Roteiro de fala:**

> Abra Agentes & Tarefas e Visualize o documento. Mostre a tabela dos 10 agentes. Explique que aqui o LangNet decide a arquitetura agêntica — quais agentes e tarefas, e a qual requisito cada um responde.


---

## Etapa 6 · Agentes (agents.yaml)

**Tempo:** 2:01 → 2:17 (16 s)  ·  **Tela:** `04_yaml_agents.png`

**Como acessar:** Etapa YAML → aba Agents YAML → Visualizar. Deriva da Agent-Task Spec.

**Funções desta tela:** Visualiza e baixa o agents.yaml (o arquivo que o CrewAI consome). (além dos controles comuns da abertura).

**Partes principais do documento:** Cada agente com papel (role), objetivo (goal) e história (backstory). Ex.: geodados_import_agent — especialista PostGIS, valida ST_IsValid, SRID 4674, allow_delegation: false.

**Rastreabilidade:** É o agente da ATS materializado em arquivo — mesmo nome, mesma responsabilidade, ligado às suas tarefas.

**Roteiro de fala:**

> Abra a aba Agents YAML e Visualize. Mostre o geodados_import_agent com role/goal/backstory. Diga que isto é gerado, não escrito à mão.


---

## Etapa 7 · Tarefas (tasks.yaml)

**Tempo:** 2:17 → 2:37 (20 s)  ·  **Tela:** `06_yaml_tasks.png`

**Como acessar:** Etapa YAML → aba Tasks YAML → Visualizar. Deriva da Agent-Task Spec.

**Funções desta tela:** Visualiza e baixa o tasks.yaml — o contrato executável de cada tarefa. (além dos controles comuns da abertura).

**Partes principais do documento:** Cada tarefa com traceability (uc/fr), tipo de execução (determinística ou por agente) e a lógica — inclusive o SQL PostGIS.

**Rastreabilidade:** 2ª ligação forte: a task calculate_urban_compliance traz traceability { uc: UC-001, fr: [FR-016, FR-017, FR-018, FR-019] } — apontando de volta ao caso de uso e ao requisito. É a rastreabilidade impressa no YAML.

**Roteiro de fala:**

> Abra a aba Tasks YAML e Visualize. Mostre a task calculate_urban_compliance: aponte o traceability {uc, fr} = UC-001 / FR-016 e o execution: deterministic. Diga: “o requisito FR-016 agora está escrito dentro da tarefa — é o coração do SDD”.


---

## Etapa 8 · Sequência de Tarefas → Rede de Petri

**Tempo:** 2:37 → 2:55 (18 s)  ·  **Tela:** `07_petri.png`

**Como acessar:** Etapa Rede de Petri. Deriva de agents.yaml + tasks.yaml + a sequência de tarefas.

**Funções desta tela:** Editor visual: Gerar Rede, Simular, Execução Real, Visualizar JSON, adicionar lugar/transição/arco. (além dos controles comuns da abertura).

**Partes principais do documento:** Rede de Petri com lugares e transições: “Início do Fluxo” (com token) → T_start → as tarefas (consultar_regramentos, gerar_dashboard, gerenciar_permissoes…) → “Fim do Fluxo”.

**Rastreabilidade:** As transições SÃO as tarefas do tasks.yaml — a orquestração é a mesma cadeia, agora verificável formalmente (deadlock, alcançabilidade).

**Roteiro de fala:**

> Abra a Rede de Petri. Mostre o canvas: o token no início, as transições que são as tarefas, o fim. Se quiser, clique Simular por 2 s. Diga que a orquestração pode ser verificada, não só testada.


---

## Etapa 9 · Casos de Teste (CEG)

**Tempo:** 2:55 → 3:15 (20 s)  ·  **Tela:** `08_test_cases.png`

**Como acessar:** Etapa Casos de Teste & Validação. Deriva dos casos de uso da Especificação.

**Funções desta tela:** Gerar casos de teste, Revisar, Refinar com o agente, Aprovar. Mostra o Grafo de Causa-Efeito por caso de uso. (além dos controles comuns da abertura).

**Partes principais do documento:** Casos derivados pela técnica do Grafo de Causa-Efeito (CEG): causas = ações do ator, efeitos = respostas do sistema. O UC-001 gerou 5 causas, 6 efeitos e 6 casos.

**Rastreabilidade:** Fecham o ciclo de verificação: os testes nascem do CRITÉRIO do caso de uso (UC-001), não do código — por isso não herdam os bugs da implementação.

**Roteiro de fala:**

> Abra Casos de Teste. Explique a técnica CEG: causas (ações do ator) → efeitos (respostas do sistema) → tabela de decisão, cada coluna é um caso. Mostre o grafo do UC-001 (5 causas → 6 casos).


---

## Etapa 10 · Código gerado

**Tempo:** 3:15 → 3:35 (20 s)  ·  **Tela:** `12_code_real.png`

**Como acessar:** Etapa Código (Geração de Código). Deriva de tudo acima — o código é o artefato DERIVADO.

**Funções desta tela:** Download, Deploy, Executar, Gerar/Atualizar; abas Arquivos, Build, Testes, Deploy. (além dos controles comuns da abertura).

**Partes principais do documento:** O app inteiro (backend, ws-server, banco, interface). Aqui, a função calculate_urban_compliance no adapters.py: a consulta espacial (ST_Contains) e a linha do status conforme/não-conforme.

**Rastreabilidade:** ÚLTIMA ligação: a função implementa a tarefa calculate_urban_compliance → UC-001 → FR-016. A cadeia requisito → spec → tarefa → código está fechada.

**Roteiro de fala:**

> Abra o Código. Mostre a função calculate_urban_compliance: a consulta com JOIN espacial e o status conforme/não-conforme. Diga: “é o FR-016 que vimos no começo, agora rodando em código — rastreável de ponta a ponta”.


---

## Etapa 11 · Rastreabilidade verificada (o portão)

**Tempo:** 3:35 → 3:51 (16 s)  ·  **Tela:** `gate_verde.png`

**Como acessar:** Painel/CLI de rastreabilidade do LangNet (portão determinístico).

**Funções desta tela:** Roda a auditoria automática de todos os saltos da cadeia. (além dos controles comuns da abertura).

**Partes principais do documento:** Portão VERDE: 37/37 requisitos funcionais, e todos os saltos OK — Req→Spec, Matriz FR→UC, FR→Implementação, Task→Modelo de Dados, Task→código.

**Rastreabilidade:** É a PROVA do SDD: o LangNet mede, de forma determinística, que TODO requisito atravessa a spec, o modelo de dados e a implementação. Nada de FR órfão.

**Roteiro de fala:**

> Mostre o portão VERDE (37/37). Diga a frase de fecho do SDD: “o LangNet não confia — ele verifica que todo requisito chegou ao código. Isto é a rastreabilidade que a norma exige, de graça”.


---

## Etapa 12 · A aplicação gerada rodando

**Tempo:** 3:51 → 4:09 (18 s)  ·  **Tela:** `01-app-home.png`

**Como acessar:** O app gerado, implantado (frontend :3001, ws-server :5030, PostGIS).

**Funções desta tela:** Interface real: mapa, desenho de área, cálculo, laudo em PDF. (além dos controles comuns da abertura).

**Partes principais do documento:** Tela de Resultado de Conformidade com mapa Leaflet. E o cálculo E2E: área 1500 → CA=1,5 conforme; 2500 → não-conforme, gravado no banco.

**Rastreabilidade:** Fecha o arco: da especificação ao software rodando — e tudo que o vídeo mostrou é rastreável até este cálculo.

**Roteiro de fala:**

> Rapidamente, abra o app em :3001. Mostre o mapa e faça um cálculo (CA=1,5 → conforme). Encerre: “da spec ao app, rastreável de ponta a ponta — isto é o SDD na ferramenta LangNet”.


---
