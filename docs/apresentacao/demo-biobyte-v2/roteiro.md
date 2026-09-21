# Roteiro — BioByte Sentinela gerado pelo LangNet

> Regra deste roteiro: **cada cena tem uma captura que existe e uma narração escrita**. Nenhum
> número aparece com dois valores diferentes. As cenas são escritas na hora em que a etapa roda —
> não depois, olhando para uma pasta de imagens.
>
> Capturas em `shots/`. Documento-fonte em `seed/levantamento_requisitos_biobyte.txt`.

---

## Parte A — Abertura: o que é o BioByte Sentinela

*(Esta parte é narrada sobre a ata e sobre a tela inicial do LangNet. Ela existe para que quem
assiste saiba, antes de ver qualquer geração, o que o sistema vai ter.)*

### Cena 1 — O problema

**TELA:** `seed/levantamento_requisitos_biobyte.txt` — primeira página, seção 1

**NARRAÇÃO:**
Numa UTI, todo dia alguém precisa olhar quais pacientes estão com cateter venoso central, há
quantos dias, e decidir quem merece atenção primeiro. Hoje isso é feito em planilha, com
informação vindo de três lugares: o prontuário, o laboratório e a anotação da enfermagem.

A coordenadora da Comissão de Controle de Infecção Hospitalar resumiu o custo disso numa frase:
*"o que mais nos custa é o tempo entre a hemocultura ficar pronta no laboratório e alguém aqui
perceber que aquele paciente tem uma infecção de corrente sanguínea. Às vezes são dois dias. E
quando o germe é multirresistente, dois dias é muita coisa."*

O sistema que vamos gerar se chama **BioByte Sentinela**. Ele vigia Infecção de Corrente
Sanguínea Associada a Cateter — ICSAC.

---

### Cena 2 — O que o BioByte Sentinela vai ter

**TELA:** lâmina com a lista abaixo (a produzir), ou a ata rolando pelas seções 2.1 a 2.12

**NARRAÇÃO:**
São doze frentes, todas pedidas nesta reunião.

**Acesso.** Médicos, enfermeiros e administradores entram com **e-mail e senha**. Sem código por
mensagem, sem aplicativo autenticador — a CCIH recusou verificação em duas etapas porque na UTI a
pessoa muitas vezes está de luva. Depois de entrar, o sistema sabe quem está operando durante todo
o uso e grava esse nome em cada registro de auditoria, sem pedir identificação de novo a cada tela.
Usuário desligado é **desativado, nunca apagado**, porque o nome dele continua nos registros
antigos.

**Cadastro do caso.** Paciente com cateter: nome, nascimento, sexo, prontuário, médico
responsável. Do episódio: idade na data, dias de cateter instalado, pontuação APACHE II, sítio de
inserção — jugular interna, subclávia ou femoral — e comorbidades. Nas palavras da enfermeira,
*"esses cinco dados são os que entram na conta do risco; se faltar um, a conta não sai."*

**Risco pelo modelo de Cox.** O hospital já tem um serviço estatístico externo que calcula o risco
de ICSAC pelo modelo de perigos proporcionais de Cox. O BioByte o consulta e recebe o escore, a
faixa de risco, o preditor linear, os fatores que pesaram e o nome da versão do modelo. Dois
avisos que a médica fez questão de registrar: esse serviço **não devolve intervalo de confiança**,
então o sistema não pode exigir esse dado; e o nome do modelo vem como texto livre e pode ser
longo, então o campo tem que caber.

**Microbiologia.** O BioByte consulta o sistema do laboratório pelo número do paciente e recebe a
hemocultura: identificador da amostra, origem, microrganismo isolado e o antibiograma — a lista de
antimicrobianos, cada um com sua classe e o resultado sensível, intermediário ou resistente. O
laboratório pode responder **"pendente", sem microrganismo nenhum**, e pode responder com uma
mensagem de problema no cadastro da amostra. O sistema lida com os dois casos sem quebrar e sem
inventar resultado. E a importação **não duplica**: buscar duas vezes o mesmo resultado não cria
registro repetido.

**Classificação NHSN.** Com a microbiologia na mão, o sistema aplica o critério NHSN vigente e diz
se a ICSAC está confirmada, descartada ou pendente — registrando **qual critério e qual versão**
dele, porque a norma muda e os casos antigos continuam valendo pela norma da época. O médico pode
sobrescrever a classificação automática, **desde que justifique por escrito**; quando não
sobrescreve, justificativa nenhuma é exigida.

