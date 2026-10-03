# Roteiro narrado — LangNet: o pipeline de SDD em 10 minutos (v11)

**O que o vídeo mostra:** o LangNet conduzindo um projeto real, o BioByte Sentinela, por todas as
etapas do pipeline do menu lateral. Em cada etapa aparecem a instrução usada, o documento gerado com
as partes que importam e, onde houve, a comparação entre versões. No fim, o sistema gerado rodando: a
tela de um agente, a rede de Petri executando com o token andando e a tela da tarefa em execução.

**Pasta das telas:** `telas/` (ao lado deste arquivo) · **Duração:** 9 min 50 s (máximo 10 min) · 1219 palavras de narração.

**Como ler cada cena:** **Tela** (o arquivo a mostrar), **Narração** (o texto exato que o narrador
fala) e **Produção** (duração e o que destacar). As cartelas de etapa (`C01` a `C13`) ficam 2 segundos
na tela, sem narração: o nome da etapa é dito na cena seguinte.

**O fio condutor:** um único requisito atravessa o vídeo — *identificar multirresistência no
antibiograma*. Em cada etapa, a câmera vai até ele.

**O que é real e o que é simulado.** Nada foi gerado de novo para o vídeo. As três comparações de
versões são reais: a especificação v1 × v2 (nasceu da edição da tela no protótipo, 29/09), o modelo de
dados v1 × v2 (correção por conversa, 28/09) e a tela v1 × v2. As duas comparações de documento foram
montadas com as versões gravadas no banco. Nas demais etapas o projeto tem uma versão só; ali o vídeo
mostra o histórico e o pedido de refino digitado e **não enviado**. A aplicação, a rede de Petri em
execução e a tela da tarefa foram filmadas rodando.

---

# ABERTURA

## Cena 1 · Uma fábrica de aplicações

**Telas:** `telas/01a-lista-de-projetos.png`, `telas/00-pipeline-menu-lateral.png`

**Narração:**
> Este é o LangNet: uma aplicação que fabrica aplicações seguindo o Desenvolvimento Orientado a
> Especificação. O menu lateral é o pipeline, na ordem em que roda: documentos e requisitos,
> especificação, modelo de dados, interface e protótipo, agentes e tarefas, ferramentas, os arquivos
> YAML, a sequência, a rede de Petri, o código e os testes. Toda etapa funciona igual: escolhe-se a
> origem e a versão, dá-se uma instrução, gera-se o documento, corrige-se conversando com o agente da
> etapa e aprova-se. O projeto de hoje é o BioByte Sentinela, vigilância de infecção hospitalar.

**Produção:** 41 s. Primeiro o cartão do BioByte v5; depois a moldura percorrendo as 11 etapas.

---

# ETAPA 1 — DOCUMENTOS E REQUISITOS

## Cena 2 · Cartela

**Tela:** `telas/C01-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 3 · O documento do cliente e a instrução

**Telas:** `telas/02d-documento-fonte-multirresistencia.png`, `telas/02a-documentos-instrucao.png`

**Narração:**
> Primeira etapa, documentos e requisitos. A entrada é a ata da comissão de controle de infecção. Na
> linha cento e quinze, a frase que vamos seguir: o sistema deve identificar se o germe é
> multirresistente, com resistência a três ou mais classes de antimicrobianos. Junto vai a instrução
> deste projeto: a seção sete da ata diz o que é trabalho de inteligência artificial; todo o resto é
> sistema convencional.

**Produção:** 32 s. Destaque a linha 115; depois a instrução no campo.

---

## Cena 4 · Como o documento de requisitos é organizado

**Tela:** `telas/03a1-requisitos-estrutura.png`

**Narração:**
> Quatro minutos depois, o documento de requisitos: vinte seções. Noventa e nove requisitos
> funcionais, que dizem o que o sistema faz, dezessete deles de natureza agêntica. Os não funcionais:
> segurança, desempenho, disponibilidade. As regras de negócio do domínio. E ainda atores, entidades,
> fluxos, glossário e as perguntas em aberto para o cliente.

**Produção:** 24 s. Imagem montada a partir das seções do documento gerado.

---

## Cena 5 · Procedência de cada requisito

**Telas:** `telas/03a-requisitos-estatisticas.png`, `telas/03b-requisitos-tabela-fr031.png`

**Narração:**
> Cada requisito diz de onde veio. Cento e trinta e nove itens foram extraídos do documento; outros
> foram inferidos, trazidos da pesquisa na web ou sugeridos pela IA e esperam aprovação. Na tabela, o
> nosso: FR-031, identificar multirresistência, natureza agêntica, com o critério de aceite. Logo
> abaixo, o FR-032, a regra das três classes, é convencional, porque contar é regra fechada.

**Produção:** 28 s. FR-031 em vermelho, FR-032 em azul.

---

## Cena 6 · O trecho de origem e o refino por conversa

**Telas:** `telas/03d-requisitos-rastreabilidade-origem.png`, `telas/03f-requisitos-refinar-com-agente.png`

**Narração:**
> Uma matriz liga cada requisito ao trecho da ata que o originou: é o primeiro elo da rastreabilidade.
> E, para corrigir, não se edita o texto: pede-se ao agente, em português, e ele grava uma versão nova
> ao lado da anterior.

**Produção:** 19 s. Pedido digitado e não enviado.

---

# ETAPA 2 — ESPECIFICAÇÃO

## Cena 7 · Cartela

**Tela:** `telas/C02-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 8 · Origem, versão e instrução

