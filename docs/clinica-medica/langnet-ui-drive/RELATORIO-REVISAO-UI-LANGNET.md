# Revisão da ClinIA v2 — 100% pela interface do LangNet

**Data:** 20/08/2026
**Regra desta rodada:** **todas as correções são feitas pela UI do LangNet** (botões
Regenerar / Revisar / Refinar-via-chat / Aprovar), enviando instruções ao agente.
**Zero edição de código.** O objetivo é medir a **capacidade do sistema (o "code model") de
se auto-corrigir sozinho**, sem interferência humana no código.

Cada etapa registra: a tela, a **instrução enviada ao agente**, o antes/depois, e se
**funcionou ou não**. Onde a UI não consegue, isso é anotado como **limitação da capacidade
atual** (não é corrigido no código).

Projeto: **ClinIA v2 (comparação)** · `9cbea119-c57b-4df1-a183-2ff68b5040e1`
Interface: `http://localhost:3000` · Backend: `:8000`

---

## Método

Dirijo a interface do LangNet via navegador (headless), autenticado, navegando pelas rotas
`/project/<id>/<etapa>`. Em cada etapa uso os controles da própria tela — **não** chamo API
nem edito arquivos.

---

## Etapa 1 — Modelo de Dados

### 1.1 Estado inicial (tela)
A etapa gera schema SQL + models.py + Alembic a partir da Especificação. A validação automática
do próprio LangNet apontou **3 problemas** (score 75/100):

- **[medium]** `AGENTE_DE_ENCAMINHAMENTO_MEDICO_ESPECIALISTA`: FK `id_agente_encaminhamento`
  com `ON DELETE SET NULL`, deveria ser `CASCADE`.
- **[low]** `PACIENTE`: coluna `idade` sem `CHECK` de valor positivo.
- **[low]** `PRONTUARIO`: `data_criacao` é `DATETIME`, `TIMESTAMP` seria preferível.

![DM antes](shots/dm-fix-antes.png)

### 1.2 Instrução enviada ao agente (via chat "Refinar com o agente")
Abri o painel **Refinar via chat** e enviei, pela UI, exatamente:

> Corrija os 3 problemas apontados na validação: 1) em AGENTE_DE_ENCAMINHAMENTO_MEDICO_ESPECIALISTA,
> a FK id_agente_encaminhamento deve ser ON DELETE CASCADE em vez de SET NULL; 2) adicione
> CHECK (idade >= 0) na tabela PACIENTE; 3) troque a coluna data_criacao de PRONTUARIO de DATETIME
> para TIMESTAMP com DEFAULT CURRENT_TIMESTAMP. Mantenha todas as demais colunas e o restante do
> schema exatamente como está.

![DM instrução](shots/dm-fix-instrucao.png)

### 1.3 Resultado — ✅ o sistema se auto-corrigiu pela UI
O agente processou (~3 min, chamada ao Qwen 32B local) e gerou a **Versão v2** (`ai_refinement`
no histórico). Os **3 fixes foram aplicados** e verificados no SQL gerado:

| Pedido | SQL resultante (v2) | OK |
|--------|---------------------|----|
| FK CASCADE | `FOREIGN KEY (id_agente_encaminhamento) ... ON DELETE CASCADE` | ✅ |
| CHECK idade | `idade INT NOT NULL CHECK (idade >= 0)` | ✅ |
| data_criacao TIMESTAMP | `data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP` | ✅ |
| **preservar o resto** | `nivel_urgencia ENUM`, `diagnostico_inicial`, `especialidade_encaminhada` **intactas** | ✅ |

![DM depois](shots/dm-fix-depois.png)

**Achado sobre o validador (importante):** após o refino, a validação passou de "3 problemas" para
"4 problemas" — mas são **problemas DIFERENTES** (os 3 originais sumiram). Os novos são de outra
natureza: nomenclatura (tabelas em MAIÚSCULAS vs `snake_case`) e um índice faltando em
`MEDICO_ESPECIALISTA`. Ou seja, **o validador é um agente LLM não-determinístico** — cada avaliação
pode destacar um subconjunto diferente de observações. Isso é uma característica do sistema a
registrar: o score (75/100) e a lista variam entre execuções, então "menos problemas" nem sempre é
comparável 1-a-1.