**Multirresistência e alerta.** Do antibiograma, o sistema identifica o microrganismo
multirresistente — resistência a três ou mais classes. Quando detecta, abre um alerta com tipo,
gravidade e situação, e **notifica por e-mail** a coordenadora da CCIH e o enfermeiro responsável.
*"É o caso em que cada hora conta"*, disse a médica. A notificação registra para quem foi, por qual
canal e quanto tempo levou — e **se o envio falhar, o sistema diz que falhou**, não finge que
enviou.

**Recomendação de tratamento.** Confirmado o caso, o sistema recomenda o pacote de medidas — o
bundle — considerando o resultado do NHSN e a multirresistência. O médico pode escolher outro, mas
a recomendação original fica registrada junto. Regra que a médica cravou: o sistema **não
recomenda bundle de germe multirresistente para caso sem multirresistência registrada**; se os
dados não sustentam, ele diz que não sustentam. Toda recomendação vem com justificativa em texto.

**Estimativa de redução de risco.** Escolhido o tratamento, o sistema estima quanto ele reduz o
risco daquele paciente num horizonte de 30, 90 ou 180 dias, devolvendo redução absoluta, relativa
e intervalo de confiança. Os dados clínicos ele **busca no próprio cadastro do caso**, sem pedir
de novo.

**Ciclo integrado.** Um comando único que faz a sequência inteira para um caso: buscar
microbiologia, classificar, detectar multirresistência, calcular escore, recomendar e estimar.
*"Na prática, é isso que eu quero clicar de manhã."* Ele devolve quais etapas concluíram e o
resultado de cada uma.

**Painel de vigilância.** Por período — 7, 30, 90 ou 365 dias: casos ativos, escore médio de
risco, casos classificados pelo NHSN, alertas de multirresistência abertos, conformidade por mês e
distribuição por faixa de risco. É o painel que fica na tela da sala da CCIH.

**Relatórios.** Exportação em PDF ou CSV, por período, com filtro por paciente, trazendo casos,
escores, classificações e alertas — informando quantos registros foram exportados.

**Auditoria.** Toda ação relevante registrada: quem fez, o que fez, sobre qual registro, quando. O
registro é **encadeado** — cada entrada guarda a marca da anterior — para que ninguém altere o
histórico sem que apareça.

---

### Cena 3 — Como ele se comporta quando algo dá errado

**TELA:** ata, seção 3

**NARRAÇÃO:**
Esta parte ocupou boa parte da reunião, e é a que mais define o sistema. A médica foi direta:
*"o pior que pode acontecer é o sistema mostrar um número que não existe."*

Laboratório fora do ar: a tela diz que o laboratório está fora do ar — não mostra resultado vazio
como se fosse resultado normal. Serviço de escore sem resposta: o sistema diz isso e **não grava
escore nenhum**. Falta dado para uma conta: o sistema diz **qual** dado falta. E-mail não
configurado: avisa, em vez de dar a notificação por enviada. Nenhuma tela mostra valor de exemplo,
texto de preenchimento ou número inventado — campo sem dado aparece vazio, com a explicação do
porquê.

Guarde esta cena. Mais adiante, o sistema gerado vai recusar uma operação por falta de dado — e
isso vai ser o **acerto** dele, não uma falha.

---

### Cena 4 — O que a segurança do hospital exigiu

**TELA:** ata, seção 4

**NARRAÇÃO:**
O gerente de TI trouxe cinco exigências e disse que nenhuma é negociável.

Primeira: **toda comunicação por HTTPS**, sem exceção, nem dentro da rede interna. Segunda: **o
servidor não confia na tela** — toda chamada chega com um token emitido no login e verificado a
cada requisição; sem token, ou com token vencido, o servidor recusa. Terceira: **senha nunca em
texto** — guarda-se o resumo criptográfico com sal, e senha não aparece em log, nem em mensagem de
erro, nem em tela. Quarta: **cada papel enxerga o que lhe cabe** — enfermeiro não apaga auditoria,
administrador não precisa ver dado clínico para gerenciar usuário. Quinta: **credencial de serviço
externo fica em configuração do servidor**, nunca no código nem na tela — e a chamada ao
laboratório vai com os dados do paciente já anonimizados.

Repare no que **não** está aí: "o sistema deve ser seguro". Requisito de segurança que não nomeia
o mecanismo não serve para gerar código, e o LangNet foi instruído a recusá-lo.

