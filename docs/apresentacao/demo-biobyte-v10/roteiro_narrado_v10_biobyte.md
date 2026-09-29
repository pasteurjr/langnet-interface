# Roteiro narrado — LangNet: o pipeline de SDD, etapa por etapa (v10)

**O que o vídeo mostra:** o LangNet percorrendo o pipeline do Desenvolvimento Orientado a
Especificação para um projeto real, o BioByte Sentinela. Cada etapa do menu lateral abre com uma
cartela com o nome da etapa, o que entra e o que sai; em seguida vêm a instrução usada, o documento
gerado e os seus detalhes. No fim, o sistema gerado funcionando.

**Pasta das telas:** `telas/` (ao lado deste arquivo)
**Duração estimada:** cerca de 18 minutos.

**Como ler cada cena:** **Tela** (o arquivo a mostrar), **Narração** (o texto exato que o narrador
fala) e **Produção** (duração e o que destacar). As cartelas de etapa são os arquivos `C01` a `C13`.

**O fio condutor.** Um único requisito atravessa o vídeo: *identificar multirresistência no
antibiograma*. Em cada etapa, a câmera vai até ele.

**O que é real e o que é simulado.** Nenhuma etapa foi gerada de novo para o vídeo, com duas
exceções reais: a correção do Modelo de Dados por conversa (feita em 28/09) e a edição da tela do
UC-011 na etapa de Interface, que gerou a Especificação v2 e refez a tela (feita em 29/09). Onde
aparece uma instrução ou pedido digitado sem efeito, ele foi escrito no campo e **não enviado** — a
Produção de cada cena diz. Três imagens foram montadas a partir de dados do banco, e a Produção as
identifica: a estrutura do documento de requisitos e as duas comparações de versões. A aplicação e
a Bancada foram filmadas rodando.

---

# ABERTURA

## Cena 1 · O que é o LangNet

**Tela:** `telas/01a-lista-de-projetos.png`

**Narração:**
> O LangNet é um software que implementa o pipeline do Desenvolvimento Orientado a Especificação. Ele
> conduz um projeto por uma sequência fixa de etapas — dos documentos do cliente até o código e os
> testes — e em cada etapa produz um documento que se pode ler, corrigir e aprovar. Cada documento
> registra de qual versão do documento anterior nasceu. É essa cadeia que dá a rastreabilidade: de
> qualquer linha de código dá para voltar até a frase do cliente que a originou.

**Produção:** 30 s. Destaque o cartão do BioByte Sentinela v5.

---

## Cena 2 · Criar o projeto

**Tela:** `telas/01b-criar-projeto.png`

**Narração:**
> Um projeto nasce com um nome, um domínio e uma descrição curta — e com as escolhas técnicas: o modelo
> de linguagem que as etapas vão usar, o framework de agentes do sistema gerado e o protocolo. O nosso
> é o BioByte Sentinela, um sistema de vigilância de infecção de corrente sanguínea associada a cateter.

**Produção:** 20 s. Formulário preenchido e não enviado — o projeto já existe.

---

## Cena 3 · O pipeline, no menu lateral

**Tela:** `telas/00-pipeline-menu-lateral.png`

**Narração:**
> Dentro do projeto, o menu lateral é o pipeline, na ordem em que ele é executado: documentos e
> requisitos, especificação, modelo de dados, interface e protótipo, agentes e tarefas, ferramentas, os
> arquivos YAML, a sequência de tarefas, a rede de Petri, a geração de código e os casos de teste.
> Todas as etapas funcionam do mesmo jeito: escolhe-se o documento de origem e a versão, escreve-se uma
> instrução, gera-se o documento, confere-se, corrige-se conversando com o agente da etapa, e aprova-se.
> Vamos passar por cada uma.

**Produção:** 35 s. A moldura laranja marca as 11 etapas; percorra-as de cima para baixo.

---

