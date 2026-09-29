# Roteiro narrado — LangNet: o pipeline de SDD em 15 minutos (v9)

**O que o vídeo mostra:** o LangNet percorrendo o pipeline do Desenvolvimento Orientado a
Especificação para um projeto real, o BioByte Sentinela: o que cada etapa recebe, que documento
produz, como esse documento aponta para o anterior — e o sistema gerado funcionando.

**Pasta das telas:** `docs/apresentacao/demo-biobyte-v9/telas/`
**Duração estimada:** 15 minutos.

**Esta é a versão reduzida da v8.** Mesmo conteúdo e mesmas telas; cenas juntadas e narração
enxugada. A v8 (54 cenas, cerca de 26 minutos) continua valendo como versão completa.

**Como ler cada cena:** **Tela** (o arquivo a mostrar), **Narração** (o texto exato que o narrador
fala) e **Produção** (duração e o que destacar).

**O fio condutor.** Um único requisito atravessa o vídeo: *identificar multirresistência no
antibiograma*. Em cada etapa, a câmera vai até ele.

**Sobre as telas simuladas.** Nenhuma etapa foi executada de novo para o vídeo. Onde aparece uma
instrução ou pedido digitado, o texto foi escrito no campo e **não enviado**. A correção do Modelo de
Dados aconteceu de verdade, e a aplicação e a Bancada foram filmadas rodando.

---

# ABERTURA

## Cena 1 · O que é o LangNet

**Telas:** `telas/01a-lista-de-projetos.png`, `telas/01b-criar-projeto.png`

**Narração:**
> O LangNet é um software que implementa o pipeline do Desenvolvimento Orientado a Especificação. Ele
> conduz um projeto por uma sequência fixa de etapas — dos documentos do cliente até o código e os testes
> — e em cada etapa produz um documento que se pode ler, corrigir e aprovar. Cada documento registra de
> qual versão do documento anterior ele nasceu, e é essa cadeia que dá a rastreabilidade: de qualquer
> linha de código dá para voltar até a frase do cliente que a originou.
>
> O menu à esquerda é o pipeline, na ordem: documentos e requisitos, especificação, modelo de dados,
> interface, agentes e tarefas, ferramentas, os arquivos YAML, a sequência, a rede de Petri, o código e os
> casos de teste. Vamos acompanhar o BioByte Sentinela, um sistema de vigilância de infecção de corrente
> sanguínea associada a cateter.

**Produção:** 50 s. Primeiro a lista de projetos; depois o formulário, percorrendo o menu de cima para baixo.

---

# DOCUMENTOS E REQUISITOS

## Cena 2 · O documento do cliente

**Telas:** `telas/02d-documento-fonte-multirresistencia.png`, `telas/02e-documento-fonte-secao7.png`

**Narração:**
> Tudo começa num documento do cliente: a ata da comissão de controle de infecção do hospital. O problema,
> nas palavras da coordenadora, é tempo — entre a hemocultura ficar pronta e alguém perceber a infecção,
> passam às vezes dois dias. Na seção dois ponto seis, o documento diz que o sistema deve identificar se o
> germe é multirresistente: resistência a três ou mais classes de antimicrobianos. É essa frase que vamos
> seguir pelo pipeline inteiro. E o documento termina separando, com todas as letras, o que é trabalho de
> inteligência artificial — cinco coisas — do que é sistema comum: cadastro, login, painel, relatório.

**Produção:** 45 s. Aponte a linha 115, "três ou mais classes"; depois a seção 7 em verde.

---

## Cena 3 · A análise, com instrução

**Telas:** `telas/02a-documentos-instrucao.png`, `telas/02b-documentos-conversa-analise.png`

**Narração:**
> O documento é carregado na primeira etapa, com uma instrução: a seção sete define o que é agente,
> classifique cada requisito de acordo. A conversa fica gravada: o pedido e, quatro minutos depois, o
> documento de requisitos.

**Produção:** 20 s.

---

## Cena 4 · O documento de requisitos

**Telas:** `telas/03a-requisitos-estatisticas.png`, `telas/03b-requisitos-tabela-fr031.png`, `telas/03d-requisitos-rastreabilidade-origem.png`