---

### Cena 5 — As duas integrações reais

**TELA:** ata, seção 5

**NARRAÇÃO:**
O hospital já disponibiliza dois serviços, e o BioByte vai consumir os dois de verdade — não são
simulações: a consulta de microbiologia ao laboratório, e o cálculo do escore de risco pelo modelo
de Cox. Cada um declara o que recebe e o que devolve, e é essa declaração que o gerador vai ler na
hora de escrever o código.

---

## Parte B — A geração, etapa por etapa

*(As cenas desta parte são escritas conforme cada etapa roda. Cada etapa tem cinco momentos:
origem, entrada, resultado, leitura crítica e ajuste.)*

### Cena 6 — A lista de projetos

**TELA:** `shots/001-lista-de-projetos.png`

**NARRAÇÃO:**
Esta é a tela inicial do LangNet. Cada cartão é um sistema que já foi gerado por ele. Vamos criar
mais um, do zero, e acompanhar cada etapa até ele estar rodando.

---

### Cena 7 — O formulário de criação

**TELA:** `shots/002-formulario-novo-projeto.png`

**NARRAÇÃO:**
Criar um projeto pede nome, domínio e descrição — e, em opções avançadas, quatro escolhas
técnicas que valem para toda a geração.

---

### Cena 8 — As escolhas técnicas, abertas

**TELA:** `shots/900-opcoes-framework-protocolo-modelo.png`

**NARRAÇÃO:**
Aqui estão as opções, todas abertas ao mesmo tempo.

O **domínio** organiza o vocabulário do projeto: escolhemos Saúde.

O **modelo de linguagem** é quem vai construir: modelo local sem custo, Claude pela API própria
sem custo por token, DeepSeek ou OpenAI na nuvem pagos por uso. Vale a pena separar duas coisas
que costumam se confundir: esta escolha é a do modelo que **constrói** o sistema. O modelo que o
**sistema gerado** usa para funcionar é outra configuração, na tela do projeto — e são escolhas
independentes.

O **framework** é a biblioteca de agentes que o código gerado vai usar: CrewAI é o padrão, e há
LangChain, LangGraph, AutoGen e os SDKs da OpenAI e da Anthropic.

O **protocolo** é como os agentes conversam entre si: OKF é o nosso padrão; MCP, A2A, ACP e ANP
estão marcados como "em breve" — e estão marcados assim porque ainda não estão prontos, não para
preencher a lista.

E o **sistema de memória**, que guarda o que os agentes aprenderam: LangChain, Redis, Pinecone,
ChromaDB, ou nenhum.

**NOTA DE PRODUÇÃO:** um seletor nativo abre uma janelinha do sistema operacional, que não entra
em captura de tela. As opções desta imagem são as mesmas do formulário, apenas desenhadas em
lista.

---

### Cena 9 — O projeto preenchido

**TELA:** `shots/003-projeto-preenchido.png`

**NARRAÇÃO:**
Nome: BioByte Sentinela. Domínio: Saúde. A descrição resume o que a CCIH pediu — priorizar
pacientes por risco, confirmar o caso pela microbiologia, recomendar o pacote de prevenção e
estimar a redução de risco, com registro auditável de cada decisão.

---

### Cena 10 — O projeto criado

**TELA:** `shots/004-projeto-criado.png`

**NARRAÇÃO:**
Projeto criado. À esquerda aparece o menu das etapas — é por ele que a geração caminha, uma etapa
de cada vez, cada uma nascendo da anterior.

---

### Cena 11 — A etapa de Documentos, vazia

**TELA:** `shots/005-etapa-documentos-vazia.png`

**NARRAÇÃO:**
Primeira etapa: documentos. É aqui que entra o material de origem. Nada foi anexado ainda.

---

### Cena 12 — A ata anexada

**TELA:** `shots/006-documento-anexado.png`

**NARRAÇÃO:**
Anexamos a ata da reunião com a CCIH — o mesmo documento das cenas de abertura. Doze mil e
quinhentos caracteres de conversa, sem nenhum requisito numerado, sem nenhum caso de uso escrito.
É fala de gente, organizada por assunto.

---

### Cena 13 — O documento carregado

**TELA:** `shots/007-documento-carregado.png`

**NARRAÇÃO:**
O documento foi lido e está pronto para a análise.

---

*(as cenas seguintes são escritas à medida que as etapas rodam)*