# ETAPA 1 — DOCUMENTOS E REQUISITOS

## Cena 4 · Cartela

**Tela:** `telas/C01-cartela.png`

**Narração:**
> Etapa um: documentos e requisitos. Entra a ata do cliente; sai o documento de requisitos.

**Produção:** 6 s.

---

## Cena 5 · O documento do cliente

**Telas:** `telas/02c-documento-fonte-problema.png`, `telas/02d-documento-fonte-multirresistencia.png`, `telas/02e-documento-fonte-secao7.png`

**Narração:**
> Tudo começa na ata da comissão de controle de infecção: trezentas e doze linhas com as falas da
> reunião. O problema, nas palavras da coordenadora, é tempo — entre a hemocultura ficar pronta e alguém
> perceber a infecção, passam às vezes dois dias. Na seção dois ponto seis, a frase que vamos seguir: o
> sistema deve identificar se o germe é multirresistente, resistência a três ou mais classes de
> antimicrobianos. E o documento termina separando o que é trabalho de inteligência artificial — cinco
> coisas — do que é sistema comum.

**Produção:** 40 s. Três cortes; na segunda tela, aponte a linha 115.

---

## Cena 6 · A instrução usada e a análise

**Telas:** `telas/02a-documentos-instrucao.png`, `telas/02b-documentos-conversa-analise.png`

**Narração:**
> O documento é carregado e vai junto com a instrução que foi usada neste projeto: a seção sete declara
> o que é trabalho de agente, todo o resto é convencional, classifique cada requisito de acordo. A
> conversa fica gravada: o pedido e, quatro minutos depois, o documento de requisitos pronto.

**Produção:** 22 s. É a instrução real desta análise, redigitada no campo para a cena.

---

## Cena 7 · Como o documento de requisitos é organizado

**Tela:** `telas/03a1-requisitos-estrutura.png`

**Narração:**
> O documento de requisitos tem vinte seções. Três tipos de requisito: funcionais, que dizem o que o
> sistema faz — noventa e nove, dos quais dezessete de natureza agêntica; não funcionais, que dizem como
> ele se comporta — segurança, desempenho, disponibilidade; e regras de negócio, as regras do domínio.
> Depois vêm atores, entidades de dados, fluxos de trabalho, glossário, duas matrizes de rastreabilidade
> e as perguntas em aberto. E cada item traz a sua procedência: extraído do documento, da instrução,
> inferido pelo modelo, vindo da pesquisa na web, ou sugerido pela IA e pendente de aprovação.

**Produção:** 45 s. Imagem montada a partir das seções do documento gerado.

---

## Cena 8 · Os números e o nosso requisito

**Telas:** `telas/03a-requisitos-estatisticas.png`, `telas/03b-requisitos-tabela-fr031.png`

**Narração:**
> Nas estatísticas, a procedência em números: cento e trinta e nove itens vieram do documento, um da
> instrução, quinze foram sugeridos pela IA. Na tabela, cada requisito tem identificador, origem,
> natureza, descrição, prioridade, atores e critério de aceite. O nosso é o FR-031, identificar
> multirresistência, agêntico. Logo abaixo, o FR-032, a regra das três classes, é convencional: contar
> é regra fechada.

**Produção:** 35 s. FR-031 em vermelho, FR-032 em azul.

---

## Cena 9 · De onde veio, e como se corrige

**Telas:** `telas/03d-requisitos-rastreabilidade-origem.png`, `telas/03f-requisitos-refinar-com-agente.png`

**Narração:**
> A seção onze liga cada requisito ao trecho da ata de onde nasceu — é o primeiro elo da
> rastreabilidade. E para corrigir o documento não se edita o texto: pede-se ao agente da etapa, em
> português, e ele grava uma versão nova, mantendo a anterior.

**Produção:** 25 s. Pedido digitado e não enviado.

---

# ETAPA 2 — ESPECIFICAÇÃO

