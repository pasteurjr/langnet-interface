# Script de Vídeo — Pipeline SDD na ferramenta LangNet (projeto Uso do Solo)

**Formato:** script para locução automática. **NARRAÇÃO** = fala EXATA a ser lida (siglas soletradas). **PRODUÇÃO** = o que mostrar (menu lateral, funções, onde se escreve). **TRECHO DO DOCUMENTO** = partes reais a exibir. Estilo demonstrativo e didático. **Ordem = navegação real.** **Duração:** ~5:20 (15 cenas).


| Cena | Etapa do pipeline | Entra | Dura |
|---|---|---|---|
| 1 | O sistema e os projetos | 0:00 | 12s |
| 2 | Configurações do Projeto — Framework e Protocolo | 0:12 | 22s |
| 3 | O menu lateral — as etapas do pipeline | 0:34 | 20s |
| 4 | Documentos — o documento de Requisitos | 0:54 | 36s |
| 5 | Especificação — casos de uso, fluxos e matriz | 1:30 | 40s |
| 6 | Modelo de Dados | 2:10 | 22s |
| 7 | Interface & Protótipo | 2:32 | 16s |
| 8 | Agentes & Tarefas | 2:48 | 20s |
| 9 | YAML de Agentes e Tarefas — a rastreabilidade impressa | 3:08 | 26s |
| 10 | Sequência de Tarefas | 3:34 | 22s |
| 11 | Rede de Petri | 3:56 | 14s |
| 12 | Geração de Código | 4:10 | 20s |
| 13 | Casos de Teste & Validação | 4:30 | 18s |
| 14 | Rastreabilidade verificada | 4:48 | 16s |
| 15 | A aplicação gerada | 5:04 | 16s |

---

## Cena 1 · O sistema e os projetos   (0:00 → 0:12 · 12s)

**Telas:** `A0_projetos.png`

**🎙 NARRAÇÃO (fala exata):**

> Esta é uma demonstração de Desenvolvimento Orientado a Especificação — o S D D — na ferramenta LangNet. Aqui estão os projetos: cada um percorre um pipeline completo, do requisito ao código rastreável. Vamos abrir o projeto de gestão do uso do solo.

**🎬 PRODUÇÃO:** Tela Projetos (11 projetos). Um clique curto no card “Uso do Solo v3”. Não se demore.


---

## Cena 2 · Configurações do Projeto — Framework e Protocolo   (0:12 → 0:34 · 22s)

**Telas:** `config_create.png`

**🎙 NARRAÇÃO (fala exata):**

> Antes de tudo, cada projeto define sua arquitetura. Nas configurações você escolhe o framework de agentes: o nosso padrão é o CrewAI, mas também há LangChain, LangGraph, AutoGen e os S D Ks da OpenAI e da Anthropic. E escolhe o protocolo de interoperabilidade entre agentes: o nosso padrão é o O K F, com opções para M C P, A dois A, A C P e A N P. É aqui que se decide sobre qual base o sistema será gerado.

