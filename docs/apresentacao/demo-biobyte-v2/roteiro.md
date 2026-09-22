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

### Cena 13.1 — A ata, lida dentro do sistema

**TELA:** `shots/008-ata-texto-no-sistema.png`

**NARRAÇÃO:**
Antes de pedir qualquer coisa ao sistema, vale abrir o que foi carregado. O arquivo tem doze
quilobytes e é a transcrição de uma reunião — não um documento de requisitos formatado.

Está tudo em linguagem de hospital: *"o que mais nos custa é o tempo entre a hemocultura ficar
pronta no laboratório e alguém aqui perceber que aquele paciente tem uma infecção de corrente
sanguínea. Às vezes são dois dias."*

É deste texto que sairão os oitenta e três requisitos funcionais, os trinta e três casos de uso,
as vinte e cinco tabelas e as vinte e oito telas. Tudo o que vem a seguir tem origem aqui — e o
sistema guarda essa ligação, como as próximas cenas mostram.

---

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

**TELA:** `shots/176-dm-gerando.png` e `shots/470-dm-modelo-final-25-tabelas.png`

**NARRAÇÃO:**
Enquanto gera, o sistema registra uma decisão importante: *"a seção 6 impõe 22 entidades"* —
Usuário, Paciente, Caso clínico, Registro de auditoria, Escore de Cox, Resultado de hemocultura, e
assim por diante.

O modelo de dados **não inventa tabela**. Ele é obrigado a realizar as entidades que a
Especificação declarou. É mais um elo da corrente: fala da CCIH, requisito, caso de uso, entidade,
tabela.

---

### Cena 37 — Vinte e cinco tabelas

**TELA:** `shots/470-dm-modelo-final-25-tabelas.png`

**NARRAÇÃO:**
Vinte e cinco tabelas, com relacionamentos, tipos, chaves e índices.

E elas **aplicam de verdade**: rodei o script num banco vazio e as vinte e cinco foram criadas
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

**TELA:** `shots/330-uispec-etapa-telas-unificadas.png`

**NARRAÇÃO:**
A etapa abre pela **Estrutura de Menus** — dezenove itens, vinte e oito telas. É o menu que o
sistema vai ter, montado a partir dos casos de uso, com o endereço de cada tela e o caso de uso
que ela realiza.

Abaixo, a lista dos casos de uso: Login, Cadastro de Usuário, Cadastro de Paciente com Cateter,
Classificação NHSN, e assim por diante — trinta e três ao todo, todos cobertos.

**NOTA DE PRODUÇÃO:** vinte e oito telas para trinta e três casos de uso porque três telas
atendem mais de um caso de uso — a mesma tela de escore de Cox serve ao cálculo e à consulta.

---

### Cena 43 — A tela do caso de uso

**TELA:** `shots/340-uispec-tela-antes-do-ajuste.png`

**NARRAÇÃO:**
Clicando no caso de uso, aparece a tela dele — **na aparência final**, a mesma que o protótipo e
o aplicativo terão. Não é um esboço ao lado do produto: é o produto.

Aqui é a tela de login: identificação com e-mail e senha, as etapas da autenticação, o painel de
sessão e as mensagens de erro que o caso de uso nomeia, agrupadas por gravidade.

Se o caso de uso declarar mais de uma tela, elas aparecem lado a lado.

---

### Cena 44 — Pedindo um ajuste pela conversa

**TELA:** `shots/341-uispec-pedido-de-ajuste.png`

**NARRAÇÃO:**
À direita, a conversa. O pedido é escrito em português, do jeito que se fala com um projetista:

*"Troque o botão Cancelar por Esqueci minha senha e deixe os dois lado a lado, com o Entrar à
esquerda. Use a cor de destaque apenas no Entrar."*

Posição, cor, rótulo — o ajuste que um responsável pelo produto faria olhando a tela.

---

### Cena 45 — O ajuste entra e vira versão

**TELA:** `shots/342-uispec-tela-depois-do-ajuste.png`

**NARRAÇÃO:**
A tela volta com **Entrar** à esquerda, em destaque, e **Esqueci minha senha** ao lado, neutro. O
"Cancelar" saiu.

E isso vira **versão 2** no histórico da etapa, com o registro do que a originou: *"refino por
chat — tela login"*. Nada se perde: dá para voltar à versão anterior a qualquer momento.

---

### Cena 46 — Renderizar a aplicação

