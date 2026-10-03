# -*- coding: utf-8 -*-
"""Roteiro V11 — reescrito por inteiro, na ordem exata das lâminas da V11.
Fala natural: explica as figuras, não lê os cartões. Meta: 50 a 55 minutos de fala (sem os vídeos)."""

FIM = "__fim__"

FALAS = {
"Engenharia de IA e Desenvolvimento Orientado a Especificação":
"Bom dia a todos. Obrigado pelo convite. Hoje a gente vai fazer um percurso longo, mas com um fio só: sair de um classificador que cabe em vinte linhas de código e chegar a uma fábrica de software conduzida por agentes. No meio do caminho vão aparecer aprendizado de máquina, redes neurais, modelos de linguagem, agentes e, no fim, um método de desenvolvimento que junta tudo isso.",

"Pasteur Ottoni de Miranda Júnior":
"Antes de começar, rapidamente quem está falando com vocês. Eu me formei em engenharia aeronáutica no ITA, passei pela Embraer e pela Mannesmann, e desde o início dos anos noventa trabalho com empresa de software e com ensino. Foram trinta anos de PUC Minas, vinte deles coordenando a especialização em Engenharia de Software. Em dois mil e um criei o ComoVou, o primeiro mapa na web do Brasil a calcular rotas, com técnicas clássicas de inteligência artificial. Hoje estou à frente da Quântica.ai. Ou seja: engenharia de software e inteligência artificial andaram juntas na minha carreira inteira, e é exatamente esse encontro o assunto de hoje.",

"O caminho de hoje":
"O roteiro tem três partes. Primeiro, os fundamentos: aprendizado de máquina, aplicação em saúde, redes profundas e modelos de linguagem. Depois, a engenharia em volta desses modelos: agentes, contexto, frameworks, ambientes de programação e protocolos. Por fim, o método: desenvolvimento orientado a especificação, e o LangNet, que é a nossa implementação dele. Ao fim de cada bloco a gente faz uma pausa para ver um notebook sendo executado, e esse notebook fica com vocês.",

"A tese":
"E a tese que eu quero defender está nessa frase. Quando um agente escreve em minutos o código que antes levava semanas, digitar deixa de ser o problema. O que separa um sistema que funciona de um que não funciona passa a ser a clareza do que foi pedido. Guardem essa ideia, porque todo o resto da palestra é uma consequência dela.",

"Introdução e Machine Learning":
"Vamos começar pelo começo: o que diferencia um programa comum de um programa que aprende, e de onde veio tudo isso.",

"Onde fica a fronteira":
"Pensem em dois problemas. Calcular o menor caminho entre duas cidades: existe um procedimento exato, e o programador o escreve passo a passo. Agora, jogar bem uma partida: não existe fórmula para a jogada certa. O programa precisa avaliar as possibilidades e escolher. A diferença está em onde mora o conhecimento. No primeiro caso ele está no código. No segundo, está nos dados, e o código só sabe extraí-lo. Essa é a fronteira do que chamamos de algoritmo inteligente.",

"Setenta anos em um minuto":
"Um minuto de história, só para situar. Nos anos cinquenta, Turing propõe o teste da imitação e Rosenblatt constrói o Perceptron, o primeiro neurônio que aprende. Nos anos oitenta, a retropropagação permite treinar redes de várias camadas. Em dois mil e doze, as redes convolucionais ganham com folga a competição de imagens, e começa o aprendizado profundo. Em dois mil e dezessete aparece o Transformer; cinco anos depois, o ChatGPT. E, de dois mil e vinte e quatro para cá, o assunto passou a ser agentes.",

"Machine Learning":
"Então, Machine Learning.",

"Aprendizado supervisionado e não supervisionado":
"Aprender de dados pode acontecer de duas formas. Na supervisionada existe um professor: eu mostro exemplos com a resposta certa, este paciente teve o desfecho, aquele não, e o modelo aprende a responder para casos novos. Na não supervisionada não há resposta nenhuma; o modelo recebe só os dados e descobre sozinho grupos parecidos. A consequência prática é importante: o supervisionado precisa de dados rotulados, e rotular costuma ser o item mais caro de um projeto clínico.",

"As seis etapas de um projeto de Machine Learning":
"Todo projeto de aprendizado de máquina segue praticamente o mesmo roteiro, que está nessa trilha no alto da lâmina: visualizar os dados, prepará-los, separar os conjuntos, escolher o modelo, treinar e avaliar. E as duas primeiras consomem a maior parte do tempo. Vou passar rapidamente por cada uma.",

"Visualizar e preparar os dados":
"Antes de qualquer modelo, a gente olha os dados: a distribuição de cada variável, a correlação entre elas. É aí que se descobre, por exemplo, uma coluna vazia em metade dos registros. Depois vem a limpeza: tirar valores sem sentido, preencher ausências, descartar o que não serve. E um detalhe que derruba muita gente: colocar tudo na mesma escala. Se uma variável vai de zero a um e outra vai até um milhão, vários algoritmos simplesmente não convergem.",

"Definir os conjuntos e escolher o modelo":
"Com os dados prontos, separamos uma parte, algo como setenta e cinco por cento, para treinar, e guardamos o resto para testar. E existe uma regra que não se negocia: o modelo nunca pode ver no treino os dados com que vai ser avaliado. Quebrar essa regra produz um resultado lindo e falso. Para escolher o algoritmo, ninguém chuta: uma busca em grade experimenta vários algoritmos e combinações de parâmetros e devolve o melhor para aquela base.",

"Treinar e avaliar: o sobreajuste":
"No treino, o perigo tem nome: sobreajuste. O modelo decora os exemplos em vez de aprender o padrão. Dá para ver isso no gráfico por época: o erro no treino continua caindo, mas o erro na validação para de cair e começa a subir. O remédio é parar na hora certa, simplificar o modelo ou arrumar mais dados.",

"Como se mede um classificador":
"E como se avalia? Nunca por um número só. A matriz de confusão mostra os acertos e os erros de cada classe. Dela saem a sensibilidade, quantos doentes o modelo pegou, e a especificidade, quantos sadios ele deixou em paz. A curva ROC mostra o equilíbrio entre as duas. E o alerta que vale para a saúde inteira: acurácia engana. Com dois por cento de prevalência, um modelo que responde sempre não acerta noventa e oito por cento das vezes, e não serve para nada.",

"Com o que se trabalha":
"O ferramental é padronizado: Python, e o Jupyter Notebook ou o Google Colab, que roda no navegador sem instalar nada. Para os algoritmos clássicos, o scikit-learn; todos os que vou mostrar agora estão lá, e cada um é uma linha de código. Para redes profundas, TensorFlow ou PyTorch. E para dados e gráficos, pandas, NumPy e matplotlib.",

"K Vizinhos Mais Próximos":
"Agora, um algoritmo por lâmina, começando pelo mais intuitivo. O K vizinhos mais próximos não constrói modelo nenhum: para classificar um caso novo, ele procura na base os K casos mais parecidos e faz uma votação. Se a maioria dos cinco pacientes mais parecidos teve o desfecho, o novo provavelmente também terá. É ótimo para começar e para explicar, mas fica lento com bases grandes e sofre quando as variáveis não estão na mesma escala.",

"Regressão Linear":
"A regressão linear prevê um número, não uma classe. Ela traça a reta que melhor passa pelos pontos e usa essa reta para estimar valores novos: a dose em função do peso, o tempo de internação em função da idade. A força dela é ser transparente, porque cada coeficiente diz quanto a saída muda quando uma entrada aumenta. O limite é o nome: ela só enxerga relação em linha reta.",

"Regressão Logística":
"Apesar do nome, a regressão logística serve para classificar. Ela pega a mesma combinação de variáveis da regressão linear e a espreme numa curva que vai de zero a um, que se lê como probabilidade. Em saúde, é talvez o algoritmo mais usado, e por um bom motivo: cada coeficiente vira uma razão de chances, que é exatamente a linguagem que o epidemiologista já usa.",

"Árvore de Decisão":
"A árvore de decisão faz uma sequência de perguntas: a febre passa de trinta e oito? O leucograma está alto? Cada resposta leva a um galho, até chegar a uma decisão. O grande valor é que a regra final pode ser lida e contestada pelo clínico. O defeito é que uma árvore sozinha decora com facilidade, e muda muito com pequenas variações nos dados.",

"Random Forest — Floresta Aleatória":
"A floresta aleatória resolve exatamente esse defeito. Em vez de uma árvore, ela treina centenas, cada uma vendo uma amostra diferente dos dados e das variáveis, e decide pela votação de todas. Individualmente, cada árvore erra; juntas, os erros se cancelam. É um dos algoritmos mais robustos que existem para dados de tabela, e ainda diz quais variáveis mais pesaram.",

"Máquina de Vetores de Suporte":
"A máquina de vetores de suporte procura a fronteira que separa as classes com a maior margem possível, como uma estrada o mais larga possível entre dois bairros. Quando os dados não se separam por uma reta, ela usa um truque matemático que leva os pontos para um espaço de mais dimensões, onde a separação fica possível. Funciona muito bem com poucos exemplos e muitas variáveis.",

"K-Means — K Médias":
"E um algoritmo não supervisionado. O K-Means recebe os dados sem resposta nenhuma e os divide em K grupos. Ele sorteia K centros, junta cada ponto ao centro mais próximo, recalcula os centros e repete até estabilizar. Serve para descobrir perfis: grupos de pacientes que se parecem sem que ninguém tenha dito antes quais eram. O cuidado é que você precisa escolher o K.",

"O pipeline de Machine Learning, do início ao fim":
"Agora vamos fazer uma pausa aqui para ver a execução do notebook de Machine Learning. São oito minutos com o notebook percorrendo as seis etapas que acabamos de ver, sobre uma base clínica real: carregar e visualizar, preparar, separar os conjuntos, comparar os algoritmos, treinar e avaliar com a matriz de confusão e a curva ROC. Quando forem refazer em casa, troquem o algoritmo: é trocando que se entende o que cada um faz.",

"Inteligência Artificial na saúde":
"Agora, onde tudo isso entra na saúde. São três frentes: prognóstico, diagnóstico e tratamento.",

"Prognóstico e avaliação de risco":
"No prognóstico, a pergunta é: qual a chance de um desfecho ruim, e em quanto tempo? O instrumento clássico é o escore de risco, que resume os fatores do paciente num número comparável. Quando o tempo importa, entram as curvas de sobrevivência e o modelo de Cox, que diz quanto cada fator multiplica o risco. E a forma de avaliar muda: em vez da acurácia, usa-se o índice de concordância, que pergunta se o modelo ordena corretamente quem adoece antes.",

"Diagnóstico":
"No diagnóstico convivem três gerações. Os sistemas especialistas, com regras escritas junto com o médico, explicam cada passo mas não aprendem nada sozinhos. Os modelos que aprendem de dados clínicos, como árvores, florestas e regressão logística. E as redes convolucionais, que classificam e segmentam imagens em radiologia, patologia e dermatologia. Nessa última, uma coisa é obrigatória: o mapa que mostra em que região da imagem a rede se apoiou. Sem ele, o laudo não se defende.",

"Tratamento":
"No tratamento, os modelos estimam a resposta esperada a cada opção terapêutica, ou ajustam uma dose a partir do peso, da função renal e da resposta anterior. É também aqui que entram os modelos de linguagem, respondendo perguntas médicas, e aí citar a evidência deixa de ser opcional. E o limite vale para as três frentes: o modelo apoia a decisão, mas a responsabilidade clínica não se transfere para ele.",

"Classificação e apoio à decisão em saúde":
"Vamos fazer uma pausa aqui para o segundo notebook, de apoio à decisão em saúde. Vocês vão ver um escore de risco sendo construído e avaliado do jeito certo: a base e o desfecho, por que a acurácia mente nesse cenário, a regressão logística com os coeficientes virando razão de chances, a árvore produzindo uma regra legível, e a curva de sobrevivência. E ele termina no ponto que mais importa: o que o modelo não pode decidir sozinho.",

"Deep Learning e Transfer Learning":
"Agora vamos abrir a caixa das redes neurais: do neurônio isolado às redes profundas, e como aproveitar uma rede que alguém já treinou.",

"O neurônio artificial":
"Esta figura é o neurônio artificial, na forma proposta por McCulloch e Pitts. À esquerda chegam as entradas, x um, x dois até x n. Cada uma passa por uma seta que tem um peso, w. O neurônio, esse círculo no meio, soma as entradas multiplicadas pelos pesos e passa o resultado pela função f, a função de ativação, que decide a saída y, à direita. Aprender, para esse neurônio, é só ajustar os pesos. E o limite dele está no cartão de baixo: sozinho, ele só separa o que uma linha reta separa.",

"A rede de múltiplas camadas":
"A solução é empilhar neurônios. Na figura, à esquerda, a camada de entrada, um nó para cada variável. No meio, as camadas intermediárias, também chamadas de ocultas. À direita, a camada de saída, um nó para cada classe. Cada linha cinza é uma conexão com o seu próprio peso, e o sinal flui da esquerda para a direita. As camadas do meio combinam as entradas em conceitos cada vez mais elaborados, e é isso que permite traçar fronteiras de qualquer formato.",

"Como a rede aprende: retropropagação":
"E como uma rede com milhares de pesos aprende? Em duas passadas. Na ida, cada camada calcula a sua saída e passa adiante, até a rede dar uma resposta, que é comparada com a esperada. Na volta, o erro é distribuído de trás para frente, camada por camada, e cada peso é corrigido na direção que reduz o erro. É o gradiente descendente aplicado em cadeia. O que não tem fórmula é quantos neurônios e quantas camadas usar: isso ainda é experimentação.",

"Redes convolucionais: o caminho da imagem":
"Para imagem, ligar cada pixel a cada neurônio é inviável. A rede convolucional faz diferente, e a figura mostra o caminho da esquerda para a direita. A imagem entra. As primeiras convoluções são filtros pequenos que varrem a imagem inteira e acham bordas e orientações; são esses quadradinhos listrados. As camadas seguintes combinam bordas em partes: um olho, um nariz. As camadas posteriores combinam as partes em objetos inteiros, rostos. E no fim sai o resultado, com a sua probabilidade.",

"Transfer Learning: reaproveitar uma rede treinada":
"E aqui está uma das ideias mais úteis na prática. Treinar uma rede do zero pede milhões de imagens. Mas, à esquerda da figura, está uma rede que alguém já treinou com milhões de imagens gerais. Os blocos de baixo aprenderam bordas, texturas, formas; isso vale para qualquer imagem. Só o classificador do topo é específico, e ele é descartado. À direita, a nova rede: os mesmos blocos, agora congelados, porque os pesos não mudam, e em cima deles camadas novas, as únicas treinadas com os seus dados. Com isso, algumas centenas de imagens bastam.",

"Treinamento e Transfer Learning":
"Vamos fazer uma pausa aqui para o terceiro notebook, de treinamento e Transfer Learning. Ele põe as duas coisas lado a lado: a mesma tarefa treinada do zero e por reaproveitamento. Vocês vão ver a curva que não sobe quando se treina do zero com poucos dados, e a mesma curva subindo depois de carregar a rede pré-treinada. E, no fim, o mapa mostrando em que região da imagem a rede se apoiou.",

"Modelos de linguagem e Transformer":
"Agora, os modelos de linguagem: o que eles são, a arquitetura que os sustenta, e o que a escala trouxe e não trouxe.",

"O que é um modelo de linguagem":
"Um modelo de linguagem faz uma coisa só: estima qual é o próximo pedaço de texto, dado todo o texto anterior. Esse pedaço se chama token, e não é bem uma palavra: hemocultura, por exemplo, vira três ou quatro tokens. O treino consiste em prever o próximo token sobre um volume imenso de texto, e o próprio texto é a resposta. Por isso ele não consulta uma base de fatos; ele produz a continuação mais provável. E é por isso que ele consegue inventar com total fluência.",

"O Transformer":
"Esta é a arquitetura que está por trás de todos eles, o Transformer. À esquerda, o codificador: a frase de entrada vira vetores, recebe a informação de posição e passa por um bloco de atenção e por uma rede feed-forward, com soma e normalização entre eles; esse bloco se repete N vezes. No centro, o decodificador, que gera a saída um token por vez. Ele tem uma atenção mascarada, que só olha para o que já foi gerado, e uma atenção cruzada, que consulta o que o codificador produziu; é a seta azul. No topo, a saída vira a probabilidade do próximo token. À direita está o coração disso tudo, a matriz de atenção: cada linha é um token perguntando, cada coluna é um token consultado, e a cor forte mostra para onde ele olhou. Febre olha para paciente. Os modelos de conversa de hoje usam só o decodificador.",

"De onde veio o Transformer":
"Essa arquitetura vem de um artigo de dois mil e dezessete com um título provocativo, A atenção é tudo de que você precisa. Antes dele, as redes recorrentes liam a frase palavra por palavra, em sequência: esqueciam o começo de frases longas e quase não podiam ser treinadas em paralelo. A atenção deixou cada token se relacionar diretamente com todos os outros. E, com o treino em paralelo, escalar deixou de ser impossível.",

"Anatomia: consulta, chave e valor":
"Por dentro da matriz de atenção há três papéis. Cada token faz uma pergunta, a consulta. Cada token anuncia o que tem, a chave. Quando a pergunta de um combina com a chave de outro, ele copia a informação, o valor. E isso acontece em várias cabeças ao mesmo tempo, cada uma olhando um aspecto diferente da frase. Para a engenharia, o ponto que importa é que essa conta cresce com o quadrado do tamanho da entrada. Daí vem o custo por token, o tamanho da janela e toda a economia de contexto.",

"Escala, e o que veio com ela":
"Quando esses modelos cresceram, apareceram capacidades que ninguém programou: seguir instrução, traduzir, resumir, escrever código. Para crescer sem explodir o custo, surgiu a Mistura de Especialistas, em inglês Mixture of Experts: um roteador ativa só alguns especialistas para cada token, e um modelo com trilhões de parâmetros usa dezenas de bilhões de cada vez. Mas a escala não resolveu a invenção confiante nem trouxe garantia de correção. E a conclusão de projeto é a linha que atravessa a palestra: se o modelo não garante, a garantia tem de vir de fora dele.",

"Inferência: os parâmetros que importam":
"Na hora de usar, poucos parâmetros fazem quase toda a diferença. A temperatura regula o sorteio do próximo token: zero deixa a resposta praticamente fixa; alta abre o leque. O cache reaproveita contas já feitas e derruba custo e espera. A quantização reduz a precisão dos pesos para o modelo caber na placa de vídeo que você tem. A regra prática: extração de dados e código pedem temperatura baixa; explorar hipóteses pede o contrário.",

"Panorama: modelos proprietários":
"Um panorama rápido dos modelos proprietários, medido num teste de correção de defeitos reais de software. Os três de ponta estão num patamar parecido. Mas reparem na coluna da fonte: o número do fabricante e o de uma medição independente divergem, às vezes muito. Citem sempre a fonte e a data.",

"Panorama: modelos abertos":
"E os modelos abertos, que interessam a vocês por um motivo específico: dado de paciente que não pode sair do hospital pede um modelo rodando dentro do hospital. Destaco o Qwen de vinte e sete bilhões: roda numa placa de vinte e quatro gigabytes, algo que a informática de um hospital consegue comprar. E atenção: pesos abertos não é código aberto.",

"A escada da adaptação":
"Quando o modelo não faz o que você quer, existe uma escada, e quase todo mundo começa pelo degrau errado. Primeiro, a instrução: pedir melhor e dar exemplos. Segundo, o contexto: trazer o protocolo e a norma para dentro do pedido. Terceiro, ferramentas: deixar o modelo consultar o sistema real em vez de lembrar. Só no quarto degrau vem o ajuste fino, que muda os pesos. Subam um degrau só quando o anterior comprovadamente não bastar.",

"Criação da estrutura de um Transformer":
"Agora vamos fazer uma pausa aqui para ver a execução do notebook de criação da estrutura de um Transformer. Em oito minutos, ele monta, peça por peça, a arquitetura que vimos na figura: a tokenização transformando o texto em números, os embeddings com a posição, o bloco de atenção com consulta, chave, valor e a matriz de atenção, a rede feed-forward e os blocos empilhados, a camada de saída com a distribuição do próximo token. No fim, a estrutura pronta gera texto, um token de cada vez.",

"Agentes":
"Até aqui o modelo responde. A partir de agora, ele age.",

"De modelo para agente":
"Um modelo recebe texto e devolve texto. Não consulta nada, não altera nada e não lembra de nada entre uma chamada e outra. Um agente recebe um objetivo, escolhe ações, executa essas ações por meio de ferramentas, olha o resultado e decide o passo seguinte. A peça nova é o laço. E, com ele, vem a capacidade de causar efeito no mundo, inclusive efeito indesejado.",

"Definição operacional, sem misticismo":
"Sem misticismo, um agente tem cinco partes. Um objetivo escrito de forma verificável, senão não há como saber se terminou. Um contexto, que é tudo o que ele sabe naquela execução. Ferramentas, cada uma com nome, parâmetros e contrato de retorno. Memória, que é o que atravessa execuções. E um critério de parada: sucesso, limite de passos ou falha declarada.",

"O laço agêntico":
"O laço tem quatro tempos. O modelo pensa: olha o objetivo e o estado e decide a próxima ação. Ele pede a ferramenta; repare que ele não executa nada, só emite um pedido com o nome e os argumentos. Quem executa é o programa, e é aí que entram permissão, limite e registro. O resultado volta para o contexto, e o laço recomeça até o critério de parada.",

"Uso de ferramenta, sem framework nenhum":
"E aqui está esse laço inteiro, em Python, sem framework nenhum. Declaro a ferramenta, chamo o modelo, e olho o que voltou. Se ele não pediu ferramenta, acabou. Se pediu, o meu código executa a função e devolve o resultado para a conversa. Repete. São vinte linhas, e é isso que todo framework faz por baixo.",

"Os padrões de composição":
"Quando há mais de um passo, existem padrões para organizar o trabalho, e a figura mostra os três mais usados. À esquerda, o encadeamento: a saída de um passo é a entrada do seguinte, simples e previsível. No meio, o roteamento: o losango classifica o pedido e manda para o especialista certo, o B, em verde. À direita, o paralelismo: a tarefa se divide em partes independentes que rodam ao mesmo tempo e são juntadas, ou votadas, no fim. Embaixo, mais três: um orquestrador que distribui trabalho, um par que produz e critica, e a autonomia com portão, em que o agente decide o caminho mas o código confere cada etapa. A regra: comecem pelo mais simples que resolve.",

"Multiagente: quando compensa, e quando não":
"Vários agentes compensam quando as subtarefas são de fato independentes e os contextos podem ficar separados. Em fluxo linear não compensam: gastam de quatro a quinze vezes mais tokens para fazer o que um condicional resolveria. E cada repasse entre agentes perde informação, como fotocópia de fotocópia.",

"Por que agentes falham em produção":
"E a aritmética que todo mundo esquece: noventa e cinco por cento de acerto por passo, vinte passos em sequência, dão trinta e seis por cento de sucesso no fim. O erro se compõe. Os modos de falha são conhecidos: laço infinito, ferramenta inventada, contexto contaminado. E o pior de todos é o silencioso: o agente diz que conseguiu e não fez nada. A saída não é um pedido mais caprichado; é reduzir o número de passos que ninguém verifica.",

"Um sistema multiagente com resultado verificável":
"Vamos fazer uma pausa aqui para o notebook de agentes. Vocês vão ver o objetivo e as ferramentas declaradas, o agente pedindo e o programa executando, o resultado real voltando para o contexto. Depois, dois agentes com contextos isolados e a junção do trabalho deles. E, no fim, uma falha injetada de propósito, para ver o portão em código barrando a falha antes que ela siga adiante.",

"Contexto e recuperação de documentos":
"Um agente só é tão bom quanto aquilo que ele sabe na hora de decidir. Esse é o assunto do bloco: contexto e recuperação de documentos.",

"De “prompt” para engenharia de contexto":
"Falou-se muito em escrever o prompt certo. Hoje o termo mais preciso é engenharia de contexto. Contexto é tudo o que entra na janela do modelo: a instrução, o histórico, os documentos trazidos, a descrição das ferramentas e o estado. Cada token disputa espaço com os outros, e encher a janela piora: o modelo passa a ignorar o meio do texto. A prática é trazer o trecho certo, não o documento inteiro.",

"Recuperação Aumentada por Geração (RAG — Retrieval-Augmented Generation)":
"A técnica principal para isso é a Recuperação Aumentada por Geração, conhecida pela sigla em inglês, RAG, de Retrieval-Augmented Generation. O problema que ela resolve: o modelo não conhece o seu protocolo nem o prontuário do seu paciente. Então os documentos são fatiados, e cada pedaço vira um vetor, uma espécie de endereço num espaço de significado. A pergunta também vira vetor, e buscamos os pedaços mais próximos dela. Esses trechos entram no pedido, e a resposta diz de onde saiu.",

"Tipos e técnicas de RAG":
"E RAG não é uma receita única; é uma família de técnicas, e a figura mostra onde cada uma entra. Na linha de cima está a preparação, feita uma vez e a cada documento novo: fatiar, transformar em embeddings, guardar num índice vetorial e anotar metadados como fonte, data e versão. O índice pode ser o FAISS, uma biblioteca para busca eficiente de similaridade entre vetores, ou bancos como Qdrant, pgvector, Chroma e Milvus. Na linha de baixo, a consulta, a cada pergunta: busca semântica, ou híbrida, que mistura sentido com palavra-chave; filtros por metadados, para ficar só na versão vigente; e o reranking, que reordena os trechos pelos mais relevantes antes de montar o contexto. Cada peça se escolhe pelo problema.",

"RAG na prática":
"E em código fica assim, e dá para ler cada bloco como uma seta da figura anterior. Um: carrego os documentos e fatio. Dois: gero os embeddings e crio o índice com o FAISS. Três: busco os quatro trechos mais parecidos com a pergunta. Quatro, cinco e seis: junto os trechos num contexto, entrego ao modelo com a instrução de responder só com aquilo, e recebo a resposta. Trocar o FAISS por outro banco muda uma linha.",

"Onde o RAG quebra: o fatiamento":
"Onde o RAG quebra, na prática? No fatiamento. Um caso real: um critério de definição de infecção hospitalar ocupa três parágrafos, e os três precisam ser lidos juntos. Fatiado por tamanho fixo, o critério laboratorial fica num pedaço e a janela de tempo em outro. A busca traz metade da regra, o modelo completa o resto com fluência, e o sistema dispara um falso positivo. A correção é fatiar pela unidade lógica: a regra inteira num pedaço só.",

"Saída estruturada e proteções":
"Duas proteções fecham o bloco. A primeira é a saída estruturada: exigir do modelo um esquema, com campos que o seu código valida, em vez de texto livre, porque interpretar texto livre é por onde o defeito entra. A segunda é o conjunto de proteções: um conjunto de casos com resposta esperada rodado a cada mudança, limite de passos e de custo, lista de ferramentas permitidas e confirmação humana em tudo o que for irreversível.",

"Frameworks de agentes":
"Existem vários frameworks para construir agentes. Vamos ver como escolher, e depois um exemplo concreto de cada um.",

"O critério de leitura":
"Diante de qualquer framework, novo ou antigo, eu faço quatro perguntas. Quem controla o laço, eu ou ele? Isso decide quanto consigo depurar. Onde mora o estado, e ele sobrevive a uma queda? Como o humano entra no fluxo, há ponto de parada para aprovação? E o que se vê de dentro: há registro de cada passo e custo por passo?",

"Comparativo, e a opinião contrária":
"Aplicando as perguntas, a tabela mostra o perfil de cada um: os SDKs da OpenAI e da Anthropic, o LangGraph com a sua máquina de estados, o CrewAI com papéis, o AutoGen com conversa, e o laço próprio. E a opinião contrária, que eu faço questão de registrar: na maioria dos casos o laço escrito à mão é mais simples de depurar. Framework se justifica por durabilidade, observabilidade e entrada do humano, não por elegância. Vamos ver como cada um se parece na prática.",

"CrewAI: papéis, tarefas e equipe":
"O CrewAI pensa como uma equipe. No primeiro arquivo, agents.yaml, declaro os agentes: cada um tem um papel, um objetivo e uma história que orienta o comportamento, aqui um triador e um redator de alertas. No segundo, tasks.yaml, as tarefas: o que fazer, o que se espera de saída e qual agente é responsável. E no terceiro, um trecho de Python junta tudo numa equipe, a crew, executando as tarefas em sequência.",

"LangGraph: estado, nós e arestas":
"O LangGraph pensa como um grafo, e o desenho à direita é exatamente o código da esquerda. Primeiro declaro o estado, que é o que viaja de nó em nó: o caso e o risco. Os nós são funções: classificar, alertar e registrar. As arestas são as transições: do início vai para classificar. Depois vem a aresta condicional, o losango: se o risco é alto, vai para alertar; se é baixo, para registrar. Os dois terminam no fim. Compilo e executo com o caso de entrada.",

"AutoGen: agentes que conversam":
"O AutoGen pensa como uma conversa. Crio dois agentes, cada um com a sua instrução: um redator, que escreve o resumo do caso, e um revisor, que critica e, quando estiver satisfeito, responde a palavra TERMINATE. A figura mostra a troca: o redator manda o rascunho, o revisor aponta que falta citar a fonte, o redator manda a nova versão, e o revisor aprova e encerra. A colaboração é o diálogo, com um limite de turnos para não rodar para sempre.",

"Outros: OpenAI Agents SDK e Claude Agent SDK":
"E os SDKs dos fabricantes seguem o mesmo princípio, com menos cerimônia. No da OpenAI, à esquerda, uma função Python vira ferramenta com um decorador, o agente recebe nome, instrução e ferramentas, e o Runner executa o laço até a resposta final. No da Anthropic, à direita, passo as opções, a instrução, as ferramentas permitidas e até um servidor MCP, e recebo as mensagens à medida que o agente trabalha. Muda a sintaxe; a ideia é a mesma do laço de vinte linhas que vimos antes.",

"Ambientes de geração de código":
"Agora, os agentes que escrevem código: onde o trabalho de programação de fato acontece hoje.",

"Mudou a unidade de trabalho":
"A unidade de trabalho mudou. Antes, você escrevia as linhas, e o editor completava palavras. Agora, você descreve a tarefa e revisa a diferença: o agente lê o repositório, propõe a mudança e roda os testes. A habilidade que ficou mais importante é saber dizer o que se quer e ler criticamente o que voltou. E o maior perigo é aceitar sem ler, porque uma diferença grande e bem formatada passa fácil por uma revisão apressada.",

"Claude Code: sessão de engenharia no terminal":
"O Claude Code transforma o terminal numa sessão com contexto sobre o repositório inteiro. À esquerda, os comandos do dia a dia: abrir, continuar, retomar uma sessão, e o modo não interativo, que roda um pedido e sai. À direita, os recursos que fazem diferença. Skills, que são capacidades e fluxos reutilizáveis. Subagents, agentes especializados para tarefas delegadas. Agent Teams, várias sessões trabalhando coordenadas. O MCP, o Model Context Protocol, que conecta ferramentas, bancos e APIs. A troca de mensagens entre sessões independentes. E o modo não interativo, que coloca o agente dentro de um script ou de um pipeline.",

"Codex: execução, revisão e saída verificável":
"O Codex, da OpenAI, tem a mesma organização, e dá para comparar quadro a quadro. O arquivo AGENTS.md guarda as convenções do repositório como contexto que se reaproveita. Também há skills. Também há MCP para ferramentas externas. O modo exec faz o papel do não interativo. E há dois destaques próprios: a saída verificável, em que os eventos saem em JSON e a resposta fica presa a um esquema que o seu programa confere, e a caixa de areia com aprovações, que define o que o agente pode fazer sem pedir licença.",

"Cursor e o panorama dos editores":
"E há os editores, como o Cursor, com o agente embutido na própria tela: contexto do projeto, edição em vários arquivos e revisão visual da diferença. O terminal favorece automação e repetição; o editor favorece exploração e revisão. Em qualquer um deles, quem aprova a mudança é uma pessoa.",

"Protocolos e contratos":
"Quando agentes, ferramentas e pessoas precisam se entender, entram os protocolos.",

"O mapa: vertical e horizontal":
"Este é o mapa, e ele tem dois eixos. No centro, o agente. No eixo vertical, para cima, o MCP, o Model Context Protocol: ele liga o agente às ferramentas, aos bancos e às APIs, cada ferramenta publicada com nome, parâmetros e formato de retorno. No eixo horizontal, à esquerda, o A2A, que liga um agente a outro agente para descobrir capacidades e delegar tarefas. E, à direita, no mesmo eixo, o OKF, o Open Knowledge Format: um formato aberto para trocar conhecimento, que agentes consomem e que pessoas também leem, como mostra o bonequinho ao lado. O MCP responde o que eu posso fazer; o A2A, com quem eu posso contar; o OKF, o que nós sabemos.",

"Conhecimento em formato aberto":
"E vale olhar o OKF mais de perto, porque ele é surpreendentemente simples. Um pacote de conhecimento é um diretório de arquivos de texto em markdown, sem banco e sem servidor. Cada arquivo é um conceito, e os arquivos se citam por links comuns, o que transforma o diretório numa rede. Para um hospital, o uso é direto: as definições de caso, as fórmulas dos indicadores e os procedimentos da comissão, legíveis por agente, revisáveis por um infectologista, com histórico e autoria de cada linha.",

"Specification-Driven Development (SDD)":
"Chegamos ao método. Specification-Driven Development, em português Desenvolvimento Orientado a Especificação. Daqui para frente vou chamá-lo pela sigla, SDD.",

"O problema: Vibe Coding":
"Primeiro, o problema, que já tem nome: Vibe Coding. Na figura, à esquerda, é o jeito de programar conversando direto com a IA: faço um pedido, a IA gera, olho o código e, se não ficou bom, peço de novo. Não há especificação, não há rastro, não há validação, não há processo. Funciona no protótipo e colapsa quando o sistema cresce, porque ninguém mais sabe qual requisito cada trecho atende. À direita, o SDD: requisitos, especificação, artefatos, desenvolvimento e validação, e cada artefato apontando de volta para a sua origem. A IA acelera cada etapa, e cada etapa é conferida. A mensagem está embaixo: o SDD permite usar a velocidade da IA sem transformar o desenvolvimento num Vibe Coding desorganizado.",

"A inversão":
"O SDD faz uma inversão. No jeito tradicional, o requisito é informal, vira código, e a documentação já nasce desatualizada. No SDD, a especificação é o artefato principal: dela sai o plano, do plano saem as tarefas, e das tarefas, o código. O que se versiona e se discute é a especificação. O código se regenera, do mesmo jeito que ninguém revisa o binário que o compilador produz.",

"Anatomia de uma especificação útil":
"Mas não é qualquer texto que serve. Uma especificação útil diz o contexto, o escopo e, com a mesma importância, o que fica de fora. E cada requisito precisa admitir um teste que diga passou ou não passou. Compare os dois exemplos. Bom: quando uma hemocultura positiva for registrada, o sistema deve avaliar os critérios de infecção em até quarenta e oito horas e produzir um parecer com a evidência citada. Ruim: o sistema deve detectar infecções corretamente. O segundo não se testa; então não é requisito, é uma intenção.",

"Da especificação ao código, e a rastreabilidade":
"E é isso que torna possível a rastreabilidade, que a figura mostra da esquerda para a direita. O requisito diz o que o sistema deve fazer. O caso de uso diz como o usuário realiza aquilo. O modelo de dados e a tela dizem onde o dado mora e onde aparece. A tarefa diz quem executa e com que regra. O caso de teste diz como conferir o comportamento. E o código implementa. As setas pretas são a derivação: cada artefato nasce do anterior. As setas tracejadas são o rastro: cada um guarda a referência de onde veio. Por isso, quando um requisito muda, o rastro mostra tudo o que precisa ser refeito. E o teste nasce do critério, não do código, e por isso não herda os defeitos dele.",

"Onde o SDD encontra os agentes":
"É aqui que o SDD e os agentes se encontram. Em vez de um agente fazendo tudo, cada etapa tem o seu: especificador, arquiteto, implementador, verificador, com um portão entre eles. Cada um recebe só o contexto de que precisa. E quem verifica no portão é um programa, não outro modelo. Lembram dos trinta e seis por cento? Com portão, o erro não se propaga; ele para na etapa, com o motivo.",

"O artefato regulatório sai de graça":
"E há um ganho que costuma decidir a conversa com a diretoria. Software de saúde precisa de rastreabilidade do requisito ao teste e ao código, com gestão de risco e ciclo de vida controlado. Quem trabalha com SDD já tem essa matriz como subproduto do método, versionada e com autoria. E isso vira a objeção comum de ponta-cabeça: dizem que código gerado por IA não é auditável; com o método, ele é. O que não é auditável é código escrito à mão, sem especificação.",

"Antipadrões: como o método morre na prática":
"Como o método morre na prática? Especificação escrita depois, só para justificar o que já foi feito. Requisito que não se testa, e o agente preenche a lacuna com o critério dele. Portão feito por outro modelo: duas incertezas empilhadas não fazem uma certeza. E o mais comum: corrigir à mão o código gerado. Na geração seguinte a correção some, e ninguém lembra por quê. O remédio é sempre o mesmo: a correção entra na especificação, e o artefato é regenerado.",

"LangNet: um framework para SDD automatizado":
"E agora o que nós construímos com isso: o LangNet, um framework para SDD automatizado.",

"Dois lados: a fábrica e a máquina":
"A frase em destaque resume: o LangNet é uma aplicação que fabrica aplicações dentro do padrão SDD. Na figura, à esquerda, a fábrica: as etapas do processo, dos documentos à especificação, aos dados e à interface, aos agentes e tarefas, à rede de Petri, aos testes e ao código. Cada etapa tem origem, geração, revisão e aprovação, com versão. A seta laranja entrega o produto, à direita: a aplicação gerada, com telas, banco, agentes, ferramentas e o executor da rede. O que liga os dois lados é a rede de Petri. E um defeito da aplicação se corrige na fábrica e se regenera, nunca no produto final.",

"As etapas, e o que se repete em todas elas":
"A trilha no alto mostra todas as etapas acesas, e o que importa é que todas seguem o mesmo ritual: escolher de qual origem e de qual versão partir, gerar, refinar conversando com o agente da etapa e aprovar. Aprovar não apaga o anterior; tudo é versionado, e cada etapa sabe de que versão da anterior nasceu. Entre as etapas há um portão, um programa que confere a passagem e, se reprova, diz por quê. E refinar é conversar: a correção é dita em português.",

"Do documento aos requisitos":
"A primeira etapa lê os documentos de entrada, e a figura mostra os dois caminhos que ela percorre. Em cima, a extração: o que está escrito no documento. Embaixo, a inferência: o que o sistema precisa e ninguém escreveu, como um controle de acesso ou um registro de auditoria. A pesquisa na web complementa a inferência com práticas e normas do domínio. Os dois caminhos alimentam três tipos de requisito: os funcionais, o que o sistema faz; os não funcionais, como desempenho, segurança e disponibilidade; e as regras de negócio, as políticas e critérios do domínio. O resultado é o documento de requisitos, em que cada item diz de onde veio.",

"A especificação funcional":
"A partir dos requisitos nasce a especificação funcional, organizada em casos de uso: o ator, as pré-condições, o fluxo principal passo a passo e os fluxos de exceção, que dizem o que acontece quando algo dá errado. Cada caso de uso traz o esboço da tela. Nos casos em que um agente decide, a especificação declara o que ele decide e com base em quê. E o portão confere que o esboço e o fluxo falam dos mesmos campos e dos mesmos botões.",

"O modelo de dados, e a correção por conversa":
"Da especificação sai o modelo de dados: tabelas, campos, tipos e relações. E aqui aparece uma característica de que eu gosto muito: a etapa aponta os próprios defeitos, como uma coluna obrigatória sem valor padrão ou um resultado de agente sem lugar para ser gravado. A correção é dita em português, algo como a urgência precisa ser uma coluna própria com valores fechados, e o agente reescreve o modelo. A versão nova fica ao lado da anterior para comparar.",

"A interface e o protótipo":
"As telas nascem do esboço e do fluxo de cada caso de uso, não de um molde genérico de formulário. E têm componentes de verdade: indicadores, gráficos, tabelas, listas. O protótipo roda antes de existir sistema: é o mesmo código das telas, com dados de exemplo no lugar do banco. Serve para discutir com o usuário enquanto mudar ainda é barato.",

"Ferramentas, agentes e tarefas":
"Na etapa de ferramentas, decide-se quem implementa cada uma: código comum, tarefa de agente ou um serviço externo, publicado por um servidor MCP com contrato de entrada e saída. Em seguida vêm os agentes e as tarefas, e cada tarefa carrega o caso de uso e o requisito que a originaram; é a matriz de rastreabilidade se formando sozinha. E cada tarefa declara se é determinística ou de agente, que é o que o executor usa para decidir como rodá-la.",

"A rede de Petri: a orquestração verificável":
"E aqui a rede de Petri, que é a peça que orquestra tudo. Leiam a figura da esquerda para a direita. Os círculos são lugares, que guardam estado; as barras pretas são transições, que são as tarefas. Cada caixa colorida é um agente, com as suas tarefas dentro. O ponto vermelho é o token, que marca onde a execução está agora: o caso acabou de chegar. Quando a transição iniciar dispara, o token se divide em dois ramos paralelos, um para o agente de tradução e outro para o de classificação. A barra do meio é um ponto de sincronização: ela só dispara quando os dois ramos terminaram. Aí o token segue para o agente de alerta. E, diferente de um fluxograma, a rede admite prova de que não trava.",

"Casos de teste e geração do código":
"Os casos de teste saem dos casos de uso por uma técnica clássica, o grafo de causa e efeito, que está à esquerda. As causas são o que chega: há antibiograma, a lista de antimicrobianos existe, o agente interpretou sem falha, há três ou mais classes resistentes. Quando todas são verdadeiras, o nó E leva ao efeito multirresistente igual a sim. Se a última é falsa, o nó não leva ao efeito multirresistente igual a não. Cada combinação vira um caso de teste, e à direita está um deles, exatamente como foi gerado: dado que essas causas valem, então esse efeito deve acontecer. O teste confere comportamento, não tela. Depois vem a geração da aplicação, e o portão confere se cada tarefa chegou ao código.",

"A aplicação rodando, e a bancada de execução":
"E a última etapa é a aplicação rodando: cadastros, relatórios, as telas dos agentes e o executor disparando a rede. Junto com ela vem a bancada, que mostra cada tarefa em execução: a entrada que recebeu, o que o agente pensou, que ferramenta chamou e o que devolveu. E uma regra que custou caro aprender: erro de ferramenta ou de agente aparece como falha declarada. Sucesso relatado sem trabalho feito é o defeito mais perigoso que existe.",

"O exemplo: BioByte":
"Para mostrar tudo isso funcionando, vamos usar um exemplo: o BioByte, um sistema de vigilância de infecção hospitalar. O contexto é a comissão de controle de infecção, que acompanha pacientes com cateter e resultados de hemocultura, muitas vezes à mão. A especificação tem casos de uso para cadastrar o caso, importar o antibiograma, classificar pelo critério da norma, identificar multirresistência e alertar a equipe. Os cadastros e relatórios são convencionais; as decisões clínicas são feitas por agentes, sempre com a justificativa gravada. A microbiologia e o escore de risco vêm de serviços externos. E o que vamos ver é o LangNet percorrendo as etapas com esse documento, até a aplicação rodando.",

"O pipeline completo do LangNet, do documento à aplicação":
"Então vamos fazer uma pausa aqui para a demonstração final, vinte minutos com o LangNet executando o pipeline completo sobre o BioByte. Vocês vão ver o documento entrando e os requisitos nascendo com a sua procedência; a especificação com os fluxos de exceção e o esboço da tela; o modelo de dados apontando o próprio defeito e sendo corrigido por conversa; as telas e o protótipo; as ferramentas, os agentes e as tarefas; a rede de Petri e a geração do código; e, no fim, a aplicação rodando, com a bancada mostrando cada entrada e cada saída. Reparem: nenhuma correção é feita à mão no produto final.",

"Fechamento":
"Para fechar.",

"As três conclusões":
"Três conclusões. A primeira: o modelo não garante correção. Quem garante é o que você põe em volta dele: portão em código, saída estruturada, evidência citada. A segunda: a especificação virou o artefato principal. O código é derivado, e o que é derivado se regenera, não se remenda. A terceira: rastreabilidade deixou de ser custo e virou subproduto. Quem trabalha assim já tem na mão o que a auditoria vai pedir.",

FIM:
"E volto à frase do começo: o gargalo deixou de ser escrever código; passou a ser especificar com precisão o que se quer. Muito obrigado pela atenção. Fico à disposição para as perguntas.",
}


def aplicar(slides):
    faltam = []
    for s in slides:
        chave = s.get("titulo", FIM)
        if chave in FALAS:
            s["fala"] = FALAS[chave]
        else:
            faltam.append(chave)
    if faltam:
        raise SystemExit("sem fala na V11: %s" % faltam)
    return slides