**Narração:**
> O documento de requisitos. Noventa e nove requisitos funcionais, vinte e cinco não funcionais, trinta e
> uma regras de negócio — e cada item diz de onde veio: extraído do documento, da instrução do usuário, ou
> sugerido pela IA e marcado como pendente de aprovação. Cada requisito tem natureza, descrição, atores e
> critério de aceite. O nosso é o FR-031, identificar multirresistência, de natureza agêntica. Logo abaixo,
> o FR-032, a regra das três classes, é convencional: contar é regra fechada. E a seção onze liga cada
> requisito ao trecho da ata de onde nasceu — é o primeiro elo da rastreabilidade.

**Produção:** 50 s. FR-031 em vermelho, FR-032 em azul; depois a linha "2.6" da rastreabilidade.

---

## Cena 5 · Corrigir conversando

**Tela:** `telas/03f-requisitos-refinar-com-agente.png`

**Narração:**
> Para corrigir o documento não se edita o texto: pede-se ao agente da etapa, em português. Por exemplo:
> no FR-031, deixe explícito que resultado intermediário não conta como resistência. O agente reescreve o
> documento e grava uma versão nova; a anterior continua disponível. Todas as etapas funcionam assim.

**Produção:** 20 s. Pedido digitado e não enviado.

---

# ESPECIFICAÇÃO

## Cena 6 · Origem e instrução

**Tela:** `telas/04b-especificacao-origem-e-instrucao.png`

**Narração:**
> Toda etapa começa igual: escolhe-se o documento de origem e a versão — aqui, os requisitos, versão um —
> e escreve-se uma instrução. Depois gera, confere, corrige conversando e aprova.

**Produção:** 15 s. Instrução digitada e não enviada.

---

## Cena 7 · O caso de uso UC-011

**Telas:** `telas/04d-especificacao-uc011-cabecalho.png`, `telas/04f-especificacao-uc011-excecoes.png`, `telas/04g-especificacao-uc011-croqui.png`

**Narração:**
> O FR-031 virou o caso de uso UC-011. O ator principal é o agente de IA, a natureza é agêntica, e a decisão
> do agente está escrita: examinar o antibiograma e julgar se o germe é multirresistente pela regra das três
> classes. O caso de uso aponta os requisitos de onde nasceu. Depois vêm o fluxo principal e os fluxos de
> exceção — antibiograma sem classe, falha do agente, resultado pendente — cada um com a mensagem exata que
> aparece na tela. E o croqui da tela, com os mesmos campos que o fluxo cita.

**Produção:** 45 s. Destaque Natureza, Decisão do Agente e RFs Relacionados; depois E1 e E3; depois o croqui.

---

## Cena 8 · A matriz de rastreabilidade

**Tela:** `telas/04h-especificacao-matriz-rastreabilidade.png`

**Narração:**
> No fim da especificação, a matriz liga cada requisito ao seu caso de uso: FR-031 e FR-032 ao UC-011.

**Produção:** 12 s.

---

# MODELO DE DADOS

## Cena 9 · A etapa confere o próprio resultado

**Tela:** `telas/05a-modelo-origem-e-validacao.png`

**Narração:**
> O modelo de dados parte da especificação — a origem está no alto, com data e hora. Escolhe-se o banco, e o
> resultado são vinte e oito tabelas. E a etapa confere o que gerou antes de alguém aprovar: nota setenta e
> cinco em cem, quinze problemas, cada um dizendo tabela e coluna. O primeiro, por exemplo: a coluna do
> escore está sem precisão declarada, e o banco vai truncar as casas decimais.

**Produção:** 28 s. Destaque a faixa "Origem" e a caixa amarela.

---

## Cena 10 · O requisito virou coluna

**Tela:** `telas/05b0-modelo-entidade-resultados-hemocultura.png`

**Narração:**
> O nosso requisito chegou ao banco: a tabela de resultados de hemocultura tem a coluna multirresistente.
> É ali que a decisão do agente vai ficar.

**Produção:** 12 s.

---

## Cena 11 · Uma correção de verdade, em português

**Telas:** `telas/05d-modelo-conversa-real.png`, `telas/05f-modelo-comparacao-v1-v2.png`