**TELA:** `shots/344-uispec-montando-o-prototipo.png` e `shots/345-uispec-prototipo-montado-na-etapa.png`

**NARRAÇÃO:**
O botão **Renderizar protótipo** monta a aplicação inteira com as alterações — as vinte e oito
telas ligadas pelo menu.

E monta **a partir das telas que você acabou de aprovar**. É o ponto que faz esta etapa valer: o
que se aprova é o que se navega, e é o que a implementação vai usar depois.

---

### Cena 47 — A aplicação navegável

**TELA:** `shots/346-prototipo-aberto-fora-do-langnet.png`

**NARRAÇÃO:**
O protótipo tem endereço próprio e abre em qualquer navegador, sem o LangNet em volta.

Repare no login: **Entrar** e **Esqueci minha senha**, lado a lado, exatamente como foi pedido na
conversa. O ajuste atravessou da conversa para a aplicação.

No menu à esquerda, as vinte e oito telas — inclusive as de erro, com nome próprio: *Escore de Cox
— Tratar Indisponibilidade do Serviço*, *Caso Clínico — Operação com Falha*.

E os dados são de exemplo, tirados do modelo de dados: o e-mail de uma enfermeira do hospital, o
registro de auditoria das sessões, a sessão que expirou. É o que faz o operador entender a tela
antes de ela existir de verdade.

---

### Cena 48 — Navegando o sistema

**TELA:** `shots/347-prototipo-painel-de-vigilancia.png`, `348-prototipo-ciclo-integrado-analise.png`, `349-prototipo-classificacao-nhsn.png`

**NARRAÇÃO:**
Painel de vigilância, ciclo integrado de análise, classificação NHSN. Vinte e oito telas
navegáveis, ligadas pelo mesmo menu.

Na implementação, só uma peça muda: a origem dos dados deixa de ser o exemplo e passa a ser o
servidor. As telas são estas.

---

## Parte I — Agentes e Tarefas

### Cena 49 — De onde nasce a divisão do trabalho

**TELA:** `shots/290-ats-etapa-aberta.png` e `shots/292-ats-origem-escolhida.png`

**NARRAÇÃO:**
A etapa de Agentes e Tarefas responde a duas perguntas: **quem** faz cada coisa no sistema, e
**qual trabalho** cada um executa.

A origem é a Especificação Funcional aprovada — os trinta e três casos de uso. Escolhida a versão,
a etapa registra de qual especificação este documento nasceu.

---

### Cena 50 — As instruções que carregam o que já aprendemos

**TELA:** `shots/293-ats-instrucoes.png`

**NARRAÇÃO:**
Antes de gerar, as instruções. Cada uma delas custou um ciclo de retrabalho nas rodadas anteriores:

*Um nome por dado* — `usuario_id` em toda tarefa, nunca `id_usuario`; divergência de nome faz a
tarefa recusar com o dado na mão.

*Toda saída prometida tem de ser produzida por algum passo.*

*Quem chama serviço externo obedece à ficha do serviço* — a consulta de microbiologia e o escore de
Cox chegam por MCP.

*Campo usado só dentro de uma condição não é entrada obrigatória.* *Texto fixo vai entre aspas.*

Não é conversa com o modelo: é o que o portão vai cobrar depois.

---

### Cena 51 — Quinze agentes, quarenta e cinco tarefas

**TELA:** `shots/354-ats-gerando.png` e `shots/362-ats-visao-geral-dos-agentes.png`

**NARRAÇÃO:**
Uma rodada, cento e um segundos, cento e cinco mil caracteres.

Quinze agentes, um por especialidade: autenticação, gestão de usuários, cadastro clínico,
integração com o laboratório, escore de risco, classificação clínica, multirresistência,
notificação, recomendação de tratamento, estimativa de redução, ciclo integrado, painel e
relatórios, auditoria encadeada, tratamento de falhas e conformidade com a LGPD.

E quarenta e cinco tarefas, agrupadas por módulo — cada uma com quem executa, o que recebe, o que
devolve e por qual passo cada saída é produzida.

---

### Cena 52 — A tarefa por dentro

**TELA:** `shots/364-ats-especificacao-detalhada-das-tarefas.png` e `shots/365-ats-modulo-escore-de-risco.png`

**NARRAÇÃO:**
Esta é a peça que a geração de código vai ler. A tarefa declara o agente responsável, as entradas
com nome e tipo, os passos na ordem, as consultas ao banco, os serviços externos que usa e o que
entrega.

