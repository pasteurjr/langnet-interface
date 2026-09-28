# Roteiro narrado — LangNet e o BioByte Sentinela v5

**O que este vídeo mostra:** o LangNet, que é a fábrica, e o sistema que ele produziu — o
BioByte Sentinela, de vigilância de infecção de corrente sanguínea associada a cateter.

**Pasta das telas:** `docs/apresentacao/demo-biobyte-v5/telas/`
**Registro dos testes:** `registro_de_testes.md` — 22 de 23 casos, conferidos contra o banco
**Como ler:** cada cena traz **a tela** (caminho do arquivo), **a narração** (texto exato,
no tom do narrador) e **a produção** (o que destacar, quanto tempo).
**Duração estimada:** 22 a 25 minutos.

> Regra deste roteiro: nada é narrado que não esteja na tela. Onde o sistema falha, a cena
> mostra a falha.

---

# BLOCO 0 — O que vai ser gerado

## Cena 1 · A fábrica

**Tela:** `telas/A0-painel-projetos.png`

**Narração:**
> Este é o LangNet. Ele não é o sistema que vamos mostrar: ele é a fábrica que produz
> sistemas. Cada projeto aqui dentro é um sistema inteiro — do documento de requisitos até
> o código rodando.
>
> Hoje vamos acompanhar um deles do começo ao fim: o BioByte Sentinela, de vigilância de
> infecção hospitalar.

**Produção:** 14 s.

---

## Cena 2 · As etapas, todas na mesma coluna

**Tela:** `telas/A0b-pipeline-menu.png`

**Narração:**
> E esta é a linha de produção, no menu à esquerda. Documentos. Especificação. Modelo de
> Dados. Interface e Protótipo. Agentes e Tarefas. Ferramentas. Os arquivos de
> configuração. Sequência de Tarefas. Rede de Petri. Geração de Código. Casos de Teste.
> E, na operação, a Execução de Agentes e a Implantação.
>
> Doze etapas. Cada uma consome o que a anterior produziu e entrega um documento que se
> pode ler, conferir e corrigir. É esse caminho que vamos percorrer.

**Produção:** 24 s. Destaque cada etapa do menu de cima para baixo, no ritmo da narração.

---

# BLOCO 1 — O problema e a decisão que mudou tudo

## Cena 3 · O pedido do hospital

**Tela:** `telas/01-documento-fonte.png`

**Narração:**
> Tudo começa com um documento. Este é o levantamento de requisitos do BioByte. Uma médica
> infectologista, uma enfermeira de controle de infecção e um analista de laboratório
> contaram o que precisam. O problema deles é tempo: entre a hemocultura ficar pronta no
> laboratório e alguém perceber que aquele paciente tem uma infecção, às vezes passam dois
> dias. E quando o germe é multirresistente, dois dias é muita coisa.

**Produção:** 14 s. Destaque a citação da médica.

---

## Cena 4 · O documento entra na etapa

**Tela:** `telas/G1-origem-documento.png`

**Narração:**
> O documento é carregado na primeira etapa. A partir daqui, nada mais é digitado à mão:
> cada etapa lê o que a anterior escreveu.

**Produção:** 10 s.

---

## Cena 5 · O que é inteligência artificial e o que não é

**Tela:** `telas/02b-requisitos-coluna-natureza.png`

**Narração:**
> Um sistema hospitalar tem duas metades bem diferentes. Uma é cadastro, consulta,
> relatório — trabalho de sempre, que um programa comum resolve. A outra é julgamento
> clínico: ler um antibiograma e decidir, escrever o alerta que a equipe vai ler. Só essa
> segunda metade é trabalho de agente.
>
> Na versão anterior essa distinção não existia em lugar nenhum, e o sistema tratou
> quarenta e cinco coisas como trabalho de agente — inclusive cadastro de usuário. Agora a
> separação está declarada requisito por requisito.

**Produção:** 26 s. Moldura na coluna de natureza. Esta é a cena mais importante do bloco.

---