**🎬 PRODUÇÃO:** Modal “Criar Novo Projeto” (o mesmo abre em “Editar”, nas Configurações do Projeto). Em Opções Avançadas, destaque os dois seletores: Framework (CrewAI — padrão) e Protocolo (OKF — padrão). Abra rapidamente cada um para mostrar as opções.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Framework (padrão CrewAI):  CrewAI · LangChain · LangGraph · AutoGen · OpenAI SDK · Anthropic SDK
Protocolo (padrão OKF):     OKF (nosso) · MCP · A2A · ACP · ANP
```


---

## Cena 3 · O menu lateral — as etapas do pipeline   (0:34 → 0:54 · 20s)

**Telas:** `sidebar.png`

**🎙 NARRAÇÃO (fala exata):**

> Ao abrir o projeto, o menu lateral revela o pipeline inteiro. Cada item é uma etapa, na ordem: Documentos, onde tudo começa; Especificação; Modelo de Dados; Interface e Protótipo; Agentes e Tarefas; o YAML de Agentes e Tarefas; a Sequência de Tarefas; a Rede de Petri; a Geração de Código; e os Casos de Teste e Validação. Deploy e Monitoramento fecham a operação. Vamos entrar em cada uma e ver o que cada documento contém.

**🎬 PRODUÇÃO:** Barra lateral do projeto, seção PIPELINE (Documentos … Casos de Teste) + OPERAÇÃO. Percorra de cima a baixo com leve destaque.


---

## Cena 4 · Documentos — o documento de Requisitos   (0:54 → 1:30 · 36s)

**Telas:** `doc_stage.png`, `req_fr.png`, `req_nfr.png`

**🎙 NARRAÇÃO (fala exata):**

> A primeira etapa é Documentos. Você traz os arquivos de origem — inclusive a legislação municipal — e a ferramenta gera o documento de Requisitos. Ele tem três partes que importam. Primeiro, os requisitos funcionais: o que o sistema deve fazer, cada um com identificador e prioridade — repare no F R zero dezesseis, o cálculo do coeficiente de aproveitamento, que vamos seguir até o código. Segundo, os não-funcionais: as metas de qualidade, como escalar para cem municípios, mapa em menos de cinco segundos e precisão geométrica. E terceiro, algo que costuma passar batido: a ferramenta detecta conflitos e ambiguidades entre os documentos de origem, e propõe a resolução — aqui, por exemplo, unificar o sistema de coordenadas.

**🎬 PRODUÇÃO:** Tela Documentos: arquivos-fonte + “🚀 Iniciar Análise”. Depois abra o documento de Requisitos: role pela tabela de Requisitos Funcionais (destaque FR-016), pela de Não-Funcionais, e pela seção “Verificações Complementares” (conflitos e ambiguidades detectados).

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
REQUISITOS FUNCIONAIS (trecho real)          |  NÃO-FUNCIONAIS (trecho real)
  FR-015  Zoneamento poligonal        Alta   |   NFR-001  Escalabilidade  100 municípios
  FR-016  Cálculo de CA (Coef. Aprov.) Alta  |   NFR-002  Performance     mapa < 5 s
  FR-017  Cálculo de TO               Alta   |   NFR-003  Usabilidade     tarefa ≤ 3 min
  FR-018  Cálculo e Validação de Recuos Alta |   NFR-013  Precisão geom.  < 0,01 m (SRID 4674)

VERIFICAÇÕES COMPLEMENTARES (a ferramenta detecta e resolve):
  CON-002  Diferença de SRID entre v2 e v3  → Resolução: adotar SRID 4674 (SIRGAS 2000)
  AMB-001  “Agentes de IA” (FR-005) é vago  → Pergunta: qual tecnologia de IA será usada?
```


---

## Cena 5 · Especificação — casos de uso, fluxos e matriz   (1:30 → 2:10 · 40s)

**Telas:** `S_uc.png`, `S_flux.png`, `spec_matriz.png`

**🎙 NARRAÇÃO (fala exata):**

> Dos requisitos deriva a Especificação Funcional — o documento primário do S D D. Ela detalha os casos de uso. Cada caso de uso traz o ator, o objetivo, os requisitos relacionados e três fluxos: o principal, o passo a passo normal; os alternativos, os caminhos válidos diferentes; e os de exceção, o tratamento de erros. No caso de uso zero zero um, o fluxo principal calcula o coeficiente, dá dois vírgula cinco contra o limite de dois, e conclui não conforme; um fluxo alternativo permite simular um ajuste e voltar a conforme. E, ao final, a especificação traz a matriz de rastreabilidade, que liga cada requisito ao caso de uso que o realiza. É esta matriz que garante que nada se perde.

**🎬 PRODUÇÃO:** Documento de Especificação. Mostre o UC-001: tabela com Ator, Objetivo e “RFs Relacionados: FR-016…”; depois os Fluxos Alternativos e de Exceção; e por fim role até a seção 13, a Matriz de Rastreabilidade (Requisito → UC que o realiza).

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
UC-001 — Consulta de Conformidade Consolidada (trecho real)
  RFs Relacionados: FR-016, FR-017, FR-018, FR-019…    RNs: BR-006, BR-007
  Fluxo Principal (passo 2): CA = 500 m² / 200 m² = 2,5 · limite 2,0 → NÃO CONFORME
  Alternativos: A2 “Simular” → 400 m² → CA 2,0 → CONFORME   |  Exceção: E1 geometria inválida

MATRIZ DE RASTREABILIDADE (seção 13, trecho real)
  Requisito | Seção Espec. | UC que o realiza | RN
  FR-001    | 5.2, UC-001  | UC-001           | RN-002
  FR-016    | 5.2, UC-001  | UC-001           | (cálculo de CA)
