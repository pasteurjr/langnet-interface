# Script de Vídeo — Passeio pelo pipeline SDD na ferramenta LangNet (projeto Uso do Solo)

**Formato:** script para locução automática. **NARRAÇÃO** = fala EXATA a ser lida (siglas soletradas). **PRODUÇÃO** = o que mostrar (menu lateral, funções, onde se escreve). **TRECHO DO DOCUMENTO** = parte real a exibir. Estilo demonstrativo. **Ordem = navegação real.** **Duração:** ~4:24 (14 cenas).


| Cena | Etapa do pipeline | Entra | Dura |
|---|---|---|---|
| 1 | O sistema e os projetos | 0:00 | 13s |
| 2 | O menu lateral — as etapas do pipeline | 0:13 | 22s |
| 3 | Documentos — a origem e o documento de Requisitos | 0:35 | 30s |
| 4 | Especificação — casos de uso e fluxos | 1:05 | 30s |
| 5 | Modelo de Dados | 1:35 | 20s |
| 6 | Interface & Protótipo | 1:55 | 16s |
| 7 | Agentes & Tarefas | 2:11 | 17s |
| 8 | YAML de Agentes e Tarefas — a rastreabilidade impressa | 2:28 | 20s |
| 9 | Sequência de Tarefas | 2:48 | 13s |
| 10 | Rede de Petri | 3:01 | 15s |
| 11 | Geração de Código | 3:16 | 18s |
| 12 | Casos de Teste & Validação | 3:34 | 18s |
| 13 | Rastreabilidade verificada | 3:52 | 16s |
| 14 | A aplicação gerada | 4:08 | 16s |

---

## Cena 1 · O sistema e os projetos   (0:00 → 0:13 · 13s)

**Telas:** `A0_projetos.png`

**🎙 NARRAÇÃO (fala exata):**

> Esta é uma demonstração de Desenvolvimento Orientado a Especificação — o S D D — na ferramenta LangNet. Aqui estão os projetos: cada projeto percorre um pipeline completo, do requisito ao código rastreável. Vamos abrir o projeto de gestão do uso do solo.

**🎬 PRODUÇÃO:** Tela Projetos (11 projetos). Um clique curto no card “Uso do Solo v3 / Abrir Projeto”. Não se demore.


---

## Cena 2 · O menu lateral — as etapas do pipeline   (0:13 → 0:35 · 22s)

**Telas:** `sidebar.png`

**🎙 NARRAÇÃO (fala exata):**

> Ao abrir o projeto, o menu lateral revela o pipeline inteiro. Cada item é uma etapa, na ordem: Documentos, onde tudo começa; Especificação; Modelo de Dados; Interface e Protótipo; Agentes e Tarefas; o YAML de Agentes e Tarefas; a Sequência de Tarefas; a Rede de Petri; a Geração de Código; e os Casos de Teste e Validação. As etapas de Deploy e Monitoramento fecham a operação. Vamos entrar em cada uma.

**🎬 PRODUÇÃO:** Barra lateral do projeto em foco, mostrando a seção PIPELINE (Documentos … Casos de Teste) e a seção OPERAÇÃO (Deploy, Monitoramento). Percorra os itens de cima a baixo com um leve destaque.


---

## Cena 3 · Documentos — a origem e o documento de Requisitos   (0:35 → 1:05 · 30s)

**Telas:** `doc_stage.png`, `req_fr.png`, `req_nfr.png`

**🎙 NARRAÇÃO (fala exata):**

> A primeira etapa é Documentos. Aqui você traz os arquivos de origem — inclusive a legislação municipal — escreve instruções de análise no painel e inicia a geração. O resultado é o documento de Requisitos. Ele traz os requisitos funcionais, o que o sistema deve fazer, cada um com prioridade; e os não-funcionais, as metas de qualidade. Repare no requisito F R zero dezesseis, o cálculo do coeficiente de aproveitamento: é ele que vamos seguir até o código.

