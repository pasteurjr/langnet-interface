# Tradutor de regras — o contrato de passos da tarefa

## O problema, em uma frase

A descrição de cada tarefa mistura passos de **banco** ("grave o alerta") com passos de **regra**
("confira a senha", "conte as resistências", "só alerte se for multirresistente"). O gerador
traduz o primeiro tipo e, para o segundo, tenta reconhecer frases soltas. O que não reconhece
some. Ensinei três frases à mão; sobraram 23 passos, e cada projeto novo trará frases novas.

## A decisão

**Parar de ler prosa. Passar a ler um contrato.** Cada tarefa ganha, no `tasks.yaml`, uma
lista `steps:` em que cada passo tem um TIPO de um conjunto fechado. A prosa continua para o
humano e para o agente; o gerador de código traduz só a lista. Todo passo declarado termina, sem
exceção, em um de dois estados: **emitido** ou **não emitido com o motivo**. Nada some.

## Os tipos de passo

| tipo | o que declara | como vira código |
|---|---|---|
| `consulta` | comando de leitura, parâmetros, onde guardar, forma (escalar, linha, linhas) | SELECT + captura |
| `escrita` | comando de escrita e parâmetros | INSERT / UPDATE / DELETE |
| `verificacao` | uma condição e a mensagem de recusa | `if not condição: desfaz e recusa com a mensagem do caso de uso` |
| `calculo` | uma variável e uma expressão | `variável = expressão` |
| `condicao` | uma condição e os passos que ela governa | `if condição:` com os passos dentro |
| `laco` | uma lista e os passos por item | `for item in lista:` |
| `externo` | ferramenta (resolvida na etapa Ferramentas), argumentos, onde guardar, mapa de saída | chamada da ferramenta + captura mapeada |
| `retorno` | campos do resultado | monta o resultado |
| `agente` | instrução em linguagem natural | só vale em tarefa `execution: agent`; em determinística é falha |

## A mini-linguagem das condições e cálculos

Pequena, fechada e sem execução de texto livre: valores, nomes (entradas e variáveis
capturadas), acesso a campo, `+ - * /`, comparações, `e / ou / nao`, e um punhado de funções
com nome em português: `conta_valor(json, 'R')`, `tamanho(x)`, `confere_senha(senha, hash)`,
`existe(x)`, `entre(x, a, b)`, `em(x, lista)`, `arredonda(x, n)`, `hoje()`, `dias_entre(a, b)`.
O que não cabe aqui não é regra de código: é ferramenta determinística declarada na etapa
Ferramentas, ou é decisão de agente.

Um nome que não existe em tempo de execução dá erro claro ("variável X não definida no passo 3"),
não NameError.

## O manifesto

Para cada tarefa, o gerador grava: passos declarados, passos emitidos, passos não emitidos e o
motivo de cada um (tipo inválido, expressão que não compila, ferramenta pendente, passo de
agente em tarefa determinística). O portão de lógica deixa de adivinhar por expressão regular e
passa a ler o manifesto. A implantação já recusa geração reprovada; agora reprova pelo motivo
certo.

## De onde vêm os passos

- Projetos novos: o gerador do `tasks.yaml` passa a produzir `steps:` junto com a descrição.
- Projetos existentes (BioByte): a etapa de YAML ganha a ação **Estruturar passos**: o agente
  converte a prosa em `steps:`, a etapa valida contra o esquema e compila cada expressão ANTES de
  gravar, o que não passou volta marcado para o usuário refinar, e depois aprova. Mesmo padrão
  das outras etapas.

## Fases

A. Esquema, validador, mini-linguagem e emissor — testáveis fora do pipeline.
B. Gerador consome `steps:`; manifesto; portão de lógica lê o manifesto.
C. Ação "Estruturar passos" na etapa de YAML, com validação antes de gravar.
D. BioByte: estruturar → gerar → implantar → bateria. Provar: login confere código de
   verificação; importação recusa paciente inexistente; escore devolve a mensagem do caso de uso
   em vez de erro de banco.
