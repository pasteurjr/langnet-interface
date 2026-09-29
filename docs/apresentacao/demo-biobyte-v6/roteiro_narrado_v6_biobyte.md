# Roteiro narrado — LangNet: o pipeline de SDD, etapa por etapa (v6)

**O que o vídeo mostra:** o LangNet percorrendo o pipeline do Desenvolvimento Orientado a
Especificação para um projeto real, o BioByte Sentinela, etapa por etapa — o que cada etapa
recebe, que documento produz, como esse documento aponta para o anterior e como se corrige.

**Pasta das telas:** `docs/apresentacao/demo-biobyte-v6/telas/`
**Duração estimada:** 20 minutos de narração (cerca de 22 com as pausas de corte).

**Como ler cada cena:**
- **Tela** — o arquivo a mostrar.
- **Narração** — o texto exato que o narrador fala.
- **Produção** — duração, o que destacar, e se a tela é uma simulação.

**O fio condutor.** Um único requisito atravessa o vídeo inteiro: *identificar multirresistência
no antibiograma*. Ele nasce numa frase da ata (linha 115), vira o requisito FR-031, o caso de
uso UC-011, a coluna `multirresistente` do banco, uma tela, a tarefa T-AGN-003, um bloco do
tasks.yaml, a terceira tarefa da sequência, o lugar P3 da rede de Petri, uma linha da matriz de
rastreabilidade do código e treze casos de teste. Em cada etapa, a câmera vai até ele.

**Sobre as telas simuladas.** Nenhuma etapa foi executada de novo para o vídeo. Onde a cena
mostra uma instrução ou um pedido de correção digitado, o texto foi escrito no campo **e não
enviado** — a Produção de cada cena diz quando é assim. A única correção por conversa
efetivamente executada é a do Modelo de Dados (cenas 17 a 20), e ela aparece como aconteceu.

---

# ABERTURA

## Cena 1 · O que é o LangNet

**Tela:** `telas/01a-lista-de-projetos.png`

**Narração:**
> O LangNet é um software que implementa o pipeline do Desenvolvimento Orientado a
> Especificação. Ele conduz um projeto por uma sequência fixa de etapas — dos documentos do
> cliente até o código e os testes — e em cada etapa produz um documento que se pode ler,
> corrigir e aprovar. Cada documento registra de qual versão do documento anterior ele nasceu.
> É essa cadeia que dá a rastreabilidade: de qualquer linha de código dá para voltar até a frase
> do cliente que a originou.
>
> Aqui estão os projetos. Vamos acompanhar um deles: o BioByte Sentinela, um sistema de
> vigilância de infecção de corrente sanguínea associada a cateter.

**Produção:** 30 s. Destaque o cartão do BioByte Sentinela v5 ao dizer o nome.

---

## Cena 2 · As etapas

**Tela:** `telas/01b-criar-projeto.png` (o menu lateral é o foco)

**Narração:**
> Um projeto começa com um nome, um domínio e uma descrição curta. A partir daí, o menu à
> esquerda é o pipeline, na ordem em que ele é executado: Documentos e Requisitos.
> Especificação. Modelo de Dados. Interface e Protótipo. Agentes e Tarefas. Ferramentas. Os
> arquivos YAML de agentes e tarefas. Sequência de Tarefas. Rede de Petri. Geração de Código. E
> Casos de Teste.
>
> Todas as etapas funcionam do mesmo jeito: escolhe-se o documento de origem e a versão,
> escreve-se uma instrução, gera-se o documento, confere-se, corrige-se conversando com o agente
> da etapa, e aprova-se. Vamos passar por cada uma.

**Produção:** 35 s. Formulário preenchido e não enviado (o projeto já existe). Percorra os itens
do menu de cima para baixo, no ritmo da narração.

---

# ETAPA 1 — DOCUMENTOS E REQUISITOS

## Cena 3 · O documento de origem: o problema

**Tela:** `telas/02c-documento-fonte-problema.png`