## Cena 10 · Cartela

**Tela:** `telas/C02-cartela.png`

**Narração:**
> Etapa dois: especificação. Entra o documento de requisitos; saem os casos de uso.

**Produção:** 6 s.

---

## Cena 11 · Origem, versão e instrução

**Telas:** `telas/04a-especificacao-escolher-origem.png`, `telas/04b-especificacao-origem-e-instrucao.png`

**Narração:**
> Escolhe-se a origem: o documento de requisitos, versão um, que se pode abrir e conferir antes de
> usar. A etapa passa a mostrar a base escolhida. E a instrução: declarar em cada caso de uso agêntico o
> que o agente decide, escrever os fluxos de exceção com a mensagem que o usuário vê, e desenhar o
> esquema da tela com os mesmos campos do fluxo.

**Produção:** 28 s. Instrução digitada e não enviada.

---

## Cena 12 · O caso de uso UC-011

**Telas:** `telas/04d-especificacao-uc011-cabecalho.png`, `telas/04e-especificacao-uc011-fluxo-principal.png`

**Narração:**
> O FR-031 virou o caso de uso UC-011. Ator principal: o agente de IA. Natureza: agêntica. A decisão do
> agente está escrita, e o caso de uso aponta os requisitos de onde nasceu. O fluxo principal é um
> roteiro em duas colunas: o que o ator faz e o que o sistema responde na tela, passo a passo — lê o
> antibiograma, agrupa por classe, conta, decide, justifica.

**Produção:** 35 s. Destaque Natureza, Decisão do Agente e RFs Relacionados; depois as duas colunas.

---

## Cena 13 · Exceções e o esquema da tela

**Telas:** `telas/04f-especificacao-uc011-excecoes.png`, `telas/04g-especificacao-uc011-croqui.png`

**Narração:**
> Os fluxos de exceção — antibiograma sem classe, falha do agente, resultado pendente — cada um com a
> mensagem exata que aparece na tela. E o esquema da tela, desenhado dentro do caso de uso: as seções,
> os campos e os botões que o fluxo cita. É a partir desse esquema que a interface será gerada.

**Produção:** 30 s.

---

## Cena 14 · A matriz e as versões

**Telas:** `telas/04h-especificacao-matriz-rastreabilidade.png`, `telas/04j-especificacao-historico.png`

**Narração:**
> No fim, a matriz liga cada requisito ao seu caso de uso: FR-031 e FR-032 ao UC-011. E o histórico
> guarda cada versão da especificação, com a versão dos requisitos de onde ela nasceu. A versão dois
> desta especificação vamos ver nascer daqui a pouco, na etapa de interface.

**Produção:** 25 s.

---

# ETAPA 3 — MODELO DE DADOS

## Cena 15 · Cartela

**Tela:** `telas/C03-cartela.png`

**Narração:**
> Etapa três: modelo de dados. Entra a especificação; saem as tabelas do banco.

**Produção:** 6 s.

---

## Cena 16 · A origem e a conferência

**Tela:** `telas/05a-modelo-origem-e-validacao.png`

**Narração:**
> A origem está no alto, com data e hora; escolhe-se o banco. O resultado: vinte e oito tabelas. E a
> etapa confere o que gerou antes de alguém aprovar — nota setenta e cinco, quinze problemas, cada um
> com tabela e coluna. O primeiro: uma coluna de escore sem precisão, que o banco truncaria.

**Produção:** 25 s. Destaque a faixa "Origem" e a caixa amarela.

---

## Cena 17 · O requisito virou coluna

**Telas:** `telas/05b0-modelo-entidade-resultados-hemocultura.png`, `telas/05b-modelo-sql-multirresistencia.png`

**Narração:**
> O documento vem em quatro formas: entidades, SQL, classes e migração. A tabela de resultados de
> hemocultura tem a coluna multirresistente — é ali que a decisão do agente vai ficar —, e o esquema SQL
> a declara.