```


---

## Cena 6 · Modelo de Dados   (2:10 → 2:32 · 22s)

**Telas:** `dm_stage.png`

**🎙 NARRAÇÃO (fala exata):**

> Da especificação deriva o Modelo de Dados: as entidades, o esquema, os modelos e as migrações — aqui, um banco geográfico. Três tabelas contam a história: municípios, a raiz; zoneamentos, com a coluna de geometria em coordenadas oficiais; e parâmetros urbanísticos, que guarda, por zona, o coeficiente máximo e a taxa de ocupação. É desta última que o cálculo do F R zero dezesseis lê os limites. E o sistema valida o esquema automaticamente.

**🎬 PRODUÇÃO:** Tela Modelo de Dados: à esquerda o painel (DBMS PostgreSQL, Regenerar/Revisar); à direita as entidades. Destaque “zoneamentos.geometria” e “parametros_urbanisticos” (ca_maximo, to_maxima). Se der, abra a aba “Schema SQL”.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Modelo de Dados (trecho real)
  zoneamentos.geometria        geometry(Geometry, 4674)   -- PostGIS · SIRGAS 2000
  parametros_urbanisticos.ca_maximo   DECIMAL(10,2)       -- limite de CA por zona (FR-016)
  parametros_urbanisticos.to_maxima   DECIMAL(10,2)       -- limite de TO por zona (FR-017)
  (o cálculo faz JOIN zoneamentos × parametros × imoveis via ST_Contains da geometria)
```


---

## Cena 7 · Interface & Protótipo   (2:32 → 2:48 · 16s)

**Telas:** `ui_stage.png`, `03_ui_spec.png`

**🎙 NARRAÇÃO (fala exata):**

> Antes do código, a ferramenta gera o protótipo de interface — uma tela para cada caso de uso. Cada tela nasce amarrada ao seu caso de uso; esta, de resultado de conformidade, é o mesmo caso de uso zero zero um, com o mapa e o resumo do coeficiente, da ocupação e da preservação.

**🎬 PRODUÇÃO:** Tela Interface e Protótipo: à esquerda a lista de telas e o painel “Gerar UI Spec”; à direita o mockup da tela de conformidade (mapa + cards de CA/TO/APP).


---

## Cena 8 · Agentes & Tarefas   (2:48 → 3:08 · 20s)

**Telas:** `at_stage.png`, `05_agent_task.png`

**🎙 NARRAÇÃO (fala exata):**

> Agora a ferramenta define a arquitetura de execução: quais agentes existem e quais tarefas cada um realiza. São dez agentes e trinta tarefas. Cada agente é um especialista — por exemplo, o Motor de Cálculo Urbanístico — e cada tarefa já aponta para o caso de uso e os requisitos que atende. É a ponte entre o que o sistema deve fazer e como ele fará.

**🎬 PRODUÇÃO:** Tela Agentes e Tarefas: o painel (Nível de Detalhamento, framework, “Gerar Agentes & Tarefas”) e o documento com a tabela de agentes (AG-01 a AG-10) e as tarefas com seu UC/RF.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Especificação de Agentes & Tarefas (trecho real)
  Agente: calculo_urbano_agent — “Motor de Cálculo Urbanístico”
  Tarefa: calculate_urban_compliance → UC-001 · FR-016..FR-019 · execução determinística
```


---

## Cena 9 · YAML de Agentes e Tarefas — a rastreabilidade impressa   (3:08 → 3:34 · 26s)

**Telas:** `yaml_stage.png`, `04_yaml_agents.png`, `06_yaml_tasks.png`

**🎙 NARRAÇÃO (fala exata):**

> A especificação vira arquivos executáveis: o agents ponto yaml e o tasks ponto yaml. No agents, cada agente ganha papel, objetivo e história — veja o Motor de Cálculo, um engenheiro que é determinístico: se o número não bate, é não conforme. E no tasks está o coração do S D D: cada tarefa carrega a própria rastreabilidade. A tarefa de conformidade traz, escrito no arquivo, o caso de uso zero zero um e os requisitos F R zero dezesseis a dezenove — e até a consulta espacial que ela executa. O requisito não se perdeu: está impresso dentro da tarefa.

**🎬 PRODUÇÃO:** Tela YAML. Mostre o agents.yaml (agente calculo_urbano_agent: role/goal/backstory) e depois o tasks.yaml (task calculate_urban_compliance: traceability, execution e a query com o JOIN espacial).

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
agents.yaml (trecho real)                 |  tasks.yaml (trecho real)
calculo_urbano_agent:                     |  calculate_urban_compliance:
  role: Motor de Cálculo Urbanístico      |    traceability: { uc: UC-001, fr: [FR-016..FR-019] }
  goal: Calcular e validar CA, TO,        |    execution: deterministic
        Recuos e Gabarito                 |    agent: calculo_urbano_agent
  backstory: engenheiro civil…            |    query: SELECT … FROM zoneamentos z
    “se o número não bate, é NÃO CONFORME”|      JOIN parametros_urbanisticos p ON p.zona_id=z.id
                                          |      … WHERE ST_Contains(z.geometria, i.geometria)
```


