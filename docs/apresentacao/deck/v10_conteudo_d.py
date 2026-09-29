# -*- coding: utf-8 -*-
"""V10 · parte D — LangNet e BioByte, e fechamento.

As etapas descritas aqui são as etapas reais do pipeline do LangNet, na ordem em que
aparecem na coluna da interface e no roteiro da demonstração final
(`docs/apresentacao/demo-biobyte-v5/roteiro_narrado_v5_biobyte.md`, 40 cenas).
"""

ETAPAS = ["Docs", "Requisitos", "Especificação", "Modelo de dados", "Interface",
          "Ferramentas", "Agentes e tarefas", "Petri", "Testes", "Código", "Aplicação"]

SLIDES = [

    dict(tipo="divisor", bloco=11, titulo="LangNet e BioByte",
         mensagem="O método do bloco anterior, implementado — e uma aplicação hospitalar gerada por ele.",
         fala="Último bloco de conteúdo. Tudo o que vimos até aqui vira uma coisa só: um pipeline que recebe um "
              "documento de pedido e devolve uma aplicação funcionando, com rastro de cada passagem. O sistema "
              "chama-se LangNet. E a aplicação que ele gerou, e que vocês vão ver rodando, chama-se BioByte "
              "Sentinela — vigilância de infecção hospitalar."),

    dict(tipo="cartoes", bloco=11, chapeu="LangNet", titulo="Dois lados: a fábrica e a máquina",
         destaque="O LangNet não é a aplicação. Ele é a fábrica que produz a aplicação.",
         cartoes=[
             ("A fábrica", "o LangNet percorre as etapas, do documento ao código, e guarda cada artefato com versão, origem e autoria."),
             ("A máquina", "a aplicação gerada roda por conta própria, com um executor que dispara as tarefas dos agentes."),
             ("O que liga os dois", "a rede de Petri: ela sai da fábrica como artefato e entra na máquina como plano de execução."),
             ("Por que essa distinção importa", "defeito de aplicação se corrige na fábrica e se regera. Nunca no artefato final.", "warn"),
         ],
         fala="Antes de percorrer as etapas, uma distinção que organiza tudo. O LangNet não é a aplicação — ele é a "
              "fábrica que produz a aplicação. De um lado está a fábrica, que percorre as etapas do documento até o "
              "código e guarda cada artefato com versão, origem e autoria. Do outro está a máquina: a aplicação "
              "gerada, que roda por conta própria com um executor disparando as tarefas dos agentes. O que liga os "
              "dois lados é a rede de Petri: ela sai da fábrica como artefato e entra na máquina como plano de "
              "execução. E dessa distinção sai a regra de ouro do método, aquela do antipadrão: defeito da aplicação "
              "se corrige na fábrica e se regera — nunca no artefato final."),

    dict(tipo="etapa", bloco=11, chapeu="LangNet", titulo="As etapas, e o que se repete em todas elas",
         trilha=ETAPAS, atual=list(range(1, 12)),
         cartoes=[
             ("O mesmo ritual em cada etapa", "escolher a origem e a versão de onde partir · gerar · refinar conversando com o agente · aprovar."),
             ("Tudo é versionado", "aprovar não apaga o anterior. Cada etapa guarda de qual versão da etapa anterior ela nasceu."),
             ("O portão entre etapas", "código determinístico confere a passagem. Reprovado significa que não avança — e diz por quê.", "good"),
             ("Refinar é conversar", "a correção é dita em português, ao agente da etapa. Ele reescreve o artefato e grava uma versão nova."),
         ],
         fala="São onze etapas, e o que importa entender primeiro é que todas elas seguem o mesmo ritual: você "
              "escolhe a origem e a versão de onde quer partir, gera, refina conversando com o agente daquela "
              "etapa, e aprova. Tudo é versionado — aprovar não apaga o anterior, e cada etapa guarda de qual "
              "versão da etapa anterior ela nasceu, que é o que dá a rastreabilidade de ponta a ponta. Entre uma "
              "etapa e a seguinte há um portão em código determinístico: se a passagem não estiver íntegra, não "
              "avança, e o portão diz por quê. E refinar é literalmente conversar: você escreve a correção em "
              "português, o agente reescreve o artefato e grava uma versão nova."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="Do documento aos requisitos",
         trilha=ETAPAS, atual=[1, 2],
         cartoes=[
             ("A entrada", "o documento do cliente — no caso, o pedido do hospital para vigilância de infecção relacionada à assistência."),
             ("Cada requisito diz de onde veio", "extraído do documento, inferido, trazido de pesquisa, ou acrescentado na conversa. A procedência fica gravada.", "good"),
             ("E diz a sua natureza", "convencional ou agêntico. Cadastrar um paciente é convencional; classificar um caso pelo critério da norma é agêntico."),
             ("Por que essa marca decide o projeto", "ela é que determina, lá na frente, o que vira código comum e o que vira tarefa de agente.", "warn"),
         ],
         fala="A primeira etapa recebe o documento do cliente — no nosso caso, o pedido do hospital para vigilância "
              "de infecção relacionada à assistência à saúde. Dele nascem os requisitos, e dois campos de cada "
              "requisito merecem atenção. O primeiro é a procedência: cada requisito diz se foi extraído "
              "literalmente do documento, inferido, trazido de pesquisa, ou acrescentado durante a conversa. Isso "
              "fica gravado, e é o começo da trilha de auditoria. O segundo é a natureza: convencional ou agêntico. "
              "Cadastrar um paciente é convencional; classificar um caso pelo critério da norma é agêntico. Essa "
              "marca parece burocrática e decide o projeto inteiro, porque é ela que determina, lá na frente, o que "
              "vira código comum e o que vira tarefa de agente. Quando ela é mal posta, o sistema faz quarenta e "
              "cinco tarefas de agente onde deveria ter oito."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="A especificação funcional",
         trilha=ETAPAS, atual=[3],
         cartoes=[
             ("O caso de uso", "ator, pré-condições, fluxo principal passo a passo, e os fluxos de exceção — o que acontece quando dá errado."),
             ("O croqui da tela", "cada caso de uso traz o esboço da tela: que campos, que botões, que resultado aparece."),
             ("A decisão do agente", "nos casos agênticos, a especificação declara o que o agente decide e com base em quê."),
             ("A consistência conferida", "o croqui e o fluxo precisam falar dos mesmos campos e dos mesmos botões. O portão confere isso.", "good"),
         ],
         fala="Da lista de requisitos nasce a especificação funcional, escrita em casos de uso. Cada caso de uso "
              "tem ator, pré-condições, fluxo principal passo a passo, e — o que mais falta nas especificações que "
              "eu vejo por aí — os fluxos de exceção, isto é, o que acontece quando dá errado. Cada caso de uso "
              "traz também o croqui da tela: que campos, que botões, que resultado aparece. E, nos casos agênticos, "
              "a especificação declara explicitamente o que o agente decide e com base em quê. Há um portão "
              "conferindo uma coisa específica aqui: o croqui e o fluxo têm de falar dos mesmos campos e dos mesmos "
              "botões. Quando eles divergem, o defeito atravessa o pipeline inteiro e só aparece na tela do usuário."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="O modelo de dados, e a correção por conversa",
         trilha=ETAPAS, atual=[4],
         cartoes=[
             ("O que sai", "as tabelas, os campos, os tipos, as chaves e as relações — derivadas das entidades dos casos de uso."),
             ("A etapa aponta os próprios defeitos", "coluna obrigatória sem valor padrão, resultado de agente sem coluna dedicada, campo que ninguém preenche.", "warn"),
             ("A correção é dita em português", "“a urgência precisa ser uma coluna própria, com valores fechados” — e o agente reescreve o modelo."),
             ("A versão nova guarda a anterior", "dá para comparar as duas e ver exatamente o que mudou.", "good"),
         ],
         fala="Das entidades dos casos de uso nasce o modelo de dados: tabelas, campos, tipos, chaves e relações. E "
              "aqui há uma coisa que eu gosto de mostrar, porque contraria a expectativa: a própria etapa aponta os "
              "seus defeitos. Ela avisa quando há coluna obrigatória sem valor padrão, quando o resultado de um "
              "agente não tem coluna dedicada para ser guardado, quando existe campo que ninguém preenche. Você lê "
              "o aviso e responde em português — por exemplo: a urgência precisa ser uma coluna própria, com valores "
              "fechados. O agente reescreve o modelo e grava uma versão nova, preservando a anterior, de modo que "
              "dá para comparar as duas e ver exatamente o que mudou. Isso vocês vão ver acontecendo na demonstração."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="A interface e o protótipo",
         trilha=ETAPAS, atual=[5],
         cartoes=[
             ("As telas saem dos casos de uso", "cada tela nasce do croqui e do fluxo do caso de uso que a origina — não de um molde genérico de formulário."),
             ("Componentes de verdade", "indicador, gráfico, tabela, lista e marcação, além dos campos. Uma tela de vigilância não é um cadastro."),
             ("O protótipo roda antes de existir sistema", "o mesmo código das telas, com a fonte de dados trocada por dados de exemplo. Compila em milissegundos."),
             ("Para que serve", "discutir a tela com o usuário antes de gerar backend, banco e agentes — quando mudar ainda é barato.", "good"),
         ],
         fala="Dos casos de uso nascem as telas. E eu insisto num ponto: cada tela nasce do croqui e do fluxo do "
              "caso de uso que a origina, e não de um molde genérico de formulário. Isso importa porque uma tela de "
              "vigilância epidemiológica não é um cadastro: ela tem indicador, gráfico, tabela, lista e marcação, "
              "além dos campos. Se o gerador só souber desenhar campo de formulário, as telas viram casca vazia — e "
              "esse foi, aliás, um defeito real que nós corrigimos. Depois das telas vem o protótipo, que é o mesmo "
              "código com a fonte de dados trocada por dados de exemplo, compilando em milissegundos. Ele serve "
              "para discutir a tela com o usuário antes de gerar backend, banco e agentes — quer dizer, enquanto "
              "mudar ainda é barato."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="Ferramentas, agentes e tarefas",
         trilha=ETAPAS, atual=[6, 7],
         cartoes=[
             ("Quem implementa cada ferramenta", "a etapa de ferramentas decide: código determinístico, tarefa de agente, ou serviço externo publicado por MCP."),
             ("No BioByte", "duas ferramentas reais publicadas por um servidor MCP: consulta à microbiologia e cálculo do escore de risco."),
             ("Cada tarefa sabe de onde veio", "toda tarefa carrega o caso de uso e o requisito que a originaram. É a matriz de rastreabilidade se formando sozinha.", "good"),
             ("O campo que roteia", "cada tarefa declara se é determinística ou de agente. O executor lê esse campo e decide como rodá-la."),
         ],
         fala="Duas etapas que andam juntas. A de ferramentas responde a uma pergunta que quase todo projeto "
              "agêntico deixa em aberto: quem implementa cada ferramenta. Pode ser código determinístico, pode ser "
              "uma tarefa de agente, ou pode ser um serviço externo publicado por MCP. No BioByte há duas "
              "ferramentas reais publicadas por um servidor MCP — a consulta à microbiologia e o cálculo do escore "
              "de risco — e vocês vão vê-las sendo chamadas de verdade na demonstração. A etapa seguinte define os "
              "agentes e as tarefas de cada um. E aqui está o detalhe que dá valor ao método: toda tarefa carrega o "
              "caso de uso e o requisito que a originaram. A matriz de rastreabilidade não é montada por ninguém — "
              "ela se forma sozinha, porque o vínculo viaja junto com o artefato."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="A rede de Petri: a orquestração verificável",
         trilha=ETAPAS, atual=[8],
         cartoes=[
             ("O que é", "lugares e transições. Os lugares guardam estado; as transições disparam quando as condições são satisfeitas."),
             ("Por que não é um fluxograma", "porque admite prova. Ausência de travamento, alcançabilidade de cada estado e invariantes são verificados na estrutura."),
             ("O que o portão confere", "que a rede é bipartida, que não há ilha inalcançável, e que cada transição tem guarda definida.", "good"),
             ("O que isso acrescenta", "os testes dizem que funcionou nos casos testados. A rede diz o que é estruturalmente possível acontecer.", "good"),
         ],
         fala="Das tarefas e da sequência entre elas nasce a rede de Petri, e é a camada que me interessa mais. Uma "
              "rede de Petri tem lugares e transições: os lugares guardam estado, e as transições disparam quando as "
              "condições estão satisfeitas. Ela não é um fluxograma bonito — a diferença é que ela admite prova. "
              "Ausência de travamento, alcançabilidade de cada estado, invariantes: essas propriedades são "
              "verificadas na estrutura, não testadas por amostragem. O portão confere que a rede é bipartida, que "
              "não sobrou nenhuma ilha inalcançável e que cada transição tem guarda definida. E o que isso "
              "acrescenta é de outra natureza: os testes dizem que funcionou nos casos que você testou; a rede diz "
              "o que é estruturalmente possível acontecer. São garantias diferentes, e as duas são necessárias."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="Casos de teste e geração do código",
         trilha=ETAPAS, atual=[9, 10],
         cartoes=[
             ("De onde saem os testes", "dos critérios dos casos de uso, por tabela de decisão — não do código. É a ordem do bloco anterior, aplicada."),
             ("O que eles conferem", "comportamento, não tela. “Exibe a mensagem X” não é caso de teste; “rejeita a senha errada” é.", "warn"),
             ("A geração", "sai a aplicação inteira: telas, backend, banco, agentes, ferramentas e o executor da rede."),
             ("O portão final", "confere se cada tarefa do documento chegou ao código, e se cada passo de lógica virou implementação — e reporta o que não virou.", "good"),
         ],
         fala="Duas etapas para fechar a fábrica. Os casos de teste saem dos critérios dos casos de uso, por tabela "
              "de decisão, e não do código — é exatamente a ordem que eu defendi no bloco anterior, aplicada. E eles "
              "conferem comportamento, não tela: “exibe a mensagem tal” não é caso de teste, “rejeita a senha "
              "errada” é. Essa distinção não é preciosismo; foi por causa dela que, num sistema nosso, uma tela de "
              "acesso que não conferia a senha passou despercebida. Depois vem a geração do código, que produz a "
              "aplicação inteira: telas, backend, banco, agentes, ferramentas e o executor da rede. E o portão "
              "final confere se cada tarefa do documento chegou ao código, e se cada passo de lógica virou "
              "implementação — reportando explicitamente o que não virou."),

    dict(tipo="etapa", bloco=11, chapeu="Etapas", titulo="A aplicação rodando, e a bancada de execução",
         trilha=ETAPAS, atual=[11],
         cartoes=[
             ("O que roda", "a aplicação com os cadastros, os relatórios e as telas dos agentes — e um executor disparando a rede."),
             ("A bancada", "mostra cada tarefa em execução: a entrada que recebeu, o que o agente pensou, que ferramenta chamou, e a saída."),
             ("Etiquetas universais", "o executor emite marcas padronizadas em cada momento da execução. É o que torna a bancada genérica."),
             ("Falha não passa calada", "erro de ferramenta ou de agente aparece como falha declarada. Sucesso relatado sem trabalho feito é o defeito que mais custa caro.", "warn"),
         ],
         fala="E aqui chegamos ao outro lado, a máquina. A aplicação roda com os cadastros, os relatórios e as "
              "telas dos agentes, e um executor dispara a rede de Petri. O que eu quero que vocês vejam é a bancada: "
              "ela mostra cada tarefa em execução com a entrada que recebeu, o que o agente pensou, que ferramenta "
              "ele chamou, e a saída que produziu. Isso funciona para qualquer aplicação gerada porque o executor "
              "emite um conjunto padronizado de etiquetas em cada momento da execução. E um último ponto, que é o "
              "que mais me importa: falha não passa calada. Erro de ferramenta ou de agente aparece como falha "
              "declarada, com o motivo. O defeito que custa mais caro num sistema agêntico não é o erro — é o "
              "sucesso relatado sem trabalho feito."),

    dict(tipo="tabela", bloco=11, chapeu="BioByte", titulo="O que foi medido, e o que ainda é lacuna",
         colunas=["Frente", "Evidência concreta"],
         linhas=[["*Microbiologia", "caso CAS-2023-001 → Staphylococcus aureus, antibiograma e marca de multirresistência, pela ferramenta MCP"],
                 ["*Escore de risco", "escore, nível e fatores devolvidos pela ferramenta — não redigidos pelo modelo"],
                 ["*Classificação", "critérios da norma aplicados: cateter, hemocultura e correlação clínica"],
                 ["*Alerta", "registrado na base; a notificação para fora do sistema continua declarada como lacuna"],
                 ["*Relatório", "arquivo gerado; o painel mostra os dados ou declara que a série está ausente"],
                 ["*Execução", "22 de 23 casos de teste conferidos contra as linhas do banco"]],
         nota="O sistema registra também o que ainda não está implementado. Uma lacuna declarada é um item de "
              "projeto; uma lacuna escondida atrás de uma mensagem de sucesso é um risco clínico.",
         fala="E aqui está o que foi medido, com a honestidade que o método exige. A consulta à microbiologia "
              "devolve o micro-organismo, o antibiograma e a marca de multirresistência pela ferramenta MCP. O "
              "escore de risco é devolvido pela ferramenta, não redigido pelo modelo — essa distinção é tudo. A "
              "classificação aplica os critérios da norma. O alerta é registrado na base, e a notificação para fora "
              "do sistema continua declarada como lacuna. Os relatórios saem, e quando não há série o painel diz "
              "que não há, em vez de desenhar um gráfico vazio. Vinte e dois dos vinte e três casos de teste "
              "conferidos contra as linhas do banco. Reparem que o sistema registra também o que ainda não está "
              "pronto: uma lacuna declarada é um item de projeto; uma lacuna escondida atrás de uma mensagem de "
              "sucesso é um risco clínico."),

    dict(tipo="cartoes", bloco=11, chapeu="BioByte", titulo="Onde isso ainda vai chegar",
         cartoes=[
             ("Sistemas que investigam", "a literatura recente mostra agentes que geram hipóteses, criticam umas às outras e as ordenam por mérito."),
             ("A nossa replicação", "reproduzimos essa arquitetura internamente, com os mesmos papéis de geração, crítica e ordenação."),
             ("A ressalva que eu faço questão de dizer", "uma ordenação por mérito mede qualidade de hipótese. Não mede correção de execução.", "warn"),
             ("Por isso a rede de Petri", "ela verifica a estrutura da orquestração. As duas coisas são necessárias, e nenhuma substitui a outra.", "good"),
         ],
         fala="Um parágrafo sobre onde isso ainda vai chegar. A literatura recente mostra sistemas de agentes que "
              "geram hipóteses de pesquisa, criticam umas às outras e as ordenam por mérito — e nós reproduzimos "
              "essa arquitetura internamente, com os mesmos papéis de geração, crítica e ordenação. Mas eu faço "
              "questão de deixar a ressalva: uma ordenação por mérito mede qualidade de hipótese; ela não mede "
              "correção de execução. São perguntas diferentes. É por isso que a rede de Petri continua fazendo "
              "falta: ela verifica a estrutura da orquestração. As duas coisas são necessárias, e nenhuma "
              "substitui a outra."),

    dict(tipo="video", bloco=11, titulo="O pipeline completo do LangNet, do documento à aplicação", minutos=20,
         resumo="a fábrica inteira, etapa por etapa, terminando na aplicação rodando",
         percurso=["O documento do hospital entrando, e os requisitos com procedência e natureza",
                   "A especificação: caso de uso, fluxos de exceção e croqui de tela",
                   "O modelo de dados apontando o próprio defeito — e a correção dita em português",
                   "As telas e o protótipo rodando antes de existir sistema",
                   "Ferramentas, agentes e tarefas, cada uma sabendo de onde veio",
                   "A rede de Petri, o portão, e a geração do código",
                   "A aplicação: cadastros, relatórios e os agentes produzindo registros",
                   "A bancada: entradas, etiquetas, saída — e uma falha que não passa calada"],
         fala="E aqui está a demonstração final. São vinte minutos percorrendo a fábrica inteira: o documento do "
              "hospital entrando, os requisitos nascendo com procedência e natureza, a especificação com os fluxos "
              "de exceção e o croqui da tela, o modelo de dados apontando o próprio defeito e sendo corrigido por "
              "conversa, as telas, o protótipo, as ferramentas, os agentes, a rede de Petri, o portão, a geração do "
              "código — e, no fim, a aplicação rodando, com os agentes produzindo registros e a bancada mostrando "
              "cada entrada e cada saída. Termina com uma falha proposital, para vocês verem que ela não passa "
              "calada. Peço que prestem atenção numa coisa só, ao longo dos vinte minutos: em nenhum momento eu "
              "edito o artefato final. Toda correção entra na etapa e o artefato é regerado."),

    # ───────────────────────── BLOCO 12 ─────────────────────────
    dict(tipo="divisor", bloco=12, titulo="Fechamento",
         mensagem="O que levar desta palestra, e por onde começar na segunda-feira.",
         fala="Vamos fechar. Eu quero deixar três conclusões, e uma sugestão bem concreta de por onde começar."),

    dict(tipo="cartoes", bloco=12, chapeu="Fechamento", titulo="As três conclusões",
         cartoes=[
             ("Primeira", "modelo não garante correção. Quem garante é o que você põe em volta dele: portão em código, saída estruturada, evidência citada.", "good"),
             ("Segunda", "a especificação virou o artefato principal. O código é derivado — e derivado se regera, não se remenda.", "good"),
             ("Terceira", "rastreabilidade deixou de ser custo e virou subproduto. Quem trabalha assim já tem o que a auditoria pede.", "good"),
             ("Por onde começar", "escolham um fluxo pequeno e verificável. Escrevam a especificação com critério testável, e o portão antes do agente."),
         ],
         fala="Três conclusões. A primeira: modelo nenhum garante correção, e nenhuma versão futura vai garantir — "
              "quem garante é o que você põe em volta dele, que é portão em código, saída estruturada e evidência "
              "citada. A segunda: a especificação virou o artefato principal, e o código passou a ser derivado; e "
              "derivado se regera, não se remenda. A terceira: rastreabilidade deixou de ser custo e virou "
              "subproduto — quem trabalha assim já tem, sem esforço adicional, aquilo que a auditoria vai pedir. E a "
              "sugestão de começo, para segunda-feira: escolham um fluxo pequeno e verificável do serviço de vocês. "
              "Escrevam a especificação dele com critério testável, e construam o portão antes de construir o "
              "agente. Se vocês fizerem só isso, já vão estar à frente da maior parte dos projetos que eu vejo."),

    dict(tipo="cartoes", bloco=12, chapeu="Fechamento", titulo="O que fica com vocês",
         cartoes=[
             ("Os notebooks", "um por bloco de fundamento: pipeline de aprendizado, escore de risco em saúde, transferência de aprendizado e o laço do agente."),
             ("Os vídeos", "as seis demonstrações, para rever no seu ritmo."),
             ("As referências", "o artigo do Transformer, as normas de software médico citadas, e a documentação dos frameworks comparados."),
             ("O contato", "para dúvida sobre o material, sobre o método, ou sobre aplicar isso a um caso concreto do serviço de vocês."),
         ],
         fala="O que fica com vocês. Os notebooks, um por bloco de fundamento: o pipeline de aprendizado, o escore "
              "de risco em saúde, a transferência de aprendizado e o laço do agente — todos executáveis, e eu sugiro "
              "que rodem trocando parâmetros, porque é trocando que se entende. Os seis vídeos, para rever no ritmo "
              "de cada um. As referências, incluindo o artigo do Transformer, as normas de software médico que eu "
              "citei e a documentação dos frameworks comparados. E o contato, para dúvida sobre o material, sobre o "
              "método, ou sobre aplicar isso a um caso concreto do serviço de vocês — que é, honestamente, a "
              "conversa que mais me interessa."),

    dict(tipo="encerramento", bloco=12,
         frase="O gargalo deixou de ser escrever código. Passou a ser especificar com precisão o que se quer.",
         assinatura="Obrigado.   ·   Perguntas",
         fala="Eu começei com esta frase e termino com ela. O gargalo deixou de ser escrever código; passou a ser "
              "especificar com precisão o que se quer. Muito obrigado pela atenção. Vamos às perguntas."),
]