**Narração:**
> Tudo começa num documento do cliente. Este é o levantamento de requisitos da comissão de
> controle de infecção do hospital: trezentas e doze linhas, com as falas da reunião. Logo no
> início está o problema, nas palavras da coordenadora: entre a hemocultura ficar pronta e alguém
> perceber a infecção, às vezes passam dois dias. E a enfermeira acrescenta: toda classificação
> tem de poder ser auditada — por qual critério, em qual versão da norma, e quem assinou.

**Produção:** 30 s. As linhas 17 a 23 estão em destaque.

---

## Cena 4 · O documento de origem: o requisito que vamos seguir

**Tela:** `telas/02d-documento-fonte-multirresistencia.png`

**Narração:**
> Mais adiante, a seção dois ponto seis: multirresistência e alerta. O documento diz que o
> sistema deve identificar, a partir do antibiograma, se o germe é multirresistente — a regra é
> resistência a três ou mais classes de antimicrobianos — e, quando for, abrir um alerta e avisar
> a equipe. Guarde esta frase. Vamos segui-la por todas as etapas do pipeline.

**Produção:** 25 s. Linhas 111 a 124 em destaque; aponte a linha 115, "três ou mais classes".

---

## Cena 5 · O documento de origem: o que é trabalho de IA

**Tela:** `telas/02e-documento-fonte-secao7.png`

**Narração:**
> E o documento termina com a seção que mais pesa no projeto. A coordenadora separa, com todas as
> letras, o que é trabalho de inteligência artificial e o que não é. São cinco coisas: traduzir o
> resultado do laboratório, classificar o caso pelo critério, ver se há multirresistência,
> recomendar o pacote de medidas e escrever o alerta. Todo o resto — cadastro, login, painel,
> relatório, auditoria, envio de e-mail — é sistema comum.

**Produção:** 30 s. Seção 7 em destaque verde.

---

## Cena 6 · O documento entra, com uma instrução

**Tela:** `telas/02a-documentos-instrucao.png`

**Narração:**
> Na etapa de Documentos, o arquivo é carregado — está aqui, na lista. Ao lado, o campo de
> instruções para a análise. A instrução que foi usada neste projeto diz exatamente isto: a seção
> sete declara o que é trabalho de agente; todo o resto é convencional; classifique cada
> requisito de acordo.

**Produção:** 25 s. Moldura azul no documento carregado, vermelha na instrução. É a instrução real
desta análise, digitada de novo no campo para a cena; não foi reenviada.

---

## Cena 7 · A análise registrada na conversa

**Tela:** `telas/02b-documentos-conversa-analise.png`

**Narração:**
> Esta é a conversa da análise, como ficou gravada: a instrução enviada, o agente processando o
> documento e, quatro minutos depois, o documento de requisitos gerado. Tudo o que foi pedido e
> tudo o que foi respondido fica registrado junto do projeto.

**Produção:** 20 s. Destaque a mensagem do usuário (13:14) e a conclusão (13:19).

---

## Cena 8 · O documento de requisitos: o que ele contém

**Tela:** `telas/03a-requisitos-estatisticas.png`

**Narração:**
> O documento de requisitos. Noventa e nove requisitos funcionais, vinte e cinco não funcionais,
> trinta e uma regras de negócio, vinte e nove atores, trinta e quatro entidades de dados, onze
> perguntas em aberto. E a procedência de cada item: cento e trinta e nove vieram do documento,
> um veio da instrução do usuário, e quinze foram sugeridos pela IA e estão marcados como
> dependentes de aprovação.

**Produção:** 30 s. Destaque a tabela "De onde vêm os requisitos".

---

## Cena 9 · Os principais requisitos, e o nosso

**Tela:** `telas/03b-requisitos-tabela-fr031.png`

**Narração:**
> Cada requisito tem identificador, origem, natureza, descrição, prioridade, atores e critério
> de aceite. Os principais deste sistema estão aqui: aplicar o critério NHSN vigente e
> classificar o caso, registrar critério e versão, permitir que o médico sobrescreva com
> justificativa — e o nosso: FR-031, identificar multirresistência no antibiograma, de natureza
> agêntica. Logo abaixo, FR-032, a regra das três classes, marcada como convencional: contar é
> regra fechada, não precisa de agente.