**Narração:**
> Esta correção foi feita de fato, por conversa. O pedido, em português: as colunas de escore médio,
> conformidade mensal e redução média de risco estão como decimal sem casas, e um escore de zero vírgula seis
> dois vira um; troque as três para duas casas decimais. A resposta não é uma promessa do modelo: é o programa
> comparando o antes e o depois — três linhas saíram, três entraram. Lado a lado, a versão um e a versão
> dois: mudaram só as três colunas pedidas, e a versão anterior continua guardada no histórico.

**Produção:** 45 s. A comparação foi montada com as duas versões gravadas no banco.

---

# INTERFACE, AGENTES E FERRAMENTAS

## Cena 12 · A tela, ligada ao banco

**Telas:** `telas/06c-interface-uc011-componentes-ligados.png`, `telas/06d-interface-prototipo-uc011.png`

**Narração:**
> Cada caso de uso vira uma tela — são trinta. A do UC-011 é declarada componente por componente, e cada
> componente diz a que coluna do banco está ligado: o campo Multirresistente aponta para a coluna que vimos
> no modelo de dados, e as mensagens de aviso são as dos fluxos de exceção. E antes de gerar uma linha do
> sistema, a tela já pode ser navegada no protótipo, com dados de exemplo — é aqui que o cliente pede ajuste,
> quando mudar ainda é barato.

**Produção:** 35 s.

---

## Cena 13 · Cinco tarefas, e cada uma sabe de onde veio

**Telas:** `telas/07c-agentes-cinco-tarefas.png`, `telas/07e-agentes-tarefa-t003-rastreabilidade.png`

**Narração:**
> A etapa de agentes e tarefas parte da especificação e confere a instrução antes de decidir: trinta e um
> casos de uso entraram, e só os de natureza agêntica viraram tarefa — cinco tarefas, em dois agentes.
> Traduzir o resultado do laboratório, classificar pelo critério, avaliar multirresistência, recomendar o
> pacote, redigir o alerta. O UC-011 virou a tarefa T-AGN-003. E a ficha da tarefa termina na
> rastreabilidade: caso de uso UC-011, requisitos FR-031 e FR-032, regra de negócio BR-009, a das três
> classes.

**Produção:** 40 s. Destaque UC-011 → T-AGN-003; depois UC/RF/RN Relacionado.

---

## Cena 14 · Quem implementa cada ferramenta

**Tela:** `telas/08a-ferramentas-inventario.png`

**Narração:**
> Antes de gerar código, uma pergunta: cada ferramenta que os agentes vão usar, de onde vem a
> implementação? Sem essa resposta, a geração escreve uma ferramenta que devolve valor fixo e parece
> funcionar. São três ferramentas, e as três têm implementação declarada.

**Produção:** 18 s. Destaque "Pendentes 0".

---

# YAML, SEQUÊNCIA E REDE DE PETRI

## Cena 15 · O tasks.yaml e a sequência

**Telas:** `telas/09c-yaml-tasks-multirresistencia.png`, `telas/10c-sequencia-task3.png`

**Narração:**
> As tarefas viram os arquivos que o framework de agentes lê. No tasks.yaml, a nossa tarefa, com os
> passos: agrupar por classe, não contar intermediário, decidir com três ou mais. E a sequência diz o que
> cada tarefa recebe e de quem: o antibiograma traduzido vem da tarefa um.

**Produção:** 30 s. Aponte os passos 7 e 9.

---

## Cena 16 · A rede de Petri

**Telas:** `telas/11a-petri-origem.png`, `telas/11c-petri-rede-inteira.png`, `telas/11d-petri-json-lugar-p3.png`

**Narração:**
> A rede de Petri é gerada do agents.yaml, do tasks.yaml e da sequência — as três origens com data e hora.
> Um lugar de início, cinco lugares de tarefa, um de fim, e entre eles as transições que liberam a próxima. O
> lugar P3, em vermelho, é a multirresistência. E a rede não é só um desenho: por dentro, cada lugar tem a
> tarefa, os campos que espera receber e o código que chama o servidor de agentes.

**Produção:** 35 s.

---

# CÓDIGO E TESTES

## Cena 17 · O código gerado e a rastreabilidade