Não é descrição literária: é contrato. O que estiver errado aqui vira defeito no sistema — e é por
isso que as próximas etapas conferem este documento antes de gerar qualquer linha.

---

### Cena 53 — Trinta e três de trinta e três

**TELA:** `shots/299-ats-matriz-de-rastreabilidade.png`

**NARRAÇÃO:**
A rastreabilidade liga cada caso de uso às tarefas que o atendem. Trinta e três casos de uso,
trinta e três cobertos — nenhum ficou órfão.

E o documento presta contas da instrução: a lista dos nomes canônicos. Conferido no documento: das
oitenta e três ocorrências do identificador de usuário, todas usam o nome canônico. A única menção
ao nome errado é a que proíbe usá-lo.

---

### Cena 54 — A etapa acusa as anteriores

**TELA:** `shots/296-ats-gap-analysis.png`

**NARRAÇÃO:**
E aqui está o que mais vale nesta etapa — esta captura é da **primeira** geração, antes das
correções; a cena 59 mostra a mesma seção depois. Antes de especificar qualquer tarefa, ela compara a
Especificação com o Modelo de Dados e lista **quinze lacunas**, cada uma com impacto e decisão.

Três são defeitos de verdade, herdados das etapas anteriores:

O banco não aceita os papéis *coordenadora da CCIH* e *enfermeiro responsável*, que os casos de uso
citam como atores.

O horizonte da estimativa de risco aceita sete, trinta, noventa e trezentos e sessenta e cinco
dias; o requisito FR-042 exige **cento e oitenta** — a tarefa teria de recusar justamente o que o
requisito manda atender.

E o e-mail do usuário é obrigatório com valor padrão vazio, sob índice de valor único: o segundo
cadastro sem e-mail seria recusado por repetição.

Nenhum desses três apareceu quando o Modelo de Dados foi gerado. Apareceram agora, porque outra
etapa leu o mesmo artefato com outra pergunta.

---

## Parte J — A etapa seguinte conserta a anterior

### Cena 55 — O pedido de correção, em português

**TELA:** `shots/306-dm-validacao-com-problemas.png` e `shots/307-dm-pedido-de-correcao.png`

**NARRAÇÃO:**
Com as lacunas na mão, voltamos ao Modelo de Dados — na conversa da própria etapa, sem editar
arquivo nenhum:

*"Na tabela usuários, a coluna papel não aceita coordenadora da CCIH nem enfermeiro responsável;
acrescente os dois, mantendo os que já existem."*

*"O horizonte da estimativa aceita 7, 30, 90 e 365; acrescente 180, porque o requisito FR-042
exige 30, 90 e 180."*

*"O e-mail é obrigatório com valor padrão vazio, sob índice de valor único; remova o valor
padrão."*

---

### Cena 56 — Duas correções entram, uma resiste

**TELA:** `shots/308-dm-refino-em-andamento.png`

**NARRAÇÃO:**
Os dois primeiros entram na versão seguinte: o papel passa a aceitar os dois cargos, e o horizonte
passa a aceitar cento e oitenta dias — o valor que o requisito exigia e o banco recusava.

O terceiro não. E o sistema respondia **"atualizado com sucesso"** — três vezes, sem alterar uma
linha.

**NOTA DE PRODUÇÃO:** esta cena é o gancho para a seguinte. Não resolver aqui.

---

### Cena 57 — Não era o modelo: era o programa

**NARRAÇÃO:**
A causa apareceu ao procurar quem escreve o SQL. **Não é o modelo de linguagem.** O SQL é emitido
pelo programa, a partir do modelo lógico — e o programa tinha uma regra: *coluna obrigatória ganha
valor padrão*, para que uma gravação que não a informe não seja recusada.

Regra boa, criada depois de seis gravações perdidas. Mas cega: aplicada também a coluna de **valor
único**, onde o padrão vazio faz o **segundo** cadastro colidir com o primeiro.

O agente obedecia; o programa desfazia em seguida, em silêncio. Por isso o pedido "falhava"
respondendo sucesso.

Duas correções, no lugar certo: coluna sob índice de valor único não recebe mais padrão; e a
resposta ao refino passa a ser escrita pelo programa **depois de comparar o modelo antes e
depois** — dizendo em quais tabelas mexeu, ou dizendo que não mexeu.

---

### Cena 58 — O mesmo defeito em quatro tabelas