**Produção:** 35 s. FR-031 em vermelho, FR-032 em azul. Aponte a coluna "Natureza" nos dois.

---

## Cena 10 · De onde veio cada requisito

**Tela:** `telas/03d-requisitos-rastreabilidade-origem.png`

**Narração:**
> A seção onze liga cada requisito ao trecho do documento de origem. A seção dois ponto seis,
> multirresistência e alerta, deu origem a vinte e nove itens — o FR-031 está entre eles. Este é
> o primeiro elo da rastreabilidade: do requisito até a frase da ata.

**Produção:** 25 s. Linha "2.5 · 2.6" em destaque.

---

## Cena 11 · O que o documento ainda não sabe

**Tela:** `telas/03e-requisitos-perguntas-abertas.png`

**Narração:**
> O documento também declara o que não sabe. São onze perguntas em aberto para o cliente
> responder, em vez de lacunas preenchidas por suposição.

**Produção:** 15 s.

---

## Cena 12 · Corrigir conversando

**Tela:** `telas/03f-requisitos-refinar-com-agente.png`

**Narração:**
> Para corrigir o documento, não se edita o texto: pede-se ao agente da etapa. Por exemplo: no
> FR-031, deixe explícito que resultado intermediário não conta como resistência, e acrescente
> um critério de aceite para o antibiograma que vem sem a classe de algum antimicrobiano. O
> agente reescreve o documento e grava uma versão nova; a anterior continua disponível.

**Produção:** 25 s. Pedido digitado e **não enviado**. Destaque o campo.

---

# ETAPA 2 — ESPECIFICAÇÃO FUNCIONAL

## Cena 13 · Escolher a origem

**Telas:** `telas/04a-especificacao-escolher-origem.png`, `telas/04b-especificacao-origem-e-instrucao.png`

**Narração:**
> A especificação parte do documento de requisitos. Primeiro escolhe-se qual documento e qual
> versão — aqui, a análise concluída às treze e dezenove, versão um. A etapa passa a mostrar a
> base escolhida. Depois vem a instrução: por exemplo, declarar em cada caso de uso agêntico o que
> exatamente o agente decide, escrever os fluxos de exceção com a mensagem que o usuário vê, e
> desenhar o croqui da tela com os mesmos campos e botões do fluxo.

**Produção:** 35 s. Primeira tela: a versão 1 aberta para conferência. Segunda: a faixa verde
"Base: Document Analysis (v1)" e a instrução. Instrução digitada e **não enviada**.

---

## Cena 14 · O caso de uso nascido do requisito

**Telas:** `telas/04c-especificacao-requisitos-cobertos.png`, `telas/04d-especificacao-uc011-cabecalho.png`

**Narração:**
> A especificação começa listando os requisitos que ela cobre — o FR-031 e o FR-032 estão lá. E
> cada um vira caso de uso. O nosso é o UC-011, identificar multirresistência no antibiograma. O
> ator principal é o agente de IA; a natureza é agêntica; a decisão do agente está escrita: examinar
> o antibiograma e julgar se o germe é multirresistente pela regra das três classes. E o caso de
> uso diz de onde veio: FR-031, FR-032 e FR-080.

**Produção:** 35 s. Corte da tabela de requisitos cobertos para o cabeçalho do UC-011; destaque
Natureza, Decisão do Agente e RFs Relacionados.

---

## Cena 15 · O fluxo, as exceções e o croqui

**Telas:** `telas/04e-especificacao-uc011-fluxo-principal.png`, `telas/04f-especificacao-uc011-excecoes.png`, `telas/04g-especificacao-uc011-croqui.png`

**Narração:**
> O fluxo principal é escrito em duas colunas: o que o ator faz e o que o sistema responde, passo a
> passo — o agente lê a lista, agrupa por classe, conta as classes resistentes, decide e justifica.
> Depois, os fluxos de exceção: antibiograma sem classe, falha do agente, resultado pendente, erro
> de cadastro, lista vazia — cada um com a mensagem exata que aparece na tela. E o croqui da tela,
> com os mesmos campos que o fluxo cita: o antibiograma, a decisão, as classes resistentes, a
> justificativa.

