# Roteiro narrado — Engenharia de IA e Desenvolvimento Orientado a Especificação (V10)

> **Esta é a versão 10.** A versão 9 permanece intacta nos arquivos `apresentacao_iasdd_v9_biobyte.pptx` e `roteiro_narrado_iasdd_v9_biobyte.md`.


| | |
|---|---|
| **Lâminas** | 92 |
| **Tempo falado das lâminas** | **59 min 11 s** (a 135 palavras por minuto) |
| **Vídeos** | 6 demonstrações · 60 minutos |
| **Total** | 119 min 11 s |
| **Palavras de narração** | 7989 |

## Como ler este roteiro

Cada lâmina tem três partes:

1. **A imagem da lâmina** — o arquivo correspondente em `roteiro_narrado_iasdd_v10_biobyte_slides/`.
2. **O que está escrito na lâmina** — o texto que a plateia lê na tela.
3. **O que a narradora fala** — a fala literal, para ser lida em voz alta exatamente como está. Não há instrução de palco misturada ao texto.

---

## Sumário

- **Bloco 1 — Introdução e Machine Learning** (lâmina 4)
  - ▶ *vídeo 8 min — O pipeline de Machine Learning, do início ao fim* (lâmina 21)
- **Bloco 2 — Inteligência Artificial na saúde** (lâmina 22)
  - ▶ *vídeo 8 min — Classificação e apoio à decisão em saúde* (lâmina 26)
- **Bloco 3 — Deep Learning e Transfer Learning** (lâmina 27)
  - ▶ *vídeo 8 min — Treinamento e Transfer Learning* (lâmina 32)
- **Bloco 4 — Modelos de linguagem e Transformer** (lâmina 33)
  - ▶ *vídeo 8 min — Tokens, atenção e geração, por dentro* (lâmina 42)
- **Bloco 5 — Agentes** (lâmina 43)
  - ▶ *vídeo 8 min — Um sistema multiagente com resultado verificável* (lâmina 51)
- **Bloco 6 — Contexto e recuperação de documentos** (lâmina 52)
- **Bloco 7 — Frameworks de agentes** (lâmina 58)
- **Bloco 8 — Ambientes de geração de código** (lâmina 61)
- **Bloco 9 — Protocolos e contratos** (lâmina 66)
- **Bloco 10 — Desenvolvimento Orientado a Especificação** (lâmina 69)
- **Bloco 11 — LangNet e BioByte** (lâmina 77)
  - ▶ *vídeo 20 min — O pipeline completo do LangNet, do documento à aplicação* (lâmina 89)
- **Bloco 12 — Fechamento** (lâmina 90)

---

<div class="slide" id="slide-1"></div>

## Lâmina 01 — Engenharia de IA e Desenvolvimento Orientado a Especificação

**Tempo falado:** 0 s

![Lâmina 01](roteiro_narrado_iasdd_v10_biobyte_slides/slide_01.png)

### O que está escrito na lâmina

- **Engenharia de IA e Desenvolvimento Orientado a Especificação**
- *De um classificador em vinte linhas a uma fábrica de software conduzida por agentes*
- Pasteur Ottoni de Miranda Junior · doze blocos · seis demonstrações em vídeo

---

<div class="slide" id="slide-2"></div>

## Lâmina 02 — O caminho de hoje

**Tempo falado:** 35 s

![Lâmina 02](roteiro_narrado_iasdd_v10_biobyte_slides/slide_02.png)

### O que está escrito na lâmina

- *Três pilares, doze blocos, e um notebook para praticar depois de cada um.*
- **Fundamento** — aprendizado de máquina, aplicação em saúde, aprendizado profundo, modelos de linguagem.
- **Engenharia** — agentes, contexto e recuperação, frameworks, ambientes de geração de código, protocolos.
- **Método** — desenvolvimento orientado a especificação, e o LangNet — a nossa implementação dele.
- **Como vamos praticar** — cada bloco fecha com uma demonstração em vídeo; o notebook correspondente fica com vocês.

### O que a narradora fala

Bom dia. O caminho de hoje tem três pilares. Fundamento: aprendizado de máquina, aplicação em saúde, aprendizado profundo e modelos de linguagem. Engenharia: agentes, contexto, frameworks, ambientes de geração de código e protocolos. E método: desenvolvimento orientado a especificação, e o LangNet, que é a nossa implementação dele. Cada bloco fecha com uma demonstração em vídeo, e o notebook correspondente fica com vocês para praticar depois da aula. Nas lâminas eu passo rápido; a profundidade está no notebook.

---

<div class="slide" id="slide-3"></div>

## Lâmina 03 — A tese

**Tempo falado:** 32 s

![Lâmina 03](roteiro_narrado_iasdd_v10_biobyte_slides/slide_03.png)

### O que está escrito na lâmina

- > **O gargalo deixou de ser escrever código. Passou a ser especificar com precisão o que se quer.**
- **O que mudou** — quando o código sai em minutos, a digitação para de ser o custo dominante do projeto.
- **O que não mudou** — um sistema continua valendo o que vale a definição do problema que ele resolve.

### O que a narradora fala

A tese da palestra é esta: o gargalo do desenvolvimento deixou de ser escrever código; passou a ser especificar com precisão o que se quer. Quando um agente escreve o código em minutos, o que separa um sistema que funciona de um que não funciona já não é a digitação — é a qualidade da especificação que você entregou a ele. Guardem essa frase, porque tudo o que vem depois é consequência dela.

---

<div class="slide" id="slide-4"></div>

## Lâmina 04 — Introdução e Machine Learning

**Tempo falado:** 28 s

![Lâmina 04](roteiro_narrado_iasdd_v10_biobyte_slides/slide_04.png)

### O que está escrito na lâmina

- **BLOCO 1 — Introdução e Machine Learning**
- *O que é aprendizado de máquina, como se monta um projeto do início ao fim, e um algoritmo por lâmina.*

### O que a narradora fala

Começamos pelo começo: o que é aprendizado de máquina, como se monta um projeto de aprendizado do início ao fim, e quais são os algoritmos clássicos. Vou dedicar uma lâmina a cada algoritmo, dizendo em poucas palavras qual é a ideia dele e para que ele se presta melhor. A matemática não vem para a tela — ela está no notebook que vocês levam.

---

<div class="slide" id="slide-5"></div>

## Lâmina 05 — Onde fica a fronteira

**Tempo falado:** 38 s

![Lâmina 05](roteiro_narrado_iasdd_v10_biobyte_slides/slide_05.png)

### O que está escrito na lâmina

- *O que separa um algoritmo convencional de um algoritmo inteligente.*
- **Algoritmo convencional** — a solução é conhecida e o programador a escreve passo a passo. O menor caminho entre dois pontos tem procedimento exato.
- **Algoritmo inteligente** — a solução não é conhecida de antemão. No jogo da velha não há fórmula da jogada certa: o programa avalia e escolhe.
- **O que realmente muda** — onde mora o conhecimento. No primeiro caso ele está no código; no segundo, está nos dados — e o código apenas o extrai.

### O que a narradora fala

Antes de falar de aprendizado, vale fixar a fronteira. Num algoritmo convencional a solução é conhecida, e o programador a escreve passo a passo: o menor caminho entre dois pontos tem procedimento exato. Num algoritmo inteligente a solução não é conhecida de antemão: no jogo da velha não existe fórmula da jogada certa, o programa avalia e escolhe. A diferença que importa é onde mora o conhecimento — no primeiro caso está no código; no segundo, está nos dados, e o código apenas o extrai.

---

<div class="slide" id="slide-6"></div>

## Lâmina 06 — Setenta anos em um minuto

**Tempo falado:** 42 s

![Lâmina 06](roteiro_narrado_iasdd_v10_biobyte_slides/slide_06.png)

### O que está escrito na lâmina

- **1950 · 1958** — Turing propõe o teste da imitação. Rosenblatt constrói o Perceptron, o primeiro neurônio que aprende.
- **Anos 1980** — a retropropagação torna possível treinar redes de várias camadas — e o ou-exclusivo deixa de ser barreira.
- **2012** — redes convolucionais vencem a competição de imagens por margem larga. Começa a era do aprendizado profundo.
- **2017 · 2022** — sai o artigo do Transformer. Cinco anos depois o ChatGPT leva modelos de linguagem ao uso geral.
- **2024 em diante** — o assunto passa a ser agentes: modelos que usam ferramentas, executam tarefas e produzem artefatos.

### O que a narradora fala

Um minuto de história. Mil novecentos e cinquenta: Turing propõe o teste da imitação. Cinquenta e oito: o Perceptron, o primeiro neurônio artificial que aprende. Anos oitenta: a retropropagação torna possível treinar redes de várias camadas. Dois mil e doze: as redes convolucionais vencem a competição de imagens e começa a era do aprendizado profundo. Dois mil e dezessete: o artigo do Transformer. Dois mil e vinte e dois: o ChatGPT leva os modelos de linguagem ao uso geral. E de dois mil e vinte e quatro em diante o assunto passa a ser agentes.

---

<div class="slide" id="slide-7"></div>

## Lâmina 07 — Aprendizado supervisionado e não supervisionado

**Tempo falado:** 38 s

![Lâmina 07](roteiro_narrado_iasdd_v10_biobyte_slides/slide_07.png)

### O que está escrito na lâmina

- *Aprendizado de máquina é, essencialmente, extrair conhecimento a partir de dados.*
- **Supervisionado** — você fornece entradas e as saídas esperadas. Existe um “professor” que ensina por exemplos; depois, o modelo responde a entradas novas.
- **Não supervisionado** — não há professor nem saída esperada. O modelo recebe só os dados e extrai deles a estrutura, agrupando o que é parecido.
- **A consequência prática** — o supervisionado exige dados rotulados — e rotular é o item mais caro de quase todo projeto clínico.

### O que a narradora fala

Aprendizado de máquina é extrair conhecimento a partir de dados. Há dois regimes. No supervisionado você fornece entradas e as saídas esperadas — é como se houvesse um professor ensinando por exemplos; depois de treinado, o modelo responde a uma entrada nova. No não supervisionado não existe professor: o modelo recebe só os dados e extrai deles a estrutura, agrupando o que é parecido. A consequência prática é financeira: o supervisionado exige dados rotulados, e rotular é o item mais caro de quase todo projeto clínico.

---

<div class="slide" id="slide-8"></div>

## Lâmina 08 — As seis etapas de um projeto de Machine Learning

**Tempo falado:** 39 s

