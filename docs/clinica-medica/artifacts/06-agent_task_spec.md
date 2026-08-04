# GERAÇÃO DE ESPECIFICAÇÃO DE AGENTES E TAREFAS

## 1. VISÃO GERAL DOS AGENTES

| ID    | Nome                           | Módulo                | LLM             | Memória |
|-------|--------------------------------|-----------------------|-----------------|---------|
| AG-01 | recepcionista_agent            | Cadastro              | GPT-4o          | Sim     |
| AG-02 | triagem_hub_agent              | Triagem               | Claude 3.5      | Não     |
| AG-03 | especialista_cardiologia_agent   | Pré-atendimento       | Claude 3.5      | Não     |
| AG-04 | especialista_pediatria_agent     | Pré-atendimento       | GPT-4o          | Não     |
| AG-05 | especialista_gastroenterologia_agent | Pré-atendimento    | GPT-4o-mini     | Não     |
| AG-06 | encaminhamento_agent           | Encaminhamento        | GPT-4o          | Sim     |
| AG-07 | registro_prontuario_agent      | Registro/Prontuário   | GPT-4o          | Sim     |
| AG-08 | medico_agent                   | Consulta Médica       | Claude 3.5      | Não     |
| AG-09 | administrador_agent            | Gestão Administrativa | Claude 3.5      | Sim     |
| AG-10 | fallback_agent                 | Fallback              | GPT-4o          | Não     |
| AG-11 | kpi_dashboard_agent            | Dashboard             | GPT-4o-mini     | Não     |
| AG-12 | agenda_medico_agent            | Gestão Agenda         | GPT-4o-mini     | Sim     |

## 2. ESPECIFICAÇÃO DETALHADA DOS AGENTES

#### AG-01: Recepcionista Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | recepcionista_agent |
| **Role**          | Gerente de Cadastros e Atendimentos Iniciais |
| **Goal**          | Realizar o cadastro e abertura de atendimentos para pacientes, garantindo a coleta completa e precisa de dados. |
| **Backstory**     | Você é um recepcionista com mais de 10 anos de experiência em clínicas médicas. Sua função principal é garantir que todos os detalhes do paciente sejam registrados corretamente para o fluxo de triagem subsequente. |
| **LLM**           | GPT-4o        |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar a triagem inicial para AG-02 (Triagem Hub Agent) após o cadastro do paciente. |
| **Memória**       | Habilitada    |
| **Verbose**       | true          |
| **Módulo**        | Cadastro      |
| **Rationale**     | Este agente é fundamental porque centraliza a entrada de dados dos pacientes, garantindo que todas as informações necessárias estejam corretamente registradas. |

#### AG-02: Triagem Hub Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | triagem_hub_agent |
| **Role**          | Agente de Triagem Automatizado |
| **Goal**          | Classificar a urgência dos pacientes com base em suas queixas e sinais vitais, roteirizando-os para o agente especialista correto. |
| **Backstory**     | Você é um especialista em IA treinado para triagem médica de acordo com protocolos clínicos. Sua função principal é classificar a urgência dos pacientes e direcioná-los ao especialista adequado. |
| **LLM**           | Claude 3.5      |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar o pré-atendimento para os agentes especialistas (AG-03, AG-04, AG-05) após a triagem. |
| **Memória**       | Não           |
| **Verbose**       | true          |
| **Módulo**        | Triagem       |
| **Rationale**     | Este agente é essencial para garantir que os pacientes sejam direcionados corretamente com base em sua urgência, otimizando o fluxo de atendimento. |

