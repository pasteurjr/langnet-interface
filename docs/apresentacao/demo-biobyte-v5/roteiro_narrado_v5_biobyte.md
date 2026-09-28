# Roteiro narrado — LangNet e o BioByte Sentinela v5

**O que este vídeo mostra:** o LangNet, que é a fábrica, e o sistema que ele produziu —
o BioByte Sentinela, de vigilância de infecção de corrente sanguínea associada a cateter.

**Pasta das telas:** `docs/apresentacao/demo-biobyte-v5/telas/`
**Registro dos testes:** `registro_de_testes.md` — 22 de 23 casos, conferidos contra o banco
**Como ler:** cada cena traz **a tela** (caminho do arquivo), **a narração** (texto exato, no
tom do narrador) e **a produção** (o que destacar, quanto tempo, o que evitar).
**Duração estimada:** 16 a 18 minutos.

> Regra deste roteiro: nada é narrado que não esteja na tela. Onde o sistema falha, a cena
> mostra a falha.

---

# BLOCO 1 — O problema e a decisão que mudou tudo

## Cena 1 · O pedido do hospital

**Tela:** `telas/01-documento-fonte.png`

**Narração:**
> Isto é o levantamento de requisitos do BioByte Sentinela. Uma médica infectologista, uma
> enfermeira de controle de infecção e um analista de laboratório contaram o que precisam.
> O problema deles é tempo: entre a hemocultura ficar pronta no laboratório e alguém
> perceber que aquele paciente tem uma infecção, às vezes passam dois dias. E quando o
> germe é multirresistente, dois dias é muita coisa.

**Produção:** 12 s. Destaque a citação da médica. Não leia o documento inteiro.

---

## Cena 2 · O que é inteligência artificial e o que não é

**Tela:** `telas/02b-requisitos-coluna-natureza.png`

**Narração:**
> Um sistema hospitalar tem duas metades bem diferentes. Uma é cadastro, consulta,
> relatório — trabalho de sempre, que um programa comum resolve. A outra é julgamento
> clínico: ler um antibiograma e decidir, escrever o alerta que a equipe vai ler. Só essa
> segunda metade é trabalho de agente.
>
> Na versão anterior essa distinção não existia em lugar nenhum, e o sistema tratou
> quarenta e cinco coisas como trabalho de agente — inclusive cadastro de usuário. Agora a
> separação está declarada requisito por requisito.

**Produção:** 25 s. Moldura na coluna de natureza, com os dois valores lado a lado. Esta é a
cena mais importante do bloco — dê tempo de ler.

---

# BLOCO 2 — A linha de produção, etapa por etapa

## Cena 3 · Requisitos, com a origem de cada um

**Tela:** `telas/02-requisitos-natureza.png`

**Narração:**
> O documento de requisitos não é uma lista solta. Cada item diz de onde veio: extraído dos
> documentos, extraído das instruções do usuário, inferido pelo modelo com justificativa,
> vindo da pesquisa complementar, ou sugerido pela inteligência artificial e ainda
> aguardando aprovação.
>
> São noventa e nove requisitos funcionais, vinte e cinco não-funcionais e trinta e uma
> regras de negócio. Noventa deles vieram direto da ata; oito foram sugestão do modelo,
> marcados como tal para alguém decidir.
>
> E repare na seção da pesquisa web: ela declara que a pesquisa foi feita, que as fontes
> estão na seção complementar, mas que nenhuma gerou requisito novo — o que foi encontrado
> confirma o que a ata já dizia. O sistema não inventa requisito para parecer completo.

**Produção:** 30 s. Destaque os cabeçalhos das cinco seções de origem, depois o aviso da
pesquisa web.

---

## Cena 4 · Os casos de uso

**Tela:** `telas/03b-caso-de-uso-natureza.png`

**Narração:**
> Trinta e um casos de uso. Cada um traz ator principal, objetivo, pré e pós-condições, o
> fluxo principal com a ação do ator e a resposta do sistema, os fluxos alternativos, os de
> exceção, e um croqui da tela aderente a essas ações.
>
> E cada um aponta o requisito de onde nasceu, declara a sua natureza e, quando é de
> agente, declara também o que exatamente o agente decide.