**Tela:** `telas/12b-codigo-rastreabilidade-md.png`

**Narração:**
> A geração produz o sistema inteiro — cento e trinta e oito arquivos — e um arquivo de rastreabilidade:
> FR-031, UC-011, a tarefa de multirresistência, a tela do detalhe do caso. Uma linha liga tudo.

**Produção:** 18 s. Linhas 38 e 39 selecionadas.

---

## Cena 18 · O portão antes de implantar

**Tela:** `telas/12e-codigo-portoes-pendencias.png`

**Narração:**
> Antes de liberar, a geração confere o que foi pedido contra o que foi gerado: ferramentas, contrato de tela,
> módulos do servidor e a lógica das tarefas. Aqui ela aponta os passos de lógica que não viraram código —
> entre eles, agrupar os antimicrobianos por classe, na tarefa de multirresistência. Com pendência, a versão
> não é implantada sem uma decisão explícita, que fica registrada.

**Produção:** 25 s. Destaque os itens de evaluate_multidrug_resistance.

---

## Cena 19 · Casos de teste do caso de uso

**Telas:** `telas/13b-testes-grafo-uc011.png`, `telas/13c-testes-tabela-decisao-uc011.png`, `telas/13d-testes-casos-uc011.png`

**Narração:**
> Os casos de teste não são escritos à mão. Para cada caso de uso, a etapa monta um grafo de causa e efeito:
> no UC-011, nove causas — o resultado concluído, as classes preenchidas, três ou mais classes resistentes — e
> treze efeitos, que são as respostas do sistema. Do grafo sai a tabela de decisão, e cada coluna vira um caso
> de teste: com três ou mais classes resistentes, o sistema deve mostrar multirresistente igual a sim; com
> menos, igual a não.

**Produção:** 40 s. Aponte TC-UC-011-03 e 04.

---

## Cena 20 · O teste que reprovou

**Tela:** `telas/13e-testes-registro-execucao.png`

**Narração:**
> Executados na aplicação, vinte e dois de vinte e três passaram. O que reprovou era justamente o nosso: a
> contagem de classes saía certa, mas o veredito voltava vazio. A cadeia de documentos disse onde estava o
> defeito; a correção foi feita no gerador, e o código foi gerado e implantado de novo.

**Produção:** 25 s. Destaque a linha vermelha.

---

# A APLICAÇÃO GERADA

## Cena 21 · Um cadastro, conferido no banco

**Telas:** `telas/40-crud-2-novo-preenchido.png`, `telas/40-crud-3-salvo-na-lista.png`, `telas/40-crud-5-excluido.png`

**Narração:**
> Este é o sistema que saiu do pipeline, rodando, com uma tela de cadastro para cada tabela do modelo de
> dados. Um paciente novo: preenchido e salvo, ele aparece na lista — e no banco, a tabela passou de três
> para quatro linhas. Excluído, volta a três. Conferimos no banco a cada passo, e não só na tela.

**Produção:** 25 s.

---

## Cena 22 · Agente 1: traduzir o resultado do laboratório

**Tela:** `telas/30-cadeia-1-traducao-b-resultado.png`

**Narração:**
> A primeira tarefa de inteligência artificial. O agente foi ao banco, leu o antibiograma do caso e
> devolveu no vocabulário do hospital: *Staphylococcus aureus* e os seis antimicrobianos, cada um com a sua
> classe.

**Produção:** 18 s.

---

## Cena 23 · Agente 2: a classificação que não fecha

**Tela:** `telas/31-cadeia-2-classificacao-b-resultado.png`

**Narração:**
> A classificação pelo critério da norma respondeu pendente, e disse por quê: a lista de critérios e a data
> de início do caso não chegaram na entrada da tarefa, e sem elas não há como saber qual versão da norma
> estava vigente — e a regra proíbe usar a de hoje para um caso antigo. O agente não fecha uma decisão que
> os dados não sustentam. É uma lacuna conhecida do gerador, e está apontada.

**Produção:** 25 s. Destaque "pendente" e a justificativa.

---

## Cena 24 · Agente 3: o veredito

**Tela:** `telas/32-cadeia-3-multirresistencia-b-resultado.png`