**Produção:** 45 s. Três cortes, no ritmo da narração. Nas exceções, destaque E1 e E3.

---

## Cena 16 · A matriz, a conversa e o histórico

**Telas:** `telas/04h-especificacao-matriz-rastreabilidade.png`, `telas/04i-especificacao-refinar-conversa.png`, `telas/04j-especificacao-historico.png`

**Narração:**
> No fim do documento, a matriz de rastreabilidade liga cada requisito ao seu caso de uso — FR-031
> e FR-032 ao UC-011. A correção aqui também é por conversa: por exemplo, pedir o fluxo de exceção
> para o antimicrobiano repetido com resultados diferentes. E o histórico mostra de qual versão dos
> requisitos esta especificação nasceu.

**Produção:** 35 s. Pedido de correção digitado e **não enviado**. No histórico, destaque
"Baseado em: Requisitos v1".

---

# ETAPA 3 — MODELO DE DADOS

## Cena 17 · A origem e a validação

**Tela:** `telas/05a-modelo-origem-e-validacao.png`

**Narração:**
> O modelo de dados parte da especificação — a origem está no alto, com data e hora. Escolhe-se o
> banco, aqui MySQL. O resultado: vinte e oito tabelas. E a etapa confere o próprio resultado antes
> de alguém aprovar: nota setenta e cinco em cem, quinze problemas, cada um dizendo tabela e
> coluna. O primeiro, por exemplo: a coluna do escore está sem precisão declarada e o banco vai
> truncar as casas decimais.

**Produção:** 35 s. Destaque a faixa "Origem" e a caixa amarela da validação.

---

## Cena 18 · O requisito virou coluna

**Telas:** `telas/05b0-modelo-entidade-resultados-hemocultura.png`, `telas/05b-modelo-sql-multirresistencia.png`, `telas/05c-modelo-sql-antibiogramas.png`

**Narração:**
> E o nosso requisito chegou ao banco. A tabela de resultados de hemocultura tem a coluna
> multirresistente — é ali que a decisão do agente vai ser guardada. No esquema SQL, a mesma coluna.
> E a tabela de antibiogramas guarda cada antimicrobiano com o seu resultado, ligada ao resultado
> da hemocultura — que é o que o agente vai ler para decidir.

**Produção:** 35 s. Três cortes: entidade, SQL, tabela antibiogramas.

---

## Cena 19 · Uma correção de verdade, pedida em português

**Tela:** `telas/05d-modelo-conversa-real.png`

**Narração:**
> Esta correção foi feita de fato. O pedido, em português: as colunas escore médio e conformidade
> mensal do painel de vigilância, e redução média de risco dos bundles, estão como decimal sem
> casas; um escore de zero vírgula seis dois vira um; troque as três para decimal com duas casas.
> E a resposta da etapa não é uma promessa do modelo: é o programa comparando o antes e o depois —
> três linhas saíram, três entraram, nas tabelas bundles e painéis de vigilância.

**Produção:** 35 s. Conversa real, gravada em 28/09/2026 às 11:34. Destaque o pedido (vermelho) e
a resposta (verde).

---

## Cena 20 · A versão nova, comparada com a anterior

**Telas:** `telas/05e-modelo-historico-v1-v2.png`, `telas/05f-modelo-comparacao-v1-v2.png`, `telas/05g-modelo-v2-coluna-corrigida.png`

**Narração:**
> O histórico agora tem duas versões: a geração inicial e o refinamento, com o pedido como
> descrição. Comparando as duas lado a lado: três linhas alteradas, quatrocentas e trinta e quatro
> iguais. Numérico sem precisão virou decimal com duas casas, nas três colunas pedidas, e em nenhum
> outro lugar. A versão um continua guardada.

**Produção:** 40 s. A comparação (05f) foi montada a partir das duas versões gravadas no banco —
a interface não tem essa tela. Destaque as linhas em vermelho e verde.

---

# ETAPA 4 — INTERFACE E PROTÓTIPO

## Cena 21 · As telas nascem dos casos de uso

**Telas:** `telas/06a-interface-origem-e-instrucao.png`, `telas/06b-interface-tela-uc011-componentes.png`