![Lâmina 08](roteiro_narrado_iasdd_v10_biobyte_slides/slide_08.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Visualizar, Preparar, Conjuntos, Modelo, Treinar, Avaliar**
- **O roteiro é sempre o mesmo** — visualizar os dados, preparar os dados, definir os conjuntos, definir o modelo, efetuar o treinamento, avaliar.
- **Onde vai o tempo** — as duas primeiras etapas costumam consumir a maior parte do projeto. A modelagem é a parte curta.
- **O que vem a seguir** — vou passar por cada etapa dizendo o que se faz nela — é esse o roteiro que o notebook da demonstração executa.

### O que a narradora fala

Um projeto de aprendizado de máquina tem seis etapas, sempre as mesmas: visualizar os dados, preparar os dados, definir os conjuntos, definir o modelo, efetuar o treinamento e avaliar. Guardem uma proporção que surpreende quem está começando: as duas primeiras consomem a maior parte do tempo de um projeto real; a modelagem, que é a parte que todo mundo acha interessante, é a parte curta. Vou passar por cada etapa dizendo o que se faz — é esse o roteiro que o notebook da primeira demonstração executa.

---

<div class="slide" id="slide-9"></div>

## Lâmina 09 — Visualizar e preparar os dados

**Tempo falado:** 39 s

![Lâmina 09](roteiro_narrado_iasdd_v10_biobyte_slides/slide_09.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Visualizar, Preparar**
- **Visualizar** — olhar a distribuição de cada variável e a correlação entre elas, antes de qualquer modelo. É aqui que se descobre a coluna vazia na metade dos registros.
- **Limpar** — remover valores fora de contexto e preencher os ausentes.
- **Tratar os fatores** — descartar os desnecessários, decompor os que misturam informação, transformar, agregar quando fizer sentido.
- **Ajustar a escala** — levar tudo a uma faixa comparável. Se um fator vai de mil a um milhão e outro de zero a cem, muitos algoritmos não convergem.

### O que a narradora fala

As duas primeiras etapas. Visualizar é olhar a distribuição de cada variável e a correlação entre elas antes de qualquer modelo — é aqui que você descobre que uma coluna está vazia na metade dos registros. Preparar é limpar: remover valores fora de contexto, preencher os ausentes, descartar fatores desnecessários, decompor os que misturam informação, agregar quando fizer sentido. E ajustar a escala. Esse ponto é prático e importante: se um fator varia de mil a um milhão e outro de zero a cem, muitos algoritmos não convergem.

---

<div class="slide" id="slide-10"></div>

## Lâmina 10 — Definir os conjuntos e escolher o modelo

**Tempo falado:** 40 s

![Lâmina 10](roteiro_narrado_iasdd_v10_biobyte_slides/slide_10.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Conjuntos, Modelo**
- **A separação** — os dados são particionados aleatoriamente: setenta a setenta e cinco por cento para treinamento, o restante para teste.
- **A regra inegociável** — o modelo nunca pode ver, no treino, os dados com que vai ser avaliado. Quebrar isso produz um resultado ótimo e falso.
- **Escolher o modelo** — na prática não se escolhe no chute: a busca em grade testa vários algoritmos e várias combinações de parâmetros e devolve o melhor naquela base.

### O que a narradora fala

A terceira etapa separa os dados: tipicamente setenta a setenta e cinco por cento para treinamento, o restante para teste, sorteados aleatoriamente. E há uma regra inegociável: o modelo nunca pode ver, no treino, os dados com que vai ser avaliado. Quando isso é violado — e é violado com frequência, por descuido — o resultado sai excelente e é falso. A quarta etapa escolhe o modelo, e na prática não se escolhe no chute: a busca em grade testa vários algoritmos e várias combinações de parâmetros e devolve o melhor.

---

<div class="slide" id="slide-11"></div>

## Lâmina 11 — Treinar e avaliar: o sobreajuste

**Tempo falado:** 37 s

![Lâmina 11](roteiro_narrado_iasdd_v10_biobyte_slides/slide_11.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Treinar, Avaliar**
- **Treinar** — apresentar os dados ao modelo repetidas vezes. Cada passagem completa é uma época.
- **O gráfico que conta a história** — perda e acurácia por época, medidas nos dois conjuntos. É ele que mostra a hora de parar.
- **Sobreajuste** — a partir de certo ponto a acurácia sobe no treino e cai no teste. O modelo decorou e perdeu a generalização.
- **Subajuste** — o oposto: o modelo treinou de menos e não acerta nem no conjunto de treinamento.

### O que a narradora fala

Treinar é apresentar os dados ao modelo repetidas vezes; cada passagem completa é uma época. O gráfico de perda e acurácia por época mostra o problema central da área: o sobreajuste. A partir de certo ponto, a acurácia no treino continua subindo mas a do teste começa a cair. O modelo decorou e perdeu a capacidade de generalizar — não adianta treinar mais, adianta parar antes. O oposto também existe: o subajuste, quando o modelo treinou de menos e não acerta nem no treino.

---

<div class="slide" id="slide-12"></div>

## Lâmina 12 — Como se mede um classificador

**Tempo falado:** 44 s

![Lâmina 12](roteiro_narrado_iasdd_v10_biobyte_slides/slide_12.png)

### O que está escrito na lâmina

- *Avaliar não é olhar um número só.*
- **Matriz de confusão** — os quatro casos: acertos e erros de cada classe. Tudo o mais é derivado dela.
- **Sensibilidade e especificidade** — a fração de doentes que o modelo pegou, e a fração de sadios que ele deixou em paz.
- **Curva ROC e a área sob ela** — resumem o compromisso entre as duas ao longo de todos os limiares de decisão.
- **O alerta da saúde** — acurácia engana em base desbalanceada. Com prevalência de dois por cento, quem responde sempre “não” acerta noventa e oito por cento — e é inútil.

### O que a narradora fala

Avaliar não é olhar um número só. A matriz de confusão mostra acertos e erros de cada classe. Dela saem a sensibilidade, que é a fração de doentes que o modelo pegou, e a especificidade, a fração de sadios que ele deixou em paz. A curva ROC resume o compromisso entre as duas ao longo de todos os limiares. E fica o alerta que vale para a saúde inteira: acurácia engana em base desbalanceada. Com prevalência de dois por cento, um modelo que responde sempre “não” acerta noventa e oito por cento das vezes — e é inútil.

---

<div class="slide" id="slide-13"></div>

## Lâmina 13 — Com o que se trabalha

**Tempo falado:** 32 s

![Lâmina 13](roteiro_narrado_iasdd_v10_biobyte_slides/slide_13.png)

### O que está escrito na lâmina

- **Linguagem e ambiente** — Python. Jupyter Notebook no navegador, ou Google Colab, que é o Jupyter hospedado e não exige instalar nada.
- **Aprendizado clássico** — scikit-learn — todos os algoritmos dos próximos slides estão nela.
- **Aprendizado profundo** — TensorFlow e PyTorch. Placas gráficas aceleram a álgebra linear por trás do treinamento.
- **Dados e gráficos** — pandas e NumPy para manipular; matplotlib para visualizar.

### O que a narradora fala

O ferramental é praticamente padronizado. Python como linguagem, e o Jupyter Notebook como ambiente — ou o Google Colab, que é o Jupyter hospedado pela Google e não exige instalar nada. Para aprendizado clássico, o scikit-learn: todos os algoritmos dos próximos slides estão nele, e é uma linha de código para usar cada um. Para aprendizado profundo, TensorFlow e PyTorch. E, para os dados e os gráficos, pandas, NumPy e matplotlib.

---

<div class="slide" id="slide-14"></div>

## Lâmina 14 — K Vizinhos Mais Próximos

**Tempo falado:** 47 s

![Lâmina 14](roteiro_narrado_iasdd_v10_biobyte_slides/slide_14.png)

### O que está escrito na lâmina

- **Ideia central:** Este caso novo se parece com quais casos antigos?
- **Como funciona:** Guarda os exemplos. Para prever, busca os K mais próximos e devolve a classe da maioria — ou a média deles, se a saída for um número.
- **Para que se presta:** Classificar ou prever por semelhança direta, sem construir modelo nenhum.
- **Onde é mais adequado:** Bases pequenas, poucas variáveis, e quando se quer justificar a resposta mostrando os casos parecidos. Exige escala ajustada.

### O que a narradora fala

O primeiro é o mais simples de todos. A ideia cabe numa pergunta: este caso novo se parece com quais casos antigos? O algoritmo guarda os exemplos e, para prever, busca os K mais próximos e devolve a classe da maioria — ou a média deles, se a saída for um número. Presta-se a classificar por semelhança direta, sem construir modelo nenhum. É mais adequado em bases pequenas e quando você quer justificar a resposta mostrando os casos parecidos, o que em medicina é um argumento forte. Dois cuidados: as variáveis precisam estar na mesma escala, e o custo cresce com o tamanho da base.

---

<div class="slide" id="slide-15"></div>

## Lâmina 15 — Regressão Linear

**Tempo falado:** 37 s

![Lâmina 15](roteiro_narrado_iasdd_v10_biobyte_slides/slide_15.png)

### O que está escrito na lâmina

- **Ideia central:** Prever um número como combinação de fatores.
- **Como funciona:** Ajusta uma reta — ou um plano, quando há vários fatores — minimizando o erro pelo gradiente descendente.
- **Para que se presta:** Prever quantidades contínuas e medir quanto cada fator pesa no resultado.
- **Onde é mais adequado:** Relações aproximadamente lineares, quando interessa não só a previsão, mas o tamanho e o sinal do efeito de cada variável.

### O que a narradora fala

Regressão linear. A ideia é prever um número a partir de outros: com uma variável é uma reta, com várias, um plano. O ajuste é feito pelo gradiente descendente, que corrige os coeficientes até o erro parar de cair. Presta-se a prever quantidades contínuas — tempo de internação, dose, custo. É mais adequada quando a relação é aproximadamente linear e quando interessa não só a previsão, mas o tamanho e o sinal do efeito de cada fator, porque os coeficientes se leem diretamente.

---

<div class="slide" id="slide-16"></div>

## Lâmina 16 — Regressão Logística

**Tempo falado:** 45 s

![Lâmina 16](roteiro_narrado_iasdd_v10_biobyte_slides/slide_16.png)

### O que está escrito na lâmina

- **Ideia central:** Separar duas classes e dizer com que probabilidade.
- **Como funciona:** Encontra a fronteira que separa as classes — o limite de decisão — e passa o resultado pela função sigmoide, que comprime tudo entre zero e um.
- **Para que se presta:** Classificação binária com probabilidade, e com o efeito de cada fator interpretável.
- **Onde é mais adequado:** Escores de risco clínico. É o algoritmo mais usado em medicina, porque cada coeficiente se traduz em razão de chances.

### O que a narradora fala

Regressão logística. Apesar do nome, é classificação. Ela encontra a fronteira que separa as classes e passa o resultado por uma função sigmoide, que comprime qualquer valor entre zero e um. O que sai não é um rótulo seco: é uma probabilidade. Por isso ela se presta a escore de risco, onde não basta dizer se o paciente vai piorar, é preciso dizer com que chance. E é o algoritmo mais usado em medicina por um motivo prático: cada coeficiente se traduz em razão de chances, que é a linguagem da literatura clínica. A limitação é que a fronteira é sempre linear.

---

<div class="slide" id="slide-17"></div>

## Lâmina 17 — Árvore de Decisão

**Tempo falado:** 46 s

![Lâmina 17](roteiro_narrado_iasdd_v10_biobyte_slides/slide_17.png)

### O que está escrito na lâmina

- **Ideia central:** Uma sequência de perguntas de sim ou não.
- **Como funciona:** Procura a variável e o ponto de corte que melhor separam as classes, parte os dados ali, e repete dentro de cada pedaço.
- **Para que se presta:** Produzir regra legível — um caminho da raiz até a folha que um especialista consegue ler e contestar.
- **Onde é mais adequado:** Critérios e protocolos que precisam ser auditados. Lida bem com mistura de variáveis numéricas e categóricas.

### O que a narradora fala

Árvore de decisão. A ideia é uma sequência de perguntas de sim ou não: o algoritmo procura a variável e o ponto de corte que melhor separam as classes, parte os dados ali, e repete dentro de cada pedaço. Ela se presta ao que nenhum outro faz tão bem: produzir regra legível. Um médico consegue ler a árvore e discordar dela apontando o nó onde discorda — e isso, em domínio regulado, vale ouro. É mais adequada quando o critério precisa ser auditado. O defeito é conhecido: a árvore isolada tende a decorar o treino. É desse defeito que nasce o algoritmo seguinte.

---

<div class="slide" id="slide-18"></div>

## Lâmina 18 — Random Forest — Floresta Aleatória

**Tempo falado:** 38 s

![Lâmina 18](roteiro_narrado_iasdd_v10_biobyte_slides/slide_18.png)

### O que está escrito na lâmina

- **Ideia central:** Muitas árvores diferentes, decidindo juntas.
- **Como funciona:** Cada árvore é treinada numa variação da base e num sorteio de variáveis. A decisão final é a média — ou o voto — de todas elas.
- **Para que se presta:** Corrigir o sobreajuste da árvore isolada, e ranquear a importância de cada fator.
- **Onde é mais adequado:** Muitos fatores e relações não lineares, quando robustez importa mais do que ler uma regra única.

### O que a narradora fala

Floresta aleatória. A ideia é construir muitas árvores ligeiramente diferentes — cada uma treinada numa variação da base e num sorteio das variáveis — e decidir pela média, ou pelo voto, de todas. Cada árvore continua viciada, mas os vícios não são os mesmos e acabam se cancelando. Presta-se a classificação robusta quando há muitos fatores e relações não lineares, e entrega de brinde o ranqueamento da importância de cada variável, que é muito útil em pesquisa. O preço é a perda da regra única legível.

---

<div class="slide" id="slide-19"></div>

## Lâmina 19 — Máquina de Vetores de Suporte

**Tempo falado:** 41 s

![Lâmina 19](roteiro_narrado_iasdd_v10_biobyte_slides/slide_19.png)

### O que está escrito na lâmina

- **Ideia central:** Entre todas as fronteiras possíveis, a de maior margem.
- **Como funciona:** Procura o plano que separa as classes deixando a maior distância para os exemplos mais próximos — os vetores de suporte. Só eles determinam a fronteira.
- **Para que se presta:** Separar classes em espaços de muitas dimensões, inclusive com fronteiras curvas, usando funções de núcleo.
- **Onde é mais adequado:** Bases de tamanho moderado com muitas variáveis: expressão gênica, texto vetorizado, espectros.

### O que a narradora fala

Máquina de vetores de suporte. A ideia é escolher, entre todas as fronteiras que separam as classes, aquela que deixa a maior margem possível. Os pontos na borda dessa margem são os vetores de suporte, e são só eles que determinam a fronteira — o resto da base não conta. Com funções de núcleo, ela representa fronteiras curvas. Presta-se a separar classes em espaços de muitas dimensões, e é mais adequada em bases de tamanho moderado com muitas variáveis, como expressão gênica ou texto vetorizado. Em base muito grande, o treinamento fica lento.

---

<div class="slide" id="slide-20"></div>

## Lâmina 20 — K-Means — K Médias

**Tempo falado:** 37 s

![Lâmina 20](roteiro_narrado_iasdd_v10_biobyte_slides/slide_20.png)

### O que está escrito na lâmina

- **Ideia central:** Achar os grupos sem que ninguém diga quais são.
- **Como funciona:** Sorteia K centros; atribui cada ponto ao centro mais próximo; recalcula cada centro como a média do seu grupo; repete até a atribuição não mudar mais.
- **Para que se presta:** Descobrir perfis e segmentos que ninguém rotulou — classificação sem treinamento.
- **Onde é mais adequado:** Exploração inicial dos dados. Exige escolher K de antemão e supõe grupos aproximadamente esféricos e de tamanho parecido.

### O que a narradora fala

K médias, o único não supervisionado da lista. Aqui ninguém diz quais são os grupos: o algoritmo os descobre. Ele sorteia K centros, atribui cada ponto ao centro mais próximo, recalcula cada centro como a média do seu grupo, e repete até a atribuição parar de mudar. Presta-se a descobrir perfis que ninguém rotulou: estratos de pacientes, padrões de uso. É mais adequado como exploração inicial. Dois limites: você escolhe o K de antemão, e ele supõe grupos aproximadamente esféricos e de tamanho parecido.

---

<div class="slide" id="slide-21"></div>

## Lâmina 21 — O pipeline de Machine Learning, do início ao fim

**▶ VÍDEO — 8 minutos.** o notebook executando as seis etapas sobre uma base clínica

![Lâmina 21](roteiro_narrado_iasdd_v10_biobyte_slides/slide_21.png)

### O que está escrito na lâmina

- **▶ VÍDEO · 8 minutos** — o notebook executando as seis etapas sobre uma base clínica
- **1.** Carregar a base e visualizar as variáveis e suas correlações
- **2.** Preparar: valores ausentes, fatores descartados, escala ajustada
- **3.** Separar treino e teste, e mostrar por que a separação importa
- **4.** Busca em grade comparando os algoritmos das lâminas anteriores
- **5.** Treinar e ler o gráfico de perda por época — o ponto do sobreajuste
- **6.** Avaliar: matriz de confusão, sensibilidade, especificidade e a curva ROC

### O que a narradora fala

Agora o primeiro vídeo. São oito minutos com o notebook executando exatamente as seis etapas que acabamos de ver, sobre uma base clínica real: carregar e visualizar, preparar, separar os conjuntos, comparar os algoritmos por busca em grade, treinar acompanhando o gráfico por época, e avaliar com matriz de confusão e curva ROC. É esse mesmo notebook que fica com vocês para refazer em casa — e eu sugiro refazer trocando o algoritmo, porque é trocando que se entende o que cada um faz.

### Produção deste vídeo

Gravar 8 minutos cobrindo, nesta ordem:

1. Carregar a base e visualizar as variáveis e suas correlações
2. Preparar: valores ausentes, fatores descartados, escala ajustada
3. Separar treino e teste, e mostrar por que a separação importa
4. Busca em grade comparando os algoritmos das lâminas anteriores
5. Treinar e ler o gráfico de perda por época — o ponto do sobreajuste
6. Avaliar: matriz de confusão, sensibilidade, especificidade e a curva ROC

---

<div class="slide" id="slide-22"></div>

## Lâmina 22 — Inteligência Artificial na saúde

**Tempo falado:** 21 s

![Lâmina 22](roteiro_narrado_iasdd_v10_biobyte_slides/slide_22.png)

### O que está escrito na lâmina

- **BLOCO 2 — Inteligência Artificial na saúde**
- *Três frentes: prognóstico e risco, diagnóstico, e tratamento.*

### O que a narradora fala

O segundo bloco leva esses algoritmos para o terreno de vocês. A inteligência artificial entra na saúde por três frentes bem distintas: prognóstico e avaliação de risco, diagnóstico, e tratamento. Cada uma usa algoritmos diferentes e, o que é menos óbvio, mede o sucesso de maneira diferente.

---

<div class="slide" id="slide-23"></div>

## Lâmina 23 — Prognóstico e avaliação de risco

**Tempo falado:** 40 s

![Lâmina 23](roteiro_narrado_iasdd_v10_biobyte_slides/slide_23.png)

### O que está escrito na lâmina

- *A pergunta: qual a chance de um desfecho ruim — e em quanto tempo?*
- **Escore de risco** — combina os fatores do paciente num número comparável entre pacientes. É o instrumento clássico da área.
- **Análise de sobrevivência** — quando o tempo importa: Kaplan-Meier estima a curva de sobrevivência; o modelo de Cox estima quanto cada fator multiplica o risco.
- **Árvores e florestas de sobrevivência** — quando a relação não é proporcional nem linear, substituem o Cox mantendo a leitura por fator.
- **Como se avalia** — índice de concordância no lugar da acurácia: o modelo ordena corretamente quem adoece antes?

### O que a narradora fala

A primeira frente é prognóstico: qual a chance de um desfecho ruim, e em quanto tempo. O instrumento clássico é o escore de risco, que combina os fatores do paciente num número comparável. Quando o tempo importa, usa-se análise de sobrevivência: a curva de Kaplan-Meier estima a probabilidade de sobreviver ao longo do tempo, e o modelo de Cox estima quanto cada fator multiplica esse risco. E a avaliação muda de natureza: no lugar da acurácia, o índice de concordância, que pergunta se o modelo ordena corretamente quem adoece antes.

---

<div class="slide" id="slide-24"></div>

## Lâmina 24 — Diagnóstico

**Tempo falado:** 41 s

![Lâmina 24](roteiro_narrado_iasdd_v10_biobyte_slides/slide_24.png)

### O que está escrito na lâmina

- *Três gerações convivendo no mesmo hospital.*
- **Sistemas especialistas** — regras escritas junto com o especialista. Explicam a conclusão passo a passo — mas não aprendem nada sozinhos.
- **Aprendizado sobre dados clínicos** — classificação a partir de exame, sinal vital e história. É o território das árvores, das florestas e da regressão logística.
- **Diagnóstico por imagem** — redes convolucionais classificam e segmentam: radiologia, patologia, dermatologia, oftalmologia.
- **Interpretação, obrigatória** — mapas de saliência mostram em que região a rede se apoiou. Sem isso, o laudo não é defensável.

### O que a narradora fala

A segunda frente é diagnóstico, e tem três gerações convivendo no mesmo hospital. Os sistemas especialistas, feitos de regras escritas junto com o especialista: explicam a conclusão passo a passo, mas não aprendem sozinhos. O aprendizado sobre dados clínicos estruturados — exame, sinal vital, história — que é o território das árvores, das florestas e da regressão logística. E o diagnóstico por imagem, com redes convolucionais. Nesse último caso a interpretação é obrigatória: os mapas de saliência mostram em que região a rede se apoiou, e sem isso o laudo não é defensável.

---

<div class="slide" id="slide-25"></div>

## Lâmina 25 — Tratamento

**Tempo falado:** 42 s

![Lâmina 25](roteiro_narrado_iasdd_v10_biobyte_slides/slide_25.png)

### O que está escrito na lâmina

- **Escolha de conduta** — modelos que estimam a resposta esperada a cada opção terapêutica, a partir do perfil do paciente.
- **Dose e ajuste** — previsão de valor contínuo a partir de peso, função renal e resposta anterior.
- **Resposta a questões médicas** — é aqui que entram os modelos de linguagem — e onde citar a evidência deixa de ser opcional e vira requisito.
- **O limite** — o modelo apoia a decisão. A responsabilidade clínica não se transfere para ele.

### O que a narradora fala

A terceira frente é tratamento. Modelos que estimam a resposta esperada a cada conduta possível. Modelos que preveem dose a partir de peso, função renal e resposta anterior. E resposta a questões médicas, que é onde entram os modelos de linguagem — e onde citar a evidência vira requisito, porque uma resposta clínica sem fonte não pode ser conferida. Fica o limite, que vale para as três frentes: o modelo apoia a decisão; a responsabilidade clínica não se transfere. Isso não é retórica — é o que define como o sistema tem de ser construído.

---

<div class="slide" id="slide-26"></div>

## Lâmina 26 — Classificação e apoio à decisão em saúde

**▶ VÍDEO — 8 minutos.** um escore de risco construído e avaliado do jeito certo

![Lâmina 26](roteiro_narrado_iasdd_v10_biobyte_slides/slide_26.png)

### O que está escrito na lâmina

- **▶ VÍDEO · 8 minutos** — um escore de risco construído e avaliado do jeito certo
- **1.** A base clínica e o desfecho que se quer prever
- **2.** Por que a acurácia mente aqui — e o que olhar no lugar dela
- **3.** Regressão logística: o coeficiente virando razão de chances
- **4.** Árvore de decisão: a regra que o clínico lê e contesta
- **5.** Curva de sobrevivência e o efeito de cada fator no tempo
- **6.** O que o modelo não pode decidir sozinho

### O que a narradora fala

O segundo vídeo mostra um escore de risco sendo construído e avaliado do jeito certo: a base, o desfecho, o motivo pelo qual a acurácia mente nesse cenário, a regressão logística com o coeficiente virando razão de chances, a árvore de decisão produzindo a regra que o clínico lê, e a curva de sobrevivência. Termina no ponto que mais importa: o que o modelo não pode decidir sozinho.

### Produção deste vídeo

Gravar 8 minutos cobrindo, nesta ordem:

1. A base clínica e o desfecho que se quer prever
2. Por que a acurácia mente aqui — e o que olhar no lugar dela
3. Regressão logística: o coeficiente virando razão de chances
4. Árvore de decisão: a regra que o clínico lê e contesta
5. Curva de sobrevivência e o efeito de cada fator no tempo
6. O que o modelo não pode decidir sozinho

---

<div class="slide" id="slide-27"></div>

## Lâmina 27 — Deep Learning e Transfer Learning

**Tempo falado:** 16 s

![Lâmina 27](roteiro_narrado_iasdd_v10_biobyte_slides/slide_27.png)

### O que está escrito na lâmina

- **BLOCO 3 — Deep Learning e Transfer Learning**
- *Do neurônio artificial às redes convolucionais — e como reaproveitar uma rede já treinada.*

### O que a narradora fala

O terceiro bloco é aprendizado profundo. Vamos do neurônio artificial até as redes convolucionais que fazem diagnóstico por imagem, e terminamos na técnica que torna tudo isso viável dentro de um hospital: a transferência de aprendizado.

---

<div class="slide" id="slide-28"></div>

## Lâmina 28 — Do neurônio artificial à rede de camadas

**Tempo falado:** 35 s

![Lâmina 28](roteiro_narrado_iasdd_v10_biobyte_slides/slide_28.png)

### O que está escrito na lâmina

- **O neurônio** — soma as entradas multiplicadas por pesos e passa o resultado por uma função de ativação.
- **O limite de um só** — um neurônio isolado separa apenas o que é linearmente separável — não consegue nem representar o ou-exclusivo.
- **A saída: camadas** — empilhar neurônios resolve o ou-exclusivo e, por extensão, fronteiras de qualquer formato.
- **A rede de múltiplas camadas** — um nó de entrada por fator, uma ou mais camadas intermediárias, um nó de saída por classe.

### O que a narradora fala

Aprendizado profundo começa num objeto muito simples. O neurônio artificial soma as entradas multiplicadas por pesos e passa o resultado por uma função de ativação. Um neurônio sozinho tem um limite conhecido desde os anos sessenta: só separa o que é linearmente separável, e não consegue representar nem o ou-exclusivo. Esse limite quase matou a área. A saída foi empilhar neurônios em camadas: com uma camada intermediária o ou-exclusivo sai, e por extensão saem fronteiras de qualquer formato.

---

<div class="slide" id="slide-29"></div>

## Lâmina 29 — Como a rede aprende: retropropagação

**Tempo falado:** 37 s

![Lâmina 29](roteiro_narrado_iasdd_v10_biobyte_slides/slide_29.png)

### O que está escrito na lâmina

- **Para frente** — cada camada calcula sua saída e passa adiante, até a rede produzir uma resposta. Compara-se com a esperada e mede-se o erro.
- **Para trás** — partindo da saída, distribui-se a responsabilidade pelo erro camada a camada, corrigindo cada peso na direção que o reduz.
- **O motor** — é o gradiente descendente outra vez — agora aplicado em cadeia, da última camada até a primeira.
- **O que não tem fórmula** — quantos neurônios pôr nas camadas intermediárias. Existem regras de bolso para o ponto de partida; o resto é experimentação.

### O que a narradora fala

A retropropagação tem dois movimentos. No movimento para frente, cada camada calcula sua saída e passa adiante até a rede produzir uma resposta; compara-se com a esperada e mede-se o erro. No movimento para trás, parte-se da saída e distribui-se a responsabilidade por aquele erro camada a camada, corrigindo cada peso na direção que o reduz — é o gradiente descendente outra vez, aplicado em cadeia. Repete-se por muitas épocas. E quantos neurônios pôr nas camadas intermediárias não tem fórmula fechada: é experimentação.

---

<div class="slide" id="slide-30"></div>

## Lâmina 30 — Redes convolucionais: o caminho da imagem

**Tempo falado:** 38 s

![Lâmina 30](roteiro_narrado_iasdd_v10_biobyte_slides/slide_30.png)

### O que está escrito na lâmina

- *Ligar cada pixel a cada neurônio é inviável — uma imagem pequena já gera milhões de pesos.*
- **A camada convolucional** — um filtro pequeno varre a imagem inteira procurando um padrão local: borda, textura, contorno. O mesmo filtro vale para a imagem toda.
- **A hierarquia** — as primeiras camadas acham bordas; as seguintes, formas; as últimas, objetos.
- **As camadas de agrupamento** — reduzem a resolução mantendo o que importa, e dão tolerância a deslocamento.
- **O resultado** — é essa arquitetura que sustenta radiologia, patologia e a segmentação de lesões.

### O que a narradora fala

Para imagem, a rede densa não serve: ligar cada pixel a cada neurônio gera milhões de pesos e a rede não generaliza. A solução é a camada convolucional. Um filtro pequeno varre a imagem inteira procurando um padrão local — borda, textura, contorno — e o mesmo filtro vale para toda a imagem, o que reduz brutalmente o número de pesos. Empilhando camadas aparece uma hierarquia: as primeiras acham bordas, as seguintes formas, as últimas objetos. É essa arquitetura que sustenta o diagnóstico por imagem.

---

<div class="slide" id="slide-31"></div>

## Lâmina 31 — Transfer Learning: reaproveitar uma rede treinada

**Tempo falado:** 41 s

![Lâmina 31](roteiro_narrado_iasdd_v10_biobyte_slides/slide_31.png)

### O que está escrito na lâmina

- *Treinar do zero exige milhões de imagens rotuladas. Reaproveitar exige algumas centenas.*

```python
base = ResNet50(weights="IMAGENET1K_V2", include_top=False)
base.trainable = False          # congela o que já foi aprendido

model = Sequential([
    base,                       # bordas, texturas, formas
    GlobalAveragePooling2D(),
    Dropout(0.3),               # reduz o sobreajuste
    Dense(2, activation="softmax")   # a SUA decisão clínica
])
model.fit(images, labels, epochs=10)
```

- **Ao lado do código:** A rede pré-treinada já sabe reconhecer borda, textura e forma — isso não depende do domínio. Você congela essa parte, troca a camada final pelas suas classes e treina só ela. Depois, se quiser mais desempenho, descongela algumas camadas finais e faz o ajuste fino. Modelos usuais: ResNet, VGG, DenseNet.

### O que a narradora fala

E aqui está o que torna tudo isso viável num hospital. Treinar uma rede do zero exige milhões de imagens rotuladas, que ninguém tem. A transferência de aprendizado resolve: pega-se uma rede já treinada num acervo enorme de imagens genéricas, congelam-se os pesos, remove-se a camada final e acrescenta-se uma camada nova com as classes do seu problema. A rede pré-treinada já sabe reconhecer borda, textura e forma, e isso não depende do domínio; você só ensina a decisão clínica. Com algumas centenas de imagens você chega perto do que exigiria milhões.

---

<div class="slide" id="slide-32"></div>

## Lâmina 32 — Treinamento e Transfer Learning

**▶ VÍDEO — 8 minutos.** a mesma tarefa treinada do zero e por reaproveitamento, lado a lado

![Lâmina 32](roteiro_narrado_iasdd_v10_biobyte_slides/slide_32.png)

### O que está escrito na lâmina

- **▶ VÍDEO · 8 minutos** — a mesma tarefa treinada do zero e por reaproveitamento, lado a lado
- **1.** A base de imagens e o que se quer classificar
- **2.** Treinar do zero: a curva que não sobe e o motivo
- **3.** Carregar a rede pré-treinada e congelar os pesos
- **4.** Trocar a camada final pelas classes do problema
- **5.** A curva agora — e quantas imagens bastaram
- **6.** Onde a rede olhou: o mapa de saliência sobre a imagem

### O que a narradora fala

O terceiro vídeo põe as duas coisas lado a lado: a mesma tarefa treinada do zero e por reaproveitamento. Você vê a curva que não sobe quando se treina do zero com poucos dados, e vê a mesma curva depois de carregar a rede pré-treinada. No fim, o mapa de saliência mostrando em que região da imagem a rede se apoiou para decidir.

### Produção deste vídeo

Gravar 8 minutos cobrindo, nesta ordem:

1. A base de imagens e o que se quer classificar
2. Treinar do zero: a curva que não sobe e o motivo
3. Carregar a rede pré-treinada e congelar os pesos
4. Trocar a camada final pelas classes do problema
5. A curva agora — e quantas imagens bastaram
6. Onde a rede olhou: o mapa de saliência sobre a imagem

---

<div class="slide" id="slide-33"></div>

## Lâmina 33 — Modelos de linguagem e Transformer

**Tempo falado:** 22 s

![Lâmina 33](roteiro_narrado_iasdd_v10_biobyte_slides/slide_33.png)

### O que está escrito na lâmina

- **BLOCO 4 — Modelos de linguagem e Transformer**
- *O que é um modelo de linguagem, de onde veio o Transformer, e o que a escala trouxe junto.*

### O que a narradora fala

O quarto bloco muda de terreno. Saímos do classificador que responde sim ou não e entramos nos modelos de linguagem. Vamos ver o que eles são de fato, de onde veio a arquitetura que os viabilizou, e o que a escala trouxe junto — inclusive o que ela não resolveu.

---

<div class="slide" id="slide-34"></div>

## Lâmina 34 — O que é um modelo de linguagem

**Tempo falado:** 44 s

![Lâmina 34](roteiro_narrado_iasdd_v10_biobyte_slides/slide_34.png)

### O que está escrito na lâmina

- *Um modelo que estima qual é o próximo pedaço de texto, dado todo o texto anterior.*
- **O token** — a unidade não é a palavra, é o token — um pedaço de palavra. “Hemocultura” pode virar três ou quatro tokens.
- **O treinamento** — prever o próximo token sobre um corpus imenso. Nenhum rótulo humano: o próprio texto é a resposta.
- **A geração** — o modelo devolve uma distribuição de probabilidade; sorteia-se um token, acrescenta-se ao texto e repete-se.
- **O que isso implica** — ele não consulta uma base de fatos. Ele produz a continuação mais provável — e é por isso que inventa com fluência.

### O que a narradora fala

Um modelo de linguagem é um estimador: dado todo o texto anterior, qual é o próximo pedaço de texto. A unidade não é a palavra, é o token — “hemocultura” pode virar três ou quatro tokens. O treinamento consiste em prever o próximo token sobre um corpus imenso, e não exige rótulo humano: o próprio texto é a resposta. Tirem daqui a consequência mais importante: ele não consulta uma base de fatos, ele produz a continuação mais provável. É por isso que ele inventa com fluência — e por que vamos precisar de recuperação de documentos e de portões determinísticos.

---

<div class="slide" id="slide-35"></div>

## Lâmina 35 — De onde veio o Transformer

**Tempo falado:** 42 s

![Lâmina 35](roteiro_narrado_iasdd_v10_biobyte_slides/slide_35.png)

### O que está escrito na lâmina

- *“Attention Is All You Need” · Vaswani et al. · Google Brain e University of Toronto · 2017*
- **Antes** — redes recorrentes e LSTM processavam a sequência passo a passo: dependências longas se perdiam e o treinamento quase não paralelizava.
- **A contribuição** — a atenção permite que cada token se relacione diretamente com todos os outros, sem passar pela recorrência.
- **O impacto** — com o treinamento paralelo, escalar deixou de ser impossível. É essa arquitetura que sustenta todos os modelos de hoje.

### O que a narradora fala

A arquitetura tem data e endereço: o artigo “Attention Is All You Need”, de Vaswani e colegas, do Google Brain e da Universidade de Toronto, de dois mil e dezessete. Antes dele, as redes recorrentes processavam a sequência passo a passo: as dependências longas se perdiam e o treinamento quase não paralelizava, o que punha um teto no tamanho dos modelos. A contribuição foi a atenção: cada token passa a se relacionar diretamente com todos os outros. E o efeito decisivo foi o colateral — como tudo virou paralelizável, escalar deixou de ser impossível.

---

<div class="slide" id="slide-36"></div>

## Lâmina 36 — Anatomia: consulta, chave e valor

**Tempo falado:** 40 s

![Lâmina 36](roteiro_narrado_iasdd_v10_biobyte_slides/slide_36.png)

### O que está escrito na lâmina

- **Q, K e V** — cada token faz uma pergunta (consulta), todos anunciam o que têm (chave), e a semelhança entre as duas decide de quem ele copia informação (valor).
- **Múltiplas cabeças** — várias relações capturadas em paralelo — cada cabeça olhando um aspecto diferente da mesma frase.
- **O ponto de engenharia** — a atenção é quadrática no tamanho da entrada. Custo por token, tamanho da janela e toda a economia de contexto nascem dessa quadrática.

### O que a narradora fala

A anatomia em uma frase. Cada token faz uma pergunta — a consulta. Todos anunciam o que têm — a chave. A semelhança entre as duas decide de quem esse token copia informação — o valor. Isso acontece em várias cabeças ao mesmo tempo, cada uma capturando um aspecto diferente da mesma frase. E guardem o ponto de engenharia: a atenção é quadrática no tamanho da entrada — dobrar o texto quadruplica a conta. Custo por token, limite de janela e toda a economia de contexto nascem dessa quadrática.

---

<div class="slide" id="slide-37"></div>

## Lâmina 37 — Escala, e o que veio com ela

**Tempo falado:** 42 s

![Lâmina 37](roteiro_narrado_iasdd_v10_biobyte_slides/slide_37.png)

### O que está escrito na lâmina

- **O que a escala trouxe** — capacidades que ninguém programou: seguir instrução, traduzir, resumir, escrever código, raciocinar em passos.
- **Mistura de especialistas** — modelos enormes que ativam só uma fração dos parâmetros por token — trilhões de parâmetros totais, dezenas de bilhões ativos.
- **O que a escala não resolveu** — a invenção confiante, a sensibilidade à forma do pedido e a ausência de garantia de correção.
- **A consequência de projeto** — se o modelo não garante correção, a garantia tem de vir de fora dele. Esse é o fio que percorre o resto da palestra.

### O que a narradora fala

O que a escala trouxe foi surpreendente: capacidades que ninguém programou — seguir instrução, traduzir, resumir, escrever código, raciocinar em passos. Elas aparecem à medida que o modelo cresce. A novidade recente é a mistura de especialistas: modelos com trilhões de parâmetros totais que ativam só dezenas de bilhões por token. Mas registrem o que a escala não resolveu: a invenção confiante e a ausência de qualquer garantia de correção. E daí sai a consequência que percorre o resto da palestra: se o modelo não garante correção, a garantia tem de vir de fora dele.

---

<div class="slide" id="slide-38"></div>

## Lâmina 38 — Inferência: os parâmetros que importam

**Tempo falado:** 42 s

![Lâmina 38](roteiro_narrado_iasdd_v10_biobyte_slides/slide_38.png)

### O que está escrito na lâmina

- *A mesma chamada, dois resultados diferentes — e a escolha não é de gosto.*

```python
# código, extração, classificação: determinístico
resp = modelo.gerar(prompt, temperatura=0.0)

# exploração de hipóteses, redação: criativo
resp = modelo.gerar(prompt, temperatura=1.0)
```

- **Ao lado do código:** Temperatura e top-p regulam o sorteio do próximo token. O cache de chaves-valores reaproveita contas já feitas — menos custo e menos espera. A quantização reduz a precisão dos pesos para o modelo caber na memória de vídeo. Regra prática: código e extração estruturada pedem temperatura baixa; exploração pede o contrário.

### O que a narradora fala

Na hora de usar, quatro parâmetros fazem quase toda a diferença. A temperatura e o top-p regulam o sorteio do próximo token: temperatura zero deixa a saída praticamente determinística, temperatura alta abre o leque. O cache de chaves-valores reaproveita contas já feitas entre chamadas, e derruba custo e espera. A quantização reduz a precisão dos pesos para o modelo caber na memória de vídeo que você tem. E fica a regra prática: código e extração estruturada pedem temperatura baixa; exploração de hipóteses pede o contrário. É a mesma chamada — o resultado é outro.

---

<div class="slide" id="slide-39"></div>

## Lâmina 39 — Panorama: modelos proprietários

**Tempo falado:** 38 s

![Lâmina 39](roteiro_narrado_iasdd_v10_biobyte_slides/slide_39.png)

### O que está escrito na lâmina


| Modelo | Fabricante | SWE-bench Verified | Fonte da medição |
|---|---|---|---|
| GPT-5.6 Sol | OpenAI | ~96% | Vals AI (independente) |
| Claude Fable 5 | Anthropic | ~95% | medição independente |
| Gemini 3.1 Pro | Google | agrupamento superior | — |

- **Nota na lâmina:** SWE-bench Verified mede correção de defeitos reais de software. Ressalva obrigatória: o número do fabricante e o de uma medição independente divergem, às vezes muito — cite sempre a fonte e a data.

### O que a narradora fala

Um panorama rápido dos proprietários, com uma ressalva que eu peço que levem a sério. O teste citado mede correção de defeitos reais de software, e os três modelos de ponta estão hoje num patamar parecido. A ressalva: o número do fabricante e o de uma medição independente divergem, às vezes muito. Quando forem citar desempenho de modelo num documento ou numa decisão de compra, citem a fonte e a data — sem isso o número não significa nada, e essa tabela envelhece em semanas.

---

<div class="slide" id="slide-40"></div>

## Lâmina 40 — Panorama: modelos abertos

**Tempo falado:** 41 s

![Lâmina 40](roteiro_narrado_iasdd_v10_biobyte_slides/slide_40.png)

### O que está escrito na lâmina


| Modelo | Arquitetura | Contexto | Licença | Onde roda |
|---|---|---|---|---|
| Kimi K3 | 2,8T / 104B ativos | 1M | pesos abertos | infraestrutura séria |
| DeepSeek-V4-Pro | 1,6T / 49B ativos | 1M | MIT | cluster |
| DeepSeek-V4-Flash | 284B / 13B ativos | 1M | MIT | servidor médio |
| Qwen3.8-27B | denso 27,8B · multimodal | 262K | Apache-2.0 | 24 GB de vídeo |
| MiniMax M3 | 428B / 23B ativos | 1M | comunitária ⚠ | ver a licença |

- **Nota na lâmina:** Alerta jurídico: “pesos abertos” não é a mesma coisa que “código aberto”. MIT e Apache-2.0 são livres para uso comercial; licenças comunitárias podem não ser. Em saúde, isso decide se o modelo pode rodar dentro do hospital com o dado do paciente.

### O que a narradora fala

E os abertos, que para vocês interessam mais por um motivo específico: dado de paciente que não pode sair do hospital exige modelo rodando dentro do hospital. A linha que eu destaco é a do Qwen de vinte e sete bilhões: denso, multimodal, licença Apache, e roda numa placa de vinte e quatro gigabytes — uma máquina que o setor de informática de vocês consegue comprar. É esse o modelo do nosso laboratório. E o alerta jurídico: “pesos abertos” não é “código aberto”. Leiam a licença antes de projetar em cima do modelo.

---

<div class="slide" id="slide-41"></div>

## Lâmina 41 — A escada da adaptação

**Tempo falado:** 55 s

![Lâmina 41](roteiro_narrado_iasdd_v10_biobyte_slides/slide_41.png)

### O que está escrito na lâmina

- *Quatro degraus, do mais barato ao mais caro. Suba um degrau só quando o anterior não bastar.*
- **1 · Instrução** — escrever melhor o pedido e dar exemplos. Custo quase zero, e resolve mais do que se imagina.
- **2 · Contexto** — trazer para dentro do pedido o documento certo — protocolo, norma, prontuário. É o bloco seis.
- **3 · Ferramentas** — deixar o modelo consultar o sistema real em vez de lembrar. É o bloco cinco.
- **4 · Ajuste fino** — mudar os pesos. Só quando se quer ensinar um formato ou um jargão que não cabe no pedido.

### O que a narradora fala

Quando o modelo não faz o que você quer existe uma escada, e quase todo mundo começa pelo degrau errado. O primeiro é a instrução: escrever melhor o pedido e dar exemplos; custa quase nada e resolve mais do que se imagina. O segundo é o contexto: trazer para dentro do pedido o protocolo, a norma, o documento certo. O terceiro é ferramenta: deixar o modelo consultar o sistema real em vez de lembrar. E só o quarto é ajuste fino, que muda os pesos — hoje viável com LoRA e QLoRA, que cabem numa única placa. Subam um degrau apenas quando o anterior comprovadamente não bastar: ajuste fino feito cedo é dinheiro queimado, e ele ensina formato e jargão, não fato novo.

---

<div class="slide" id="slide-42"></div>

## Lâmina 42 — Tokens, atenção e geração, por dentro

**▶ VÍDEO — 8 minutos.** abrindo o modelo para ver o que ele faz a cada passo

![Lâmina 42](roteiro_narrado_iasdd_v10_biobyte_slides/slide_42.png)

### O que está escrito na lâmina

- **▶ VÍDEO · 8 minutos** — abrindo o modelo para ver o que ele faz a cada passo
- **1.** O tokenizador: a frase clínica virando tokens
- **2.** O mapa de atenção: a que cada token está olhando
- **3.** A distribuição do próximo token, antes do sorteio
- **4.** Temperatura zero e temperatura alta, sobre o mesmo pedido
- **5.** A janela de contexto enchendo — e o que acontece quando estoura
- **6.** Uma invenção confiante, flagrada e explicada

### O que a narradora fala

O quarto vídeo abre o modelo. Vocês vão ver o tokenizador quebrando uma frase clínica, o mapa de atenção mostrando a que cada token está olhando, a distribuição do próximo token antes do sorteio, e o mesmo pedido saindo diferente com temperatura zero e temperatura alta. E termina com uma invenção confiante sendo flagrada — para que ninguém saia daqui achando que fluência é sinal de correção.

### Produção deste vídeo

Gravar 8 minutos cobrindo, nesta ordem:

1. O tokenizador: a frase clínica virando tokens
2. O mapa de atenção: a que cada token está olhando
3. A distribuição do próximo token, antes do sorteio
4. Temperatura zero e temperatura alta, sobre o mesmo pedido
5. A janela de contexto enchendo — e o que acontece quando estoura
6. Uma invenção confiante, flagrada e explicada

---

<div class="slide" id="slide-43"></div>

## Lâmina 43 — Agentes

**Tempo falado:** 18 s

![Lâmina 43](roteiro_narrado_iasdd_v10_biobyte_slides/slide_43.png)

### O que está escrito na lâmina

- **BLOCO 5 — Agentes**
- *Entrada, tarefa e saída; contexto, memória e ferramentas; o ciclo agêntico e a composição.*

### O que a narradora fala

Quinto bloco: agentes. Vamos sair do modelo que responde e chegar ao programa que faz. Entrada, tarefa e saída; contexto, memória e ferramentas; o ciclo que o agente executa; e como se compõem vários deles — inclusive quando isso não compensa.

---

<div class="slide" id="slide-44"></div>

## Lâmina 44 — De modelo para agente

**Tempo falado:** 39 s

![Lâmina 44](roteiro_narrado_iasdd_v10_biobyte_slides/slide_44.png)

### O que está escrito na lâmina

- *Um modelo responde. Um agente age — e o que muda é bem pouco código.*
- **O modelo** — recebe texto e devolve texto. Não consulta nada, não altera nada, não lembra de nada entre chamadas.
- **O agente** — recebe um objetivo, escolhe ações, executa-as por meio de ferramentas, observa o resultado e decide o passo seguinte.
- **A peça nova** — o laço. E, com ele, a capacidade de causar efeito no mundo — inclusive efeito indesejado.

### O que a narradora fala

A diferença entre modelo e agente é menor do que o vocabulário sugere. Um modelo recebe texto e devolve texto: não consulta nada, não altera nada, não lembra de nada entre chamadas. Um agente recebe um objetivo, escolhe uma ação, executa-a por meio de uma ferramenta, observa o resultado e decide o passo seguinte. A peça nova é o laço. E com o laço vem a capacidade de causar efeito no mundo — inclusive efeito indesejado, que é o motivo pelo qual o resto deste bloco existe.

---

<div class="slide" id="slide-45"></div>

## Lâmina 45 — Definição operacional, sem misticismo

**Tempo falado:** 40 s

![Lâmina 45](roteiro_narrado_iasdd_v10_biobyte_slides/slide_45.png)

### O que está escrito na lâmina

- **Objetivo** — o que se quer obtido, escrito de forma verificável. Sem isso, não há como dizer se o agente terminou.
- **Contexto** — o que ele sabe nesta execução: a instrução, os documentos trazidos, o estado do sistema.
- **Ferramentas** — o que ele pode fazer. Cada ferramenta tem nome, parâmetros e um contrato de retorno.
- **Memória** — o que atravessa execuções. Distinga sempre memória de contexto — confundi-las é fonte de bug sutil.
- **Critério de parada** — quando ele para. Por sucesso, por limite de passos, ou por falha declarada.

### O que a narradora fala

A definição operacional, sem misticismo: um agente tem cinco peças. Um objetivo escrito de forma verificável, sem o qual não há como dizer se ele terminou. Um contexto, que é o que ele sabe nesta execução. Um conjunto de ferramentas, que é o que ele pode fazer. Uma memória, que é o que atravessa execuções — e eu insisto em distinguir memória de contexto, porque confundi-las é fonte de defeito sutil. E um critério de parada. Se alguma dessas cinco estiver faltando no projeto de vocês, ele vai falhar em produção.

---

<div class="slide" id="slide-46"></div>

## Lâmina 46 — O laço agêntico

**Tempo falado:** 43 s

![Lâmina 46](roteiro_narrado_iasdd_v10_biobyte_slides/slide_46.png)

### O que está escrito na lâmina

- **1 · Pensar** — o modelo recebe o objetivo e o estado, e decide qual é a próxima ação.
- **2 · Pedir a ferramenta** — ele não executa nada. Ele emite um pedido: este nome de ferramenta, com estes argumentos.
- **3 · O programa executa** — quem chama a ferramenta é o seu código — não o modelo. Aqui entram permissão, limite e registro.
- **4 · Observar e repetir** — o resultado volta ao contexto e o laço recomeça, até o critério de parada.

### O que a narradora fala

O laço tem quatro passos, e eu quero que o terceiro fique gravado. Primeiro, o modelo recebe o objetivo e o estado e decide a próxima ação. Segundo, ele pede a ferramenta: emite um nome e argumentos. Ele não executa nada — nenhum modelo executa nada. Terceiro, quem executa é o seu programa, e é aí que entram a permissão, o limite e o registro de auditoria. Quarto, o resultado volta ao contexto e o laço recomeça. Essa separação entre quem pede e quem executa é o que permite que um sistema com agente seja auditável.

---

<div class="slide" id="slide-47"></div>

## Lâmina 47 — Uso de ferramenta, sem framework nenhum

**Tempo falado:** 39 s

![Lâmina 47](roteiro_narrado_iasdd_v10_biobyte_slides/slide_47.png)

### O que está escrito na lâmina

- *O laço inteiro cabe em vinte linhas. Framework é conveniência, não requisito.*

```python
ferramentas = [{"name": "consultar_microbiologia",
                "parameters": {"caso": "string"}}]

while True:
    r = modelo.chamar(mensagens, tools=ferramentas)
    if not r.tool_calls:
        return r.texto                  # terminou

    for chamada in r.tool_calls:
        # QUEM EXECUTA É O SEU CÓDIGO
        saida = MINHAS_FUNCOES[chamada.name](**chamada.args)
        mensagens.append(resultado(chamada.id, saida))
```

- **Ao lado do código:** Declare as ferramentas, chame o modelo, execute o que ele pediu, devolva o resultado, repita. É isto que todo framework de agente faz por baixo. Comece assim: quando o laço próprio ficar insuficiente, você vai saber exatamente por quê — e aí escolhe o framework pelo motivo certo.

### O que a narradora fala

E aqui está o laço inteiro, sem framework nenhum. Você declara as ferramentas, chama o modelo, e olha o que voltou: se ele não pediu ferramenta, acabou. Se pediu, o seu código executa a função e devolve o resultado para a conversa. Repete. São vinte linhas, e é isso que todo framework faz por baixo. Eu mostro isso por uma razão prática: comecem assim. Quando o laço próprio ficar insuficiente, vocês vão saber exatamente por quê — e aí escolhem o framework pelo motivo certo, não por moda.

---

<div class="slide" id="slide-48"></div>

## Lâmina 48 — Os padrões de composição

**Tempo falado:** 42 s

![Lâmina 48](roteiro_narrado_iasdd_v10_biobyte_slides/slide_48.png)

### O que está escrito na lâmina

- **Encadeamento** — a saída de um passo é a entrada do seguinte. Simples, previsível, e resolve a maioria dos casos.
- **Roteamento** — um classificador decide qual especialista atende. Barato e muito eficaz.
- **Paralelismo** — várias tarefas independentes ao mesmo tempo, com agregação no fim.
- **Orquestrador e executores** — um agente planeja e distribui; os outros executam pedaços.
- **Avaliador e otimizador** — um produz, outro critica, e o ciclo repete até o critério ser atendido.
- **Autonomia com portão** — o agente decide o caminho, mas cada etapa passa por uma verificação em código.

### O que a narradora fala

Há seis maneiras de compor. Encadeamento: a saída de um passo é a entrada do seguinte — simples e resolve a maioria dos casos reais. Roteamento: um classificador barato decide qual especialista atende. Paralelismo, para tarefas independentes. Orquestrador e executores: um planeja, os outros executam. Avaliador e otimizador: um produz, outro critica, e repete. E o sexto, que é o que interessa em domínio regulado: autonomia com portão — o agente escolhe o caminho, mas cada etapa passa por uma verificação em código. É esse o padrão do sistema que vou mostrar no fim.

---

<div class="slide" id="slide-49"></div>

## Lâmina 49 — Multiagente: quando compensa, e quando não

**Tempo falado:** 42 s

![Lâmina 49](roteiro_narrado_iasdd_v10_biobyte_slides/slide_49.png)

### O que está escrito na lâmina

- **Compensa** — quando as subtarefas são de fato paralelizáveis e os contextos, isolados. As duas condições, juntas.
- **Não compensa** — em fluxo linear. Quatro a quinze vezes mais tokens para reimplementar o que um condicional resolveria.
- **A perda de contexto** — cada repasse entre agentes perde informação — como fotocópia de fotocópia.
- **A pergunta a fazer** — esta divisão existe porque o problema pede, ou porque a arquitetura ficou bonita no diagrama?

### O que a narradora fala

Sobre multiagente eu vou na contramão do entusiasmo. Só compensa quando duas condições valem juntas: as subtarefas são de fato paralelizáveis, e os contextos são isolados. Se as partes não são independentes, o custo explode sem ganho — medidas em fluxo linear mostram de quatro a quinze vezes mais tokens para reimplementar o que um condicional resolveria. E há um efeito que quase ninguém contabiliza: a passagem de contexto entre agentes perde informação, como fotocópia de fotocópia. A pergunta a fazer diante de qualquer desenho multiagente é: esta divisão existe porque o problema pede?

---

<div class="slide" id="slide-50"></div>

## Lâmina 50 — Por que agentes falham em produção

**Tempo falado:** 46 s

![Lâmina 50](roteiro_narrado_iasdd_v10_biobyte_slides/slide_50.png)

### O que está escrito na lâmina

- *Noventa e cinco por cento de acerto por passo, vinte passos: trinta e seis por cento de sucesso no fim.*
- **O erro composto** — a confiabilidade multiplica ao longo da cadeia. É aritmética, não pessimismo.
- **Os modos de falha** — laço infinito, ferramenta inventada, contexto contaminado, custo imprevisto.
- **E o pior de todos** — a falha silenciosa: o agente relata sucesso e não fez nada. Nenhum teste de tela pega isso.
- **A saída** — não é escrever um pedido melhor. É reduzir o número de passos não verificados.

### O que a narradora fala

E agora o número que muda a conversa. Um agente com noventa e cinco por cento de acerto por passo, numa cadeia de vinte passos, termina com trinta e seis por cento de sucesso de ponta a ponta. Não é pessimismo, é aritmética. Os modos de falha são conhecidos — laço infinito, ferramenta inventada, contexto contaminado, custo imprevisto. E o pior é a falha silenciosa: o agente relata sucesso e não fez nada; nenhum teste de tela pega isso, porque a tela mostra a mensagem de sucesso. A saída não é escrever um pedido melhor — é reduzir o número de passos não verificados.

---

<div class="slide" id="slide-51"></div>

## Lâmina 51 — Um sistema multiagente com resultado verificável

**▶ VÍDEO — 8 minutos.** agentes com contexto, ferramentas e saída conferida

![Lâmina 51](roteiro_narrado_iasdd_v10_biobyte_slides/slide_51.png)

### O que está escrito na lâmina

- **▶ VÍDEO · 8 minutos** — agentes com contexto, ferramentas e saída conferida
- **1.** O objetivo e as ferramentas declaradas
- **2.** O agente pedindo a ferramenta — e o programa executando
- **3.** O resultado real voltando para o contexto
- **4.** Dois agentes com contextos isolados, e a agregação
- **5.** Uma falha injetada de propósito
- **6.** O portão em código pegando a falha antes de ela seguir adiante

### O que a narradora fala

O quinto vídeo mostra tudo isso rodando: o objetivo, as ferramentas declaradas, o agente pedindo e o programa executando, o resultado real voltando para o contexto. Depois, dois agentes com contextos isolados e a agregação do trabalho deles. E, no fim, uma falha injetada de propósito, para vocês verem o portão em código pegando a falha antes de ela seguir adiante — que é a diferença entre uma demonstração e um sistema.

### Produção deste vídeo

Gravar 8 minutos cobrindo, nesta ordem:

1. O objetivo e as ferramentas declaradas
2. O agente pedindo a ferramenta — e o programa executando
3. O resultado real voltando para o contexto
4. Dois agentes com contextos isolados, e a agregação
5. Uma falha injetada de propósito
6. O portão em código pegando a falha antes de ela seguir adiante

---

<div class="slide" id="slide-52"></div>

## Lâmina 52 — Contexto e recuperação de documentos

**Tempo falado:** 14 s

![Lâmina 52](roteiro_narrado_iasdd_v10_biobyte_slides/slide_52.png)

### O que está escrito na lâmina

- **BLOCO 6 — Contexto e recuperação de documentos**
- *Engenharia de contexto, RAG, e o erro de fatiamento que produz falso positivo clínico.*

### O que a narradora fala

Sexto bloco: contexto. Como se leva o conhecimento certo para dentro do pedido, o que é recuperação aumentada por geração, e um erro de implementação que, num hospital, produz notificação falsa.

---

<div class="slide" id="slide-53"></div>

## Lâmina 53 — De “prompt” para engenharia de contexto

**Tempo falado:** 40 s

![Lâmina 53](roteiro_narrado_iasdd_v10_biobyte_slides/slide_53.png)

### O que está escrito na lâmina

- *O contexto é tudo o que entra na janela do modelo — e a janela é um recurso escasso e caro.*
- **O que compõe o contexto** — a instrução do sistema, o histórico, os documentos recuperados, as definições de ferramentas e o estado.
- **Por que é engenharia** — cada token disputa espaço com outro. Decidir o que entra e o que fica de fora é decisão de projeto.
- **O efeito de encher demais** — com a janela cheia, o modelo passa a ignorar o meio do texto. Mais contexto pode piorar a resposta.
- **A prática** — trazer o trecho certo, não o documento inteiro. Precisão vale mais que volume.

### O que a narradora fala

A expressão “engenharia de prompt” ficou pequena. O que importa é engenharia de contexto: o contexto é tudo o que entra na janela — a instrução do sistema, o histórico, os documentos recuperados, as definições das ferramentas e o estado. E a janela é recurso escasso e caro, por causa daquela quadrática. Decidir o que entra e o que fica de fora é decisão de projeto. E registrem um efeito contraintuitivo: com a janela muito cheia, o modelo passa a ignorar o meio do texto. Mais contexto pode piorar a resposta.

---

<div class="slide" id="slide-54"></div>

## Lâmina 54 — Recuperação aumentada por geração

**Tempo falado:** 42 s

![Lâmina 54](roteiro_narrado_iasdd_v10_biobyte_slides/slide_54.png)

### O que está escrito na lâmina

- **O problema** — o modelo não conhece o seu protocolo, a sua norma interna nem o prontuário do seu paciente.
- **Indexar** — os documentos são fatiados e cada pedaço vira um vetor — um endereço num espaço de significado.
- **Recuperar** — a pergunta também vira vetor; busca-se o que está próximo dela. Proximidade é semelhança de sentido.
- **Gerar com fonte** — os trechos recuperados entram no pedido, e a resposta cita de onde saiu. Sem citação, não há conferência.

### O que a narradora fala

A técnica que resolve isso chama-se recuperação aumentada por geração. O problema é simples: o modelo não conhece o seu protocolo nem o prontuário do seu paciente. A solução tem três tempos. Indexar: os documentos são fatiados e cada pedaço vira um vetor, que é um endereço num espaço de significado. Recuperar: a pergunta também vira vetor, e busca-se o que está próximo — proximidade, aqui, é semelhança de sentido, não de palavra. E gerar com fonte, citando de onde saiu cada trecho. Essa última parte não é enfeite: sem citação, ninguém consegue conferir.

---

<div class="slide" id="slide-55"></div>

## Lâmina 55 — RAG na prática, com LangChain e Qdrant

**Tempo falado:** 36 s

![Lâmina 55](roteiro_narrado_iasdd_v10_biobyte_slides/slide_55.png)

### O que está escrito na lâmina

- *Vinte linhas para transformar um diretório de protocolos em algo que o modelo consegue consultar.*

```python
docs   = carregar("protocolos/")
pedacos = fatiar_por_regra(docs)      # NÃO por tamanho fixo

indice = Qdrant.from_documents(
    pedacos, embeddings, collection_name="ccih")

trechos = indice.similarity_search(pergunta, k=5)
resposta = modelo.gerar(
    monta_prompt(pergunta, trechos),
    temperatura=0.0)

# a resposta carrega a origem de cada trecho
citar(trechos)
```

- **Ao lado do código:** Qdrant é o banco de vetores; os embeddings convertem texto em vetor; o LangChain costura as peças. Repare no detalhe que decide a qualidade: o fatiamento. É ele que faz a diferença entre uma resposta certa e uma resposta pela metade.

### O que a narradora fala

Na prática são vinte linhas. Você carrega o diretório de protocolos, fatia os documentos, transforma cada pedaço em vetor e guarda num banco de vetores. Na hora da pergunta, busca os trechos mais próximos, monta o pedido com eles e gera a resposta com temperatura baixa, citando a origem. O LangChain costura as peças. E eu quero que vocês reparem numa linha só: a do fatiamento. É ela que decide a qualidade de tudo — e é sobre ela o próximo slide.

---

<div class="slide" id="slide-56"></div>

## Lâmina 56 — Onde o RAG quebra: o fatiamento

**Tempo falado:** 47 s

![Lâmina 56](roteiro_narrado_iasdd_v10_biobyte_slides/slide_56.png)

### O que está escrito na lâmina

- *Um caso real: um critério de definição de caso de infecção hospitalar ocupa três parágrafos.*
- **A regra inteira** — critério clínico, mais critério laboratorial, mais janela temporal. Os três precisam ser lidos juntos.
- **Fatiado por tamanho fixo** — o critério laboratorial se separa da janela temporal. A busca devolve metade da regra.
- **O que o modelo faz** — completa o resto sozinho, com fluência — e o sistema notifica um falso positivo.
- **A correção** — fatiar pela unidade lógica: a regra inteira num pedaço, com metadados por tipo de infecção e expansão de janela em volta do trecho.

### O que a narradora fala

Deixe eu mostrar onde isso quebra, com um caso do domínio de vocês. Um critério de definição de caso de infecção hospitalar ocupa três parágrafos: critério clínico, critério laboratorial e janela temporal. Os três só fazem sentido lidos juntos. Se você fatia em pedaços de tamanho fixo, o laboratorial se separa da janela; a busca devolve metade da regra; o modelo completa o resto sozinho, com fluência; e o sistema notifica um falso positivo. Ninguém percebe, porque a resposta está bem escrita. A correção é fatiar pela unidade lógica — a regra inteira num pedaço. É o tipo de decisão que parece técnica e é clínica.

---

<div class="slide" id="slide-57"></div>

## Lâmina 57 — Saída estruturada e proteções

**Tempo falado:** 46 s

![Lâmina 57](roteiro_narrado_iasdd_v10_biobyte_slides/slide_57.png)

### O que está escrito na lâmina

- **Saída estruturada** — exija um esquema, não um texto livre. O modelo devolve campos que o seu código valida antes de usar.
- **Por que isso importa** — texto livre obriga a interpretar a resposta do modelo — e interpretar é onde o defeito entra.
- **Avaliação** — um conjunto de casos com resposta esperada, rodado a cada mudança. Sem isso, você não sabe se melhorou ou piorou.
- **Proteções** — limite de passos, limite de custo, lista de ferramentas permitidas, e confirmação humana no que é irreversível.

### O que a narradora fala

Duas práticas fecham o bloco. A primeira é saída estruturada: em vez de aceitar texto livre, exija um esquema com campos definidos, e valide esses campos no seu código. Isso importa porque texto livre obriga o seu programa a interpretar o que o modelo escreveu, e interpretar é onde o defeito entra. A segunda é avaliação: um conjunto de casos com resposta esperada, rodado a cada mudança — sem isso vocês não têm como saber se uma alteração melhorou ou piorou o sistema. E, junto, as proteções: limite de passos, limite de custo, lista fechada de ferramentas, e confirmação humana no que é irreversível.

---

<div class="slide" id="slide-58"></div>

## Lâmina 58 — Frameworks de agentes

**Tempo falado:** 13 s

![Lâmina 58](roteiro_narrado_iasdd_v10_biobyte_slides/slide_58.png)

### O que está escrito na lâmina

- **BLOCO 7 — Frameworks de agentes**
- *Cinco opções, um critério de leitura, e uma opinião contrária.*

### O que a narradora fala

Sétimo bloco: frameworks. São cinco opções relevantes hoje. Eu vou dar um critério de leitura para vocês compararem, passar por cada uma, e terminar com uma opinião contrária ao consenso.

---

<div class="slide" id="slide-59"></div>

## Lâmina 59 — O critério de leitura

**Tempo falado:** 40 s

![Lâmina 59](roteiro_narrado_iasdd_v10_biobyte_slides/slide_59.png)

### O que está escrito na lâmina

- *Quatro perguntas que separam os cinco — e que valem para qualquer framework novo que aparecer.*
- **Quem controla o laço?** — você, ou o framework? Isso determina o quanto você consegue depurar quando der errado.
- **Onde mora o estado?** — em memória, em sessão, em arquivo, ou num armazenamento durável que sobrevive a uma queda?
- **Como o humano entra?** — existe ponto de interrupção e aprovação, ou o fluxo só vai do começo ao fim?
- **O que se vê de dentro?** — há registro de cada passo, custo por passo e possibilidade de reexecutar a partir do meio?

### O que a narradora fala

Antes de comparar, o critério — e ele vale para qualquer framework novo que apareça depois desta palestra. Primeira pergunta: quem controla o laço, você ou o framework? Isso determina o quanto você consegue depurar quando der errado. Segunda: onde mora o estado — em memória, em sessão, ou num armazenamento durável que sobrevive a uma queda? Terceira: como o humano entra, existe ponto de interrupção e aprovação? Quarta: o que se enxerga de dentro, há registro de cada passo e custo por passo? Comparem por essas quatro, não por popularidade.

---

<div class="slide" id="slide-60"></div>

## Lâmina 60 — Comparativo, e a opinião contrária

**Tempo falado:** 54 s

![Lâmina 60](roteiro_narrado_iasdd_v10_biobyte_slides/slide_60.png)

### O que está escrito na lâmina


|  | Controle do laço | Estado | Humano no laço | Caso ideal |
|---|---|---|---|---|
| OpenAI Agents SDK | o framework | sessão | proteções | produtos OpenAI |
| Claude Agent SDK | o framework | arquivos | ganchos e permissões | código e documentos |
| LangGraph | máquina de estados | durável | interrupção nativa | produção regulada |
| CrewAI | escondido | fraco | limitado | protótipo rápido |
| AutoGen / AG2 | conversa | fraco | granular | exploração e pesquisa |
| O seu próprio laço | você | você decide | você decide | a maioria dos casos |

- **Nota na lâmina:** A opinião contrária: para boa parte dos casos, o laço escrito à mão é mais simples de depurar. Framework se justifica por durabilidade, observabilidade e entrada do humano no fluxo — não por elegância.

### O que a narradora fala

Os cinco, comparados pelas quatro perguntas. O SDK da OpenAI e o da Anthropic controlam o laço, com estado em sessão e em arquivos. O LangGraph é máquina de estados com persistência durável e interrupção nativa — é a escolha quando o fluxo precisa sobreviver a uma queda e passar por aprovação humana, quer dizer, produção regulada. O CrewAI declara papéis e tarefas em YAML e esconde o laço: ótimo para protótipo rápido, e é o que usamos no LangNet. O AutoGen põe agentes conversando, melhor para pesquisa. E a opinião contrária: para boa parte dos casos, o laço escrito à mão é mais simples de depurar. Framework se justifica por durabilidade, observabilidade e entrada do humano — não por elegância.

---

<div class="slide" id="slide-61"></div>

## Lâmina 61 — Ambientes de geração de código

**Tempo falado:** 21 s

![Lâmina 61](roteiro_narrado_iasdd_v10_biobyte_slides/slide_61.png)

### O que está escrito na lâmina

- **BLOCO 8 — Ambientes de geração de código**
- *Onde o agente trabalha de verdade: Claude Code, Codex, Cursor — e o que muda no ofício.*

### O que a narradora fala

Oitavo bloco. Até aqui falamos de agentes em abstrato; agora vamos ao lugar onde eles já fazem trabalho de produção todos os dias, que é dentro do repositório de código. Três ambientes, os comandos que vocês vão usar de fato, e o que isso muda no ofício.

---

<div class="slide" id="slide-62"></div>

## Lâmina 62 — Mudou a unidade de trabalho

**Tempo falado:** 47 s

![Lâmina 62](roteiro_narrado_iasdd_v10_biobyte_slides/slide_62.png)

### O que está escrito na lâmina

- *A unidade deixou de ser a linha de código. Passou a ser a tarefa descrita.*
- **Antes** — você escrevia as linhas. O editor completava palavras; a revisão era sobre o que você tinha digitado.
- **Agora** — você descreve a tarefa e revisa o diferencial. O agente lê o repositório, propõe a mudança e roda os testes.
- **O que ficou mais importante** — saber dizer o que se quer, e saber ler criticamente o que voltou.
- **O que ficou mais perigoso** — aceitar sem ler. Um diferencial grande e bem formatado passa fácil por uma revisão apressada.

### O que a narradora fala

A primeira coisa a entender é que a unidade de trabalho mudou. Antes era a linha de código: você escrevia as linhas, o editor completava palavras, e a revisão era sobre o que você tinha digitado. Agora a unidade é a tarefa descrita: você diz o que quer, o agente lê o repositório, propõe a mudança e roda os testes, e você revisa o diferencial. O que ficou mais importante foi saber dizer o que se quer e ler criticamente o que voltou. E o que ficou mais perigoso foi aceitar sem ler — um diferencial grande e bem formatado passa fácil por uma revisão apressada.

---

<div class="slide" id="slide-63"></div>

## Lâmina 63 — Claude Code: sessão de engenharia no terminal

**Tempo falado:** 40 s

![Lâmina 63](roteiro_narrado_iasdd_v10_biobyte_slides/slide_63.png)

### O que está escrito na lâmina

- *O terminal vira uma sessão com contexto persistente sobre o repositório inteiro.*

```python
claude                      # abre a sessão no repositório
claude -c                   # continua a última sessão
claude -r <id-da-sessao>    # retoma uma sessão específica
claude -p "rode os testes"  # modo não interativo, para automação
claude mcp                  # conecta ferramentas externas

/help      /compact      /resume
```

- **Ao lado do código:** As extensões que importam: skills codificam um fluxo repetível; subagentes e equipes dividem investigação e implementação; e o MCP liga o agente a ferramentas e dados externos. O modo não interativo é o que permite pôr o agente dentro de um pipeline de integração contínua.

### O que a narradora fala

O Claude Code transforma o terminal numa sessão de engenharia com contexto persistente sobre o repositório inteiro. Vocês abrem a sessão, continuam a anterior, retomam uma sessão específica pelo identificador, ou rodam em modo não interativo passando a tarefa na linha de comando — e é esse último modo que permite pôr o agente dentro de um pipeline de integração contínua. As extensões que importam são três: as skills, que codificam um fluxo repetível; os subagentes, que dividem investigação e implementação; e o MCP, que liga o agente a ferramentas externas.

---

<div class="slide" id="slide-64"></div>

## Lâmina 64 — Codex: execução, revisão e saída verificável

**Tempo falado:** 37 s

![Lâmina 64](roteiro_narrado_iasdd_v10_biobyte_slides/slide_64.png)

### O que está escrito na lâmina

- *O mesmo agente serve à exploração interativa e à automação reproduzível.*

```python
codex                                  # sessão interativa
codex exec "inspecione o repositório"   # automação
codex exec --json "rode as checagens"   # eventos registrados
codex exec --output-schema esquema.json "avalie"

/init          # cria o AGENTS.md do repositório
$skill-creator # cria uma skill
```

- **Ao lado do código:** A sessão interativa serve à exploração. O modo de execução serve à automação: o registro em JSON deixa rastro de cada evento, e o esquema de saída obriga o agente a devolver algo que o seu código consegue validar. O arquivo AGENTS.md transforma as convenções do time em contexto reutilizável.

### O que a narradora fala

O Codex cobre o mesmo terreno com ênfase diferente: a sessão interativa serve à exploração, o modo de execução serve à automação. Duas opções merecem atenção. O registro em formato JSON deixa rastro de cada evento — e rastro é o que uma auditoria pede. E o esquema de saída obriga o agente a devolver algo que o seu código consegue validar, em vez de texto livre: é a mesma ideia de saída estruturada do bloco seis, agora aplicada ao próprio agente de código.

---

<div class="slide" id="slide-65"></div>

## Lâmina 65 — Cursor e o panorama dos editores

**Tempo falado:** 35 s

![Lâmina 65](roteiro_narrado_iasdd_v10_biobyte_slides/slide_65.png)

### O que está escrito na lâmina

- **Cursor** — editor completo com agente embutido: contexto do projeto, edição em vários arquivos e revisão do diferencial na própria tela.
- **A diferença de ênfase** — o terminal favorece automação e repetição; o editor favorece exploração e revisão visual.
- **O que não muda** — em qualquer um deles, quem aprova a mudança é uma pessoa. O agente propõe.
- **Como escolher** — pelo fluxo do time, não pela ferramenta. Quem já vive no terminal ganha pouco mudando para o editor, e vice-versa.

### O que a narradora fala

O Cursor resolve o mesmo problema pelo outro lado: é um editor completo com o agente embutido, com contexto do projeto, edição em vários arquivos e revisão do diferencial na própria tela. A diferença é de ênfase — o terminal favorece automação, o editor favorece exploração e revisão visual. O que não muda em nenhum dos três é o essencial: quem aprova a mudança é uma pessoa; o agente propõe. E escolham pelo fluxo do time, não pela ferramenta.

---

<div class="slide" id="slide-66"></div>

## Lâmina 66 — Protocolos e contratos

**Tempo falado:** 22 s

![Lâmina 66](roteiro_narrado_iasdd_v10_biobyte_slides/slide_66.png)

### O que está escrito na lâmina

- **BLOCO 9 — Protocolos e contratos**
- *MCP na vertical, A2A na horizontal, formatos de conhecimento — e o que nenhum deles resolve.*

### O que a narradora fala

Nono bloco: protocolos. Quando os agentes deixam de ser um script isolado e viram parte de um sistema, aparece a pergunta de como eles conversam com ferramentas e entre si. Existem padrões para isso. E existe uma coisa importante que nenhum deles resolve — e que sobra para vocês.

---

<div class="slide" id="slide-67"></div>

## Lâmina 67 — O mapa: vertical e horizontal

**Tempo falado:** 55 s

![Lâmina 67](roteiro_narrado_iasdd_v10_biobyte_slides/slide_67.png)

### O que está escrito na lâmina

- **MCP — a vertical** — liga um agente às ferramentas e aos dados. Um servidor MCP publica ferramentas com nome, parâmetros e esquema de retorno.
- **Por que isso importa** — a ferramenta deixa de ser código colado dentro do agente e passa a ser um serviço com contrato, reaproveitável e versionável.
- **A2A — a horizontal** — liga agentes a outros agentes: descoberta de capacidades, delegação de tarefa e acompanhamento.
- **Como ler os dois juntos** — o MCP responde “o que eu posso fazer”; o A2A responde “com quem eu posso contar”.

### O que a narradora fala

O mapa tem dois eixos. Na vertical, o MCP liga um agente às ferramentas e aos dados: um servidor publica ferramentas com nome, parâmetros e esquema de retorno, e qualquer agente compatível passa a poder usá-las. Isso importa porque a ferramenta deixa de ser código colado dentro do agente e vira um serviço com contrato. Na horizontal, o A2A liga agentes a outros agentes: descoberta de capacidades e delegação de tarefa. Uma frase para guardar o par: o MCP responde “o que eu posso fazer”; o A2A, “com quem eu posso contar”. E a crítica que importa: nenhum desses protocolos expressa governança — registram quem chamou quem, não sob qual política nem com que base legal. Em saúde, essa camada sobra para vocês.

---

<div class="slide" id="slide-68"></div>

## Lâmina 68 — Conhecimento em formato aberto

**Tempo falado:** 45 s

![Lâmina 68](roteiro_narrado_iasdd_v10_biobyte_slides/slide_68.png)

### O que está escrito na lâmina

- *Um pacote de conhecimento é um diretório de arquivos em markdown. Sem banco, sem servidor.*
- **A ideia** — cada arquivo é um conceito; o caminho do arquivo é o identificador; os arquivos se referenciam por links comuns.
- **Por que vira grafo** — porque as referências são ligações de verdade — o diretório deixa de ser lista e passa a ser rede.
- **O uso direto para vocês** — um pacote com as definições de caso, as fórmulas dos indicadores e os procedimentos da comissão de controle de infecção.
- **O que isso entrega** — legível por agente, revisável por infectologista, com histórico e autoria por linha — metade do que uma auditoria já pede.

### O que a narradora fala

Há ainda uma camada que quase ninguém discute: em que formato o conhecimento fica. A proposta mais interessante é radicalmente simples — um pacote de conhecimento é um diretório de arquivos em markdown, sem banco e sem servidor. Cada arquivo é um conceito, o caminho é o identificador, e os arquivos se referenciam por links comuns, o que transforma o diretório num grafo. Para vocês o uso é direto: um pacote com as definições de caso, as fórmulas dos indicadores e os procedimentos da comissão. Legível por agente e revisável por infectologista ao mesmo tempo, com histórico e autoria linha a linha.

---

<div class="slide" id="slide-69"></div>

## Lâmina 69 — Desenvolvimento Orientado a Especificação

**Tempo falado:** 17 s

![Lâmina 69](roteiro_narrado_iasdd_v10_biobyte_slides/slide_69.png)

### O que está escrito na lâmina

- **BLOCO 10 — Desenvolvimento Orientado a Especificação**
- *Especificar antes de delegar. A especificação é o que se versiona; o código é o que se regenera.*

### O que a narradora fala

Décimo bloco, e é o centro da palestra. Desenvolvimento orientado a especificação. A ideia cabe numa frase: especificar antes de delegar. A especificação é o que se versiona e se revisa; o código é o que se regenera.

---

<div class="slide" id="slide-70"></div>

## Lâmina 70 — O problema

**Tempo falado:** 41 s

![Lâmina 70](roteiro_narrado_iasdd_v10_biobyte_slides/slide_70.png)

### O que está escrito na lâmina

- *Programar “no sentimento” funciona no protótipo e colapsa no sistema.*
- **O que acontece** — enquanto é pequeno, tudo bem. Quando cresce, ninguém mais segura o conjunto na cabeça.
- **O sintoma** — o código existe e funciona — e ninguém sabe qual requisito ele atende, nem se ainda atende.
- **Com agente, mais rápido** — o agente produz em minutos o volume que antes levava semanas. O descompasso entre código e intenção cresce na mesma velocidade.
- **Em domínio regulado** — isso tem outro nome: não conformidade. Não é dívida técnica, é risco regulatório.

### O que a narradora fala

Começo pelo problema. Programar no sentimento funciona no protótipo e colapsa no sistema: enquanto é pequeno, tudo bem; quando cresce, ninguém mais segura o conjunto na cabeça. O sintoma é este — o código existe, funciona, e ninguém sabe qual requisito ele atende, nem se ainda atende. Com agentes isso ficou mais rápido, não menos: o agente produz em minutos o volume que antes levava semanas. E em domínio regulado esse descompasso tem outro nome: não conformidade. Não é dívida técnica, que se paga quando der. É risco regulatório, que aparece na auditoria.

---

<div class="slide" id="slide-71"></div>

## Lâmina 71 — A inversão

**Tempo falado:** 43 s

![Lâmina 71](roteiro_narrado_iasdd_v10_biobyte_slides/slide_71.png)

### O que está escrito na lâmina

- **O jeito de hoje** — requisito informal → código → documentação que já nasce desatualizada.
- **O desenvolvimento orientado a especificação** — especificação primária → plano → tarefas → código derivado.
- **O que se versiona** — a especificação. Ela é revisada, discutida e mantida como o artefato principal.
- **O que se regenera** — o código. É a mesma relação entre código-fonte e binário: ninguém revisa o binário.

### O que a narradora fala

A inversão é esta. Hoje o fluxo é requisito informal, código, e uma documentação que já nasce desatualizada, porque foi escrita depois, a partir do código. No desenvolvimento orientado a especificação o fluxo se inverte: a especificação é primária, dela sai o plano, do plano as tarefas, e das tarefas o código, que é derivado. O que se versiona e se mantém é a especificação; o código é o que se regenera. A analogia que fixa a ideia é a relação entre código-fonte e binário: ninguém revisa o binário, ninguém corrige um defeito editando o executável.

---

<div class="slide" id="slide-72"></div>

## Lâmina 72 — Anatomia de uma especificação útil

**Tempo falado:** 53 s

![Lâmina 72](roteiro_narrado_iasdd_v10_biobyte_slides/slide_72.png)

### O que está escrito na lâmina

- **Contexto, escopo e não objetivos** — dizer o que está fora é tão importante quanto dizer o que está dentro.
- **Requisitos verificáveis** — cada requisito precisa admitir um teste que diga passou ou não passou.
- **Bom** — “Quando uma hemocultura positiva for registrada, o sistema deve avaliar os critérios de infecção em até 48 horas e produzir um parecer com a evidência citada.”
- **Ruim** — “O sistema deve detectar infecções corretamente.” Não é verificável, então não é requisito — é uma intenção.

### O que a narradora fala

O que faz uma especificação ser útil. Ela precisa de contexto e escopo, e precisa dos não objetivos — dizer o que está fora é o que impede o projeto de inchar. E precisa de requisitos verificáveis: cada requisito tem de admitir um teste que diga passou ou não passou. Comparem os dois exemplos. O bom diz quando o comportamento é disparado, o que o sistema deve fazer, em quanto tempo e com que evidência — dá para escrever o teste lendo a frase. O ruim diz “o sistema deve detectar infecções corretamente”, que não é verificável e portanto não é requisito. Se a especificação estiver cheia de frases do segundo tipo, o agente preenche as lacunas do jeito dele.

---

<div class="slide" id="slide-73"></div>

## Lâmina 73 — Da especificação ao código, e a rastreabilidade

**Tempo falado:** 43 s

![Lâmina 73](roteiro_narrado_iasdd_v10_biobyte_slides/slide_73.png)

### O que está escrito na lâmina

- **O requisito** — R-014: avaliar os critérios de infecção dentro da janela de 48 horas.
- **O teste, gerado do critério** — confere as bordas da janela — o caso que passa em 47 horas e o que não passa em 49.
- **A implementação** — derivada da especificação, não o contrário.
- **Por que a ordem importa** — o teste nasceu do critério, não do código. Por isso ele não herda os defeitos da implementação.

### O que a narradora fala

Vamos ver a ordem funcionando. O requisito diz: avaliar os critérios de infecção dentro de uma janela de quarenta e oito horas. Desse critério nasce o teste, que confere as bordas da janela. E só então nasce a implementação. A ordem é o ponto inteiro: quando o teste é escrito depois, olhando para o código, ele herda os defeitos da implementação — se o programador entendeu a janela errado, o teste confirma o erro com muita confiança. Escrito a partir do critério, não tem como herdar nada. E fica a trilha: requisito, teste, função, ligados por identificador.

---

<div class="slide" id="slide-74"></div>

## Lâmina 74 — Onde o SDD encontra os agentes

**Tempo falado:** 45 s

![Lâmina 74](roteiro_narrado_iasdd_v10_biobyte_slides/slide_74.png)

### O que está escrito na lâmina

- *Especificador → portão → Arquiteto → portão → Implementador → portão → Verificador*
- **Contexto isolado por etapa** — cada agente recebe só o que precisa. Isso corta a contaminação de contexto de uma etapa para a outra.
- **O portão em código determinístico** — quem verifica é programa, não outro modelo. Verificar com um segundo modelo apenas empilha incerteza.
- **Por que isso resolve o erro composto** — o monólito de vinte passos tem trinta e seis por cento de sucesso. Com portão, o erro não se propaga — ele para na etapa.
- **O que o portão devolve** — aprovado, ou reprovado com o motivo. E reprovado significa que a etapa não avança.

### O que a narradora fala

Aqui as duas metades da palestra se encontram. A cadeia é: um agente especifica, um portão confere; um projeta, um portão confere; um implementa, um portão confere; um verifica. Duas decisões sustentam isso. Contexto isolado por etapa, que corta a contaminação de uma etapa para a outra. E — a que eu mais defendo — o portão é código determinístico: quem verifica é programa, não outro modelo, porque verificar com um segundo modelo apenas empilha incerteza. É assim que se resolve o erro composto do bloco cinco: o erro não se propaga pela cadeia, ele para na etapa em que nasceu.

---

<div class="slide" id="slide-75"></div>

## Lâmina 75 — O artefato regulatório sai de graça

**Tempo falado:** 53 s

![Lâmina 75](roteiro_narrado_iasdd_v10_biobyte_slides/slide_75.png)

### O que está escrito na lâmina

- **O que a norma pede** — rastreabilidade de requisito a projeto, a teste, a código. Mais gestão de risco documentada e ciclo de vida controlado.
- **As referências** — IEC 62304 para ciclo de vida de software médico, ISO 14971 para gestão de risco, e a resolução da ANVISA.
- **O que o SDD entrega** — quem trabalha assim já tem a matriz de rastreabilidade — como subproduto, versionada, com autoria e histórico.
- **A inversão da objeção** — o SDD é o que torna código gerado por IA auditável. O que não é auditável é código escrito à mão sem especificação.

### O que a narradora fala

E há um ganho que costuma decidir a conversa com a diretoria. Software de saúde exige rastreabilidade de requisito a projeto, a teste, a código, mais gestão de risco documentada e ciclo de vida controlado. Quem trabalha orientado a especificação já tem a matriz de rastreabilidade — não como um documento montado na véspera da auditoria, mas como subproduto do método, versionado e com autoria. E isso permite inverter a objeção mais comum que vocês vão ouvir. Vão dizer: código gerado por inteligência artificial não é auditável. A resposta é que o método é precisamente o que o torna auditável. O que não é auditável é código escrito à mão, sem especificação, por alguém que já saiu da empresa.

---

<div class="slide" id="slide-76"></div>

## Lâmina 76 — Antipadrões: como o método morre na prática

**Tempo falado:** 49 s

![Lâmina 76](roteiro_narrado_iasdd_v10_biobyte_slides/slide_76.png)

### O que está escrito na lâmina

- **Especificação escrita depois** — para justificar o que já foi feito. Vira documentação, e documentação não guia nada.
- **Requisito não verificável** — quando ninguém consegue escrever o teste, o agente preenche a lacuna com o critério dele.
- **Portão feito por outro modelo** — duas incertezas empilhadas não fazem uma certeza.
- **Corrigir no artefato final** — editar o código gerado à mão. Na próxima geração a correção some — e ninguém lembra por quê.
- **O remédio** — a correção entra na especificação e o artefato é regerado. Sempre. Sem exceção de “é só um detalhe”.

### O que a narradora fala

Os quatro jeitos de matar o método. Primeiro: escrever a especificação depois, para justificar o que já foi feito — isso é documentação, e documentação não guia nada. Segundo: o requisito não verificável, em que o agente preenche a lacuna com o critério dele. Terceiro: pôr outro modelo como portão, porque duas incertezas empilhadas não produzem uma certeza. E o quarto, o mais comum e o mais tentador: corrigir à mão no artefato final. Você edita o código gerado, funciona, e na próxima geração a correção some. O remédio é uma regra sem exceção: a correção entra na especificação, e o artefato é regerado. Inclusive quando parece só um detalhe.

---

<div class="slide" id="slide-77"></div>

## Lâmina 77 — LangNet e BioByte

**Tempo falado:** 25 s

![Lâmina 77](roteiro_narrado_iasdd_v10_biobyte_slides/slide_77.png)

### O que está escrito na lâmina

- **BLOCO 11 — LangNet e BioByte**
- *O método do bloco anterior, implementado — e uma aplicação hospitalar gerada por ele.*

### O que a narradora fala

Último bloco de conteúdo. Tudo o que vimos até aqui vira uma coisa só: um pipeline que recebe um documento de pedido e devolve uma aplicação funcionando, com rastro de cada passagem. O sistema chama-se LangNet. E a aplicação que ele gerou, e que vocês vão ver rodando, chama-se BioByte Sentinela — vigilância de infecção hospitalar.

---

<div class="slide" id="slide-78"></div>

## Lâmina 78 — Dois lados: a fábrica e a máquina

**Tempo falado:** 51 s

![Lâmina 78](roteiro_narrado_iasdd_v10_biobyte_slides/slide_78.png)

### O que está escrito na lâmina

- *O LangNet não é a aplicação. Ele é a fábrica que produz a aplicação.*
- **A fábrica** — o LangNet percorre as etapas, do documento ao código, e guarda cada artefato com versão, origem e autoria.
- **A máquina** — a aplicação gerada roda por conta própria, com um executor que dispara as tarefas dos agentes.
- **O que liga os dois** — a rede de Petri: ela sai da fábrica como artefato e entra na máquina como plano de execução.
- **Por que essa distinção importa** — defeito de aplicação se corrige na fábrica e se regera. Nunca no artefato final.

### O que a narradora fala

Antes de percorrer as etapas, uma distinção que organiza tudo. O LangNet não é a aplicação — ele é a fábrica que produz a aplicação. De um lado a fábrica, que percorre as etapas do documento até o código e guarda cada artefato com versão, origem e autoria. Do outro a máquina: a aplicação gerada, rodando por conta própria com um executor que dispara as tarefas dos agentes. O que liga os dois é a rede de Petri, que sai da fábrica como artefato e entra na máquina como plano de execução. E daí sai a regra de ouro: defeito da aplicação se corrige na fábrica e se regera — nunca no artefato final.

---

<div class="slide" id="slide-79"></div>

## Lâmina 79 — As etapas, e o que se repete em todas elas

**Tempo falado:** 49 s

![Lâmina 79](roteiro_narrado_iasdd_v10_biobyte_slides/slide_79.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Docs, Requisitos, Especificação, Modelo de dados, Interface, Ferramentas, Agentes e tarefas, Petri, Testes, Código, Aplicação**
- **O mesmo ritual em cada etapa** — escolher a origem e a versão de onde partir · gerar · refinar conversando com o agente · aprovar.
- **Tudo é versionado** — aprovar não apaga o anterior. Cada etapa guarda de qual versão da etapa anterior ela nasceu.
- **O portão entre etapas** — código determinístico confere a passagem. Reprovado significa que não avança — e diz por quê.
- **Refinar é conversar** — a correção é dita em português, ao agente da etapa. Ele reescreve o artefato e grava uma versão nova.

### O que a narradora fala

São onze etapas, e o que importa entender primeiro é que todas seguem o mesmo ritual: você escolhe a origem e a versão de onde partir, gera, refina conversando com o agente daquela etapa, e aprova. Tudo é versionado — aprovar não apaga o anterior, e cada etapa guarda de qual versão da anterior ela nasceu, que é o que dá a rastreabilidade de ponta a ponta. Entre uma etapa e a seguinte há um portão em código determinístico: se a passagem não estiver íntegra, não avança, e o portão diz por quê. E refinar é literalmente conversar: você escreve a correção em português e o agente reescreve o artefato.

---

<div class="slide" id="slide-80"></div>

## Lâmina 80 — Do documento aos requisitos

**Tempo falado:** 53 s

![Lâmina 80](roteiro_narrado_iasdd_v10_biobyte_slides/slide_80.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Docs, Requisitos**
- **A entrada** — o documento do cliente — no caso, o pedido do hospital para vigilância de infecção relacionada à assistência.
- **Cada requisito diz de onde veio** — extraído do documento, inferido, trazido de pesquisa, ou acrescentado na conversa. A procedência fica gravada.
- **E diz a sua natureza** — convencional ou agêntico. Cadastrar um paciente é convencional; classificar um caso pelo critério da norma é agêntico.
- **Por que essa marca decide o projeto** — ela é que determina, lá na frente, o que vira código comum e o que vira tarefa de agente.

### O que a narradora fala

A primeira etapa recebe o documento do cliente — no nosso caso, o pedido do hospital para vigilância de infecção relacionada à assistência. Dele nascem os requisitos, e dois campos merecem atenção. A procedência: cada requisito diz se foi extraído do documento, inferido, trazido de pesquisa, ou acrescentado na conversa — e isso fica gravado, começando a trilha de auditoria. E a natureza: convencional ou agêntico. Cadastrar um paciente é convencional; classificar um caso pelo critério da norma é agêntico. Essa marca parece burocrática e decide o projeto inteiro, porque determina o que vira código comum e o que vira tarefa de agente. Quando é mal posta, o sistema faz quarenta e cinco tarefas de agente onde deveria ter oito.

---

<div class="slide" id="slide-81"></div>

## Lâmina 81 — A especificação funcional

**Tempo falado:** 49 s

![Lâmina 81](roteiro_narrado_iasdd_v10_biobyte_slides/slide_81.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Especificação**
- **O caso de uso** — ator, pré-condições, fluxo principal passo a passo, e os fluxos de exceção — o que acontece quando dá errado.
- **O croqui da tela** — cada caso de uso traz o esboço da tela: que campos, que botões, que resultado aparece.
- **A decisão do agente** — nos casos agênticos, a especificação declara o que o agente decide e com base em quê.
- **A consistência conferida** — o croqui e o fluxo precisam falar dos mesmos campos e dos mesmos botões. O portão confere isso.

### O que a narradora fala

Da lista de requisitos nasce a especificação funcional, escrita em casos de uso. Cada um tem ator, pré-condições, fluxo principal passo a passo, e — o que mais falta nas especificações que eu vejo por aí — os fluxos de exceção, isto é, o que acontece quando dá errado. Cada caso de uso traz também o croqui da tela, e nos casos agênticos declara o que o agente decide e com base em quê. Há um portão conferindo uma coisa específica: o croqui e o fluxo têm de falar dos mesmos campos e dos mesmos botões. Quando divergem, o defeito atravessa o pipeline e só aparece na tela do usuário.

---

<div class="slide" id="slide-82"></div>

## Lâmina 82 — O modelo de dados, e a correção por conversa

**Tempo falado:** 45 s

![Lâmina 82](roteiro_narrado_iasdd_v10_biobyte_slides/slide_82.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Modelo de dados**
- **O que sai** — as tabelas, os campos, os tipos, as chaves e as relações — derivadas das entidades dos casos de uso.
- **A etapa aponta os próprios defeitos** — coluna obrigatória sem valor padrão, resultado de agente sem coluna dedicada, campo que ninguém preenche.
- **A correção é dita em português** — “a urgência precisa ser uma coluna própria, com valores fechados” — e o agente reescreve o modelo.
- **A versão nova guarda a anterior** — dá para comparar as duas e ver exatamente o que mudou.

### O que a narradora fala

Das entidades dos casos de uso nasce o modelo de dados. E aqui há uma coisa que contraria a expectativa: a própria etapa aponta os seus defeitos. Ela avisa quando há coluna obrigatória sem valor padrão, quando o resultado de um agente não tem coluna dedicada, quando existe campo que ninguém preenche. Você lê o aviso e responde em português — por exemplo: a urgência precisa ser uma coluna própria, com valores fechados. O agente reescreve o modelo e grava uma versão nova, preservando a anterior, de modo que dá para comparar as duas. Isso vocês vão ver acontecendo na demonstração.

---

<div class="slide" id="slide-83"></div>

## Lâmina 83 — A interface e o protótipo

**Tempo falado:** 48 s

![Lâmina 83](roteiro_narrado_iasdd_v10_biobyte_slides/slide_83.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Interface**
- **As telas saem dos casos de uso** — cada tela nasce do croqui e do fluxo do caso de uso que a origina — não de um molde genérico de formulário.
- **Componentes de verdade** — indicador, gráfico, tabela, lista e marcação, além dos campos. Uma tela de vigilância não é um cadastro.
- **O protótipo roda antes de existir sistema** — o mesmo código das telas, com a fonte de dados trocada por dados de exemplo. Compila em milissegundos.
- **Para que serve** — discutir a tela com o usuário antes de gerar backend, banco e agentes — quando mudar ainda é barato.

### O que a narradora fala

Dos casos de uso nascem as telas, e cada tela nasce do croqui e do fluxo do caso de uso que a origina — não de um molde genérico de formulário. Isso importa porque uma tela de vigilância epidemiológica não é um cadastro: tem indicador, gráfico, tabela, lista e marcação, além dos campos. Se o gerador só souber desenhar campo de formulário, as telas viram casca vazia — e esse foi um defeito real que nós corrigimos. Depois vem o protótipo, que é o mesmo código com a fonte de dados trocada, compilando em milissegundos: ele serve para discutir a tela com o usuário enquanto mudar ainda é barato.

---

<div class="slide" id="slide-84"></div>

## Lâmina 84 — Ferramentas, agentes e tarefas

**Tempo falado:** 50 s

![Lâmina 84](roteiro_narrado_iasdd_v10_biobyte_slides/slide_84.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Ferramentas, Agentes e tarefas**
- **Quem implementa cada ferramenta** — a etapa de ferramentas decide: código determinístico, tarefa de agente, ou serviço externo publicado por MCP.
- **No BioByte** — duas ferramentas reais publicadas por um servidor MCP: consulta à microbiologia e cálculo do escore de risco.
- **Cada tarefa sabe de onde veio** — toda tarefa carrega o caso de uso e o requisito que a originaram. É a matriz de rastreabilidade se formando sozinha.
- **O campo que roteia** — cada tarefa declara se é determinística ou de agente. O executor lê esse campo e decide como rodá-la.

### O que a narradora fala

Duas etapas que andam juntas. A de ferramentas responde a uma pergunta que quase todo projeto agêntico deixa em aberto: quem implementa cada ferramenta — código determinístico, tarefa de agente, ou serviço externo publicado por MCP. No BioByte são duas ferramentas reais publicadas por um servidor MCP, a consulta à microbiologia e o cálculo do escore de risco, e vocês vão vê-las sendo chamadas de verdade. A etapa seguinte define os agentes e as tarefas. E aqui está o detalhe que dá valor ao método: toda tarefa carrega o caso de uso e o requisito que a originaram. A matriz de rastreabilidade não é montada por ninguém — ela se forma sozinha.

---

<div class="slide" id="slide-85"></div>

## Lâmina 85 — A rede de Petri: a orquestração verificável

**Tempo falado:** 50 s

![Lâmina 85](roteiro_narrado_iasdd_v10_biobyte_slides/slide_85.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Petri**
- **O que é** — lugares e transições. Os lugares guardam estado; as transições disparam quando as condições são satisfeitas.
- **Por que não é um fluxograma** — porque admite prova. Ausência de travamento, alcançabilidade de cada estado e invariantes são verificados na estrutura.
- **O que o portão confere** — que a rede é bipartida, que não há ilha inalcançável, e que cada transição tem guarda definida.
- **O que isso acrescenta** — os testes dizem que funcionou nos casos testados. A rede diz o que é estruturalmente possível acontecer.

### O que a narradora fala

Das tarefas e da sequência entre elas nasce a rede de Petri, e é a camada que mais me interessa. Ela tem lugares e transições: os lugares guardam estado, as transições disparam quando as condições estão satisfeitas. Não é um fluxograma bonito — a diferença é que ela admite prova. Ausência de travamento, alcançabilidade de cada estado e invariantes são verificados na estrutura, não testados por amostragem. O portão confere que a rede é bipartida, que não sobrou ilha inalcançável e que cada transição tem guarda. E o que isso acrescenta é de outra natureza: os testes dizem que funcionou nos casos testados; a rede diz o que é estruturalmente possível acontecer.

---

<div class="slide" id="slide-86"></div>

## Lâmina 86 — Casos de teste e geração do código

**Tempo falado:** 50 s

![Lâmina 86](roteiro_narrado_iasdd_v10_biobyte_slides/slide_86.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Testes, Código**
- **De onde saem os testes** — dos critérios dos casos de uso, por tabela de decisão — não do código. É a ordem do bloco anterior, aplicada.
- **O que eles conferem** — comportamento, não tela. “Exibe a mensagem X” não é caso de teste; “rejeita a senha errada” é.
- **A geração** — sai a aplicação inteira: telas, backend, banco, agentes, ferramentas e o executor da rede.
- **O portão final** — confere se cada tarefa do documento chegou ao código, e se cada passo de lógica virou implementação — e reporta o que não virou.

### O que a narradora fala

Duas etapas fecham a fábrica. Os casos de teste saem dos critérios dos casos de uso, por tabela de decisão, e não do código — é a ordem que eu defendi no bloco anterior, aplicada. E conferem comportamento, não tela: “exibe a mensagem tal” não é caso de teste, “rejeita a senha errada” é. Não é preciosismo: foi por causa dessa distinção que, num sistema nosso, uma tela de acesso que não conferia a senha passou despercebida. Depois vem a geração, que produz a aplicação inteira. E o portão final confere se cada tarefa do documento chegou ao código e se cada passo de lógica virou implementação — reportando o que não virou.

---

<div class="slide" id="slide-87"></div>

## Lâmina 87 — A aplicação rodando, e a bancada de execução

**Tempo falado:** 48 s

![Lâmina 87](roteiro_narrado_iasdd_v10_biobyte_slides/slide_87.png)

### O que está escrito na lâmina

- *Trilha das etapas, com estas em destaque:* **Aplicação**
- **O que roda** — a aplicação com os cadastros, os relatórios e as telas dos agentes — e um executor disparando a rede.
- **A bancada** — mostra cada tarefa em execução: a entrada que recebeu, o que o agente pensou, que ferramenta chamou, e a saída.
- **Etiquetas universais** — o executor emite marcas padronizadas em cada momento da execução. É o que torna a bancada genérica.
- **Falha não passa calada** — erro de ferramenta ou de agente aparece como falha declarada. Sucesso relatado sem trabalho feito é o defeito que mais custa caro.

### O que a narradora fala

E aqui chegamos à máquina. A aplicação roda com os cadastros, os relatórios e as telas dos agentes, e um executor dispara a rede. O que eu quero que vocês vejam é a bancada: ela mostra cada tarefa em execução com a entrada que recebeu, o que o agente pensou, que ferramenta chamou e a saída que produziu. Isso funciona para qualquer aplicação gerada, porque o executor emite um conjunto padronizado de etiquetas. E o último ponto, que é o que mais me importa: falha não passa calada. O defeito que custa mais caro num sistema agêntico não é o erro — é o sucesso relatado sem trabalho feito.

---

<div class="slide" id="slide-88"></div>

## Lâmina 88 — O que foi medido, e o que ainda é lacuna

**Tempo falado:** 52 s

![Lâmina 88](roteiro_narrado_iasdd_v10_biobyte_slides/slide_88.png)

### O que está escrito na lâmina


| Frente | Evidência concreta |
|---|---|
| Microbiologia | caso CAS-2023-001 → Staphylococcus aureus, antibiograma e marca de multirresistência, pela ferramenta MCP |
| Escore de risco | escore, nível e fatores devolvidos pela ferramenta — não redigidos pelo modelo |
| Classificação | critérios da norma aplicados: cateter, hemocultura e correlação clínica |
| Alerta | registrado na base; a notificação para fora do sistema continua declarada como lacuna |
| Relatório | arquivo gerado; o painel mostra os dados ou declara que a série está ausente |
| Execução | 22 de 23 casos de teste conferidos contra as linhas do banco |

- **Nota na lâmina:** O sistema registra também o que ainda não está implementado. Uma lacuna declarada é um item de projeto; uma lacuna escondida atrás de uma mensagem de sucesso é um risco clínico.

### O que a narradora fala

E aqui está o que foi medido, com a honestidade que o método exige. A consulta à microbiologia devolve o micro-organismo, o antibiograma e a marca de multirresistência pela ferramenta MCP. O escore de risco é devolvido pela ferramenta, não redigido pelo modelo — essa distinção é tudo. A classificação aplica os critérios da norma. O alerta é registrado, e a notificação para fora do sistema continua declarada como lacuna. Vinte e dois dos vinte e três casos de teste conferidos contra as linhas do banco. Reparem que o sistema registra também o que não está pronto: uma lacuna declarada é item de projeto; uma lacuna escondida atrás de uma mensagem de sucesso é risco clínico.

---

<div class="slide" id="slide-89"></div>

## Lâmina 89 — O pipeline completo do LangNet, do documento à aplicação

**▶ VÍDEO — 20 minutos.** a fábrica inteira, etapa por etapa, terminando na aplicação rodando

![Lâmina 89](roteiro_narrado_iasdd_v10_biobyte_slides/slide_89.png)

### O que está escrito na lâmina

- **▶ VÍDEO · 20 minutos** — a fábrica inteira, etapa por etapa, terminando na aplicação rodando
- **1.** O documento do hospital entrando, e os requisitos com procedência e natureza
- **2.** A especificação: caso de uso, fluxos de exceção e croqui de tela
- **3.** O modelo de dados apontando o próprio defeito — e a correção dita em português
- **4.** As telas e o protótipo rodando antes de existir sistema
- **5.** Ferramentas, agentes e tarefas, cada uma sabendo de onde veio
- **6.** A rede de Petri, o portão, e a geração do código
- **7.** A aplicação: cadastros, relatórios e os agentes produzindo registros
- **8.** A bancada: entradas, etiquetas, saída — e uma falha que não passa calada

### O que a narradora fala

E aqui está a demonstração final: vinte minutos percorrendo a fábrica inteira. O documento do hospital entrando, os requisitos nascendo com procedência e natureza, a especificação com os fluxos de exceção e o croqui da tela, o modelo de dados apontando o próprio defeito e sendo corrigido por conversa, as telas, o protótipo, as ferramentas, os agentes, a rede de Petri, o portão, a geração do código — e, no fim, a aplicação rodando, com os agentes produzindo registros e a bancada mostrando cada entrada e cada saída. Peço que prestem atenção numa coisa só ao longo dos vinte minutos: em nenhum momento eu edito o artefato final. Toda correção entra na etapa e o artefato é regerado.

### Produção deste vídeo

Gravar 20 minutos cobrindo, nesta ordem:

1. O documento do hospital entrando, e os requisitos com procedência e natureza
2. A especificação: caso de uso, fluxos de exceção e croqui de tela
3. O modelo de dados apontando o próprio defeito — e a correção dita em português
4. As telas e o protótipo rodando antes de existir sistema
5. Ferramentas, agentes e tarefas, cada uma sabendo de onde veio
6. A rede de Petri, o portão, e a geração do código
7. A aplicação: cadastros, relatórios e os agentes produzindo registros
8. A bancada: entradas, etiquetas, saída — e uma falha que não passa calada

---

<div class="slide" id="slide-90"></div>

## Lâmina 90 — Fechamento

**Tempo falado:** 7 s

![Lâmina 90](roteiro_narrado_iasdd_v10_biobyte_slides/slide_90.png)

### O que está escrito na lâmina

- **BLOCO 12 — Fechamento**
- *O que levar desta palestra, e por onde começar na segunda-feira.*

### O que a narradora fala

Vamos fechar. Eu quero deixar três conclusões, e uma sugestão bem concreta de por onde começar.

---

<div class="slide" id="slide-91"></div>

## Lâmina 91 — As três conclusões

**Tempo falado:** 48 s

![Lâmina 91](roteiro_narrado_iasdd_v10_biobyte_slides/slide_91.png)

### O que está escrito na lâmina

- **Primeira** — modelo não garante correção. Quem garante é o que você põe em volta dele: portão em código, saída estruturada, evidência citada.
- **Segunda** — a especificação virou o artefato principal. O código é derivado — e derivado se regera, não se remenda.
- **Terceira** — rastreabilidade deixou de ser custo e virou subproduto. Quem trabalha assim já tem o que a auditoria pede.
- **Por onde começar** — escolham um fluxo pequeno e verificável. Escrevam a especificação com critério testável, e o portão antes do agente.

### O que a narradora fala

Três conclusões. A primeira: modelo nenhum garante correção, e nenhuma versão futura vai garantir — quem garante é o que você põe em volta dele, que é portão em código, saída estruturada e evidência citada. A segunda: a especificação virou o artefato principal, e o código passou a ser derivado; e derivado se regera, não se remenda. A terceira: rastreabilidade deixou de ser custo e virou subproduto. E a sugestão para segunda-feira: escolham um fluxo pequeno e verificável do serviço de vocês, escrevam a especificação dele com critério testável, e construam o portão antes de construir o agente. Os notebooks, os vídeos e as referências ficam com vocês.

---

<div class="slide" id="slide-92"></div>

## Lâmina 92 — Capa

**Tempo falado:** 15 s

![Lâmina 92](roteiro_narrado_iasdd_v10_biobyte_slides/slide_92.png)

### O que está escrito na lâmina

- > **O gargalo deixou de ser escrever código. Passou a ser especificar com precisão o que se quer.**
- Obrigado.   ·   Perguntas

### O que a narradora fala

Eu começei com esta frase e termino com ela. O gargalo deixou de ser escrever código; passou a ser especificar com precisão o que se quer. Muito obrigado pela atenção. Vamos às perguntas.

---