#### AG-03: Especialista Cardiologia Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | especialista_cardiologia_agent |
| **Role**          | Agente Especialista em Cardiologia |
| **Goal**          | Realizar o pré-atendimento específico para pacientes com problemas cardíacos, gerando um pré-diagnóstico. |
| **Backstory**     | Você é um médico especializado em cardiologia treinado para triagem e diagnósticos automatizados. Sua função principal é coletar informações específicas dos pacientes e gerar um pré-diagnóstico com base nessas informações. |
| **LLM**           | Claude 3.5      |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar o encaminhamento para AG-06 (Encaminhamento Agent) após gerar o pré-diagnóstico. |
| **Memória**       | Não           |
| **Verbose**       | true          |
| **Módulo**        | Pré-atendimento|
| **Rationale**     | Este agente é crucial para garantir diagnósticos precisos e rápidos para pacientes cardíacos, facilitando o encaminhamento adequado. |

#### AG-04: Especialista Pediatria Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | especialista_pediatria_agent |
| **Role**          | Agente Especialista em Pediatria |
| **Goal**          | Realizar o pré-atendimento específico para pacientes pediátricos, gerando um pré-diagnóstico. |
| **Backstory**     | Você é um médico especializado em pediatria treinado para triagem e diagnósticos automatizados. Sua função principal é coletar informações específicas dos pacientes e gerar um pré-diagnóstico com base nessas informações. |
| **LLM**           | GPT-4o        |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar o encaminhamento para AG-06 (Encaminhamento Agent) após gerar o pré-diagnóstico. |
| **Memória**       | Não           |
| **Verbose**       | true          |
| **Módulo**        | Pré-atendimento|
| **Rationale**     | Este agente é crucial para garantir diagnósticos precisos e rápidos para pacientes pediátricos, facilitando o encaminhamento adequado. |

#### AG-05: Especialista Gastroenterologia Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | especialista_gastroenterologia_agent |
| **Role**          | Agente Especialista em Gastroenterologia |
| **Goal**          | Realizar o pré-atendimento específico para pacientes com problemas gastrointestinais, gerando um pré-diagnóstico. |
| **Backstory**     | Você é um médico especializado em gastroenterologia treinado para triagem e diagnósticos automatizados. Sua função principal é coletar informações específicas dos pacientes e gerar um pré-diagnóstico com base nessas informações. |
| **LLM**           | GPT-4o-mini     |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar o encaminhamento para AG-06 (Encaminhamento Agent) após gerar o pré-diagnóstico. |
| **Memória**       | Não           |
| **Verbose**       | true          |
| **Módulo**        | Pré-atendimento|
| **Rationale**     | Este agente é crucial para garantir diagnósticos precisos e rápidos para pacientes gastrointestinais, facilitando o encaminhamento adequado. |

#### AG-06: Encaminhamento Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | encaminhamento_agent |
| **Role**          | Agente de Encaminhamento Automatizado |
| **Goal**          | Selecionar médicos disponíveis e criar encaminhamentos para pacientes com base nos pré-diagnósticos. |
| **Backstory**     | Você é um especialista em IA treinado para gerenciar encaminhamentos médicos, garantindo que os pacientes sejam direcionados aos médicos corretos e disponíveis. |
| **LLM**           | GPT-4o        |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar a confirmação do encaminhamento para o recepcionista (AG-01). |
| **Memória**       | Sim           |
| **Verbose**       | true          |
| **Módulo**        | Encaminhamento|
| **Rationale**     | Este agente é essencial para garantir que os pacientes sejam encaminhados corretamente, otimizando o fluxo de atendimento. |

#### AG-07: Registro Prontuário Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | registro_prontuario_agent |
| **Role**          | Agente de Registro/Prontuário Automatizado |
| **Goal**          | Consolidar a triagem, pré-diagnóstico e encaminhamento no prontuário do paciente. |
| **Backstory**     | Você é um especialista em IA treinado para gerenciar o registro de prontuários médicos, garantindo que todas as informações relevantes sejam registradas corretamente. |
| **LLM**           | GPT-4o        |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar a consulta médica para AG-08 (Médico Agent) após registrar o prontuário. |
| **Memória**       | Sim           |
| **Verbose**       | true          |
| **Módulo**        | Registro/Prontuário|
| **Rationale**     | Este agente é fundamental para garantir que os registros de prontuários estejam completos e precisos, facilitando a revisão médica subsequente. |