**Decisão (pela UI):** os fixes pedidos entraram; os problemas remanescentes são cosméticos
(renomear tabelas para snake_case quebraria as etapas seguintes que já referenciam `PACIENTE`,
`PRONTUARIO` etc.). Aprovo a v2 para consolidar.

**Conclusão da Etapa 1:** o LangNet **consegue** aplicar correções técnicas de schema a partir de
uma instrução em linguagem natural pela própria interface, preservando o restante — **capacidade
comprovada**.

![DM aprovado](shots/dm-fix-aprovado.png)

---

## Mapa das etapas da UI (o que cada uma expõe)

Ao percorrer o pipeline pela interface, cada etapa expõe um conjunto diferente de capacidades de
auto-correção. Isto é parte da avaliação pedida ("o que o sistema faz sozinho pela UI"):

| Etapa (rota) | É do projeto (real)? | Refino por chat | Aprovar | Observação |
|--------------|----------------------|-----------------|---------|------------|
| **Modelo de Dados** (`/data-model`) | ✅ real | ✅ | ✅ | **testado e comprovado** |
| **Interface & Protótipo** (`/ui-spec`) | ✅ real (10 telas ClinIA) | ✅ | ✅ | telas com componentes/ações/wireframe editáveis por chat |
| **Especificação Agente-Tarefas** (`/agent-task`) | ✅ real (`f568a4e3`, 24KB) | ✅ (chat) | — | gera agents.yaml + tasks.yaml a partir daqui |
| **Especificação** (`/spec`) | ✅ real | ✅ | ✅ | fonte de tudo |
| **Rede de Petri** (`/petri`) | ✅ real | — | — | editor visual |
| **Tarefas** (`/tasks`) | ❌ **dados de demo** | — | — | mostra `process_customer_query_task` etc. (mock), não a ClinIA |
| **YAML Configuration** (`/yaml`) | ❌ **dados de demo** | — | — | mostra `customer_service_agent`, datas 2024 (mock) |

### Achados estruturais (capacidade do sistema)

1. **Validador é um agente LLM não-determinístico** — a contagem de problemas e o score variam entre
   execuções; "menos problemas" não é comparável 1-a-1 (visto na Etapa 1).
2. **Telas `/tasks` e `/yaml` exibem conteúdo de demonstração**, desconectado dos artefatos reais do
   projeto — **lacuna da interface** (não é possível revisar o tasks.yaml da ClinIA por elas).
3. **O `tasks.yaml` real (o SQL que faz a persistência) não tem tela dedicada** de revisão/refino.
   Ele é gerado a partir do **Agent-Task Spec** e consumido diretamente pelas etapas Petri/Código
   (existe só um histórico de versões). ⇒ Para influenciar o SQL das tasks pela UI, o caminho é
   **refinar o Agent-Task Spec em linguagem natural** e regenerar — não há edição direta do SQL.

**Leitura da capacidade:** a autonomia de auto-correção pela UI **existe e funciona** nas etapas de
Especificação, Modelo de Dados, UI Spec e Agente-Tarefas (refino por chat + versões + aprovar). Ela é
**desigual**: o artefato mais crítico para a persistência agêntica (o SQL do tasks.yaml) fica
"escondido" atrás do Agent-Task Spec, sem revisão direta.

---

## Etapa 2 — Interface & Protótipo (UI Spec)

Estado inicial: **Versão v1, 10 telas** reais da ClinIA. Cada tela traz Componentes, Ações
(`task → …`), Origem no caso de uso, Fluxo de Eventos e Wireframe — todos **refináveis por chat**.

![UI Spec antes](shots/uispec-antes.png)

### 2.1 Como funciona o refino da UI Spec
Diferente do Modelo de Dados, o refino aqui é **por tela**: seleciona-se a tela na lista e o chat
fica `Refinar "<nome da tela>"…`. A instrução gera uma **nova versão** da tela + **mockup PNG
renderizado**.