---

## Cena 10 · Sequência de Tarefas   (3:34 → 3:56 · 22s)

**Telas:** `seq_stage.png`, `seq_doc.png`

**🎙 NARRAÇÃO (fala exata):**

> Antes da Rede de Petri vem uma etapa essencial, que deriva diretamente dos agentes e das tarefas: a Sequência de Tarefas. Ela define a ordem exata de execução — aqui, quinze tarefas. Começa importando os geodados do zoneamento e dos imóveis, passa pelo cálculo de conformidade, que é a tarefa seis, o nosso F R zero dezesseis, e segue até o laudo. A ferramenta identifica o que pode rodar em paralelo e liga a saída de cada tarefa à entrada da seguinte, num estado compartilhado. É esta sequência — e não um salto — que alimenta a Rede de Petri.

**🎬 PRODUÇÃO:** Tela Sequência de Tarefas: o painel (origem “Specs & Docs”, Gerar/Revisar) e, à direita, o fluxo gerado “task_flow … v1”. Abra o Histórico para mostrar “Concluído · 15 tarefas · Paralelismo: Sim”. Role o documento do fluxo pela lista ordenada de tarefas.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Fluxo de Execução — Sequência de Tarefas (trecho real · 15 tarefas · com paralelismo)
  Task 1  import_zoneamento_geodata      → geodados_import_agent   (importação inicial)
  Task 2  import_imoveis_geodata         → geodados_import_agent
  Task 4  update_parametros_urbanisticos → parâmetros CA/TO por zona
  Task 6  calculate_urban_compliance     → calculo_urbano_agent   (UC-001 · FR-016)
  Task 7  calculate_app_overlap          → cálculo espacial de APP
  …                                       (a saída de cada tarefa entra no State da seguinte)
```


---

## Cena 11 · Rede de Petri   (3:56 → 4:10 · 14s)

**Telas:** `petri_stage.png`

**🎙 NARRAÇÃO (fala exata):**

> Essa sequência é formalizada como uma Rede de Petri. Cada transição é uma tarefa; os tokens percorrem a rede do início ao fim. É uma orquestração que pode ser verificada formalmente, e não apenas testada.

**🎬 PRODUÇÃO:** Editor da Rede de Petri: o “Início do Fluxo” com o token, as transições (tarefas) e o “Fim do Fluxo”. Opcional: um clique em Simular para o token avançar.


---

## Cena 12 · Geração de Código   (4:10 → 4:30 · 20s)

**Telas:** `code_stage.png`, `12_code_real.png`

**🎙 NARRAÇÃO (fala exata):**

> Só então vem o código — o artefato derivado. A ferramenta gera o projeto inteiro, dezenas de arquivos. E aqui está a função que calcula a conformidade: a mesma consulta espacial da tarefa, com o JOIN entre a geometria do lote e a zona, e a classificação em conforme ou não conforme. É o requisito F R zero dezesseis, que vimos no começo, agora executável.

**🎬 PRODUÇÃO:** Tela Geração de Código: a árvore de arquivos à esquerda e o editor à direita. Enquadre a função calculate_urban_compliance, com o JOIN espacial e a linha do status conforme / não conforme.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Código gerado (trecho real)
  def calculate_urban_compliance(imovel_id):
      SELECT z.nome, p.ca_maximo, p.to_maxima FROM zoneamentos z
        JOIN parametros_urbanisticos p ON p.zona_id = z.id
        JOIN imoveis i ON i.id = %s WHERE ST_Contains(z.geometria, i.geometria)
      ca = area_construida / area_terreno
      status = 'conforme' if ca <= ca_maximo else 'nao_conforme'
```


---

## Cena 13 · Casos de Teste & Validação   (4:30 → 4:48 · 18s)

**Telas:** `tests_stage.png`

**🎙 NARRAÇÃO (fala exata):**