**🎬 PRODUÇÃO:** Tela Documentos: lista de arquivos-fonte, campo “Instruções para Análise”, “Pesquisa Web” e “🚀 Iniciar Análise”. Depois, abra o documento de Requisitos e role pela tabela de Requisitos Funcionais (destaque FR-016 “Cálculo de CA”) e pela de Requisitos Não-Funcionais.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
REQUISITOS FUNCIONAIS (trecho real do documento)
  FR-014  Parâmetros urbanísticos por zona                 Alta
  FR-015  Zoneamento poligonal                             Alta
  FR-016  Cálculo de CA (Coeficiente de Aproveitamento)    Alta   <= nosso fio condutor
  FR-017  Cálculo de TO (Taxa de Ocupação)                 Alta
  FR-018  Cálculo e Validação de Recuos                    Alta

REQUISITOS NÃO-FUNCIONAIS (trecho real)
  NFR-001  Escalabilidade   100 municípios simultâneos
  NFR-002  Performance      Latência do mapa < 5 s
  NFR-003  Usabilidade      Tarefa principal ≤ 3 min
  NFR-005  Confiabilidade   Uptime 99,5%
```


---

## Cena 4 · Especificação — casos de uso e fluxos   (1:05 → 1:35 · 30s)

**Telas:** `spec_stage.png`, `S_uc.png`, `S_flux.png`

**🎙 NARRAÇÃO (fala exata):**

> Dos requisitos deriva a Especificação Funcional — o documento primário do S D D. Ela detalha os casos de uso. Cada caso de uso traz o ator, o objetivo, os requisitos relacionados e três fluxos: o principal, o passo a passo normal; os alternativos, os caminhos válidos diferentes; e os de exceção, o tratamento de erros. Veja o caso de uso zero zero um: no fluxo principal o sistema calcula o coeficiente, dá dois vírgula cinco contra o limite de dois, e conclui não conforme. E ele está ligado, explicitamente, ao requisito F R zero dezesseis.

**🎬 PRODUÇÃO:** Tela Especificação (painel de config com Gerar/Revisar). Depois o documento, no UC-001: a tabela com Ator, Objetivo e “RFs Relacionados: FR-016…”, e então os Fluxos Alternativos e de Exceção.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
UC-001 — Consulta de Conformidade Consolidada (trecho real)
  RFs Relacionados: FR-016, FR-017, FR-018, FR-019, FR-020…
  Fluxo Principal (passo 2): CA = 500 m² / 200 m² = 2,5 · limite 2,0 → NÃO CONFORME
  Fluxos Alternativos:  A1 sobreposição com APP (12,5 m²)   A2 “Simular” → 400 m² → CA 2,0 → CONFORME
  Fluxos de Exceção:    E1 geometria inválida → Editor de Mapas   E2 zona sem parâmetros → Notificar
```


---

## Cena 5 · Modelo de Dados   (1:35 → 1:55 · 20s)

**Telas:** `dm_stage.png`

**🎙 NARRAÇÃO (fala exata):**

> Da especificação deriva o Modelo de Dados. A ferramenta gera as entidades, o esquema, os modelos e as migrações — aqui, um banco geográfico. Repare na tabela de parâmetros urbanísticos por zona, com o coeficiente máximo e a taxa de ocupação: é dela que o cálculo do requisito F R zero dezesseis vai ler os limites. E o sistema ainda valida o esquema automaticamente.

**🎬 PRODUÇÃO:** Tela Modelo de Dados: à esquerda o painel (DBMS PostgreSQL, Regenerar/Revisar/Refinar); à direita as entidades — destaque “parametros_urbanisticos” com ca_maximo e to_maxima, e a coluna geometria.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Entidade parametros_urbanisticos (trecho real)
  ca_maximo        DECIMAL(10,2)      -- limite de CA por zona (FR-016)
  to_maxima        DECIMAL(10,2)      -- limite de TO por zona (FR-017)
  zoneamentos.geometria  geometry(Geometry, 4674)   -- PostGIS · SIRGAS 2000