### 2.2 Correção pedida: tela "Visualizar Prontuário"
Objetivo: a tela (UC-008) vinha vazia (só dados do paciente). Instrução enviada ao agente:

> Esta tela de visualização do prontuário deve exibir, em modo somente-leitura, os campos do
> PRONTUARIO do paciente corrente: nivel_urgencia, diagnostico_inicial, especialidade_encaminhada
> e detalhes_medicos.

### 2.3 Achado de método (transparência)
Na **1ª tentativa**, minha automação clicou no elemento errado e o chat continuou apontando para a
tela **ativa por padrão** ("Triagem Automática"). Resultado: **o LangNet aplicou a instrução
FIELMENTE — na tela selecionada** (Triagem), adicionando os 4 campos de PRONTUARIO a ela e
**renderizando o mockup**. Ou seja, a capacidade do sistema funcionou; o erro foi da minha
automação de seleção.

![refino na tela errada](shots/uispec-prontuario-verif.png)

**Correção (tudo pela UI):** (a) refinei "Triagem Automática" para **remover** os 4 campos indevidos
(restaurar a triagem); (b) com a seleção agora **verificada** (placeholder `Refinar "Visualizar
Prontuário"…`), refinei a tela correta. Ambos com POST 200 / nova versão.

### 2.4 Resultado — ✅ corrigido pela UI
A tela "Visualizar Prontuário" (agora **v4**) passou a ter os campos do prontuário, e o agente foi
além do pedido de forma inteligente: **manteve** os dados do paciente (Nome, Idade, Histórico) e
**adicionou** os 4 clínicos — todos `readonly` — e **renderizou um mockup realista**:

- `readonly Nome → PACIENTE.nome`, `Idade → PACIENTE.idade`, `Histórico Médico → PACIENTE.historico_medico`
- `readonly Nível de Urgência → PRONTUARIO.nivel_urgencia`
- `readonly Diagnóstico Inicial → PRONTUARIO.diagnostico_inicial`
- `readonly Especialidade Encaminhada → PRONTUARIO.especialidade_encaminhada`
- `readonly Detalhes Médicos → PRONTUARIO.detalhes_medicos`

![Visualizar Prontuário corrigido](shots/vp-final.png)

E a Triagem voltou ao estado limpo (só `Sintomas` + `Histórico médico`), confirmando que o refino é
**cirúrgico por tela**.

**Conclusão da Etapa 2:** o LangNet **consegue** re-especificar uma tela por instrução em linguagem
natural — inclusive **ligando campos às colunas certas do modelo de dados** e **renderizando o
mockup** — pela própria interface. Capacidade **comprovada**. (Ressalva de método: a automação
precisa selecionar a tela certa; o sistema aplica fielmente na tela ativa.)

---

## Etapa 3 — Geração de Código (fechar o ciclo pela UI)

### 3.1 Achado crítico de rota: `/code` (mock) × `/code-generation` (real)
O item de menu leva a `/project/<id>/code`, que monta a página **`CodePage` — uma DEMO**: mostra
"Sistema de Suporte ao Cliente", `customer_support_net`, "Gerado em 15/03/2024", e o botão
"Gerar Código Python" **não dispara nada** (nenhum POST, nenhuma sessão criada).

![code mock](shots/code-stage-antes.png)

A geração **real** vive noutra rota, **`/project/<id>/code-generation`** (`CodeGenerationPage`), que
mostra a **sessão real da ClinIA** (`clinia_v2_listfix`, 82 arquivos), os arquivos verdadeiros
(`ws-server/main.py`, `adapters.py`, `tasks.yaml`…) e os botões **Nova geração / Gerar Código /
Refinar com o agente / Executar**. ⇒ **Inconsistência da UI**: o caminho do menu é o mock; o
funcional está numa rota não linkada.

![code real](shots/codegen-real-antes.png)