**Produção:** 22 s. Destaque as linhas de Natureza e Decisão do Agente, depois role até o
croqui para mostrar que os botões do desenho são as ações do fluxo.

---

## Cena 5 · O modelo de dados

**Tela:** `telas/06b-modelo-antibiograma.png`

**Narração:**
> Vinte e oito tabelas, vinte e nove chaves estrangeiras, oitenta e cinco índices. Entre
> elas, as que sustentam a decisão clínica: o resultado da hemocultura, o antibiograma, os
> antimicrobianos com as suas classes. É contra estas tabelas que os agentes vão trabalhar.

**Produção:** 15 s.

---

## Cena 6 · As telas, desenhadas a partir dos casos de uso

**Tela:** `telas/07-interface-telas.png`

**Narração:**
> A especificação de interface desenha as telas a partir dos casos de uso. Trinta telas,
> quinhentos e noventa e sete componentes declarados — indicadores, tabelas, gráficos,
> campos, marcações. Os trinta e um casos de uso estão cobertos.

**Produção:** 15 s.

---

## Cena 7 · O protótipo, antes de existir sistema

**Tela:** `telas/73-prototipo-tela.png`

**Narração:**
> Antes de gerar uma linha de código do sistema, as telas já podem ser navegadas. Isto é o
> protótipo: as mesmas trinta telas, ligadas pelo menu, com dados de exemplo. Aqui está a
> trilha de auditoria — filtros por período e por usuário, a verificação de integridade do
> encadeamento, e as entradas com a marca da entrada anterior.
>
> É o que a tela deve fazer. Guarde esta imagem.

**Produção:** 22 s. Destaque o selo "Encadeamento íntegro · 1.284 entradas verificadas".

---

## Cena 8 · Quem implementa cada ferramenta

**Tela:** `telas/61-ferramentas-resultado.png`

**Narração:**
> Antes de gerar o sistema, uma pergunta precisa de resposta: cada ferramenta que os
> agentes vão usar, de onde vem a implementação? Esta etapa faz o inventário. Três
> ferramentas — consulta ao banco, leitura de dados estruturados e busca por semelhança — e
> as três com implementação declarada, nenhuma pendente.
>
> Não é burocracia. Um agente montado sem ferramenta responde, educadamente, que não
> conseguiu obter o dado.

**Produção:** 20 s. Destaque a coluna de origem e o contador "3 com implementação · 0 pendentes".

---

## Cena 9 · Cinco tarefas, dois agentes

**Tela:** `telas/04b-cinco-tarefas-dois-agentes.png`

**Narração:**
> Trinta e um casos de uso entraram; seis são de agente; e a especificação de agentes e
> tarefas produziu cinco tarefas em dois agentes. Traduzir o resultado do laboratório para
> o vocabulário do hospital. Classificar o caso pelo critério da norma. Avaliar
> multirresistência. Recomendar o pacote de medidas com justificativa. Redigir o alerta
> para a equipe.
>
> Cinco. Na versão anterior eram quarenta e cinco.
>
> E cada tarefa carrega a sua rastreabilidade: o caso de uso que implementa e os requisitos
> que atende.

**Produção:** 25 s. Destaque a lista das cinco e, depois, a linha de "UC Relacionado" e
"RF Relacionado" de uma delas.

---

## Cena 10 · O contrato com o CrewAI

**Tela:** `telas/05-yaml-crewai.png`

**Narração:**
> As tarefas viram dois arquivos no formato que o CrewAI entende. Um descreve os agentes —
> papel, objetivo, história. O outro descreve as tarefas — o que fazer e o que se espera de
> saída. Nada além disso.

**Produção:** 14 s. Destaque `description` e `expected_output`.

---

## Cena 11 · De onde saem os casos de teste

**Tela:** `telas/64-grafo-causa-efeito.png`

**Narração:**
> Os casos de teste não são escritos à mão. Esta etapa lê cada caso de uso e monta um grafo
> de causa e efeito. À esquerda, as causas: as ações do ator e as condições do mundo. À
> direita, os efeitos: o que o sistema responde. No meio, as combinações — este efeito só
> acontece se estas causas forem verdadeiras e aquela for falsa.

