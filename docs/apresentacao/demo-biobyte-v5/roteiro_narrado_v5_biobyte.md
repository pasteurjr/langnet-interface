# Roteiro narrado — BioByte Sentinela v5

**Projeto-teste:** BioByte Sentinela v5 · vigilância de infecção de corrente sanguínea associada a cateter
**Pasta das telas:** `docs/apresentacao/demo-biobyte-v5/telas/`
**Como ler:** cada cena traz **a tela** (caminho do arquivo), **a narração** (texto exato, no tom do narrador) e **a produção** (o que destacar, quanto tempo, o que evitar).
**Duração estimada:** 11 a 13 minutos.

> Regra deste roteiro: nada é afirmado que não esteja na tela. Onde o sistema falhou, a cena mostra a falha.

---

## Bloco 1 — O problema que a versão 5 veio resolver

### Cena 1 · O pedido do hospital

**Tela:** `telas/01-documento-fonte.png`

**Narração:**
> Isto é o levantamento de requisitos do BioByte Sentinela. Uma médica infectologista, uma enfermeira de controle de infecção e um analista de laboratório contaram o que precisam. O problema deles é tempo: entre a hemocultura ficar pronta no laboratório e alguém perceber que aquele paciente tem uma infecção, às vezes passam dois dias. E quando o germe é multirresistente, dois dias é muita coisa.

**Produção:** 12 segundos. Destaque o bloco de citação da médica. Não leia o documento inteiro.

---

### Cena 2 · A decisão que mudou tudo: o que é inteligência artificial e o que não é

**Tela:** `telas/02b-requisitos-coluna-natureza.png`

**Narração:**
> Este é o documento de requisitos que o sistema produziu a partir daquela conversa. Repare na marcação de cada requisito. Um sistema hospitalar tem duas metades bem diferentes. Uma é cadastro, consulta, relatório — trabalho de sempre, que um programa comum resolve. A outra é julgamento clínico: ler um antibiograma e decidir, escrever o alerta que a equipe vai ler. Só essa segunda metade é trabalho de agente.
>
> Na versão anterior essa distinção não existia em lugar nenhum, e o sistema tratou quarenta e cinco coisas como trabalho de agente — inclusive cadastro de usuário. Agora a separação está declarada requisito por requisito, e vem do próprio documento do hospital.

**Produção:** 25 segundos. Destaque com moldura a coluna de natureza, mostrando os dois valores lado a lado. Esta é a cena mais importante do primeiro bloco — dê tempo de ler.

---

### Cena 3 · A separação chega ao caso de uso

**Tela:** `telas/03b-caso-de-uso-natureza.png`

**Narração:**
> A mesma separação desce para o caso de uso. Cada caso de uso agora declara a sua natureza e, quando é de agente, declara também o que exatamente o agente decide. Não é uma anotação decorativa: é o que o resto da linha de produção vai ler para saber quem faz o quê.

**Produção:** 15 segundos. Destaque as duas linhas — natureza e decisão do agente.

---

## Bloco 2 — A linha de produção

### Cena 4 · Cinco tarefas, dois agentes

**Tela:** `telas/04b-cinco-tarefas-dois-agentes.png`

**Narração:**
> E aqui está o resultado. Trinta e um casos de uso entraram; seis são de agente; e a especificação de agentes e tarefas produziu cinco tarefas distribuídas em dois agentes. Traduzir o resultado do laboratório para o vocabulário do hospital. Classificar o caso pelo critério da norma. Avaliar multirresistência. Recomendar o pacote de medidas com justificativa. Redigir o alerta para a equipe.
>
> Cinco. Na versão anterior eram quarenta e cinco.

**Produção:** 22 segundos. Destaque a lista das cinco tarefas. Se couber, mostre o número "45" da versão anterior num canto, para contraste.

---

### Cena 5 · O contrato com o CrewAI

**Tela:** `telas/05-yaml-crewai.png`

**Narração:**
> As tarefas viram dois arquivos de configuração no formato que o CrewAI entende. Um descreve os agentes — papel, objetivo, história. O outro descreve as tarefas — o que fazer e o que se espera de saída. Nada além disso: quem executa cada tarefa e com quais ferramentas é decidido na geração do código, não aqui.

**Produção:** 14 segundos. Destaque `description` e `expected_output` numa tarefa.

---

### Cena 6 · O modelo de dados

**Tela:** `telas/06b-modelo-antibiograma.png`

**Narração:**
> O modelo de dados sai da mesma fonte. Vinte e oito tabelas, entre elas as que vão sustentar a decisão clínica: o resultado da hemocultura, o antibiograma, os antimicrobianos com as suas classes. É contra estas tabelas que os agentes vão trabalhar — não contra um exemplo inventado.

**Produção:** 14 segundos. Destaque a tabela de antibiograma.

---

### Cena 7 · As telas do hospital

**Tela:** `telas/07-interface-telas.png`

**Narração:**
> A especificação de interface desenha as telas do sistema a partir dos casos de uso. Trinta telas. E aqui aparece de novo a separação: as telas de cadastro e relatório são convencionais; as que chamam um agente ficam marcadas como tal.

**Produção:** 14 segundos.

---

### Cena 8 · A planta do fluxo