---

## Parte C — A etapa de Requisitos

### Cena 14 — O pedido de análise

**TELA:** `shots/141-instrucoes-e-pesquisa-web.png`

**NARRAÇÃO:**
A ata está anexada. Antes de iniciar, escrevemos as instruções que orientam a leitura — o que a
CCIH exigiu e nós não queremos que se perca: que os requisitos de segurança nomeiem o mecanismo,
que o login seja simples sem verificação em duas etapas, que a sessão valha em todas as telas, e
que o sistema registre o que os serviços externos **não** devolvem.

E marcamos a pesquisa complementar na web. Guarde isso: ela vai reaparecer mais adiante, e de um
jeito que talvez surpreenda.

---

### Cena 15 — A análise em andamento

**TELA:** `shots/142-analise-em-andamento.png`

**NARRAÇÃO:**
A ata não é lida de uma vez. Ela é cortada nos próprios títulos, em cinco pedaços, e cada pedaço
é analisado sozinho. Depois cada pedaço é **conferido de novo** contra o que saiu dele — a
pergunta "o que este trecho exige e não está na lista?".

Isso não é detalhe de implementação: é o que faz a etapa funcionar em qualquer modelo. Pedir os
cento e quarenta requisitos numa resposta só produz um texto que nenhum provedor entrega inteiro.

---

### Cena 16 — De onde vem cada requisito

**TELA:** `shots/131-trecho-de-onde-vem-os-requisitos.png`

**NARRAÇÃO:**
Esta é a tabela mais importante do documento, e é a primeira coisa que um revisor procura.

Cento e doze requisitos foram **extraídos da ata** — estão lá, ditos por alguém na reunião. Dez
vieram das **instruções** que demos à análise. Doze vieram da **pesquisa na web**. E oito são
**sugestão da própria IA** — ninguém os pediu, e por isso ficam separados, esperando aprovação.

Repare no que essa separação permite: o revisor consegue olhar o documento e dizer "isto eu pedi,
isto eu não pedi". Sem ela, sugestão de máquina e exigência de cliente se misturam — e é assim que
um sistema ganha funcionalidade que ninguém queria.

Logo abaixo, a tabela de requisitos: identificador, origem, nome, descrição, prioridade, atores,
dependências e critério de aceite. Cada linha tem também a frase da ata que a sustenta.

---

### Cena 17 — Rastreabilidade até a origem

**TELA:** `shots/134-trecho-rastreabilidade-requisito-trecho.png`

**NARRAÇÃO:**
Cada requisito declara de qual trecho da ata nasceu. A tabela cruza os dois.

Isso responde à pergunta que toda revisão faz: *"de onde você tirou isso?"*. E responde sem
depender de ninguém lembrar — a amarração é montada pelo programa, lendo os próprios dados.

---

### Cena 18 — O mapa de cobertura

**TELA:** `shots/135-trecho-mapa-de-cobertura.png`

**NARRAÇÃO:**
Quanto cada assunto da reunião rendeu, e de que procedência.

Serve para enxergar desequilíbrio: um assunto que ocupou meia hora de reunião e rendeu dois
requisitos provavelmente foi mal lido. É uma ferramenta de desconfiança, não de comemoração.

---

### Cena 19 — O que o sistema não conseguiu resolver

**TELA:** `shots/136-trecho-perguntas-em-aberto.png` e `shots/137-trecho-lacunas-e-pedidos.png`

**NARRAÇÃO:**
Aqui está a parte que mais diz sobre a qualidade da ferramenta: o que ela **não** resolveu.

As perguntas em aberto são as que a ata não responde — qual o tempo exato de expiração da sessão,
qual o tempo limite da consulta ao laboratório, quais são exatamente os bundles cadastrados.

E as lacunas são achados de verdade. Uma delas merece atenção: **não há auditoria de leitura**. A
CCIH pediu para auditar quem *alterou* registro. Ninguém pensou em auditar quem *leu* prontuário —
e isso é exigência da lei de proteção de dados.

Não foi um humano que percebeu. E o sistema **não** inventou a resposta: ele declarou a falta.

---

### Cena 20 — A pesquisa complementar

**TELA:** `shots/138-trecho-pesquisa-complementar.png`

**NARRAÇÃO:**
As fontes consultadas, agrupadas por consulta, com endereço. E, desta vez, elas produziram
requisito: doze deles, cada um citando a fonte que o sustenta — base legal do tratamento de dados,
atendimento a pedidos de acesso e portabilidade, registro das operações, notificação de incidente
de segurança.