**Produção:** 20 s.

---

## Cena 18 · Uma correção de verdade, e a comparação

**Telas:** `telas/05d-modelo-conversa-real.png`, `telas/05e-modelo-historico-v1-v2.png`, `telas/05f-modelo-comparacao-v1-v2.png`

**Narração:**
> Esta correção foi feita de fato. O pedido, em português: três colunas estão como decimal sem casas, um
> escore de zero vírgula seis dois vira um; troque para duas casas. A resposta é o programa comparando o
> antes e o depois: três linhas saíram, três entraram. O histórico agora tem a versão um e a versão
> dois. E lado a lado: só as três colunas pedidas mudaram.

**Produção:** 40 s. A comparação foi montada com as duas versões gravadas no banco.

---

# ETAPA 4 — INTERFACE E PROTÓTIPO

## Cena 19 · Cartela

**Tela:** `telas/C04-cartela.png`

**Narração:**
> Etapa quatro: interface e protótipo. Entram a especificação e o modelo de dados; saem as telas.

**Produção:** 6 s.

---

## Cena 20 · A tela, componente por componente

**Telas:** `telas/06a-interface-origem-e-instrucao.png`, `telas/06c-interface-uc011-componentes-ligados.png`

**Narração:**
> São trinta telas, uma por caso de uso. A do UC-011 é declarada componente por componente, e cada
> componente diz a que coluna do banco está ligado: o campo Multirresistente aponta para a coluna que
> vimos no modelo de dados. As mensagens de aviso são as dos fluxos de exceção.

**Produção:** 25 s. Instrução digitada e não enviada.

---

## Cena 21 · O protótipo navegável

**Tela:** `telas/06d-interface-prototipo-uc011.png`

**Narração:**
> E antes de existir sistema, a tela já pode ser navegada no protótipo, com dados de exemplo. É aqui que
> o cliente vê a tela e pede ajuste, quando mudar ainda é barato.

**Produção:** 15 s.

---

## Cena 22 · Modificar a tela editando o roteiro

**Telas:** `telas/06e-interface-editar-no-spec-e-regenerar.png`, `telas/04k-especificacao-edicao-pelo-prototipo.png`

**Narração:**
> A tela pode ser modificada e visualizada ao mesmo tempo. Aqui, ao lado da tela, está a origem dela na
> especificação: o fluxo de eventos e o esquema da tela, editáveis. Acrescentamos uma linha ao esquema:
> o limiar da regra, três classes resistentes, regra BR-009. Ao salvar, a mudança vira uma versão nova
> da especificação, e a tela é regenerada a partir dela.

**Produção:** 35 s. Edição feita de verdade em 29/09/2026; destaque a linha nova.

---

## Cena 23 · A especificação versão dois

**Tela:** `telas/04l-especificacao-comparacao-v1-v2.png`

**Narração:**
> A especificação ganhou a versão dois. Na comparação, a versão um à esquerda, a dois à direita: no
> esquema da tela do UC-011, uma linha acrescentada — o limiar da regra.

**Produção:** 18 s. Montada com as duas versões gravadas no banco.

---

## Cena 24 · A tela refeita a partir da versão dois

**Telas:** `telas/06f-interface-tela-regenerada-v2.png`, `telas/06g-interface-mockup-regenerado.png`

**Narração:**
> E a tela foi refeita: ganhou o indicador limiar da regra, e o selo agora diz gerado do UC-011,
> especificação versão dois. No desenho da tela, o novo cartão aparece ao lado da decisão: multirresistente,
> sim; três classes; limiar três.

**Produção:** 25 s. Destaque o componente novo e o selo "Especificação v2".

---

# ETAPA 5 — AGENTES E TAREFAS

## Cena 25 · Cartela

**Tela:** `telas/C05-cartela.png`

**Narração:**
> Etapa cinco: agentes e tarefas. Entra a especificação; saem os agentes e as tarefas.

