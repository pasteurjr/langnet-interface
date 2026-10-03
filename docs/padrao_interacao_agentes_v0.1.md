# Padrão de interação com agentes no aplicativo gerado — rascunho v0.1

**Data:** 03/10/2026 · **Para:** o agente de Geração de Código do LangNet · **Status:** para revisão do autor

## 1. O desenho

| Onde | O que é | Para quem |
|---|---|---|
| **LangNet (fábrica)** | a interface do visualtasksexec com as abas (rede de Petri, execução, verboses) | quem constrói: testa a orquestração dos agentes |
| **Aplicativo gerado (máquina)** | os **mesmos** agentes, a **mesma** rede de Petri e o **mesmo** framework (`frameworkagentsadapter`), com uma interface amigável | quem usa: médico, enfermeiro, administrador |

No aplicativo gerado, o usuário **nunca** vê lugar, transição, token, verbose nem JSON. Ele vê a pergunta,
o que o sistema está fazendo em linguagem dele, a resposta e o porquê.

## 2. Três tipos de execução, declarados no caso de uso

Cada linha "Resposta do Sistema" do fluxo principal e dos fluxos de exceção traz **Executado por**:

| Valor | O que é | Quem escreve | Roda IA? |
|---|---|---|---|
| `pronto` | login, cadastro, relatório, auditoria | molde determinístico do gerador | não |
| `código gerado` | regra própria do caso de uso que um programa comum resolve | o LLM, uma vez, na Geração de Código | não |
| `agente` | interpretar, classificar, decidir, redigir | a tarefa no framework (CrewAI), definida em Agentes e Tarefas | sim, a cada execução |

Teste para separar `código gerado` de `agente`: *um programa comum, lendo o banco e seguindo uma regra
escrita, resolveria?* Sim → `código gerado`.

## 3. Os dois modos de interação com agente

### Modo A — agente embutido na tela de negócio
A tela do caso de uso continua sendo a tela do caso de uso (campos, tabelas, indicadores). O passo `agente`
aparece **dentro** dela, como um bloco. É o modo padrão quando o caso de uso é uma tela de trabalho
(ex.: UC-011, multirresistência; UC-013, redigir o alerta).

### Modo B — conversa (chat)
Um painel de conversa conduz uma **sequência** de passos de agente e de programa, tirada da rede de Petri:
pergunta ao usuário só o que falta, executa, mostra o resultado de cada etapa e segue. É o modo para fluxos
que atravessam vários casos de uso (ex.: "analisar o caso CAS-2023-001": tradução → classificação →
multirresistência → recomendação → alerta).

**Regra de escolha** (declarada na etapa de Interface, por tela): o caso de uso com um passo `agente` dentro
de uma tela de trabalho → **Modo A**. A sequência da rede que começa num gatilho do usuário e passa por mais
de um caso de uso → **Modo B**. O mesmo agente pode aparecer nos dois modos; a tarefa é uma só.

## 4. A ficha de interação — o que o gerador recebe por passo `agente`

Montada pelo programa a partir das etapas anteriores (não é inventada pelo modelo):

```yaml
acao: "Identificar multirresistência"          # rótulo do botão (Interface)
caso_de_uso: UC-011                            # Especificação
tarefa: evaluate_multidrug_resistance          # Agentes e Tarefas
modo: embutido                                 # embutido | conversa (Interface)
entradas:                                      # cada entrada diz DE ONDE vem
  - campo: caso_id
    origem: contexto        # contexto (caso/atendimento corrente) | tela (campo X) | perguntar | programa
    pergunta: "Qual caso clínico você quer avaliar?"   # usada se o contexto estiver vazio
    escolher_de: casos_clinicos                         # lista para escolher (nunca digitar id)
  - campo: antibiograma_traduzido
    origem: programa        # o programa busca no banco / no passo anterior; o usuário não vê
saidas:                                        # como cada campo de saída aparece
  - campo: multirresistente      ; mostrar: decisao        # selo grande: Sim / Não / Pendente
  - campo: classes_resistentes   ; mostrar: lista
  - campo: contagem_classes_resistentes ; mostrar: indicador
  - campo: justificativa         ; mostrar: texto          # sempre visível, nunca escondida
grava: { tabela: decisoes_sistema, mostrar_registro: true }
humano_no_meio: confirmar         # nenhum | confirmar | revisar_e_editar
recusas:                                       # do fluxo de exceção do caso de uso
  - quando: "antibiograma sem classe"
    mensagem: "Classe ausente em um ou mais antimicrobianos."
  - quando: "caso não informado"
    mensagem: "Escolha um caso clínico para avaliar."
depois: [ "Redigir alerta (UC-013)" ]          # próxima ação sugerida, tirada da rede
```

