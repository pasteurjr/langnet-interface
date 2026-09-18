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