# BLOCO 2 — Requisitos

## Cena 6 · Cada requisito diz de onde veio

**Tela:** `telas/02-requisitos-natureza.png`

**Narração:**
> O documento de requisitos não é uma lista solta. Cada item diz a sua origem: extraído dos
> documentos, extraído das instruções do usuário, inferido pelo modelo com justificativa,
> vindo da pesquisa complementar, ou sugerido pela inteligência artificial e ainda
> aguardando aprovação.
>
> São noventa e nove requisitos funcionais, vinte e cinco não-funcionais e trinta e uma
> regras de negócio. Noventa vieram direto da ata; oito foram sugestão do modelo, marcados
> como tal para alguém decidir.
>
> E repare na seção da pesquisa web: ela declara que a pesquisa foi feita, que as fontes
> estão na seção complementar, mas que nenhuma gerou requisito novo — o que foi encontrado
> confirma o que a ata já dizia. O sistema não inventa requisito para parecer completo.

**Produção:** 32 s. Destaque os cabeçalhos das cinco seções de origem, depois o aviso da
pesquisa web.

---

# BLOCO 3 — Especificação

## Cena 7 · Escolher a origem e dar a instrução

**Tela:** `telas/G3-especificacao-geracao.png`

**Narração:**
> A etapa de especificação começa escolhendo de onde ela parte: o documento de requisitos,
> naquela versão. Ao lado, um campo de instruções adicionais — aqui está escrito "detalhar
> os fluxos de exceção de cada caso de uso agêntico e citar a regra de negócio aplicada".
>
> É assim em toda etapa: escolhe-se a origem, dá-se a instrução, e gera. O que sair fica
> versionado, e a versão anterior não se perde.

**Produção:** 22 s. Destaque o seletor de origem e depois o campo de instruções.

---

## Cena 8 · O caso de uso gerado

**Tela:** `telas/H1-especificacao-casos-de-uso.png`

**Narração:**
> Trinta e um casos de uso. Cada um traz ator principal, objetivo, pré e pós-condições, e o
> fluxo principal escrito como diálogo: a ação do ator de um lado, a resposta do sistema do
> outro.

**Produção:** 20 s. Destaque o fluxo principal com as duas colunas.

---

## Cena 9 · Os fluxos de exceção e o croqui

**Telas:** `telas/H2-especificacao-fluxo-excecao.png`, `telas/03b-caso-de-uso-natureza.png`

**Narração:**
> Cada caso de uso traz também os fluxos alternativos, os de exceção, e um croqui da tela
> aderente a essas ações — os botões do desenho são as ações do fluxo.
>
> E cada um aponta o requisito de onde nasceu, declara a sua natureza e, quando é de
> agente, declara o que exatamente o agente decide.

**Produção:** 24 s. Corte do fluxo de exceção para o croqui, depois para as linhas de
Natureza e Decisão do Agente.

---

# BLOCO 4 — Modelo de dados, e uma correção por conversa

## Cena 10 · A origem e a geração

**Tela:** `telas/G4-modelo-dados-geracao.png`

**Narração:**
> O modelo de dados parte da especificação — e a tela diz qual, com data e hora. Escolhe-se
> o banco de destino, dá-se a instrução, e gera.

**Produção:** 16 s. Destaque a barra de origem e o seletor de banco.

---

## Cena 11 · As tabelas

**Telas:** `telas/M1-modelo-entidades.png`, `telas/M2-modelo-schema-sql.png`

**Narração:**
> O resultado vem em quatro formas, em abas: as entidades com os seus relacionamentos, o
> esquema em SQL, as classes em Python e a migração. Vinte e oito tabelas, vinte e nove
> chaves estrangeiras, oitenta e cinco índices.

**Produção:** 22 s. Corte da aba de entidades para a do esquema SQL.

---

## Cena 12 · A etapa aponta os próprios defeitos

**Tela:** `telas/R5-modelo-historico-versoes.png`

