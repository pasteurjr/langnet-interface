# -*- coding: utf-8 -*-
"""V10 · passe de enxugamento para caber no teto de uma hora de lâminas faladas.

REMOVER  — lâminas que repetem o que outra já diz.
ENXUGAR  — narrações reescritas mais curtas, mantendo o argumento e cortando a elaboração.

O passe fica separado de propósito: dá para ver exatamente o que foi cortado e por quê.
"""

REMOVER = {
    "As cinco opções",                       # a tabela comparativa já percorre os cinco
    "Ajuste fino: o que é e o que custa",     # absorvido na escada da adaptação
    "A família A2A, e a crítica que importa",  # a crítica migrou para o mapa MCP × A2A
    "A ponte para o próximo bloco",           # transição pura, dita na fala do divisor do bloco 10
    "Onde isso ainda vai chegar",             # fora da estrutura aprovada; não é BioByte nem LangNet
    "O que fica com vocês",                   # absorvido nas três conclusões
    "Com o que se faz isso hoje",             # o ferramental é o próprio bloco 11
}

ENXUGAR = {

"O caminho de hoje":
    "Bom dia. O caminho de hoje tem três pilares. Fundamento: aprendizado de máquina, aplicação em saúde, "
    "aprendizado profundo e modelos de linguagem. Engenharia: agentes, contexto, frameworks, ambientes de "
    "geração de código e protocolos. E método: desenvolvimento orientado a especificação, e o LangNet, que é a "
    "nossa implementação dele. Cada bloco fecha com uma demonstração em vídeo, e o notebook correspondente fica "
    "com vocês para praticar depois da aula. Nas lâminas eu passo rápido; a profundidade está no notebook.",

"Onde fica a fronteira":
    "Antes de falar de aprendizado, vale fixar a fronteira. Num algoritmo convencional a solução é conhecida, e o "
    "programador a escreve passo a passo: o menor caminho entre dois pontos tem procedimento exato. Num algoritmo "
    "inteligente a solução não é conhecida de antemão: no jogo da velha não existe fórmula da jogada certa, o "
    "programa avalia e escolhe. A diferença que importa é onde mora o conhecimento — no primeiro caso está no "
    "código; no segundo, está nos dados, e o código apenas o extrai.",

"Setenta anos em um minuto":
    "Um minuto de história. Mil novecentos e cinquenta: Turing propõe o teste da imitação. Cinquenta e oito: o "
    "Perceptron, o primeiro neurônio artificial que aprende. Anos oitenta: a retropropagação torna possível "
    "treinar redes de várias camadas. Dois mil e doze: as redes convolucionais vencem a competição de imagens e "
    "começa a era do aprendizado profundo. Dois mil e dezessete: o artigo do Transformer. Dois mil e vinte e "
    "dois: o ChatGPT leva os modelos de linguagem ao uso geral. E de dois mil e vinte e quatro em diante o "
    "assunto passa a ser agentes.",

"Aprendizado supervisionado e não supervisionado":
    "Aprendizado de máquina é extrair conhecimento a partir de dados. Há dois regimes. No supervisionado você "
    "fornece entradas e as saídas esperadas — é como se houvesse um professor ensinando por exemplos; depois de "
    "treinado, o modelo responde a uma entrada nova. No não supervisionado não existe professor: o modelo recebe "
    "só os dados e extrai deles a estrutura, agrupando o que é parecido. A consequência prática é financeira: o "
    "supervisionado exige dados rotulados, e rotular é o item mais caro de quase todo projeto clínico.",

"As seis etapas de um projeto de Machine Learning":
    "Um projeto de aprendizado de máquina tem seis etapas, sempre as mesmas: visualizar os dados, preparar os "
    "dados, definir os conjuntos, definir o modelo, efetuar o treinamento e avaliar. Guardem uma proporção que "
    "surpreende quem está começando: as duas primeiras consomem a maior parte do tempo de um projeto real; a "
    "modelagem, que é a parte que todo mundo acha interessante, é a parte curta. Vou passar por cada etapa "
    "dizendo o que se faz — é esse o roteiro que o notebook da primeira demonstração executa.",

"Visualizar e preparar os dados":
    "As duas primeiras etapas. Visualizar é olhar a distribuição de cada variável e a correlação entre elas antes "
    "de qualquer modelo — é aqui que você descobre que uma coluna está vazia na metade dos registros. Preparar é "
    "limpar: remover valores fora de contexto, preencher os ausentes, descartar fatores desnecessários, decompor "
    "os que misturam informação, agregar quando fizer sentido. E ajustar a escala. Esse ponto é prático e "
    "importante: se um fator varia de mil a um milhão e outro de zero a cem, muitos algoritmos não convergem.",

"Definir os conjuntos e escolher o modelo":
    "A terceira etapa separa os dados: tipicamente setenta a setenta e cinco por cento para treinamento, o "
    "restante para teste, sorteados aleatoriamente. E há uma regra inegociável: o modelo nunca pode ver, no "
    "treino, os dados com que vai ser avaliado. Quando isso é violado — e é violado com frequência, por descuido "
    "— o resultado sai excelente e é falso. A quarta etapa escolhe o modelo, e na prática não se escolhe no "
    "chute: a busca em grade testa vários algoritmos e várias combinações de parâmetros e devolve o melhor.",

"Treinar e avaliar: o sobreajuste":
    "Treinar é apresentar os dados ao modelo repetidas vezes; cada passagem completa é uma época. O gráfico de "
    "perda e acurácia por época mostra o problema central da área: o sobreajuste. A partir de certo ponto, a "
    "acurácia no treino continua subindo mas a do teste começa a cair. O modelo decorou e perdeu a capacidade de "
    "generalizar — não adianta treinar mais, adianta parar antes. O oposto também existe: o subajuste, quando o "
    "modelo treinou de menos e não acerta nem no treino.",

"Como se mede um classificador":
    "Avaliar não é olhar um número só. A matriz de confusão mostra acertos e erros de cada classe. Dela saem a "
    "sensibilidade, que é a fração de doentes que o modelo pegou, e a especificidade, a fração de sadios que ele "
    "deixou em paz. A curva ROC resume o compromisso entre as duas ao longo de todos os limiares. E fica o alerta "
    "que vale para a saúde inteira: acurácia engana em base desbalanceada. Com prevalência de dois por cento, um "
    "modelo que responde sempre “não” acerta noventa e oito por cento das vezes — e é inútil.",

"Com o que se trabalha":
    "O ferramental é praticamente padronizado. Python como linguagem, e o Jupyter Notebook como ambiente — ou o "
    "Google Colab, que é o Jupyter hospedado pela Google e não exige instalar nada. Para aprendizado clássico, o "
    "scikit-learn: todos os algoritmos dos próximos slides estão nele, e é uma linha de código para usar cada um. "
    "Para aprendizado profundo, TensorFlow e PyTorch. E, para os dados e os gráficos, pandas, NumPy e matplotlib.",

"K Vizinhos Mais Próximos":
    "O primeiro é o mais simples de todos. A ideia cabe numa pergunta: este caso novo se parece com quais casos "
    "antigos? O algoritmo guarda os exemplos e, para prever, busca os K mais próximos e devolve a classe da "
    "maioria — ou a média deles, se a saída for um número. Presta-se a classificar por semelhança direta, sem "
    "construir modelo nenhum. É mais adequado em bases pequenas e quando você quer justificar a resposta "
    "mostrando os casos parecidos, o que em medicina é um argumento forte. Dois cuidados: as variáveis precisam "
    "estar na mesma escala, e o custo cresce com o tamanho da base.",

"Regressão Linear":
    "Regressão linear. A ideia é prever um número a partir de outros: com uma variável é uma reta, com várias, um "
    "plano. O ajuste é feito pelo gradiente descendente, que corrige os coeficientes até o erro parar de cair. "
    "Presta-se a prever quantidades contínuas — tempo de internação, dose, custo. É mais adequada quando a "
    "relação é aproximadamente linear e quando interessa não só a previsão, mas o tamanho e o sinal do efeito de "
    "cada fator, porque os coeficientes se leem diretamente.",

"Regressão Logística":
    "Regressão logística. Apesar do nome, é classificação. Ela encontra a fronteira que separa as classes e passa "
    "o resultado por uma função sigmoide, que comprime qualquer valor entre zero e um. O que sai não é um rótulo "
    "seco: é uma probabilidade. Por isso ela se presta a escore de risco, onde não basta dizer se o paciente vai "
    "piorar, é preciso dizer com que chance. E é o algoritmo mais usado em medicina por um motivo prático: cada "
    "coeficiente se traduz em razão de chances, que é a linguagem da literatura clínica. A limitação é que a "
    "fronteira é sempre linear.",

"Árvore de Decisão":
    "Árvore de decisão. A ideia é uma sequência de perguntas de sim ou não: o algoritmo procura a variável e o "
    "ponto de corte que melhor separam as classes, parte os dados ali, e repete dentro de cada pedaço. Ela se "
    "presta ao que nenhum outro faz tão bem: produzir regra legível. Um médico consegue ler a árvore e discordar "
    "dela apontando o nó onde discorda — e isso, em domínio regulado, vale ouro. É mais adequada quando o "
    "critério precisa ser auditado. O defeito é conhecido: a árvore isolada tende a decorar o treino. É desse "
    "defeito que nasce o algoritmo seguinte.",

"Random Forest — Floresta Aleatória":
    "Floresta aleatória. A ideia é construir muitas árvores ligeiramente diferentes — cada uma treinada numa "
    "variação da base e num sorteio das variáveis — e decidir pela média, ou pelo voto, de todas. Cada árvore "
    "continua viciada, mas os vícios não são os mesmos e acabam se cancelando. Presta-se a classificação robusta "
    "quando há muitos fatores e relações não lineares, e entrega de brinde o ranqueamento da importância de cada "
    "variável, que é muito útil em pesquisa. O preço é a perda da regra única legível.",

"Máquina de Vetores de Suporte":
    "Máquina de vetores de suporte. A ideia é escolher, entre todas as fronteiras que separam as classes, aquela "
    "que deixa a maior margem possível. Os pontos na borda dessa margem são os vetores de suporte, e são só eles "
    "que determinam a fronteira — o resto da base não conta. Com funções de núcleo, ela representa fronteiras "
    "curvas. Presta-se a separar classes em espaços de muitas dimensões, e é mais adequada em bases de tamanho "
    "moderado com muitas variáveis, como expressão gênica ou texto vetorizado. Em base muito grande, o "
    "treinamento fica lento.",

"K-Means — K Médias":
    "K médias, o único não supervisionado da lista. Aqui ninguém diz quais são os grupos: o algoritmo os "
    "descobre. Ele sorteia K centros, atribui cada ponto ao centro mais próximo, recalcula cada centro como a "
    "média do seu grupo, e repete até a atribuição parar de mudar. Presta-se a descobrir perfis que ninguém "
    "rotulou: estratos de pacientes, padrões de uso. É mais adequado como exploração inicial. Dois limites: você "
    "escolhe o K de antemão, e ele supõe grupos aproximadamente esféricos e de tamanho parecido.",

"Prognóstico e avaliação de risco":
    "A primeira frente é prognóstico: qual a chance de um desfecho ruim, e em quanto tempo. O instrumento "
    "clássico é o escore de risco, que combina os fatores do paciente num número comparável. Quando o tempo "
    "importa, usa-se análise de sobrevivência: a curva de Kaplan-Meier estima a probabilidade de sobreviver ao "
    "longo do tempo, e o modelo de Cox estima quanto cada fator multiplica esse risco. E a avaliação muda de "
    "natureza: no lugar da acurácia, o índice de concordância, que pergunta se o modelo ordena corretamente quem "
    "adoece antes.",

"Diagnóstico":
    "A segunda frente é diagnóstico, e tem três gerações convivendo no mesmo hospital. Os sistemas especialistas, "
    "feitos de regras escritas junto com o especialista: explicam a conclusão passo a passo, mas não aprendem "
    "sozinhos. O aprendizado sobre dados clínicos estruturados — exame, sinal vital, história — que é o território "
    "das árvores, das florestas e da regressão logística. E o diagnóstico por imagem, com redes convolucionais. "
    "Nesse último caso a interpretação é obrigatória: os mapas de saliência mostram em que região a rede se "
    "apoiou, e sem isso o laudo não é defensável.",

"Tratamento":
    "A terceira frente é tratamento. Modelos que estimam a resposta esperada a cada conduta possível. Modelos que "
    "preveem dose a partir de peso, função renal e resposta anterior. E resposta a questões médicas, que é onde "
    "entram os modelos de linguagem — e onde citar a evidência vira requisito, porque uma resposta clínica sem "
    "fonte não pode ser conferida. Fica o limite, que vale para as três frentes: o modelo apoia a decisão; a "
    "responsabilidade clínica não se transfere. Isso não é retórica — é o que define como o sistema tem de ser "
    "construído.",

"Do neurônio artificial à rede de camadas":
    "Aprendizado profundo começa num objeto muito simples. O neurônio artificial soma as entradas multiplicadas "
    "por pesos e passa o resultado por uma função de ativação. Um neurônio sozinho tem um limite conhecido desde "
    "os anos sessenta: só separa o que é linearmente separável, e não consegue representar nem o ou-exclusivo. "
    "Esse limite quase matou a área. A saída foi empilhar neurônios em camadas: com uma camada intermediária o "
    "ou-exclusivo sai, e por extensão saem fronteiras de qualquer formato.",

"Como a rede aprende: retropropagação":
    "A retropropagação tem dois movimentos. No movimento para frente, cada camada calcula sua saída e passa "
    "adiante até a rede produzir uma resposta; compara-se com a esperada e mede-se o erro. No movimento para "
    "trás, parte-se da saída e distribui-se a responsabilidade por aquele erro camada a camada, corrigindo cada "
    "peso na direção que o reduz — é o gradiente descendente outra vez, aplicado em cadeia. Repete-se por muitas "
    "épocas. E quantos neurônios pôr nas camadas intermediárias não tem fórmula fechada: é experimentação.",

"Redes convolucionais: o caminho da imagem":
    "Para imagem, a rede densa não serve: ligar cada pixel a cada neurônio gera milhões de pesos e a rede não "
    "generaliza. A solução é a camada convolucional. Um filtro pequeno varre a imagem inteira procurando um "
    "padrão local — borda, textura, contorno — e o mesmo filtro vale para toda a imagem, o que reduz brutalmente "
    "o número de pesos. Empilhando camadas aparece uma hierarquia: as primeiras acham bordas, as seguintes "
    "formas, as últimas objetos. É essa arquitetura que sustenta o diagnóstico por imagem.",

"Transfer Learning: reaproveitar uma rede treinada":
    "E aqui está o que torna tudo isso viável num hospital. Treinar uma rede do zero exige milhões de imagens "
    "rotuladas, que ninguém tem. A transferência de aprendizado resolve: pega-se uma rede já treinada num acervo "
    "enorme de imagens genéricas, congelam-se os pesos, remove-se a camada final e acrescenta-se uma camada nova "
    "com as classes do seu problema. A rede pré-treinada já sabe reconhecer borda, textura e forma, e isso não "
    "depende do domínio; você só ensina a decisão clínica. Com algumas centenas de imagens você chega perto do "
    "que exigiria milhões.",

"O que é um modelo de linguagem":
    "Um modelo de linguagem é um estimador: dado todo o texto anterior, qual é o próximo pedaço de texto. A "
    "unidade não é a palavra, é o token — “hemocultura” pode virar três ou quatro tokens. O treinamento consiste "
    "em prever o próximo token sobre um corpus imenso, e não exige rótulo humano: o próprio texto é a resposta. "
    "Tirem daqui a consequência mais importante: ele não consulta uma base de fatos, ele produz a continuação "
    "mais provável. É por isso que ele inventa com fluência — e por que vamos precisar de recuperação de "
    "documentos e de portões determinísticos.",

"De onde veio o Transformer":
    "A arquitetura tem data e endereço: o artigo “Attention Is All You Need”, de Vaswani e colegas, do Google "
    "Brain e da Universidade de Toronto, de dois mil e dezessete. Antes dele, as redes recorrentes processavam a "
    "sequência passo a passo: as dependências longas se perdiam e o treinamento quase não paralelizava, o que "
    "punha um teto no tamanho dos modelos. A contribuição foi a atenção: cada token passa a se relacionar "
    "diretamente com todos os outros. E o efeito decisivo foi o colateral — como tudo virou paralelizável, "
    "escalar deixou de ser impossível.",

"Anatomia: consulta, chave e valor":
    "A anatomia em uma frase. Cada token faz uma pergunta — a consulta. Todos anunciam o que têm — a chave. A "
    "semelhança entre as duas decide de quem esse token copia informação — o valor. Isso acontece em várias "
    "cabeças ao mesmo tempo, cada uma capturando um aspecto diferente da mesma frase. E guardem o ponto de "
    "engenharia: a atenção é quadrática no tamanho da entrada — dobrar o texto quadruplica a conta. Custo por "
    "token, limite de janela e toda a economia de contexto nascem dessa quadrática.",

"Escala, e o que veio com ela":
    "O que a escala trouxe foi surpreendente: capacidades que ninguém programou — seguir instrução, traduzir, "
    "resumir, escrever código, raciocinar em passos. Elas aparecem à medida que o modelo cresce. A novidade "
    "recente é a mistura de especialistas: modelos com trilhões de parâmetros totais que ativam só dezenas de "
    "bilhões por token. Mas registrem o que a escala não resolveu: a invenção confiante e a ausência de qualquer "
    "garantia de correção. E daí sai a consequência que percorre o resto da palestra: se o modelo não garante "
    "correção, a garantia tem de vir de fora dele.",

"Panorama: modelos proprietários":
    "Um panorama rápido dos proprietários, com uma ressalva que eu peço que levem a sério. O teste citado mede "
    "correção de defeitos reais de software, e os três modelos de ponta estão hoje num patamar parecido. A "
    "ressalva: o número do fabricante e o de uma medição independente divergem, às vezes muito. Quando forem "
    "citar desempenho de modelo num documento ou numa decisão de compra, citem a fonte e a data — sem isso o "
    "número não significa nada, e essa tabela envelhece em semanas.",

"Panorama: modelos abertos":
    "E os abertos, que para vocês interessam mais por um motivo específico: dado de paciente que não pode sair do "
    "hospital exige modelo rodando dentro do hospital. A linha que eu destaco é a do Qwen de vinte e sete "
    "bilhões: denso, multimodal, licença Apache, e roda numa placa de vinte e quatro gigabytes — uma máquina que "
    "o setor de informática de vocês consegue comprar. É esse o modelo do nosso laboratório. E o alerta jurídico: "
    "“pesos abertos” não é “código aberto”. Leiam a licença antes de projetar em cima do modelo.",

"A escada da adaptação":
    "Quando o modelo não faz o que você quer existe uma escada, e quase todo mundo começa pelo degrau errado. O "
    "primeiro é a instrução: escrever melhor o pedido e dar exemplos; custa quase nada e resolve mais do que se "
    "imagina. O segundo é o contexto: trazer para dentro do pedido o protocolo, a norma, o documento certo. O "
    "terceiro é ferramenta: deixar o modelo consultar o sistema real em vez de lembrar. E só o quarto é ajuste "
    "fino, que muda os pesos — hoje viável com LoRA e QLoRA, que cabem numa única placa. Subam um degrau apenas "
    "quando o anterior comprovadamente não bastar: ajuste fino feito cedo é dinheiro queimado, e ele ensina "
    "formato e jargão, não fato novo.",

"De modelo para agente":
    "A diferença entre modelo e agente é menor do que o vocabulário sugere. Um modelo recebe texto e devolve "
    "texto: não consulta nada, não altera nada, não lembra de nada entre chamadas. Um agente recebe um objetivo, "
    "escolhe uma ação, executa-a por meio de uma ferramenta, observa o resultado e decide o passo seguinte. A "
    "peça nova é o laço. E com o laço vem a capacidade de causar efeito no mundo — inclusive efeito indesejado, "
    "que é o motivo pelo qual o resto deste bloco existe.",

"Definição operacional, sem misticismo":
    "A definição operacional, sem misticismo: um agente tem cinco peças. Um objetivo escrito de forma "
    "verificável, sem o qual não há como dizer se ele terminou. Um contexto, que é o que ele sabe nesta execução. "
    "Um conjunto de ferramentas, que é o que ele pode fazer. Uma memória, que é o que atravessa execuções — e eu "
    "insisto em distinguir memória de contexto, porque confundi-las é fonte de defeito sutil. E um critério de "
    "parada. Se alguma dessas cinco estiver faltando no projeto de vocês, ele vai falhar em produção.",

"O laço agêntico":
    "O laço tem quatro passos, e eu quero que o terceiro fique gravado. Primeiro, o modelo recebe o objetivo e o "
    "estado e decide a próxima ação. Segundo, ele pede a ferramenta: emite um nome e argumentos. Ele não executa "
    "nada — nenhum modelo executa nada. Terceiro, quem executa é o seu programa, e é aí que entram a permissão, o "
    "limite e o registro de auditoria. Quarto, o resultado volta ao contexto e o laço recomeça. Essa separação "
    "entre quem pede e quem executa é o que permite que um sistema com agente seja auditável.",

"Uso de ferramenta, sem framework nenhum":
    "E aqui está o laço inteiro, sem framework nenhum. Você declara as ferramentas, chama o modelo, e olha o que "
    "voltou: se ele não pediu ferramenta, acabou. Se pediu, o seu código executa a função e devolve o resultado "
    "para a conversa. Repete. São vinte linhas, e é isso que todo framework faz por baixo. Eu mostro isso por uma "
    "razão prática: comecem assim. Quando o laço próprio ficar insuficiente, vocês vão saber exatamente por quê — "
    "e aí escolhem o framework pelo motivo certo, não por moda.",

"Os padrões de composição":
    "Há seis maneiras de compor. Encadeamento: a saída de um passo é a entrada do seguinte — simples e resolve a "
    "maioria dos casos reais. Roteamento: um classificador barato decide qual especialista atende. Paralelismo, "
    "para tarefas independentes. Orquestrador e executores: um planeja, os outros executam. Avaliador e "
    "otimizador: um produz, outro critica, e repete. E o sexto, que é o que interessa em domínio regulado: "
    "autonomia com portão — o agente escolhe o caminho, mas cada etapa passa por uma verificação em código. É "
    "esse o padrão do sistema que vou mostrar no fim.",

"Multiagente: quando compensa, e quando não":
    "Sobre multiagente eu vou na contramão do entusiasmo. Só compensa quando duas condições valem juntas: as "
    "subtarefas são de fato paralelizáveis, e os contextos são isolados. Se as partes não são independentes, o "
    "custo explode sem ganho — medidas em fluxo linear mostram de quatro a quinze vezes mais tokens para "
    "reimplementar o que um condicional resolveria. E há um efeito que quase ninguém contabiliza: a passagem de "
    "contexto entre agentes perde informação, como fotocópia de fotocópia. A pergunta a fazer diante de qualquer "
    "desenho multiagente é: esta divisão existe porque o problema pede?",

"Por que agentes falham em produção":
    "E agora o número que muda a conversa. Um agente com noventa e cinco por cento de acerto por passo, numa "
    "cadeia de vinte passos, termina com trinta e seis por cento de sucesso de ponta a ponta. Não é pessimismo, é "
    "aritmética. Os modos de falha são conhecidos — laço infinito, ferramenta inventada, contexto contaminado, "
    "custo imprevisto. E o pior é a falha silenciosa: o agente relata sucesso e não fez nada; nenhum teste de "
    "tela pega isso, porque a tela mostra a mensagem de sucesso. A saída não é escrever um pedido melhor — é "
    "reduzir o número de passos não verificados.",

"De “prompt” para engenharia de contexto":
    "A expressão “engenharia de prompt” ficou pequena. O que importa é engenharia de contexto: o contexto é tudo "
    "o que entra na janela — a instrução do sistema, o histórico, os documentos recuperados, as definições das "
    "ferramentas e o estado. E a janela é recurso escasso e caro, por causa daquela quadrática. Decidir o que "
    "entra e o que fica de fora é decisão de projeto. E registrem um efeito contraintuitivo: com a janela muito "
    "cheia, o modelo passa a ignorar o meio do texto. Mais contexto pode piorar a resposta.",

"Recuperação aumentada por geração":
    "A técnica que resolve isso chama-se recuperação aumentada por geração. O problema é simples: o modelo não "
    "conhece o seu protocolo nem o prontuário do seu paciente. A solução tem três tempos. Indexar: os documentos "
    "são fatiados e cada pedaço vira um vetor, que é um endereço num espaço de significado. Recuperar: a pergunta "
    "também vira vetor, e busca-se o que está próximo — proximidade, aqui, é semelhança de sentido, não de "
    "palavra. E gerar com fonte, citando de onde saiu cada trecho. Essa última parte não é enfeite: sem citação, "
    "ninguém consegue conferir.",

"RAG na prática, com LangChain e Qdrant":
    "Na prática são vinte linhas. Você carrega o diretório de protocolos, fatia os documentos, transforma cada "
    "pedaço em vetor e guarda num banco de vetores. Na hora da pergunta, busca os trechos mais próximos, monta o "
    "pedido com eles e gera a resposta com temperatura baixa, citando a origem. O LangChain costura as peças. E "
    "eu quero que vocês reparem numa linha só: a do fatiamento. É ela que decide a qualidade de tudo — e é sobre "
    "ela o próximo slide.",

"Onde o RAG quebra: o fatiamento":
    "Deixe eu mostrar onde isso quebra, com um caso do domínio de vocês. Um critério de definição de caso de "
    "infecção hospitalar ocupa três parágrafos: critério clínico, critério laboratorial e janela temporal. Os "
    "três só fazem sentido lidos juntos. Se você fatia em pedaços de tamanho fixo, o laboratorial se separa da "
    "janela; a busca devolve metade da regra; o modelo completa o resto sozinho, com fluência; e o sistema "
    "notifica um falso positivo. Ninguém percebe, porque a resposta está bem escrita. A correção é fatiar pela "
    "unidade lógica — a regra inteira num pedaço. É o tipo de decisão que parece técnica e é clínica.",

"Saída estruturada e proteções":
    "Duas práticas fecham o bloco. A primeira é saída estruturada: em vez de aceitar texto livre, exija um "
    "esquema com campos definidos, e valide esses campos no seu código. Isso importa porque texto livre obriga o "
    "seu programa a interpretar o que o modelo escreveu, e interpretar é onde o defeito entra. A segunda é "
    "avaliação: um conjunto de casos com resposta esperada, rodado a cada mudança — sem isso vocês não têm como "
    "saber se uma alteração melhorou ou piorou o sistema. E, junto, as proteções: limite de passos, limite de "
    "custo, lista fechada de ferramentas, e confirmação humana no que é irreversível.",

"O critério de leitura":
    "Antes de comparar, o critério — e ele vale para qualquer framework novo que apareça depois desta palestra. "
    "Primeira pergunta: quem controla o laço, você ou o framework? Isso determina o quanto você consegue depurar "
    "quando der errado. Segunda: onde mora o estado — em memória, em sessão, ou num armazenamento durável que "
    "sobrevive a uma queda? Terceira: como o humano entra, existe ponto de interrupção e aprovação? Quarta: o que "
    "se enxerga de dentro, há registro de cada passo e custo por passo? Comparem por essas quatro, não por "
    "popularidade.",

"Comparativo, e a opinião contrária":
    "Os cinco, comparados pelas quatro perguntas. O SDK da OpenAI e o da Anthropic controlam o laço, com estado "
    "em sessão e em arquivos. O LangGraph é máquina de estados com persistência durável e interrupção nativa — é "
    "a escolha quando o fluxo precisa sobreviver a uma queda e passar por aprovação humana, quer dizer, produção "
    "regulada. O CrewAI declara papéis e tarefas em YAML e esconde o laço: ótimo para protótipo rápido, e é o que "
    "usamos no LangNet. O AutoGen põe agentes conversando, melhor para pesquisa. E a opinião contrária: para boa "
    "parte dos casos, o laço escrito à mão é mais simples de depurar. Framework se justifica por durabilidade, "
    "observabilidade e entrada do humano — não por elegância.",

"Mudou a unidade de trabalho":
    "A primeira coisa a entender é que a unidade de trabalho mudou. Antes era a linha de código: você escrevia as "
    "linhas, o editor completava palavras, e a revisão era sobre o que você tinha digitado. Agora a unidade é a "
    "tarefa descrita: você diz o que quer, o agente lê o repositório, propõe a mudança e roda os testes, e você "
    "revisa o diferencial. O que ficou mais importante foi saber dizer o que se quer e ler criticamente o que "
    "voltou. E o que ficou mais perigoso foi aceitar sem ler — um diferencial grande e bem formatado passa fácil "
    "por uma revisão apressada.",

"Claude Code: sessão de engenharia no terminal":
    "O Claude Code transforma o terminal numa sessão de engenharia com contexto persistente sobre o repositório "
    "inteiro. Vocês abrem a sessão, continuam a anterior, retomam uma sessão específica pelo identificador, ou "
    "rodam em modo não interativo passando a tarefa na linha de comando — e é esse último modo que permite pôr o "
    "agente dentro de um pipeline de integração contínua. As extensões que importam são três: as skills, que "
    "codificam um fluxo repetível; os subagentes, que dividem investigação e implementação; e o MCP, que liga o "
    "agente a ferramentas externas.",

"Codex: execução, revisão e saída verificável":
    "O Codex cobre o mesmo terreno com ênfase diferente: a sessão interativa serve à exploração, o modo de "
    "execução serve à automação. Duas opções merecem atenção. O registro em formato JSON deixa rastro de cada "
    "evento — e rastro é o que uma auditoria pede. E o esquema de saída obriga o agente a devolver algo que o seu "
    "código consegue validar, em vez de texto livre: é a mesma ideia de saída estruturada do bloco seis, agora "
    "aplicada ao próprio agente de código.",

"Cursor e o panorama dos editores":
    "O Cursor resolve o mesmo problema pelo outro lado: é um editor completo com o agente embutido, com contexto "
    "do projeto, edição em vários arquivos e revisão do diferencial na própria tela. A diferença é de ênfase — o "
    "terminal favorece automação, o editor favorece exploração e revisão visual. O que não muda em nenhum dos "
    "três é o essencial: quem aprova a mudança é uma pessoa; o agente propõe. E escolham pelo fluxo do time, não "
    "pela ferramenta.",

"O mapa: vertical e horizontal":
    "O mapa tem dois eixos. Na vertical, o MCP liga um agente às ferramentas e aos dados: um servidor publica "
    "ferramentas com nome, parâmetros e esquema de retorno, e qualquer agente compatível passa a poder usá-las. "
    "Isso importa porque a ferramenta deixa de ser código colado dentro do agente e vira um serviço com contrato. "
    "Na horizontal, o A2A liga agentes a outros agentes: descoberta de capacidades e delegação de tarefa. Uma "
    "frase para guardar o par: o MCP responde “o que eu posso fazer”; o A2A, “com quem eu posso contar”. E a "
    "crítica que importa: nenhum desses protocolos expressa governança — registram quem chamou quem, não sob qual "
    "política nem com que base legal. Em saúde, essa camada sobra para vocês.",

"Conhecimento em formato aberto":
    "Há ainda uma camada que quase ninguém discute: em que formato o conhecimento fica. A proposta mais "
    "interessante é radicalmente simples — um pacote de conhecimento é um diretório de arquivos em markdown, sem "
    "banco e sem servidor. Cada arquivo é um conceito, o caminho é o identificador, e os arquivos se referenciam "
    "por links comuns, o que transforma o diretório num grafo. Para vocês o uso é direto: um pacote com as "
    "definições de caso, as fórmulas dos indicadores e os procedimentos da comissão. Legível por agente e "
    "revisável por infectologista ao mesmo tempo, com histórico e autoria linha a linha.",

"O problema":
    "Começo pelo problema. Programar no sentimento funciona no protótipo e colapsa no sistema: enquanto é "
    "pequeno, tudo bem; quando cresce, ninguém mais segura o conjunto na cabeça. O sintoma é este — o código "
    "existe, funciona, e ninguém sabe qual requisito ele atende, nem se ainda atende. Com agentes isso ficou mais "
    "rápido, não menos: o agente produz em minutos o volume que antes levava semanas. E em domínio regulado esse "
    "descompasso tem outro nome: não conformidade. Não é dívida técnica, que se paga quando der. É risco "
    "regulatório, que aparece na auditoria.",

"A inversão":
    "A inversão é esta. Hoje o fluxo é requisito informal, código, e uma documentação que já nasce desatualizada, "
    "porque foi escrita depois, a partir do código. No desenvolvimento orientado a especificação o fluxo se "
    "inverte: a especificação é primária, dela sai o plano, do plano as tarefas, e das tarefas o código, que é "
    "derivado. O que se versiona e se mantém é a especificação; o código é o que se regenera. A analogia que fixa "
    "a ideia é a relação entre código-fonte e binário: ninguém revisa o binário, ninguém corrige um defeito "
    "editando o executável.",

"Anatomia de uma especificação útil":
    "O que faz uma especificação ser útil. Ela precisa de contexto e escopo, e precisa dos não objetivos — dizer "
    "o que está fora é o que impede o projeto de inchar. E precisa de requisitos verificáveis: cada requisito tem "
    "de admitir um teste que diga passou ou não passou. Comparem os dois exemplos. O bom diz quando o "
    "comportamento é disparado, o que o sistema deve fazer, em quanto tempo e com que evidência — dá para "
    "escrever o teste lendo a frase. O ruim diz “o sistema deve detectar infecções corretamente”, que não é "
    "verificável e portanto não é requisito. Se a especificação estiver cheia de frases do segundo tipo, o agente "
    "preenche as lacunas do jeito dele.",

"Da especificação ao código, e a rastreabilidade":
    "Vamos ver a ordem funcionando. O requisito diz: avaliar os critérios de infecção dentro de uma janela de "
    "quarenta e oito horas. Desse critério nasce o teste, que confere as bordas da janela. E só então nasce a "
    "implementação. A ordem é o ponto inteiro: quando o teste é escrito depois, olhando para o código, ele herda "
    "os defeitos da implementação — se o programador entendeu a janela errado, o teste confirma o erro com muita "
    "confiança. Escrito a partir do critério, não tem como herdar nada. E fica a trilha: requisito, teste, "
    "função, ligados por identificador.",

"Onde o SDD encontra os agentes":
    "Aqui as duas metades da palestra se encontram. A cadeia é: um agente especifica, um portão confere; um "
    "projeta, um portão confere; um implementa, um portão confere; um verifica. Duas decisões sustentam isso. "
    "Contexto isolado por etapa, que corta a contaminação de uma etapa para a outra. E — a que eu mais defendo — "
    "o portão é código determinístico: quem verifica é programa, não outro modelo, porque verificar com um "
    "segundo modelo apenas empilha incerteza. É assim que se resolve o erro composto do bloco cinco: o erro não "
    "se propaga pela cadeia, ele para na etapa em que nasceu.",

"O artefato regulatório sai de graça":
    "E há um ganho que costuma decidir a conversa com a diretoria. Software de saúde exige rastreabilidade de "
    "requisito a projeto, a teste, a código, mais gestão de risco documentada e ciclo de vida controlado. Quem "
    "trabalha orientado a especificação já tem a matriz de rastreabilidade — não como um documento montado na "
    "véspera da auditoria, mas como subproduto do método, versionado e com autoria. E isso permite inverter a "
    "objeção mais comum que vocês vão ouvir. Vão dizer: código gerado por inteligência artificial não é "
    "auditável. A resposta é que o método é precisamente o que o torna auditável. O que não é auditável é código "
    "escrito à mão, sem especificação, por alguém que já saiu da empresa.",

"Antipadrões: como o método morre na prática":
    "Os quatro jeitos de matar o método. Primeiro: escrever a especificação depois, para justificar o que já foi "
    "feito — isso é documentação, e documentação não guia nada. Segundo: o requisito não verificável, em que o "
    "agente preenche a lacuna com o critério dele. Terceiro: pôr outro modelo como portão, porque duas incertezas "
    "empilhadas não produzem uma certeza. E o quarto, o mais comum e o mais tentador: corrigir à mão no artefato "
    "final. Você edita o código gerado, funciona, e na próxima geração a correção some. O remédio é uma regra sem "
    "exceção: a correção entra na especificação, e o artefato é regerado. Inclusive quando parece só um detalhe.",

"Dois lados: a fábrica e a máquina":
    "Antes de percorrer as etapas, uma distinção que organiza tudo. O LangNet não é a aplicação — ele é a fábrica "
    "que produz a aplicação. De um lado a fábrica, que percorre as etapas do documento até o código e guarda cada "
    "artefato com versão, origem e autoria. Do outro a máquina: a aplicação gerada, rodando por conta própria com "
    "um executor que dispara as tarefas dos agentes. O que liga os dois é a rede de Petri, que sai da fábrica "
    "como artefato e entra na máquina como plano de execução. E daí sai a regra de ouro: defeito da aplicação se "
    "corrige na fábrica e se regera — nunca no artefato final.",

"As etapas, e o que se repete em todas elas":
    "São onze etapas, e o que importa entender primeiro é que todas seguem o mesmo ritual: você escolhe a origem "
    "e a versão de onde partir, gera, refina conversando com o agente daquela etapa, e aprova. Tudo é versionado "
    "— aprovar não apaga o anterior, e cada etapa guarda de qual versão da anterior ela nasceu, que é o que dá a "
    "rastreabilidade de ponta a ponta. Entre uma etapa e a seguinte há um portão em código determinístico: se a "
    "passagem não estiver íntegra, não avança, e o portão diz por quê. E refinar é literalmente conversar: você "
    "escreve a correção em português e o agente reescreve o artefato.",

"Do documento aos requisitos":
    "A primeira etapa recebe o documento do cliente — no nosso caso, o pedido do hospital para vigilância de "
    "infecção relacionada à assistência. Dele nascem os requisitos, e dois campos merecem atenção. A procedência: "
    "cada requisito diz se foi extraído do documento, inferido, trazido de pesquisa, ou acrescentado na conversa "
    "— e isso fica gravado, começando a trilha de auditoria. E a natureza: convencional ou agêntico. Cadastrar um "
    "paciente é convencional; classificar um caso pelo critério da norma é agêntico. Essa marca parece "
    "burocrática e decide o projeto inteiro, porque determina o que vira código comum e o que vira tarefa de "
    "agente. Quando é mal posta, o sistema faz quarenta e cinco tarefas de agente onde deveria ter oito.",

"A especificação funcional":
    "Da lista de requisitos nasce a especificação funcional, escrita em casos de uso. Cada um tem ator, "
    "pré-condições, fluxo principal passo a passo, e — o que mais falta nas especificações que eu vejo por aí — os "
    "fluxos de exceção, isto é, o que acontece quando dá errado. Cada caso de uso traz também o croqui da tela, e "
    "nos casos agênticos declara o que o agente decide e com base em quê. Há um portão conferindo uma coisa "
    "específica: o croqui e o fluxo têm de falar dos mesmos campos e dos mesmos botões. Quando divergem, o "
    "defeito atravessa o pipeline e só aparece na tela do usuário.",

"O modelo de dados, e a correção por conversa":
    "Das entidades dos casos de uso nasce o modelo de dados. E aqui há uma coisa que contraria a expectativa: a "
    "própria etapa aponta os seus defeitos. Ela avisa quando há coluna obrigatória sem valor padrão, quando o "
    "resultado de um agente não tem coluna dedicada, quando existe campo que ninguém preenche. Você lê o aviso e "
    "responde em português — por exemplo: a urgência precisa ser uma coluna própria, com valores fechados. O "
    "agente reescreve o modelo e grava uma versão nova, preservando a anterior, de modo que dá para comparar as "
    "duas. Isso vocês vão ver acontecendo na demonstração.",

"A interface e o protótipo":
    "Dos casos de uso nascem as telas, e cada tela nasce do croqui e do fluxo do caso de uso que a origina — não "
    "de um molde genérico de formulário. Isso importa porque uma tela de vigilância epidemiológica não é um "
    "cadastro: tem indicador, gráfico, tabela, lista e marcação, além dos campos. Se o gerador só souber desenhar "
    "campo de formulário, as telas viram casca vazia — e esse foi um defeito real que nós corrigimos. Depois vem "
    "o protótipo, que é o mesmo código com a fonte de dados trocada, compilando em milissegundos: ele serve para "
    "discutir a tela com o usuário enquanto mudar ainda é barato.",

"Ferramentas, agentes e tarefas":
    "Duas etapas que andam juntas. A de ferramentas responde a uma pergunta que quase todo projeto agêntico deixa "
    "em aberto: quem implementa cada ferramenta — código determinístico, tarefa de agente, ou serviço externo "
    "publicado por MCP. No BioByte são duas ferramentas reais publicadas por um servidor MCP, a consulta à "
    "microbiologia e o cálculo do escore de risco, e vocês vão vê-las sendo chamadas de verdade. A etapa seguinte "
    "define os agentes e as tarefas. E aqui está o detalhe que dá valor ao método: toda tarefa carrega o caso de "
    "uso e o requisito que a originaram. A matriz de rastreabilidade não é montada por ninguém — ela se forma "
    "sozinha.",

"A rede de Petri: a orquestração verificável":
    "Das tarefas e da sequência entre elas nasce a rede de Petri, e é a camada que mais me interessa. Ela tem "
    "lugares e transições: os lugares guardam estado, as transições disparam quando as condições estão "
    "satisfeitas. Não é um fluxograma bonito — a diferença é que ela admite prova. Ausência de travamento, "
    "alcançabilidade de cada estado e invariantes são verificados na estrutura, não testados por amostragem. O "
    "portão confere que a rede é bipartida, que não sobrou ilha inalcançável e que cada transição tem guarda. E o "
    "que isso acrescenta é de outra natureza: os testes dizem que funcionou nos casos testados; a rede diz o que "
    "é estruturalmente possível acontecer.",

"Casos de teste e geração do código":
    "Duas etapas fecham a fábrica. Os casos de teste saem dos critérios dos casos de uso, por tabela de decisão, "
    "e não do código — é a ordem que eu defendi no bloco anterior, aplicada. E conferem comportamento, não tela: "
    "“exibe a mensagem tal” não é caso de teste, “rejeita a senha errada” é. Não é preciosismo: foi por causa "
    "dessa distinção que, num sistema nosso, uma tela de acesso que não conferia a senha passou despercebida. "
    "Depois vem a geração, que produz a aplicação inteira. E o portão final confere se cada tarefa do documento "
    "chegou ao código e se cada passo de lógica virou implementação — reportando o que não virou.",

"A aplicação rodando, e a bancada de execução":
    "E aqui chegamos à máquina. A aplicação roda com os cadastros, os relatórios e as telas dos agentes, e um "
    "executor dispara a rede. O que eu quero que vocês vejam é a bancada: ela mostra cada tarefa em execução com "
    "a entrada que recebeu, o que o agente pensou, que ferramenta chamou e a saída que produziu. Isso funciona "
    "para qualquer aplicação gerada, porque o executor emite um conjunto padronizado de etiquetas. E o último "
    "ponto, que é o que mais me importa: falha não passa calada. O defeito que custa mais caro num sistema "
    "agêntico não é o erro — é o sucesso relatado sem trabalho feito.",

"O que foi medido, e o que ainda é lacuna":
    "E aqui está o que foi medido, com a honestidade que o método exige. A consulta à microbiologia devolve o "
    "micro-organismo, o antibiograma e a marca de multirresistência pela ferramenta MCP. O escore de risco é "
    "devolvido pela ferramenta, não redigido pelo modelo — essa distinção é tudo. A classificação aplica os "
    "critérios da norma. O alerta é registrado, e a notificação para fora do sistema continua declarada como "
    "lacuna. Vinte e dois dos vinte e três casos de teste conferidos contra as linhas do banco. Reparem que o "
    "sistema registra também o que não está pronto: uma lacuna declarada é item de projeto; uma lacuna escondida "
    "atrás de uma mensagem de sucesso é risco clínico.",

"O pipeline completo do LangNet, do documento à aplicação":
    "E aqui está a demonstração final: vinte minutos percorrendo a fábrica inteira. O documento do hospital "
    "entrando, os requisitos nascendo com procedência e natureza, a especificação com os fluxos de exceção e o "
    "croqui da tela, o modelo de dados apontando o próprio defeito e sendo corrigido por conversa, as telas, o "
    "protótipo, as ferramentas, os agentes, a rede de Petri, o portão, a geração do código — e, no fim, a "
    "aplicação rodando, com os agentes produzindo registros e a bancada mostrando cada entrada e cada saída. "
    "Peço que prestem atenção numa coisa só ao longo dos vinte minutos: em nenhum momento eu edito o artefato "
    "final. Toda correção entra na etapa e o artefato é regerado.",

"As três conclusões":
    "Três conclusões. A primeira: modelo nenhum garante correção, e nenhuma versão futura vai garantir — quem "
    "garante é o que você põe em volta dele, que é portão em código, saída estruturada e evidência citada. A "
    "segunda: a especificação virou o artefato principal, e o código passou a ser derivado; e derivado se regera, "
    "não se remenda. A terceira: rastreabilidade deixou de ser custo e virou subproduto. E a sugestão para "
    "segunda-feira: escolham um fluxo pequeno e verificável do serviço de vocês, escrevam a especificação dele "
    "com critério testável, e construam o portão antes de construir o agente. Os notebooks, os vídeos e as "
    "referências ficam com vocês.",
}


def aplicar(slides):
    """Remove as lâminas redundantes e troca as narrações enxugadas."""
    saida = []
    vistos = set()
    for s in slides:
        t = s.get("titulo", "")
        if t in REMOVER:
            continue
        if t in ENXUGAR:
            s = dict(s, fala=ENXUGAR[t])
            vistos.add(t)
        saida.append(s)
    faltando = set(ENXUGAR) - vistos
    if faltando:
        raise SystemExit("títulos de ENXUGAR que não casaram: %s" % sorted(faltando))
    return saida