```


---

## Cena 6 · Interface & Protótipo   (1:55 → 2:11 · 16s)

**Telas:** `ui_stage.png`, `03_ui_spec.png`

**🎙 NARRAÇÃO (fala exata):**

> Antes do código, a ferramenta gera o protótipo de interface — uma tela para cada caso de uso. Cada tela nasce amarrada ao seu caso de uso; esta, de resultado de conformidade, é o mesmo caso de uso zero zero um que acabamos de ver.

**🎬 PRODUÇÃO:** Tela Interface e Protótipo: à esquerda a lista de telas e o painel “Gerar UI Spec”; à direita o mockup da tela de conformidade (mapa + resumo de CA/TO/APP).


---

## Cena 7 · Agentes & Tarefas   (2:11 → 2:28 · 17s)

**Telas:** `at_stage.png`, `05_agent_task.png`

**🎙 NARRAÇÃO (fala exata):**

> Agora a ferramenta define a arquitetura de execução: quais agentes existem e quais tarefas cada um realiza, e sob qual framework. É a ponte entre o que o sistema deve fazer e como ele fará — cada tarefa já apontando para o caso de uso e os requisitos que atende.

**🎬 PRODUÇÃO:** Tela Agentes e Tarefas: o painel (Nível de Detalhamento, framework CrewAI, “Gerar Agentes & Tarefas”) e o documento de especificação de agentes e tarefas com a lista de agentes.


---

## Cena 8 · YAML de Agentes e Tarefas — a rastreabilidade impressa   (2:28 → 2:48 · 20s)

**Telas:** `yaml_stage.png`, `06_yaml_tasks.png`

**🎙 NARRAÇÃO (fala exata):**

> A especificação de agentes e tarefas vira arquivos executáveis: o agents ponto yaml e o tasks ponto yaml. Aqui está o coração do S D D: cada tarefa carrega a própria rastreabilidade. A tarefa que calcula a conformidade traz, escrito no arquivo, o caso de uso zero zero um e os requisitos F R zero dezesseis a dezenove. O requisito não se perdeu — está impresso dentro da tarefa que o executa.

**🎬 PRODUÇÃO:** Tela YAML (painel “Gerar agents.yaml/tasks.yaml”). No tasks.yaml, enquadre a task calculate_urban_compliance e destaque a linha de traceability e o campo execution.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
calculate_urban_compliance:
  traceability: { uc: UC-001, fr: [FR-016, FR-017, FR-018, FR-019] }
  execution: deterministic
  agent: calculo_urbano_agent
```


---

## Cena 9 · Sequência de Tarefas   (2:48 → 3:01 · 13s)

**Telas:** `seq_stage.png`

**🎙 NARRAÇÃO (fala exata):**

> Com os agentes e tarefas prontos, a ferramenta organiza a Sequência de Tarefas: a ordem em que elas são executadas para cumprir cada caso de uso, ligando entradas e saídas de uma tarefa à seguinte.

**🎬 PRODUÇÃO:** Tela Sequência de Tarefas: o painel de geração e a origem “Specs & Docs”. Mostre rapidamente que ela encadeia as tarefas do fluxo.


---

## Cena 10 · Rede de Petri   (3:01 → 3:16 · 15s)

**Telas:** `petri_stage.png`

**🎙 NARRAÇÃO (fala exata):**

> Essa sequência é formalizada como uma Rede de Petri. Cada transição é uma tarefa; os tokens percorrem a rede do início ao fim. É uma orquestração que pode ser verificada formalmente, e não apenas testada.

**🎬 PRODUÇÃO:** Editor da Rede de Petri: o lugar “Início do Fluxo” com o token, as transições (as tarefas) e o “Fim do Fluxo”. Opcional: um clique em Simular para o token avançar.


---

