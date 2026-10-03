# -*- coding: utf-8 -*-
"""Falas da V14: as da V13, com as lâminas novas e as que mudaram."""
from v13_falas import FALAS as F13

NOVAS = {
"Conteúdo da apresentação":
"Este é o nosso percurso de hoje. Começamos com um minuto de história da inteligência artificial e depois seguimos em doze blocos, em três partes. Nos fundamentos: aprendizado de máquina, redes profundas, a aplicação disso tudo na saúde, e os modelos de linguagem com o Transformer. Na engenharia em volta desses modelos: agentes, engenharia de contexto, frameworks, agentes para produção de código e protocolos. E no método: o desenvolvimento orientado a especificação e o LangNet, a nossa implementação dele. Ao fim de vários blocos a gente faz uma pausa para ver um notebook sendo executado, e esses notebooks ficam com vocês. E o fio que atravessa tudo é uma ideia só: quando o código sai em minutos, o gargalo passa a ser especificar com precisão o que se quer.",

"Histórico da IA":
"Antes de tudo, de onde veio isso.",

"Machine Learning":
"Primeiro bloco, Machine Learning: o que diferencia um programa comum de um programa que aprende, e como se monta um projeto do início ao fim.",

"Exemplo de infraestrutura de desenvolvimento de IA local":
"E um exemplo de infraestrutura local para desenvolver IA. Uma máquina principal com um i7 de décima segunda geração, cento e vinte e oito gigabytes de memória e três placas, uma RTX 5080, uma 5060 e uma 4060, com dois discos NVMe de dois terabytes: ela serve os modelos abertos e faz os treinos pesados. E uma máquina de apoio, com noventa e seis gigabytes e uma RTX 3060, para os treinos menores e os notebooks. A vantagem de ter isso em casa: o dado sensível não sai da instituição, e o modelo local faz o trabalho repetitivo sem gastar tokens pagos.",

"Engenharia de contexto":
"Um agente só é tão bom quanto aquilo que ele sabe na hora de decidir. Esse é o assunto do bloco: engenharia de contexto.",

"Busca convencional × busca vetorial":
"E aqui está a diferença que faz o RAG funcionar. À esquerda, a busca convencional, por palavra: pergunto por bacteremia por cateter, e o índice só devolve o texto que tem essas palavras. O documento certo, que fala em infecção de corrente sanguínea por cateter, fica de fora, porque usa outras palavras para a mesma coisa. À direita, a busca vetorial. Cada texto vira um embedding, um vetor com mais de mil números que representa o seu sentido. Textos parecidos ficam perto nesse espaço de significado. A pergunta também vira vetor, e a busca pega os vizinhos mais próximos, medidos pela similaridade de cosseno. Por isso ela encontra bacteremia, infecção de corrente sanguínea e ICS por cateter juntos, e deixa de fora fratura e dieta.",

"Panorama: modelos proprietários":
"Um panorama dos modelos proprietários como estão hoje, fim de setembro de dois mil e vinte e seis. A OpenAI tem no topo o GPT-6 Astra, lançado no começo do mês, com o Sol e o Luna, mais baratos, e ainda a linha 5.6. A Anthropic tem o Claude Fable 5.1 no topo, depois o Opus 5.5, o Sonnet 5.5, recém-lançado, e o Haiku 4.5; o Mythos, o mais poderoso, só com acesso restrito. O Google tem o Gemini 3.1 Pro e a família Flash, com o Gemini 4 anunciado. E a xAI, a empresa do Elon Musk, lançou o Grok 4.7 na semana passada. Essa lista muda todo mês: quando citarem um modelo ou um número, citem a fonte e a data.",

"Panorama: modelos abertos":
"E os modelos abertos, que interessam por um motivo: dado de paciente que não pode sair do hospital pede um modelo rodando dentro do hospital. O mais recente é o DeepSeek V4.1 Flash, de setembro: quinhentos e cinquenta bilhões de parâmetros, mas só de oito a dezesseis bilhões ativos por vez, licença MIT, e ele já supera o V4 Pro, que é bem maior. A Alibaba abriu o Qwen 3.8 Max, de dois vírgula quatro trilhões, e o Qwen de vinte e sete bilhões, que roda numa placa de vinte e quatro gigabytes. E atenção: pesos abertos não é código aberto; leiam a licença.",

"LangChain: peças prontas, encadeadas":
"Começo pelo mais usado, o LangChain. A ideia é ter peças prontas: o modelo de prompt, o modelo de linguagem, o leitor da saída, o recuperador, as ferramentas e a memória. E elas se ligam numa cadeia com a barra vertical, como um encanamento; o recuperador, a ferramenta e a memória entram na cadeia quando é preciso. No primeiro arquivo, uma cadeia de três peças: o prompt, o modelo e o leitor da saída, executada com o caso de entrada. No segundo, a mesma ideia com RAG: o recuperador busca no índice FAISS, o resultado entra como contexto no prompt, e o modelo responde. É a base sobre a qual o LangGraph foi construído.",
}

FALAS = dict(F13)
FALAS.update(NOVAS)
FIM = "__fim__"


def aplicar(slides):
    faltam = [s.get("titulo", FIM) for s in slides if s.get("titulo", FIM) not in FALAS]
    if faltam:
        raise SystemExit("sem fala na V14: %s" % faltam)
    for s in slides:
        s["fala"] = FALAS[s.get("titulo", FIM)]
    return slides
