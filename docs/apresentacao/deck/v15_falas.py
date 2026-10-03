# -*- coding: utf-8 -*-
"""Falas da V15: as da V14, com as lâminas de algoritmos e de CNN explicando também as figuras."""
from v14_falas import FALAS as F14

NOVAS = {
"Histórico da IA-70 anos em 1 minuto":
"Antes de tudo, de onde veio isso: setenta anos de inteligência artificial em um minuto.",

"K Vizinhos Mais Próximos":
"Agora, um algoritmo por lâmina, começando pelo mais intuitivo. O K vizinhos mais próximos não constrói modelo nenhum: para classificar um caso novo, ele procura na base os K casos mais parecidos e faz uma votação. Na figura, os círculos azuis são a classe zero e os triângulos vermelhos a classe um; as estrelas são casos novos. Com K igual a três, cada estrela se liga aos seus três vizinhos mais próximos e recebe a classe da maioria. É ótimo para começar e para explicar, mas fica lento com bases grandes e sofre quando as variáveis não estão na mesma escala.",

"Regressão Linear":
"A regressão linear prevê um número, não uma classe. Na figura, cada x vermelho é um país: a renda per capita no eixo de baixo, o índice de desenvolvimento humano no eixo lateral. A reta azul é a que passa mais perto de todos os pontos ao mesmo tempo, e é ela que se usa para estimar o valor de um caso novo. A força desse algoritmo é ser transparente: a inclinação da reta diz quanto a saída muda quando a entrada aumenta. O limite está no nome: ele só enxerga relação em linha reta.",

"Regressão Logística":
"Apesar do nome, a regressão logística serve para classificar. Na figura da esquerda, alunos aprovados e reprovados, pela frequência e pela nota; a reta azul é o limite de decisão, que separa as duas classes. À direita está o truque: a curva em S, a sigmoide, espreme qualquer valor num número entre zero e um, que se lê como probabilidade. Em saúde é talvez o algoritmo mais usado, porque cada coeficiente vira uma razão de chances, a linguagem que o epidemiologista já usa.",

"Árvore de Decisão":
"A árvore de decisão faz uma sequência de perguntas de sim ou não. A figura mostra a primeira: a característica um é menor que zero vírgula zero seis? Essa pergunta corta o plano em dois, a faixa azul e a vermelha, e à direita está a árvore correspondente, com quantos exemplos de cada classe caem de cada lado. As perguntas seguintes vão cortando cada região até ela ficar de uma classe só. O grande valor é que a regra final pode ser lida e contestada pelo clínico; o defeito é que uma árvore sozinha decora com facilidade.",

"Random Forest — Floresta Aleatória":
"A floresta aleatória resolve exatamente esse defeito. Em vez de uma árvore, ela treina muitas, cada uma vendo uma amostra diferente dos dados. Na figura, as cinco primeiras são árvores individuais: cada uma corta o plano de um jeito diferente, e todas erram em algum lugar. O último painel é a floresta, a votação de todas: a fronteira fica mais suave e mais fiel aos dados. É um dos algoritmos mais robustos que existem para dados de tabela, e ainda diz quais variáveis mais pesaram.",

"Máquina de Vetores de Suporte":
"A máquina de vetores de suporte procura a fronteira que separa as classes com a maior margem possível, como uma estrada o mais larga possível entre dois bairros. A figura mostra o truque que a torna poderosa: no plano, os pontos azuis e vermelhos não se separam por uma reta. Acrescentando uma dimensão, que aqui é uma das características elevada ao quadrado, os pontos se afastam em três dimensões, e um plano simples passa a separá-los. Funciona muito bem com poucos exemplos e muitas variáveis.",

"K-Means — K Médias":
"E um algoritmo não supervisionado. O K-Means recebe os dados sem resposta nenhuma e os divide em K grupos, e a figura mostra o processo, painel a painel, com K igual a três. Os dados chegam sem cor. Três centros são sorteados, os triângulos. Cada ponto vai para o centro mais próximo e ganha a sua cor. Os centros se deslocam para o meio do seu grupo, os pontos são redistribuídos, e isso se repete até nada mais mudar. Serve para descobrir perfis de pacientes; o cuidado é que você precisa escolher o K.",

"Panorama: modelos proprietários":
"Um panorama dos modelos proprietários como estão hoje, fim de setembro de dois mil e vinte e seis. Em cima, as linhas de cada fabricante: a OpenAI com o GPT-6 Astra no topo, e o Sol e o Luna mais baratos; a Anthropic com o Claude Fable 5.1, o Opus 5.5, o Sonnet 5.5 e o Haiku; o Google com o Gemini 3.1 Pro e a família Flash; e a xAI, do Elon Musk, com o Grok 4.7. Embaixo, quem é melhor em quê. Para gerar código, trabalho de escritório, planilhas e interpretação de texto difícil, o Claude Opus 5.5 está na frente. Para produzir texto, a família Claude também lidera. O GPT-6 Astra ganha em raciocínio científico e em matemática. E reparem na coluna do segundo lugar: o Claude Fable 5.1, o topo da linha da Anthropic, aparece em segundo em escritório, planilhas, conhecimento e matemática. É que o Opus 5.5 saiu três semanas depois, empata com ele na maior parte do trabalho e custa menos; e o Fable continua à frente do GPT-6 Astra em código e em conhecimento. E o Grok aparece em terceiro no trabalho de escritório. Escolham o modelo pela tarefa, e citem sempre a fonte e a data, porque esses números mudam todo mês.",

"Panorama: modelos abertos":
"E os modelos abertos, que interessam por um motivo: dado de paciente que não pode sair do hospital pede um modelo rodando dentro do hospital. Em cima, os principais: o DeepSeek V4.1 Flash, de setembro, o V4 Pro, o Qwen 3.8, o Kimi K3 e o MiniMax. Embaixo, quem é melhor em quê. Para gerar código, o DeepSeek V4 Pro tem o melhor resultado publicado, com o V4.1 Flash, bem menor, logo atrás. O Kimi K3 lidera em raciocínio científico, com o Qwen 3.8 em segundo, em planilhas, com o MiniMax em segundo, e em produção de texto, onde fica atrás só do Claude. Para custo e velocidade, o V4.1 Flash, que usa só uma fração dos parâmetros por vez. E para rodar dentro de casa, o Qwen de vinte e sete bilhões, que cabe numa placa de vinte e quatro gigabytes. Atenção: pesos abertos não é código aberto; leiam a licença.",

"O pipeline de Machine Learning, do início ao fim":
"Agora vamos dar uma parada para ver uma demonstração de um notebook sobre o pipeline de Machine Learning. São dezesseis minutos com uma base real de exames de câncer de mama, benigno ou maligno. O notebook prepara e visualiza os dados, com estatísticas, histogramas e a matriz de espalhamento; separa treino e teste; escolhe o modelo com validação cruzada; treina; e avalia com precisão, recall, F-score e a matriz de confusão. No fim, prevê um caso novo. Quando forem refazer, troquem o algoritmo e comparem qual deixa escapar menos tumores malignos.",

"Treinamento e Transfer Learning":
"Agora vamos dar uma parada para ver uma demonstração de um notebook sobre deep learning e Transfer Learning. O problema é real: olhar uma tomografia do pulmão e dizer se é COVID-19 ou normal. O notebook divide as imagens em treino, validação e teste, aplica aumento de dados, reaproveita a VGG16 congelada com uma cabeça nova, treina, faz o ajuste fino e avalia com recall, precisão e especificidade. Reparem no resumo do modelo: só uns cento e trinta mil parâmetros são treinados, contra quase quinze milhões congelados.",

"Classificação e apoio à decisão em saúde":
"Agora vamos dar uma parada para ver uma demonstração de um notebook sobre IA na medicina, com dados reais, em quatro momentos. Diagnóstico: uma DenseNet treinada lê raios-X de tórax, e o Grad-CAM mostra onde ela olhou. Avaliação: curva ROC, o efeito da prevalência e a calibração. Prognóstico: num ensaio clínico de HIV com mais de dois mil pacientes, a curva de Kaplan-Meier e o modelo de Cox. E tratamento: o T-learner estima quanto cada paciente se beneficia.",

"Criação da estrutura de um Transformer":
"Agora vamos dar uma parada para ver uma demonstração de um notebook que constrói, do zero, um modelo de linguagem do tipo GPT. Ele começa pela tokenização, monta a atenção com consulta, chave, valor e a máscara causal, empilha os blocos da arquitetura, faz o pré-treino e carrega os pesos oficiais do GPT-2. E termina com dois ajustes finos: um para classificar mensagens e outro para seguir instruções, avaliado por outro modelo. É o mesmo caminho dos grandes modelos, em escala pequena.",

"Fine-tuning com LoRA: um modelo de 7B sobre infecção":
"E agora vamos dar uma parada para ver uma demonstração de um notebook sobre ajuste fino, o último degrau da escada. O modelo é o Llama 2 de sete bilhões de parâmetros, ajustado para responder sobre controle de infecção. Com LoRA, os pesos originais ficam congelados e só duas matrizes finas são treinadas, menos de um por cento dos pesos; com QLoRA, o modelo fica em quatro bits e cabe numa única placa. O vídeo compara as respostas antes e depois do ajuste.",

"RAG: um assistente de controle de infecção hospitalar":
"Agora vamos dar uma parada para ver uma demonstração de um notebook sobre RAG: um assistente de controle de infecção hospitalar. Ele junta tudo o que vimos neste bloco: carrega a base de documentos, divide em trechos, gera os embeddings, indexa com o FAISS, busca e gera a resposta com as fontes, usando o DeepSeek. No fim, a mesma pergunta respondida sem RAG e com RAG, lado a lado, e o que acontece com uma pergunta que está fora da base.",

"Agentes com CrewAI: qualificação de leads e e-mail de vendas":
"Agora vamos dar uma parada para ver uma demonstração de um notebook com o CrewAI. É um pipeline comercial: cinco agentes em duas equipes. A primeira pesquisa o interessado e a empresa na internet e dá uma nota; se a nota for boa, a segunda escreve um e-mail de vendas personalizado. Vocês vão ver os agentes e as tarefas declarados em YAML, a saída estruturada com Pydantic, o Flow ligando as duas equipes, e a execução real, com o custo em tokens.",

"AutoGen: residente e infectologista revisam pareceres da CCIH":
"E agora uma demonstração curta de um notebook com o AutoGen. Dois agentes trabalham como na comissão de controle de infecção: o residente dá um parecer rápido sobre uma hemocultura, um antibiograma ou um indicador, e o infectologista confere contra o protocolo. Se houver erro, aponta a regra e o residente refaz; se estiver certo, escreve APROVADO e a conversa termina. Uma ferramenta faz as contas exatas, que o modelo faz mal.",

"O pipeline completo do LangNet, do documento à aplicação":
"Então vamos dar uma parada para ver uma demonstração do LangNet: dez minutos percorrendo todas as etapas do pipeline sobre o BioByte. O documento do cliente e os requisitos com a sua procedência; a especificação com o caso de uso, as exceções, o esquema da tela e a versão dois; o modelo de dados corrigido por conversa; a tela e o protótipo; agentes, ferramentas, rede de Petri, código e testes. E, no fim, o sistema gerado: a tela do agente, a rede de Petri executando e a tela da tarefa.",

"App de validação rápida":
"E, por fim, vamos dar uma parada para ver uma demonstração do app de validação rápida. Nele, cada teste executa sozinho os casos de uso de uma sprint nas telas do sistema: o executor abre o sistema no navegador e preenche tudo, sem ninguém digitando. Ao fim de cada passo ele para e mostra as telas de antes e depois e a conferência automática; o validador observa, aprova ou reprova. No fim, um relatório com tudo. A máquina faz o trabalho repetitivo; o validador fica com o que importa: olhar e decidir.",

"App de validação: documentos e trilha de correções":
"Agora vamos dar uma parada para ver uma demonstração do app de validação. Ele reúne num só lugar toda a documentação de um projeto, com todas as versões: requisitos, casos de uso, planejamento e os vídeos de cada caso de uso, gerados executando o próprio sistema. O validador trabalha no tutorial guiado, pode ditar por voz e redigir a observação com IA. Cada observação volta como uma trilha de correções, até o passo ser aprovado. E ainda há notificações, monitor ao vivo e a conversa com o Claude.",

"Fine-tuning de modelos":
"Vamos olhar o último degrau mais de perto. Ajuste fino é continuar o treino de um modelo pronto com exemplos do seu domínio: centenas ou milhares de pares de pergunta e resposta, poucas épocas, e uma comparação das respostas antes e depois. Treinar todos os pesos de um modelo de bilhões de parâmetros é caro demais, e é aí que entra o LoRA, que a figura mostra. A matriz de pesos de cada camada, o W, fica congelada. Treinam-se só duas matrizes finas, B e A, cujo produto é a mudança que o modelo precisa aprender. A largura delas é o posto: com posto dezesseis, numa camada de dezesseis milhões de pesos, treinam-se só cento e trinta e um mil, menos de um por cento. No fim, B vezes A se soma a W. O QLoRA vai além e guarda o modelo em quatro bits, e assim um modelo de sete bilhões cabe numa única placa. E a regra: o ajuste fino ensina estilo, formato e jargão; informação que muda continua sendo trabalho do RAG.",

"Redes convolucionais: o caminho da imagem":
"Para imagem, ligar cada pixel a cada neurônio é inviável, e a rede convolucional faz diferente. Em cima, o caminho da imagem: filtros pequenos varrem a imagem e acham bordas; as camadas seguintes combinam bordas em partes, como olho e nariz, e depois em rostos inteiros. Embaixo, a arquitetura que produz isso. À esquerda, as camadas convolucionais empilhadas: cada neurônio de uma camada olha só um pedaço da camada de baixo. Depois o pooling, que reduz a matriz ficando com o maior valor de cada bloco. O flatten transforma a matriz num vetor. E a camada densa liga tudo a tudo e dá a resposta, por exemplo com a softmax, que devolve a probabilidade de cada classe.",
}

FALAS = dict(F14)
FALAS.update(NOVAS)
FIM = "__fim__"


def aplicar(slides):
    faltam = [s.get("titulo", FIM) for s in slides if s.get("titulo", FIM) not in FALAS]
    if faltam:
        raise SystemExit("sem fala na V15: %s" % faltam)
    for s in slides:
        s["fala"] = FALAS[s.get("titulo", FIM)]
    return slides