Nada disso está na ata. Tudo isso a lei exige.

**NOTA DE PRODUÇÃO:** vale dizer na narração que esta seção nunca tinha funcionado em nenhuma
geração anterior — saía sempre com zero.

---

### Cena 21 — O documento pede revisão humana

**TELA:** `shots/140-trecho-aprovacoes.png`

**NARRAÇÃO:**
O documento termina com um quadro de aprovações em branco — responsável pelo negócio, responsável
técnico, responsável pela segurança — e com um aviso: documento gerado automaticamente, requer
revisão e aprovação humana antes de seguir.

O sistema não se declara pronto. Ele declara o que fez e pede conferência.

---

## Parte D — Corrigindo um requisito pela conversa

### Cena 22 — Achando o defeito

**TELA:** `shots/119-documento-antes-do-refino.png`

**NARRAÇÃO:**
Lendo o documento, dois requisitos não passam por uma revisão séria:

*"O painel deve responder em poucos segundos"* — e o critério de aceite diz *"medir o tempo e
verificar que está em poucos segundos"*. O critério repete o requisito. Não há como testar isso.

*"O sistema deve rodar continuamente na rotina da CCIH"* — mesmo problema. E o nome do ator saiu
com erro de digitação.

---

### Cena 23 — O pedido de correção

**TELA:** `shots/120-pedido-de-correcao-escrito.png`

**NARRAÇÃO:**
Escrevemos na conversa o que está errado e o que se espera. Em português, como se fala com um
analista.

O que acontece a seguir é o ponto desta cena: **o documento inteiro não vai para o modelo.** O
programa descobre quais requisitos o pedido atinge, manda só esses, recebe só esses de volta, e
troca no lugar.

---

### Cena 24 — O que mudou, e só o que mudou

**TELA:** `shots/122-comparacao-entre-versoes.png`

**NARRAÇÃO:**
A comparação abre lado a lado. Mudaram duas linhas: os dois requisitos apontados. Os outros cento
e quinze ficaram idênticos, caractere a caractere — não porque o modelo prometeu preservá-los, mas
porque ele nunca os viu.

E repare na correção: em vez de inventar "dois segundos", o sistema escreveu que o painel responde
dentro de um limite medido em segundos e que **o valor exato ainda será definido pela CCIH**.

Inventar o número seria pior do que deixar em aberto. Ele deixou em aberto.

---

### Cena 25 — As duas versões

**TELA:** `shots/115-historico-com-duas-versoes.png`

**NARRAÇÃO:**
O histórico guarda as duas: a versão um, da análise inicial, e a versão dois, do refinamento —
com o pedido que a originou registrado na descrição. Dá para voltar a qualquer uma.

---

## Parte E — A Especificação Funcional

### Cena 26 — De onde a especificação nasce

**TELA:** `shots/151-spec-origem-modal.png` e `shots/152-spec-origem-versoes.png`

**NARRAÇÃO:**
A etapa não deixa gerar sem antes escolher a origem: qual documento de requisitos, e **qual
versão dele**. São três cliques de propósito.

Isso não é burocracia. É o que permite, mais tarde, responder "esta especificação nasceu de qual
versão dos requisitos?" — e a resposta fica gravada, não depende de ninguém lembrar.

---

### Cena 27 — A geração em fases

**TELA:** `shots/154-spec-gerando.png`

**NARRAÇÃO:**
A especificação também não é escrita de uma vez. Primeiro o sistema monta um **plano**: quantos
casos de uso existem e quais são. Depois escreve os casos **em lotes**. Depois as demais seções.
E o programa monta o documento.

Foram treze chamadas ao modelo, e o resultado: **trinta e três casos de uso planejados, trinta e
três escritos**. Nenhum ficou pelo caminho.

---

### Cena 28 — Um caso de uso por dentro

**TELA:** `shots/158-spec-uc-001.png`

**NARRAÇÃO:**
Este é o UC-001, autenticar usuário. Ator, objetivo, pré-condições, pós-condições. E duas linhas
que valem a atenção: **os requisitos que este caso de uso realiza** — FR-001, 002, 005 e 006 — e a
**regra de negócio** que se aplica a ele.

Repare no que isso completa. O caso de uso aponta para os requisitos. Os requisitos apontam para o
trecho da ata. A corrente vai da fala da coordenadora da CCIH até aqui, e dá para percorrer nos
dois sentidos.