**Tela:** `telas/04b-especificacao-origem-e-instrucao.png`

**Narração:**
> Segunda etapa, a especificação funcional. A origem é o documento de requisitos, versão um. A
> instrução pede três coisas: declarar o que o agente decide em cada caso de uso agêntico, escrever os
> fluxos de exceção com a mensagem que o usuário vê, e desenhar o esquema da tela com os mesmos campos
> do fluxo.

**Produção:** 25 s. Instrução digitada e não enviada.

---

## Cena 9 · O caso de uso UC-011

**Telas:** `telas/04d-especificacao-uc011-cabecalho.png`, `telas/04e-especificacao-uc011-fluxo-principal.png`

**Narração:**
> O FR-031 virou o caso de uso UC-011. O ator principal é o agente de IA, e a decisão dele está
> escrita: com base no antibiograma, decidir se o germe é multirresistente e justificar. O fluxo
> principal tem duas colunas, o que o ator faz e o que o sistema responde: lê o antibiograma, agrupa
> por classe, conta, decide e justifica.

**Produção:** 28 s. Destaque Natureza, Decisão do Agente e RFs Relacionados; depois as duas colunas.

---

## Cena 10 · Exceções e o esquema da tela

**Telas:** `telas/04f-especificacao-uc011-excecoes.png`, `telas/04g-especificacao-uc011-croqui.png`

**Narração:**
> Os fluxos de exceção: antibiograma sem classe, falha do agente, resultado pendente, cada um com a
> mensagem exata da tela. E dentro do próprio caso de uso, o esquema da tela, com os campos e os
> botões do fluxo. É desse esquema que a interface vai nascer.

**Produção:** 22 s.

---

## Cena 11 · A matriz, e a versão dois

**Telas:** `telas/04h-especificacao-matriz-rastreabilidade.png`, `telas/04l-especificacao-comparacao-v1-v2.png`

**Narração:**
> No fim do documento, a matriz liga cada requisito ao seu caso de uso: FR-031 e FR-032 ao UC-011. E
> aqui a comparação entre versões: a especificação ganhou a versão dois. À esquerda a um, à direita a
> dois; no esquema da tela do UC-011, uma linha nova, o limiar da regra.

**Produção:** 24 s. Comparação montada com as duas versões gravadas no banco; destaque a linha nova.

---

# ETAPA 3 — MODELO DE DADOS

## Cena 12 · Cartela

**Tela:** `telas/C03-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 13 · As tabelas, a conferência e a correção

**Telas:** `telas/05a-modelo-origem-e-validacao.png`, `telas/05b0-modelo-entidade-resultados-hemocultura.png`

**Narração:**
> Terceira etapa, o modelo de dados: vinte e oito tabelas geradas da especificação. A etapa confere o
> próprio resultado antes da aprovação: nota setenta e cinco, quinze pontos a revisar. Na tabela de
> resultados de hemocultura, a coluna multirresistente: é ali que a decisão do agente vai ficar
> gravada.

**Produção:** 23 s. Destaque a caixa amarela e a coluna multirresistente.

---

## Cena 14 · A correção por conversa, e a comparação

**Telas:** `telas/05d-modelo-conversa-real.png`, `telas/05f-modelo-comparacao-v1-v2.png`

**Narração:**
> A correção foi feita de verdade, em português: três colunas de escore estavam sem casas decimais;
> troque para duas. O programa responde comparando o antes e o depois, e grava a versão dois. Lado a
> lado, só as três colunas pedidas mudaram.

**Produção:** 20 s. Comparação montada com as duas versões gravadas no banco.

---

# ETAPA 4 — INTERFACE E PROTÓTIPO

## Cena 15 · Cartela

**Tela:** `telas/C04-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 16 · A tela e o protótipo

