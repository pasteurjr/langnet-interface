# Descrição do Sistema — Clínica Médica com Triagem Inteligente por Agentes

> **Este é o texto-semente entregue ao pipeline do LangNet** (etapa de Requisitos). Tudo o que o
> sistema gerar (especificação, modelo de dados, telas, agentes, tarefas, rede de Petri, código)
> deriva desta descrição. Registrado aqui para o relatório de verificação.

**Projeto:** Clínica Médica Inteligente (nome interno: *ClinIA*)
**Data:** 2026-08-03 · **Objetivo do teste:** validar o ciclo completo do LangNet num domínio
fortemente **agêntico** (roteamento entre agentes especialistas), distinto do domínio anterior.

---

## 1. Visão geral

Sistema para uma clínica médica que usa **agentes de IA** para fazer a **triagem** dos pacientes e
conduzir um **pré-atendimento** antes do médico humano. O paciente entra, descreve sua queixa, e uma
cadeia de agentes o classifica, aprofunda a coleta na especialidade certa, produz um **pré-diagnóstico**
e o **encaminha para o médico** adequado — com todo o histórico registrado em banco.

A ideia central é um **agente-hub de triagem** que roteia para **agentes especialistas** por área
médica. Cada especialista interage com o paciente, refina os sintomas, gera um pré-diagnóstico e
encaminha ao médico humano daquela especialidade.

## 2. Papéis (atores)

- **Paciente** — pessoa que busca atendimento; descreve sintomas, responde às perguntas dos agentes.
- **Recepcionista/Atendente** — cadastra pacientes, acompanha a fila de triagem, confirma encaminhamentos.
- **Médico** — humano de uma especialidade; recebe o pré-diagnóstico do agente e conduz a consulta final.
- **Administrador** — gere cadastros (médicos, especialidades, agentes), parâmetros e relatórios.

## 3. Agentes de IA (o coração do sistema)

1. **Agente de Triagem (Hub)** — recebe o paciente e a queixa inicial (texto livre + sinais vitais
   opcionais), faz uma **classificação de urgência** (verde/amarelo/vermelho — protocolo tipo Manchester)
   e determina a **especialidade de destino**. Encaminha para o agente especialista correto.
2. **Agentes Especialistas** (um por área) — conduzem um **pré-atendimento** dirigido àquela área,
   com um roteiro de perguntas específico, e produzem um **pré-diagnóstico** (hipóteses + nível de
   confiança + recomendação de exames). Áreas iniciais:
   - **Cardiologia**
   - **Dermatologia**
   - **Gastroenterologia**
   - **Endocrinologia**
   - **Oncologia**
   - **Pronto-Socorro / Emergência** (para casos classificados como urgentes/vermelhos)
3. **Agente de Encaminhamento** — a partir do pré-diagnóstico e da especialidade, seleciona o
   **médico** disponível daquela área (agenda/disponibilidade) e cria o encaminhamento.
4. **Agente de Registro/Prontuário** — consolida triagem + pré-diagnóstico + encaminhamento no
   **prontuário** do paciente e gera um resumo para o médico.

> Fluxo agêntico principal: **Paciente → Triagem(Hub) → [classifica urgência + área] → Especialista(área)
> → [pré-diagnóstico] → Encaminhamento → Médico**. Casos vermelhos desviam direto para Pronto-Socorro.

## 4. Cadastros (CRUD) e banco de dados

O sistema precisa de um banco de dados completo com, no mínimo:
- **Pacientes** (nome, CPF, data de nascimento, contato, convênio, histórico).
- **Médicos** (nome, CRM, especialidade, disponibilidade/agenda, contato).
- **Especialidades** (nome, descrição, agente especialista associado).
- **Agentes** (nome, tipo: triagem/especialista/encaminhamento/registro, especialidade associada,
  prompt/roteiro, status ativo).
- **Atendimentos / Triagens** (paciente, queixa, sinais vitais, classificação de urgência, área de
  destino, data/hora, status).
- **Pré-diagnósticos** (atendimento, agente, hipóteses, confiança, exames sugeridos, texto).
- **Encaminhamentos** (atendimento, especialidade, médico, prioridade, status).
- **Prontuário / Registros** (paciente, histórico consolidado de atendimentos).

## 5. Interface (telas de negócio)

Interface completa, organizada por módulos:
- **Recepção**: cadastro/edição de pacientes; abertura de atendimento; fila de triagem.
- **Triagem (agêntica)**: tela onde o agente-hub recebe a queixa, classifica urgência e mostra a área
  de destino — com o resultado do roteamento.
- **Pré-atendimento por especialidade (agêntica)**: tela do agente especialista conduzindo o roteiro e
  exibindo o **pré-diagnóstico** gerado.
- **Encaminhamentos**: lista de encaminhamentos gerados, com o médico selecionado.
- **Prontuário do paciente**: histórico consolidado.
- **Painel/Dashboard**: KPIs (atendimentos do dia, distribuição por especialidade, urgências,
  tempo médio de triagem).
- **Cadastros administrativos**: médicos, especialidades, agentes.

## 6. Casos de uso principais (para a triagem)

- **UC — Cadastrar paciente**: recepção registra o paciente no banco.
- **UC — Abrir atendimento / Triagem**: o paciente descreve a queixa; o **agente de triagem** classifica
  urgência e área; registra o atendimento.
- **UC — Pré-atendimento especialista**: o **agente da especialidade** conduz o roteiro e gera o
  pré-diagnóstico.
- **UC — Encaminhar ao médico**: o **agente de encaminhamento** escolhe o médico e cria o encaminhamento.
- **UC — Consultar prontuário**: médico/recepção consulta o histórico do paciente.
- **UC — Dashboard operacional**: administrador acompanha KPIs do dia.

## 7. Requisitos não-funcionais

- Registrar **tudo** em banco (triagem, pré-diagnóstico, encaminhamento, prontuário) com
  rastreabilidade (qual agente produziu o quê e quando).
- A triagem deve ser **auditável**: guardar a queixa original, a classificação e a justificativa.
- Aviso claro de que os pré-diagnósticos são **apoio à decisão** — a decisão final é sempre do médico humano.
- Interface responsiva e organizada por módulos.

---

*Nota de escopo do teste: este documento é a entrada. O propósito é observar como o LangNet
especifica, modela, prototipa, decompõe em agentes/tarefas, desenha a Rede de Petri e gera o código —
usando a própria revisão do pipeline em cada etapa.*