**Narração:**
> A etapa de interface parte da especificação e do modelo de dados. São trinta telas, uma para
> cada caso de uso, organizadas no menu que o sistema vai ter. A tela do UC-011 é o detalhe do caso
> clínico na seção de multirresistência — com o contexto do resultado, os indicadores de
> antimicrobianos testados, classes avaliadas e classes resistentes, e o botão Identificar
> multirresistência.

**Produção:** 35 s. Instrução digitada e **não enviada**. Destaque a tela UC-011 selecionada.

---

## Cena 22 · Cada componente ligado ao banco

**Tela:** `telas/06c-interface-uc011-componentes-ligados.png`

**Narração:**
> A tela é declarada componente por componente, e cada componente diz a que coluna do banco está
> ligado. O campo Multirresistente aponta para resultados de hemocultura, coluna multirresistente —
> a mesma que vimos no modelo de dados. As mensagens de aviso e erro são as dos fluxos de exceção
> da especificação. E o botão Identificar multirresistência aciona a tarefa do agente. Logo abaixo,
> a origem: esta tela foi gerada do UC-011, especificação versão um.

**Produção:** 35 s. Destaque a linha `radio Multirresistente → resultados_hemocultura.multirresistente`.

---

## Cena 23 · O protótipo, antes de existir sistema

**Tela:** `telas/06d-interface-prototipo-uc011.png`

**Narração:**
> E antes de gerar uma linha do sistema, a tela já pode ser navegada no protótipo, com dados de
> exemplo: amostra, microrganismo, doze antimicrobianos, seis classes avaliadas, três classes
> resistentes — limiar atingido. É aqui que o cliente vê a tela e pede ajuste, quando mudar ainda
> é barato.

**Produção:** 25 s. Dados fictícios do protótipo, não do banco.

---

# ETAPA 5 — AGENTES E TAREFAS

## Cena 24 · A origem e a instrução

**Telas:** `telas/07a-agentes-escolher-origem.png`, `telas/07b-agentes-origem-e-instrucao.png`

**Narração:**
> A etapa de agentes e tarefas parte da especificação — versão um, fixada na faixa verde. A
> instrução deste projeto pedia que só os casos de uso de natureza agêntica virassem tarefa de
> agente: cinco tarefas, em dois agentes; todo o resto, código convencional; e cada tarefa citando o
> caso de uso e os requisitos de onde nasceu.

**Produção:** 30 s. Instrução digitada e **não enviada** (o documento gerado registra a instrução
original, ver próxima cena).

---

## Cena 25 · Cinco tarefas, dois agentes

**Tela:** `telas/07c-agentes-cinco-tarefas.png`

**Narração:**
> O documento gerado confere a instrução antes de decidir: trinta e um casos de uso entraram; cinco
> viraram tarefa. Traduzir o resultado do laboratório. Classificar pelo critério. Avaliar
> multirresistência — o nosso UC-011 vira a tarefa T-AGN-003. Redigir o alerta. Recomendar o pacote.
> E registra as premissas: login, cadastro, escore, painel, relatório e auditoria não geram agente
> nem tarefa.

**Produção:** 30 s. Linha UC-011 → T-AGN-003 em destaque.

---

## Cena 26 · O agente e a tarefa

**Telas:** `telas/07d-agentes-agente-ag01.png`, `telas/07e0-agentes-tarefa-t003-ficha.png`

**Narração:**
> O primeiro agente é o Classificador Clínico: papel, objetivo, história profissional com três
> princípios — honestidade acima de tudo, nunca inventar dado clínico, rastreabilidade total — e as
> ferramentas que pode usar. A tarefa T-AGN-003 tem a sua ficha: nome, agente responsável,
> ferramentas, formato de entrada e de saída.

**Produção:** 30 s.

---

## Cena 27 · A tarefa sabe de onde veio

**Tela:** `telas/07e-agentes-tarefa-t003-rastreabilidade.png`

**Narração:**
> E a ficha termina na rastreabilidade: caso de uso UC-011, requisitos FR-031, FR-032 e FR-080,
> regras de negócio BR-009 — a regra das três classes — e BR-030, decisão auditável. Acima, os casos
> de borda: antibiograma vazio, antimicrobiano sem classe, exatamente três classes, intermediários,
> classe repetida com resultados diferentes.

