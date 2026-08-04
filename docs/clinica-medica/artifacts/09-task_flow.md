# Fluxo de Execução de Tarefas - Sistema de Clínica Médica

## 1. Visão Geral

- **Total de Tasks:** 13
- **Total de Agentes:** 12
- **Tipo de Fluxo:** Misto (Linear e Paralelo)
- **Modelo de State:** Acumulativo (LangGraph-style)

## 2. Definição do State (TypedDict)

### 2.1 Campos de Configuração e Entrada Inicial
Inclui TODOS os campos que o state inicial precisa — configurações, inputs do usuário e dados externos.

| Campo | Tipo | Descrição | Obrigatório | Valor Padrão |
|-------|------|-----------|-------------|--------------|
| campo_config | Dict[str, Any] | Configuração do sistema | Sim | {} |
| arquivo_input | str | Arquivo fornecido pelo usuário | Sim | "" |
| paciente_id | UUID | Identificador único do paciente | Não | None |
| queixa_inicial | String | Queixa inicial do paciente | Não | "" |
| sinais_vitais | Text | Sinais vitais do paciente | Não | "" |
| especialidade_id | UUID | Identificador da especialidade médica | Não | None |
| hipoteses | JSON | Hipóteses de diagnóstico geradas pelo agente especialista | Não | {} |
| nivel_confianca | Enum (baixa/média/alta) | Nível de confiança do pré-diagnóstico | Não | "" |
| exames_sugeridos | Text | Exames sugeridos para o paciente | Não | "" |
| medico_id | UUID | Identificador único do médico | Não | None |
| atendimento_id | UUID | Identificador único do atendimento | Não | None |
| triagem | Text | Informações da triagem realizada pelo agente de triagem | Não | "" |
| pre_diagnostico_id | UUID | Identificador único do pré-diagnóstico | Não | None |
| encaminhamento_id | UUID | Identificador único do encaminhamento | Não | None |
| resumo_medico | Text | Resumo médico gerado pelo agente de registro/prontuário | Não | "" |
| diagnostico_final | String | Diagnóstico final registrado pelo médico | Não | "" |
| conduta | String | Conduta médica recomendada pelo médico | Não | "" |
| prescricao | String | Prescrição médica fornecida pelo médico | Não | "" |
| acao | Enum (cadastrar/atualizar/excluir) | Ação solicitada no módulo de gestão administrativa | Não | "" |
| tipo_registro | Enum (medicos/especialidades/agentes/agendas/usuarios) | Tipo de registro para gerência administrativa | Não | "" |
| dados | JSON | Dados fornecidos para ação de gestão administrativa | Não | {} |
| justificativa | Text | Justificativa para procedimento manual ou fallback | Não | "" |
| periodo | Enum (diario/semanal/mensal) | Período para visualização de KPIs | Não | "" |
| metricas_selecionadas | List[String] | Métricas selecionadas para visualização de KPIs | Não | [] |
| horarios_disponiveis | List[DateTime] | Horários disponíveis do médico para gerência da agenda médica | Não | [] |

### 2.2 Campos de Output das Tasks
Apenas campos PRODUZIDOS por tasks durante a execução.

| Campo | Tipo | Produzido Por (ID) | Consumido Por (IDs) |
|-------|------|-------------------|---------------------|
| cadastrar_paciente_json | str | T-001 | Nenhum |
| cadastrar_paciente_data | Dict[str, Any] | T-001 | Nenhum |
| atualizar_paciente_json | str | T-002 | Nenhum |
| atualizar_paciente_data | Dict[str, Any] | T-002 | Nenhum |
| triagem_agentiva_json | str | T-003 | T-004, T-005, T-006 |
| triagem_agentiva_data | Dict[str, Any] | T-003 | T-004, T-005, T-006 |
| pre_atendimento_cardiologia_json | str | T-004 | T-007 |
| pre_atendimento_cardiologia_data | Dict[str, Any] | T-004 | T-007 |
| pre_atendimento_pediatria_json | str | T-005 | T-007 |
| pre_atendimento_pediatria_data | Dict[str, Any] | T-005 | T-007 |
| pre_atendimento_gastroenterologia_json | str | T-006 | T-007 |
| pre_atendimento_gastroenterologia_data | Dict[str, Any] | T-006 | T-007 |
| criar_encaminhamento_json | str | T-007 | T-008 |
| criar_encaminhamento_data | Dict[str, Any] | T-007 | T-008 |
| registrar_prontuario_json | str | T-008 | Nenhum |
| registrar_prontuario_data | Dict[str, Any] | T-008 | Nenhum |
| consulta_medica_json | str | T-009 | Nenhum |
| consulta_medica_data | Dict[str, Any] | T-009 | Nenhum |
| gerir_administrador_json | str | T-010 | Nenhum |
| gerir_administrador_data | Dict[str, Any] | T-010 | Nenhum |
| fallback_manual_json | str | T-011 | Nenhum |
| fallback_manual_data | Dict[str, Any] | T-011 | Nenhum |
| visualizar_kpis_json | str | T-012 | Nenhum |
| visualizar_kpis_data | Dict[str, Any] | T-012 | Nenhum |
| gerir_agenda_medico_json | str | T-013 | Nenhum |
| gerir_agenda_medico_data | Dict[str, Any] | T-013 | Nenhum |