#### AG-08: Médico Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | medico_agent |
| **Role**          | Agente de Consulta Médica Automatizado |
| **Goal**          | Realizar a consulta médica final, validar ou refutar hipóteses do pré-diagnóstico e registrar o diagnóstico final. |
| **Backstory**     | Você é um médico treinado para realizar consultas médicas automatizadas, garantindo que as decisões clínicas finais sejam tomadas corretamente. |
| **LLM**           | Claude 3.5      |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Nenhum          |
| **Memória**       | Não           |
| **Verbose**       | true          |
| **Módulo**        | Consulta Médica|
| **Rationale**     | Este agente é crucial para garantir que as decisões clínicas finais sejam tomadas com base nos dados disponíveis, otimizando o fluxo de atendimento. |

#### AG-09: Administrador Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | administrador_agent |
| **Role**          | Agente de Gestão Administrativa |
| **Goal**          | Gerenciar médicos, especialidades, agentes, agendas e usuários; auditar o sistema. |
| **Backstory**     | Você é um administrador treinado para gerenciar a clínica médica, garantindo que todos os processos estejam funcionando corretamente e otimizados. |
| **LLM**           | Claude 3.5      |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Nenhum          |
| **Memória**       | Sim           |
| **Verbose**       | true          |
| **Módulo**        | Gestão Administrativa|
| **Rationale**     | Este agente é fundamental para garantir que a clínica médica esteja bem gerenciada e otimizada, facilitando o funcionamento correto do sistema. |

#### AG-10: Fallback Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | fallback_agent |
| **Role**          | Agente de Fallback Manual |
| **Goal**          | Implementar procedimento alternativo quando um agente de IA estiver indisponível ou retornar erro. |
| **Backstory**     | Você é um especialista em IA treinado para gerenciar situações de fallback, garantindo que os pacientes sejam atendidos mesmo em situações de falha do sistema. |
| **LLM**           | GPT-4o        |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Nenhum          |
| **Memória**       | Não           |
| **Verbose**       | true          |
| **Módulo**        | Fallback|
| **Rationale**     | Este agente é essencial para garantir que os pacientes sejam atendidos mesmo em situações de falha do sistema, otimizando a continuidade dos processos. |

#### AG-11: KPI Dashboard Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | kpi_dashboard_agent |
| **Role**          | Agente de Visualização de KPIs |
| **Goal**          | Exibir KPIs operacionais do sistema para monitoramento e análise. |
| **Backstory**     | Você é um especialista em IA treinado para gerar dashboards com KPIs, garantindo que os administradores possam monitorar o desempenho do sistema facilmente. |
| **LLM**           | GPT-4o-mini     |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Nenhum          |
| **Memória**       | Não           |
| **Verbose**       | true          |
| **Módulo**        | Dashboard|
| **Rationale**     | Este agente é fundamental para garantir que os administradores possam monitorar o desempenho do sistema facilmente, facilitando a tomada de decisões. |

#### AG-12: Agenda Médico Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | agenda_medico_agent |
| **Role**          | Agente de Gestão da Agenda Médica |
| **Goal**          | Gerenciar a agenda e disponibilidade dos médicos para encaminhamentos. |
| **Backstory**     | Você é um especialista em IA treinado para gerenciar agendas médicas, garantindo que os pacientes sejam direcionados aos médicos disponíveis corretamente. |
| **LLM**           | GPT-4o-mini     |
| **Tools**         | database_tool, embedding_tool |
| **Delegação**     | Pode delegar a atualização da agenda para AG-09 (Administrador Agent). |
| **Memória**       | Sim           |
| **Verbose**       | true          |
| **Módulo**        | Gestão Agenda|
| **Rationale**     | Este agente é essencial para garantir que os pacientes sejam direcionados aos médicos disponíveis corretamente, otimizando o fluxo de atendimento. |

## 3. ESPECIFICAÇÃO DETALHADA DAS TAREFAS