**Produção:** 6 s.

---

## Cena 26 · Cinco tarefas, dois agentes

**Telas:** `telas/07b-agentes-origem-e-instrucao.png`, `telas/07c-agentes-cinco-tarefas.png`

**Narração:**
> A instrução deste projeto pedia que só os casos de uso de natureza agêntica virassem tarefa de agente.
> O documento gerado confere isso antes de decidir: trinta e um casos de uso entraram, cinco viraram
> tarefa, em dois agentes. O UC-011 virou a tarefa T-AGN-003.

**Produção:** 25 s. Instrução digitada e não enviada.

---

## Cena 27 · O agente e a ficha da tarefa

**Telas:** `telas/07d-agentes-agente-ag01.png`, `telas/07e-agentes-tarefa-t003-rastreabilidade.png`

**Narração:**
> O agente tem papel, objetivo, história profissional e as ferramentas que pode usar. E a ficha da tarefa
> traz entrada, saída, restrições, casos de borda — e termina na rastreabilidade: caso de uso UC-011,
> requisitos FR-031 e FR-032, regra de negócio BR-009.

**Produção:** 28 s. Destaque UC, RF e RN Relacionado.

---

# ETAPA 6 — FERRAMENTAS

## Cena 28 · Cartela

**Tela:** `telas/C06-cartela.png`

**Narração:**
> Etapa seis: ferramentas.

**Produção:** 5 s.

---

## Cena 29 · Quem implementa cada ferramenta

**Telas:** `telas/08a-ferramentas-inventario.png`, `telas/08b-ferramentas-contrato.png`

**Narração:**
> Cada ferramenta que os agentes usam precisa dizer de onde vem a implementação; sem isso, a geração
> escreveria uma ferramenta que finge funcionar. Três ferramentas, as três resolvidas. E a determinística
> tem o seu contrato: o que faz, entrada, saída e a regra que vira código.

**Produção:** 25 s. Destaque "Pendentes 0".

---

# ETAPA 7 — YAML DE AGENTES E TAREFAS

## Cena 30 · Cartela

**Tela:** `telas/C07-cartela.png`

**Narração:**
> Etapa sete: os arquivos YAML de agentes e tarefas.

**Produção:** 5 s.

---

## Cena 31 · Os arquivos que o framework lê

**Telas:** `telas/09a-yaml-origem.png`, `telas/09c-yaml-tasks-multirresistencia.png`

**Narração:**
> A origem é o documento de agentes e tarefas, versão um. No tasks.yaml, a nossa tarefa: o formato da
> entrada, que vem da tarefa de tradução, e os passos — agrupar por classe, não contar intermediário,
> decidir multirresistente quando a contagem for três ou mais.

**Produção:** 25 s. Aponte os passos 7 e 9.

---

# ETAPA 8 — SEQUÊNCIA DE TAREFAS

## Cena 32 · Cartela

**Tela:** `telas/C08-cartela.png`

**Narração:**
> Etapa oito: sequência de tarefas.

**Produção:** 5 s.

---

## Cena 33 · O que cada tarefa recebe, e de quem

**Telas:** `telas/10a2-sequencia-origens-fixadas.png`, `telas/10c-sequencia-task3.png`

**Narração:**
> A sequência parte de três origens: a especificação, o documento de agentes e tarefas e o tasks.yaml.
> Ela diz em que ordem as tarefas acontecem e de onde vem cada dado: a tarefa três recebe o antibiograma
> traduzido, que vem da tarefa um.

**Produção:** 22 s.

---

# ETAPA 9 — REDE DE PETRI

## Cena 34 · Cartela

**Tela:** `telas/C09-cartela.png`

**Narração:**
> Etapa nove: rede de Petri.

**Produção:** 5 s.

---

## Cena 35 · A rede, e o que tem dentro de um lugar