**NARRAÇÃO:**
Refeito o pedido, a resposta passou a ser esta, e é conferível:

*"Modelo alterado: quatro linhas saíram e quatro entraram, em usuários, pacientes, resultados de
hemocultura e tokens de acesso."*

Quatro, não uma — porque a regra vale para toda coluna de valor único, e o mesmo defeito estava
escondido no número do prontuário, no identificador da amostra e no token de acesso. Nenhum deles
tinha sido pedido; todos teriam quebrado a segunda gravação.

É a diferença entre corrigir um sintoma e corrigir a regra que o produz.

---

### Cena 59 — As lacunas fechadas

**TELA:** `shots/361-ats-gap-analysis-preliminar.png`

**NARRAÇÃO:**
Com o modelo de dados corrigido, a etapa foi regerada. A lista de lacunas caiu de **quinze para
quatro** — e nenhuma das três que tinham sido corrigidas voltou.

Repare numa delas, que mudou de lado. Antes: *"o banco não aceita coordenadora da CCIH nem
enfermeiro responsável"*. Agora: *"o banco aceita os dois, mas o caso de uso de cadastro ainda não
os oferece"*.

A lacuna subiu um degrau. Deixou de ser defeito do banco e virou item da Especificação — que é
exatamente onde ela tem de ser resolvida.

As quatro que restam são honestas e ficam declaradas: recuperação de senha, cópia de segurança,
auditoria de leitura, e o cadastro dos dois papéis novos. Nenhuma delas foi inventada pelo sistema;
todas faltam mesmo no documento de origem.

---

## Parte K — Ferramentas

### Cena 60 — Quem implementa cada serviço

**TELA:** `shots/379-ferramentas-etapa-aberta.png` e `shots/380-ferramentas-levantando.png`

**NARRAÇÃO:**
As tarefas pedem serviços: consultar o laboratório, calcular o escore, gravar no banco, ler um
PDF, enviar e-mail. Esta etapa responde **quem implementa cada um**.

Ela lê o documento de Agentes e Tarefas e levanta a lista — não por adivinhação: cada ferramenta
vem com os agentes e as tarefas que a citam.

Cinco ferramentas. Quatro se resolvem sozinhas: o acesso ao banco vira passo de consulta dentro da
própria tarefa; a leitura de PDF e a execução de SQL já existem na biblioteca; a chamada externa é
um encaminhador, e o serviço real é o que está atrás dele — laboratório, escore de Cox e e-mail,
os três por MCP.

---

### Cena 61 — A quinta não se resolve, e a etapa diz por quê

**TELA:** `shots/383-ferramentas-pendencia.png`

**NARRAÇÃO:**
A quinta fica pendente: o leitor de JSON, usado por quatro tarefas. E a etapa não esconde — diz o
passo e o motivo.

Aqui está o ponto que vale mostrar. O primeiro motivo era **de rótulo**: o passo que guarda o
resultado de uma expressão chama-se *cálculo*, e o modelo escreveu *atribui* — o nome do campo no
lugar do nome do passo. O passo estava completo e correto; o contrato inteiro era recusado pela
etiqueta.

Corrigido isso no programa — e só quando os campos são exatamente os do passo certo, para que
passo incompleto continue sendo recusado — apareceram os **dois defeitos de verdade**, que a
reclamação de nome vinha escondendo: uma expressão com colchete, que a linguagem de regras não
tem, e um valor prometido na saída que nenhum passo produzia.

---

### Cena 62 — A correção pela conversa

**TELA:** `shots/384-ferramentas-pedido.png` e `shots/385-ferramentas-depois-do-refino.png`

**NARRAÇÃO:**
O pedido vai pela conversa da etapa, dizendo o que a linguagem aceita:

*"Reescreva sem colchete, com o passo de cálculo dados igual a de_json do texto. E acrescente um
passo que produza o valor válido — o retorno só pode listar o que algum passo produziu."*

A regra volta com seis passos, o valor válido produzido por um passo, e nenhum colchete.

---

### Cena 63 — Cinco de cinco

**TELA:** `shots/386-ferramentas-inventario-resolvido.png` e `shots/387-ferramentas-aprovada.png`

**NARRAÇÃO:**
Cinco ferramentas, cinco resolvidas, nenhuma pendente. A etapa é aprovada, e a aprovação fica
gravada com data e hora.