**Narração:**
> E a etapa não se dá por satisfeita sozinha. Ela valida o que produziu e dá uma nota:
> setenta e cinco em cem, quinze problemas. Um deles diz, com todas as letras: a coluna de
> escore está sem precisão declarada, o banco vai assumir número inteiro e truncar as casas
> decimais.
>
> É um defeito de verdade. Um escore de zero vírgula seis dois viraria um.

**Produção:** 22 s. Destaque o problema apontado pelo validador.

---

## Cena 13 · Pedindo a correção em português

**Tela:** `telas/R2-modelo-pedido.png`

**Narração:**
> Para corrigir, não se edita arquivo. Pede-se ao agente da etapa, escrevendo:
>
> "As colunas escore médio e conformidade mensal do painel de vigilância, e redução média
> de risco dos pacotes, estão como decimal sem casas e não guardam fração: um escore de
> zero vírgula seis dois vira um. Troque as três para decimal com duas casas."

**Produção:** 22 s. Mostre o texto sendo digitado no campo de refino.

---

## Cena 14 · A versão nova

**Telas:** `telas/R4-modelo-coluna-corrigida.png`, `telas/R5-modelo-historico-versoes.png`

**Narração:**
> O agente leu o esquema, entendeu o pedido e gerou a versão dois. As três colunas agora
> guardam duas casas decimais. A versão um continua lá, no histórico — nada foi
> sobrescrito.
>
> Isto é o ciclo de trabalho: gerar, conferir, pedir a correção em português, aprovar.

**Produção:** 24 s. Destaque a coluna corrigida e, depois, as duas versões no histórico.

---

# BLOCO 5 — Interface e protótipo

## Cena 15 · A geração das telas

**Tela:** `telas/G5-interface-geracao.png`

**Narração:**
> A etapa de interface desenha as telas a partir dos casos de uso. Aqui também se escreve a
> instrução antes de gerar: "na tela de alerta, preencher a gravidade como alta quando
> houver multirresistência".

**Produção:** 16 s.

---

## Cena 16 · As trinta telas

**Tela:** `telas/07-interface-telas.png`

**Narração:**
> Trinta telas, quinhentos e noventa e sete componentes declarados — indicadores, tabelas,
> gráficos, campos, marcações. Os trinta e um casos de uso estão cobertos.

**Produção:** 15 s.

---

## Cena 17 · O protótipo, antes de existir sistema

**Tela:** `telas/73-prototipo-tela.png`

**Narração:**
> E antes de gerar uma linha de código do sistema, as telas já podem ser navegadas. Isto é
> o protótipo: as mesmas trinta telas, ligadas pelo menu, com dados de exemplo. Aqui está a
> trilha de auditoria — filtros por período e por usuário, a verificação de integridade do
> encadeamento, e as entradas com a marca da entrada anterior.
>
> É o que a tela deve fazer. Guarde esta imagem: vamos rever esta mesma tela no sistema
> gerado.

**Produção:** 24 s. Destaque o selo "Encadeamento íntegro · 1.284 entradas verificadas".

---

# BLOCO 6 — Agentes, tarefas e ferramentas

## Cena 18 · Quem implementa cada ferramenta

**Tela:** `telas/61-ferramentas-resultado.png`

**Narração:**
> Antes de gerar o sistema, uma pergunta precisa de resposta: cada ferramenta que os
> agentes vão usar, de onde vem a implementação? Esta etapa faz o inventário. Três
> ferramentas — consulta ao banco, leitura de dados estruturados e busca por semelhança — e
> as três com implementação declarada, nenhuma pendente.
>
> Não é burocracia. Um agente montado sem ferramenta responde, educadamente, que não
> conseguiu obter o dado.

**Produção:** 20 s.

---

## Cena 19 · Cinco tarefas, dois agentes

**Telas:** `telas/G6-agentes-tarefas-geracao.png`, `telas/04b-cinco-tarefas-dois-agentes.png`