**Telas:** `telas/11a-petri-origem.png`, `telas/11c-petri-rede-inteira.png`, `telas/11d-petri-json-lugar-p3.png`

**Narração:**
> A rede é gerada do agents.yaml, do tasks.yaml e da sequência. Um lugar de início, cinco de tarefa, um
> de fim, e as transições que liberam a próxima. O lugar P3, em vermelho, é a multirresistência. Por
> dentro, cada lugar tem a tarefa, os campos que espera e o código que chama o servidor de agentes.

**Produção:** 30 s. Diálogo de geração preenchido e não enviado.

---

# ETAPA 10 — GERAÇÃO DE CÓDIGO

## Cena 36 · Cartela

**Tela:** `telas/C10-cartela.png`

**Narração:**
> Etapa dez: geração de código.

**Produção:** 5 s.

---

## Cena 37 · O sistema, e a linha que liga tudo

**Telas:** `telas/12a-codigo-origens.png`, `telas/12b-codigo-rastreabilidade-md.png`

**Narração:**
> A geração parte dos arquivos YAML, da sequência e do documento de agentes e tarefas. Sai o sistema
> inteiro — cento e trinta e oito arquivos — e um arquivo de rastreabilidade: FR-031, UC-011, a tarefa
> de multirresistência, a tela do detalhe do caso. Uma linha liga tudo.

**Produção:** 25 s. Linhas 38 e 39 selecionadas.

---

## Cena 38 · O portão antes de implantar

**Tela:** `telas/12e-codigo-portoes-pendencias.png`

**Narração:**
> Antes de liberar, a geração confere o que foi pedido contra o que foi gerado, e aponta os passos de
> lógica que não viraram código. Com pendência, a versão não é implantada sem uma decisão explícita.

**Produção:** 18 s.

---

# ETAPA 11 — CASOS DE TESTE E VALIDAÇÃO

## Cena 39 · Cartela

**Tela:** `telas/C11-cartela.png`

**Narração:**
> Etapa onze: casos de teste e validação.

**Produção:** 5 s.

---

## Cena 40 · Do caso de uso ao caso de teste

**Telas:** `telas/13b-testes-grafo-uc011.png`, `telas/13c-testes-tabela-decisao-uc011.png`, `telas/13d-testes-casos-uc011.png`

**Narração:**
> Para cada caso de uso, um grafo de causa e efeito — no UC-011, nove causas e treze efeitos. Do grafo
> sai a tabela de decisão, e cada coluna vira um caso de teste: com três ou mais classes resistentes, o
> sistema deve mostrar multirresistente igual a sim; com menos, igual a não.

**Produção:** 30 s. Aponte TC-UC-011-03 e 04.

---

## Cena 41 · O teste que reprovou

**Tela:** `telas/13e-testes-registro-execucao.png`

**Narração:**
> Executados na aplicação, vinte e dois de vinte e três passaram. O que reprovou era justamente o nosso:
> a contagem saía certa, mas o veredito voltava vazio. A cadeia de documentos disse onde estava o
> defeito; ele foi corrigido no gerador, e o código foi gerado e implantado de novo.

**Produção:** 22 s. Destaque a linha vermelha.

---

# OPERAÇÃO — O SISTEMA IMPLANTADO

## Cena 42 · Cartela

**Tela:** `telas/C12-cartela.png`

**Narração:**
> Agora a operação: o sistema implantado.

**Produção:** 5 s.

---

## Cena 43 · Implantar

**Tela:** `telas/14a-implantacao.png`

**Narração:**
> A implantação escolhe a versão gerada e recebe a configuração: o banco e o provedor de IA. Os portões
> avisam das pendências antes de subir. No ar: a interface, a API e o servidor de agentes.

**Produção:** 18 s. Senha e chave aparecem mascaradas.

---

## Cena 44 · Um cadastro, conferido no banco