**A honestidade da cena:** um passo da regra corrigida lê o campo chamado *caminho*, e não o campo
*indicado* por caminho. O contrato aceita, porque a forma está certa. A semântica é duvidosa, e
está anotada: quem vai cobrar isso é a etapa de Casos de Teste, executando a ferramenta e
conferindo a resposta.

---

## Parte L — YAML de Agentes e Tarefas

### Cena 64 — O documento vira configuração executável

**TELA:** `shots/404-yaml-etapa-aberta.png` e `shots/405-yaml-agentes-origem.png`

**NARRAÇÃO:**
Até aqui tudo é documento para pessoa ler. Esta etapa traduz o documento de Agentes e Tarefas em
**dois arquivos de configuração** que o sistema executa: um descreve os agentes, outro as tarefas.

A origem é escolhida na lista, com a contagem à vista — *quinze agentes, quarenta e cinco
tarefas* —, e a etapa registra de qual versão nasceu.

---

### Cena 65 — Quinze agentes, quarenta e cinco tarefas

**TELA:** `shots/406-yaml-agentes-gerando.png` e `shots/410-yaml-tarefas-pronto.png`

**NARRAÇÃO:**
Sai exatamente o que entrou: quinze agentes e quarenta e cinco tarefas. Nenhuma tarefa aponta para
agente que não existe.

E cada tarefa traz o campo que decide **como** ela roda: trinta e oito são determinísticas — o
programa executa, sem modelo de linguagem — e sete são de julgamento, que é quando o agente é
chamado. É a arquitetura híbrida escrita no arquivo, não na intenção.

---

### Cena 66 — O que faltava: as ferramentas

**NARRAÇÃO:**
E aqui esta etapa quase deixou passar o defeito mais caro do dia.

Na primeira geração, os quinze agentes e as quarenta e cinco tarefas saíram **sem nenhuma
ferramenta declarada**. O inventário da etapa anterior tinha cinco ferramentas resolvidas — e
nenhuma chegava ao arquivo. Na prática: o aplicativo gerado não teria como chamar o laboratório,
o escore de Cox nem o e-mail. As três integrações reais do sistema, mudas.

A informação que faltava já estava gravada: cada ferramenta do inventário diz **quem a usa**.
Ninguém precisava perguntar ao modelo — bastava ler o que a etapa anterior tinha apurado.

Agora o programa lê o inventário e escreve as ferramentas em cada agente e em cada tarefa. Com
critério: a chamada externa vai só para os quatro que falam com fora; o leitor de JSON, para os
dois que recebem resposta de serviço; o leitor de PDF, só para quem exporta relatório. Ferramenta
não resolvida não entra — declarar o que ninguém implementa seria pior que a falta.

---

### Cena 67 — E a trava que nasceu do erro

**NARRAÇÃO:**
A primeira versão dessa ligação **quebrou o arquivo de tarefas**: escreveu as ferramentas num
nível de recuo errado, e o arquivo deixou de ser lido.

O erro apareceu porque o artefato foi conferido — não porque a tela disse "gerado com sucesso".

Duas coisas saíram dali: o recuo passou a ser o da primeira linha do bloco, e o programa ganhou
uma trava — depois de acrescentar as ferramentas, ele tenta ler o arquivo de volta; se não
conseguir, descarta o acréscimo, mantém o original e **diz que descartou**.

Um arquivo de configuração quebrado derruba a geração de código inteira. Esta trava custa
milissegundos.

---

## Parte M — Sequência de Tarefas

### Cena 68 — Três origens, uma sequência

**TELA:** `shots/419-sequencia-etapa-aberta.png` e `shots/420-sequencia-tres-origens.png`

**NARRAÇÃO:**
Esta etapa responde **em que ordem** o sistema faz o que faz, e **o que cada tarefa recebe e
entrega**.

Ela exige três origens, e não deixa gerar sem as três: a Especificação Funcional, o documento de
Agentes e Tarefas, e o arquivo de configuração das tarefas. Cada uma é escolhida na sua aba, e a
etapa registra de qual versão veio.

---

### Cena 69 — O estado que atravessa o sistema

**TELA:** `shots/424-seq-visao-geral.png` e `shots/425-seq-definicao-do-state.png`

**NARRAÇÃO:**
Primeiro, o **estado**: a estrutura que atravessa o sistema inteiro, passando de tarefa em tarefa.