> Os casos de teste nascem dos casos de uso, pela técnica do grafo de causa e efeito. As causas são as ações do usuário; os efeitos, as respostas do sistema; e cada combinação vira um caso de teste. No S D D isto é essencial: o teste deriva do critério, não do código — por isso não herda os defeitos da implementação. Aqui, do caso de uso zero zero um saem cinco causas, seis efeitos e seis casos de teste.

**🎬 PRODUÇÃO:** Tela Casos de Teste: a lista de casos de uso à esquerda e, à direita, o Grafo de Causa-Efeito do UC-001, com as causas e efeitos ligados e a contagem de casos.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Grafo de Causa-Efeito — UC-001 (trecho real)
  Causas (ações): c1 selecionar imóvel · c2 geometria válida · c3 zona com parâmetros
  Efeitos (respostas): e1 CA calculado · e2 status conforme/não conforme · e3 laudo gerado
  → 5 causas · 6 efeitos · 6 casos de teste derivados
```


---

## Cena 14 · Rastreabilidade verificada   (4:48 → 5:04 · 16s)

**Telas:** `gate_verde.png`

**🎙 NARRAÇÃO (fala exata):**

> E a ferramenta prova a cadeia inteira. O portão de rastreabilidade verifica automaticamente que todos os trinta e sete requisitos atravessam a especificação, o modelo de dados e a implementação. Nenhum requisito órfão, nenhuma tarefa sem origem. É a garantia de que o software é fiel à especificação.

**🎬 PRODUÇÃO:** Mostre o portão de rastreabilidade em VERDE — 37 de 37, todos os saltos OK. Congele por 3 segundos.

**📄 TRECHO DO DOCUMENTO (exibir na tela):**

```
Portão de Rastreabilidade (real)
  FR-016 → UC-001 → task calculate_urban_compliance → código
  37/37 requisitos · Req→Spec, Matriz FR→UC, FR→Implementação, Task→código: OK