**Produção:** 22 s. Destaque um efeito e siga os arcos até as causas. Mostre um círculo de negação.

---

## Cena 12 · A tabela de decisão e o caso pronto

**Telas:** `telas/65-tabela-de-decisao.png` e `telas/66-casos-de-teste-texto.png`

**Narração:**
> Do grafo sai a tabela de decisão. Cada coluna é uma combinação possível — e cada coluna
> vira um caso de teste. Trinta e um casos de uso, quatrocentos e vinte e três casos de
> teste. E cada caso vem escrito: as entradas, que são as ações do ator, e a resposta
> esperada do sistema.

**Produção:** 22 s. Corte da tabela para o caso escrito.

---

## Cena 13 · A planta do fluxo

**Tela:** `telas/08-rede-de-petri.png`

**Narração:**
> Esta é a planta do fluxo, em rede de Petri. Sete lugares, seis transições. Cada lugar é
> uma tarefa de agente esperando a sua vez; cada transição é a regra que libera a próxima.
> A marca só avança quando o lugar anterior concluiu de verdade.

**Produção:** 18 s.

---

## Cena 14 · O sistema sai pronto

**Tela:** `telas/09-codigo-gerado.png`

**Narração:**
> A geração de código monta o sistema inteiro: o servidor dos agentes, a interface do
> hospital, o banco com o seu esquema, os cadastros e a ligação entre tudo. Cento e trinta
> e sete arquivos.

**Produção:** 12 s.

---

# BLOCO 3 — A aplicação funcionando

> Nota de produção: daqui em diante nada é maquete. É o sistema implantado, com banco de
> dados de verdade e dois casos clínicos plantados.

## Cena 15 · O menu do sistema

**Tela:** `telas/E0-app-menu.png`

**Narração:**
> Esta é a interface do hospital. Atendimento, engajamento, relatórios, integrações,
> cadastros. Repare na marcação: o losango indica a tela que chama um agente; o ponto, a
> tela convencional. A separação que começou no documento chegou até o menu lateral.

**Produção:** 18 s. Destaque dois itens lado a lado, um com losango e um sem.

---

## Cena 16 · O cadastro funcionando

**Tela:** `telas/E1-cadastro-pacientes.png`

**Narração:**
> Cadastro de pacientes, com os registros vindos do banco. Novo, Ver, Editar, Excluir.
> Isto não é tela de exemplo: a lista é uma consulta ao banco, e o que se grava aqui
> aparece nas outras telas.
>
> Rodamos o ciclo completo — listar, criar, ler, alterar e excluir — em três entidades, e
> conferimos cada passo contra a linha no banco, não contra a resposta da tela. Quinze
> casos, quinze aprovados.

**Produção:** 22 s. Destaque uma linha da tabela e os quatro botões.

---

## Cena 17 · Os registros que os agentes produziram

**Telas:** `telas/E2-cadastro-classificacoes.png`, `telas/E4-notificacoes.png`

**Narração:**
> E aqui estão os registros que o sistema produziu. As classificações, com o critério
> aplicado e a justificativa. As notificações enviadas à equipe — duas entregues, uma com
> falha registrada e o motivo. Nada disso foi digitado: é o resultado do trabalho dos
> agentes, gravado.

**Produção:** 20 s. Destaque a linha da notificação que falhou e a coluna de motivo.

---

## Cena 18 · A trilha de auditoria

**Tela:** `telas/E3-trilha-auditoria.png`

**Narração:**
> A trilha de auditoria encadeada. Cada entrada guarda a marca da entrada anterior — mexer
> no histórico quebra a corrente e fica detectável. Dez eventos do ciclo: o login, a
> importação da hemocultura, a tradução, a classificação, a avaliação de
> multirresistência, o alerta, a notificação, a recomendação e a exportação.

**Produção:** 20 s. Destaque a coluna da marca anterior.

---

# BLOCO 4 — Os agentes trabalhando

## Cena 19 · O agente traduz o resultado do laboratório

**Tela:** `telas/E5-agente-traducao.png`