**Tela:** `telas/08-rede-de-petri.png`

**Narração:**
> Esta é a planta do fluxo, em rede de Petri. Sete lugares, seis transições. Cada lugar é uma tarefa de agente esperando a sua vez; cada transição é a regra que libera a próxima. A marca começa no início e só avança quando o lugar anterior concluiu de verdade. Isto não é um desenho ilustrativo: é o que vai ser executado.

**Produção:** 18 segundos. Destaque a sequência dos cinco lugares centrais.

---

### Cena 9 · O sistema sai pronto

**Tela:** `telas/09-codigo-gerado.png`

**Narração:**
> A geração de código monta o sistema inteiro: o servidor dos agentes, a interface do hospital, o banco com o seu esquema, e a ligação entre eles. Cento e trinta e seis arquivos.

**Produção:** 12 segundos.

---

## Bloco 3 — As duas interfaces

> Nota de produção: este bloco existe porque há **duas** coisas para ver, e elas são diferentes. A interface do hospital é o que o médico usa. A Bancada de Execução é o nosso instrumento — é onde se vê a rede rodando por dentro.

### Cena 10 · A interface do hospital

**Tela:** `telas/20-app-inicial.png`

**Narração:**
> Esta é a interface do sistema gerado — o que o hospital usa. Atendimento, engajamento, relatórios, integrações, cadastros. E repare no menu: as telas marcadas com o losango são as que chamam um agente; as outras são convencionais. A separação que começou no documento do hospital chegou até o menu lateral.

**Produção:** 18 segundos. Destaque dois itens do menu lado a lado — um com losango, um sem.

---

### Cena 11 · A Bancada de Execução

**Tela:** `telas/30-bancada-rede.png`

**Narração:**
> E esta é a Bancada de Execução. É a outra interface, e serve a outro propósito: aqui a rede de Petri aparece inteira e roda diante de nós. Não é uma animação — cada lugar abre uma conversa com o servidor dos agentes, manda a tarefa, e espera a resposta.

**Produção:** 16 segundos.

---

### Cena 12 · A marca andando

**Telas:** `telas/31-bancada-passo.png`, `telas/32-bancada-passo.png`, `telas/33-bancada-passo.png`

**Narração:**
> A marca sai do início e entra na primeira tarefa: traduzir o resultado do laboratório. Concluída, a transição libera a próxima: classificar o caso. Depois, avaliar multirresistência. Cada passagem dessas é uma tarefa de verdade sendo executada, contra o banco de verdade.

**Produção:** 20 segundos, cortando entre as três capturas no ritmo da narração.

---

## Bloco 4 — A prova

### Cena 13 · A pergunta que não admite conversa

**Tela:** `telas/50-prova-multirresistencia.png`

**Narração:**
> Aqui está a prova. Plantamos no banco dois casos. No primeiro, o germe é resistente a quatro classes de antimicrobianos — pela regra, é multirresistente. No segundo, é resistente a uma só — não é. Se o sistema responder a mesma coisa nos dois, ele está inventando.
>
> A tarefa consultou o banco, fez a junção entre antibiograma e antimicrobianos, e respondeu: no primeiro caso, quatro classes — cefalosporina, betalactâmico, fluoroquinolona e aminoglicosídeo. No segundo, uma: fluoroquinolona. Acertou os dois.

**Produção:** 28 segundos. Destaque os dois números lado a lado — quatro e um. Esta é a cena que sustenta o vídeo inteiro.

---

### Cena 14 · O que ainda falta, dito na cara

**Tela:** `telas/51-portao-logica.png`

**Narração:**
> E aqui está o que ainda não funciona. A conta saiu certa: quatro classes. Mas o campo que diz "é multirresistente, sim ou não" voltou vazio. A regra prática — resistência a três ou mais classes — não virou código, e o modelo também não a aplicou.
>
> O interessante é que o sistema sabia disso antes de rodar. O portão de lógica, que confere se cada passo descrito na tarefa virou código, tinha apontado esse passo exatamente. Ele não impediu o defeito, mas o nomeou antes que alguém fosse enganado por ele.

**Produção:** 25 segundos. Destaque `multirresistente: null` ao lado de `contagem_classes_resistentes: 4`. Em seguida, o item correspondente na lista do portão.

---

### Cena 15 · Falha não passa calada

**Tela:** `telas/34-bancada-falha-bloqueia.png`

**Narração:**
> E quando uma tarefa falha, a rede para. Esta tarefa não recebeu o que precisava e devolveu erro; a transição seguinte não disparou. É assim que tem de ser: um sistema que segue em frente com dado ruim entrega um laudo errado com cara de laudo certo.

**Produção:** 16 segundos. Destaque o lugar em vermelho e a transição que não disparou.

---

## Encerramento

**Tela:** `telas/08-rede-de-petri.png` (retomada)

**Narração:**
> Do documento do hospital até o sistema rodando, sem ninguém escrever código. O que mudou nesta versão não foi o modelo nem a ferramenta: foi ter declarado, desde o requisito, o que é trabalho de inteligência artificial e o que é trabalho de sempre. Cinco tarefas em vez de quarenta e cinco. E o que ainda falta está apontado, não escondido.

**Produção:** 18 segundos. Fecha na rede.