Ela vem em três partes: o que entra no começo — configuração e dados do usuário; o que cada
tarefa **produz**, com a coluna dizendo quem produz e quem consome; e os metadados de execução.

É essa tabela que impede o defeito mais comum de sistema multiagente: a tarefa que espera um dado
que ninguém produziu.

---

### Cena 70 — A tarefa, com o SQL e a mensagem do caso de uso

**TELA:** `shots/426-seq-sequencia-de-execucao.png`

**NARRAÇÃO:**
E então, tarefa por tarefa — quarenta e cinco delas.

Veja a primeira. A função de entrada diz o que ela tira do estado: e-mail e senha. Os passos são
concretos: busca o usuário com o SQL escrito por extenso, usando a ferramenta `database_tool` —
a mesma que a etapa anterior ligou a este agente. Se não achar, ou se o usuário estiver inativo,
devolve **"E-mail ou senha inválidos"** — a frase exata do caso de uso. Confere a senha contra o
resumo criptográfico guardado. Emite o token, grava, e captura o identificador com uma consulta
explícita, nunca com o atalho que quebra sob concorrência.

Isto não é mais descrição: é o que a geração de código vai transformar em programa.

---

### Cena 71 — Quarenta e cinco não cabem numa resposta só

**NARRAÇÃO:**
A primeira tentativa saiu **cortada no meio de uma frase**, com oito tarefas das quarenta e cinco.

É um defeito que este projeto já conhecia e já tinha resolvido duas vezes — na Especificação e nos
Requisitos. A causa nunca é o modelo: é o tamanho do pedido.

Agora o programa corta a lista em blocos de seis, pede o cabeçalho e o estado num pedido curto,
pede cada bloco em separado — mandando só o recorte da configuração daquelas seis tarefas — e
monta o documento.

Resultado medido: **quarenta e cinco de quarenta e cinco**, cento e quarenta e quatro mil
caracteres, noventa blocos de código, dois minutos. Nenhuma tarefa faltando, nenhuma repetida,
nenhuma inventada.

**NOTA DE PRODUÇÃO:** cena sem captura — narrar sobre a Cena 70 ou sobre o log dos oito lotes.

---

## Parte N — Rede de Petri

### Cena 72 — O sistema vira um modelo formal

**TELA:** `shots/427-petri-etapa-aberta.png` e `shots/433-petri-origens.png`

**NARRAÇÃO:**
Esta etapa transforma o sistema num **modelo formal**: uma rede de Petri.

Ela come três artefatos, todos gerados nesta mesma cascata: a configuração dos agentes, a das
tarefas e o documento de sequência. Lugares são estados; transições são as tarefas; a ficha é o
trabalho andando.

Não é diagrama ilustrativo — é o que o executor do aplicativo vai percorrer.

---

### Cena 73 — Quarenta e nove lugares, quarenta e oito transições

**TELA:** `shots/492-petri-rede-conferida.png`

**NARRAÇÃO:**
A rede sai com quarenta e nove lugares, quarenta e oito transições, cento e sessenta e dois arcos
e quinze agentes — cada lugar sabe a qual agente pertence.

À esquerda, a ficha inicial. O fluxo entra pela autenticação, passa pela validação do token, e
então se abre: cadastros, classificação, microbiologia, escore de risco.

---

### Cena 74 — Oito conferências, e o que cada uma responde

**NARRAÇÃO:**
Uma rede bonita que executa errado não serve. Por isso ela é conferida contra os artefatos que a
originaram, e cada conferência responde a uma pergunta concreta:

*As quarenta e cinco tarefas da sequência estão na rede?* **Quarenta e cinco de quarenta e cinco.**

*Todo arco liga um lugar a uma transição, como a regra da rede de Petri exige?* **Zero arcos
inválidos.**

*Toda tarefa é alcançada a partir da ficha inicial?* **Todas** — e o fim do fluxo também.

*Cada lugar aponta para um agente que existe na configuração?* **Sim, nenhum inválido.**

E a mais importante: *a ordem respeita os dados?* Se a estimativa de redução de risco consome o
identificador da recomendação, a recomendação tem de vir antes. **Cinquenta e seis dependências
conferidas, zero violações.**

---

### Cena 75 — O que estava errado, e como se conserta

**NARRAÇÃO:**
Nada disso passou de primeira, e vale contar por quê.

**Nenhum lugar da rede declarava o que entrega.** Zero de quarenta e nove — enquanto quarenta e um
declaravam o que consomem. A rede sabia o que cada tarefa recebe e não sabia o que ela produz, e
por isso não tinha como saber de onde vem cada dado.