**Narração:**
> A tarefa que seguimos o vídeo inteiro. O agente agrupou por classe e contou quatro classes resistentes —
> cefalosporina, betalactâmico, fluoroquinolona e aminoglicosídeo —, deixando o carbapenêmico de fora, porque
> era intermediário. E decidiu: multirresistente, sim. É exatamente o ponto que o teste tinha reprovado; esta é
> a execução depois da correção. E repare no registro da decisão: gravado na tabela de decisões, com o seu
> identificador.

**Produção:** 30 s. Destaque "multirresistente: true" e "registro_decisao".

---

## Cena 25 · Agente 5: o alerta

**Tela:** `telas/34-cadeia-5-alerta-b-resultado.png`

**Narração:**
> E a última tarefa redige o alerta para a equipe da UTI: *Staphylococcus aureus* resistente a quatro classes
> de antibióticos, por que isso importa para um paciente com cateter, e o que fazer. A recomendação de
> tratamento respondeu insuficiente, porque o caso ainda não está confirmado pela norma — e o alerta diz
> isso.

**Produção:** 25 s. Leia o começo do texto do alerta.

---

## Cena 26 · As decisões gravadas

**Telas:** `telas/45-decisoes-gravadas.png`, `telas/45-decisao-alerta-detalhe.png`

**Narração:**
> Cada resposta ficou gravada, ligada ao caso, com a tarefa e a versão do prompt que a produziu. O
> documento de agentes e tarefas pedia isso, e o gerador passou a ler essa frase. É o que a enfermeira da
> reunião pediu: mostrar depois por qual critério, com base em quê e quando.

**Produção:** 25 s. Destaque "origem_dado" e "valor".

---

# A EXECUÇÃO NA BANCADA

## Cena 27 · A entrada da execução

**Telas:** `telas/15a-bancada-rede.png`, `telas/71-bancada-entrada-aplicada.png`

**Narração:**
> A outra forma de rodar o sistema é a Bancada: a rede de Petri ligada ao servidor de agentes. No alto, a
> entrada — os campos que as primeiras tarefas da rede esperam. O operador informa o caso e aplica.

**Produção:** 20 s. Destaque "aplicado: caso_id".

---

## Cena 28 · Operação: entrada, execução, saída

**Telas:** `telas/15b3-bancada-marca-P3.png`, `telas/72-operacao-P3.png`

**Narração:**
> Em modo pausar por tarefa, a rede executa uma tarefa e para, esperando o operador. A aba Operação mostra
> a tarefa e o agente; tudo o que ele recebeu — as regras do sistema, a instrução do tasks.yaml e o caso
> informado na entrada —; os passos da execução — iniciou, raciocinou, saída final —; e, à direita, o
> documento produzido: multirresistente, verdadeiro, quatro classes. O operador confere e decide: aprovar e
> continuar, ou refazer.

**Produção:** 40 s. Percorra o painel de cima para baixo.

---

## Cena 29 · A cadeia chega ao alerta

**Telas:** `telas/72-operacao-P5.png`, `telas/74-painel-logs.png`

**Narração:**
> Aprovada cada parada, a cadeia chega à última tarefa: o texto do alerta para a equipe da UTI, com o
> microrganismo, a origem da amostra e as quatro classes — do resultado do laboratório ao texto que o
> enfermeiro vai ler, cada passo conferido e registrado no log da execução.

**Produção:** 25 s.

---

# ENCERRAMENTO

## Cena 30 · Do documento ao alerta

**Tela:** `telas/12b-codigo-rastreabilidade-md.png` (retomada)

**Narração:**
> Percorremos o pipeline com uma frase da ata: identificar multirresistência. Ela virou requisito, caso de
> uso, coluna, tela, tarefa, trecho do tasks.yaml, lugar da rede e treze casos de teste — e, no sistema
> gerado, uma decisão gravada e um alerta redigido. Quando algo falhou, a cadeia de documentos disse
> exatamente onde; a correção foi feita no gerador, não no código, e o sistema foi gerado de novo. O que
> ainda falta — a classificação que não recebe os critérios da norma, as telas comuns sem executor — está
> apontado do mesmo jeito.

**Produção:** 35 s.