## 5. Os componentes de interface (sempre os mesmos, em todo aplicativo)

| Componente | Para quê | Regras |
|---|---|---|
| **Seletor de contexto** | escolher o caso/atendimento quando falta | lista com rótulo legível (paciente, data, situação); nunca campo de id |
| **Botão de ação do agente** | disparar o passo | rótulo igual ao do caso de uso; desabilitado só com o motivo escrito ao lado |
| **Andamento** | mostrar o que está acontecendo | frases do usuário ("lendo o antibiograma…", "contando classes resistentes…"), tiradas dos passos da tarefa; sem verbose técnico |
| **Cartão de decisão** | mostrar o resultado | o veredito em destaque, os números, a justificativa sempre visível, a versão do critério, link "ver registro" |
| **Pergunta** | pedir uma entrada que falta | a pergunta da ficha, com o tipo certo de campo (lista, data, número) |
| **Confirmação** | humano no meio | Aceitar · Refazer com observação · Cancelar — a observação vai para o agente na nova tentativa |
| **Recusa** | o agente não pôde decidir | a mensagem do caso de uso + o que falta para poder decidir; nunca "sucesso" |
| **Erro** | falha técnica | mensagem clara + "tentar novamente"; o erro real vai para o registro, nunca some |
| **Próximo passo** | continuar o fluxo | botão para a ação seguinte da rede, levando o contexto |

No **Modo B**, as mesmas peças viram mensagens da conversa: a pergunta é uma mensagem do sistema, o cartão de
decisão é uma mensagem com o cartão, a confirmação são botões na mensagem.

## 6. Estados de toda interação (os dois modos)

`aguardando entrada` → `executando` → `concluído` | `recusado` | `erro` → (`confirmado` | `refazer`)

Toda tela e todo chat tratam **os cinco**. Resposta com `status: erro` ou recusa **nunca** aparece como sucesso.

## 7. De onde vem cada pedaço (as etapas do pipeline)

| Pedaço da ficha | Etapa |
|---|---|
| `Executado por` de cada passo, mensagens de recusa | Especificação |
| tela, rótulo da ação, `modo`, componentes | Interface & Protótipo |
| tarefa, entradas e saídas com tipo | Agentes & Tarefas |
| `origem` das entradas, `depois` | Sequência e Rede de Petri |
| `grava` | Modelo de Dados |

## 8. Regras para o agente de Geração de Código

1. Para cada passo `agente`, ler a ficha e gerar **só** com os componentes da seção 5.
2. Toda entrada tem origem; `contexto` vazio vira **Pergunta**, nunca valor vazio enviado ao agente.
3. Toda saída declarada aparece; a justificativa nunca fica escondida.
4. As mensagens de recusa são as do caso de uso, literais.
5. O agente roda no framework, pela mesma tarefa que a fábrica testou; nada de reimplementar a tarefa na tela.
6. Para cada passo `código gerado`, escrever a resposta como código comum, com as mensagens do caso de uso.
7. Para cada passo `pronto`, usar o molde.

**Portão (programa, não modelo):** toda ação de toda tela tem quem a execute; toda entrada tem origem;
toda mensagem de exceção aparece no código; nenhuma resposta de erro é tratada como sucesso.

## 9. Exemplo — BioByte

- **Modo A, UC-011:** abre a tela → sem caso no contexto, aparece "Qual caso clínico você quer avaliar?"
  com a lista de casos → "Identificar multirresistência" → andamento "lendo o antibiograma… contando
  classes resistentes…" → cartão: **Multirresistente: Sim · 4 classes** (cefalosporina, betalactâmico,
  fluoroquinolona, aminoglicosídeo), justificativa visível, "ver registro" → botão "Redigir alerta".
- **Modo B, "analisar um caso":** "Qual caso?" → tradução (cartão) → classificação (cartão: *Pendente —
  faltam os critérios NHSN vigentes e a data de início do caso*) → a conversa diz o que falta e oferece
  continuar só com a multirresistência → alerta redigido → "Enviar à equipe?" (confirmação).

## 10. Decisões que preciso de você

1. O Modo B (chat) é **um painel por fluxo** (ex.: "Analisar caso") ou **um assistente único** do aplicativo que sabe acionar todos os fluxos?
2. `humano_no_meio`: qual é o padrão — confirmar sempre decisão clínica, ou só antes de gravar/enviar?
3. O andamento pode mostrar o **pensamento** do agente resumido, ou só os passos?
4. Qual versão do framework o aplicativo gerado usa: `frameworkagentsadapter` (TropicalSales) ou v4/v5?