**Telas:** `telas/40-crud-2-novo-preenchido.png`, `telas/40-crud-3-salvo-na-lista.png`, `telas/40-crud-5-excluido.png`

**Narração:**
> Este é o sistema que saiu do pipeline. Um paciente novo: salvo, ele aparece na lista e no banco;
> excluído, a lista volta ao que era. Conferido no banco a cada passo.

**Produção:** 18 s.

---

## Cena 45 · Os agentes na tela do hospital

**Telas:** `telas/30-cadeia-1-traducao-b-resultado.png`, `telas/31-cadeia-2-classificacao-b-resultado.png`

**Narração:**
> A primeira tarefa de inteligência artificial: o agente leu o antibiograma do caso no banco e devolveu
> no vocabulário do hospital, *Staphylococcus aureus* e seis antimicrobianos com a sua classe. A
> classificação pela norma respondeu pendente, e disse por quê: os critérios e a data de início do caso
> não chegaram na entrada — uma lacuna conhecida, apontada.

**Produção:** 30 s.

---

## Cena 46 · O veredito e o alerta

**Telas:** `telas/32-cadeia-3-multirresistencia-b-resultado.png`, `telas/34-cadeia-5-alerta-b-resultado.png`

**Narração:**
> A tarefa que seguimos o vídeo inteiro: quatro classes resistentes, o carbapenêmico de fora porque era
> intermediário, e o veredito — multirresistente, sim. Com ele, a última tarefa redige o alerta para a
> equipe da UTI: o microrganismo, as quatro classes, por que importa para um paciente com cateter e o
> que fazer.

**Produção:** 30 s. Destaque "multirresistente: true" e o início do texto do alerta.

---

## Cena 47 · As decisões gravadas

**Telas:** `telas/45-decisoes-gravadas.png`, `telas/45-decisao-alerta-detalhe.png`

**Narração:**
> Cada resposta ficou gravada, ligada ao caso, com a tarefa e a versão do prompt que a produziu. É o que
> a enfermeira da reunião pediu: mostrar depois por qual critério, com base em quê e quando.

**Produção:** 20 s.

---

# OPERAÇÃO — EXECUÇÃO DE AGENTES

## Cena 48 · Cartela

**Tela:** `telas/C13-cartela.png`

**Narração:**
> Execução de agentes: a bancada.

**Produção:** 5 s.

---

## Cena 49 · A entrada da execução

**Tela:** `telas/71-bancada-entrada-aplicada.png`

**Narração:**
> A bancada roda a rede de Petri contra o servidor de agentes. No alto, a entrada: os campos que as
> primeiras tarefas da rede esperam. O operador informa o caso e aplica.

**Produção:** 15 s.

---

## Cena 50 · Tarefa a tarefa, pela aba Operação

**Telas:** `telas/72-operacao-P1.png`, `telas/72-operacao-P3.png`, `telas/72-operacao-P5.png`

**Narração:**
> Em modo pausar por tarefa, a rede para em cada lugar. A aba Operação mostra a tarefa e o agente, tudo o
> que ele recebeu — as regras, a instrução do tasks.yaml, o caso —, os passos da execução e o documento
> produzido. Na tradução, o antibiograma. Na multirresistência, o veredito. Na última, o alerta. O
> operador confere cada saída e aprova ou refaz.

**Produção:** 40 s. Três cortes.

---

# ENCERRAMENTO

## Cena 51 · Do documento ao alerta

**Tela:** `telas/12b-codigo-rastreabilidade-md.png` (retomada)

**Narração:**
> Uma frase da ata virou requisito, caso de uso, coluna, tela, tarefa, lugar da rede e casos de teste —
> e, no sistema gerado, uma decisão gravada e um alerta redigido. Cada etapa registrou de onde veio, e
> cada correção entrou na etapa certa: na especificação, pelo protótipo; no modelo de dados, por
> conversa; no gerador, quando o teste reprovou.

**Produção:** 30 s.