**Narração:**
> A etapa de agentes e tarefas parte da especificação. Trinta e um casos de uso entraram;
> seis são de agente; e saíram cinco tarefas em dois agentes. Traduzir o resultado do
> laboratório para o vocabulário do hospital. Classificar o caso pelo critério da norma.
> Avaliar multirresistência. Recomendar o pacote de medidas com justificativa. Redigir o
> alerta para a equipe.
>
> Cinco. Na versão anterior eram quarenta e cinco.

**Produção:** 24 s.

---

## Cena 20 · Cada tarefa sabe de onde veio

**Tela:** `telas/H6-ats-rastreabilidade.png`

**Narração:**
> E cada tarefa carrega a sua ficha completa: o agente que a executa, as ferramentas que
> usa, o formato da entrada e o da saída, as restrições, os casos de borda — e a
> rastreabilidade: o caso de uso que implementa e os requisitos que atende, pelo número.

**Produção:** 22 s. Destaque as linhas de UC Relacionado e RF Relacionado.

---

## Cena 21 · Os arquivos de configuração

**Telas:** `telas/G7-yaml-geracao.png`, `telas/05-yaml-crewai.png`

**Narração:**
> As tarefas viram dois arquivos no formato que o CrewAI entende. Um descreve os agentes —
> papel, objetivo, história. O outro descreve as tarefas — o que fazer e o que se espera de
> saída. Nada além disso: quem executa cada tarefa e com quais ferramentas é decidido na
> geração do código.

**Produção:** 18 s. Destaque `description` e `expected_output`.

---

## Cena 22 · A sequência de tarefas

**Telas:** `telas/G8-sequencia-tarefas.png`, `telas/H5-sequencia-documento.png`

**Narração:**
> Antes da rede, a sequência: em que ordem as tarefas acontecem, o que cada uma precisa
> receber e o que entrega à seguinte. É daqui que sai o desenho do fluxo.

**Produção:** 18 s.

---

# BLOCO 7 — A planta e o código

## Cena 23 · A rede de Petri

**Telas:** `telas/G9-petri-geracao.png`, `telas/H7-petri-estrutura.png`, `telas/08-rede-de-petri.png`

**Narração:**
> A rede de Petri é gerada da sequência. Sete lugares, seis transições. Cada lugar é uma
> tarefa de agente esperando a sua vez; cada transição é a regra que libera a próxima. A
> marca só avança quando o lugar anterior concluiu de verdade.
>
> E ela não é um desenho: é uma estrutura, com o código de cada lugar dentro. É isso que
> vai ser executado.

**Produção:** 26 s. Corte da tela de geração para a estrutura em texto, depois para o
desenho.

---

## Cena 24 · De onde saem os casos de teste

**Tela:** `telas/64-grafo-causa-efeito.png`

**Narração:**
> Os casos de teste não são escritos à mão. Esta etapa lê cada caso de uso e monta um grafo
> de causa e efeito. À esquerda, as causas: as ações do ator e as condições do mundo. À
> direita, os efeitos: o que o sistema responde. No meio, as combinações — este efeito só
> acontece se estas causas forem verdadeiras e aquela for falsa.

**Produção:** 22 s. Siga os arcos de um efeito até as causas. Mostre um círculo de negação.

---

## Cena 25 · A tabela de decisão e o caso pronto

**Telas:** `telas/65-tabela-de-decisao.png`, `telas/66-casos-de-teste-texto.png`

**Narração:**
> Do grafo sai a tabela de decisão. Cada coluna é uma combinação possível — e cada coluna
> vira um caso de teste. Trinta e um casos de uso, quatrocentos e vinte e três casos de
> teste. E cada caso vem escrito: as entradas, que são as ações do ator, e a resposta
> esperada do sistema.

**Produção:** 22 s.

---

## Cena 26 · O sistema sai pronto

**Telas:** `telas/G10-codigo-geracao.png`, `telas/09-codigo-gerado.png`

**Narração:**
> A geração de código monta o sistema inteiro: o servidor dos agentes, a interface do
> hospital, o banco com o seu esquema, os cadastros e a ligação entre tudo. Cento e trinta
> e sete arquivos.