**Produção:** 30 s. Destaque UC Relacionado, RF Relacionado e RN Relacionado.

---

## Cena 28 · Conversa e histórico

**Telas:** `telas/07f-agentes-refinar-conversa.png`, `telas/07g-agentes-historico.png`

**Narração:**
> Como nas outras etapas, a correção é pedida ao agente: por exemplo, nunca devolver o campo
> multirresistente vazio quando a contagem foi feita. E o histórico guarda cada versão do documento
> de agentes e tarefas.

**Produção:** 20 s. Pedido digitado e **não enviado**.

---

# ETAPA 6 — FERRAMENTAS

## Cena 29 · De onde vem cada ferramenta

**Telas:** `telas/08a-ferramentas-inventario.png`, `telas/08b-ferramentas-contrato.png`

**Narração:**
> Antes de gerar código, uma pergunta: cada ferramenta que os agentes usam, de onde vem a
> implementação? Sem essa resposta, a geração escreve uma ferramenta que devolve valor fixo e parece
> funcionar. São três ferramentas, as três resolvidas: duas vêm da biblioteca do gerador; a de leitura
> de dados estruturados é determinística, e o contrato dela está aqui — o que faz, entrada, saída e os
> passos que viram código. A coluna ao lado mostra quem usa cada uma — a tarefa de multirresistência
> está lá.

**Produção:** 40 s. Destaque "Pendentes 0" e a tarefa evaluate_multidrug_resistance.

---

# ETAPA 7 — YAML DE AGENTES E TAREFAS

## Cena 30 · Os arquivos que o framework lê

**Telas:** `telas/09a-yaml-origem.png`, `telas/09b-yaml-agents.png`, `telas/09c-yaml-tasks-multirresistencia.png`

**Narração:**
> O documento de agentes e tarefas vira os dois arquivos que o framework de agentes lê. A origem está
> fixada: a especificação de agentes, versão um. O agents.yaml descreve cada agente. E no tasks.yaml,
> a tarefa de multirresistência: o formato da entrada, que vem da tarefa de tradução, e os passos —
> verificar antibiograma vazio, verificar classe ausente, deduplicar, agrupar por classe, não contar
> intermediário, e decidir multirresistente quando a contagem for três ou mais.

**Produção:** 45 s. Três cortes. Na terceira, aponte os passos 7 e 9.

---

# ETAPA 8 — SEQUÊNCIA DE TAREFAS

## Cena 31 · Três origens e a ordem de execução

**Telas:** `telas/10a1-sequencia-tres-origens.png`, `telas/10a2-sequencia-origens-fixadas.png`, `telas/10b-sequencia-visao-geral.png`

**Narração:**
> A sequência de tarefas precisa de três origens: a especificação funcional, a especificação de agentes
> e tarefas e o tasks.yaml. Selecionadas as três, a etapa descreve em que ordem as tarefas acontecem e
> que dado passa de uma para a outra.

**Produção:** 30 s.

---

## Cena 32 · O que cada tarefa recebe, e de quem

**Telas:** `telas/10c-sequencia-task3.png`, `telas/10d-sequencia-task5-recebe-da-task3.png`

**Narração:**
> A tarefa três, avaliar multirresistência, recebe o identificador do caso e o resultado traduzido — e
> o documento diz de onde vem cada um: o resultado traduzido vem da tarefa um. Mais adiante, a tarefa
> cinco, redigir o alerta, recebe o resultado da multirresistência — vindo da tarefa três. É esse
> encadeamento que vai virar a rede.

**Produção:** 30 s.

---

# ETAPA 9 — REDE DE PETRI

## Cena 33 · A origem e a rede

**Telas:** `telas/11a-petri-origem.png`, `telas/11c-petri-rede-inteira.png`

**Narração:**
> A rede de Petri é gerada do agents.yaml, do tasks.yaml e da sequência — as três origens com data e
> hora. O resultado: um lugar de início, cinco lugares de tarefa, um lugar de fim, e entre eles as
> transições que liberam a próxima tarefa. O lugar P3, em vermelho, é a tarefa de multirresistência.