### 2.3 Campos de Metadados
| Campo | Tipo | Descrição |
|-------|------|-----------|
| execution_log | List[Dict] | Log de execução |
| current_task | str | Task em execução |
| timestamp | str | Timestamp ISO |

## 3. Sequência de Execução

### Task 1: Cadastrar Paciente

**ID:** T-001
**Agente:** recepcionista_agent (string, não objeto)
**Ordem:** 1 (primeira task)
**Tipo:** Inicial

**Input Function:**
```python
def cadastrar_paciente_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "nome": state.get("nome", ""),
        "cpf": state.get("cpf", ""),
        "data_nascimento": state.get("data_nascimento", None),
        "contato": state.get("contato", ""),
        "convenio": state.get("convenio", ""),
        "historico": state.get("historico", ""),
        "status": state.get("status", ""),
        "consentimento": state.get("consentimento", False)
    }
```

**Input Schema:**
- **nome** (String): Nome completo do paciente — vem de: config inicial seção 2.1
- **cpf** (String): CPF do paciente — vem de: config inicial seção 2.1
- **data_nascimento** (Date): Data de nascimento do paciente — vem de: config inicial seção 2.1
- **contato** (String): Informações de contato do paciente — vem de: config inicial seção 2.1
- **convenio** (String): Convênio médico associado ao paciente — vem de: config inicial seção 2.1
- **historico** (Text): Histórico médico anterior — vem de: config inicial seção 2.1
- **status** (Enum (ativo/inativo)): Status atual do paciente — vem de: config inicial seção 2.1
- **consentimento** (Boolean): Indicador de consentimento para processamento de dados — vem de: config inicial seção 2.1

**Process Steps:**
1. INSERT: chame database_tool com query="INSERT INTO pacientes(nome, cpf, data_nascimento, contato, convenio) VALUES(%s, %s, %s, %s, %s)" params=[{nome}, {cpf}, {data_nascimento}, {contato}, {convenio}]
2. Capture o id UUID: chame database_tool com query="SELECT id FROM pacientes WHERE cpf=%s ORDER BY created_at DESC LIMIT 1" params=[{cpf}] Guarde em paciente_id (NUNCA use LAST_INSERT_ID()).
3. Se {consentimento} for True: chame database_tool com query="INSERT INTO consentimentos(paciente_id, data_hora, versao_termo) VALUES(%s, NOW(), 'v1')" params=[paciente_id]
4. Retorne paciente_id + status "sucesso".