**Produção:** 14 s.

---

# BLOCO 8 — A aplicação funcionando

> Nota de produção: daqui em diante nada é maquete. É o sistema implantado, com banco de
> dados de verdade e dois casos clínicos plantados.

## Cena 27 · O menu do sistema gerado

**Tela:** `telas/E0-app-menu.png`

**Narração:**
> Esta é a interface do hospital. Atendimento, engajamento, relatórios, integrações,
> cadastros. Repare na marcação: o losango indica a tela que chama um agente; o ponto, a
> tela convencional. A separação que começou no documento chegou até o menu lateral.

**Produção:** 20 s. Destaque dois itens lado a lado, um com losango e um sem.

---

## Cena 28 · O cadastro funcionando

**Tela:** `telas/E1-cadastro-pacientes.png`

**Narração:**
> Cadastro de pacientes, com os registros vindos do banco. Novo, Ver, Editar, Excluir.
> Isto não é tela de exemplo: a lista é uma consulta ao banco, e o que se grava aqui
> aparece nas outras telas.
>
> Rodamos o ciclo completo — listar, criar, ler, alterar e excluir — em três entidades, e
> conferimos cada passo contra a linha no banco, não contra a resposta da tela. Quinze
> casos, quinze aprovados.

**Produção:** 22 s.

---

## Cena 29 · Os relatórios

**Telas:** `telas/N1-relatorio-vigilancia.png`, `telas/N2-painel-vigilancia.png`

**Narração:**
> Os relatórios de vigilância, com o período, o formato e a quantidade de registros. E o
> painel, com os casos ativos, o escore médio, a distribuição das classificações e os
> alertas em aberto.

**Produção:** 18 s.

---

## Cena 30 · Os registros que os agentes produziram

**Telas:** `telas/E2-cadastro-classificacoes.png`, `telas/N3-alertas.png`, `telas/E4-notificacoes.png`

**Narração:**
> E aqui estão os registros que o sistema produziu. As classificações, com o critério
> aplicado e a justificativa. O alerta de multirresistência, com o texto redigido pelo
> agente. As notificações enviadas à equipe — duas entregues, uma com falha registrada e o
> motivo.
>
> Nada disso foi digitado: é o resultado do trabalho dos agentes, gravado.

**Produção:** 24 s. Destaque a notificação que falhou e a coluna de motivo.

---

## Cena 31 · A trilha de auditoria

**Tela:** `telas/E3-trilha-auditoria.png`

**Narração:**
> É a mesma tela que vimos no protótipo, agora com dados de verdade. A trilha encadeada:
> cada entrada guarda a marca da entrada anterior — mexer no histórico quebra a corrente e
> fica detectável. Dez eventos do ciclo: o login, a importação da hemocultura, a tradução,
> a classificação, a avaliação de multirresistência, o alerta, a notificação, a
> recomendação e a exportação.

**Produção:** 22 s. Destaque a coluna da marca anterior.

---

# BLOCO 9 — Os agentes trabalhando

## Cena 32 · O agente traduz o resultado do laboratório

**Tela:** `telas/E5-agente-traducao.png`

**Narração:**
> Agora a parte de inteligência artificial. O operador escolhe o caso — e repare que a
> lista traz os casos que existem no banco, não exemplos — e aperta Traduzir.
>
> O agente vai ao banco, encontra o resultado bruto, traduz a nomenclatura do laboratório
> para o vocabulário do hospital e diz se o resultado é aproveitável. A resposta vem com a
> versão do prompt que a produziu, para que a decisão possa ser rastreada depois.

**Produção:** 24 s. Destaque o seletor com o caso real e, na resposta, a versão do prompt.

---

## Cena 33 · O agente classifica pelo critério da norma

**Tela:** `telas/E6-agente-classificacao.png`

**Narração:**
> A classificação pelo critério do NHSN. O agente aplica o critério vigente à data do caso
> — não o de hoje — e devolve confirmada, descartada ou pendente, com a justificativa e o
> critério citado pelo nome e pela versão.

