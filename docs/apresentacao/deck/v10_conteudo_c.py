# -*- coding: utf-8 -*-
"""V10 · parte C — ambientes de geração de código, protocolos e contratos, SDD."""

SLIDES = [

    # ───────────────────────── BLOCO 8 ─────────────────────────
    dict(tipo="divisor", bloco=8, titulo="Ambientes de geração de código",
         mensagem="Onde o agente trabalha de verdade: Claude Code, Codex, Cursor — e o que muda no ofício.",
         fala="Oitavo bloco. Até aqui falamos de agentes em abstrato; agora vamos ao lugar onde eles já fazem "
              "trabalho de produção todos os dias, que é dentro do repositório de código. Três ambientes, os "
              "comandos que vocês vão usar de fato, e o que isso muda no ofício."),

    dict(tipo="cartoes", bloco=8, chapeu="Ambientes", titulo="Mudou a unidade de trabalho",
         destaque="A unidade deixou de ser a linha de código. Passou a ser a tarefa descrita.",
         cartoes=[
             ("Antes", "você escrevia as linhas. O editor completava palavras; a revisão era sobre o que você tinha digitado."),
             ("Agora", "você descreve a tarefa e revisa o diferencial. O agente lê o repositório, propõe a mudança e roda os testes."),
             ("O que ficou mais importante", "saber dizer o que se quer, e saber ler criticamente o que voltou."),
             ("O que ficou mais perigoso", "aceitar sem ler. Um diferencial grande e bem formatado passa fácil por uma revisão apressada.", "warn"),
         ],
         fala="A primeira coisa a entender é que a unidade de trabalho mudou. Antes, a unidade era a linha de "
              "código: você escrevia as linhas, o editor completava palavras, e a revisão era sobre o que você tinha "
              "digitado. Agora a unidade é a tarefa descrita: você diz o que quer, o agente lê o repositório, propõe "
              "a mudança e roda os testes, e você revisa o diferencial. Duas consequências. O que ficou mais "
              "importante foi saber dizer o que se quer e saber ler criticamente o que voltou. E o que ficou mais "
              "perigoso foi aceitar sem ler — um diferencial grande e bem formatado passa com facilidade por uma "
              "revisão apressada, e é assim que entra defeito."),

    dict(tipo="codigo", bloco=8, chapeu="Ambientes", titulo="Claude Code: sessão de engenharia no terminal",
         intro="O terminal vira uma sessão com contexto persistente sobre o repositório inteiro.",
         codigo="\n".join([
             'claude                      # abre a sessão no repositório',
             'claude -c                   # continua a última sessão',
             'claude -r <id-da-sessao>    # retoma uma sessão específica',
             'claude -p "rode os testes"  # modo não interativo, para automação',
             'claude mcp                  # conecta ferramentas externas',
             '',
             '/help      /compact      /resume',
         ]),
         explicacao="As extensões que importam: skills codificam um fluxo repetível; subagentes e equipes dividem "
                    "investigação e implementação; e o MCP liga o agente a ferramentas e dados externos. "
                    "O modo não interativo é o que permite pôr o agente dentro de um pipeline de integração contínua.",
         fala="O Claude Code transforma o terminal numa sessão de engenharia com contexto persistente sobre o "
              "repositório inteiro. Vocês abrem a sessão, continuam a anterior, retomam uma sessão específica pelo "
              "identificador, ou rodam em modo não interativo passando a tarefa direto na linha de comando — e é "
              "esse último modo que permite pôr o agente dentro de um pipeline de integração contínua. As extensões "
              "que importam são três: as skills, que codificam um fluxo repetível para ele seguir sempre igual; os "
              "subagentes e equipes, que dividem investigação e implementação; e o MCP, que liga o agente a "
              "ferramentas e dados externos — e sobre o qual falo no próximo bloco."),

    dict(tipo="codigo", bloco=8, chapeu="Ambientes", titulo="Codex: execução, revisão e saída verificável",
         intro="O mesmo agente serve à exploração interativa e à automação reproduzível.",
         codigo="\n".join([
             'codex                                  # sessão interativa',
             'codex exec "inspecione o repositório"   # automação',
             'codex exec --json "rode as checagens"   # eventos registrados',
             'codex exec --output-schema esquema.json "avalie"',
             '',
             '/init          # cria o AGENTS.md do repositório',
             '$skill-creator # cria uma skill',
         ]),
         explicacao="A sessão interativa serve à exploração. O modo de execução serve à automação: "
                    "o registro em JSON deixa rastro de cada evento, e o esquema de saída obriga o agente a "
                    "devolver algo que o seu código consegue validar. "
                    "O arquivo AGENTS.md transforma as convenções do time em contexto reutilizável.",
         fala="O Codex cobre o mesmo terreno com uma ênfase diferente. A sessão interativa serve à exploração; o "
              "modo de execução serve à automação. Duas opções merecem atenção: o registro em formato JSON, que "
              "deixa rastro de cada evento — e rastro é o que uma auditoria pede; e o esquema de saída, que obriga o "
              "agente a devolver algo que o seu código consegue validar, em vez de texto livre. É a mesma ideia de "
              "saída estruturada que vimos no bloco seis, agora aplicada ao próprio agente de código. E o arquivo "
              "de convenções do repositório transforma as regras do time em contexto que o agente carrega sozinho, "
              "sem ninguém precisar repetir."),

    dict(tipo="cartoes", bloco=8, chapeu="Ambientes", titulo="Cursor e o panorama dos editores",
         cartoes=[
             ("Cursor", "editor completo com agente embutido: contexto do projeto, edição em vários arquivos e revisão do diferencial na própria tela."),
             ("A diferença de ênfase", "o terminal favorece automação e repetição; o editor favorece exploração e revisão visual."),
             ("O que não muda", "em qualquer um deles, quem aprova a mudança é uma pessoa. O agente propõe."),
             ("Como escolher", "pelo fluxo do time, não pela ferramenta. Quem já vive no terminal ganha pouco mudando para o editor, e vice-versa."),
         ],
         fala="O Cursor resolve o mesmo problema pelo outro lado: é um editor completo com o agente embutido, com "
              "contexto do projeto, edição em vários arquivos ao mesmo tempo e revisão do diferencial na própria "
              "tela. A diferença é de ênfase: o terminal favorece automação e repetição, o editor favorece "
              "exploração e revisão visual. O que não muda em nenhum dos três é o ponto essencial: quem aprova a "
              "mudança é uma pessoa; o agente propõe. E a recomendação para escolher é prosaica — escolham pelo "
              "fluxo do time, não pela ferramenta. Quem já vive no terminal ganha pouco mudando para o editor, e o "
              "contrário também vale."),

    # ───────────────────────── BLOCO 9 ─────────────────────────
    dict(tipo="divisor", bloco=9, titulo="Protocolos e contratos",
         mensagem="MCP na vertical, A2A na horizontal, formatos de conhecimento — e o que nenhum deles resolve.",
         fala="Nono bloco: protocolos. Quando os agentes deixam de ser um script isolado e viram parte de um "
              "sistema, aparece a pergunta de como eles conversam com ferramentas e entre si. Existem padrões para "
              "isso. E existe uma coisa importante que nenhum deles resolve — e que sobra para vocês."),

    dict(tipo="cartoes", bloco=9, chapeu="Protocolos", titulo="O mapa: vertical e horizontal",
         cartoes=[
             ("MCP — a vertical", "liga um agente às ferramentas e aos dados. Um servidor MCP publica ferramentas com nome, parâmetros e esquema de retorno."),
             ("Por que isso importa", "a ferramenta deixa de ser código colado dentro do agente e passa a ser um serviço com contrato, reaproveitável e versionável."),
             ("A2A — a horizontal", "liga agentes a outros agentes: descoberta de capacidades, delegação de tarefa e acompanhamento."),
             ("Como ler os dois juntos", "o MCP responde “o que eu posso fazer”; o A2A responde “com quem eu posso contar”."),
         ],
         fala="O mapa tem dois eixos. Na vertical está o MCP, o protocolo de contexto de modelo, que liga um agente "
              "às ferramentas e aos dados: um servidor publica ferramentas com nome, parâmetros e esquema de "
              "retorno, e qualquer agente compatível passa a poder usá-las. Isso importa mais do que parece, porque "
              "a ferramenta deixa de ser código colado dentro do agente e vira um serviço com contrato — "
              "reaproveitável, versionável, testável por fora. Na horizontal está o A2A, que liga agentes a outros "
              "agentes: descoberta de capacidades, delegação de tarefa e acompanhamento. Uma frase para guardar o "
              "par: o MCP responde “o que eu posso fazer”; o A2A responde “com quem eu posso contar”. No último "
              "bloco vocês vão ver um servidor MCP real sendo publicado e consumido."),

    dict(tipo="cartoes", bloco=9, chapeu="Protocolos", titulo="A família A2A, e a crítica que importa",
         cartoes=[
             ("Extensões oficiais", "identidade do agente, marcação de tempo, rastreabilidade, e um portal de entrada para governar o acesso."),
             ("A família", "pagamento iniciado por agente, comércio com consentimento criptográfico, e um padrão para interface."),
             ("Alternativas", "o ACP, da IBM, herda a tradição de atos de fala com tipos; o ANP aposta em identidade descentralizada."),
             ("A crítica", "nenhum desses protocolos expressa governança. Registram quem chamou quem — não sob qual política, nem com que base legal.", "warn"),
         ],
         fala="O A2A tem extensões oficiais para identidade do agente, marcação de tempo, rastreabilidade e um "
              "portal de entrada que governa o acesso. E tem uma família em volta: pagamento iniciado por agente, "
              "comércio com consentimento criptográfico, padrão de interface. Há alternativas — o ACP, da IBM, que "
              "herda a tradição de atos de fala com tipos; e o ANP, que aposta em identidade descentralizada. Mas "
              "eu quero fechar este slide com a crítica que dá valor a ele: nenhum desses protocolos expressa "
              "governança. Eles registram quem chamou quem, e não sob qual política nem com que base legal. Em "
              "saúde, essa camada não vem pronta em protocolo nenhum. Ela sobra para vocês construírem."),

    dict(tipo="cartoes", bloco=9, chapeu="Protocolos", titulo="Conhecimento em formato aberto",
         destaque="Um pacote de conhecimento é um diretório de arquivos em markdown. Sem banco, sem servidor.",
         cartoes=[
             ("A ideia", "cada arquivo é um conceito; o caminho do arquivo é o identificador; os arquivos se referenciam por links comuns."),
             ("Por que vira grafo", "porque as referências são ligações de verdade — o diretório deixa de ser lista e passa a ser rede."),
             ("O uso direto para vocês", "um pacote com as definições de caso, as fórmulas dos indicadores e os procedimentos da comissão de controle de infecção."),
             ("O que isso entrega", "legível por agente, revisável por infectologista, com histórico e autoria por linha — metade do que uma auditoria já pede.", "good"),
         ],
         fala="Há ainda uma camada que quase ninguém discute: em que formato o conhecimento fica. A proposta mais "
              "interessante é radicalmente simples — um pacote de conhecimento é um diretório de arquivos em "
              "markdown, sem banco de dados e sem servidor. Cada arquivo é um conceito, o caminho do arquivo é o "
              "identificador, e os arquivos se referenciam por links comuns, o que transforma o diretório num grafo "
              "em vez de uma lista. Para vocês o uso é direto: um pacote com as definições de caso, as fórmulas dos "
              "indicadores e os procedimentos da comissão de controle de infecção. O resultado é legível por agente "
              "e revisável por infectologista ao mesmo tempo, com histórico e autoria linha a linha. Isso já é "
              "metade do que uma auditoria pede."),

    dict(tipo="cartoes", bloco=9, chapeu="Protocolos", titulo="A ponte para o próximo bloco",
         destaque="Protocolo resolve como as peças se ligam. Não resolve o que deve ser construído.",
         cartoes=[
             ("O que já temos", "modelos capazes, agentes que usam ferramentas, contexto recuperável e protocolos para ligar tudo."),
             ("O que ainda falta", "uma resposta para: como saber que o sistema construído é o sistema que foi pedido?"),
             ("A resposta do próximo bloco", "especificar antes de delegar — e verificar cada passagem com código, não com opinião.", "good"),
         ],
         fala="Fazendo a ponte. A esta altura temos modelos capazes, agentes que usam ferramentas, contexto "
              "recuperável e protocolos para ligar tudo isso. Mas falta responder a uma pergunta que nenhuma dessas "
              "camadas responde: como eu sei que o sistema construído é o sistema que foi pedido? Protocolo resolve "
              "como as peças se ligam; não resolve o que deve ser construído. É essa lacuna que o próximo bloco "
              "preenche — especificar antes de delegar, e verificar cada passagem com código, não com opinião."),

    # ───────────────────────── BLOCO 10 ─────────────────────────
    dict(tipo="divisor", bloco=10, titulo="Desenvolvimento Orientado a Especificação",
         mensagem="Especificar antes de delegar. A especificação é o que se versiona; o código é o que se regenera.",
         fala="Décimo bloco, e é o centro da palestra. Desenvolvimento orientado a especificação. A ideia cabe numa "
              "frase: especificar antes de delegar. A especificação é o que se versiona e se revisa; o código é o "
              "que se regenera."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="O problema",
         destaque="Programar “no sentimento” funciona no protótipo e colapsa no sistema.",
         cartoes=[
             ("O que acontece", "enquanto é pequeno, tudo bem. Quando cresce, ninguém mais segura o conjunto na cabeça."),
             ("O sintoma", "o código existe e funciona — e ninguém sabe qual requisito ele atende, nem se ainda atende."),
             ("Com agente, mais rápido", "o agente produz em minutos o volume que antes levava semanas. O descompasso entre código e intenção cresce na mesma velocidade.", "warn"),
             ("Em domínio regulado", "isso tem outro nome: não conformidade. Não é dívida técnica, é risco regulatório.", "warn"),
         ],
         fala="Começo pelo problema. Programar no sentimento funciona no protótipo e colapsa no sistema. Enquanto é "
              "pequeno, tudo bem; quando cresce, ninguém mais segura o conjunto na cabeça. O sintoma é este: o "
              "código existe, funciona, e ninguém sabe qual requisito ele atende — nem se ainda atende. Com agentes, "
              "isso ficou mais rápido, não menos: o agente produz em minutos o volume que antes levava semanas, e o "
              "descompasso entre o código e a intenção cresce na mesma velocidade. E em domínio regulado esse "
              "descompasso tem outro nome: não conformidade. Não é dívida técnica, que se paga quando der. É risco "
              "regulatório, que aparece na auditoria."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="A inversão",
         cartoes=[
             ("O jeito de hoje", "requisito informal → código → documentação que já nasce desatualizada."),
             ("O desenvolvimento orientado a especificação", "especificação primária → plano → tarefas → código derivado.", "good"),
             ("O que se versiona", "a especificação. Ela é revisada, discutida e mantida como o artefato principal."),
             ("O que se regenera", "o código. É a mesma relação entre código-fonte e binário: ninguém revisa o binário."),
         ],
         fala="A inversão é esta. Hoje o fluxo é: requisito informal, código, e uma documentação que já nasce "
              "desatualizada — porque foi escrita depois, a partir do código. No desenvolvimento orientado a "
              "especificação o fluxo se inverte: a especificação é primária, dela sai o plano, do plano saem as "
              "tarefas, e das tarefas sai o código, que é derivado. O que se versiona, revisa e mantém é a "
              "especificação. O código é o que se regenera. A analogia que fixa a ideia é a relação entre "
              "código-fonte e binário: ninguém revisa o binário, ninguém corrige um defeito editando o executável. "
              "O que eu estou propondo é subir esse mesmo raciocínio um andar."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="Anatomia de uma especificação útil",
         cartoes=[
             ("Contexto, escopo e não objetivos", "dizer o que está fora é tão importante quanto dizer o que está dentro."),
             ("Requisitos verificáveis", "cada requisito precisa admitir um teste que diga passou ou não passou."),
             ("Bom", "“Quando uma hemocultura positiva for registrada, o sistema deve avaliar os critérios de infecção em até 48 horas e produzir um parecer com a evidência citada.”", "good"),
             ("Ruim", "“O sistema deve detectar infecções corretamente.” Não é verificável, então não é requisito — é uma intenção.", "warn"),
         ],
         fala="O que faz uma especificação ser útil. Ela precisa de contexto e escopo, e precisa dos não objetivos "
              "— dizer o que está fora é tão importante quanto dizer o que está dentro, e é o que impede o projeto "
              "de inchar. E precisa de requisitos verificáveis: cada requisito tem de admitir um teste que diga "
              "passou ou não passou. Comparem os dois exemplos da tela. O bom diz quando o comportamento é "
              "disparado, o que o sistema deve fazer, em quanto tempo e com que evidência — dá para escrever o teste "
              "lendo a frase. O ruim diz “o sistema deve detectar infecções corretamente”, que não é verificável e "
              "portanto não é requisito: é uma intenção. Se a especificação de vocês estiver cheia de frases do "
              "segundo tipo, o agente vai preencher as lacunas sozinho — e vai preencher do jeito dele."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="Da especificação ao código, e a rastreabilidade",
         cartoes=[
             ("O requisito", "R-014: avaliar os critérios de infecção dentro da janela de 48 horas."),
             ("O teste, gerado do critério", "confere as bordas da janela — o caso que passa em 47 horas e o que não passa em 49."),
             ("A implementação", "derivada da especificação, não o contrário."),
             ("Por que a ordem importa", "o teste nasceu do critério, não do código. Por isso ele não herda os defeitos da implementação.", "good"),
         ],
         fala="Vamos ver a ordem funcionando num caso. O requisito diz: avaliar os critérios de infecção dentro de "
              "uma janela de quarenta e oito horas. Desse critério nasce o teste, que confere as bordas da janela — "
              "o caso que passa em quarenta e sete horas e o que não passa em quarenta e nove. E só então nasce a "
              "implementação, derivada da especificação. A ordem é o ponto inteiro. Quando o teste é escrito depois "
              "do código, olhando para o código, ele herda os defeitos da implementação: se o programador entendeu a "
              "janela errado, o teste vai confirmar o erro com muita confiança. Escrito a partir do critério, ele "
              "não tem como herdar nada. E fica a trilha: requisito, teste, função — os três ligados por "
              "identificador."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="Onde o SDD encontra os agentes",
         destaque="Especificador → portão → Arquiteto → portão → Implementador → portão → Verificador",
         cartoes=[
             ("Contexto isolado por etapa", "cada agente recebe só o que precisa. Isso corta a contaminação de contexto de uma etapa para a outra."),
             ("O portão em código determinístico", "quem verifica é programa, não outro modelo. Verificar com um segundo modelo apenas empilha incerteza.", "good"),
             ("Por que isso resolve o erro composto", "o monólito de vinte passos tem trinta e seis por cento de sucesso. Com portão, o erro não se propaga — ele para na etapa."),
             ("O que o portão devolve", "aprovado, ou reprovado com o motivo. E reprovado significa que a etapa não avança.", "warn"),
         ],
         fala="Aqui as duas metades da palestra se encontram. A cadeia é: um agente especifica, um portão confere; "
              "um agente projeta, um portão confere; um agente implementa, um portão confere; um agente verifica. "
              "Duas decisões de projeto sustentam isso. A primeira é contexto isolado por etapa: cada agente recebe "
              "só o que precisa, o que corta a contaminação de uma etapa para a outra. A segunda, e é a que eu mais "
              "defendo: o portão é código determinístico. Quem verifica é programa, não outro modelo. Verificar com "
              "um segundo modelo apenas empilha incerteza sobre incerteza — o portão tem de ser algo que passa ou "
              "não passa. E é assim que se resolve o erro composto que eu mostrei no bloco cinco: o erro não se "
              "propaga pela cadeia, ele para na etapa em que nasceu."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="O artefato regulatório sai de graça",
         cartoes=[
             ("O que a norma pede", "rastreabilidade de requisito a projeto, a teste, a código. Mais gestão de risco documentada e ciclo de vida controlado."),
             ("As referências", "IEC 62304 para ciclo de vida de software médico, ISO 14971 para gestão de risco, e a resolução da ANVISA."),
             ("O que o SDD entrega", "quem trabalha assim já tem a matriz de rastreabilidade — como subproduto, versionada, com autoria e histórico.", "good"),
             ("A inversão da objeção", "o SDD é o que torna código gerado por IA auditável. O que não é auditável é código escrito à mão sem especificação.", "good"),
         ],
         fala="E há um ganho que costuma decidir a conversa com a diretoria. Software de saúde exige "
              "rastreabilidade de requisito a projeto, a teste, a código; exige gestão de risco documentada e ciclo "
              "de vida controlado. São as normas que estão na tela. Quem trabalha orientado a especificação já tem a "
              "matriz de rastreabilidade — não como um documento que alguém monta na véspera da auditoria, mas como "
              "subproduto do método, versionada, com autoria e histórico. E isso permite inverter a objeção mais "
              "comum que vocês vão ouvir. Vão dizer: código gerado por inteligência artificial não é auditável. A "
              "resposta é que o desenvolvimento orientado a especificação é precisamente o que torna esse código "
              "auditável. O que não é auditável é código escrito à mão, sem especificação, por uma pessoa que já "
              "saiu da empresa."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="Antipadrões: como o método morre na prática",
         cartoes=[
             ("Especificação escrita depois", "para justificar o que já foi feito. Vira documentação, e documentação não guia nada.", "warn"),
             ("Requisito não verificável", "quando ninguém consegue escrever o teste, o agente preenche a lacuna com o critério dele.", "warn"),
             ("Portão feito por outro modelo", "duas incertezas empilhadas não fazem uma certeza.", "warn"),
             ("Corrigir no artefato final", "editar o código gerado à mão. Na próxima geração a correção some — e ninguém lembra por quê.", "warn"),
             ("O remédio", "a correção entra na especificação e o artefato é regerado. Sempre. Sem exceção de “é só um detalhe”.", "good"),
         ],
         fala="Antes de mostrar o método funcionando, os quatro jeitos de matá-lo. O primeiro é escrever a "
              "especificação depois, para justificar o que já foi feito: isso não é especificação, é documentação, e "
              "documentação não guia nada. O segundo é o requisito não verificável, que eu já mostrei: quando "
              "ninguém consegue escrever o teste, o agente preenche a lacuna com o critério dele. O terceiro é pôr "
              "outro modelo como portão: duas incertezas empilhadas não produzem uma certeza. E o quarto é o mais "
              "comum de todos, e o mais tentador: corrigir à mão no artefato final. Você edita o código gerado, "
              "funciona, e na próxima geração a correção some — e ninguém lembra por quê. O remédio é uma regra sem "
              "exceção: a correção entra na especificação, e o artefato é regerado. Sempre, inclusive quando parece "
              "só um detalhe."),

    dict(tipo="cartoes", bloco=10, chapeu="SDD", titulo="Com o que se faz isso hoje",
         cartoes=[
             ("Ferramentas de mercado", "há iniciativas de especificação executável acopladas aos ambientes de código do bloco oito."),
             ("O que todas têm em comum", "transformar a especificação em plano, o plano em tarefas, e manter o vínculo entre requisito e artefato."),
             ("O que quase nenhuma tem", "portão determinístico entre as etapas, e verificação formal da orquestração."),
             ("O que vamos ver a seguir", "o LangNet: um pipeline completo com portão em cada passagem, e a rede de Petri validando a execução.", "good"),
         ],
         fala="Sobre ferramental, existem hoje iniciativas de especificação executável acopladas aos ambientes de "
              "código que vimos no bloco oito, e todas compartilham o mesmo núcleo: transformar a especificação em "
              "plano, o plano em tarefas, e manter o vínculo entre requisito e artefato. O que quase nenhuma delas "
              "tem são duas coisas: portão determinístico entre as etapas, e verificação formal da orquestração. É "
              "exatamente aí que entra o que vamos ver no último bloco — um pipeline completo, com portão em cada "
              "passagem, e uma rede de Petri validando a execução. E não é uma proposta: é um sistema rodando, com "
              "uma aplicação hospitalar gerada por ele."),
]