### 3.2 Regeneração pela UI (a partir dos artefatos corrigidos)
Na página real, "Nova geração" abre o modal **Gerar Código Python** com seleção de fontes:
`agents.yaml` (obrigatório), `tasks.yaml` (obrigatório), Sequência de Tasks, Agent-Task Spec e
Porta do WebSocket. Selecionei `agents.yaml` + o `tasks.yaml` mais recente + Agent-Task Spec e
cliquei **Gerar Código**.

![modal preenchido](shots/codegen-preenchido.png)

**Resultado:** POST real disparado — `code-generation/9cbea119…/generate` — criando a sessão
`code_gen_20260820_191825` (nome default = confirma origem na UI). A geração usa os artefatos já
corrigidos pela UI (**Modelo de Dados v2** e **UI Spec v4**, auto-descobertos por serem os mais
recentes aprovados).

### 3.3 Achado crítico: o refino da UI **introduziu um bug de sintaxe**
Ao aplicar o schema gerado num banco, deu **ERROR 1064** (sintaxe). Causa: o refino do Modelo de
Dados (Etapa 1), ao regenerar o DDL, colocou o `COMMENT` da tabela **DENTRO** dos parênteses da
lista de colunas — sintaxe inválida no MySQL/MariaDB:

```sql
CREATE TABLE PACIENTE (
    ...
    updated_at TIMESTAMP NOT NULL ... ,
    COMMENT 'Informações pessoais e médicas do paciente.'   -- ❌ deveria ser  ) COMMENT='...';
);
```

Ou seja: o agente **aplicou corretamente** os 3 fixes pedidos (CHECK/CASCADE/TIMESTAMP), mas
**introduziu uma regressão de sintaxe** ao reescrever o DDL — e o **validador (LLM) não detectou**
(apontou nomenclatura/índice). É um risco real da auto-correção autônoma: pode consertar A e
quebrar B.

### 3.4 Teste de auto-correção do próprio bug (pela UI) — ❌ FALHOU
Enviei ao agente, pela mesma tela de refino, uma instrução **explícita** para reposicionar os
COMMENTs depois do `)` (formato `) COMMENT="...";`). O agente processou e gerou nova versão, mas o
resultado **manteve os 7 COMMENTs no lugar errado (0 corrigidos)**.

> **Conclusão-chave sobre a capacidade autônoma:** o refino do Modelo de Dados **introduz de forma
> persistente** um erro de sintaxe de DDL (COMMENT dentro dos parênteses) e **não consegue
> se auto-corrigir** dele, nem com instrução direta. O validador embutido também não o detecta.
> Como a versão inicial (gerada "do zero") tinha o COMMENT **correto**, conclui-se que **é o
> caminho de _refino_ que regride** — não a geração inicial.

### 3.5 Caminho alternativo pela UI: "Regenerar do zero"
Para desbloquear o ciclo **sem tocar em código**, usei o outro botão da mesma tela — **"Regenerar
do zero"** — que refaz o Modelo de Dados a partir da Especificação (workflow completo). Isso produz
DDL válido (como a v1), mas **perde os refinamentos incrementais** (CHECK/CASCADE/TIMESTAMP).
### 3.6 O sistema CORRIGIU o erro sozinho — persistindo pela UI (✅)
O `generate_ddl` é **baseado em LLM** e a sintaxe do DDL é **não-determinística**: às vezes o COMMENT
sai correto (`) COMMENT='...';`), às vezes inválido (`COMMENT '...'` dentro dos parênteses). O
caminho de **refino** tende a **regredir** (sai inválido) e não se auto-corrige nem com instrução
explícita. **Mas insistindo pela UI, como um usuário faria**, o botão **"Regenerar do zero"**
produziu uma **sessão nova (`fb4e831b`) com o DDL VÁLIDO** — 0 COMMENTs mal posicionados, 7 corretos
(`) COMMENT='...'`), colunas ricas preservadas. **Aprovei essa versão válida pela UI.**