**Produção:** 20 s.

---

## Cena 34 · O agente se recusa a inventar

**Tela:** `telas/E7-agente-alerta.png`

**Narração:**
> E esta é a cena que mais importa. Pedimos ao agente que redija o alerta de
> multirresistência para um caso que não é multirresistente. Ele olhou o antibiograma,
> contou as classes, e respondeu:
>
> "Caso sem multirresistência registrada — apenas uma classe resistente, fluoroquinolona,
> abaixo do limiar de três classes distintas. Não é possível redigir alerta afirmativo sem
> inventar dado clínico."
>
> Ele contou, aplicou a regra e recusou, citando a regra de negócio pelo número. Um sistema
> que inventa é pior do que um sistema que não responde.

**Produção:** 30 s. Destaque o motivo da insuficiência inteiro. Esta cena sustenta o vídeo.

---

# BLOCO 10 — A Bancada de Execução

> Nota: a Bancada é a segunda interface. A do hospital é para quem atende; a Bancada é
> nossa, para ver a orquestração por dentro.

## Cena 35 · A rede carregada

**Tela:** `telas/B0-bancada-inicio.png`

**Narração:**
> A Bancada de Execução. A rede de Petri aparece inteira e roda diante de nós. Não é
> animação: cada lugar abre uma conversa com o servidor dos agentes, manda a tarefa e
> espera a resposta. No painel, o projeto, o endereço do servidor que está no ar e as cinco
> tarefas desta rede.

**Produção:** 20 s.

---

## Cena 36 · A marca andando

**Telas:** `telas/B1-marca-P1.png`, `telas/B2-marca-P2.png`, `telas/B3-marca-P3.png`, `telas/B4-marca-P4.png`, `telas/B5-marca-P5.png`

**Narração:**
> A marca sai do início e entra na primeira tarefa: traduzir o resultado do laboratório.
> Concluída, a transição libera a próxima: classificar o caso. Depois, avaliar
> multirresistência. Recomendar o pacote. Redigir o alerta. Cada passagem dessas é uma
> tarefa de verdade sendo executada contra o banco de verdade.

**Produção:** 26 s, cortando entre as capturas no ritmo da narração.

---

## Cena 37 · O log de disparos

**Tela:** `telas/41-bancada-log-disparos.png`

**Narração:**
> O simulador registra cada disparo: a hora, a transição, e as marcas que saíram de um
> lugar e entraram no outro. É a prova de que a rede executou na ordem que a planta manda.

**Produção:** 18 s.

---

## Cena 38 · Os painéis — entradas, execução e etiquetas

**Tela:** `telas/C3-painel-inputs.png`

**Narração:**
> E aqui está o que o agente recebeu e o que ele devolveu. O acompanhamento mostra a tarefa
> iniciada, o agente começando a trabalhar, o raciocínio, e a saída final.
>
> Embaixo, as etiquetas: nome da tarefa, nome do agente, a entrada que ele recebeu, a
> ferramenta que usou, os passos, a saída, o tipo da saída e a marca de tarefa concluída.
> São onze etiquetas, as mesmas para qualquer sistema que esta fábrica produza.

**Produção:** 28 s. Percorra a linha de etiquetas extraídas, uma a uma.

---

## Cena 39 · Falha não passa calada

**Tela:** `telas/34-bancada-passo.png`

**Narração:**
> E quando uma tarefa falha, a rede para. A transição seguinte não dispara. Um sistema que
> segue em frente com dado ruim entrega um laudo errado com cara de laudo certo.

**Produção:** 16 s.

---

# BLOCO 11 — O que se pode pedir ao sistema

## Cena 40 · Corrigir conversando, em qualquer etapa

**Tela:** `telas/62-casos-de-teste-etapa.png`

**Narração:**
> Vimos isso no modelo de dados, e vale para toda etapa: cada uma tem um chat com o agente
> que a produziu. Não é preciso editar arquivo. Pede-se a correção em português, a etapa
> gera uma versão nova, e a anterior fica no histórico.