**Narração:**
> Agora a parte de inteligência artificial. O operador escolhe o caso — e repare que a
> lista traz os casos que existem no banco, não exemplos — e aperta Traduzir.
>
> O agente vai ao banco, encontra o resultado bruto, traduz a nomenclatura do laboratório
> para o vocabulário do hospital e diz se o resultado é aproveitável. A resposta vem com a
> versão do prompt que a produziu, para que qualquer decisão possa ser rastreada depois.

**Produção:** 25 s. Destaque o seletor com o caso real e, na resposta, a versão do prompt.

---

## Cena 20 · O agente classifica pelo critério da norma

**Tela:** `telas/E6-agente-classificacao.png`

**Narração:**
> A classificação pelo critério do NHSN. O agente aplica o critério vigente à data do caso
> — não o critério de hoje — e devolve confirmada, descartada ou pendente, com a
> justificativa e o critério citado pelo nome e pela versão.

**Produção:** 22 s. Destaque o critério aplicado e o resultado.

---

## Cena 21 · O agente se recusa a inventar

**Tela:** `telas/E7-agente-alerta.png`

**Narração:**
> E esta é a cena que mais importa. Pedimos ao agente que redija o alerta de
> multirresistência para um caso que não é multirresistente. Ele olhou o antibiograma,
> contou as classes, e respondeu:
>
> "Caso sem multirresistência registrada — apenas uma classe resistente, fluoroquinolona,
> abaixo do limiar de três classes distintas. Não é possível redigir alerta afirmativo sem
> inventar dado clínico."
>
> Ele contou, aplicou a regra e recusou, citando a regra de negócio pelo número. Um sistema
> que inventa é pior do que um sistema que não responde.

**Produção:** 30 s. Destaque o motivo da insuficiência inteiro. Esta cena sustenta o vídeo.

---

# BLOCO 5 — A Bancada de Execução

> Nota: a Bancada é a segunda interface. A do hospital é para quem atende; a Bancada é
> nossa, para ver a orquestração por dentro.

## Cena 22 · A rede carregada

**Tela:** `telas/B0-bancada-inicio.png`

**Narração:**
> A Bancada de Execução. A rede de Petri aparece inteira e roda diante de nós. Não é
> animação: cada lugar abre uma conversa com o servidor dos agentes, manda a tarefa e
> espera a resposta. No painel, o projeto, o endereço do servidor que está no ar e as cinco
> tarefas desta rede.

**Produção:** 20 s. Destaque o painel com o endereço e a lista das cinco tarefas.

---

## Cena 23 · A marca andando

**Telas:** `telas/B1-marca-P1.png` … `telas/B5-marca-P5.png`

**Narração:**
> A marca sai do início e entra na primeira tarefa: traduzir o resultado do laboratório.
> Concluída, a transição libera a próxima: classificar o caso. Depois, avaliar
> multirresistência. Recomendar o pacote. Redigir o alerta. Cada passagem dessas é uma
> tarefa de verdade sendo executada contra o banco de verdade.

**Produção:** 24 s, cortando entre as capturas no ritmo da narração.

---

## Cena 24 · O log de disparos

**Tela:** `telas/41-bancada-log-disparos.png`

**Narração:**
> O simulador registra cada disparo: a hora, a transição, e as marcas que saíram de um
> lugar e entraram no outro. É a prova de que a rede executou na ordem que a planta manda.

**Produção:** 18 s. Destaque duas entradas seguidas do log.

---

## Cena 25 · Os painéis — entradas, execução e etiquetas

**Tela:** `telas/C3-painel-inputs.png`

**Narração:**
> E aqui está o que o agente recebeu e o que ele devolveu. O acompanhamento mostra a tarefa
> iniciada, o agente começando a trabalhar, o raciocínio, e a saída final.
>
> Embaixo, as etiquetas: nome da tarefa, nome do agente, a entrada que ele recebeu, a
> ferramenta que usou, os passos, a saída, o tipo da saída e a marca de tarefa concluída.
> São onze etiquetas, as mesmas para qualquer sistema que esta fábrica produza.

**Produção:** 28 s. Destaque a linha de etiquetas extraídas, uma a uma. Esta é a cena que
mostra o miolo do funcionamento.

---

## Cena 26 · Falha não passa calada

**Tela:** `telas/34-bancada-passo.png`