A causa não era o modelo: era o programa procurando a resposta no lugar errado. Ele buscava a
saída num formato estruturado, e a configuração das tarefas declara em **português corrido** —
*"retornar um JSON com as chaves resultado_id e situacao"*. Ensinado a ler o texto, passou de zero
para **quarenta e uma de quarenta e cinco** tarefas com saída declarada.

Com isso, duas correções viraram possíveis, e as duas são feitas pelo programa, não por pedido ao
modelo: a tarefa chamada sob demanda — a que trata campo sem dado — deixa de ficar ilhada, ligada
pelo dado que consome; e a ordem passa a obedecer o que a sequência **declara**, ligando cada
consumidor à saída do seu produtor.

E cada costura fica escrita: *"a estimativa passou a vir depois da recomendação porque consome o
identificador da recomendação, produzido por ela"*.

**NOTA DE PRODUÇÃO:** cena sem captura — narrar sobre a rede da cena 73.

---

## Parte O — Casos de Teste

### Cena 75 — De caso de uso para caso de teste, por método

**TELA:** `shots/436-testes-etapa-aberta.png`

**NARRAÇÃO:**
Esta etapa não pede ao modelo que "invente testes". Ela aplica um método com nome e idade: o
**Grafo de Causa-Efeito**.

As **causas** são o que o operador faz e as condições do sistema — acessar a tela, preencher os
campos, ter credenciais válidas, estar ativo. Os **efeitos** são o que o sistema responde. As
regras ligam uns aos outros, e as **restrições** dizem o que não pode coexistir: causas
mutuamente exclusivas, causas que obrigam outras.

Dali sai uma tabela de decisão, e **cada coluna da tabela é um caso de teste**. Não é opinião: é
derivação.

---

### Cena 76 — Trinta e três grafos, trezentos e sessenta e um casos

**TELA:** `shots/437-testes-gerando.png` e `shots/438-testes-prontos.png`

**NARRAÇÃO:**
Trinta e três casos de uso, trinta e três grafos, trezentos e sessenta e um casos de teste.

E cada caso diz **onde conferir**: na tela, no sistema — executando a tarefa e cobrando a
resposta — ou num serviço externo. Essa distinção existe porque já nos custou caro: um caso que
só procurava a frase "Credenciais inválidas" na tela passava com um login que não conferia senha
nenhuma.

---

### Cena 77 — O caso de uso que ficou com zero testes

**TELA:** `shots/439-testes-uc-sem-casos.png`

**NARRAÇÃO:**
Na primeira rodada, um caso de uso entre trinta e três saiu com **zero casos de teste** — o
cadastro de paciente com cateter. E ele tinha nove causas e dez efeitos: o grafo estava completo.

Pedimos ao agente que refizesse. Não adiantou — e não podia adiantar, porque a tabela de decisão
**não é escrita pelo modelo**: é calculada pelo programa, a partir do grafo.

O defeito estava no cálculo. Ao montar cada coluna, o programa considera só as causas que entram
na regra daquele efeito; as outras são indiferentes. Mas, na hora de conferir as restrições, ele
tratava as indiferentes como **falsas** — e isso reprova para sempre uma restrição do tipo "pelo
menos uma destas é verdadeira". Todas as combinações eram descartadas.

Corrigido: a restrição só reprova quando é impossível satisfazê-la com **qualquer** valor das
causas indiferentes.

O caso de uso passou de zero para treze casos. E o efeito foi maior do que ele: no projeto
inteiro, **de duzentos e setenta e dois para trezentos e sessenta e um casos** — oitenta e nove
testes que existiam por direito e estavam sendo engolidos em silêncio.

---

### Cena 78 — O que a etapa admite sobre si mesma

**NARRAÇÃO:**
Dezesseis casos saem marcados como **contraditórios**, com o motivo escrito: *"todas as causas são
verdadeiras e o efeito descreve uma exceção — falta na tabela a causa que a dispara"*.

É a etapa dizendo que o grafo daquele caso de uso está incompleto: a exceção existe no texto, mas
a condição que a provoca não foi declarada como causa.

Ela podia ter escondido — bastava não marcar. Preferiu entregar o caso com a ressalva colada.

**NOTA DE PRODUÇÃO:** cena sem captura — narrar sobre a tela da Cena 76.

---