```


---

## Cena 15 · A aplicação gerada   (5:04 → 5:20 · 16s)

**Telas:** `01-app-home.png`

**🎙 NARRAÇÃO (fala exata):**

> E este é o resultado: a aplicação gerada, rodando. O mesmo cálculo de conformidade que rastreamos desde o requisito — área, coeficiente, veredito — agora funcionando sobre um mapa real. Da especificação ao software, rastreável de ponta a ponta. Isto é o S D D, na ferramenta LangNet.

**🎬 PRODUÇÃO:** Aplicação gerada no navegador: a tela inicial e o resultado de conformidade. Se der, um cálculo rápido resultando em “conforme”. Encerre com o título.


---

## Locução corrida (só as falas, para colar no gerador de voz)

Esta é uma demonstração de Desenvolvimento Orientado a Especificação — o S D D — na ferramenta LangNet. Aqui estão os projetos: cada um percorre um pipeline completo, do requisito ao código rastreável. Vamos abrir o projeto de gestão do uso do solo.
Antes de tudo, cada projeto define sua arquitetura. Nas configurações você escolhe o framework de agentes: o nosso padrão é o CrewAI, mas também há LangChain, LangGraph, AutoGen e os S D Ks da OpenAI e da Anthropic. E escolhe o protocolo de interoperabilidade entre agentes: o nosso padrão é o O K F, com opções para M C P, A dois A, A C P e A N P. É aqui que se decide sobre qual base o sistema será gerado.
Ao abrir o projeto, o menu lateral revela o pipeline inteiro. Cada item é uma etapa, na ordem: Documentos, onde tudo começa; Especificação; Modelo de Dados; Interface e Protótipo; Agentes e Tarefas; o YAML de Agentes e Tarefas; a Sequência de Tarefas; a Rede de Petri; a Geração de Código; e os Casos de Teste e Validação. Deploy e Monitoramento fecham a operação. Vamos entrar em cada uma e ver o que cada documento contém.
A primeira etapa é Documentos. Você traz os arquivos de origem — inclusive a legislação municipal — e a ferramenta gera o documento de Requisitos. Ele tem três partes que importam. Primeiro, os requisitos funcionais: o que o sistema deve fazer, cada um com identificador e prioridade — repare no F R zero dezesseis, o cálculo do coeficiente de aproveitamento, que vamos seguir até o código. Segundo, os não-funcionais: as metas de qualidade, como escalar para cem municípios, mapa em menos de cinco segundos e precisão geométrica. E terceiro, algo que costuma passar batido: a ferramenta detecta conflitos e ambiguidades entre os documentos de origem, e propõe a resolução — aqui, por exemplo, unificar o sistema de coordenadas.
Dos requisitos deriva a Especificação Funcional — o documento primário do S D D. Ela detalha os casos de uso. Cada caso de uso traz o ator, o objetivo, os requisitos relacionados e três fluxos: o principal, o passo a passo normal; os alternativos, os caminhos válidos diferentes; e os de exceção, o tratamento de erros. No caso de uso zero zero um, o fluxo principal calcula o coeficiente, dá dois vírgula cinco contra o limite de dois, e conclui não conforme; um fluxo alternativo permite simular um ajuste e voltar a conforme. E, ao final, a especificação traz a matriz de rastreabilidade, que liga cada requisito ao caso de uso que o realiza. É esta matriz que garante que nada se perde.
Da especificação deriva o Modelo de Dados: as entidades, o esquema, os modelos e as migrações — aqui, um banco geográfico. Três tabelas contam a história: municípios, a raiz; zoneamentos, com a coluna de geometria em coordenadas oficiais; e parâmetros urbanísticos, que guarda, por zona, o coeficiente máximo e a taxa de ocupação. É desta última que o cálculo do F R zero dezesseis lê os limites. E o sistema valida o esquema automaticamente.
Antes do código, a ferramenta gera o protótipo de interface — uma tela para cada caso de uso. Cada tela nasce amarrada ao seu caso de uso; esta, de resultado de conformidade, é o mesmo caso de uso zero zero um, com o mapa e o resumo do coeficiente, da ocupação e da preservação.
Agora a ferramenta define a arquitetura de execução: quais agentes existem e quais tarefas cada um realiza. São dez agentes e trinta tarefas. Cada agente é um especialista — por exemplo, o Motor de Cálculo Urbanístico — e cada tarefa já aponta para o caso de uso e os requisitos que atende. É a ponte entre o que o sistema deve fazer e como ele fará.
A especificação vira arquivos executáveis: o agents ponto yaml e o tasks ponto yaml. No agents, cada agente ganha papel, objetivo e história — veja o Motor de Cálculo, um engenheiro que é determinístico: se o número não bate, é não conforme. E no tasks está o coração do S D D: cada tarefa carrega a própria rastreabilidade. A tarefa de conformidade traz, escrito no arquivo, o caso de uso zero zero um e os requisitos F R zero dezesseis a dezenove — e até a consulta espacial que ela executa. O requisito não se perdeu: está impresso dentro da tarefa.
Antes da Rede de Petri vem uma etapa essencial, que deriva diretamente dos agentes e das tarefas: a Sequência de Tarefas. Ela define a ordem exata de execução — aqui, quinze tarefas. Começa importando os geodados do zoneamento e dos imóveis, passa pelo cálculo de conformidade, que é a tarefa seis, o nosso F R zero dezesseis, e segue até o laudo. A ferramenta identifica o que pode rodar em paralelo e liga a saída de cada tarefa à entrada da seguinte, num estado compartilhado. É esta sequência — e não um salto — que alimenta a Rede de Petri.
Essa sequência é formalizada como uma Rede de Petri. Cada transição é uma tarefa; os tokens percorrem a rede do início ao fim. É uma orquestração que pode ser verificada formalmente, e não apenas testada.
Só então vem o código — o artefato derivado. A ferramenta gera o projeto inteiro, dezenas de arquivos. E aqui está a função que calcula a conformidade: a mesma consulta espacial da tarefa, com o JOIN entre a geometria do lote e a zona, e a classificação em conforme ou não conforme. É o requisito F R zero dezesseis, que vimos no começo, agora executável.
Os casos de teste nascem dos casos de uso, pela técnica do grafo de causa e efeito. As causas são as ações do usuário; os efeitos, as respostas do sistema; e cada combinação vira um caso de teste. No S D D isto é essencial: o teste deriva do critério, não do código — por isso não herda os defeitos da implementação. Aqui, do caso de uso zero zero um saem cinco causas, seis efeitos e seis casos de teste.
E a ferramenta prova a cadeia inteira. O portão de rastreabilidade verifica automaticamente que todos os trinta e sete requisitos atravessam a especificação, o modelo de dados e a implementação. Nenhum requisito órfão, nenhuma tarefa sem origem. É a garantia de que o software é fiel à especificação.
E este é o resultado: a aplicação gerada, rodando. O mesmo cálculo de conformidade que rastreamos desde o requisito — área, coeficiente, veredito — agora funcionando sobre um mapa real. Da especificação ao software, rastreável de ponta a ponta. Isto é o S D D, na ferramenta LangNet.