**Narração:**
> E quando uma tarefa falha, a rede para. A transição seguinte não dispara. Um sistema que
> segue em frente com dado ruim entrega um laudo errado com cara de laudo certo.

**Produção:** 16 s. Destaque o lugar em vermelho e a transição que não disparou.

---

# BLOCO 6 — O que se pode pedir ao sistema

## Cena 27 · Refinar um artefato conversando

**Tela:** `telas/62-casos-de-teste-etapa.png`

**Narração:**
> Cada etapa tem um chat com o agente que a produziu. Não é preciso editar arquivo: pede-se
> a correção em português e a etapa gera uma versão nova, preservando a anterior.

**Produção:** 20 s. Destaque o botão "Refinar com o agente" e mostre os comandos abaixo em
tela, um por vez.

**Comandos de exemplo, para mostrar na tela:**
- *"Separe o requisito FR-031 em dois: um para contar as classes e outro para decidir a multirresistência."*
- *"O caso de uso UC-011 não diz o que fazer quando o antibiograma vem vazio. Acrescente o fluxo de exceção."*
- *"Na tela de alerta, o campo de gravidade deve vir preenchido com 'alta' quando houver multirresistência."*
- *"Acrescente à tarefa de recomendação a restrição de nunca sugerir pacote de germe multirresistente sem multirresistência registrada."*
- *"Gere um caso de teste para a situação em que o laboratório está fora do ar."*

---

# Encerramento

**Tela:** `telas/08-rede-de-petri.png` (retomada)

**Narração:**
> Do documento do hospital até o sistema rodando, sem ninguém escrever código. O que mudou
> nesta versão não foi o modelo nem a ferramenta: foi ter declarado, desde o requisito, o
> que é trabalho de inteligência artificial e o que é trabalho de sempre. Cinco tarefas em
> vez de quarenta e cinco. E o que ainda falta está apontado, não escondido.

**Produção:** 18 s. Fecha na rede.

---

# Anexo de produção — o que está provado e o que não está

Medido em 28/09/2026 contra a aplicação implantada, com dois casos clínicos plantados no
banco. Registro completo em `registro_de_testes.md`.

**Provado, com tela e com gabarito — 22 de 23 casos:**

| | |
|---|---|
| Cadastro | 15 de 15: listar, criar, ler, alterar e excluir em pacientes, antimicrobianos e bundles, conferidos contra a linha no banco |
| Contagem de classes resistentes | 4 no caso multirresistente, 1 no outro — batendo com o gabarito |
| Tradução do laboratório | 6 antimicrobianos, todos com classe, microrganismo correto |
| Recusa de amostra inexistente | o agente declara não aproveitável e justifica, sem inventar |
| Classificação pela norma | responde com o critério citado por nome e versão |
| Recomendação de pacote | escolhe um pacote que existe no cadastro, com justificativa |
| Redação do alerta | texto clínico citando o achado |
| Rede de Petri | a marca percorre os cinco lugares e chega ao fim; falha bloqueia a transição |
| Painéis da Bancada | as 11 etiquetas universais, com entrada e saída de cada tarefa |
| Rastreabilidade | 22 requisitos ligados a caso de uso, tarefa e tela |

**Não provado — não narre como pronto:**

- **A regra das três classes não é aplicada pela tarefa de multirresistência**: a contagem
  sai certa e o campo do veredito volta vazio. É o único caso reprovado da bateria.
  (A tarefa do *alerta* aplica a regra corretamente — é ela que aparece na Cena 21.)
- Das 58 telas, 24 abrem sem dados porque são telas de ação: só mostram conteúdo depois que
  o operador executa.
- 4 telas ainda mostram "Ação não vinculada a uma tarefa do sistema" — são casos de uso
  convencionais sem executor próprio.
- 56 itens do documento de requisitos (não-funcionais e regras de negócio) ficaram sem
  classificação de natureza.
- A etapa de casos de teste apontou 36 casos contraditórios, onde falta na tabela a causa
  que dispara a exceção.
- Duas colunas do modelo de dados guardam fração como inteiro (`DECIMAL(10,0)`): o escore
  médio e a conformidade mensal do painel de vigilância.