Abaixo, o fluxo principal: o que o usuário faz, o que o sistema responde, passo a passo.

---

### Cena 29 — O que acontece quando dá errado

**TELA:** `shots/159-spec-fluxos-de-excecao.png`

**NARRAÇÃO:**
Cada caso de uso traz fluxos alternativos e fluxos de exceção.

E aqui há um detalhe que merece ser mostrado: quando o e-mail não existe e quando a senha está
errada, o sistema responde **exatamente a mesma mensagem** — "E-mail ou senha inválidos".

Isso é prática de segurança: mensagens diferentes revelariam quais e-mails estão cadastrados.
Ninguém pediu isso na ata. Veio da leitura que o sistema fez das exigências de segurança.

---

### Cena 30 — Modelo de dados e rastreabilidade

**TELA:** `shots/160-spec-modelo-de-dados-conceitual.png` e `shots/162-spec-rastreabilidade.png`

**NARRAÇÃO:**
A especificação já esboça o modelo conceitual de dados — que a próxima etapa vai transformar em
tabelas — e fecha com a matriz de rastreabilidade, ligando requisito a caso de uso.

---

### Cena 31 — Leitura crítica: dois defeitos

**TELA:** `shots/163-spec-atores-do-sistema.png`

**NARRAÇÃO:**
Agora a parte honesta. Olhe a lista de atores do sistema.

Aparecem dezoito itens, entre eles "BioByte; CCIH", "BioByte; CCIH; médico", "médico; enfermeiro",
"médico; enfermeiro; administrador". Não são dezoito atores — são **combinações** de atores
tratadas como se fossem atores distintos. Os atores reais são quatro ou cinco.

E há um segundo defeito: duas seções receberam o número 12, e o título do Mapa de Cobertura saiu
com um pedaço de tabela grudado.

Nenhum dos dois compromete o conteúdo — os casos de uso estão certos. Mas são exatamente o tipo de
coisa que a próxima etapa consome, e por isso vale corrigir aqui, na conversa, antes de seguir.

**NOTA DE PRODUÇÃO:** esta cena existe para mostrar que a leitura crítica faz parte do método —
cada etapa é conferida no próprio documento antes de alimentar a seguinte.

---

## Parte F — Corrigindo a Especificação pela conversa

### Cena 32 — O pedido

**TELA:** `shots/164-spec-pedido-de-correcao.png`

**NARRAÇÃO:**
Escrevemos na conversa o defeito da cena anterior: a lista de atores traz combinações tratadas
como atores distintos, e queremos a lista real, cada ator uma vez, com o papel de cada um.

Repare no botão escolhido: **Refinar**, não "Analisar". Analisar só resume o documento; quem
altera é Refinar. É um atrito da interface que vale mostrar.

---

### Cena 33 — O refino acontece por trecho

**TELA:** `shots/165-spec-refino-em-andamento.png`

**NARRAÇÃO:**
A especificação tem duzentos e vinte e nove mil caracteres. Ela não vai inteira para o modelo.

O sistema a divide em quarenta e nove unidades — as seções e cada caso de uso — descobre que o
pedido nomeia a seção cinco, e refina **só ela**. As outras quarenta e oito não são tocadas.

---

### Cena 34 — Antes e depois

**TELA:** `shots/168-spec-atores-do-sistema.png`

**NARRAÇÃO:**
Antes, dezessete linhas, várias delas combinações: "BioByte; CCIH; médico", "médico; enfermeiro;
administrador", "Sistema; Servidor; Área de segurança do hospital".

Depois, treze atores reais, cada um uma vez, com o papel descrito. O BioByte é o sistema de
vigilância; a CCIH é a comissão que analisa e decide; o sistema do laboratório é serviço externo
que fornece resultados; a ANVISA é o órgão que recebe notificação obrigatória.

E repare no que ele separou: "Gerente de TI; Equipe de desenvolvimento" virou dois atores
distintos, com papéis diferentes. "Sistema; Servidor; Área de segurança" virou três.

O documento cresceu setecentos e oitenta e seis caracteres — exatamente o tamanho das descrições
acrescentadas. Nenhum caso de uso foi tocado.

---

## Parte G — O Modelo de Dados

### Cena 35 — De onde o banco nasce

**TELA:** `shots/174-dm-etapa-aberta.png` e `shots/175-dm-origem-escolhida.png`