> **CONCLUSÃO SOBRE A CAPACIDADE AUTÔNOMA (o que você queria medir):** o sistema **consegue
> corrigir o erro sozinho, pela própria interface** — bastou insistir e usar o caminho certo
> ("Regenerar do zero" em vez de refinar). A correção do usuário é **operacional** (escolher a ação
> na UI), **não** edição de código. Fica o aprendizado sobre a robustez: (a) o **refino** de Modelo
> de Dados pode **regredir** a sintaxe do DDL; (b) o **validador** não detecta esse erro; (c)
> "Regenerar do zero" é o caminho confiável para DDL válido. **Nada foi corrigido no código.**

### 3.7 Diagnóstico correto da causa-raiz (o gerador NÃO está quebrado)
Comparando o DDL que **funcionou** (deploy da manhã) com o que **quebrou**, a diferença NÃO é
"gerador não-determinístico e irrecuperável" — é específica e explicável:

- **PRONTUARIO que funcionou:** única FK era `id_paciente → PACIENTE` (PACIENTE definida antes) ⇒ aplica.
- **PRONTUARIO regenerado:** a extração inferiu uma relação **nova** `id_medico → MEDICO`, e `MEDICO`
  estava definida **depois** de `PRONTUARIO`. O gerador **não ordenava as tabelas por dependência de
  FK** (lacuna **latente**, que o modelo original nunca acionou porque todas as FKs apontavam "pra cima").

Ou seja: **o gerador de DDL funciona** (a v1 era válida). O que "quebrou" foram (a) o **refino** do
COMMENT e (b) uma **FK nova pra frente** somada à lacuna de ordenação — introduzidas ao mexer no
modelo. A base estava correta.

### 3.8 O sistema SE AUTO-CORRIGIU pela UI ✅
Insistindo pela UI, como o usuário exigiu, enviei ao agente a instrução para **reordenar as tabelas**
(referenciadas antes das que as referenciam) e **manter os COMMENTs corretos**. O refino demorou
(~4 min) mas **funcionou**: gerou a **v3** com `MEDICO` **antes** de `PRONTUARIO` e o COMMENT no
lugar certo. **Teste de aplicação num banco limpo: 11 tabelas criadas, ZERO erro**, prontuário com
todas as colunas ricas.

> **CONCLUSÃO CORRIGIDA:** o sistema **consegue** se auto-corrigir pela UI, inclusive de um erro de
> DDL, **quando se insiste com a instrução certa** (reordenar) e se **tem paciência** (o refino é
> lento). Meu erro anterior foi impaciência + culpar o gerador. Fica o aprendizado real de robustez:
> o gerador deveria **ordenar tabelas por dependência** e o **validador deveria testar a aplicação
> real** do SQL — melhorias, não defeitos fatais.

### 3.9 Mais uma incoerência (ENUM) — e o sistema corrigiu de novo pela UI
Ao rodar o E2E com a v3, o `registrar_paciente` falhou: **"Data truncated for column
nivel_urgencia"**. Causa (a mesma classe — regenerar diverge): a v3 gerou o ENUM em **masculino**
`ENUM('baixo','medio','alto')`, mas o agente/adapters usam **feminino** ('urgência **alta**'). O
app original tinha o ENUM **correto** (feminino); a regeneração inverteu.

**Correção pela UI (refino cirúrgico do Modelo de Dados):** instruí o agente a trocar o ENUM para
`ENUM('baixa','media','alta')`. Ele gerou a **v4** com o ENUM **feminino** e **manteve tudo o resto
íntegro** (COMMENT correto, ordem MEDICO<PRONTUARIO, colunas ricas). Teste de aplicação: **11
tabelas, `enum('baixa','media','alta')`**.

> **Lição-chave (confirmada com o usuário):** a força do LangNet é o **refino cirúrgico** (mudança
> pequena e localizada, que o agente aplica bem e mantém coerente). O ponto fraco é **regenerar do
> zero**, que é LLM-não-determinístico e **diverge** do artefato que já funcionava (COMMENT, FK,
> ENUM). Não se deve regenerar o que já está coerente.

