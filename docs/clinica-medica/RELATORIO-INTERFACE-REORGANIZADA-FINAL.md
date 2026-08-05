# Interface Reorganizada — Resultado Final (propagado até o app)

**Data:** 2026-08-05 · **Projeto:** ClinIA · **Correções feitas pelo agente do LangNet + gerador**

> Fechamento do ciclo que você pediu: LangNet reorganizou a Especificação (via UI/agente) →
> propaguei para Protótipo e Código → o **app rodando reflete a interface reorganizada**, com
> rastreabilidade verificada. Abaixo o resultado, os comentários e o que ainda falta.

## 1. O menu ficou em DOIS módulos (como você pediu) ✅

O app gerado agora separa claramente:
- **ATENDIMENTO** (no topo — o fluxo agêntico): Recepção & Triagem → Pré-atendimento por Especialista
  → Geração de Pré-diagnóstico → Seleção de Médico → Registro/Prontuário → Consulta Médica →
  Dashboard KPIs.
- **CADASTROS** (ao final — administrativo): Cadastro de Pacientes, Consentimentos, Gestão de Agendas,
  Agentes, Especialidades, Médicos, Pacientes.

![App ClinIA — menu reorganizado em ATENDIMENTO (fluxo) + CADASTROS (admin)](R1)

**Comentário:** acabou a confusão de cadastros misturados com telas agênticas. O fluxo de atendimento
está em cima, os cadastros administrativos embaixo.

## 2. Como isso foi feito (rastreabilidade + quem fez)

1. **LangNet (agente) refinou a Especificação** para a **v3** — UC-002 virou "Recepção & Triagem" com
   identificação do paciente + abertura de atendimento + especialidade de lista fechada. *(Via o mesmo
   endpoint que o botão "Refinar" da UI aciona.)*
2. **Propaguei** regenerando **Protótipo** (nova sessão, `specification_version=3`) e **Código**. A
   proveniência liga cada artefato à spec v3; o `sync-status` saiu de `stale:true` (após o refino) e
   voltou a `stale:false` (após regenerar) — **a rastreabilidade em ação**.
3. **Ajustes no GERADOR** (necessários porque o agrupamento do menu não vem da spec):
   - `_infer_module`: reconhece o fluxo de atendimento (triagem/pré-atend/encaminh/prontuário/consulta
     → **Atendimento**) e faz fallback por tipo (agêntico→Atendimento, crud→Cadastros).
   - `_MODULE_ORDER`: **Atendimento** primeiro, **Cadastros** ao final.
   - **Dedup de telas** por nome de componente (o refino gerou "Recepção & Triagem" duplicada → o build
     quebrava com "Identifier already declared"; corrigido).

## 3. ⚠️ O que ainda falta (achado honesto)

**A tela "Recepção & Triagem" renderizou como CRUD de pacientes** (mostra a tabela dos 3 pacientes com
Ver/Editar/Excluir), **não** como a tela híbrida ideal. Ao adicionar os campos de identificação do
paciente (Nome, CPF, …), o classificador `_classify_screen` a tratou como **cadastro de pacientes**,
perdendo a parte **agêntica** (campo de queixa/sinais + botão "Iniciar Triagem" + resultado da
classificação).

**O correto** seria uma **tela híbrida**: um **formulário** que (a) identifica/cadastra o paciente, e
(b) captura queixa+sinais e **dispara o agente de triagem** (classifica urgência + roteia). Hoje o
gerador monta OU uma tela CRUD OU uma tela agêntica — não uma **combinada**. Este é o próximo ajuste no
gerador (suportar tela "cadastro + ação agêntica"), que eu faço e revalido.

Também segue pendente da demonstração anterior (a corrigir no fluxo/adapters):
- Persistência de **encaminhamento/prontuário** exige `atendimento_id`/`paciente_id` — a spec v3 já
  descreve a abertura do atendimento na triagem; falta os **adapters** implementarem esse encadeamento.

## 4. Conclusão

- **Interface reorganizada e rodando**: 2 módulos claros (Atendimento × Cadastros), fluxo de
  atendimento no topo, cadastros ao final — **fim da confusão**.
- **Feito pelo LangNet** (refino da Especificação v3 pelo agente) **+ ajustes no gerador** (agrupamento
  de menu, dedup), tudo com **rastreabilidade** comprovada (proveniência + staleness ao vivo).
- **Próximo passo**: a tela **híbrida** Recepção & Triagem (cadastrar paciente **e** disparar o agente
  na mesma tela) e o encadeamento de persistência (atendimento_id) — para o fluxo agêntico rodar de
  ponta a ponta pela UI reorganizada.