**Output Function:**
```python
def cadastrar_paciente_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de cadastrar_paciente"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "cadastrar_paciente",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "cadastrar_paciente_json": output_json,
        "cadastrar_paciente_data": output_data,
        "execution_log": execution_log,
        "current_task": "cadastrar_paciente",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "paciente_id": "UUID capturado no passo 2",
  "status": "sucesso ou erro"
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- cadastrar_paciente_json (str)
- cadastrar_paciente_data (Dict)

**Campos do State Requeridos:**
- nome → origem: config inicial seção 2.1
- cpf → origem: config inicial seção 2.1
- data_nascimento → origem: config inicial seção 2.1
- contato → origem: config inicial seção 2.1
- convenio → origem: config inicial seção 2.1
- historico → origem: config inicial seção 2.1
- status → origem: config inicial seção 2.1
- consentimento → origem: config inicial seção 2.1

**Dependências:**
- Nenhuma (task inicial)

---

### Task 2: Atualizar Paciente

**ID:** T-002
**Agente:** recepcionista_agent (string, não objeto)
**Ordem:** 2
**Tipo:** Processamento

**Input Function:**
```python
def atualizar_paciente_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "nome": state.get("nome", ""),
        "cpf": state.get("cpf", ""),
        "data_nascimento": state.get("data_nascimento", None),
        "contato": state.get("contato", ""),
        "convenio": state.get("convenio", ""),
        "historico": state.get("historico", ""),
        "status": state.get("status", ""),
        "consentimento": state.get("consentimento", False)
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **nome** (String): Nome completo do paciente — vem de: config inicial seção 2.1
- **cpf** (String): CPF do paciente — vem de: config inicial seção 2.1
- **data_nascimento** (Date): Data de nascimento do paciente — vem de: config inicial seção 2.1
- **contato** (String): Informações de contato do paciente — vem de: config inicial seção 2.1
- **convenio** (String): Convênio médico associado ao paciente — vem de: config inicial seção 2.1
- **historico** (Text): Histórico médico anterior — vem de: config inicial seção 2.1
- **status** (Enum (ativo/inativo)): Status atual do paciente — vem de: config inicial seção 2.1
- **consentimento** (Boolean): Indicador de consentimento para processamento de dados — vem de: config inicial seção 2.1

**Process Steps:**
1. UPDATE: chame database_tool com query="UPDATE pacientes SET nome=%s, cpf=%s, data_nascimento=%s, contato=%s, convenio=%s, historico=%s, status=%s WHERE id=%s" params=[{nome}, {cpf}, {data_nascimento}, {contato}, {convenio}, {historico}, {status}, {paciente_id}]
2. Se {consentimento} for True: a. INSERT: chame database_tool com query="INSERT INTO consentimentos(paciente_id, data_hora, versao_termo) VALUES(%s, NOW(), 'v1')" params=[{paciente_id}]
3. Retorne paciente_id + status "sucesso".