**Telas:** `telas/06c-interface-uc011-componentes-ligados.png`, `telas/06d-interface-prototipo-uc011.png`

**Narração:**
> Quarta etapa, interface e protótipo: trinta telas, uma por caso de uso. A do UC-011 é declarada
> componente por componente, cada um ligado a uma coluna do banco. Antes de existir sistema, ela já
> pode ser navegada no protótipo, com dados de exemplo, que é quando mudar ainda é barato.

**Produção:** 23 s.

---

## Cena 17 · Editar e ver ao mesmo tempo

**Telas:** `telas/06e-interface-editar-no-spec-e-regenerar.png`, `telas/06f-interface-tela-regenerada-v2.png`

**Narração:**
> Ao lado da tela fica a origem dela na especificação, editável. Acrescentamos uma linha ao esquema: o
> limiar da regra, três classes. Ao salvar, a especificação ganha a versão dois, a que acabamos de
> ver, e a tela é refeita a partir dela, com o novo indicador e o selo gerado do UC-011, especificação
> versão dois.

**Produção:** 26 s. Edição real de 29/09; destaque a linha nova e o selo "Especificação v2".

---

# ETAPA 5 — AGENTES E TAREFAS

## Cena 18 · Cartela

**Tela:** `telas/C05-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 19 · Só o que é agêntico vira agente

**Telas:** `telas/07b-agentes-origem-e-instrucao.png`, `telas/07c-agentes-cinco-tarefas.png`, `telas/07e-agentes-tarefa-t003-rastreabilidade.png`

**Narração:**
> Quinta etapa, agentes e tarefas. A instrução: só os casos de uso agênticos viram tarefa de agente.
> Trinta e um casos de uso entraram, cinco viraram tarefa, em dois agentes. O UC-011 virou a tarefa
> T-AGN-003, com entrada, saída, restrições e, no fim da ficha, a rastreabilidade: UC-011, FR-031,
> FR-032 e a regra BR-009.

**Produção:** 25 s. Instrução digitada e não enviada. Destaque o bloco de rastreabilidade.

---

# ETAPA 6 — FERRAMENTAS

## Cena 20 · Cartela

**Tela:** `telas/C06-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 21 · Quem implementa cada ferramenta

**Tela:** `telas/08b-ferramentas-contrato.png`

**Narração:**
> Sexta etapa, ferramentas. Cada ferramenta dos agentes diz quem a implementa: código determinístico,
> tarefa de agente ou um serviço externo por MCP. E tem contrato: o que faz, entrada, saída e a regra
> que vira código.

**Produção:** 17 s.

---

# ETAPA 7 — YAML DE AGENTES E TAREFAS

## Cena 22 · Cartela

**Tela:** `telas/C07-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 23 · O que o framework lê

**Tela:** `telas/09c-yaml-tasks-multirresistencia.png`

**Narração:**
> Sétima etapa, os arquivos YAML. No tasks.yaml, a nossa tarefa: a entrada vem da tarefa de tradução,
> e os passos dizem agrupar por classe, não contar intermediário e decidir multirresistente com três
> ou mais.

**Produção:** 16 s. Aponte os passos 7 e 9.

---

# ETAPA 8 — SEQUÊNCIA DE TAREFAS

## Cena 24 · Cartela

**Tela:** `telas/C08-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 25 · Quem recebe o quê, e de quem

**Tela:** `telas/10c-sequencia-task3.png`

**Narração:**
> Oitava, a sequência: a ordem das tarefas e de onde vem cada dado. A tarefa três recebe o
> antibiograma traduzido, que sai da tarefa um.

**Produção:** 12 s.

---

# ETAPA 9 — REDE DE PETRI

## Cena 26 · Cartela