**Produção:** 35 s. Diálogo de geração preenchido e **não enviado**. Na rede, aponte P3.

---

## Cena 34 · O que tem dentro de um lugar, e a conferência

**Telas:** `telas/11d-petri-json-lugar-p3.png`, `telas/11e-petri-conferencia-estrutural.png`

**Narração:**
> A rede não é só um desenho. Por dentro, o lugar P3 tem o nome da tarefa, os campos de entrada que
> espera, o agente que a executa, e o código que chama o servidor de agentes. E a rede passa por uma
> conferência estrutural: uma transição solta foi removida e nenhuma pendência ficou.

**Produção:** 30 s.

---

# ETAPA 10 — GERAÇÃO DE CÓDIGO

## Cena 35 · As origens e o que foi gerado

**Telas:** `telas/12a-codigo-origens.png`, `telas/12b-codigo-rastreabilidade-md.png`

**Narração:**
> A geração de código parte dos artefatos anteriores: agents.yaml, tasks.yaml, sequência e a
> especificação de agentes e tarefas. Sai o sistema inteiro — cento e trinta e oito arquivos: o
> servidor dos agentes, a interface do hospital, o banco. E entre eles, um arquivo de rastreabilidade
> gerado automaticamente: requisito, caso de uso, tarefa, tela. FR-031, UC-011, evaluate multidrug
> resistance, Detalhe do Caso Clínico — Multirresistência.

**Produção:** 40 s. Origens preenchidas e **não enviadas**. Linhas 38 e 39 selecionadas.

---

## Cena 36 · A tela gerada e o portão

**Telas:** `telas/12c-codigo-tela-uc011.png`, `telas/12e-codigo-portoes-pendencias.png`

**Narração:**
> A tela do UC-011 foi gerada com as mensagens que a especificação definiu. E antes de liberar, a
> geração confere o que foi pedido contra o que foi gerado. Ferramentas, contrato de tela e módulos do
> servidor: sem pendências. Lógica das tarefas: onze passos que não viraram código — entre eles,
> deduplicar e agrupar os antimicrobianos por classe, na tarefa de multirresistência. Por isso esta
> versão não pode ser implantada sem uma decisão explícita.

**Produção:** 40 s. Destaque os dois itens de evaluate_multidrug_resistance.

---

# ETAPA 11 — CASOS DE TESTE

## Cena 37 · Do caso de uso ao grafo

**Telas:** `telas/13a-testes-origem-e-uc011.png`, `telas/13b-testes-grafo-uc011.png`

**Narração:**
> Os casos de teste partem da especificação — versão um, fixada no alto. Para cada caso de uso, a
> etapa monta um grafo de causa e efeito. No UC-011: nove causas, que são as condições e ações — o
> resultado concluído, a lista de antimicrobianos, as classes preenchidas, três ou mais classes
> resistentes — e treze efeitos, que são as respostas do sistema.

**Produção:** 35 s.

---

## Cena 38 · A tabela de decisão e os casos

**Telas:** `telas/13c-testes-tabela-decisao-uc011.png`, `telas/13d-testes-casos-uc011.png`

**Narração:**
> Do grafo sai a tabela de decisão: cada coluna é uma combinação de causas, e cada coluna vira um caso
> de teste. São treze para o UC-011. O caso três: com três ou mais classes resistentes, o sistema deve
> exibir multirresistente igual a sim. O caso quatro: com menos de três, multirresistente igual a não.

**Produção:** 35 s. Aponte TC-UC-011-03 e TC-UC-011-04.

---

## Cena 39 · Os testes executados na aplicação

**Tela:** `telas/13e-testes-registro-execucao.png`

**Narração:**
> E os testes foram executados contra a aplicação implantada. Vinte e dois de vinte e três passaram.
> Os cadastros foram conferidos contra a linha no banco. Nos agentes, a contagem de classes saiu certa
> nos dois casos: quatro e um. O caso reprovado é justamente o nosso: a regra das três classes. A
> contagem veio certa, mas o campo multirresistente voltou vazio. É o mesmo ponto que o portão da
> geração tinha apontado — e é na tarefa, no documento de agentes e tarefas, que ele se corrige.

