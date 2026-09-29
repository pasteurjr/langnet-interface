# -*- coding: utf-8 -*-
"""V10 · parte A — abertura, Machine Learning, IA na saúde, Deep Learning.

Fonte do conteúdo dos algoritmos e do processo de ML:
`docs/apresentacao/deck/algoritmos inteligentes3.pptx` (lâminas 17-67, 151-154).
O texto de `fala` é o que a narradora diz, literalmente.
"""

TRILHA_ML = ["Visualizar", "Preparar", "Conjuntos", "Modelo", "Treinar", "Avaliar"]

SLIDES = [

    dict(tipo="capa",
         titulo="Engenharia de IA e Desenvolvimento Orientado a Especificação",
         subtitulo="De um classificador em vinte linhas a uma fábrica de software conduzida por agentes",
         rodape="Pasteur Ottoni de Miranda Junior · doze blocos · seis demonstrações em vídeo"),

    dict(tipo="cartoes", bloco=0, chapeu="Abertura", titulo="O caminho de hoje",
         destaque="Três pilares, doze blocos, e um notebook para praticar depois de cada um.",
         cartoes=[
             ("Fundamento", "aprendizado de máquina, aplicação em saúde, aprendizado profundo, modelos de linguagem."),
             ("Engenharia", "agentes, contexto e recuperação, frameworks, ambientes de geração de código, protocolos."),
             ("Método", "desenvolvimento orientado a especificação, e o LangNet — a nossa implementação dele."),
             ("Como vamos praticar", "cada bloco fecha com uma demonstração em vídeo; o notebook correspondente fica com vocês."),
         ],
         fala="Bom dia. O caminho de hoje tem três pilares. O primeiro é fundamento: aprendizado de máquina, "
              "aplicação em saúde, aprendizado profundo e modelos de linguagem. O segundo é engenharia: agentes, "
              "contexto, frameworks, ambientes de geração de código e protocolos. O terceiro é método: "
              "desenvolvimento orientado a especificação, e o LangNet, que é a nossa implementação desse método. "
              "São doze blocos. Cada um fecha com uma demonstração em vídeo, e o notebook correspondente fica com "
              "vocês para praticar depois da aula. Nas lâminas eu vou passar rápido; a profundidade está no notebook."),

    dict(tipo="citacao", bloco=0, chapeu="Abertura", titulo="A tese",
         frase="O gargalo deixou de ser escrever código. Passou a ser especificar com precisão o que se quer.",
         cartoes=[
             ("O que mudou", "quando o código sai em minutos, a digitação para de ser o custo dominante do projeto."),
             ("O que não mudou", "um sistema continua valendo o que vale a definição do problema que ele resolve."),
         ],
         fala="A tese da palestra é esta: o gargalo do desenvolvimento deixou de ser escrever código; passou a ser "
              "especificar com precisão o que se quer. Quando um agente escreve o código em minutos, o que separa um "
              "sistema que funciona de um que não funciona já não é a digitação — é a qualidade da especificação que "
              "você entregou a ele. Guardem essa frase, porque tudo o que vem depois é consequência dela."),

    # ───────────────────────── BLOCO 1 ─────────────────────────
    dict(tipo="divisor", bloco=1, titulo="Introdução e Machine Learning",
         mensagem="O que é aprendizado de máquina, como se monta um projeto do início ao fim, e um algoritmo por lâmina.",
         fala="Começamos pelo começo: o que é aprendizado de máquina, como se monta um projeto de aprendizado do "
              "início ao fim, e quais são os algoritmos clássicos. Vou dedicar uma lâmina a cada algoritmo, dizendo "
              "em poucas palavras qual é a ideia dele e para que ele se presta melhor. A matemática não vem para a "
              "tela — ela está no notebook que vocês levam."),

    dict(tipo="cartoes", bloco=1, chapeu="Fundamentos", titulo="Onde fica a fronteira",
         destaque="O que separa um algoritmo convencional de um algoritmo inteligente.",
         cartoes=[
             ("Algoritmo convencional", "a solução é conhecida e o programador a escreve passo a passo. O menor caminho entre dois pontos tem procedimento exato."),
             ("Algoritmo inteligente", "a solução não é conhecida de antemão. No jogo da velha não há fórmula da jogada certa: o programa avalia e escolhe."),
             ("O que realmente muda", "onde mora o conhecimento. No primeiro caso ele está no código; no segundo, está nos dados — e o código apenas o extrai."),
         ],
         fala="Antes de falar de aprendizado, vale fixar a fronteira. Num algoritmo convencional a solução é "
              "conhecida, e o programador a escreve passo a passo: o menor caminho entre dois pontos tem um "
              "procedimento exato. Num algoritmo inteligente a solução não é conhecida de antemão: no jogo da velha "
              "não existe fórmula da jogada certa, o programa avalia possibilidades e escolhe. A diferença que "
              "importa é onde mora o conhecimento. No primeiro caso ele está no código. No segundo, ele está nos "
              "dados, e o código apenas o extrai."),

    dict(tipo="cartoes", bloco=1, chapeu="Fundamentos", titulo="Setenta anos em um minuto",
         cartoes=[
             ("1950 · 1958", "Turing propõe o teste da imitação. Rosenblatt constrói o Perceptron, o primeiro neurônio que aprende."),
             ("Anos 1980", "a retropropagação torna possível treinar redes de várias camadas — e o ou-exclusivo deixa de ser barreira."),
             ("2012", "redes convolucionais vencem a competição de imagens por margem larga. Começa a era do aprendizado profundo."),
             ("2017 · 2022", "sai o artigo do Transformer. Cinco anos depois o ChatGPT leva modelos de linguagem ao uso geral."),
             ("2024 em diante", "o assunto passa a ser agentes: modelos que usam ferramentas, executam tarefas e produzem artefatos."),
         ],
         fala="Um minuto de história, só para situar. Em mil novecentos e cinquenta Turing propõe o teste da "
              "imitação; oito anos depois aparece o Perceptron, o primeiro neurônio artificial que aprende. Nos anos "
              "oitenta a retropropagação torna possível treinar redes de várias camadas. Em dois mil e doze as redes "
              "convolucionais vencem a competição de imagens por margem larga, e começa a era do aprendizado "
              "profundo. Em dois mil e dezessete sai o artigo do Transformer; cinco anos depois o ChatGPT leva os "
              "modelos de linguagem ao uso geral. E de dois mil e vinte e quatro em diante o assunto passa a ser "
              "agentes: modelos que usam ferramentas e executam tarefas."),

    dict(tipo="cartoes", bloco=1, chapeu="Fundamentos", titulo="Aprendizado supervisionado e não supervisionado",
         destaque="Aprendizado de máquina é, essencialmente, extrair conhecimento a partir de dados.",
         cartoes=[
             ("Supervisionado", "você fornece entradas e as saídas esperadas. Existe um “professor” que ensina por exemplos; depois, o modelo responde a entradas novas."),
             ("Não supervisionado", "não há professor nem saída esperada. O modelo recebe só os dados e extrai deles a estrutura, agrupando o que é parecido."),
             ("A consequência prática", "o supervisionado exige dados rotulados — e rotular é o item mais caro de quase todo projeto clínico."),
         ],
         fala="Aprendizado de máquina é, essencialmente, extrair conhecimento a partir de dados: o modelo aprende a "
              "fazer alguma coisa com os dados que recebe. Há dois regimes. No supervisionado você fornece entradas "
              "e as saídas esperadas — é como se houvesse um professor ensinando por exemplos; depois de treinado, o "
              "modelo responde a uma entrada nova de forma compatível com o que aprendeu. No não supervisionado não "
              "existe professor: o modelo recebe só os dados e extrai deles a estrutura, agrupando o que é parecido. "
              "A consequência prática é financeira: o supervisionado exige dados rotulados, e rotular é o item mais "
              "caro de quase todo projeto clínico."),

    dict(tipo="etapa", bloco=1, chapeu="O processo", titulo="As seis etapas de um projeto de Machine Learning",
         trilha=TRILHA_ML, atual=[1, 2, 3, 4, 5, 6],
         cartoes=[
             ("O roteiro é sempre o mesmo", "visualizar os dados, preparar os dados, definir os conjuntos, definir o modelo, efetuar o treinamento, avaliar."),
             ("Onde vai o tempo", "as duas primeiras etapas costumam consumir a maior parte do projeto. A modelagem é a parte curta."),
             ("O que vem a seguir", "vou passar por cada etapa dizendo o que se faz nela — é esse o roteiro que o notebook da demonstração executa."),
         ],
         fala="Um projeto de aprendizado de máquina tem seis etapas, e são sempre as mesmas: visualizar os dados, "
              "preparar os dados, definir os conjuntos, definir o modelo, efetuar o treinamento e avaliar. Guardem "
              "desde já uma proporção que surpreende quem está começando: as duas primeiras etapas consomem a maior "
              "parte do tempo de um projeto real. A modelagem, que é a parte que todo mundo acha interessante, é a "
              "parte curta. Vou passar por cada etapa dizendo o que se faz nela — é exatamente esse o roteiro que o "
              "notebook da primeira demonstração executa do início ao fim."),

    dict(tipo="etapa", bloco=1, chapeu="O processo", titulo="Visualizar e preparar os dados",
         trilha=TRILHA_ML, atual=[1, 2],
         cartoes=[
             ("Visualizar", "olhar a distribuição de cada variável e a correlação entre elas, antes de qualquer modelo. É aqui que se descobre a coluna vazia na metade dos registros."),
             ("Limpar", "remover valores fora de contexto e preencher os ausentes."),
             ("Tratar os fatores", "descartar os desnecessários, decompor os que misturam informação, transformar, agregar quando fizer sentido."),
             ("Ajustar a escala", "levar tudo a uma faixa comparável. Se um fator vai de mil a um milhão e outro de zero a cem, muitos algoritmos não convergem.", "warn"),
         ],
         fala="As duas primeiras etapas. Visualizar é olhar a distribuição de cada variável e a correlação entre "
              "elas, antes de qualquer modelo — é aqui que você descobre que uma coluna está vazia na metade dos "
              "registros. Preparar é limpar: remover valores fora de contexto, preencher os ausentes, descartar os "
              "fatores desnecessários, decompor os que misturam mais de uma informação, agregar os que fizerem "
              "sentido. E ajustar a escala. Esse último ponto é prático e importante: se um fator varia de mil a um "
              "milhão e outro varia de zero a cem, muitos algoritmos simplesmente não convergem."),

    dict(tipo="etapa", bloco=1, chapeu="O processo", titulo="Definir os conjuntos e escolher o modelo",
         trilha=TRILHA_ML, atual=[3, 4],
         cartoes=[
             ("A separação", "os dados são particionados aleatoriamente: setenta a setenta e cinco por cento para treinamento, o restante para teste."),
             ("A regra inegociável", "o modelo nunca pode ver, no treino, os dados com que vai ser avaliado. Quebrar isso produz um resultado ótimo e falso.", "warn"),
             ("Escolher o modelo", "na prática não se escolhe no chute: a busca em grade testa vários algoritmos e várias combinações de parâmetros e devolve o melhor naquela base."),
         ],
         fala="A terceira etapa separa os dados. Tipicamente setenta a setenta e cinco por cento vão para "
              "treinamento e o restante para teste, sorteados aleatoriamente. E há uma regra inegociável: o modelo "
              "nunca pode ver, no treino, os dados com que vai ser avaliado. Quando isso é violado — e é violado com "
              "frequência, por descuido — o resultado sai excelente e é completamente falso. A quarta etapa escolhe "
              "o modelo. Na prática a gente não escolhe no chute: usa busca em grade, que testa vários algoritmos e "
              "várias combinações de parâmetros e devolve o que foi melhor naquela base."),

    dict(tipo="etapa", bloco=1, chapeu="O processo", titulo="Treinar e avaliar: o sobreajuste",
         trilha=TRILHA_ML, atual=[5, 6],
         cartoes=[
             ("Treinar", "apresentar os dados ao modelo repetidas vezes. Cada passagem completa é uma época."),
             ("O gráfico que conta a história", "perda e acurácia por época, medidas nos dois conjuntos. É ele que mostra a hora de parar."),
             ("Sobreajuste", "a partir de certo ponto a acurácia sobe no treino e cai no teste. O modelo decorou e perdeu a generalização.", "warn"),
             ("Subajuste", "o oposto: o modelo treinou de menos e não acerta nem no conjunto de treinamento."),
         ],
         fala="Treinar é apresentar os dados ao modelo repetidas vezes; cada passagem completa é uma época. O "
              "gráfico de perda e acurácia por época conta a história do treinamento, e é ele que mostra o problema "
              "central da área: o sobreajuste. A partir de certo ponto, a acurácia no conjunto de treino continua "
              "subindo, mas a do conjunto de teste começa a cair, e a perda começa a aumentar. O modelo decorou o "
              "treino e perdeu a capacidade de generalizar. Não adianta treinar mais — adianta parar antes. O "
              "oposto também existe: o subajuste, quando o modelo treinou de menos e não acerta nem no treino."),

    dict(tipo="cartoes", bloco=1, chapeu="O processo", titulo="Como se mede um classificador",
         destaque="Avaliar não é olhar um número só.",
         cartoes=[
             ("Matriz de confusão", "os quatro casos: acertos e erros de cada classe. Tudo o mais é derivado dela."),
             ("Sensibilidade e especificidade", "a fração de doentes que o modelo pegou, e a fração de sadios que ele deixou em paz."),
             ("Curva ROC e a área sob ela", "resumem o compromisso entre as duas ao longo de todos os limiares de decisão."),
             ("O alerta da saúde", "acurácia engana em base desbalanceada. Com prevalência de dois por cento, quem responde sempre “não” acerta noventa e oito por cento — e é inútil.", "warn"),
         ],
         fala="Avaliar não é olhar um número só. A matriz de confusão mostra os quatro casos: acertos e erros de "
              "cada classe. Dela saem a sensibilidade, que é a fração de doentes que o modelo pegou, e a "
              "especificidade, que é a fração de sadios que ele deixou em paz. A curva ROC, e a área sob ela, "
              "resumem o compromisso entre as duas ao longo de todos os limiares de decisão. E fica o alerta que "
              "vale para a saúde inteira: acurácia engana em base desbalanceada. Se a doença tem prevalência de dois "
              "por cento, um modelo que responde sempre “não” acerta noventa e oito por cento das vezes — e é "
              "completamente inútil."),

    dict(tipo="cartoes", bloco=1, chapeu="O processo", titulo="Com o que se trabalha",
         cartoes=[
             ("Linguagem e ambiente", "Python. Jupyter Notebook no navegador, ou Google Colab, que é o Jupyter hospedado e não exige instalar nada."),
             ("Aprendizado clássico", "scikit-learn — todos os algoritmos dos próximos slides estão nela."),
             ("Aprendizado profundo", "TensorFlow e PyTorch. Placas gráficas aceleram a álgebra linear por trás do treinamento."),
             ("Dados e gráficos", "pandas e NumPy para manipular; matplotlib para visualizar."),
         ],
         fala="O ferramental é praticamente padronizado. Python como linguagem, e o Jupyter Notebook como ambiente "
              "— ou o Google Colab, que é o Jupyter hospedado pela Google e não exige instalar nada na máquina de "
              "vocês. Para aprendizado clássico, a biblioteca é o scikit-learn: todos os algoritmos que eu vou "
              "apresentar nos próximos slides estão nela, e é uma linha de código para usar cada um. Para "
              "aprendizado profundo, TensorFlow e PyTorch, com placas gráficas acelerando a álgebra linear. E, para "
              "os dados e os gráficos, pandas, NumPy e matplotlib."),

    # ── um algoritmo por lâmina ──
    dict(tipo="algoritmo", bloco=1, chapeu="Algoritmos supervisionados",
         titulo="K Vizinhos Mais Próximos",
         ideia="Este caso novo se parece com quais casos antigos?",
         como="Guarda os exemplos. Para prever, busca os K mais próximos e devolve a classe da maioria — ou a média deles, se a saída for um número.",
         serve="Classificar ou prever por semelhança direta, sem construir modelo nenhum.",
         onde="Bases pequenas, poucas variáveis, e quando se quer justificar a resposta mostrando os casos parecidos. Exige escala ajustada.",
         fala="O primeiro é o mais simples de todos: K vizinhos mais próximos. A ideia cabe numa pergunta — este "
              "caso novo se parece com quais casos antigos? O algoritmo guarda os exemplos, e para prever busca os K "
              "mais próximos e devolve a classe da maioria, ou a média deles se a saída for um número. Ele se presta "
              "a classificar por semelhança direta, sem construir modelo nenhum. É mais adequado em bases pequenas, "
              "com poucas variáveis, e quando você quer justificar a resposta mostrando os casos parecidos — o que "
              "em medicina é um argumento forte. Dois cuidados: as variáveis precisam estar na mesma escala, e o "
              "custo cresce com a base, porque a cada previsão ele varre tudo."),

    dict(tipo="algoritmo", bloco=1, chapeu="Algoritmos supervisionados",
         titulo="Regressão Linear",
         ideia="Prever um número como combinação de fatores.",
         como="Ajusta uma reta — ou um plano, quando há vários fatores — minimizando o erro pelo gradiente descendente.",
         serve="Prever quantidades contínuas e medir quanto cada fator pesa no resultado.",
         onde="Relações aproximadamente lineares, quando interessa não só a previsão, mas o tamanho e o sinal do efeito de cada variável.",
         fala="Regressão linear. A ideia é prever um número a partir de outros: o valor de uma variável como "
              "combinação das demais. Com uma variável é uma reta; com várias, um plano. O ajuste é feito pelo "
              "gradiente descendente, que corrige os coeficientes até o erro parar de cair. Presta-se a prever "
              "quantidades contínuas — tempo de internação, dose, custo. E é mais adequada quando a relação é "
              "aproximadamente linear e quando interessa não apenas a previsão, mas o tamanho e o sinal do efeito de "
              "cada fator, porque os coeficientes se leem diretamente: este fator soma tanto, aquele subtrai tanto."),

    dict(tipo="algoritmo", bloco=1, chapeu="Algoritmos supervisionados",
         titulo="Regressão Logística",
         ideia="Separar duas classes e dizer com que probabilidade.",
         como="Encontra a fronteira que separa as classes — o limite de decisão — e passa o resultado pela função sigmoide, que comprime tudo entre zero e um.",
         serve="Classificação binária com probabilidade, e com o efeito de cada fator interpretável.",
         onde="Escores de risco clínico. É o algoritmo mais usado em medicina, porque cada coeficiente se traduz em razão de chances.",
         fala="Regressão logística. Apesar do nome, é classificação. Ela encontra uma fronteira que separa as "
              "classes — o limite de decisão — e passa o resultado por uma função sigmoide, que comprime qualquer "
              "valor para o intervalo entre zero e um. O que sai não é um rótulo seco: é uma probabilidade. Por isso "
              "ela se presta a escore de risco, onde não basta dizer se o paciente vai piorar, é preciso dizer com "
              "que chance. E é o algoritmo mais usado em medicina por um motivo bem prático: cada coeficiente se "
              "traduz em razão de chances, que é a linguagem da literatura clínica. A limitação é que a fronteira é "
              "sempre linear; quando não dá para separar por uma reta, é preciso acrescentar termos de grau maior — "
              "ou trocar de algoritmo."),

    dict(tipo="algoritmo", bloco=1, chapeu="Algoritmos supervisionados",
         titulo="Árvore de Decisão",
         ideia="Uma sequência de perguntas de sim ou não.",
         como="Procura a variável e o ponto de corte que melhor separam as classes, parte os dados ali, e repete dentro de cada pedaço.",
         serve="Produzir regra legível — um caminho da raiz até a folha que um especialista consegue ler e contestar.",
         onde="Critérios e protocolos que precisam ser auditados. Lida bem com mistura de variáveis numéricas e categóricas.",
         fala="Árvore de decisão. A ideia é uma sequência de perguntas de sim ou não. O algoritmo procura a variável "
              "e o ponto de corte que melhor separam as classes, parte os dados ali, e repete o processo dentro de "
              "cada pedaço. Para classificar um caso novo, você percorre a árvore da raiz até a folha, respondendo "
              "aos testes. Ela se presta ao que nenhum outro faz tão bem: produzir regra legível. Um médico consegue "
              "ler a árvore e discordar dela, apontando o nó onde discorda — e isso, em domínio regulado, vale ouro. "
              "É mais adequada quando o critério precisa ser auditado. O defeito é conhecido: a árvore isolada tende "
              "a decorar o treino. É desse defeito que nasce o algoritmo seguinte."),

    dict(tipo="algoritmo", bloco=1, chapeu="Algoritmos supervisionados",
         titulo="Random Forest — Floresta Aleatória",
         ideia="Muitas árvores diferentes, decidindo juntas.",
         como="Cada árvore é treinada numa variação da base e num sorteio de variáveis. A decisão final é a média — ou o voto — de todas elas.",
         serve="Corrigir o sobreajuste da árvore isolada, e ranquear a importância de cada fator.",
         onde="Muitos fatores e relações não lineares, quando robustez importa mais do que ler uma regra única.",
         fala="Floresta aleatória. Ela nasce do defeito da anterior: a árvore isolada tende a decorar os dados de "
              "treino. A ideia é construir muitas árvores ligeiramente diferentes — cada uma treinada numa variação "
              "da base e num sorteio das variáveis — e tomar a decisão pela média, ou pelo voto, de todas. Cada "
              "árvore continua viciada, mas os vícios não são os mesmos, e acabam se cancelando. Presta-se a "
              "classificação robusta quando há muitos fatores e relações não lineares. E entrega de brinde uma coisa "
              "muito útil em pesquisa: o ranqueamento da importância de cada variável. O preço é a perda da regra "
              "única legível — você ganha acerto e perde a leitura direta."),

    dict(tipo="algoritmo", bloco=1, chapeu="Algoritmos supervisionados",
         titulo="Máquina de Vetores de Suporte",
         ideia="Entre todas as fronteiras possíveis, a de maior margem.",
         como="Procura o plano que separa as classes deixando a maior distância para os exemplos mais próximos — os vetores de suporte. Só eles determinam a fronteira.",
         serve="Separar classes em espaços de muitas dimensões, inclusive com fronteiras curvas, usando funções de núcleo.",
         onde="Bases de tamanho moderado com muitas variáveis: expressão gênica, texto vetorizado, espectros.",
         fala="Máquina de vetores de suporte. A ideia é escolher, entre todas as fronteiras que separam as classes, "
              "aquela que deixa a maior margem possível. Os pontos que ficam na borda dessa margem são os vetores de "
              "suporte, e são só eles que determinam a fronteira — o resto da base não conta, o que dá ao algoritmo "
              "uma estabilidade interessante. Com funções de núcleo, ele representa fronteiras curvas sem precisar "
              "calcular explicitamente as dimensões extras. Presta-se a separar classes em espaços de muitas "
              "dimensões. É mais adequada em bases de tamanho moderado com muitas variáveis, como dados de expressão "
              "gênica ou texto vetorizado. Em base muito grande, o treinamento fica lento."),

    dict(tipo="algoritmo", bloco=1, chapeu="Algoritmo não supervisionado",
         titulo="K-Means — K Médias",
         ideia="Achar os grupos sem que ninguém diga quais são.",
         como="Sorteia K centros; atribui cada ponto ao centro mais próximo; recalcula cada centro como a média do seu grupo; repete até a atribuição não mudar mais.",
         serve="Descobrir perfis e segmentos que ninguém rotulou — classificação sem treinamento.",
         onde="Exploração inicial dos dados. Exige escolher K de antemão e supõe grupos aproximadamente esféricos e de tamanho parecido.",
         fala="K médias, o único não supervisionado da lista. Aqui ninguém diz quais são os grupos: o algoritmo os "
              "descobre. Ele sorteia K centros, atribui cada ponto ao centro mais próximo, recalcula cada centro "
              "como a média dos pontos que ficaram com ele, e repete. Quando a atribuição para de mudar, ele para — "
              "num exemplo com três grupos isso costuma acontecer na terceira iteração. Presta-se a descobrir perfis "
              "que ninguém rotulou: estratos de pacientes, padrões de uso, agrupamentos de exames. É mais adequado "
              "como exploração inicial, antes de decidir o que se vai modelar. Dois limites: você precisa escolher o "
              "K de antemão, e ele supõe grupos aproximadamente esféricos e de tamanho parecido."),

    dict(tipo="video", bloco=1, titulo="O pipeline de Machine Learning, do início ao fim", minutos=8,
         resumo="o notebook executando as seis etapas sobre uma base clínica",
         percurso=["Carregar a base e visualizar as variáveis e suas correlações",
                   "Preparar: valores ausentes, fatores descartados, escala ajustada",
                   "Separar treino e teste, e mostrar por que a separação importa",
                   "Busca em grade comparando os algoritmos das lâminas anteriores",
                   "Treinar e ler o gráfico de perda por época — o ponto do sobreajuste",
                   "Avaliar: matriz de confusão, sensibilidade, especificidade e a curva ROC"],
         fala="Agora o primeiro vídeo. São oito minutos com o notebook executando exatamente as seis etapas que "
              "acabamos de ver, sobre uma base clínica real: carregar e visualizar, preparar, separar os conjuntos, "
              "comparar os algoritmos por busca em grade, treinar acompanhando o gráfico por época, e avaliar com "
              "matriz de confusão e curva ROC. É esse mesmo notebook que fica com vocês para refazer em casa — e eu "
              "sugiro refazer trocando o algoritmo, porque é trocando que se entende o que cada um faz."),

    # ───────────────────────── BLOCO 2 ─────────────────────────
    dict(tipo="divisor", bloco=2, titulo="Inteligência Artificial na saúde",
         mensagem="Três frentes: prognóstico e risco, diagnóstico, e tratamento.",
         fala="O segundo bloco leva esses algoritmos para o terreno de vocês. A inteligência artificial entra na "
              "saúde por três frentes bem distintas: prognóstico e avaliação de risco, diagnóstico, e tratamento. "
              "Cada uma usa algoritmos diferentes e, o que é menos óbvio, mede o sucesso de maneira diferente."),

    dict(tipo="cartoes", bloco=2, chapeu="IA na saúde", titulo="Prognóstico e avaliação de risco",
         destaque="A pergunta: qual a chance de um desfecho ruim — e em quanto tempo?",
         cartoes=[
             ("Escore de risco", "combina os fatores do paciente num número comparável entre pacientes. É o instrumento clássico da área."),
             ("Análise de sobrevivência", "quando o tempo importa: Kaplan-Meier estima a curva de sobrevivência; o modelo de Cox estima quanto cada fator multiplica o risco."),
             ("Árvores e florestas de sobrevivência", "quando a relação não é proporcional nem linear, substituem o Cox mantendo a leitura por fator."),
             ("Como se avalia", "índice de concordância no lugar da acurácia: o modelo ordena corretamente quem adoece antes?"),
         ],
         fala="A primeira frente é prognóstico: qual a chance de um desfecho ruim, e em quanto tempo. O instrumento "
              "clássico é o escore de risco, que combina os fatores do paciente num número comparável. Quando o "
              "tempo importa, usa-se análise de sobrevivência: a curva de Kaplan-Meier estima a probabilidade de "
              "sobreviver ao longo do tempo, e o modelo de riscos proporcionais de Cox estima quanto cada fator "
              "multiplica esse risco. Quando a proporcionalidade não se sustenta, entram as árvores e florestas de "
              "sobrevivência. E a avaliação muda de natureza: no lugar da acurácia, usa-se o índice de concordância, "
              "que pergunta se o modelo ordena corretamente quem adoece antes — que é o que o clínico precisa saber."),

    dict(tipo="cartoes", bloco=2, chapeu="IA na saúde", titulo="Diagnóstico",
         destaque="Três gerações convivendo no mesmo hospital.",
         cartoes=[
             ("Sistemas especialistas", "regras escritas junto com o especialista. Explicam a conclusão passo a passo — mas não aprendem nada sozinhos."),
             ("Aprendizado sobre dados clínicos", "classificação a partir de exame, sinal vital e história. É o território das árvores, das florestas e da regressão logística."),
             ("Diagnóstico por imagem", "redes convolucionais classificam e segmentam: radiologia, patologia, dermatologia, oftalmologia."),
             ("Interpretação, obrigatória", "mapas de saliência mostram em que região a rede se apoiou. Sem isso, o laudo não é defensável.", "warn"),
         ],
         fala="A segunda frente é diagnóstico, e ela tem três gerações convivendo no mesmo hospital. Os sistemas "
              "especialistas, feitos de regras escritas junto com o especialista: explicam a conclusão passo a "
              "passo, mas não aprendem nada sozinhos. O aprendizado sobre dados clínicos estruturados — exame, sinal "
              "vital, história — que é o território das árvores, das florestas e da regressão logística. E o "
              "diagnóstico por imagem, com redes convolucionais que classificam e segmentam. Nesse último caso a "
              "interpretação deixa de ser um extra: os mapas de saliência mostram em que região da imagem a rede se "
              "apoiou, e sem isso o laudo não é defensável diante de um questionamento."),

    dict(tipo="cartoes", bloco=2, chapeu="IA na saúde", titulo="Tratamento",
         cartoes=[
             ("Escolha de conduta", "modelos que estimam a resposta esperada a cada opção terapêutica, a partir do perfil do paciente."),
             ("Dose e ajuste", "previsão de valor contínuo a partir de peso, função renal e resposta anterior."),
             ("Resposta a questões médicas", "é aqui que entram os modelos de linguagem — e onde citar a evidência deixa de ser opcional e vira requisito."),
             ("O limite", "o modelo apoia a decisão. A responsabilidade clínica não se transfere para ele.", "warn"),
         ],
         fala="A terceira frente é tratamento. Modelos que estimam a resposta esperada a cada conduta possível, "
              "ajudando na escolha. Modelos que preveem dose a partir de peso, função renal e resposta anterior. E "
              "resposta a questões médicas, que é onde entram os modelos de linguagem — e onde a citação da "
              "evidência deixa de ser um detalhe de estilo e vira requisito, porque uma resposta clínica sem fonte é "
              "inútil: não pode ser conferida. Fica o limite, que vale para as três frentes: o modelo apoia a "
              "decisão; a responsabilidade clínica não se transfere para ele. Isso não é retórica — é o que define "
              "como o sistema tem de ser construído, e vamos ver isso concretamente no último bloco."),

    dict(tipo="video", bloco=2, titulo="Classificação e apoio à decisão em saúde", minutos=8,
         resumo="um escore de risco construído e avaliado do jeito certo",
         percurso=["A base clínica e o desfecho que se quer prever",
                   "Por que a acurácia mente aqui — e o que olhar no lugar dela",
                   "Regressão logística: o coeficiente virando razão de chances",
                   "Árvore de decisão: a regra que o clínico lê e contesta",
                   "Curva de sobrevivência e o efeito de cada fator no tempo",
                   "O que o modelo não pode decidir sozinho"],
         fala="O segundo vídeo mostra um escore de risco sendo construído e avaliado do jeito certo: a base, o "
              "desfecho, o motivo pelo qual a acurácia mente nesse cenário, a regressão logística com o coeficiente "
              "virando razão de chances, a árvore de decisão produzindo a regra que o clínico lê, e a curva de "
              "sobrevivência. Termina no ponto que mais importa: o que o modelo não pode decidir sozinho."),

    # ───────────────────────── BLOCO 3 ─────────────────────────
    dict(tipo="divisor", bloco=3, titulo="Deep Learning e Transfer Learning",
         mensagem="Do neurônio artificial às redes convolucionais — e como reaproveitar uma rede já treinada.",
         fala="O terceiro bloco é aprendizado profundo. Vamos do neurônio artificial até as redes convolucionais "
              "que fazem diagnóstico por imagem, e terminamos na técnica que torna tudo isso viável dentro de um "
              "hospital: a transferência de aprendizado."),

    dict(tipo="cartoes", bloco=3, chapeu="Deep Learning", titulo="Do neurônio artificial à rede de camadas",
         cartoes=[
             ("O neurônio", "soma as entradas multiplicadas por pesos e passa o resultado por uma função de ativação."),
             ("O limite de um só", "um neurônio isolado separa apenas o que é linearmente separável — não consegue nem representar o ou-exclusivo."),
             ("A saída: camadas", "empilhar neurônios resolve o ou-exclusivo e, por extensão, fronteiras de qualquer formato."),
             ("A rede de múltiplas camadas", "um nó de entrada por fator, uma ou mais camadas intermediárias, um nó de saída por classe."),
         ],
         fala="Aprendizado profundo começa num objeto muito simples. O neurônio artificial soma as entradas "
              "multiplicadas por pesos e passa o resultado por uma função de ativação. Um neurônio sozinho tem um "
              "limite conhecido desde os anos sessenta: ele só separa o que é linearmente separável, e por isso não "
              "consegue representar nem o ou-exclusivo, aquela função lógica que dá verdadeiro quando as entradas "
              "diferem. Esse limite quase matou a área. A saída foi empilhar neurônios em camadas: com uma camada "
              "intermediária o ou-exclusivo sai, e por extensão saem fronteiras de qualquer formato. É essa a rede "
              "de múltiplas camadas — um nó de entrada por fator, camadas intermediárias, e um nó de saída por classe."),

    dict(tipo="cartoes", bloco=3, chapeu="Deep Learning", titulo="Como a rede aprende: retropropagação",
         cartoes=[
             ("Para frente", "cada camada calcula sua saída e passa adiante, até a rede produzir uma resposta. Compara-se com a esperada e mede-se o erro."),
             ("Para trás", "partindo da saída, distribui-se a responsabilidade pelo erro camada a camada, corrigindo cada peso na direção que o reduz."),
             ("O motor", "é o gradiente descendente outra vez — agora aplicado em cadeia, da última camada até a primeira."),
             ("O que não tem fórmula", "quantos neurônios pôr nas camadas intermediárias. Existem regras de bolso para o ponto de partida; o resto é experimentação."),
         ],
         fala="Como essa rede aprende. O algoritmo chama-se retropropagação e tem dois movimentos. No movimento "
              "para frente, cada camada calcula sua saída e passa adiante até a rede produzir uma resposta; "
              "compara-se essa resposta com a esperada e mede-se o erro. No movimento para trás, parte-se da saída e "
              "distribui-se a responsabilidade por aquele erro camada a camada, corrigindo cada peso na direção que "
              "o reduz. É o gradiente descendente outra vez, agora aplicado em cadeia. Repete-se isso por muitas "
              "épocas. E há uma coisa que não tem fórmula fechada: quantos neurônios pôr nas camadas "
              "intermediárias. Existem regras de bolso para o ponto de partida, mas a determinação é experimental."),

    dict(tipo="cartoes", bloco=3, chapeu="Deep Learning", titulo="Redes convolucionais: o caminho da imagem",
         destaque="Ligar cada pixel a cada neurônio é inviável — uma imagem pequena já gera milhões de pesos.",
         cartoes=[
             ("A camada convolucional", "um filtro pequeno varre a imagem inteira procurando um padrão local: borda, textura, contorno. O mesmo filtro vale para a imagem toda."),
             ("A hierarquia", "as primeiras camadas acham bordas; as seguintes, formas; as últimas, objetos."),
             ("As camadas de agrupamento", "reduzem a resolução mantendo o que importa, e dão tolerância a deslocamento."),
             ("O resultado", "é essa arquitetura que sustenta radiologia, patologia e a segmentação de lesões."),
         ],
         fala="Para imagem, a rede densa não serve: ligar cada pixel a cada neurônio gera milhões de pesos, e a rede "
              "não generaliza. A solução é a camada convolucional. Um filtro pequeno varre a imagem inteira "
              "procurando um padrão local — uma borda, uma textura, um contorno — e o mesmo filtro vale para toda a "
              "imagem, o que reduz brutalmente o número de pesos. Empilhando camadas, aparece uma hierarquia: as "
              "primeiras acham bordas, as seguintes formas, as últimas objetos inteiros. Entre elas, as camadas de "
              "agrupamento reduzem a resolução e dão tolerância a deslocamento — o achado não precisa estar sempre "
              "no mesmo lugar. É essa arquitetura que sustenta o diagnóstico por imagem."),

    dict(tipo="codigo", bloco=3, chapeu="Deep Learning", titulo="Transfer Learning: reaproveitar uma rede treinada",
         intro="Treinar do zero exige milhões de imagens rotuladas. Reaproveitar exige algumas centenas.",
         codigo="\n".join([
             'base = ResNet50(weights="IMAGENET1K_V2", include_top=False)',
             'base.trainable = False          # congela o que já foi aprendido',
             '',
             'model = Sequential([',
             '    base,                       # bordas, texturas, formas',
             '    GlobalAveragePooling2D(),',
             '    Dropout(0.3),               # reduz o sobreajuste',
             '    Dense(2, activation="softmax")   # a SUA decisão clínica',
             '])',
             'model.fit(images, labels, epochs=10)',
         ]),
         explicacao="A rede pré-treinada já sabe reconhecer borda, textura e forma — isso não depende do domínio. "
                    "Você congela essa parte, troca a camada final pelas suas classes e treina só ela. "
                    "Depois, se quiser mais desempenho, descongela algumas camadas finais e faz o ajuste fino. "
                    "Modelos usuais: ResNet, VGG, DenseNet.",
         fala="E aqui está o que torna tudo isso viável num hospital. Treinar uma rede convolucional do zero exige "
              "milhões de imagens rotuladas, que ninguém tem. A transferência de aprendizado resolve: pega-se uma "
              "rede já treinada num acervo enorme de imagens genéricas — ResNet, VGG, DenseNet — congelam-se os "
              "pesos dela, remove-se a camada final e acrescenta-se uma camada nova com as classes do seu problema. "
              "A rede pré-treinada já sabe reconhecer borda, textura e forma, e isso não depende do domínio; você só "
              "ensina a última parte, que é a decisão clínica. Com algumas centenas de imagens você chega perto do "
              "que exigiria milhões. Depois, se quiser mais desempenho, descongela algumas camadas finais e faz o "
              "ajuste fino."),

    dict(tipo="video", bloco=3, titulo="Treinamento e Transfer Learning", minutos=8,
         resumo="a mesma tarefa treinada do zero e por reaproveitamento, lado a lado",
         percurso=["A base de imagens e o que se quer classificar",
                   "Treinar do zero: a curva que não sobe e o motivo",
                   "Carregar a rede pré-treinada e congelar os pesos",
                   "Trocar a camada final pelas classes do problema",
                   "A curva agora — e quantas imagens bastaram",
                   "Onde a rede olhou: o mapa de saliência sobre a imagem"],
         fala="O terceiro vídeo põe as duas coisas lado a lado: a mesma tarefa treinada do zero e por "
              "reaproveitamento. Você vê a curva que não sobe quando se treina do zero com poucos dados, e vê a "
              "mesma curva depois de carregar a rede pré-treinada. No fim, o mapa de saliência mostrando em que "
              "região da imagem a rede se apoiou para decidir."),
]