**Tela:** `telas/C09-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 27 · A rede que orquestra a execução

**Telas:** `telas/11c-petri-rede-inteira.png`, `telas/11d-petri-json-lugar-p3.png`

**Narração:**
> Nona, a rede de Petri. Os círculos são lugares, as barras são transições, e cada caixa é um agente
> com as suas tarefas. O lugar P3 é a multirresistência; por dentro, ele guarda a tarefa, os campos
> que espera e o código que chama o servidor de agentes.

**Produção:** 22 s. P3 em vermelho.

---

# ETAPA 10 — GERAÇÃO DE CÓDIGO

## Cena 28 · Cartela

**Tela:** `telas/C10-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 29 · O sistema, e o portão

**Telas:** `telas/12b-codigo-rastreabilidade-md.png`, `telas/12e-codigo-portoes-pendencias.png`

**Narração:**
> Décima, a geração de código: cento e trinta e oito arquivos, e um arquivo de rastreabilidade em que
> uma linha liga o FR-031, o UC-011, a tarefa e a tela. Antes de liberar, o portão confere o pedido
> contra o gerado, e aponta o que não virou código.

**Produção:** 22 s. Linhas 38 e 39 selecionadas.

---

# ETAPA 11 — CASOS DE TESTE

## Cena 30 · Cartela

**Tela:** `telas/C11-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 31 · Do caso de uso ao teste executado

**Telas:** `telas/13b-testes-grafo-uc011.png`, `telas/13d-testes-casos-uc011.png`, `telas/13e-testes-registro-execucao.png`

**Narração:**
> Décima primeira, os casos de teste. Cada caso de uso vira um grafo de causa e efeito: Cada
> combinação vira um teste: com três ou mais classes resistentes, multirresistente igual a sim.
> Executados na aplicação, vinte e dois de vinte e três passaram, e o que reprovou mostrou onde estava
> o defeito, que foi corrigido na fábrica.

**Produção:** 26 s. Aponte TC-UC-011-03; destaque a linha vermelha no registro.

---

# OPERAÇÃO — O SISTEMA GERADO

## Cena 32 · Cartela

**Tela:** `telas/C12-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 33 · Os agentes na tela do hospital

**Telas:** `telas/32-cadeia-3-multirresistencia-b-resultado.png`, `telas/34-cadeia-5-alerta-b-resultado.png`

**Narração:**
> Implantado, este é o sistema que saiu do pipeline. Na tela da multirresistência, o agente respondeu:
> quatro classes resistentes, o carbapenêmico de fora por ser intermediário, e o veredito,
> multirresistente sim. Com ele, a última tarefa redigiu o alerta para a equipe da UTI, e cada decisão
> ficou gravada com a justificativa.

**Produção:** 24 s. Destaque "multirresistente: true" e o início do alerta.

---

# OPERAÇÃO — EXECUÇÃO DE AGENTES

## Cena 34 · Cartela

**Tela:** `telas/C13-cartela.png`

**Produção:** 2 s, sem narração.

---

## Cena 35 · A rede de Petri executando

**Telas:** `telas/71-bancada-entrada-aplicada.png`, `telas/15b1-bancada-marca-P1.png`, `telas/15b3-bancada-marca-P3.png`

**Narração:**
> Na bancada de execução, o operador informa o caso e a rede de Petri roda contra o servidor de
> agentes. O ponto no lugar é o token, o estado atual da execução. Ele parte do início, passa pela
> tradução e chega à multirresistência; à direita, o registro de cada disparo.

**Produção:** 23 s. Três cortes; acompanhe o token de P1 para P3.

---

## Cena 36 · A tela da tarefa

**Tela:** `telas/72-operacao-P3.png`

**Narração:**
> E, parada na tarefa, a aba Operação mostra tudo: o agente, as regras, a instrução que ele recebeu, o
> caso, os passos da execução e o documento produzido, com o veredito e a justificativa. O operador
> confere e aprova, ou manda refazer com uma mensagem.

**Produção:** 21 s. Destaque o documento gerado à direita e os botões Aprovar / Refazer.

---

# ENCERRAMENTO

## Cena 37 · Do documento ao alerta

**Tela:** `telas/12b-codigo-rastreabilidade-md.png` (retomada)

**Narração:**
> Uma frase da ata virou requisito, caso de uso, coluna, tela, tarefa, lugar da rede e teste, e no
> sistema gerado, uma decisão gravada e um alerta. Cada etapa registrou de onde veio, e cada correção
> entrou na etapa certa. Isso é o LangNet.

**Produção:** 21 s.