**Produção:** 40 s. Destaque a linha vermelha.

---

# A APLICAÇÃO E A EXECUÇÃO

## Cena 40 · O sistema gerado

**Telas:** `telas/14a-app-menu-e-cadastro.png`, `telas/14c-app-painel-vigilancia.png`

**Narração:**
> Este é o sistema que saiu do pipeline, rodando. O menu é o que a etapa de interface definiu —
> atendimento, engajamento, relatórios, integrações, cadastros. O cadastro de pacientes lê e grava no
> banco: estes três registros estão na tabela. E o painel de vigilância guarda, por período, os casos
> ativos, as classificações — uma confirmada, uma descartada — e os alertas em aberto.

**Produção:** 30 s.

---

## Cena 41 · Os agentes trabalhando

**Telas:** `telas/14e-app-agente-traducao.png`, `telas/14d-app-registros-dos-agentes.png`, `telas/14f-app-agente-classificacao-pendente.png`

**Narração:**
> O operador escolhe um caso que existe no banco e pede a tradução do resultado do laboratório. O
> agente responde se o resultado é aproveitável — aqui, sim — e a resposta vem com a versão do prompt
> que a produziu, para que a decisão possa ser rastreada depois. As classificações que os agentes produziram ficam gravadas. E quando
> faltam dados, o agente não fecha a decisão: aqui ele aplicou o critério vigente à data do caso, viu
> que os dados necessários não estão no banco, e respondeu pendente — citando o critério, a versão e o
> motivo.

**Produção:** 40 s. Na terceira tela, destaque "pendente" e "versão critério 2024".

---

## Cena 42 · A rede executando

**Telas:** `telas/15a-bancada-rede.png`, `telas/15b1-bancada-marca-P1.png`, `telas/15b2-bancada-marca-P2.png`, `telas/15b3-bancada-marca-P3.png`, `telas/15b4-bancada-marca-P4.png`, `telas/15b5-bancada-marca-P5.png`

**Narração:**
> Na execução, a rede de Petri gerada é a que comanda. A marca sai do início e entra na primeira
> tarefa. Concluída, a transição libera a segunda. Depois a terceira — a multirresistência. A quarta. A
> quinta. Cada passagem é uma tarefa de agente executada contra o banco.

**Produção:** 30 s. Corte entre as capturas no ritmo da narração.

---

## Cena 43 · Entradas, saídas e o registro de cada disparo

**Telas:** `telas/15d-bancada-entradas.png`, `telas/15e-bancada-logs-execucao.png`

**Narração:**
> O acompanhamento mostra cada tarefa começando, o agente raciocinando e a saída. Na tarefa do alerta,
> a saída diz: situação indeterminada — não houve antibiograma traduzido nem contagem de classes; o
> agente não redigiu um alerta sem dado. Embaixo, as etiquetas extraídas: nome da tarefa, agente,
> entrada, ferramenta, passos, saída, tarefa concluída — as mesmas para qualquer sistema que o LangNet
> gere. À direita, o registro de cada disparo da rede, com a hora e as marcas que passaram de um lugar a
> outro. E o log da execução, do carregamento do projeto até o comando de início.

**Produção:** 40 s. Na primeira tela, destaque "Situação INDETERMINADA" e a linha de etiquetas
(`tags_extracted`).

---

# ENCERRAMENTO

## Cena 44 · A cadeia inteira

**Tela:** `telas/12b-codigo-rastreabilidade-md.png` (retomada)

**Narração:**
> Percorremos o pipeline inteiro com uma frase da ata: identificar multirresistência. Ela virou o
> requisito FR-031, o caso de uso UC-011, uma coluna do banco, uma tela, a tarefa T-AGN-003, um bloco
> do tasks.yaml, o lugar P3 da rede, uma linha desta matriz e treze casos de teste. Cada documento
> registra de qual versão do anterior nasceu. E quando um teste falha, como falhou aqui, a cadeia diz
> exatamente onde corrigir.

**Produção:** 35 s. Fecha nas linhas FR-031 e FR-032.