## Cena 11 · Geração de Código   (3:16 → 3:34 · 18s)

**Telas:** `code_stage.png`, `12_code_real.png`

**🎙 NARRAÇÃO (fala exata):**

> Só então vem o código — o artefato derivado. A ferramenta gera o projeto inteiro, dezenas de arquivos. E aqui está a função que calcula a conformidade: a consulta espacial e a classificação em conforme ou não conforme. É o requisito F R zero dezesseis, que vimos no começo, agora rodando.

**🎬 PRODUÇÃO:** Tela Geração de Código: a árvore de arquivos à esquerda e o editor à direita. Depois, enquadre a função calculate_urban_compliance, com o JOIN espacial e a linha do status conforme / não conforme.


---

## Cena 12 · Casos de Teste & Validação   (3:34 → 3:52 · 18s)

**Telas:** `tests_stage.png`

**🎙 NARRAÇÃO (fala exata):**

> Os casos de teste nascem dos casos de uso, pela técnica do grafo de causa e efeito. As causas são as ações do usuário; os efeitos, as respostas do sistema. No S D D isto é essencial: o teste deriva do critério, não do código — por isso não herda os defeitos da implementação.

**🎬 PRODUÇÃO:** Tela Casos de Teste: a lista de casos de uso à esquerda e, à direita, o Grafo de Causa-Efeito do UC-001, com as causas e efeitos ligados.


---

## Cena 13 · Rastreabilidade verificada   (3:52 → 4:08 · 16s)

**Telas:** `gate_verde.png`

**🎙 NARRAÇÃO (fala exata):**

> E a ferramenta prova essa cadeia. A matriz de rastreabilidade liga cada requisito ao caso de uso que o realiza; e o portão de rastreabilidade verifica automaticamente que todos os trinta e sete requisitos atravessam a especificação, o modelo de dados e a implementação. Nenhum requisito órfão.

**🎬 PRODUÇÃO:** Mostre o portão de rastreabilidade em VERDE — 37 de 37, todos os saltos OK. Congele por 3 segundos.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Matriz de Rastreabilidade (trecho real)
  FR-016 → Especificação 5.2 / UC-001 → realizado por UC-001 → task calculate_urban_compliance
  FR-015 → UC-005 (Zoneamento)   ·   FR-005 / FR-007 → UC-004 (Legislação com IA)
  Portão: 37/37 · Req→Spec, Matriz FR→UC, FR→Implementação, Task→código: OK