#### T-CAD-001: Cadastro de Pacientes

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-001     |
| **Nome**           | cadastrar_paciente |
| **Descrição**      | Cadastrar um novo paciente no sistema, armazenando os dados fornecidos. |
| **Agent**          | AG-01 (Recepcionista Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- nome: String\n- cpf: String\n- data_nascimento: Date\n- contato: String\n- convenio: String\n- historico: Text\n- status: Enum (ativo/inativo)\n- consentimento: Boolean |
| **Output Schema**  | \n- paciente_id: UUID (ID do paciente armazenado) |
| **Dependencies**   | None (primeira task do módulo) |
| **Módulo**         | Cadastro       |
| **UC Relacionado** | UC-001 (Cadastro de Pacientes) |
| **RF Relacionado** | FR-002 (CRUD de Pacientes)      |
| **Rationale**      | Esta task é fundamental porque permite que o sistema ingira informações básicas dos pacientes, garantindo precisão e rastreabilidade. |

#### T-CAD-002: Atualização de Pacientes

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-002     |
| **Nome**           | atualizar_paciente |
| **Descrição**      | Atualizar informações do paciente no sistema, armazenando os dados fornecidos. |
| **Agent**          | AG-01 (Recepcionista Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- nome: String\n- cpf: String\n- data_nascimento: Date\n- contato: String\n- convenio: String\n- historico: Text\n- status: Enum (ativo/inativo)\n- consentimento: Boolean |
| **Output Schema**  | \n- paciente_id: UUID (ID do paciente armazenado) |
| **Dependencies**   | T-CAD-001 (Cadastro de Pacientes) |
| **Módulo**         | Cadastro       |
| **UC Relacionado** | UC-002 (Atualização de Pacientes) |
| **RF Relacionado** | FR-002 (CRUD de Pacientes)      |
| **Rationale**      | Esta task permite manter as informações do paciente atualizadas, garantindo que o sistema sempre tenha dados precisos e relevantes. |

#### T-CAD-003: Triagem Agentiva

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-003     |
| **Nome**           | triagem_agentiva |
| **Descrição**      | Classificar a urgência do paciente com base em sinais vitais e queixa inicial, roteirizando-o para o agente especialista correto. |
| **Agent**          | AG-02 (Triagem Hub Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- queixa_inicial: String\n- sinais_vitais: Text |
| **Output Schema**  | \n- classificacao_urgencia: Enum (verde/amarelo/vermelho)\n- justificativa: Text\n- area_destino: String |
| **Dependencies**   | T-CAD-001 (Cadastro de Pacientes) |
| **Módulo**         | Triagem        |
| **UC Relacionado** | UC-002 (Triagem Agentiva) |
| **RF Relacionado** | FR-009 (Agente de Triagem), FR-010 (Classificação de Urgência Manchester) |
| **Rationale**      | Esta task é essencial para garantir que os pacientes sejam direcionados corretamente com base em sua urgência, otimizando o fluxo de atendimento. |

#### T-CAD-004: Pré-atendimento Cardiologia

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-004     |
| **Nome**           | pre_atendimento_cardiologia |
| **Descrição**      | Realizar o pré-atendimento específico para pacientes com problemas cardíacos, gerando um pré-diagnóstico. |
| **Agent**          | AG-03 (Especialista Cardiologia Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- queixa_inicial: String\n- sinais_vitais: Text |
| **Output Schema**  | \n- hipoteses: JSON\n- nivel_confianca: Enum (baixa/média/alta)\n- exames_sugeridos: Text |
| **Dependencies**   | T-CAD-003 (Triagem Agentiva) |
| **Módulo**         | Pré-atendimento|
| **UC Relacionado** | UC-003 (Pré-atendimento por Especialista) |
| **RF Relacionado** | FR-013 (Pré-atendimento por Especialista), FR-014 (Geração de Pré-diagnóstico) |
| **Rationale**      | Esta task é crucial para garantir diagnósticos precisos e rápidos para pacientes cardíacos, facilitando o encaminhamento adequado. |

#### T-CAD-005: Pré-atendimento Pediatria

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-005     |
| **Nome**           | pre_atendimento_pediatria |
| **Descrição**      | Realizar o pré-atendimento específico para pacientes pediátricos, gerando um pré-diagnóstico. |
| **Agent**          | AG-04 (Especialista Pediatria Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- queixa_inicial: String\n- sinais_vitais: Text |
| **Output Schema**  | \n- hipoteses: JSON\n- nivel_confianca: Enum (baixa/média/alta)\n- exames_sugeridos: Text |
| **Dependencies**   | T-CAD-003 (Triagem Agentiva) |
| **Módulo**         | Pré-atendimento|
| **UC Relacionado** | UC-003 (Pré-atendimento por Especialista) |
| **RF Relacionado** | FR-013 (Pré-atendimento por Especialista), FR-014 (Geração de Pré-diagnóstico) |
| **Rationale**      | Esta task é crucial para garantir diagnósticos precisos e rápidos para pacientes pediátricos, facilitando o encaminhamento adequado. |

#### T-CAD-006: Pré-atendimento Gastroenterologia

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-006     |
| **Nome**           | pre_atendimento_gastroenterologia |
| **Descrição**      | Realizar o pré-atendimento específico para pacientes com problemas gastrointestinais, gerando um pré-diagnóstico. |
| **Agent**          | AG-05 (Especialista Gastroenterologia Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- queixa_inicial: String\n- sinais_vitais: Text |
| **Output Schema**  | \n- hipoteses: JSON\n- nivel_confianca: Enum (baixa/média/alta)\n- exames_sugeridos: Text |
| **Dependencies**   | T-CAD-003 (Triagem Agentiva) |
| **Módulo**         | Pré-atendimento|
| **UC Relacionado** | UC-003 (Pré-atendimento por Especialista) |
| **RF Relacionado** | FR-013 (Pré-atendimento por Especialista), FR-014 (Geração de Pré-diagnóstico) |
| **Rationale**      | Esta task é crucial para garantir diagnósticos precisos e rápidos para pacientes gastrointestinais, facilitando o encaminhamento adequado. |

#### T-CAD-007: Encaminhamento

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-007     |
| **Nome**           | criar_encaminhamento |
| **Descrição**      | Selecionar médico disponível e criar encaminhamento para o paciente com base no pré-diagnóstico. |
| **Agent**          | AG-06 (Encaminhamento Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- especialidade_id: UUID\n- hipoteses: JSON\n- nivel_confianca: Enum (baixa/média/alta)\n- exames_sugeridos: Text |
| **Output Schema**  | \n- encaminhamento_id: UUID (ID do encaminhamento armazenado) |
| **Dependencies**   | T-CAD-004, T-CAD-005, T-CAD-006 (Pré-atendimento por Especialista) |
| **Módulo**         | Encaminhamento|
| **UC Relacionado** | UC-004 (Geração de Pré-diagnóstico), UC-005 (Agente de Encaminhamento) |
| **RF Relacionado** | FR-015 (Agente de Encaminhamento), FR-031 (Agenda e Disponibilidade Médica) |
| **Rationale**      | Esta task é essencial para garantir que os pacientes sejam encaminhados corretamente, otimizando o fluxo de atendimento. |

#### T-CAD-008: Registro de Prontuário

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-008     |
| **Nome**           | registrar_prontuario |
| **Descrição**      | Consolidar a triagem, pré-diagnóstico e encaminhamento no prontuário do paciente. |
| **Agent**          | AG-07 (Registro Prontuário Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- atendimento_id: UUID\n- triagem: Text\n- pre_diagnostico_id: UUID\n- encaminhamento_id: UUID\n- resumo_medico: Text |
| **Output Schema**  | \n- prontuario_id: UUID (ID do prontuário armazenado) |
| **Dependencies**   | T-CAD-003, T-CAD-004, T-CAD-005, T-CAD-006, T-CAD-007 (Encaminhamento) |
| **Módulo**         | Registro/Prontuário|
| **UC Relacionado** | UC-006 (Agente de Registro/Prontuário) |
| **RF Relacionado** | FR-016 (Agente de Registro/Prontuário), FR-021 (Tela de Prontuário) |
| **Rationale**      | Esta task é fundamental para garantir que os registros de prontuários estejam completos e precisos, facilitando a revisão médica subsequente. |

#### T-CAD-009: Consulta Médica

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-009     |
| **Nome**           | consulta_medica |
| **Descrição**      | Realizar a consulta médica final, validar ou refutar hipóteses do pré-diagnóstico e registrar o diagnóstico final. |
| **Agent**          | AG-08 (Médico Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- atendimento_id: UUID\n- hipoteses: JSON\n- nivel_confianca: Enum (baixa/média/alta)\n- exames_sugeridos: Text |
| **Output Schema**  | \n- diagnostico_final: String\n- conduta: String\n- prescricao: String |
| **Dependencies**   | T-CAD-008 (Registro de Prontuário) |
| **Módulo**         | Consulta Médica|
| **UC Relacionado** | UC-007 (Consulta Médica) |
| **RF Relacionado** | FR-030 (Fluxo de Consulta Médica), BR-003 (Pré-diagnóstico como Apoio) |
| **Rationale**      | Esta task é crucial para garantir que as decisões clínicas finais sejam tomadas com base nos dados disponíveis, otimizando o fluxo de atendimento. |

#### T-CAD-010: Gestão de Administrador

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-010     |
| **Nome**           | gerir_administrador |
| **Descrição**      | Gerenciar médicos, especialidades, agentes, agendas e usuários; auditar o sistema. |
| **Agent**          | AG-09 (Administrador Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- acao: Enum (cadastrar/atualizar/excluir)\n- tipo_registro: Enum (medicos/especialidades/agentes/agendas/usuarios)\n- dados: JSON |
| **Output Schema**  | \n- status: String (sucesso/falha) |
| **Dependencies**   | None          |
| **Módulo**         | Gestão Administrativa|
| **UC Relacionado** | UC-012 (CRUD de Agentes de IA), UC-013 (CRUD de Especialidades), UC-014 (CRUD de Médicos) |
| **RF Relacionado** | FR-005, FR-004, FR-003 (CRUD de Agentes/Especialidades/Médicos) |
| **Rationale**      | Esta task é fundamental para garantir que a clínica médica esteja bem gerenciada e otimizada, facilitando o funcionamento correto do sistema. |

#### T-CAD-011: Fallback Manual

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-011     |
| **Nome**           | fallback_manual |
| **Descrição**      | Implementar procedimento alternativo quando um agente de IA estiver indisponível ou retornar erro. |
| **Agent**          | AG-10 (Fallback Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- paciente_id: UUID\n- atendimento_id: UUID\n- justificativa: Text |
| **Output Schema**  | \n- status: String (sucesso/falha) |
| **Dependencies**   | None          |
| **Módulo**         | Fallback|
| **UC Relacionado** | UC-009 (Fallback Manual) |
| **RF Relacionado** | FR-027 (Fallback Manual)      |
| **Rationale**      | Este agente é essencial para garantir que os pacientes sejam atendidos mesmo em situações de falha do sistema, otimizando a continuidade dos processos. |

#### T-CAD-012: Visualização de KPIs

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-012     |
| **Nome**           | visualizar_kpis |
| **Descrição**      | Exibir KPIs operacionais do sistema para monitoramento e análise. |
| **Agent**          | AG-11 (KPI Dashboard Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- periodo: Enum (diario/semanal/mensal)\n- metricas_selecionadas: List[String] |
| **Output Schema**  | \n- kpis: JSON |
| **Dependencies**   | None          |
| **Módulo**         | Dashboard|
| **UC Relacionado** | UC-010 (Visualização de KPIs) |
| **RF Relacionado** | FR-022 (Painel/Dashboard KPIs)      |
| **Rationale**      | Este agente é fundamental para garantir que os administradores possam monitorar o desempenho do sistema facilmente, facilitando a tomada de decisões. |

#### T-CAD-013: Gestão da Agenda Médica

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-013     |
| **Nome**           | gerir_agenda_medico |
| **Descrição**      | Gerenciar a agenda e disponibilidade dos médicos para encaminhamentos. |
| **Agent**          | AG-12 (Agenda Médico Agent) |
| **Tools**          | database_tool, embedding_tool |
| **Input Schema**   | \n- medico_id: UUID\n- horarios_disponiveis: List[DateTime] |
| **Output Schema**  | \n- status: String (sucesso/falha) |
| **Dependencies**   | None          |
| **Módulo**         | Gestão Agenda|
| **UC Relacionado** | UC-011 (Gestão de Agenda e Disponibilidade Médica) |
| **RF Relacionado** | FR-031 (Agenda e Disponibilidade Médica)      |
| **Rationale**      | Este agente é essencial para garantir que os pacientes sejam direcionados aos médicos disponíveis corretamente, otimizando o fluxo de atendimento. |

## 4. MATRIZ DE RASTREABILIDADE

| Task ID   | Task Nome                 | UC          | RF          | Módulo       |
|-----------|---------------------------|-------------|-------------|--------------|
| T-CAD-001 | cadastrar_paciente        | UC-001      | FR-002      | Cadastro     |
| T-CAD-002 | atualizar_paciente        | UC-002      | FR-002      | Cadastro     |
| T-CAD-003 | triagem_agentiva          | UC-002      | FR-009, FR-010 | Triagem    |
| T-CAD-004 | pre_atendimento_cardiologia | UC-003     | FR-013, FR-014  | Pré-atendimento|
| T-CAD-005 | pre_atendimento_pediatria | UC-003      | FR-013, FR-014  | Pré-atendimento|
| T-CAD-006 | pre_atendimento_gastroenterologia | UC-003     | FR-013, FR-014  | Pré-atendimento|
| T-CAD-007 | criar_encaminhamento    | UC-005      | FR-015, FR-031  | Encaminhamento |
| T-CAD-008 | registrar_prontuario    | UC-006      | FR-016, FR-021  | Registro/Prontuário|
| T-CAD-009 | consulta_medica         | UC-007      | FR-030, BR-003  | Consulta Médica|
| T-CAD-010 | gerir_administrador     | UC-012, UC-013, UC-014 | FR-005, FR-004, FR-003 | Gestão Administrativa |
| T-CAD-011 | fallback_manual         | UC-009      | FR-027        | Fallback     |
| T-CAD-012 | visualizar_kpis         | UC-010      | FR-022        | Dashboard    |
| T-CAD-013 | gerir_agenda_medico     | UC-011      | FR-031        | Gestão Agenda|

## 5. GRAFO DE DEPENDÊNCIAS (RESUMO VISUAL)

```
MÓDULO: Cadastro
├─ T-CAD-001 (Cadastro de Pacientes)
│  ↓
├─ T-CAD-002 (Atualização de Pacientes)

MÓDULO: Triagem
└─ T-CAD-003 (Triagem Agentiva)

MÓDULO: Pré-atendimento
├─ T-CAD-004 (Pré-atendimento Cardiologia)
│  ↓
├─ T-CAD-005 (Pré-atendimento Pediatria)
│  ↓
└─ T-CAD-006 (Pré-atendimento Gastroenterologia)

MÓDULO: Encaminhamento
└─ T-CAD-007 (Encaminhamento)

MÓDULO: Registro/Prontuário
└─ T-CAD-008 (Registro de Prontuário)

MÓDULO: Consulta Médica
└─ T-CAD-009 (Consulta Médica)

MÓDULO: Gestão Administrativa
└─ T-CAD-010 (Gestão de Administrador)

MÓDULO: Fallback
└─ T-CAD-011 (Fallback Manual)

MÓDULO: Dashboard
└─ T-CAD-012 (Visualização de KPIs)

MÓDULO: Gestão Agenda
└─ T-CAD-013 (Gestão da Agenda Médica)
```