**NARRAÇÃO:**
Mesma exigência das etapas anteriores: escolher a origem. O modelo de dados nasce de uma **versão
específica da Especificação** — a de hoje, 18 de setembro.

E há uma escolha a mais, que vale mostrar: o banco de destino. MySQL, aqui. A mesma especificação
gera para outro banco sem reescrever nada.

---

### Cena 36 — A especificação impõe as tabelas

**TELA:** `shots/176-dm-gerando.png`

**NARRAÇÃO:**
Enquanto gera, o sistema registra uma decisão importante: *"a seção 6 impõe 22 entidades"* —
Usuário, Paciente, Caso clínico, Registro de auditoria, Escore de Cox, Resultado de hemocultura, e
assim por diante.

O modelo de dados **não inventa tabela**. Ele é obrigado a realizar as entidades que a
Especificação declarou. É mais um elo da corrente: fala da CCIH, requisito, caso de uso, entidade,
tabela.

---

### Cena 37 — Vinte e quatro tabelas

**TELA:** `shots/178-modelo-de-dados-gerado.png`

**NARRAÇÃO:**
Vinte e quatro tabelas, com relacionamentos, tipos, chaves e índices.

E elas **aplicam de verdade**: rodei o script num banco vazio e as vinte e quatro foram criadas
sem um erro. Isso não é detalhe — um modelo de dados que não vira banco não serve para nada.

---

### Cena 38 — Uma tabela por dentro

**TELA:** `shots/181-dm-escore.png`

**NARRAÇÃO:**
A tabela dos escores de Cox. Repare na coluna `versao_modelo`: **VARCHAR de 120 caracteres**.

Esse número vem de uma frase da reunião. A médica disse: *"o nome do modelo vem como texto livre e
pode ser longo — 'Cox proportional hazards', por exemplo — então o campo tem que caber."*

Na geração anterior esse campo tinha vinte caracteres e estourava na primeira gravação, derrubando
o registro inteiro. A fala da reunião atravessou requisito, caso de uso e chegou ao tipo da coluna.

E `intervalo_confianca` está **opcional** — porque o serviço de Cox não devolve esse dado, e a ata
diz isso com todas as letras.

---

### Cena 39 — O sistema critica o próprio trabalho

**TELA:** `shots/183-dm-validacao-com-problemas.png`

**NARRAÇÃO:**
Esta é a tela mais honesta do pipeline. A etapa valida o que ela mesma acabou de gerar e mostra o
resultado: **nota 25 de 100, 21 problemas**.

Três deles são o mesmo defeito: colunas que recebem dado de serviço externo com cem caracteres,
abaixo do mínimo de cento e vinte — *identificador da amostra*, *intervalo de confiança do bundle*,
*intervalo de confiança da estimativa*. É a mesma armadilha da cena anterior, em outros campos.

Um quarto aponta que a coluna de e-mail tem valor padrão vazio sob um índice único: dois usuários
sem e-mail colidiriam.

**NOTA DE PRODUÇÃO:** vale narrar que eu conferi **uma** coluna, vi que estava certa, e concluí que
a regra tinha sido aplicada. O validador encontrou outras três onde não foi. A máquina foi mais
cética que o humano.

---

### Cena 40 — Corrigindo pela conversa

**TELA:** `shots/184-dm-pedido-de-correcao.png` e `shots/186-dm-refino-concluido.png`

**NARRAÇÃO:**
Pedimos a correção nomeando tabela e coluna. O agente corrigiu as três colunas alimentadas por
serviço externo — e **deixou intactas** outras três que também tinham cem caracteres, mas são
campos internos.

Ele aplicou a regra, não o padrão de texto. Isso é o que separa entender de substituir.

**NOTA DE HONESTIDADE:** das quatro correções pedidas no mesmo parágrafo, ele fez três. A do e-mail
ficou de fora. É um comportamento que se repetiu na Especificação: **um pedido, um alvo** — quando
o pedido junta alvos de naturezas diferentes, um deles escapa.

---

### Cena 41 — O modelo vira script

**TELA:** `shots/187-dm-aba-schema-sql.png`, `188-dm-aba-models-py.png`, `189-dm-aba-alembic.png`, `190-dm-aba-yaml.png`

**NARRAÇÃO:**
E aqui está o que essa etapa realmente entrega. Quatro abas, quatro artefatos do mesmo modelo:

O **Schema SQL** — o script que cria as tabelas.
O **models.py** — as classes Python, com SQLAlchemy e Pydantic, que o código gerado vai usar.
O **Alembic** — a migração versionada, para evoluir o banco sem perder dado.
E o **YAML** — a descrição legível do modelo, que as etapas seguintes consomem.

Não é um desenho de banco. É banco, código, migração e contrato, saindo juntos e coerentes entre
si.

---

## Parte H — Interface e Protótipo

### Cena 42 — A estrutura de menus do sistema

**TELA:** `shots/270-etapa-estrutura-de-menus.png`

**NARRAÇÃO:**
A etapa abre pela **Estrutura de Menus** — dezoito itens, trinta e três telas. É o menu que o
sistema vai ter, montado a partir dos casos de uso, com o endereço de cada tela e o caso de uso
que ela realiza.

Abaixo, a lista dos casos de uso: UC-001 Login, UC-002 Cadastro de Usuário, UC-003 Cadastro de
Paciente com Cateter, e assim por diante. Cada um diz quantas telas tem e a qual tabela se liga.

---

### Cena 43 — A tela do caso de uso

**TELA:** `shots/273-uispec-tela-antes-do-ajuste.png`

**NARRAÇÃO:**
Clicando no caso de uso, aparece a tela dele — **na aparência final**, a mesma que o protótipo e
o aplicativo terão. Não é um esboço ao lado do produto: é o produto.

Aqui é a tela de login: identificação com e-mail e senha, as etapas da autenticação, o painel de
sessão, e as mensagens de erro do caso de uso agrupadas e coloridas por gravidade.

Se o caso de uso declarar mais de uma tela, elas aparecem lado a lado.

---

### Cena 44 — Pedindo um ajuste pela conversa

**TELA:** `shots/274-uispec-pedido-de-ajuste.png`

**NARRAÇÃO:**
À direita, a conversa. O pedido é escrito em português, do jeito que se fala com um projetista:

*"Troque o botão Fechar por Esqueci minha senha e deixe os dois lado a lado, com o Entrar à
esquerda. Use a cor de destaque apenas no Entrar."*

Posição, cor, rótulo — o ajuste que um responsável pelo produto faria olhando a tela.

---

### Cena 45 — O ajuste entra e vira versão

**TELA:** `shots/275-uispec-tela-depois-do-ajuste.png`

**NARRAÇÃO:**
A tela volta com **Entrar** à esquerda, em destaque, e **Esqueci minha senha** ao lado, neutro. O
"Fechar" saiu.

E isso vira **versão 2** no histórico da etapa, com o registro do que a originou: *"refino por
chat — tela login"*. Nada se perde: dá para voltar à versão anterior a qualquer momento.

---

### Cena 46 — Renderizar a aplicação

**TELA:** `shots/277-uispec-montando-o-prototipo.png` e `shots/278-uispec-prototipo-montado-na-etapa.png`

**NARRAÇÃO:**
O botão **Renderizar protótipo** monta a aplicação inteira com as alterações — as trinta e três
telas ligadas pelo menu.

E monta **a partir das telas que você acabou de aprovar**. É o ponto que faz esta etapa valer: o
que se aprova é o que se navega, e é o que a implementação vai usar depois.

---

### Cena 47 — A aplicação navegável

**TELA:** `shots/279-prototipo-aberto-fora-do-langnet.png`

**NARRAÇÃO:**
O protótipo tem endereço próprio e abre em qualquer navegador, sem o LangNet em volta.

Repare no login: **Entrar** e **Esqueci minha senha**, lado a lado, exatamente como foi pedido na
conversa. O ajuste atravessou da conversa para a aplicação.

No menu à esquerda, as trinta e três telas — inclusive as de erro, com nome próprio: *Consulta de
Microbiologia — Falha do Laboratório*, *Escore de Cox — Serviço Indisponível*, *Caso Clínico —
Operação com Falha*.

---

### Cena 48 — Navegando o sistema

**TELA:** `shots/280-prototipo-ciclo-integrado.png`, `281-prototipo-painel-de-vigilancia.png`, `282-prototipo-classificacao-nhsn.png`

**NARRAÇÃO:**
Ciclo integrado, painel de vigilância, classificação NHSN. Dados de exemplo tirados do modelo de
dados, para o operador entender o que cada tela faz.

Na implementação, só uma peça muda: a origem dos dados deixa de ser o exemplo e passa a ser o
servidor. As telas são estas.

---