```


---

## Cena 14 · A aplicação gerada   (4:08 → 4:24 · 16s)

**Telas:** `01-app-home.png`

**🎙 NARRAÇÃO (fala exata):**

> E este é o resultado: a aplicação gerada, rodando. O mesmo cálculo de conformidade que rastreamos desde o requisito — área, coeficiente, veredito — agora funcionando sobre um mapa real. Da especificação ao software, rastreável de ponta a ponta. Isto é o S D D, na ferramenta LangNet.

**🎬 PRODUÇÃO:** Aplicação gerada no navegador: a tela inicial e o resultado de conformidade. Se der, um cálculo rápido resultando em “conforme”. Encerre com o título.


---

## Locução corrida (só as falas, para colar no gerador de voz)

Esta é uma demonstração de Desenvolvimento Orientado a Especificação — o S D D — na ferramenta LangNet. Aqui estão os projetos: cada projeto percorre um pipeline completo, do requisito ao código rastreável. Vamos abrir o projeto de gestão do uso do solo.
Ao abrir o projeto, o menu lateral revela o pipeline inteiro. Cada item é uma etapa, na ordem: Documentos, onde tudo começa; Especificação; Modelo de Dados; Interface e Protótipo; Agentes e Tarefas; o YAML de Agentes e Tarefas; a Sequência de Tarefas; a Rede de Petri; a Geração de Código; e os Casos de Teste e Validação. As etapas de Deploy e Monitoramento fecham a operação. Vamos entrar em cada uma.
A primeira etapa é Documentos. Aqui você traz os arquivos de origem — inclusive a legislação municipal — escreve instruções de análise no painel e inicia a geração. O resultado é o documento de Requisitos. Ele traz os requisitos funcionais, o que o sistema deve fazer, cada um com prioridade; e os não-funcionais, as metas de qualidade. Repare no requisito F R zero dezesseis, o cálculo do coeficiente de aproveitamento: é ele que vamos seguir até o código.
Dos requisitos deriva a Especificação Funcional — o documento primário do S D D. Ela detalha os casos de uso. Cada caso de uso traz o ator, o objetivo, os requisitos relacionados e três fluxos: o principal, o passo a passo normal; os alternativos, os caminhos válidos diferentes; e os de exceção, o tratamento de erros. Veja o caso de uso zero zero um: no fluxo principal o sistema calcula o coeficiente, dá dois vírgula cinco contra o limite de dois, e conclui não conforme. E ele está ligado, explicitamente, ao requisito F R zero dezesseis.
Da especificação deriva o Modelo de Dados. A ferramenta gera as entidades, o esquema, os modelos e as migrações — aqui, um banco geográfico. Repare na tabela de parâmetros urbanísticos por zona, com o coeficiente máximo e a taxa de ocupação: é dela que o cálculo do requisito F R zero dezesseis vai ler os limites. E o sistema ainda valida o esquema automaticamente.
Antes do código, a ferramenta gera o protótipo de interface — uma tela para cada caso de uso. Cada tela nasce amarrada ao seu caso de uso; esta, de resultado de conformidade, é o mesmo caso de uso zero zero um que acabamos de ver.
Agora a ferramenta define a arquitetura de execução: quais agentes existem e quais tarefas cada um realiza, e sob qual framework. É a ponte entre o que o sistema deve fazer e como ele fará — cada tarefa já apontando para o caso de uso e os requisitos que atende.
A especificação de agentes e tarefas vira arquivos executáveis: o agents ponto yaml e o tasks ponto yaml. Aqui está o coração do S D D: cada tarefa carrega a própria rastreabilidade. A tarefa que calcula a conformidade traz, escrito no arquivo, o caso de uso zero zero um e os requisitos F R zero dezesseis a dezenove. O requisito não se perdeu — está impresso dentro da tarefa que o executa.
Com os agentes e tarefas prontos, a ferramenta organiza a Sequência de Tarefas: a ordem em que elas são executadas para cumprir cada caso de uso, ligando entradas e saídas de uma tarefa à seguinte.
Essa sequência é formalizada como uma Rede de Petri. Cada transição é uma tarefa; os tokens percorrem a rede do início ao fim. É uma orquestração que pode ser verificada formalmente, e não apenas testada.
Só então vem o código — o artefato derivado. A ferramenta gera o projeto inteiro, dezenas de arquivos. E aqui está a função que calcula a conformidade: a consulta espacial e a classificação em conforme ou não conforme. É o requisito F R zero dezesseis, que vimos no começo, agora rodando.
Os casos de teste nascem dos casos de uso, pela técnica do grafo de causa e efeito. As causas são as ações do usuário; os efeitos, as respostas do sistema. No S D D isto é essencial: o teste deriva do critério, não do código — por isso não herda os defeitos da implementação.
E a ferramenta prova essa cadeia. A matriz de rastreabilidade liga cada requisito ao caso de uso que o realiza; e o portão de rastreabilidade verifica automaticamente que todos os trinta e sete requisitos atravessam a especificação, o modelo de dados e a implementação. Nenhum requisito órfão.
E este é o resultado: a aplicação gerada, rodando. O mesmo cálculo de conformidade que rastreamos desde o requisito — área, coeficiente, veredito — agora funcionando sobre um mapa real. Da especificação ao software, rastreável de ponta a ponta. Isto é o S D D, na ferramenta LangNet.