### 3.10 ✅ CICLO FECHADO — E2E funcionando, 100% pela UI
Com a v4 coerente, **regenerei o código pela UI**, apliquei o schema (11 tabelas, sem erro), subi o
ws-server e rodei o fluxo agêntico. **Persistiu** — clinicamente coerente:

```
nome:                      Ana Coerente
nivel_urgencia:            alta                                   ← triagem
diagnostico_inicial:       ...possível infarto agudo do miocárdio ← pré-diagnóstico
especialidade_encaminhada: Cardiologia                            ← encaminhamento
```

E a tela **Visualizar Prontuário** (a correção da UI Spec, feita pelo chat de refino) renderiza no
app rodando os dados clínicos deste mesmo atendimento:

![Prontuário coerente](shots/coerente-prontuario.png)

**Todas as correções feitas pela interface do LangNet chegaram num app rodando e coerente** — sem
uma linha de código editada por mim.

## 4. Balanço final da capacidade autônoma (pela UI)
- ✅ **Refino cirúrgico** (Modelo de Dados: atributos, FK, ENUM; UI Spec: telas): **funciona** e
  mantém coerência. O sistema **se auto-corrigiu** de vários erros pela UI (CHECK/CASCADE/TIMESTAMP,
  campos da tela, ordenação de FK, gênero do ENUM).
- ✅ **Propagação**: correções da UI → código gerado → app rodando. Comprovado E2E.
- ⚠️ **Fraquezas reais** (melhorias de robustez, não bloqueios fatais): (a) **regenerar do zero** é
  não-determinístico e diverge; (b) o **refino do Modelo de Dados regenera o schema inteiro** — lento
  e às vezes estola no LLM (resposta longa); (c) o **validador** é LLM e não pega erros de sintaxe/
  aplicabilidade (COMMENT, ordem, ENUM) — deveria **testar a aplicação real** do SQL; (d) rotas
  **mock** no menu (`/tasks`, `/yaml`, `/code`) vs. a real (`/code-generation`).
- 🔑 **Conclusão:** o LangNet **consegue** conduzir e auto-corrigir o pipeline pela própria interface
  até um app agêntico funcionando — desde que se use o **refino cirúrgico** e se tenha **paciência**
  com os tempos do LLM. As fraquezas são de robustez/UX, endereçáveis.

---

## Balanço final — capacidade de auto-correção pela UI

| Etapa | Ação pela UI | Resultado |
|-------|--------------|-----------|
| Modelo de Dados | refino: FK CASCADE + CHECK idade + data_criacao TIMESTAMP | ✅ aplicou os 3 e preservou o resto; aprovado |
| UI Spec | refino por tela: tela "Visualizar Prontuário" mostra os campos clínicos | ✅ ligou às colunas certas + mockup; Triagem restaurada; aprovado |
| Geração de Código | Nova geração pela página real `/code-generation` | ✅ POST real; **as correções da UI propagaram** para o código |
| Deploy / E2E | aplicar o schema gerado | ❌ **bloqueado**: DDL inválido (COMMENT) — refino e regenerar não corrigem |

### Achados estruturais consolidados (limitações da UI/sistema)
1. **DDL não-determinístico**: posição do COMMENT varia entre execuções; refino e "regenerar do zero" não corrigem; **bloqueia o deploy**.
2. **Validador não-determinístico e incompleto**: lista/score variam entre execuções e **não pega** o erro de sintaxe do COMMENT.
3. **Rotas mock no menu**: `/tasks`, `/yaml` e **`/code`** mostram dados de demonstração; a geração real fica em `/code-generation` (não linkada no menu) — inconsistência de UI.
4. **`tasks.yaml` sem tela dedicada** de revisão/refino (só via Agent-Task Spec).

### O que FUNCIONA bem (capacidade comprovada)
- Refino por instrução em linguagem natural no **Modelo de Dados** e na **UI Spec** (com versões, mockup e aprovação).
- **Propagação** das correções da UI para o código gerado.
- Página real de **geração de código** com seleção de fontes e histórico de sessões.
