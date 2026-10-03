# -*- coding: utf-8 -*-
"""Falas da V12: só as lâminas que mudaram. As demais mantêm a fala da V11."""
from v11_falas import FALAS as F11

NOVAS = {
"Conteúdo da apresentação":
"Este é o nosso percurso de hoje, em doze blocos e três partes. Nos fundamentos: aprendizado de máquina, redes profundas, a aplicação disso tudo na saúde, e os modelos de linguagem com o Transformer. Na engenharia em volta desses modelos: agentes, contexto e recuperação de documentos, frameworks, agentes para produção de código e protocolos. E no método: o desenvolvimento orientado a especificação e o LangNet, a nossa implementação dele. Ao fim de vários blocos a gente faz uma pausa para ver um notebook sendo executado, e esses notebooks ficam com vocês. E o fio que atravessa tudo é uma ideia só: quando o código sai em minutos, o gargalo passa a ser especificar com precisão o que se quer.",

"Introdução e Machine Learning":
"Agora, o primeiro bloco: o que diferencia um programa comum de um programa que aprende, e como se monta um projeto de aprendizado de máquina.",

"A rede de múltiplas camadas":
"A solução para o limite do neurônio isolado é empilhar neurônios, e esta figura, da nossa apresentação original, mostra como. À esquerda, a camada de entrada: as variáveis x um e x dois, mais uma entrada fixa igual a um, o viés. No meio, duas camadas ocultas. À direita, a camada de saída, com y um e y dois. Cada seta é uma conexão com o seu peso; W um, W dois e W três são os conjuntos de pesos entre uma camada e a seguinte. As camadas do meio combinam as entradas em conceitos cada vez mais elaborados. É isso que permite traçar fronteiras de qualquer formato.",

"Treinamento e Transfer Learning":
"Vamos fazer uma pausa aqui para o segundo notebook, de treinamento e Transfer Learning. Ele põe as duas coisas lado a lado: a mesma tarefa treinada do zero e por reaproveitamento. Vocês vão ver a curva que não sobe quando se treina do zero com poucos dados, e a mesma curva subindo depois de carregar a rede pré-treinada. E, no fim, o mapa mostrando em que região da imagem a rede se apoiou.",

"Inteligência Artificial na saúde":
"Com o aprendizado de máquina e as redes profundas na mão, vamos ver onde tudo isso entra na saúde. São três frentes: prognóstico, diagnóstico e tratamento.",

"Classificação e apoio à decisão em saúde":
"Vamos fazer uma pausa aqui para o terceiro notebook, de apoio à decisão em saúde. Vocês vão ver um escore de risco sendo construído e avaliado do jeito certo: a base e o desfecho, por que a acurácia mente nesse cenário, a regressão logística com os coeficientes virando razão de chances, a árvore produzindo uma regra legível, e a curva de sobrevivência. E ele termina no ponto que mais importa: o que o modelo não pode decidir sozinho.",

"De onde veio o Transformer":
"A arquitetura que está por trás de todos esses modelos vem de um artigo de dois mil e dezessete com um título provocativo: A atenção é tudo de que você precisa. Antes dele, as redes recorrentes liam a frase palavra por palavra, em sequência: esqueciam o começo de frases longas e quase não podiam ser treinadas em paralelo. A atenção deixou cada token se relacionar diretamente com todos os outros. E, com o treino em paralelo, escalar deixou de ser impossível.",

"O Transformer":
"E esta é a arquitetura, o Transformer. À esquerda, o codificador: a frase de entrada vira vetores, recebe a informação de posição e passa por um bloco de atenção e por uma rede feed-forward, com soma e normalização entre eles; esse bloco se repete N vezes. No centro, o decodificador, que gera a saída um token por vez. Ele tem uma atenção mascarada, que só olha para o que já foi gerado, e uma atenção cruzada, que consulta o que o codificador produziu; é a seta azul. No topo, a saída vira a probabilidade do próximo token. À direita está o coração disso tudo, a matriz de atenção: cada linha é um token perguntando, cada coluna é um token consultado, e a cor forte mostra para onde ele olhou. Febre olha para paciente. Os modelos de conversa de hoje usam só o decodificador.",

"Agentes para produção de código":
"Agora, os agentes para produção de código: onde o trabalho de programação de fato acontece hoje.",

"Os protocolos: MCP, A2A e OKF":
"Quando agentes, ferramentas e pessoas precisam se entender, entram os protocolos, e vale conhecer três. O MCP, Model Context Protocol, liga um agente ou um modelo a ferramentas, dados, sistemas e APIs: cada ferramenta é publicada por um servidor com nome, parâmetros e formato de retorno. O A2A, Agent2Agent, cuida da conversa entre agentes: um agente descobre o que o outro sabe fazer, delega uma tarefa e acompanha o andamento. E o OKF, Open Knowledge Format, é um formato aberto para organizar e trocar conhecimento, que tanto um agente quanto uma pessoa conseguem ler. Nos três, o que era código colado vira serviço com contrato.",

"O mapa: vertical e horizontal":
"E este mapa mostra onde cada um se encaixa. No centro, o agente. No eixo vertical, para cima, o MCP, que o conecta às ferramentas, aos bancos e às APIs. No eixo horizontal, à esquerda, o A2A, que o liga a outro agente. À direita, no mesmo eixo, o OKF: a base de conhecimento aberta que agentes consomem e que pessoas também leem, como mostra o bonequinho ao lado. Resumindo: o MCP responde o que eu posso fazer; o A2A, com quem eu posso contar; o OKF, o que nós sabemos.",

"Conhecimento em formato aberto":
"E vale olhar o OKF mais de perto, porque ele é surpreendentemente simples. Um pacote de conhecimento é um diretório de arquivos de texto em markdown, sem banco e sem servidor, e os arquivos se citam por links comuns, o que transforma o diretório numa rede. Para um hospital: as definições de caso, as fórmulas dos indicadores e os procedimentos da comissão, legíveis por agente e revisáveis por um infectologista.",

"__fim__":
"O gargalo deixou de ser escrever código; passou a ser especificar com precisão o que se quer. Muito obrigado pela atenção. Fico à disposição para as perguntas.",

"O pipeline completo do LangNet, do documento à aplicação":
"Então vamos fazer uma pausa aqui para a demonstração final: dez minutos com o LangNet percorrendo todas as etapas do pipeline sobre o BioByte. Vocês vão ver o documento do cliente e os requisitos com a sua procedência; a especificação com o caso de uso, as exceções, o esquema da tela e a versão dois; o modelo de dados corrigido por conversa e a comparação entre versões; a tela e o protótipo editados ao mesmo tempo; agentes, ferramentas, rede de Petri, código e testes. E, no fim, o sistema gerado: a tela do agente, a rede de Petri executando com o token andando, e a tela da tarefa em execução.",
}

FALAS = dict(F11)
FALAS.update(NOVAS)
FIM = "__fim__"


def aplicar(slides):
    faltam = []
    for s in slides:
        k = s.get("titulo", FIM)
        if k in FALAS:
            s["fala"] = FALAS[k]
        else:
            faltam.append(k)
    if faltam:
        raise SystemExit("sem fala na V12: %s" % faltam)
    return slides