**Produção:** 20 s. Mostre os comandos abaixo escritos na tela, um por vez.

**Comandos de exemplo, para aparecer escritos na tela:**
- *"Separe o requisito FR-031 em dois: um para contar as classes e outro para decidir a multirresistência."*
- *"O caso de uso UC-011 não diz o que fazer quando o antibiograma vem vazio. Acrescente o fluxo de exceção."*
- *"Na tela de alerta, a gravidade deve vir preenchida com 'alta' quando houver multirresistência."*
- *"Acrescente à tarefa de recomendação a restrição de nunca sugerir pacote de germe multirresistente sem multirresistência registrada."*
- *"Gere um caso de teste para a situação em que o laboratório está fora do ar."*

---

# Encerramento

**Tela:** `telas/08-rede-de-petri.png` (retomada)

**Narração:**
> Do documento do hospital até o sistema rodando, sem ninguém escrever código. Doze etapas,
> cada uma com o seu documento, cada documento conferível e corrigível por conversa.
>
> O que mudou nesta versão não foi o modelo nem a ferramenta: foi ter declarado, desde o
> requisito, o que é trabalho de inteligência artificial e o que é trabalho de sempre.
> Cinco tarefas em vez de quarenta e cinco. E o que ainda falta está apontado, não
> escondido.

**Produção:** 20 s. Fecha na rede.

---

# Anexo de produção — o que está provado e o que não está

Medido em 28/09/2026 contra a aplicação implantada, com dois casos clínicos plantados no
banco. Registro completo em `registro_de_testes.md`.

**Provado, com tela e com gabarito — 22 de 23 casos:**

| | |
|---|---|
| Cadastro | 15 de 15: listar, criar, ler, alterar e excluir em pacientes, antimicrobianos e bundles, conferidos contra a linha no banco |
| Correção por conversa | pedido em português mudou três colunas de `DECIMAL(10,0)` para `DECIMAL(5,2)` e gerou a versão 2, preservando a 1 |
| Contagem de classes resistentes | 4 no caso multirresistente, 1 no outro — batendo com o gabarito |
| Tradução do laboratório | 6 antimicrobianos, todos com classe, microrganismo correto |
| Recusa de amostra inexistente | o agente declara não aproveitável e justifica, sem inventar |
| Classificação pela norma | responde com o critério citado por nome e versão |
| Recomendação de pacote | escolhe um pacote que existe no cadastro, com justificativa |
| Redação do alerta | recusa corretamente quando não há multirresistência, citando a regra |
| Rede de Petri | a marca percorre os cinco lugares e chega ao fim; falha bloqueia a transição |
| Painéis da Bancada | as 11 etiquetas universais, com entrada e saída de cada tarefa |
| Rastreabilidade | 22 requisitos ligados a caso de uso, tarefa e tela |

**Não provado — não narre como pronto:**

- **A regra das três classes não é aplicada pela tarefa de multirresistência**: a contagem
  sai certa e o campo do veredito volta vazio. É o único caso reprovado da bateria. (A
  tarefa do *alerta* aplica a regra corretamente — é ela que aparece na Cena 34.)
- Pela tela do hospital, as tarefas recebem o caso mas não o identificador da amostra: o
  croqui do caso de uso oferece um, a tarefa pede o outro. A cadeia completa roda na Bancada.
- Das 58 telas, 24 abrem sem dados porque são telas de ação: só mostram conteúdo depois que
  o operador executa.
- 4 telas ainda mostram "Ação não vinculada a uma tarefa do sistema" — casos de uso
  convencionais sem executor próprio.
- 56 itens do documento de requisitos (não-funcionais e regras de negócio) ficaram sem
  classificação de natureza.
- A etapa de casos de teste apontou 36 casos contraditórios, onde falta na tabela a causa
  que dispara a exceção.
- O validador do modelo de dados dá nota 75 em 100, com 15 problemas apontados — três deles
  foram corrigidos na Cena 14; os outros doze continuam.
