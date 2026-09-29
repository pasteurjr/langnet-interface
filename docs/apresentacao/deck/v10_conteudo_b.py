# -*- coding: utf-8 -*-
"""V10 · parte B — modelos de linguagem e Transformer, agentes, contexto e RAG, frameworks."""

SLIDES = [

    # ───────────────────────── BLOCO 4 ─────────────────────────
    dict(tipo="divisor", bloco=4, titulo="Modelos de linguagem e Transformer",
         mensagem="O que é um modelo de linguagem, de onde veio o Transformer, e o que a escala trouxe junto.",
         fala="O quarto bloco muda de terreno. Saímos do classificador que responde sim ou não e entramos nos "
              "modelos de linguagem. Vamos ver o que eles são de fato, de onde veio a arquitetura que os "
              "viabilizou, e o que a escala trouxe junto — inclusive o que ela não resolveu."),

    dict(tipo="cartoes", bloco=4, chapeu="Modelos de linguagem", titulo="O que é um modelo de linguagem",
         destaque="Um modelo que estima qual é o próximo pedaço de texto, dado todo o texto anterior.",
         cartoes=[
             ("O token", "a unidade não é a palavra, é o token — um pedaço de palavra. “Hemocultura” pode virar três ou quatro tokens."),
             ("O treinamento", "prever o próximo token sobre um corpus imenso. Nenhum rótulo humano: o próprio texto é a resposta."),
             ("A geração", "o modelo devolve uma distribuição de probabilidade; sorteia-se um token, acrescenta-se ao texto e repete-se."),
             ("O que isso implica", "ele não consulta uma base de fatos. Ele produz a continuação mais provável — e é por isso que inventa com fluência.", "warn"),
         ],
         fala="Um modelo de linguagem é, no fundo, um estimador: dado todo o texto anterior, qual é o próximo "
              "pedaço de texto. A unidade não é a palavra, é o token, um pedaço de palavra — “hemocultura” pode "
              "virar três ou quatro tokens. O treinamento consiste em prever o próximo token sobre um corpus imenso, "
              "e não exige rótulo humano nenhum: o próprio texto é a resposta. Na hora de gerar, o modelo devolve "
              "uma distribuição de probabilidade, sorteia-se um token, acrescenta-se ao texto e repete-se. Tirem "
              "daqui a consequência mais importante: ele não consulta uma base de fatos, ele produz a continuação "
              "mais provável. É exatamente por isso que ele inventa com fluência — e por que precisaremos, mais "
              "adiante, de recuperação de documentos e de portões determinísticos."),

    dict(tipo="cartoes", bloco=4, chapeu="Modelos de linguagem", titulo="De onde veio o Transformer",
         destaque="“Attention Is All You Need” · Vaswani et al. · Google Brain e University of Toronto · 2017",
         cartoes=[
             ("Antes", "redes recorrentes e LSTM processavam a sequência passo a passo: dependências longas se perdiam e o treinamento quase não paralelizava."),
             ("A contribuição", "a atenção permite que cada token se relacione diretamente com todos os outros, sem passar pela recorrência."),
             ("O impacto", "com o treinamento paralelo, escalar deixou de ser impossível. É essa arquitetura que sustenta todos os modelos de hoje."),
         ],
         fala="A arquitetura tem data e endereço: o artigo “Attention Is All You Need”, de Vaswani e colegas, do "
              "Google Brain e da Universidade de Toronto, publicado em dois mil e dezessete. Antes dele, as redes "
              "recorrentes e as LSTM processavam a sequência passo a passo: as dependências longas se perdiam pelo "
              "caminho e o treinamento quase não paralelizava, o que punha um teto no tamanho dos modelos. A "
              "contribuição do artigo foi a atenção: cada token passa a se relacionar diretamente com todos os "
              "outros, sem depender da recorrência. E o efeito colateral foi o decisivo — como tudo passou a ser "
              "calculável em paralelo, escalar deixou de ser impossível. Todos os modelos de linguagem de hoje "
              "descendem desse artigo."),

    dict(tipo="cartoes", bloco=4, chapeu="Modelos de linguagem", titulo="Anatomia: consulta, chave e valor",
         cartoes=[
             ("Q, K e V", "cada token faz uma pergunta (consulta), todos anunciam o que têm (chave), e a semelhança entre as duas decide de quem ele copia informação (valor)."),
             ("Múltiplas cabeças", "várias relações capturadas em paralelo — cada cabeça olhando um aspecto diferente da mesma frase."),
             ("O ponto de engenharia", "a atenção é quadrática no tamanho da entrada. Custo por token, tamanho da janela e toda a economia de contexto nascem dessa quadrática.", "warn"),
         ],
         fala="A anatomia, em uma frase. Cada token faz uma pergunta — a consulta. Todos os tokens anunciam o que "
              "têm — a chave. A semelhança entre a pergunta e o anúncio decide de quem esse token vai copiar "
              "informação — o valor. Consulta, chave e valor: Q, K e V. Isso acontece em várias cabeças ao mesmo "
              "tempo, cada uma capturando um aspecto diferente da mesma frase: uma olha concordância, outra olha "
              "referência, outra olha o assunto. E guardem o ponto de engenharia: a atenção é quadrática no tamanho "
              "da entrada. Dobrar o texto quadruplica a conta. Custo por token, limite de janela e toda a economia "
              "de contexto que vamos discutir no bloco seis nascem dessa quadrática."),

    dict(tipo="cartoes", bloco=4, chapeu="Modelos de linguagem", titulo="Escala, e o que veio com ela",
         cartoes=[
             ("O que a escala trouxe", "capacidades que ninguém programou: seguir instrução, traduzir, resumir, escrever código, raciocinar em passos."),
             ("Mistura de especialistas", "modelos enormes que ativam só uma fração dos parâmetros por token — trilhões de parâmetros totais, dezenas de bilhões ativos."),
             ("O que a escala não resolveu", "a invenção confiante, a sensibilidade à forma do pedido e a ausência de garantia de correção.", "warn"),
             ("A consequência de projeto", "se o modelo não garante correção, a garantia tem de vir de fora dele. Esse é o fio que percorre o resto da palestra."),
         ],
         fala="O que a escala trouxe foi surpreendente: capacidades que ninguém programou explicitamente — seguir "
              "instrução, traduzir, resumir, escrever código, raciocinar em passos. Elas aparecem à medida que o "
              "modelo cresce. Do lado da arquitetura, a novidade recente é a mistura de especialistas: modelos com "
              "trilhões de parâmetros totais que ativam só algumas dezenas de bilhões por token, o que dá capacidade "
              "de modelo gigante com custo de modelo médio. Mas registrem também o que a escala não resolveu: a "
              "invenção confiante, a sensibilidade à forma do pedido, e a ausência de qualquer garantia de "
              "correção. E daí sai a consequência de projeto que percorre todo o resto desta palestra: se o modelo "
              "não garante correção, a garantia tem de vir de fora dele."),

    dict(tipo="codigo", bloco=4, chapeu="Modelos de linguagem", titulo="Inferência: os parâmetros que importam",
         intro="A mesma chamada, dois resultados diferentes — e a escolha não é de gosto.",
         codigo="\n".join([
             '# código, extração, classificação: determinístico',
             'resp = modelo.gerar(prompt, temperatura=0.0)',
             '',
             '# exploração de hipóteses, redação: criativo',
             'resp = modelo.gerar(prompt, temperatura=1.0)',
         ]),
         explicacao="Temperatura e top-p regulam o sorteio do próximo token. "
                    "O cache de chaves-valores reaproveita contas já feitas — menos custo e menos espera. "
                    "A quantização reduz a precisão dos pesos para o modelo caber na memória de vídeo. "
                    "Regra prática: código e extração estruturada pedem temperatura baixa; exploração pede o contrário.",
         fala="Na hora de usar, quatro parâmetros fazem quase toda a diferença. A temperatura e o top-p regulam o "
              "sorteio do próximo token: temperatura zero deixa a saída praticamente determinística, temperatura "
              "alta abre o leque. O cache de chaves-valores reaproveita contas já feitas entre chamadas, e derruba "
              "custo e espera. A quantização reduz a precisão dos pesos para o modelo caber na memória de vídeo que "
              "você tem. E fica a regra prática: código e extração estruturada pedem temperatura baixa; exploração "
              "de hipóteses pede o contrário. É a mesma chamada — o resultado é outro."),

    dict(tipo="tabela", bloco=4, chapeu="Modelos de linguagem", titulo="Panorama: modelos proprietários",
         colunas=["Modelo", "Fabricante", "SWE-bench Verified", "Fonte da medição"],
         linhas=[["*GPT-5.6 Sol", "OpenAI", "~96%", "Vals AI (independente)"],
                 ["*Claude Fable 5", "Anthropic", "~95%", "medição independente"],
                 ["*Gemini 3.1 Pro", "Google", "agrupamento superior", "—"]],
         nota="SWE-bench Verified mede correção de defeitos reais de software. Ressalva obrigatória: o número do "
              "fabricante e o de uma medição independente divergem, às vezes muito — cite sempre a fonte e a data.",
         fala="Um panorama rápido dos proprietários, com uma ressalva que eu peço que vocês levem a sério. O teste "
              "citado mede correção de defeitos reais de software, e os três modelos de ponta estão hoje num "
              "patamar parecido. A ressalva é esta: o número divulgado pelo fabricante e o número de uma medição "
              "independente divergem, às vezes muito. Quando vocês forem citar desempenho de modelo num documento "
              "ou numa decisão de compra, citem a fonte e a data da medição. Sem isso, o número não significa nada "
              "— e essa tabela envelhece em semanas."),

    dict(tipo="tabela", bloco=4, chapeu="Modelos de linguagem", titulo="Panorama: modelos abertos",
         colunas=["Modelo", "Arquitetura", "Contexto", "Licença", "Onde roda"],
         linhas=[["*Kimi K3", "2,8T / 104B ativos", "1M", "pesos abertos", "infraestrutura séria"],
                 ["*DeepSeek-V4-Pro", "1,6T / 49B ativos", "1M", "MIT", "cluster"],
                 ["*DeepSeek-V4-Flash", "284B / 13B ativos", "1M", "MIT", "servidor médio"],
                 ["*Qwen3.8-27B", "denso 27,8B · multimodal", "262K", "Apache-2.0", "24 GB de vídeo"],
                 ["*MiniMax M3", "428B / 23B ativos", "1M", "comunitária ⚠", "ver a licença"]],
         nota="Alerta jurídico: “pesos abertos” não é a mesma coisa que “código aberto”. MIT e Apache-2.0 são "
              "livres para uso comercial; licenças comunitárias podem não ser. Em saúde, isso decide se o modelo "
              "pode rodar dentro do hospital com o dado do paciente.",
         fala="E os abertos, que para vocês interessam mais, por um motivo específico: dado de paciente que não "
              "pode sair do hospital exige modelo rodando dentro do hospital. A linha que eu destaco é a do "
              "Qwen três ponto oito de vinte e sete bilhões: é denso, é multimodal, tem licença Apache, e roda numa "
              "placa de vinte e quatro gigabytes — quer dizer, numa máquina que o setor de informática de vocês "
              "consegue comprar. É esse o modelo que roda no nosso laboratório. E vai o alerta jurídico: “pesos "
              "abertos” não é a mesma coisa que “código aberto”. MIT e Apache são livres para uso comercial; "
              "licenças comunitárias, muitas vezes, não são. Leiam a licença antes de projetar em cima do modelo."),

    dict(tipo="cartoes", bloco=4, chapeu="Modelos de linguagem", titulo="A escada da adaptação",
         destaque="Quatro degraus, do mais barato ao mais caro. Suba um degrau só quando o anterior não bastar.",
         cartoes=[
             ("1 · Instrução", "escrever melhor o pedido e dar exemplos. Custo quase zero, e resolve mais do que se imagina."),
             ("2 · Contexto", "trazer para dentro do pedido o documento certo — protocolo, norma, prontuário. É o bloco seis."),
             ("3 · Ferramentas", "deixar o modelo consultar o sistema real em vez de lembrar. É o bloco cinco."),
             ("4 · Ajuste fino", "mudar os pesos. Só quando se quer ensinar um formato ou um jargão que não cabe no pedido.", "warn"),
         ],
         fala="Quando o modelo não faz o que você quer, existe uma escada — e quase todo mundo começa pelo degrau "
              "errado. O primeiro degrau é a instrução: escrever melhor o pedido e dar exemplos; custa quase nada e "
              "resolve mais do que se imagina. O segundo é o contexto: trazer para dentro do pedido o documento "
              "certo, o protocolo, a norma. O terceiro é ferramenta: deixar o modelo consultar o sistema real em vez "
              "de lembrar. E só o quarto é ajuste fino, que muda os pesos do modelo. Subam um degrau apenas quando o "
              "anterior comprovadamente não bastar. Ajuste fino feito cedo demais é dinheiro queimado — e ele "
              "não ensina fato novo, ensina formato e jargão."),

    dict(tipo="cartoes", bloco=4, chapeu="Modelos de linguagem", titulo="Ajuste fino: o que é e o que custa",
         cartoes=[
             ("Ajuste fino supervisionado", "continua o treinamento com pares de pergunta e resposta do seu domínio. O gargalo é o dado, não a máquina."),
             ("Quantos exemplos", "da ordem de milhares de pares bem escritos. Poucos e ruins pioram o modelo em vez de melhorar."),
             ("LoRA", "em vez de mexer em todos os pesos, treina matrizes pequenas acopladas à rede. Reduz o custo em uma ordem de grandeza."),
             ("QLoRA", "LoRA sobre um modelo quantizado: ajuste fino de um modelo grande cabendo numa única placa de vídeo."),
         ],
         fala="Se você chegar ao quarto degrau, vale saber o que ele é. Ajuste fino supervisionado é continuar o "
              "treinamento do modelo com pares de pergunta e resposta do seu domínio. O gargalo não é a máquina, é o "
              "dado: da ordem de milhares de pares bem escritos, e pares poucos e mal feitos pioram o modelo em vez "
              "de melhorar. A técnica que barateou isso chama-se LoRA: em vez de mexer em todos os pesos, treinam-se "
              "matrizes pequenas acopladas à rede, o que reduz o custo em uma ordem de grandeza. E a variante "
              "QLoRA aplica a mesma ideia sobre um modelo quantizado, permitindo ajustar um modelo grande dentro de "
              "uma única placa de vídeo. É assim que um grupo pequeno consegue fazer ajuste fino hoje."),

    dict(tipo="video", bloco=4, titulo="Tokens, atenção e geração, por dentro", minutos=8,
         resumo="abrindo o modelo para ver o que ele faz a cada passo",
         percurso=["O tokenizador: a frase clínica virando tokens",
                   "O mapa de atenção: a que cada token está olhando",
                   "A distribuição do próximo token, antes do sorteio",
                   "Temperatura zero e temperatura alta, sobre o mesmo pedido",
                   "A janela de contexto enchendo — e o que acontece quando estoura",
                   "Uma invenção confiante, flagrada e explicada"],
         fala="O quarto vídeo abre o modelo. Vocês vão ver o tokenizador quebrando uma frase clínica, o mapa de "
              "atenção mostrando a que cada token está olhando, a distribuição do próximo token antes do sorteio, e "
              "o mesmo pedido saindo diferente com temperatura zero e temperatura alta. E termina com uma invenção "
              "confiante sendo flagrada — para que ninguém saia daqui achando que fluência é sinal de correção."),

    # ───────────────────────── BLOCO 5 ─────────────────────────
    dict(tipo="divisor", bloco=5, titulo="Agentes",
         mensagem="Entrada, tarefa e saída; contexto, memória e ferramentas; o ciclo agêntico e a composição.",
         fala="Quinto bloco: agentes. Vamos sair do modelo que responde e chegar ao programa que faz. Entrada, "
              "tarefa e saída; contexto, memória e ferramentas; o ciclo que o agente executa; e como se compõem "
              "vários deles — inclusive quando isso não compensa."),

    dict(tipo="cartoes", bloco=5, chapeu="Agentes", titulo="De modelo para agente",
         destaque="Um modelo responde. Um agente age — e o que muda é bem pouco código.",
         cartoes=[
             ("O modelo", "recebe texto e devolve texto. Não consulta nada, não altera nada, não lembra de nada entre chamadas."),
             ("O agente", "recebe um objetivo, escolhe ações, executa-as por meio de ferramentas, observa o resultado e decide o passo seguinte."),
             ("A peça nova", "o laço. E, com ele, a capacidade de causar efeito no mundo — inclusive efeito indesejado.", "warn"),
         ],
         fala="A diferença entre modelo e agente é menor do que o vocabulário sugere. Um modelo recebe texto e "
              "devolve texto: não consulta nada, não altera nada, não lembra de nada entre uma chamada e outra. Um "
              "agente recebe um objetivo, escolhe uma ação, executa essa ação por meio de uma ferramenta, observa o "
              "resultado e decide o passo seguinte. A peça nova é o laço. E, junto com o laço, vem a capacidade de "
              "causar efeito no mundo — gravar no banco, enviar uma mensagem, alterar um registro. Inclusive efeito "
              "indesejado, o que é exatamente o motivo pelo qual o resto deste bloco existe."),

    dict(tipo="cartoes", bloco=5, chapeu="Agentes", titulo="Definição operacional, sem misticismo",
         cartoes=[
             ("Objetivo", "o que se quer obtido, escrito de forma verificável. Sem isso, não há como dizer se o agente terminou."),
             ("Contexto", "o que ele sabe nesta execução: a instrução, os documentos trazidos, o estado do sistema."),
             ("Ferramentas", "o que ele pode fazer. Cada ferramenta tem nome, parâmetros e um contrato de retorno."),
             ("Memória", "o que atravessa execuções. Distinga sempre memória de contexto — confundi-las é fonte de bug sutil."),
             ("Critério de parada", "quando ele para. Por sucesso, por limite de passos, ou por falha declarada.", "warn"),
         ],
         fala="Vamos à definição operacional, sem misticismo. Um agente tem cinco peças. Um objetivo, escrito de "
              "forma verificável — sem isso não há como dizer se ele terminou. Um contexto, que é o que ele sabe "
              "nesta execução: a instrução, os documentos trazidos, o estado do sistema. Um conjunto de ferramentas, "
              "que é o que ele pode fazer, cada uma com nome, parâmetros e contrato de retorno. Uma memória, que é "
              "o que atravessa execuções — e eu insisto em distinguir memória de contexto, porque confundir as duas "
              "é fonte de defeito sutil. E um critério de parada: por sucesso, por limite de passos, ou por falha "
              "declarada. Se alguma dessas cinco peças estiver faltando no seu projeto, ele vai falhar em produção."),

    dict(tipo="cartoes", bloco=5, chapeu="Agentes", titulo="O laço agêntico",
         cartoes=[
             ("1 · Pensar", "o modelo recebe o objetivo e o estado, e decide qual é a próxima ação."),
             ("2 · Pedir a ferramenta", "ele não executa nada. Ele emite um pedido: este nome de ferramenta, com estes argumentos."),
             ("3 · O programa executa", "quem chama a ferramenta é o seu código — não o modelo. Aqui entram permissão, limite e registro."),
             ("4 · Observar e repetir", "o resultado volta ao contexto e o laço recomeça, até o critério de parada."),
         ],
         fala="O laço tem quatro passos e eu quero que o terceiro fique gravado. Primeiro, o modelo recebe o "
              "objetivo e o estado e decide qual é a próxima ação. Segundo, ele pede a ferramenta: emite um nome e "
              "um conjunto de argumentos. Ele não executa nada — nenhum modelo executa nada. Terceiro, quem executa "
              "a ferramenta é o seu programa, e é exatamente aí que entram a permissão, o limite e o registro de "
              "auditoria. Quarto, o resultado volta para o contexto e o laço recomeça, até o critério de parada. "
              "Essa separação entre quem pede e quem executa é a coisa mais importante deste bloco: é ela que "
              "permite que um sistema com agente seja auditável."),

    dict(tipo="codigo", bloco=5, chapeu="Agentes", titulo="Uso de ferramenta, sem framework nenhum",
         intro="O laço inteiro cabe em vinte linhas. Framework é conveniência, não requisito.",
         codigo="\n".join([
             'ferramentas = [{"name": "consultar_microbiologia",',
             '                "parameters": {"caso": "string"}}]',
             '',
             'while True:',
             '    r = modelo.chamar(mensagens, tools=ferramentas)',
             '    if not r.tool_calls:',
             '        return r.texto                  # terminou',
             '',
             '    for chamada in r.tool_calls:',
             '        # QUEM EXECUTA É O SEU CÓDIGO',
             '        saida = MINHAS_FUNCOES[chamada.name](**chamada.args)',
             '        mensagens.append(resultado(chamada.id, saida))',
         ]),
         explicacao="Declare as ferramentas, chame o modelo, execute o que ele pediu, devolva o resultado, repita. "
                    "É isto que todo framework de agente faz por baixo. "
                    "Comece assim: quando o laço próprio ficar insuficiente, você vai saber exatamente por quê — "
                    "e aí escolhe o framework pelo motivo certo.",
         fala="E aqui está o laço inteiro, sem framework nenhum. Você declara as ferramentas disponíveis, chama o "
              "modelo, e olha o que voltou: se ele não pediu ferramenta, acabou, devolve o texto. Se pediu, o seu "
              "código executa a função correspondente e devolve o resultado para a conversa. Repete. São vinte "
              "linhas, e é isso que todo framework de agente faz por baixo. Eu mostro esse código por uma razão "
              "prática: comecem assim. Quando o laço próprio ficar insuficiente, vocês vão saber exatamente por que "
              "ficou — e aí escolhem o framework pelo motivo certo, em vez de escolher por moda."),

    dict(tipo="cartoes", bloco=5, chapeu="Agentes", titulo="Os padrões de composição",
         cartoes=[
             ("Encadeamento", "a saída de um passo é a entrada do seguinte. Simples, previsível, e resolve a maioria dos casos."),
             ("Roteamento", "um classificador decide qual especialista atende. Barato e muito eficaz."),
             ("Paralelismo", "várias tarefas independentes ao mesmo tempo, com agregação no fim."),
             ("Orquestrador e executores", "um agente planeja e distribui; os outros executam pedaços."),
             ("Avaliador e otimizador", "um produz, outro critica, e o ciclo repete até o critério ser atendido."),
             ("Autonomia com portão", "o agente decide o caminho, mas cada etapa passa por uma verificação em código.", "good"),
         ],
         fala="Há seis maneiras de compor. Encadeamento: a saída de um passo é a entrada do seguinte — simples, "
              "previsível e resolve a maioria dos casos reais. Roteamento: um classificador barato decide qual "
              "especialista atende. Paralelismo, para tarefas independentes, com agregação no fim. Orquestrador e "
              "executores: um agente planeja e distribui, os outros executam pedaços. Avaliador e otimizador: um "
              "produz, outro critica, e repete até o critério ser atendido. E o sexto, que é o que interessa em "
              "domínio regulado: autonomia com portão — o agente escolhe o caminho, mas cada etapa passa por uma "
              "verificação escrita em código. É esse o padrão do sistema que vou mostrar no fim."),

    dict(tipo="cartoes", bloco=5, chapeu="Agentes", titulo="Multiagente: quando compensa, e quando não",
         cartoes=[
             ("Compensa", "quando as subtarefas são de fato paralelizáveis e os contextos, isolados. As duas condições, juntas."),
             ("Não compensa", "em fluxo linear. Quatro a quinze vezes mais tokens para reimplementar o que um condicional resolveria.", "warn"),
             ("A perda de contexto", "cada repasse entre agentes perde informação — como fotocópia de fotocópia."),
             ("A pergunta a fazer", "esta divisão existe porque o problema pede, ou porque a arquitetura ficou bonita no diagrama?"),
         ],
         fala="Sobre multiagente, eu vou na contramão do entusiasmo. Só compensa quando duas condições valem ao "
              "mesmo tempo: as subtarefas são de fato paralelizáveis, e os contextos são isolados. Se as partes não "
              "são independentes, o custo explode sem ganho — medidas em fluxo linear mostram de quatro a quinze "
              "vezes mais tokens para reimplementar o que um condicional resolveria em uma linha. E há um efeito que "
              "quase ninguém contabiliza: a passagem de contexto entre agentes perde informação, como fotocópia de "
              "fotocópia. A pergunta a fazer diante de qualquer desenho multiagente é: esta divisão existe porque o "
              "problema pede, ou porque ficou bonita no diagrama?"),

    dict(tipo="cartoes", bloco=5, chapeu="Agentes", titulo="Por que agentes falham em produção",
         destaque="Noventa e cinco por cento de acerto por passo, vinte passos: trinta e seis por cento de sucesso no fim.",
         cartoes=[
             ("O erro composto", "a confiabilidade multiplica ao longo da cadeia. É aritmética, não pessimismo."),
             ("Os modos de falha", "laço infinito, ferramenta inventada, contexto contaminado, custo imprevisto."),
             ("E o pior de todos", "a falha silenciosa: o agente relata sucesso e não fez nada. Nenhum teste de tela pega isso.", "warn"),
             ("A saída", "não é escrever um pedido melhor. É reduzir o número de passos não verificados.", "good"),
         ],
         fala="E agora o número que muda a conversa. Um agente com noventa e cinco por cento de acerto por passo, "
              "numa cadeia de vinte passos, termina com trinta e seis por cento de sucesso de ponta a ponta. Não é "
              "pessimismo, é aritmética: a confiabilidade multiplica. Os modos de falha são conhecidos — laço "
              "infinito, ferramenta inventada, contexto contaminado, custo imprevisto. E o pior de todos é a falha "
              "silenciosa: o agente relata sucesso e não fez nada. Nenhum teste de tela pega isso, porque a tela "
              "mostra a mensagem de sucesso. A saída não é escrever um pedido melhor — é reduzir o número de passos "
              "não verificados. Guardem essa frase, porque o bloco dez inteiro é a consequência dela."),

    dict(tipo="video", bloco=5, titulo="Um sistema multiagente com resultado verificável", minutos=8,
         resumo="agentes com contexto, ferramentas e saída conferida",
         percurso=["O objetivo e as ferramentas declaradas",
                   "O agente pedindo a ferramenta — e o programa executando",
                   "O resultado real voltando para o contexto",
                   "Dois agentes com contextos isolados, e a agregação",
                   "Uma falha injetada de propósito",
                   "O portão em código pegando a falha antes de ela seguir adiante"],
         fala="O quinto vídeo mostra tudo isso rodando: o objetivo, as ferramentas declaradas, o agente pedindo e o "
              "programa executando, o resultado real voltando para o contexto. Depois, dois agentes com contextos "
              "isolados e a agregação do trabalho deles. E, no fim, uma falha injetada de propósito, para vocês "
              "verem o portão em código pegando a falha antes de ela seguir adiante — que é a diferença entre uma "
              "demonstração e um sistema."),

    # ───────────────────────── BLOCO 6 ─────────────────────────
    dict(tipo="divisor", bloco=6, titulo="Contexto e recuperação de documentos",
         mensagem="Engenharia de contexto, RAG, e o erro de fatiamento que produz falso positivo clínico.",
         fala="Sexto bloco: contexto. Como se leva o conhecimento certo para dentro do pedido, o que é recuperação "
              "aumentada por geração, e um erro de implementação que, num hospital, produz notificação falsa."),

    dict(tipo="cartoes", bloco=6, chapeu="Contexto e RAG", titulo="De “prompt” para engenharia de contexto",
         destaque="O contexto é tudo o que entra na janela do modelo — e a janela é um recurso escasso e caro.",
         cartoes=[
             ("O que compõe o contexto", "a instrução do sistema, o histórico, os documentos recuperados, as definições de ferramentas e o estado."),
             ("Por que é engenharia", "cada token disputa espaço com outro. Decidir o que entra e o que fica de fora é decisão de projeto."),
             ("O efeito de encher demais", "com a janela cheia, o modelo passa a ignorar o meio do texto. Mais contexto pode piorar a resposta.", "warn"),
             ("A prática", "trazer o trecho certo, não o documento inteiro. Precisão vale mais que volume."),
         ],
         fala="A expressão “engenharia de prompt” ficou pequena. O que importa hoje é engenharia de contexto: o "
              "contexto é tudo o que entra na janela do modelo — a instrução do sistema, o histórico, os documentos "
              "recuperados, as definições das ferramentas e o estado. E a janela é recurso escasso e caro, por causa "
              "daquela quadrática. Cada token disputa espaço com outro, então decidir o que entra e o que fica de "
              "fora é decisão de projeto, não detalhe. E registrem um efeito contraintuitivo: com a janela muito "
              "cheia, o modelo passa a ignorar o meio do texto. Mais contexto pode piorar a resposta. A prática "
              "correta é trazer o trecho certo, não o documento inteiro."),

    dict(tipo="cartoes", bloco=6, chapeu="Contexto e RAG", titulo="Recuperação aumentada por geração",
         cartoes=[
             ("O problema", "o modelo não conhece o seu protocolo, a sua norma interna nem o prontuário do seu paciente."),
             ("Indexar", "os documentos são fatiados e cada pedaço vira um vetor — um endereço num espaço de significado."),
             ("Recuperar", "a pergunta também vira vetor; busca-se o que está próximo dela. Proximidade é semelhança de sentido."),
             ("Gerar com fonte", "os trechos recuperados entram no pedido, e a resposta cita de onde saiu. Sem citação, não há conferência.", "good"),
         ],
         fala="A técnica que resolve isso chama-se recuperação aumentada por geração. O problema é simples: o "
              "modelo não conhece o seu protocolo, a sua norma interna, nem o prontuário do seu paciente. A solução "
              "tem três tempos. Indexar: os documentos são fatiados e cada pedaço vira um vetor, que é um endereço "
              "num espaço de significado. Recuperar: a pergunta também vira vetor, e busca-se o que está próximo "
              "dela — proximidade, aqui, é semelhança de sentido, não de palavra. E gerar com fonte: os trechos "
              "recuperados entram no pedido, e a resposta cita de onde saiu. Essa última parte não é enfeite: sem "
              "citação, ninguém consegue conferir, e uma resposta clínica que não pode ser conferida não serve."),

    dict(tipo="codigo", bloco=6, chapeu="Contexto e RAG", titulo="RAG na prática, com LangChain e Qdrant",
         intro="Vinte linhas para transformar um diretório de protocolos em algo que o modelo consegue consultar.",
         codigo="\n".join([
             'docs   = carregar("protocolos/")',
             'pedacos = fatiar_por_regra(docs)      # NÃO por tamanho fixo',
             '',
             'indice = Qdrant.from_documents(',
             '    pedacos, embeddings, collection_name="ccih")',
             '',
             'trechos = indice.similarity_search(pergunta, k=5)',
             'resposta = modelo.gerar(',
             '    monta_prompt(pergunta, trechos),',
             '    temperatura=0.0)',
             '',
             '# a resposta carrega a origem de cada trecho',
             'citar(trechos)',
         ]),
         explicacao="Qdrant é o banco de vetores; os embeddings convertem texto em vetor; o LangChain costura as "
                    "peças. Repare no detalhe que decide a qualidade: o fatiamento. "
                    "É ele que faz a diferença entre uma resposta certa e uma resposta pela metade.",
         fala="Na prática, são vinte linhas. Você carrega o diretório de protocolos, fatia os documentos, "
              "transforma cada pedaço em vetor e guarda num banco de vetores — no exemplo, o Qdrant. Na hora da "
              "pergunta, busca os cinco trechos mais próximos, monta o pedido com eles e gera a resposta com "
              "temperatura baixa, citando a origem de cada trecho. O LangChain costura essas peças. E eu quero que "
              "vocês reparem numa linha só: a do fatiamento. É ela que decide a qualidade de tudo — e é sobre ela o "
              "próximo slide."),

    dict(tipo="cartoes", bloco=6, chapeu="Contexto e RAG", titulo="Onde o RAG quebra: o fatiamento",
         destaque="Um caso real: um critério de definição de caso de infecção hospitalar ocupa três parágrafos.",
         cartoes=[
             ("A regra inteira", "critério clínico, mais critério laboratorial, mais janela temporal. Os três precisam ser lidos juntos."),
             ("Fatiado por tamanho fixo", "o critério laboratorial se separa da janela temporal. A busca devolve metade da regra."),
             ("O que o modelo faz", "completa o resto sozinho, com fluência — e o sistema notifica um falso positivo.", "warn"),
             ("A correção", "fatiar pela unidade lógica: a regra inteira num pedaço, com metadados por tipo de infecção e expansão de janela em volta do trecho.", "good"),
         ],
         fala="Deixe eu mostrar onde isso quebra, com um caso concreto do domínio de vocês. Um critério de "
              "definição de caso de infecção hospitalar ocupa três parágrafos: o critério clínico, o critério "
              "laboratorial e a janela temporal. Os três só fazem sentido lidos juntos. Se você fatia o documento em "
              "pedaços de tamanho fixo, o critério laboratorial se separa da janela temporal. A busca devolve metade "
              "da regra. O modelo completa o resto sozinho, com toda a fluência do mundo, e o sistema notifica um "
              "falso positivo. Ninguém percebe, porque a resposta está bem escrita. A correção é fatiar pela unidade "
              "lógica — a regra inteira num pedaço — com metadados por tipo de infecção e expansão de janela ao "
              "redor do trecho recuperado. É o tipo de decisão que parece técnica e é clínica."),

    dict(tipo="cartoes", bloco=6, chapeu="Contexto e RAG", titulo="Saída estruturada e proteções",
         cartoes=[
             ("Saída estruturada", "exija um esquema, não um texto livre. O modelo devolve campos que o seu código valida antes de usar.", "good"),
             ("Por que isso importa", "texto livre obriga a interpretar a resposta do modelo — e interpretar é onde o defeito entra."),
             ("Avaliação", "um conjunto de casos com resposta esperada, rodado a cada mudança. Sem isso, você não sabe se melhorou ou piorou."),
             ("Proteções", "limite de passos, limite de custo, lista de ferramentas permitidas, e confirmação humana no que é irreversível."),
         ],
         fala="Duas práticas fecham o bloco. A primeira é saída estruturada: em vez de aceitar texto livre, exija um "
              "esquema, com campos definidos, e valide esses campos no seu código antes de usar. Isso importa porque "
              "texto livre obriga o seu programa a interpretar o que o modelo escreveu, e interpretar é exatamente "
              "onde o defeito entra. A segunda é avaliação: um conjunto de casos com resposta esperada, rodado a "
              "cada mudança. Sem isso vocês não têm como saber se uma alteração melhorou ou piorou o sistema — vão "
              "decidir por impressão. E, junto, as proteções: limite de passos, limite de custo, lista fechada de "
              "ferramentas permitidas, e confirmação humana em tudo o que for irreversível."),

    # ───────────────────────── BLOCO 7 ─────────────────────────
    dict(tipo="divisor", bloco=7, titulo="Frameworks de agentes",
         mensagem="Cinco opções, um critério de leitura, e uma opinião contrária.",
         fala="Sétimo bloco: frameworks. São cinco opções relevantes hoje. Eu vou dar um critério de leitura para "
              "vocês compararem, passar por cada uma, e terminar com uma opinião contrária ao consenso."),

    dict(tipo="cartoes", bloco=7, chapeu="Frameworks", titulo="O critério de leitura",
         destaque="Quatro perguntas que separam os cinco — e que valem para qualquer framework novo que aparecer.",
         cartoes=[
             ("Quem controla o laço?", "você, ou o framework? Isso determina o quanto você consegue depurar quando der errado."),
             ("Onde mora o estado?", "em memória, em sessão, em arquivo, ou num armazenamento durável que sobrevive a uma queda?"),
             ("Como o humano entra?", "existe ponto de interrupção e aprovação, ou o fluxo só vai do começo ao fim?"),
             ("O que se vê de dentro?", "há registro de cada passo, custo por passo e possibilidade de reexecutar a partir do meio?"),
         ],
         fala="Antes de comparar, o critério. São quatro perguntas, e elas valem para qualquer framework novo que "
              "aparecer depois desta palestra. Primeira: quem controla o laço, você ou o framework? Isso determina o "
              "quanto você consegue depurar quando der errado. Segunda: onde mora o estado — em memória, em sessão, "
              "em arquivo, ou num armazenamento durável que sobrevive a uma queda do processo? Terceira: como o "
              "humano entra? Existe ponto de interrupção e aprovação, ou o fluxo só vai do começo ao fim? E quarta: "
              "o que se enxerga de dentro — há registro de cada passo, custo por passo, e possibilidade de "
              "reexecutar a partir do meio? Comparem por essas quatro, não por popularidade."),

    dict(tipo="cartoes", bloco=7, chapeu="Frameworks", titulo="As cinco opções",
         cartoes=[
             ("OpenAI Agents SDK", "controla o laço; estado em sessão; proteções declarativas. Encaixe natural em quem já usa a plataforma da OpenAI."),
             ("Anthropic Claude Agent SDK", "controla o laço; estado em arquivos; ganchos e permissões granulares. Forte para trabalho sobre código e documentos."),
             ("LangChain e LangGraph", "o LangGraph é máquina de estados com persistência durável e interrupção nativa — a escolha para produção regulada."),
             ("CrewAI", "papéis e tarefas declarados em YAML; esconde o laço. Excelente para chegar rápido a um protótipo; estado fraco."),
             ("AutoGen / AG2", "agentes conversando entre si, com controle granular do humano. Bom para exploração e pesquisa."),
         ],
         fala="As cinco. O SDK de agentes da OpenAI controla o laço, guarda estado em sessão e tem proteções "
              "declarativas — encaixe natural para quem já vive na plataforma deles. O SDK de agentes da Anthropic "
              "também controla o laço, guarda estado em arquivos e tem ganchos e permissões bem granulares; é forte "
              "para trabalho sobre código e documentos. O LangGraph, da família LangChain, é uma máquina de estados "
              "com persistência durável e interrupção nativa — é a escolha quando o fluxo precisa sobreviver a uma "
              "queda e passar por aprovação humana, quer dizer, produção regulada. O CrewAI declara papéis e tarefas "
              "em arquivos YAML e esconde o laço: é excelente para chegar rápido a um protótipo, e é o que "
              "usamos no LangNet. E o AutoGen põe agentes conversando entre si, com bom controle humano — mais "
              "adequado a exploração e pesquisa."),

    dict(tipo="tabela", bloco=7, chapeu="Frameworks", titulo="Comparativo, e a opinião contrária",
         colunas=["", "Controle do laço", "Estado", "Humano no laço", "Caso ideal"],
         linhas=[["*OpenAI Agents SDK", "o framework", "sessão", "proteções", "produtos OpenAI"],
                 ["*Claude Agent SDK", "o framework", "arquivos", "ganchos e permissões", "código e documentos"],
                 ["*LangGraph", "máquina de estados", "durável", "interrupção nativa", "produção regulada"],
                 ["*CrewAI", "escondido", "fraco", "limitado", "protótipo rápido"],
                 ["*AutoGen / AG2", "conversa", "fraco", "granular", "exploração e pesquisa"],
                 ["*O seu próprio laço", "você", "você decide", "você decide", "a maioria dos casos"]],
         nota="A opinião contrária: para boa parte dos casos, o laço escrito à mão é mais simples de depurar. "
              "Framework se justifica por durabilidade, observabilidade e entrada do humano no fluxo — não por elegância.",
         fala="E a opinião contrária, que eu faço questão de deixar registrada. Para boa parte dos casos reais, o "
              "laço escrito à mão — aquelas vinte linhas do bloco cinco — é mais simples de depurar do que qualquer "
              "framework. Adotar framework se justifica por três motivos concretos: durabilidade do estado, "
              "observabilidade do que aconteceu, e entrada do humano no meio do fluxo. Não se justifica por "
              "elegância nem por estar na moda. E eu acrescento uma recomendação de sequência: não adotem framework "
              "antes de ter um conjunto de avaliação funcionando. Sem medir, vocês vão trocar de framework pela "
              "sensação de que o outro é melhor."),
]