**Output Function:**
```python
def atualizar_paciente_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de atualizar_paciente"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "atualizar_paciente",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "atualizar_paciente_json": output_json,
        "atualizar_paciente_data": output_data,
        "execution_log": execution_log,
        "current_task": "atualizar_paciente",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "paciente_id": "UUID do paciente armazenado",
  "status": "sucesso ou erro"
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- atualizar_paciente_json (str)
- atualizar_paciente_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- nome → origem: config inicial seção 2.1
- cpf → origem: config inicial seção 2.1
- data_nascimento → origem: config inicial seção 2.1
- contato → origem: config inicial seção 2.1
- convenio → origem: config inicial seção 2.1
- historico → origem: config inicial seção 2.1
- status → origem: config inicial seção 2.1
- consentimento → origem: config inicial seção 2.1

**Dependências:**
- T-001 (Cadastro de Pacientes)

---

### Task 3: Triagem Agentiva

**ID:** T-003
**Agente:** triagem_hub_agent (string, não objeto)
**Ordem:** 3
**Tipo:** Processamento

**Input Function:**
```python
def triagem_agentiva_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "queixa_inicial": state.get("queixa_inicial", ""),
        "sinais_vitais": state.get("sinais_vitais", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **queixa_inicial** (String): Queixa inicial do paciente — vem de: config inicial seção 2.1
- **sinais_vitais** (Text): Sinais vitais do paciente — vem de: config inicial seção 2.1

**Process Steps:**
1. Receber os dados de entrada (paciente_id, queixa_inicial, sinais_vitais).
2. Utilizar o embedding_tool para analisar a queixa_inicial e sinais_vitais.
3. Consultar o database_tool para obter informações adicionais sobre o paciente, se necessário.
4. Classificar a urgência do paciente em uma das categorias: verde, amarelo ou vermelho.
5. Determinar o agente especialista mais adequado com base na classificação de urgência.
6. Gerar uma justificativa para a classificação de urgência e a roteirização.

**Output Function:**
```python
def triagem_agentiva_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de triagem_agentiva"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "triagem_agentiva",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "triagem_agentiva_json": output_json,
        "triagem_agentiva_data": output_data,
        "execution_log": execution_log,
        "current_task": "triagem_agentiva",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "classificacao_urgencia": "Enum (verde/amarelo/vermelho)",
  "justificativa": "Text",
  "area_destino": "String"
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- triagem_agentiva_json (str)
- triagem_agentiva_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- queixa_inicial → origem: config inicial seção 2.1
- sinais_vitais → origem: config inicial seção 2.1

**Dependências:**
- T-001 (Cadastro de Pacientes)

---

### Task 4: Pré-atendimento Cardiologia

**ID:** T-004
**Agente:** especialista_cardiologia_agent (string, não objeto)
**Ordem:** 4a
**Tipo:** Processamento

**Input Function:**
```python
def pre_atendimento_cardiologia_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "queixa_inicial": state.get("queixa_inicial", ""),
        "sinais_vitais": state.get("sinais_vitais", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **queixa_inicial** (String): Queixa inicial do paciente — vem de: config inicial seção 2.1
- **sinais_vitais** (Text): Sinais vitais do paciente — vem de: config inicial seção 2.1

**Process Steps:**
1. Receber os dados de entrada do paciente.
2. Utilizar o embedding_tool para processar a queixa inicial e sinais vitais.
3. Consultar o database_tool para buscar histórico médico do paciente (SELECT * FROM historico_medico WHERE paciente_id = {paciente_id}).
4. Analisar os dados recebidos e compará-los com informações históricas do paciente.
5. Gerar hipóteses de diagnóstico baseado na análise.
6. Determinar o nível de confiança no pré-diagnóstico (baixa/média/alta).
7. Sugerir exames complementares, se necessário.

**Output Function:**
```python
def pre_atendimento_cardiologia_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de pre_atendimento_cardiologia"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "pre_atendimento_cardiologia",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "pre_atendimento_cardiologia_json": output_json,
        "pre_atendimento_cardiologia_data": output_data,
        "execution_log": execution_log,
        "current_task": "pre_atendimento_cardiologia",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "hipoteses": "JSON contendo as possíveis condições cardíacas que o paciente pode estar apresentando.",
  "nivel_confianca": "Enum indicando a confiabilidade do pré-diagnóstico (baixa/média/alta).",
  "exames_sugeridos": "Texto descrevendo os exames complementares recomendados para confirmar ou refutar as hipóteses."
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- pre_atendimento_cardiologia_json (str)
- pre_atendimento_cardiologia_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- queixa_inicial → origem: config inicial seção 2.1
- sinais_vitais → origem: config inicial seção 2.1

**Dependências:**
- T-003 (Triagem Agentiva)

---

### Task 5: Pré-atendimento Pediatria

**ID:** T-005
**Agente:** especialista_pediatria_agent (string, não objeto)
**Ordem:** 4b
**Tipo:** Processamento

**Input Function:**
```python
def pre_atendimento_pediatria_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "queixa_inicial": state.get("queixa_inicial", ""),
        "sinais_vitais": state.get("sinais_vitais", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **queixa_inicial** (String): Queixa inicial do paciente — vem de: config inicial seção 2.1
- **sinais_vitais** (Text): Sinais vitais do paciente — vem de: config inicial seção 2.1

**Process Steps:**
1. Receber os dados de entrada do paciente.
2. Utilizar o embedding_tool para processar a queixa inicial e sinais vitais.
3. Consultar o database_tool para buscar históricos médicos e condições similares.
4. Gerar hipóteses de diagnóstico baseado nos dados recebidos e na consulta ao banco.
5. Avaliar a confiança do pré-diagnóstico.
6. Sugerir exames complementares, se necessário.

**Output Function:**
```python
def pre_atendimento_pediatria_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de pre_atendimento_pediatria"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "pre_atendimento_pediatria",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "pre_atendimento_pediatria_json": output_json,
        "pre_atendimento_pediatria_data": output_data,
        "execution_log": execution_log,
        "current_task": "pre_atendimento_pediatria",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "hipoteses": "JSON",
  "nivel_confianca": "Enum (baixa/média/alta)",
  "exames_sugeridos": "Text"
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- pre_atendimento_pediatria_json (str)
- pre_atendimento_pediatria_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- queixa_inicial → origem: config inicial seção 2.1
- sinais_vitais → origem: config inicial seção 2.1

**Dependências:**
- T-003 (Triagem Agentiva)

---

### Task 6: Pré-atendimento Gastroenterologia

**ID:** T-006
**Agente:** especialista_gastroenterologia_agent (string, não objeto)
**Ordem:** 4c
**Tipo:** Processamento

**Input Function:**
```python
def pre_atendimento_gastroenterologia_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "queixa_inicial": state.get("queixa_inicial", ""),
        "sinais_vitais": state.get("sinais_vitais", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **queixa_inicial** (String): Queixa inicial do paciente — vem de: config inicial seção 2.1
- **sinais_vitais** (Text): Sinais vitais do paciente — vem de: config inicial seção 2.1

**Process Steps:**
1. Receber os dados de entrada do paciente.
2. Utilizar o embedding_tool para processar a queixa inicial e sinais vitais.
3. Consultar o database_tool para buscar histórico médico do paciente (SELECT).
4. Analisar os dados recebidos e compará-los com informações médicas relevantes.
5. Gerar hipóteses de diagnóstico baseado na análise.
6. Determinar o nível de confiança no pré-diagnóstico.
7. Sugerir exames complementares, se necessário.

**Output Function:**
```python
def pre_atendimento_gastroenterologia_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de pre_atendimento_gastroenterologia"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "pre_atendimento_gastroenterologia",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "pre_atendimento_gastroenterologia_json": output_json,
        "pre_atendimento_gastroenterologia_data": output_data,
        "execution_log": execution_log,
        "current_task": "pre_atendimento_gastroenterologia",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "hipoteses": "JSON contendo as possíveis condições médicas do paciente.",
  "nivel_confianca": "Enum (baixa/média/alta) indicando a confiabilidade do pré-diagnóstico.",
  "exames_sugeridos": "Text descrevendo os exames que devem ser realizados para confirmar o diagnóstico."
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- pre_atendimento_gastroenterologia_json (str)
- pre_atendimento_gastroenterologia_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- queixa_inicial → origem: config inicial seção 2.1
- sinais_vitais → origem: config inicial seção 2.1

**Dependências:**
- T-003 (Triagem Agentiva)

---

### Task 7: Criar Encaminhamento

**ID:** T-007
**Agente:** encaminhamento_agent (string, não objeto)
**Ordem:** 5
**Tipo:** Processamento

**Input Function:**
```python
def criar_encaminhamento_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "especialidade_id": state.get("especialidade_id", None),
        "hipoteses": state.get("pre_atendimento_cardiologia_data", {}).get("hipoteses", {}) or \
                     state.get("pre_atendimento_pediatria_data", {}).get("hipoteses", {}) or \
                     state.get("pre_atendimento_gastroenterologia_data", {}).get("hipoteses", {}),
        "nivel_confianca": state.get("pre_atendimento_cardiologia_data", {}).get("nivel_confianca", "") or \
                         state.get("pre_atendimento_pediatria_data", {}).get("nivel_confianca", "") or \
                         state.get("pre_atendimento_gastroenterologia_data", {}).get("nivel_confianca", ""),
        "exames_sugeridos": state.get("pre_atendimento_cardiologia_data", {}).get("exames_sugeridos", "") or \
                            state.get("pre_atendimento_pediatria_data", {}).get("exames_sugeridos", "") or \
                            state.get("pre_atendimento_gastroenterologia_data", {}).get("exames_sugeridos", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **especialidade_id** (UUID): ID da especialidade médica — vem de: T-003 output
- **hipoteses** (JSON): Hipóteses de diagnóstico — vem de: T-004, T-005 ou T-006 output
- **nivel_confianca** (Enum): Nível de confiança do pré-diagnóstico — vem de: T-004, T-005 ou T-006 output
- **exames_sugeridos** (Text): Exames sugeridos — vem de: T-004, T-005 ou T-006 output

**Process Steps:**
1. Selecionar médico disponível na especialidade: chame database_tool com
   query="SELECT id FROM medicos WHERE especialidade_id=%s ORDER BY created_at ASC LIMIT 1"
   params=[{especialidade_id}]
   Guarde em medico_id.
2. Obter atendimento_id do prontuário do paciente: chame database_tool com
   query="SELECT atendimento_id FROM prontuarios WHERE paciente_id=%s ORDER BY created_at DESC LIMIT 1"
   params=[{paciente_id}]
   Guarde em atendimento_id.
3. INSERT encaminhamento: chame database_tool com
   query="INSERT INTO encaminhamentos(atendimento_id, especialidade_id, medico_id, prioridade) VALUES(%s, %s, %s, 'normal')"
   params=[atendimento_id, {especialidade_id}, medico_id]
4. Capture o id UUID: chame database_tool com
   query="SELECT id FROM encaminhamentos WHERE atendimento_id=%s AND especialidade_id=%s ORDER BY created_at DESC LIMIT 1"
   params=[atendimento_id, {especialidade_id}]
   Guarde em encaminhamento_id (NUNCA use LAST_INSERT_ID()).
5. Atualizar prontuário com o encaminhamento_id: chame database_tool com
   query="UPDATE prontuarios SET encaminhamento_id=%s WHERE atendimento_id=%s"
   params=[encaminhamento_id, atendimento_id]
6. Retorne encaminhamento_id + status "sucesso".

**Output Function:**
```python
def criar_encaminhamento_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de criar_encaminhamento"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "criar_encaminhamento",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "criar_encaminhamento_json": output_json,
        "criar_encaminhamento_data": output_data,
        "execution_log": execution_log,
        "current_task": "criar_encaminhamento",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "encaminhamento_id": "UUID capturado no passo 4",
  "status": "String (sucesso ou erro)"
}
```

**Tools Necessárias:**
- database_tool

**Campos do State Produzidos:**
- criar_encaminhamento_json (str)
- criar_encaminhamento_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- especialidade_id → origem: T-003 output
- hipoteses → origem: T-004, T-005 ou T-006 output
- nivel_confianca → origem: T-004, T-005 ou T-006 output
- exames_sugeridos → origem: T-004, T-005 ou T-006 output

**Dependências:**
- T-003 (Triagem Agentiva)
- T-004 (Pré-atendimento Cardiologia) / T-005 (Pré-atendimento Pediatria) / T-006 (Pré-atendimento Gastroenterologia)

---

### Task 8: Registrar Prontuário

**ID:** T-008
**Agente:** registro_prontuario_agent (string, não objeto)
**Ordem:** 6
**Tipo:** Processamento

**Input Function:**
```python
def registrar_prontuario_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "atendimento_id": state.get("criar_encaminhamento_data", {}).get("atendimento_id", None),
        "triagem": state.get("triagem_agentiva_json", ""),
        "pre_diagnostico_id": state.get("pre_atendimento_cardiologia_data", {}).get("id", "") or \
                              state.get("pre_atendimento_pediatria_data", {}).get("id", "") or \
                              state.get("pre_atendimento_gastroenterologia_data", {}).get("id", ""),
        "encaminhamento_id": state.get("criar_encaminhamento_data", {}).get("encaminhamento_id", None),
        "resumo_medico": state.get("consulta_medica_json", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **atendimento_id** (UUID): ID do atendimento — vem de: T-007 output
- **triagem** (Text): Informações da triagem — vem de: T-003 output
- **pre_diagnostico_id** (UUID): ID do pré-diagnóstico — vem de: T-004, T-005 ou T-006 output
- **encaminhamento_id** (UUID): ID do encaminhamento — vem de: T-007 output
- **resumo_medico** (Text): Resumo médico — vem de: T-009 output

**Process Steps:**
1. INSERT: chame database_tool com
   query="INSERT INTO prontuarios(paciente_id, atendimento_id, triagem, pre_diagnostico_id, encaminhamento_id, resumo_medico) VALUES(%s, %s, %s, %s, %s, %s)"
   params=[{paciente_id}, {atendimento_id}, {triagem}, {pre_diagnostico_id}, {encaminhamento_id}, {resumo_medico}]
2. Capture o id UUID: chame database_tool com
   query="SELECT id FROM prontuarios WHERE paciente_id=%s AND atendimento_id=%s ORDER BY created_at DESC LIMIT 1"
   params=[{paciente_id}, {atendimento_id}]
   Guarde em prontuario_id (NUNCA use LAST_INSERT_ID()).
3. Retorne prontuario_id + status "sucesso".

**Output Function:**
```python
def registrar_prontuario_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de registrar_prontuario"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "registrar_prontuario",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "registrar_prontuario_json": output_json,
        "registrar_prontuario_data": output_data,
        "execution_log": execution_log,
        "current_task": "registrar_prontuario",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "prontuario_id": "UUID capturado no passo 2",
  "status": "String (sucesso ou erro)"
}
```

**Tools Necessárias:**
- database_tool

**Campos do State Produzidos:**
- registrar_prontuario_json (str)
- registrar_prontuario_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- atendimento_id → origem: T-007 output
- triagem → origem: T-003 output
- pre_diagnostico_id → origem: T-004, T-005 ou T-006 output
- encaminhamento_id → origem: T-007 output
- resumo_medico → origem: T-009 output

**Dependências:**
- T-001 (Cadastro de Pacientes)
- T-003 (Triagem Agentiva)
- T-004 (Pré-atendimento Cardiologia) / T-005 (Pré-atendimento Pediatria) / T-006 (Pré-atendimento Gastroenterologia)
- T-007 (Criar Encaminhamento)
- T-009 (Consulta Médica)

---

### Task 9: Consulta Médica

**ID:** T-009
**Agente:** medico_agent (string, não objeto)
**Ordem:** 7
**Tipo:** Processamento

**Input Function:**
```python
def consulta_medica_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", None),
        "atendimento_id": state.get("criar_encaminhamento_data", {}).get("atendimento_id", None),
        "hipoteses": state.get("pre_atendimento_cardiologia_data", {}).get("hipoteses", {}) or \
                     state.get("pre_atendimento_pediatria_data", {}).get("hipoteses", {}) or \
                     state.get("pre_atendimento_gastroenterologia_data", {}).get("hipoteses", {}),
        "nivel_confianca": state.get("pre_atendimento_cardiologia_data", {}).get("nivel_confianca", "") or \
                         state.get("pre_atendimento_pediatria_data", {}).get("nivel_confianca", "") or \
                         state.get("pre_atendimento_gastroenterologia_data", {}).get("nivel_confianca", ""),
        "exames_sugeridos": state.get("pre_atendimento_cardiologia_data", {}).get("exames_sugeridos", "") or \
                            state.get("pre_atendimento_pediatria_data", {}).get("exames_sugeridos", "") or \
                            state.get("pre_atendimento_gastroenterologia_data", {}).get("exames_sugeridos", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: T-001 output
- **atendimento_id** (UUID): ID do atendimento — vem de: T-007 output
- **hipoteses** (JSON): Hipóteses de diagnóstico — vem de: T-004, T-005 ou T-006 output
- **nivel_confianca** (Enum): Nível de confiança do pré-diagnóstico — vem de: T-004, T-005 ou T-006 output
- **exames_sugeridos** (Text): Exames sugeridos — vem de: T-004, T-005 ou T-006 output

**Process Steps:**
1. Consultar o banco de dados para obter informações detalhadas do paciente e do atendimento usando database_tool.
2. Analisar as hipóteses fornecidas e validar ou refutar com base nas informações obtidas.
3. Utilizar embedding_tool para comparar os sintomas e exames sugeridos com a literatura médica.
4. Formular o diagnóstico final, conduta e prescrição.

**Output Function:**
```python
def consulta_medica_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de consulta_medica"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "consulta_medica",
        "timestamp": datetime.now().isoformat(),
       0 "status": "completed"
    })

    return {
        **state,
        "consulta_medica_json": output_json,
        "consulta_medica_data": output_data,
        "execution_log": execution_log,
        "current_task": "consulta_medica",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "diagnostico_final": "String",
  "conduta": "String",
  "prescricao": "String"
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- consulta_medica_json (str)
- consulta_medica_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: T-001 output
- atendimento_id → origem: T-007 output
- hipoteses → origem: T-004, T-005 ou T-006 output
- nivel_confianca → origem: T-004, T-005 ou T-006 output
- exames_sugeridos → origem: T-004, T-005 ou T-006 output

**Dependências:**
- T-001 (Cadastro de Pacientes)
- T-003 (Triagem Agentiva)
- T-004 (Pré-atendimento Cardiologia) / T-005 (Pré-atendimento Pediatria) / T-006 (Pré-atendimento Gastroenterologia)
- T-007 (Criar Encaminhamento)

---

### Task 10: Gerir Administrador

**ID:** T-010
**Agente:** administrador_agent (string, não objeto)
**Ordem:** 8
**Tipo:** Processamento

**Input Function:**
```python
def gerir_administrador_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "acao": state.get("acao", ""),
        "tipo_registro": state.get("tipo_registro", ""),
        "dados": state.get("dados", {})
    }
```

**Input Schema:**
- **acao** (Enum): Ação a ser realizada (cadastrar/atualizar/excluir) — vem de: entrada externa
- **tipo_registro** (Enum): Tipo de registro a ser gerenciado (medicos/especialidades/agentes/agendas/usuarios) — vem de: entrada externa
- **dados** (JSON): Dados para operação — vem de: entrada externa

**Process Steps:**
1. Validar os campos de entrada para garantir que ação e tipo_registro estejam corretos.
2. Converter o campo 'dados' em um formato adequado para interação com o banco de dados.
3. Utilizar o database_tool para realizar as operações necessárias no banco de dados (SELECT, INSERT, UPDATE ou DELETE) conforme a ação solicitada e tipo de registro.
4. Retornar o status da operação como sucesso ou falha.

**Output Function:**
```python
def gerir_administrador_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de gerir_administrador"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "gerir_administrador",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "gerir_administrador_json": output_json,
        "gerir_administrador_data": output_data,
        "execution_log": execution_log,
        "current_task": "gerir_administrador",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "status": "String (sucesso/falha)"
}
```

**Tools Necessárias:**
- database_tool

**Campos do State Produzidos:**
- gerir_administrador_json (str)
- gerir_administrador_data (Dict)

**Campos do State Requeridos:**
- acao → origem: entrada externa
- tipo_registro → origem: entrada externa
- dados → origem: entrada externa

**Dependências:**
- Nenhuma

---

### Task 11: Fallback Manual

**ID:** T-011
**Agente:** fallback_agent (string, não objeto)
**Ordem:** 9
**Tipo:** Processamento

**Input Function:**
```python
def fallback_manual_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "paciente_id": state.get("paciente_id", ""),
        "atendimento_id": state.get("atendimento_id", ""),
        "justificativa": state.get("justificativa", "")
    }
```

**Input Schema:**
- **paciente_id** (UUID): Identificador único do paciente — vem de: entrada externa
- **atendimento_id** (UUID): Identificador único do atendimento — vem de: entrada externa
- **justificativa** (Text): Justificativa para fallback — vem de: entrada externa

**Process Steps:**
1. Registrar a ocorrência do erro no banco de dados usando database_tool.
2. Gerar um embedding da justificativa utilizando embedding_tool.
3. Atualizar o status do atendimento para 'pendente' no banco de dados.

**Output Function:**
```python
def fallback_manual_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de fallback_manual"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "fallback_manual",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    })

    return {
        **state,
        "fallback_manual_json": output_json,
        "fallback_manual_data": output_data,
        "execution_log": execution_log,
        "current_task": "fallback_manual",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "status": "String (sucesso/falha)"
}
```

**Tools Necessárias:**
- database_tool
- embedding_tool

**Campos do State Produzidos:**
- fallback_manual_json (str)
- fallback_manual_data (Dict)

**Campos do State Requeridos:**
- paciente_id → origem: entrada externa
- atendimento_id → origem: entrada externa
- justificativa → origem: entrada externa

**Dependências:**
- Nenhuma

---

### Task 12: Visualizar KPIs

**ID:** T-012
**Agente:** kpi_dashboard_agent (string, não objeto)
**Ordem:** 10
**Tipo:** Processamento

**Input Function:**
```python
def visualizar_kpis_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai campos necessários do state"""
    return {
        "periodo": state.get("periodo", ""),
        "metricas_selecionadas": state.get("metricas_selecionadas", [])
    }
```

**Input Schema:**
- **periodo** (Enum): Período para visualização de KPIs (diario/semanal/mensal) — vem de: entrada externa
- **metricas_selecionadas** (List[String]): Métricas a serem selecionadas — vem de: entrada externa

**Process Steps:**
1. Receber os parâmetros de entrada: {periodo} e {metricas_selecionadas}.
2. Utilizar o database_tool para consultar as métricas selecionadas no banco de dados conforme o período especificado.
3. Formatar os resultados em um JSON estruturado.

**Output Function:**
```python
def visualizar_kpis_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado de visualizar_kpis"""
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {"error": "Failed to parse output