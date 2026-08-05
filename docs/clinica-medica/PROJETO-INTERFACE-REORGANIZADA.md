# Projeto da Interface Reorganizada — ClinIA

> Este documento define **como a interface da ClinIA deve ficar** e **como o paciente é cadastrado no
> momento da triagem**. É a base das instruções que serão passadas AO LANGNET (refino da
> Especificação) — não uma edição manual do artefato. Objetivo: acabar com a confusão (cadastros
> misturados com telas agênticas) e deixar o fluxo de atendimento claro.

## 1. Diagnóstico do problema atual (o que está confuso)

- O menu mistura, sem separação clara, telas **de cadastro** (Gestão de Pacientes/Médicos/…) com telas
  **agênticas** (Triagem, Pré-atendimento…). Tudo cai num bloco "CADASTROS".
- **Não existe** uma etapa que **cadastre o paciente e abra o atendimento** no momento da triagem —
  por isso `criar_encaminhamento` falha com `atendimento_id null` e `registrar_prontuario` com
  `paciente_id null` (as FKs nunca são criadas).
- A triagem devolve `area_destino` em **texto livre** ("Cardiologia", "Emergência", "Pediatra
  Infectologista"), o que impede o roteamento automático para o agente especialista certo.
- Há **uma única** tela "Pré-atendimento por Especialista" fixa em cardiologia — não roteia dinâmico.

## 2. Interface-alvo: DOIS módulos claros

### MÓDULO A — ATENDIMENTO (fluxo agêntico, no TOPO do menu, na ordem do fluxo)
O caminho que o paciente percorre. Cada tela é uma etapa do atendimento:

1. **Recepção & Triagem** — *a porta de entrada.* Um **atendente** (ou o próprio paciente) informa:
   - **Identificação**: Nome, CPF, Data de Nascimento, Contato, Convênio.
   - **Queixa** (texto livre) + **Sinais Vitais** (PA, FC, temperatura, SpO₂).
   - Ao clicar **"Iniciar Triagem"**, o sistema executa (ver §3):
     (a) **identifica** o paciente pelo CPF; se **não existir, CADASTRA** automaticamente;
     (b) **abre um Atendimento** (registro da triagem) ligado ao paciente;
     (c) o **agente de triagem** classifica a **urgência** (verde/amarelo/vermelho) e escolhe a
         **especialidade de destino** (de uma **lista fechada** das especialidades cadastradas);
     (d) **roteia** para o pré-atendimento da especialidade.
   - Resultado exibido: classificação + justificativa + especialidade roteada + botão **"Encaminhar ao
     Especialista"**.

2. **Pré-atendimento do Especialista** — recebe o atendimento roteado. Mostra os **dados já
   cadastrados** (paciente, queixa, sinais, classificação) e o **agente especialista da área** conduz
   o roteiro e gera o **Pré-diagnóstico** (hipóteses + confiança + exames sugeridos). *Uma tela que se
   adapta à especialidade roteada* (ou uma por especialidade, mas alimentada pela triagem).

3. **Encaminhamento ao Médico** — a partir do pré-diagnóstico + especialidade, o **agente de
   encaminhamento** seleciona o **médico** disponível e **cria o encaminhamento** (persistido, ligado
   ao `atendimento_id`).

4. **Prontuário & Consulta Médica** — o **médico** vê o **histórico consolidado** do atendimento
   (triagem + pré-diagnóstico + encaminhamento) e registra a consulta. O **agente de registro**
   consolida tudo no prontuário do paciente.

### MÓDULO B — CADASTROS (administrativo, ao FINAL do menu)
Onde o **administrador** gerencia os dados de apoio — CRUD puro, separado do fluxo:
- **Pacientes** · **Médicos** · **Especialidades** · **Agentes de IA**
Consulta e edição dos registros (inclusive os que o fluxo de atendimento criou automaticamente).

> Regra de organização: **Atendimento em cima** (o que se usa no dia a dia, conduzido por agentes),
> **Cadastros embaixo** (administração). Nada de misturar.

## 3. COMO o paciente é cadastrado na triagem (o ponto-chave que faltava)

A tela **Recepção & Triagem** deixa de ser "só um agente" e passa a orquestrar uma sequência
determinística + agêntica ao clicar **"Iniciar Triagem"**:

```
1. buscar_paciente_por_cpf(cpf)              [determinístico]
2. SE não existe:
     paciente_id = cadastrar_paciente(nome, cpf, nascimento, contato, convenio)   [determinístico]
   SENÃO: paciente_id = registro encontrado
3. atendimento_id = abrir_atendimento(paciente_id, queixa, sinais_vitais)          [determinístico]
4. triagem = triagem_hub_agent(queixa, sinais_vitais)  → { urgencia, especialidade } [AGENTE]
5. gravar_triagem(atendimento_id, urgencia, especialidade)                          [determinístico]
6. rotear → Pré-atendimento(especialidade)
```

Assim: **o operador/paciente digita os dados uma vez na triagem; o sistema cadastra o paciente (se
novo) e abre o atendimento** — gerando `paciente_id` e `atendimento_id` que as etapas seguintes
(encaminhamento, prontuário) exigem. **Resolve os erros de FK** encontrados na demo.

## 4. Correções de comportamento a embutir (via LangNet)

1. **Triagem cadastra/identifica paciente + abre atendimento** (§3) → gera as FKs.
2. **`especialidade` de LISTA FECHADA** — a triagem escolhe entre as especialidades cadastradas
   (Cardiologia, Pediatria, Gastroenterologia, Endocrinologia, Oncologia, Pronto-Socorro), não texto
   livre → roteamento automático confiável.
3. **Encaminhamento e Prontuário recebem os IDs** (`atendimento_id`, `paciente_id`) do atendimento
   corrente, não nomes.
4. **Pré-atendimento roteado** pela especialidade da triagem.

## 5. Rastreabilidade exigida (Spec ⟷ Interface ⟷ Implementação)

Cada uma dessas mudanças precisa **nascer na Especificação** (nos casos de uso e nos wireframes) e
**propagar** para o Protótipo (ui_spec) e para o Código, mantendo a proveniência (qual versão da spec
gerou qual protótipo/código). A verificação desse encadeamento é parte da tarefa (ver relatório).
