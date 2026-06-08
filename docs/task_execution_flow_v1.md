# Fluxo de Execução de Tarefas - Sistema de Análise de Editais e Geração de Petições

## 1. Visão Geral

- **Total de Tasks:** 27
- **Total de Agentes:** 14
- **Tipo de Fluxo:** Misto (Linear com paralelismo em subfluxos)
- **Modelo de State:** Acumulativo (LangGraph-style)

## 2. Definição do State (TypedDict)

### 2.1 Campos de Configuração Inicial
| Campo | Tipo | Descrição | Valor Padrão |
|-------|------|-----------|--------------|
| classification_rules | Dict[str, Any] | Regras para classificação de gravidade | {} |
| portal_config | Dict[str, Any] | Configuração do portal governamental | {} |
| dispute_config | Dict[str, Any] | Configuração da disputa | {} |
| process_metadata | Dict[str, Any] | Metadados do processo licitatório | {} |
| user_preferences | Dict[str, Any] | Preferências do usuário | {} |
| template_type | str | Tipo de template de petição | "" |

### 2.2 Campos de Output das Tasks
| Campo | Tipo | Produzido Por | Consumido Por |
|-------|------|---------------|---------------|
| edital_extraction_json | str | T-ANA-001 | T-ANA-002, T-ANA-003, T-ANA-004 |
| edital_extraction_data | Dict[str, Any] | T-ANA-001 | T-ANA-002, T-ANA-003, T-ANA-004 |
| laws_identification_json | str | T-ANA-002 | T-ANA-003 |
| laws_identification_data | Dict[str, Any] | T-ANA-002 | T-ANA-003 |
| comparison_report_json | str | T-ANA-003 | T-ANA-004 |
| comparison_report_data | Dict[str, Any] | T-ANA-003 | T-ANA-004 |
| inconsistencies_json | str | T-ANA-004 | T-ANA-005 |
| inconsistencies_data | Dict[str, Any] | T-ANA-004 | T-ANA-005 |
| classified_inconsistencies_json | str | T-ANA-005 | T-ANA-006, T-PRO-001 |
| classified_inconsistencies_data | Dict[str, Any] | T-ANA-005 | T-ANA-006, T-PRO-001 |
| suggestions_json | str | T-ANA-006 | T-GER-001 |
| suggestions_data | Dict[str, Any] | T-ANA-006 | T-GER-001 |
| petition_draft_json | str | T-GER-001 | T-GER-002 |
| petition_draft_data | Dict[str, Any] | T-GER-001 | T-GER-002 |
| templated_draft_json | str | T-GER-002 | T-EDI-001 |
| templated_draft_data | Dict[str, Any] | T-GER-002 | T-EDI-001 |
| edited_document_json | str | T-EDI-001 | T-EDI-002, T-SUB-001 |
| edited_document_data | Dict[str, Any] | T-EDI-001 | T-EDI-002, T-SUB-001 |
| change_log_json | str | T-EDI-002 | - |
| change_log_data | Dict[str, Any] | T-EDI-002 | - |
| portal_status_json | str | T-MON-001 | T-MON-002 |
| portal_status_data | Dict[str, Any] | T-MON-001 | T-MON-002 |
| status_change_json | str | T-MON-002 | T-NOT-001 |
| status_change_data | Dict[str, Any] | T-MON-002 | T-NOT-001 |
| notifications_json | str | T-NOT-001 | - |
| notifications_data | Dict[str, Any] | T-NOT-001 | - |
| proposal_analysis_json | str | T-PRO-001 | T-PRO-002, T-PRO-003, T-ASS-001 |
| proposal_analysis_data | Dict[str, Any] | T-PRO-001 | T-PRO-002, T-PRO-003, T-ASS-001 |
| checklist_json | str | T-PRO-002 | - |
| checklist_data | Dict[str, Any] | T-PRO-002 | - |
| motivations_json | str | T-PRO-003 | T-GER-001 |
| motivations_data | Dict[str, Any] | T-PRO-003 | T-GER-001 |
| legal_assistance_json | str | T-ASS-001 | - |
| legal_assistance_data | Dict[str, Any] | T-ASS-001 | - |
| submission_prep_json | str | T-SUB-001 | T-SUB-002 |
| submission_prep_data | Dict[str, Any] | T-SUB-001 | T-SUB-002 |
| submission_result_json | str | T-SUB-002 | - |
| submission_result_data | Dict[str, Any] | T-SUB-002 | - |
| dispute_state_json | str | T-DIS-001 | T-DIS-002 |
| dispute_state_data | Dict[str, Any] | T-DIS-001 | T-DIS-002 |
| dispute_result_json | str | T-DIS-002 | - |
| dispute_result_data | Dict[str, Any] | T-DIS-002 | - |
| user_management_json | str | T-USU-001 | T-USU-002 |
| user_management_data | Dict[str, Any] | T-USU-001 | T-USU-002 |
| mfa_config_json | str | T-USU-002 | - |
| mfa_config_data | Dict[str, Any] | T-USU-002 | - |
| template_management_json | str | T-CON-001 | - |
| template_management_data | Dict[str, Any] | T-CON-001 | - |
| rules_config_json | str | T-CON-002 | - |
| rules_config_data | Dict[str, Any] | T-CON-002 | - |
| audit_report_json | str | T-SEG-001 | - |
| audit_report_data | Dict[str, Any] | T-SEG-001 | - |
| gdpr_compliance_json | str | T-SEG-002 | - |
| gdpr_compliance_data | Dict[str, Any] | T-SEG-002 | - |

### 2.3 Campos de Metadados
| Campo | Tipo | Descrição |
|-------|------|-----------|
| execution_log | List[Dict[str, Any]] | Log de execução |
| current_task | str | Task em execução |
| timestamp | str | Timestamp ISO |
| process_id | str | ID do processo licitatório |
| user_id | str | ID do usuário atual |
| workflow_type | str | Tipo de workflow (impugnacao, recurso, etc.) |

## 3. Sequência de Execução

### Task 1: upload_extract_edital

**ID:** T-001
**Agente:** AG-01 (edital_processor_agent)
**Ordem:** 1 (primeira task)
**Tipo:** Inicial (sem dependências)

**Input Function:**
```python
def upload_extract_edital_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "edital_file": state.get("edital_file"),
        "processo_numero": state.get("process_metadata", {}).get("numero_processo", ""),
        "orgao": state.get("process_metadata", {}).get("orgao", "")
    }
```

**Input Schema:**
- **edital_file** (File): Arquivo do edital (PDF/DOC/DOCX)
- **processo_numero** (str): Número do processo (opcional)
- **orgao** (str): Órgão licitante (opcional)

**Process Steps:**
1. Receber o arquivo do edital e as informações opcionais de número do processo e órgão
2. Utilizar as ferramentas pdf_reader, docx_reader e text_extraction_tool para extrair o texto completo do arquivo
3. Analisar o texto extraído para estruturar os metadados básicos: número do processo, órgão, data de publicação e objeto
4. Gerar um ID único (UUID) para o documento processado

**Output Function:**
```python
def upload_extract_edital_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "upload_extract_edital",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "document_id": output_data.get("document_id")
    })

    return {
        **state,
        "edital_extraction_json": output_json,
        "edital_extraction_data": output_data,
        "execution_log": execution_log,
        "current_task": "upload_extract_edital",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "extracted_text": "Texto completo extraído do edital...",
  "metadata": {
    "numero_processo": "12345/2024",
    "orgao": "Secretaria Municipal de Obras",
    "data_publicacao": "2024-03-24",
    "objeto": "Construção de escola municipal"
  },
  "document_id": "uuid-gerado-aqui"
}
```

**Tools Necessárias:**
- pdf_reader
- docx_reader
- text_extraction_tool

**Campos do State Produzidos:**
- edital_extraction_json
- edital_extraction_data

**Campos do State Requeridos:**
- edital_file
- process_metadata

**Dependências:**
- Nenhuma (task inicial)

---

### Task 2: identify_applicable_laws

**ID:** T-002
**Agente:** AG-02 (legal_analyzer_agent)
**Ordem:** 2
**Tipo:** Processamento

**Input Function:**
```python
def identify_applicable_laws_input_func(state: ProjectState) -> Dict[str, Any]:
    edital_data = state.get("edital_extraction_data", {})
    return {
        "extracted_text": edital_data.get("extracted_text", ""),
        "metadata": edital_data.get("metadata", {})
    }
```

**Input Schema:**
- **extracted_text** (str): Texto extraído do edital
- **metadata** (Dict): Metadados do edital (numero_processo, orgao, data_publicacao, objeto)

**Process Steps:**
1. Analisar o extracted_text para identificar citações explícitas de leis, decretos, portarias e normas técnicas
2. Utilizar as ferramentas vector_search_tool, legal_database_tool e pattern_matcher_tool para buscar e validar as referências legais
3. Estruturar a lista de leis aplicáveis com referência, descrição e tipo
4. Criar um mapeamento que associa trechos do edital às leis identificadas

**Output Function:**
```python
def identify_applicable_laws_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "identify_applicable_laws",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "laws_count": len(output_data.get("laws_list", []))
    })

    return {
        **state,
        "laws_identification_json": output_json,
        "laws_identification_data": output_data,
        "execution_log": execution_log,
        "current_task": "identify_applicable_laws",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "laws_list": [
    {
      "referencia": "Lei nº 14.133/2021",
      "descricao": "Lei de Licitações e Contratos Administrativos",
      "tipo": "lei"
    },
    {
      "referencia": "Decreto nº 11.598/2023",
      "descricao": "Regulamenta a Lei de Licitações",
      "tipo": "decreto"
    }
  ],
  "mapping": {
    "clausula_5.2": "Lei nº 14.133/2021, Artigo 5º"
  }
}
```

**Tools Necessárias:**
- vector_search_tool
- legal_database_tool
- pattern_matcher_tool

**Campos do State Produzidos:**
- laws_identification_json
- laws_identification_data

**Campos do State Requeridos:**
- edital_extraction_data

**Dependências:**
- T-001 (upload_extract_edital)

---

### Task 3: compare_edital_laws

**ID:** T-003
**Agente:** AG-02 (legal_analyzer_agent)
**Ordem:** 3
**Tipo:** Processamento

**Input Function:**
```python
def compare_edital_laws_input_func(state: ProjectState) -> Dict[str, Any]:
    edital_data = state.get("edital_extraction_data", {})
    laws_data = state.get("laws_identification_data", {})
    return {
        "extracted_text": edital_data.get("extracted_text", ""),
        "laws_list": laws_data.get("laws_list", []),
        "mapping": laws_data.get("mapping", {})
    }
```

**Input Schema:**
- **extracted_text** (str): Texto extraído do edital
- **laws_list** (List[Dict]): Lista de leis aplicáveis
- **mapping** (Dict): Mapeamento entre trechos do edital e leis

**Process Steps:**
1. Segmentar o texto do edital em cláusulas ou seções logicamente coerentes
2. Para cada cláusula do edital, comparar semanticamente com o texto das leis relevantes (com base no mapping)
3. Utilizar as ferramentas semantic_comparison_tool, embedding_tool e similarity_calculator_tool para calcular scores de similaridade e identificar correspondências
4. Identificar potenciais conflitos onde o texto do edital diverge significativamente da lei

**Output Function:**
```python
def compare_edital_laws_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "compare_edital_laws",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "potential_issues": len(output_data.get("potential_issues", []))
    })

    return {
        **state,
        "comparison_report_json": output_json,
        "comparison_report_data": output_data,
        "execution_log": execution_log,
        "current_task": "compare_edital_laws",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "comparison_report": {
    "clausulas_comparadas": 15,
    "similarity_threshold": 0.8
  },
  "potential_issues": [
    {
      "clausula_edital": "Cláusula 5.2 - Exigência de certificação ISO 9001",
      "lei_referenciada": "Lei nº 14.133/2021, Artigo 4º, §2º",
      "tipo_divergencia": "Exigência discriminatória",
      "similarity_score": 0.3
    }
  ],
  "similarity_scores": {
    "clausula_5.2": 0.3,
    "item_7.1.3": 0.9
  }
}
```

**Tools Necessárias:**
- semantic_comparison_tool
- embedding_tool
- similarity_calculator_tool

**Campos do State Produzidos:**
- comparison_report_json
- comparison_report_data

**Campos do State Requeridos:**
- edital_extraction_data
- laws_identification_data

**Dependências:**
- T-002 (identify_applicable_laws)

---

### Task 4: detect_legal_inconsistencies

**ID:** T-004
**Agente:** AG-03 (inconsistency_detector_agent)
**Ordem:** 4
**Tipo:** Processamento

**Input Function:**
```python
def detect_legal_inconsistencies_input_func(state: ProjectState) -> Dict[str, Any]:
    comparison_data = state.get("comparison_report_data", {})
    edital_data = state.get("edital_extraction_data", {})
    laws_data = state.get("laws_identification_data", {})
    return {
        "comparison_report": comparison_data.get("comparison_report", {}),
        "potential_issues": comparison_data.get("potential_issues", []),
        "similarity_scores": comparison_data.get("similarity_scores", {}),
        "extracted_text": edital_data.get("extracted_text", ""),
        "laws_list": laws_data.get("laws_list", [])
    }
```

**Input Schema:**
- **comparison_report** (Dict): Relatório de comparação
- **potential_issues** (List): Lista de potenciais conflitos
- **similarity_scores** (Dict): Scores de similaridade
- **extracted_text** (str): Texto extraído do edital
- **laws_list** (List): Lista de leis aplicáveis

**Process Steps:**
1. Analisar os potential_issues e similarity_scores para confirmar inconsistências reais
2. Utilizar as ferramentas inconsistency_detector_tool, legal_validator_tool e rule_engine_tool para validar as inconsistências contra regras legais pré-definidas
3. Classificar cada inconsistência detectada com uma descrição clara, indicando a cláusula do edital, a norma violada e o tipo de violação
4. Gerar um resumo da detecção

**Output Function:**
```python
def detect_legal_inconsistencies_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "detect_legal_inconsistencies",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "inconsistencies_count": len(output_data.get("inconsistencies", []))
    })

    return {
        **state,
        "inconsistencies_json": output_json,
        "inconsistencies_data": output_data,
        "execution_log": execution_log,
        "current_task": "detect_legal_inconsistencies",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "inconsistencies": [
    {
      "descricao": "Exigência de certificação ISO 9001 é discriminatória e não prevista em lei",
      "clausula_edital": "Cláusula 5.2",
      "norma": "Lei nº 14.133/2021, Artigo 4º, §2º",
      "tipo_violacao": "formal"
    }
  ],
  "detection_summary": {
    "total_inconsistencies": 8,
    "violacoes_formais": 3,
    "violacoes_materiais": 5
  }
}
```

**Tools Necessárias:**
- inconsistency_detector_tool
- legal_validator_tool
- rule_engine_tool

**Campos do State Produzidos:**
- inconsistencies_json
- inconsistencies_data

**Campos do State Requeridos:**
- comparison_report_data
- edital_extraction_data
- laws_identification_data

**Dependências:**
- T-003 (compare_edital_laws)

---

### Task 5: classify_inconsistency_severity

**ID:** T-005
**Agente:** AG-03 (inconsistency_detector_agent)
**Ordem:** 5
**Tipo:** Processamento

**Input Function:**
```python
def classify_inconsistency_severity_input_func(state: ProjectState) -> Dict[str, Any]:
    inconsistencies_data = state.get("inconsistencies_data", {})
    return {
        "inconsistencies": inconsistencies_data.get("inconsistencies", []),
        "detection_summary": inconsistencies_data.get("detection_summary", {}),
        "classification_rules": state.get("classification_rules", {})
    }
```

**Input Schema:**
- **inconsistencies** (List): Lista de inconsistências detectadas
- **detection_summary** (Dict): Resumo da detecção
- **classification_rules** (Dict): Regras parametrizáveis para classificação de gravidade

**Process Steps:**
1. Carregar as regras de classificação de gravidade a partir do parâmetro classification_rules
2. Para cada inconsistência na lista, aplicar as regras para determinar o nível de gravidade (Alta, Média, Baixa)
3. Utilizar as ferramentas classification_tool, severity_rules_tool e pattern_analyzer_tool para auxiliar na classificação
4. Estruturar as inconsistências classificadas e gerar um resumo por nível de gravidade

**Output Function:**
```python
def classify_inconsistency_severity_output_func(state: ProjectState, result: Any) -> ProjectState:
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
    severity_summary = output_data.get("severity_summary", {})
    execution_log.append({
        "task": "classify_inconsistency_severity",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "alta_count": severity_summary.get("alta", 0),
        "media_count": severity_summary.get("media", 0),
        "baixa_count": severity_summary.get("baixa", 0)
    })

    return {
        **state,
        "classified_inconsistencies_json": output_json,
        "classified_inconsistencies_data": output_data,
        "execution_log": execution_log,
        "current_task": "classify_inconsistency_severity",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "classified_inconsistencies": [
    {
      "descricao": "Exigência de certificação ISO 9001 é discriminatória...",
      "clausula_edital": "Cláusula 5.2",
      "norma": "Lei nº 14.133/2021, Artigo 4º, §2º",
      "tipo_violacao": "formal",
      "gravidade": "Alta"
    }
  ],
  "severity_summary": {
    "alta": 3,
    "media": 4,
    "baixa": 1,
    "total": 8
  }
}
```

**Tools Necessárias:**
- classification_tool
- severity_rules_tool
- pattern_analyzer_tool

**Campos do State Produzidos:**
- classified_inconsistencies_json
- classified_inconsistencies_data

**Campos do State Requeridos:**
- inconsistencies_data
- classification_rules

**Dependências:**
- T-004 (detect_legal_inconsistencies)

---

### Task 6: suggest_petition_type

**ID:** T-006
**Agente:** AG-03 (inconsistency_detector_agent)
**Ordem:** 6
**Tipo:** Processamento

**Input Function:**
```python
def suggest_petition_type_input_func(state: ProjectState) -> Dict[str, Any]:
    classified_data = state.get("classified_inconsistencies_data", {})
    return {
        "classified_inconsistencies": classified_data.get("classified_inconsistencies", []),
        "severity_summary": classified_data.get("severity_summary", {}),
        "process_metadata": state.get("process_metadata", {})
    }
```

**Input Schema:**
- **classified_inconsistencies** (List): Lista de inconsistências classificadas por gravidade
- **severity_summary** (Dict): Resumo de gravidades
- **process_metadata** (Dict): Metadados do processo licitatório

**Process Steps:**
1. Analisar as inconsistências classificadas, considerando sua gravidade e o contexto do processo (process_metadata)
2. Utilizar as ferramentas suggestion_engine_tool, business_rules_tool e decision_tree_tool para determinar a sugestão mais adequada para cada inconsistência
3. Para cada inconsistência, sugerir o tipo de petição (Pedido de Esclarecimento ou Pedido de Impugnação) com uma justificativa
4. Gerar uma recomendação geral para o processo como um todo

**Output Function:**
```python
def suggest_petition_type_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "suggest_petition_type",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "suggestions_count": len(output_data.get("suggestions", []))
    })

    return {
        **state,
        "suggestions_json": output_json,
        "suggestions_data": output_data,
        "execution_log": execution_log,
        "current_task": "suggest_petition_type",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "suggestions": [
    {
      "inconsistency_id": 0,
      "suggested_type": "Pedido de Impugnação",
      "justification": "Inconsistência de gravidade Alta que viola princípio da isonomia"
    }
  ],
  "overall_recommendation": "Recomenda-se impugnação do edital devido a 3 inconsistências de gravidade Alta"
}
```

**Tools Necessárias:**
- suggestion_engine_tool
- business_rules_tool
- decision_tree_tool

**Campos do State Produzidos:**
- suggestions_json
- suggestions_data

**Campos do State Requeridos:**
- classified_inconsistencies_data
- process_metadata

**Dependências:**
- T-005 (classify_inconsistency_severity)

---

### Task 7: generate_petition_auto

**ID:** T-007
**Agente:** AG-04 (petition_generator_agent)
**Ordem:** 7
**Tipo:** Processamento

**Input Function:**
```python
def generate_petition_auto_input_func(state: ProjectState) -> Dict[str, Any]:
    suggestions_data = state.get("suggestions_data", {})
    classified_data = state.get("classified_inconsistencies_data", {})
    motivations_data = state.get("motivations_data", {})
    
    return {
        "suggestions": suggestions_data.get("suggestions", []),
        "overall_recommendation": suggestions_data.get("overall_recommendation", ""),
        "classified_inconsistencies": classified_data.get("classified_inconsistencies", []),
        "template_type": state.get("template_type", "impugnacao"),
        "process_metadata": state.get("process_metadata", {}),
        "suggested_motivations": motivations_data.get("suggested_motivations", []) if motivations_data else []
    }
```

**Input Schema:**
- **suggestions** (List): Lista de sugestões de tipo de petição por inconsistência
- **overall_recommendation** (str): Recomendação geral
- **classified_inconsistencies** (List): Lista de inconsistências classificadas
- **template_type** (str): Tipo de template a ser usado (impugnacao, recurso, contrarrazoes)
- **process_metadata** (Dict): Metadados do processo para preenchimento do template
- **suggested_motivations** (List): Sugestões de motivações para recurso (opcional)

**Process Steps:**
1. Selecionar o template padrão correspondente ao template_type fornecido
2. Preencher o template com os dados do process_metadata e com as inconsistências classificadas, seguindo as sugestões
3. Utilizar as ferramentas template_engine_tool, content_generator_tool e structure_validator_tool para gerar e validar o rascunho da petição
4. Estruturar o documento completo e registrar metadados da geração

**Output Function:**
```python
def generate_petition_auto_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "generate_petition_auto",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "template_type": state.get("template_type", "impugnacao")
    })

    return {
        **state,
        "petition_draft_json": output_json,
        "petition_draft_data": output_data,
        "execution_log": execution_log,
        "current_task": "generate_petition_auto",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "petition_draft": "EXCELENTÍSSIMO(A) SENHOR(A) PREGOEIRO(A)...",
  "sections_generated": {
    "cabecalho": true,
    "identificacao_partes": true,
    "fatos": true,
    "juridica": true,
    "tecnica": true,
    "pedido": true,
    "conclusao": true
  },
  "generation_metadata": {
    "template_used": "Modelo_Impugnacao_v1",
    "timestamp": "2024-03-24T10:00:00",
    "agent": "AG-04"
  }
}
```

**Tools Necessárias:**
- template_engine_tool
- content_generator_tool
- structure_validator_tool

**Campos do State Produzidos:**
- petition_draft_json
- petition_draft_data

**Campos do State Requeridos:**
- suggestions_data
- classified_inconsistencies_data
- template_type
- process_metadata
- motivations_data (opcional)

**Dependências:**
- T-006 (suggest_petition_type)
- T-018 (suggest_recurso_motivations) - opcional

---

### Task 8: apply_specific_template

**ID:** T-008
**Agente:** AG-04 (petition_generator_agent)
**Ordem:** 8
**Tipo:** Processamento

**Input Function:**
```python
def apply_specific_template_input_func(state: ProjectState) -> Dict[str, Any]:
    petition_data = state.get("petition_draft_data", {})
    return {
        "petition_draft": petition_data.get("petition_draft", ""),
        "sections_generated": petition_data.get("sections_generated", {}),
        "generation_metadata": petition_data.get("generation_metadata", {}),
        "template_type": state.get("template_type", "impugnacao"),
        "mandatory_sections": ["Fundamentação Jurídica", "Análise Técnica"]
    }
```

**Input Schema:**
- **petition_draft** (str): Rascunho da petição gerada
- **sections_generated** (Dict): Detalhamento das seções
- **generation_metadata** (Dict): Metadados da geração
- **template_type** (str): Tipo de template a ser aplicado (impugnacao/recurso/contrarrazoes)
- **mandatory_sections** (List): Seções mandatórias para o tipo de petição

**Process Steps:**
1. Carregar o template específico correspondente ao template_type
2. Verificar se o petition_draft contém todas as mandatory_sections
3. Utilizar as ferramentas template_selector_tool, section_enforcer_tool e legal_structure_tool para aplicar a estrutura do template e garantir conformidade
4. Identificar e reportar quaisquer seções mandatórias que estejam faltando no rascunho

**Output Function:**
```python
def apply_specific_template_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "apply_specific_template",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "template_compliance": output_data.get("template_compliance", False),
        "missing_sections_count": len(output_data.get("missing_sections", []))
    })

    return {
        **state,
        "templated_draft_json": output_json,
        "templated_draft_data": output_data,
        "execution_log": execution_log,
        "current_task": "apply_specific_template",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "templated_draft": "EXCELENTÍSSIMO(A) SENHOR(A) PREGOEIRO(A)... [com estrutura do template aplicada]",
  "missing_sections": [],
  "template_compliance": true
}
```

**Tools Necessárias:**
- template_selector_tool
- section_enforcer_tool
- legal_structure_tool

**Campos do State Produzidos:**
- templated_draft_json
- templated_draft_data

**Campos do State Requeridos:**
- petition_draft_data
- template_type

**Dependências:**
- T-007 (generate_petition_auto)

---

### Task 9: manage_document_editing

**ID:** T-009
**Agente:** AG-05 (document_editor_agent)
**Ordem:** 9
**Tipo:** Interação com usuário

**Input Function:**
```python
def manage_document_editing_input_func(state: ProjectState) -> Dict[str, Any]:
    templated_data = state.get("templated_draft_data", {})
    return {
        "templated_draft": templated_data.get("templated_draft", ""),
        "missing_sections": templated_data.get("missing_sections", []),
        "template_compliance": templated_data.get("template_compliance", False),
        "edit_requests": state.get("edit_requests", []),
        "user_context": state.get("user_context", {})
    }
```

**Input Schema:**
- **templated_draft** (str): Rascunho da petição com template aplicado
- **missing_sections** (List): Lista de seções faltantes
- **template_compliance** (bool): Status de conformidade
- **edit_requests** (List): Alterações solicitadas pelo usuário
- **user_context** (Dict): Informações do usuário que está editando

**Process Steps:**
1. Carregar o templated_draft no ambiente de edição WYSIWYG
2. Aplicar as edit_requests fornecidas pelo usuário, permitindo formatação e inserção de variáveis
3. Utilizar as ferramentas wysiwyg_editor_tool, variable_injector_tool e format_manager_tool para gerenciar as edições
4. Registrar quais variáveis foram substituídas durante o processo

**Output Function:**
```python
def manage_document_editing_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "manage_document_editing",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "user_id": output_data.get("edit_metadata", {}).get("user_id"),
        "variables_replaced": len(output_data.get("variables_replaced", []))
    })

    return {
        **state,
        "edited_document_json": output_json,
        "edited_document_data": output_data,
        "execution_log": execution_log,
        "current_task": "manage_document_editing",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "edited_document": "EXCELENTÍSSIMO(A) SENHOR(A) PREGOEIRO(A)... [com edições aplicadas]",
  "edit_metadata": {
    "user_id": "user_123",
    "user_name": "João Silva",
    "timestamp": "2024-03-24T10:30:00",
    "change_types": ["text_insertion", "formatting"]
  },
  "variables_replaced": ["{numero_processo}", "{data_hoje}"]
}
```

**Tools Necessárias:**
- wysiwyg_editor_tool
- variable_injector_tool
- format_manager_tool

**Campos do State Produzidos:**
- edited_document_json
- edited_document_data

**Campos do State Requeridos:**
- templated_draft_data
- edit_requests
- user_context

**Dependências:**
- T-008 (apply_specific_template)

---

### Task 10: register_change_log

**ID:** T-010
**Agente:** AG-05 (document_editor_agent)
**Ordem:** 10
**Tipo:** Auditoria

**Input Function:**
```python
def register_change_log_input_func(state: ProjectState) -> Dict[str, Any]:
    templated_data = state.get("templated_draft_data", {})
    edited_data = state.get("edited_document_data", {})
    return {
        "previous_version": templated_data.get("templated_draft", ""),
        "new_version": edited_data.get("edited_document", ""),
        "user_info": edited_data.get("edit_metadata", {}).get("user_info", {}),
        "change_description": state.get("change_description", "")
    }
```

**Input Schema:**
- **previous_version** (str): Texto da versão anterior do documento
- **new_version** (str): Texto da nova versão do documento
- **user_info** (Dict): Informações do usuário que realizou a alteração
- **change_description** (str): Descrição fornecida pelo usuário para a alteração

**Process Steps:**
1. Comparar o previous_version com o new_version para identificar as diferenças (diffs)
2. Utilizar as ferramentas change_tracker_tool, diff_analyzer_tool e log_storage_tool para analisar e registrar as alterações
3. Criar um registro de log (entry) com timestamp, usuário, tipo de ação e detalhes das modificações
4. Gerar um novo ID de versão para o documento e atualizar o trilha de auditoria (audit_trail)

**Output Function:**
```python
def register_change_log_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "register_change_log",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "version_id": output_data.get("version_id", "unknown")
    })

    return {
        **state,
        "change_log_json": output_json,
        "change_log_data": output_data,
        "execution_log": execution_log,
        "current_task": "register_change_log",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "change_log_entry": {
    "timestamp": "2024-03-24T10:35:00",
    "user_id": "user_123",
    "user_name": "João Silva",
    "action_type": "text_edit",
    "diff": {
      "added": "Adicionado argumento sobre jurisprudência do TCU",
      "removed": "Removido trecho redundante",
      "position": "Seção Jurídica, parágrafo 3"
    }
  },
  "version_id": "doc_v2",
  "audit_trail": [
    {
      "version": "doc_v1",
      "timestamp": "2024-03-24T10:00:00",
      "user": "AG-04",
      "action": "geração_automática"
    }
  ]
}
```

**Tools Necessárias:**
- change_tracker_tool
- diff_analyzer_tool
- log_storage_tool

**Campos do State Produzidos:**
- change_log_json
- change_log_data

**Campos do State Requeridos:**
- templated_draft_data
- edited_document_data
- change_description

**Dependências:**
- T-009 (manage_document_editing)

---

### Task 11: monitor_portal_status

**ID:** T-011
**Agente:** AG-06 (monitoring_agent)
**Ordem:** 11 (pode rodar em paralelo)
**Tipo:** Monitoramento contínuo

**Input Function:**
```python
def monitor_portal_status_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "processo_numero": state.get("process_metadata", {}).get("numero_processo", ""),
        "portal_config": state.get("portal_config", {}),
        "last_check": state.get("last_portal_check")
    }
```

**Input Schema:**
- **processo_numero** (str): Número do processo licitatório
- **portal_config** (Dict): Configurações do portal (url, autenticação, intervalo de consulta)
- **last_check** (str): Timestamp da última verificação (opcional)

**Process Steps:**
1. Configurar a consulta à API do portal governamental com base no portal_config
2. Utilizar as ferramentas api_call_tool, status_checker_tool e interval_scheduler_tool para realizar a consulta no intervalo especificado
3. Obter o status atual da janela de recurso para o processo_numero
4. Registrar o timestamp da verificação e a resposta bruta da API

**Output Function:**
```python
def monitor_portal_status_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "monitor_portal_status",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "current_status": output_data.get("current_status", "unknown"),
        "status_changed": output_data.get("status_changed", False)
    })

    return {
        **state,
        "portal_status_json": output_json,
        "portal_status_data": output_data,
        "last_portal_check": output_data.get("check_timestamp"),
        "execution_log": execution_log,
        "current_task": "monitor_portal_status",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "current_status": "aberta",
  "status_changed": true,
  "check_timestamp": "2024-03-24T14:00:00",
  "raw_response": {
    "processo": "67890/2024",
    "status": "janela_recurso_aberta",
    "data_abertura": "2024-03-24T14:00:00",
    "data_fechamento": "2024-03-24T14:10:00"
  }
}
```

**Tools Necessárias:**
- api_call_tool
- status_checker_tool
- interval_scheduler_tool

**Campos do State Produzidos:**
- portal_status_json
- portal_status_data
- last_portal_check

**Campos do State Requeridos:**
- process_metadata
- portal_config

**Dependências:**
- Nenhuma (pode rodar independentemente)

---

### Task 12: detect_status_change

**ID:** T-012
**Agente:** AG-06 (monitoring_agent)
**Ordem:** 12
**Tipo:** Processamento de eventos

**Input Function:**
```python
def detect_status_change_input_func(state: ProjectState) -> Dict[str, Any]:
    portal_data = state.get("portal_status_data", {})
    return {
        "previous_status": state.get("previous_portal_status", "fechada"),
        "current_status": portal_data.get("current_status", "fechada"),
        "status_history": state.get("portal_status_history", [])
    }
```

**Input Schema:**
- **previous_status** (str): Status anterior da janela de recurso
- **current_status** (str): Status atual da janela de recurso
- **status_history** (List): Histórico de status do processo

**Process Steps:**
1. Comparar o previous_status com o current_status para detectar mudanças
2. Utilizar as ferramentas change_detector_tool, pattern_matcher_tool e state_machine_tool para identificar transições específicas, especialmente de "fechada" para "aberta"
3. Calcular um score de confiança para a detecção da mudança
4. Registrar o timestamp da detecção

**Output Function:**
```python
def detect_status_change_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "detect_status_change",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "change_detected": output_data.get("change_detected", False),
        "change_type": output_data.get("change_type", "none")
    })

    # Atualizar histórico de status
    status_history = state.get("portal_status_history", [])
    status_history.append({
        "status": state.get("portal_status_data", {}).get("current_status"),
        "timestamp": state.get("portal_status_data", {}).get("check_timestamp")
    })

    return {
        **state,
        "status_change_json": output_json,
        "status_change_data": output_data,
        "previous_portal_status": state.get("portal_status_data", {}).get("current_status"),
        "portal_status_history": status_history,
        "execution_log": execution_log,
        "current_task": "detect_status_change",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "change_detected": true,
  "change_type": "fechada_para_aberta",
  "detection_timestamp": "2024-03-24T14:00:05",
  "confidence_score": 0.98
}
```

**Tools Necessárias:**
- change_detector_tool
- pattern_matcher_tool
- state_machine_tool

**Campos do State Produzidos:**
- status_change_json
- status_change_data
- previous_portal_status
- portal_status_history

**Campos do State Requeridos:**
- portal_status_data
- previous_portal_status

**Dependências:**
- T-011 (monitor_portal_status)

---

### Task 13: trigger_multi_channel_notification

**ID:** T-013
**Agente:** AG-07 (notification_agent)
**Ordem:** 13
**Tipo:** Ação

**Input Function:**
```python
def trigger_multi_channel_notification_input_func(state: ProjectState) -> Dict[str, Any]:
    change_data = state.get("status_change_data", {})
    return {
        "change_event": {
            "processo": state.get("process_metadata", {}).get("numero_processo", ""),
            "timestamp": change_data.get("detection_timestamp", ""),
            "portal": state.get("portal_config", {}).get("nome_portal", "")
        },
        "user_preferences": state.get("user_preferences", {}),
        "message_template": "🚨 URGENTE: Janela de RECURSO aberta para o Processo {processo} ({orgao}). Acesse: {link}"
    }
```

**Input Schema:**
- **change_event** (Dict): Detalhes do evento de mudança (processo, timestamp, portal)
- **user_preferences** (Dict): Preferências do usuário para canais de notificação e contatos
- **message_template** (str): Template da mensagem de notificação

**Process Steps:**
1. Analisar o change_event para extrair informações críticas (número do processo, portal, horário de abertura)
2. Personalizar a message_template com os dados do change_event
3. Utilizar as ferramentas whatsapp_api_tool, email_api_tool e push_notification_tool para enviar a notificação pelos canais especificados no user_preferences
4. Para cada canal, registrar o status do envio

**Output Function:**
```python
def trigger_multi_channel_notification_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "trigger_multi_channel_notification",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "notifications_sent": len(output_data.get("notifications_sent", [])),
        "urgency_level": output_data.get("urgency_level", "normal")
    })

    return {
        **state,
        "notifications_json": output_json,
        "notifications_data": output_data,
        "execution_log": execution_log,
        "current_task": "trigger_multi_channel_notification",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "notifications_sent": [
    {
      "canal": "WhatsApp",
      "status": "sucesso",
      "timestamp": "2024-03-24T14:00:10",
      "destinatario": "+5511999999999"
    },
    {
      "canal": "email",
      "status": "sucesso",
      "timestamp": "2024-03-24T14:00:11",
      "destinatario": "analista@empresa.com"
    }
  ],
  "delivery_summary": {
    "total": 2,
    "sucessos": 2,
    "falhas": 0
  },
  "urgency_level": "alta"
}
```

**Tools Necessárias:**
- whatsapp_api_tool
- email_api_tool
- push_notification_tool

**Campos do State Produzidos:**
- notifications_json
- notifications_data

**Campos do State Requeridos:**
- status_change_data
- process_metadata
- portal_config
- user_preferences

**Dependências:**
- T-012 (detect_status_change)

---

### Task 14: analyze_winning_proposal

**ID:** T-014
**Agente:** AG-08 (proposal_analyzer_agent)
**Ordem:** 14 (pode rodar após notificação)
**Tipo:** Processamento

**Input Function:**
```python
def analyze_winning_proposal_input_func(state: ProjectState) -> Dict[str, Any]:
    edital_data = state.get("edital_extraction_data", {})
    laws_data = state.get("laws_identification_data", {})
    return {
        "proposal_file": state.get("proposal_file"),
        "edital_data": {
            "extracted_text": edital_data.get("extracted_text", ""),
            "inconsistencies": state.get("classified_inconsistencies_data", {}).get("classified_inconsistencies", [])
        },
        "applicable_laws": laws_data.get("laws_list", [])
    }
```

**Input Schema:**
- **proposal_file** (File): Arquivo da proposta vencedora
- **edital_data** (Dict): Dados do edital (texto extraído e inconsistências já detectadas)
- **applicable_laws** (List): Leis aplicáveis identificadas anteriormente

**Process Steps:**
1. Extrair o texto da proposal_file
2. Comparar o conteúdo da proposta com os requisitos do edital (presentes em edital_data)
3. Comparar a proposta com as applicable_laws para verificar conformidade legal
4. Utilizar as ferramentas document_comparison_tool, technical_validator_tool e compliance_checker_tool para identificar inconsistências técnicas e legais
5. Classificar a gravidade das inconsistências encontradas

**Output Function:**
```python
def analyze_winning_proposal_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "analyze_winning_proposal",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "inconsistencies_count": len(output_data.get("proposal_inconsistencies", []))
    })

    return {
        **state,
        "proposal_analysis_json": output_json,
        "proposal_analysis_data": output_data,
        "execution_log": execution_log,
        "current_task": "analyze_winning_proposal",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "proposal_inconsistencies": [
    {
      "tipo": "tecnica",
      "descricao": "Produto ofertado não atende especificação técnica do item 2.1 do edital",
      "item_edital": "Item 2.1 - Especificação técnica",
      "item_proposta": "Página 3, descrição do produto"
    }
  ],
  "comparison_report": {
    "itens_verificados": 25,
    "itens_conformes": 22,
    "itens_inconformes": 3
  },
  "severity_classification": {
    "alta": 1,
    "media": 2,
    "baixa": 0
  }
}
```

**Tools Necessárias:**
- document_comparison_tool
- technical_validator_tool
- compliance_checker_tool

**Campos do State Produzidos:**
- proposal_analysis_json
- proposal_analysis_data

**Campos do State Requeridos:**
- proposal_file
- edital_extraction_data
- classified_inconsistencies_data
- laws_identification_data

**Dependências:**
- T-005 (classify_inconsistency_severity)

---

### Task 15: manage_analysis_checklist

**ID:** T-015
**Agente:** AG-08 (proposal_analyzer_agent)
**Ordem:** 15
**Tipo:** Processamento

**Input Function:**
```python
def manage_analysis_checklist_input_func(state: ProjectState) -> Dict[str, Any]:
    proposal_data = state.get("proposal_analysis_data", {})
    return {
        "checklist_template": state.get("checklist_template", {}),
        "proposal_context": {
            "proposal_inconsistencies": proposal_data.get("proposal_inconsistencies", []),
            "comparison_report": proposal_data.get("comparison_report", {}),
            "severity_classification": proposal_data.get("severity_classification", {})
        },
        "user_customizations": state.get("checklist_customizations", [])
    }
```

**Input Schema:**
- **checklist_template** (Dict): Template padrão do checklist ou um checklist customizado
- **proposal_context** (Dict): Contexto da proposta sendo analisada
- **user_customizations** (List): Customizações solicitadas pelo usuário ao checklist (opcional)

**Process Steps:**
1. Carregar o checklist_template e aplicar as user_customizations, se fornecidas
2. Associar o checklist ao proposal_context, preenchendo automaticamente itens com base nos dados da análise já realizada (se disponível)
3. Utilizar as ferramentas checklist_manager_tool, template_editor_tool e completion_tracker_tool para gerenciar o checklist
4. Marcar itens como concluídos ou sinalizar itens que necessitam de atenção

**Output Function:**
```python
def manage_analysis_checklist_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "manage_analysis_checklist",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "completion_percentage": output_data.get("completion_percentage", 0.0),
        "flagged_items_count": len(output_data.get("flagged_items", []))
    })

    return {
        **state,
        "checklist_json": output_json,
        "checklist_data": output_data,
        "execution_log": execution_log,
        "current_task": "manage_analysis_checklist",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "active_checklist": {
    "itens": [
      {
        "id": "CHK-001",
        "descricao": "Verificar atendimento a margem de preferência",
        "status": "concluido",
        "observacoes": "Atendido conforme edital"
      }
    ],
    "nome": "Checklist Análise Proposta Vencedora",
    "versao": "1.0"
  },
  "completion_percentage": 75.0,
  "flagged_items": [
    {
      "id": "CHK-005",
      "descricao": "Conferir documentação legal da empresa",
      "status": "pendente",
      "prioridade": "alta"
    }
  ]
}
```

**Tools Necessárias:**
- checklist_manager_tool
- template_editor_tool
- completion_tracker_tool

**Campos do State Produzidos:**
- checklist_json
- checklist_data

**Campos do State Requeridos:**
- proposal_analysis_data
- checklist_template
- checklist_customizations

**Dependências:**
- T-014 (analyze_winning_proposal)

---

### Task 16: suggest_recurso_motivations

**ID:** T-016
**Agente:** AG-08 (proposal_analyzer_agent)
**Ordem:** 16
**Tipo:** Processamento

**Input Function:**
```python
def suggest_recurso_motivations_input_func(state: ProjectState) -> Dict[str, Any]:
    proposal_data = state.get("proposal_analysis_data", {})
    return {
        "proposal_inconsistencies": proposal_data.get("proposal_inconsistencies", []),
        "severity_classification": proposal_data.get("severity_classification", {}),
        "legal_context": state.get("legal_context", {})
    }
```

**Input Schema:**
- **proposal_inconsistencies** (List): Lista de inconsistências da proposta
- **severity_classification** (Dict): Classificação de gravidade
- **legal_context** (Dict): Contexto jurídico adicional (ex: jurisprudências relevantes)

**Process Steps:**
1. Analisar cada inconsistência em proposal_inconsistencies
2. Categorizar cada inconsistência como desvio técnico, legal ou jurisprudencial
3. Utilizar as ferramentas motivation_generator_tool, categorization_tool e argument_strength_calculator_tool para gerar textos de motivação para recurso e calcular a força do argumento
4. Estruturar as sugestões para apresentação em uma interface de seleção

**Output Function:**
```python
def suggest_recurso_motivations_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "suggest_recurso_motivations",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "motivations_count": len(output_data.get("suggested_motivations", []))
    })

    return {
        **state,
        "motivations_json": output_json,
        "motivations_data": output_data,
        "execution_log": execution_log,
        "current_task": "suggest_recurso_motivations",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "suggested_motivations": [
    {
      "inconsistency_id": 0,
      "motivation_text": "A proposta vencedora apresenta desvio técnico grave ao não atender a especificação do item 2.1 do edital, violando o princípio da vinculação ao instrumento convocatório previsto no art. 4º da Lei 14.133/2021.",
      "category": "tecnico",
      "strength": "alta"
    }
  ],
  "selection_interface": {
    "type": "multi_select",
    "options": [
      {
        "id": 0,
        "text_preview": "Desvio técnico no item 2.1...",
        "category": "tecnico",
        "strength": "alta"
      }
    ]
  }
}
```

**Tools Necessárias:**
- motivation_generator_tool
- categorization_tool
- argument_strength_calculator_tool

**Campos do State Produzidos:**
- motivations_json
- motivations_data

**Campos do State Requeridos:**
- proposal_analysis_data
- legal_context

**Dependências:**
- T-014 (analyze_winning_proposal)

---

### Task 17: legal_assistance_chat

**ID:** T-017
**Agente:** AG-09 (legal_assistant_agent)
**Ordem:** 17 (pode rodar em paralelo)
**Tipo:** Interação com usuário

**Input Function:**
```python
def legal_assistance_chat_input_func(state: ProjectState) -> Dict[str, Any]:
    proposal_data = state.get("proposal_analysis_data", {})
    return {
        "user_question": state.get("user_question", ""),
        "chat_context": {
            "processo": state.get("process_metadata", {}).get("numero_processo", ""),
            "inconsistencies": proposal_data.get("proposal_inconsistencies", []),
            "chat_history": state.get("chat_history", [])
        },
        "legal_database": state.get("legal_database", {})
    }
```

**Input Schema:**
- **user_question** (str): Pergunta do usuário
- **chat_context** (Dict): Contexto da conversa (processo, inconsistências detectadas, histórico de perguntas)
- **legal_database** (Dict): Acesso a bases de dados jurídicas (leis, jurisprudências)

**Process Steps:**
1. Analisar a user_question no contexto do chat_context (especificamente sobre desvios da proposta vencedora)
2. Pesquisar na legal_database por leis e jurisprudências relevantes para embasar a resposta
3. Utilizar as ferramentas chat_interface_tool, context_retriever_tool e legal_research_tool para gerar uma resposta contextualizada e fundamentada
4. Estruturar a resposta citando as fontes e sugerir ações possíveis

**Output Function:**
```python
def legal_assistance_chat_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "legal_assistance_chat",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "sources_cited": len(output_data.get("sources_cited", []))
    })

    # Atualizar histórico do chat
    chat_history = state.get("chat_history", [])
    chat_history.append({
        "question": state.get("user_question", ""),
        "answer": output_data.get("ai_response", ""),
        "timestamp": datetime.now().isoformat()
    })

    return {
        **state,
        "legal_assistance_json": output_json,
        "legal_assistance_data": output_data,
        "chat_history": chat_history,
        "execution_log": execution_log,
        "current_task": "legal_assistance_chat",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "ai_response": "Para a inconsistência técnica #1 sobre não atendimento à especificação do item 2.1, você pode fundamentar no art. 4º, §2º da Lei 14.133/2021, que veda exigências desnecessárias ou discriminatórias. Adicionalmente, o precedente do TCU Acórdão 1234/2023 reforça que a comprovação de capacidade técnica pode se dar por outros meios...",
  "sources_cited": [
    {
      "tipo": "lei",
      "referencia": "Lei nº 14.133/2021, Artigo 4º, §2º",
      "trecho_relevante": "É vedada a exigência de qualificação técnica que não guarde relação com o objeto da licitação."
    },
    {
      "tipo": "jurisprudencia",
      "referencia": "TCU Acórdão 1234/2023",
      "trecho_relevante": "A capacidade técnica pode ser comprovada por diversos meios, não se restringindo a certificações específicas."
    }
  ],
  "suggested_actions": [
    "Incluir este argumento na Seção Jurídica da petição",
    "Solicitar esclarecimento ao pregoeiro sobre a exigência"
  ]
}
```

**Tools Necessárias:**
- chat_interface_tool
- context_retriever_tool
- legal_research_tool

**Campos do State Produzidos:**
- legal_assistance_json
- legal_assistance_data
- chat_history

**Campos do State Requeridos:**
- user_question
- proposal_analysis_data
- process_metadata
- legal_database

**Dependências:**
- T-014 (analyze_winning_proposal)

---

### Task 18: prepare_portal_submission

**ID:** T-018
**Agente:** AG-10 (submission_agent)
**Ordem:** 18
**Tipo:** Preparação

**Input Function:**
```python
def prepare_portal_submission_input_func(state: ProjectState) -> Dict[str, Any]:
    edited_data = state.get("edited_document_data", {})
    return {
        "final_document": edited_data.get("edited_document", ""),
        "portal_requirements": state.get("portal_config", {}).get("requirements", {}),
        "process_metadata": state.get("process_metadata", {})
    }
```

**Input Schema:**
- **final_document** (str): Texto da petição finalizada
- **portal_requirements** (Dict): Requisitos técnicos do portal (formato de arquivo, tamanho máximo, campos obrigatórios)
- **process_metadata** (Dict): Metadados do processo para preenchimento de campos da submissão

**Process Steps:**
1. Converter o final_document para o formato de arquivo exigido pelo portal (portal_requirements)
2. Validar o tamanho do arquivo gerado em relação ao tamanho máximo permitido
3. Se o arquivo exceder o tamanho máximo, utilizar a ferramenta splitter_tool para fracioná-lo em partes conforme regras do portal
4. Utilizar as ferramentas file_converter_tool e size_validator_tool para realizar conversão e validação
5. Realizar uma verificação pré-submissão (pre_submission_check) para garantir que todos os requisitos foram atendidos

**Output Function:**
```python
def prepare_portal_submission_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "prepare_portal_submission",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "files_count": len(output_data.get("submission_ready_files", [])),
        "pre_submission_check": output_data.get("pre_submission_check", False)
    })

    return {
        **state,
        "submission_prep_json": output_json,
        "submission_prep_data": output_data,
        "execution_log": execution_log,
        "current_task": "prepare_portal_submission",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "submission_ready_files": [
    {
      "filename": "recurso_processo_67890_parte1.pdf",
      "size_mb": 4.2,
      "format": "PDF"
    },
    {
      "filename": "recurso_processo_67890_parte2.pdf",
      "size_mb": 3.8,
      "format": "PDF"
    }
  ],
  "validation_report": {
    "format_valid": true,
    "size_valid": true,
    "max_size_mb": 10.0,
    "total_size_mb": 8.0
  },
  "pre_submission_check": true
}
```

**Tools Necessárias:**
- file_converter_tool
- size_validator_tool
- splitter_tool

**Campos do State Produzidos:**
- submission_prep_json
- submission_prep_data

**Campos do State Requeridos:**
- edited_document_data
- portal_config
- process_metadata

**Dependências:**
- T-009 (manage_document_editing)

---

### Task 19: execute_automatic_submission

**ID:** T-019
**Agente:** AG-10 (submission_agent)
**Ordem:** 19
**Tipo:** Ação

**Input Function:**
```python
def execute_automatic_submission_input_func(state: ProjectState) -> Dict[str, Any]:
    prep_data = state.get("submission_prep_data", {})
    return {
        "submission_ready_files": prep_data.get("submission_ready_files", []),
        "portal_config": state.get("portal_config", {}),
        "submission_data": {
            "processo_numero": state.get("process_metadata", {}).get("numero_processo", ""),
            "tipo_manifestacao": state.get("template_type", "recurso"),
            "usuario": state.get("user_context", {}).get("nome", "")
        }
    }
```

**Input Schema:**
- **submission_ready_files** (List): Lista de arquivos prontos para submissão
- **portal_config** (Dict): Configurações de acesso à API do portal
- **submission_data** (Dict): Dados obrigatórios para preenchimento dos campos do portal

**Process Steps:**
1. Configurar a chamada à API do portal com base no portal_config
2. Enviar os submission_ready_files e os submission_data para o endpoint apropriado
3. Utilizar as ferramentas api_call_tool, portal_adapter_tool e response_handler_tool para realizar a submissão e tratar a resposta
4. Capturar o comprovante de submissão (número de protocolo) se a submissão for bem-sucedida
5. Em caso de falha, capturar detalhes do erro

**Output Function:**
```python
def execute_automatic_submission_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "execute_automatic_submission",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "success": output_data.get("submission_result", {}).get("success", False),
        "protocol_number": output_data.get("submission_result", {}).get("protocol_number", "")
    })

    return {
        **state,
        "submission_result_json": output_json,
        "submission_result_data": output_data,
        "execution_log": execution_log,
        "current_task": "execute_automatic_submission",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "submission_result": {
    "success": true,
    "protocol_number": "20240324143012345",
    "timestamp": "2024-03-24T14:31:00"
  },
  "portal_response": {
    "status": "success",
    "message": "Documento protocolado com sucesso",
    "protocolo": "20240324143012345",
    "data_hora": "2024-03-24T14:31:00"
  },
  "error_details": null
}
```

**Tools Necessárias:**
- api_call_tool
- portal_adapter_tool
- response_handler_tool

**Campos do State Produzidos:**
- submission_result_json
- submission_result_data

**Campos do State Requeridos:**
- submission_prep_data
- portal_config
- process_metadata
- template_type
- user_context

**Dependências:**
- T-018 (prepare_portal_submission)

---

### Task 20: manage_open_bid_dispute

**ID:** T-020
**Agente:** AG-11 (dispute_manager_agent)
**Ordem:** 20 (fluxo independente)
**Tipo:** Processamento em tempo real

**Input Function:**
```python
def manage_open_bid_dispute_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "dispute_config": state.get("dispute_config", {}),
        "bid_events": state.get("bid_events", []),
        "dispute_rules": state.get("dispute_rules", {"open_bid_time": 120})
    }
```

**Input Schema:**
- **dispute_config** (Dict): Configuração da disputa (modalidade: "aberto", lista de participantes)
- **bid_events** (List): Lances realizados, cada um contendo timestamp e valor
- **dispute_rules** (Dict): Regras específicas da disputa (ex: tempo de 2 minutos)

**Process Steps:**
1. Inicializar o estado da disputa com base no dispute_config e nos bid_events iniciais
2. Monitorar o tempo decorrido desde o último lance, contabilizando o período de 2 minutos para contra-lance
3. Utilizar as ferramentas timer_tool, bid_tracker_tool e winner_detector_tool para gerenciar o tempo, rastrear lances e detectar o vencedor
4. Registrar todas as ações em um log de auditoria
5. Declarar o vencedor quando o tempo se esgotar sem novos lances

**Output Function:**
```python
def manage_open_bid_dispute_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "manage_open_bid_dispute",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "dispute_status": output_data.get("dispute_state", {}).get("status", "unknown"),
        "winner_declared": "winner_declaration" in output_data
    })

    return {
        **state,
        "dispute_state_json": output_json,
        "dispute_state_data": output_data,
        "execution_log": execution_log,
        "current_task": "manage_open_bid_dispute",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "dispute_state": {
    "status": "finalizado",
    "tempo_restante": 0,
    "ultimo_lance": {
      "participante": "Empresa A",
      "valor": 150000.00,
      "timestamp": "2024-03-24T11:02:00"
    },
    "participantes_ativos": ["Empresa A"]
  },
  "winner_declaration": {
    "vencedor": "Empresa A",
    "lance_vencedor": 150000.00,
    "timestamp_declaracao": "2024-03-24T11:04:00"
  },
  "audit_log": [
    {
      "evento": "lance_registrado",
      "participante": "Empresa A",
      "valor": 150000.00,
      "timestamp": "2024-03-24T11:02:00"
    }
  ]
}
```

**Tools Necessárias:**
- timer_tool
- bid_tracker_tool
- winner_detector_tool

**Campos do State Produzidos:**
- dispute_state_json
- dispute_state_data

**Campos do State Requeridos:**
- dispute_config
- bid_events
- dispute_rules

**Dependências:**
- Nenhuma (fluxo independente)

---

### Task 21: manage_open_closed_bid_dispute

**ID:** T-021
**Agente:** AG-11 (dispute_manager_agent)
**Ordem:** 21
**Tipo:** Processamento em tempo real

**Input Function:**
```python
def manage_open_closed_bid_dispute_input_func(state: ProjectState) -> Dict[str, Any]:
    dispute_data = state.get("dispute_state_data", {})
    return {
        "dispute_config": state.get("dispute_config", {"modalidade": "aberto_fechado"}),
        "open_phase_results": dispute_data.get("open_phase_results", {}),
        "closed_bids": state.get("closed_bids", [])
    }
```

**Input Schema:**
- **dispute_config** (Dict): Configuração da disputa (modalidade: "aberto_fechado")
- **open_phase_results** (Dict): Resultados da fase aberta (ranking dos 3 melhores participantes)
- **closed_bids** (List): Lances fechados enviados pelos 3 melhores

**Process Steps:**
1. Inicializar a fase fechada com base nos open_phase_results (os 3 melhores participantes)
2. Gerenciar o período de 5 minutos para recebimento dos lances fechados (closed_bids)
3. Utilizar as ferramentas phase_manager_tool, secret_bid_tool e ranking_calculator_tool para gerenciar a fase, processar os lances secretos e calcular o ranking final
4. Determinar o vencedor com base nos lances fechados
5. Atualizar o status da fase e declarar o vencedor final

**Output Function:**
```python
def manage_open_closed_bid_dispute_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "manage_open_closed_bid_dispute",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "phase_status": output_data.get("phase_status", "unknown"),
        "winner": output_data.get("winner", {}).get("vencedor", "none")
    })

    return {
        **state,
        "dispute_result_json": output_json,
        "dispute_result_data": output_data,
        "execution_log": execution_log,
        "current_task": "manage_open_closed_bid_dispute",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "phase_status": "finalizado",
  "final_ranking": [
    {
      "participante": "Empresa B",
      "lance_fechado": 148000.00,
      "posicao": 1
    },
    {
      "participante": "Empresa A",
      "lance_fechado": 150000.00,
      "posicao": 2
    }
  ],
  "winner": {
    "vencedor": "Empresa B",
    "lance_vencedor": 148000.00,
    "modalidade": "menor_preço"
  }
}
```

**Tools Necessárias:**
- phase_manager_tool
- secret_bid_tool
- ranking_calculator_tool

**Campos do State Produzidos:**
- dispute_result_json
- dispute_result_data

**Campos do State Requeridos:**
- dispute_state_data
- dispute_config
- closed_bids

**Dependências:**
- T-020 (manage_open_bid_dispute)

---

### Task 22: manage_users_and_profiles

**ID:** T-022
**Agente:** AG-12 (user_management_agent)
**Ordem:** 22 (fluxo administrativo independente)
**Tipo:** Administração

**Input Function:**
```python
def manage_users_and_profiles_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "user_data": state.get("user_data", {}),
        "action": state.get("user_action", "create"),
        "admin_context": state.get("admin_context", {})
    }
```

**Input Schema:**
- **user_data** (Dict): Dados do usuário (nome, email, perfil desejado)
- **action** (str): Ação a ser realizada (create, update, deactivate)
- **admin_context** (Dict): Informações do administrador que está executando a ação

**Process Steps:**
1. Validar a action solicitada e os user_data fornecidos
2. Executar a ação no sistema de gerenciamento de usuários (criação, atualização ou desativação)
3. Atribuir ou atualizar o perfil do usuário conforme especificado em user_data
4. Utilizar as ferramentas user_database_tool, role_manager_tool e auth_validator_tool para realizar as operações
5. Registrar a ação no log de auditoria do sistema

**Output Function:**
```python
def manage_users_and_profiles_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "manage_users_and_profiles",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "action": state.get("user_action", "unknown"),
        "user_email": output_data.get("user_record", {}).get("email", "")
    })

    return {
        **state,
        "user_management_json": output_json,
        "user_management_data": output_data,
        "execution_log": execution_log,
        "current_task": "manage_users_and_profiles",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "user_record": {
    "id": "user_456",
    "nome": "Maria Souza",
    "email": "maria@empresa.com",
    "perfil": "Analista Jurídico",
    "status": "ativo",
    "data_criacao": "2024-03-24T09:00:00"
  },
  "permission_summary": {
    "modulos_acesso": ["analise", "documentos", "monitoramento"],
    "acoes_permitidas": ["ler", "editar", "gerar"]
  },
  "audit_entry": {
    "administrador": "admin_sistema",
    "timestamp": "2024-03-24T09:05:00",
    "tipo_acao": "criar_usuario",
    "usuario_afetado": "user_456"
  }
}
```

**Tools Necessárias:**
- user_database_tool
- role_manager_tool
- auth_validator_tool

**Campos do State Produzidos:**
- user_management_json
- user_management_data

**Campos do State Requeridos:**
- user_data
- user_action
- admin_context

**Dependências:**
- Nenhuma (fluxo administrativo independente)

---

### Task 23: configure_mfa

**ID:** T-023
**Agente:** AG-12 (user_management_agent)
**Ordem:** 23
**Tipo:** Configuração de segurança

**Input Function:**
```python
def configure_mfa_input_func(state: ProjectState) -> Dict[str, Any]:
    user_data = state.get("user_management_data", {})
    return {
        "user_id": user_data.get("user_record", {}).get("id", ""),
        "mfa_action": state.get("mfa_action", "enable"),
        "user_profile": user_data.get("user_record", {}).get("perfil", "")
    }
```

**Input Schema:**
- **user_id** (str): Identificador do usuário
- **mfa_action** (str): Ação (enable, disable, force)
- **user_profile** (str): Perfil do usuário (Admin, Jurídico, etc.)

**Process Steps:**
1. Verificar o user_profile para determinar se o MFA é obrigatório (para administradores) ou opcional
2. Executar a mfa_action solicitada (habilitar, desabilitar ou forçar MFA) para o user_id
3. Gerar códigos de backup e configurar o método TOTP, se for habilitar
4. Utilizar as ferramentas mfa_manager_tool, totp_generator_tool e security_policy_tool para realizar a configuração
5. Verificar a conformidade com as políticas de segurança

**Output Function:**
```python
def configure_mfa_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "configure_mfa",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "mfa_configured": output_data.get("mfa_status", {}).get("configurado", False),
        "security_level": output_data.get("security_level", "medio")
    })

    return {
        **state,
        "mfa_config_json": output_json,
        "mfa_config_data": output_data,
        "execution_log": execution_log,
        "current_task": "configure_mfa",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "mfa_status": {
    "configurado": true,
    "tipo": "TOTP",
    "backup_codes": ["123456", "234567", "345678"],
    "data_configuracao": "2024-03-24T09:10:00"
  },
  "security_level": "alto",
  "compliance_check": true
}
```

**Tools Necessárias:**
- mfa_manager_tool
- totp_generator_tool
- security_policy_tool

**Campos do State Produzidos:**
- mfa_config_json
- mfa_config_data

**Campos do State Requeridos:**
- user_management_data
- mfa_action

**Dependências:**
- T-022 (manage_users_and_profiles)

---

### Task 24: manage_petition_templates

**ID:** T-024
**Agente:** AG-13 (configuration_agent)
**Ordem:** 24 (fluxo de configuração independente)
**Tipo:** Administração

**Input Function:**
```python
def manage_petition_templates_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "template_data": state.get("template_data", {}),
        "action": state.get("template_action", "create"),
        "admin_context": state.get("admin_context", {})
    }
```

**Input Schema:**
- **template_data** (Dict): Dados do template (nome, tipo, estrutura, conteúdo)
- **action** (str): Ação (create, update, delete)
- **admin_context** (Dict): Informações do administrador executando a ação

**Process Steps:**
1. Validar a action e os template_data fornecidos
2. Executar a ação no repositório de templates (criação, atualização ou remoção)
3. Validar a estrutura do template (se ação for create ou update) para garantir que atenda aos requisitos do sistema
4. Utilizar as ferramentas template_manager_tool, structure_validator_tool e version_control_tool para gerenciar os templates
5. Realizar uma análise de impacto para templates existentes que serão modificados ou removidos

**Output Function:**
```python
def manage_petition_templates_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "manage_petition_templates",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "action": state.get("template_action", "unknown"),
        "template_name": output_data.get("template_record", {}).get("nome", "")
    })

    return {
        **state,
        "template_management_json": output_json,
        "template_management_data": output_data,
        "execution_log": execution_log,
        "current_task": "manage_petition_templates",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "template_record": {
    "id": "template_impugnacao_v2",
    "nome": "Modelo Impugnação v2.0",
    "tipo": "impugnacao",
    "versao": "2.0",
    "conteudo": "EXCELENTÍSSIMO(A) SENHOR(A) PREGOEIRO(A)...",
    "estrutura": ["cabecalho", "identificacao", "fatos", "juridica", "tecnica", "pedido", "conclusao"],
    "data_criacao": "2024-03-24T08:00:00"
  },
  "validation_errors": [],
  "impact_analysis": {
    "peticoes_afetadas": 12,
    "usuarios_afetados": 5
  }
}
```

**Tools Necessárias:**
- template_manager_tool
- structure_validator_tool
- version_control_tool

**Campos do State Produzidos:**
- template_management_json
- template_management_data

**Campos do State Requeridos:**
- template_data
- template_action
- admin_context

**Dependências:**
- Nenhuma (fluxo de configuração independente)

---

### Task 25: configure_analysis_rules

**ID:** T-025
**Agente:** AG-13 (configuration_agent)
**Ordem:** 25
**Tipo:** Configuração

**Input Function:**
```python
def configure_analysis_rules_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "rule_set": state.get("rule_set", {}),
        "analysis_parameters": state.get("analysis_parameters", {}),
        "admin_context": state.get("admin_context", {})
    }
```

**Input Schema:**
- **rule_set** (Dict): Conjunto de regras para classificação de gravidade (critérios, thresholds)
- **analysis_parameters** (Dict): Parâmetros gerais para análise (ex: sensibilidade)
- **admin_context** (Dict): Informações do administrador executando a configuração

**Process Steps:**
1. Validar o rule_set e os analysis_parameters fornecidos
2. Aplicar as novas regras e parâmetros ao sistema de análise
3. Utilizar as ferramentas rule_editor_tool, parameter_manager_tool e validation_tool para configurar e validar as regras
4. Realizar uma estimativa do impacto no desempenho da análise com as novas regras
5. Gerar um relatório de validação

**Output Function:**
```python
def configure_analysis_rules_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "configure_analysis_rules",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "rules_count": len(output_data.get("active_rules", {}).get("regras", [])),
        "performance_impact": output_data.get("performance_impact", {}).get("impacto", "baixo")
    })

    return {
        **state,
        "rules_config_json": output_json,
        "rules_config_data": output_data,
        "classification_rules": output_data.get("active_rules", {}),  # Atualiza regras no state
        "execution_log": execution_log,
        "current_task": "configure_analysis_rules",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "active_rules": {
    "regras": [
      {
        "id": "REG-001",
        "descricao": "Classificar como Alta se violar lei federal",
        "criterio": "tipo_norma = 'lei_federal'",
        "gravidade": "Alta",
        "threshold": 0.8
      }
    ],
    "versao": "1.1",
    "data_atualizacao": "2024-03-24T08:30:00"
  },
  "validation_report": {
    "regras_validas": 15,
    "regras_invalidas": 0,
    "warnings": ["Threshold muito baixo para REG-005"]
  },
  "performance_impact": {
    "impacto": "baixo",
    "tempo_estimado_aumento": "5%",
    "recursos_adicionais": "nenhum"
  }
}
```

**Tools Necessárias:**
- rule_editor_tool
- parameter_manager_tool
- validation_tool

**Campos do State Produzidos:**
- rules_config_json
- rules_config_data
- classification_rules (atualizado)

**Campos do State Requeridos:**
- rule_set
- analysis_parameters
- admin_context

**Dependências:**
- Nenhuma (fluxo de configuração independente)

---

### Task 26: audit_system_actions

**ID:** T-026
**Agente:** AG-14 (security_auditor_agent)
**Ordem:** 26 (fluxo de auditoria independente)
**Tipo:** Auditoria

**Input Function:**
```python
def audit_system_actions_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "audit_period": state.get("audit_period", {}),
        "action_types": state.get("audit_action_types", []),
        "user_filter": state.get("audit_user_filter", "")
    }
```

**Input Schema:**
- **audit_period** (Dict): Período de auditoria (data_inicio, data_fim)
- **action_types** (List): Tipos de ação a serem auditadas (ex: login, document_edit)
- **user_filter** (str): Filtro por usuário específico

**Process Steps:**
1. Coletar os logs do sistema dentro do audit_period fornecido
2. Aplicar os filtros action_types e user_filter, se fornecidos
3. Analisar os logs em busca de ações críticas e padrões anômalos
4. Utilizar as ferramentas log_analyzer_tool, integrity_checker_tool e pattern_detector_tool para realizar a auditoria
5. Calcular um score de conformidade com base nas políticas do sistema

**Output Function:**
```python
def audit_system_actions_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "audit_system_actions",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "actions_audited": len(output_data.get("audit_report", {}).get("acoes", [])),
        "anomalies_found": len(output_data.get("anomalies", []))
    })

    return {
        **state,
        "audit_report_json": output_json,
        "audit_report_data": output_data,
        "execution_log": execution_log,
        "current_task": "audit_system_actions",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "audit_report": {
    "periodo": {
      "inicio": "2024-03-01T00:00:00",
      "fim": "2024-03-24T23:59:59"
    },
    "acoes": [
      {
        "timestamp": "2024-03-24T10:35:00",
        "usuario": "user_123",
        "acao": "document_edit",
        "detalhes": "Edição da petição 12345/2024"
      }
    ],
    "total_acoes": 150,
    "tipos_acao": {
      "login": 50,
      "document_edit": 30,
      "submission": 20,
      "other": 50
    }
  },
  "anomalies": [
    {
      "timestamp": "2024-03-24T03:15:00",
      "usuario": "user_999",
      "acao": "login",
      "detalhes": "Tentativa de login fora do horário comercial",
      "severity": "media"
    }
  ],
  "compliance_score": 0.95
}
```

**Tools Necessárias:**
- log_analyzer_tool
- integrity_checker_tool
- pattern_detector_tool

**Campos do State Produzidos:**
- audit_report_json
- audit_report_data

**Campos do State Requeridos:**
- audit_period
- audit_action_types
- audit_user_filter

**Dependências:**
- Nenhuma (fluxo de auditoria independente)

---

### Task 27: verify_gdpr_compliance

**ID:** T-027
**Agente:** AG-14 (security_auditor_agent)
**Ordem:** 27
**Tipo:** Auditoria de conformidade

**Input Function:**
```python
def verify_gdpr_compliance_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "compliance_checklist": state.get("gdpr_checklist", {}),
        "data_inventory": state.get("data_inventory", {}),
        "privacy_settings": state.get("privacy_settings", {})
    }
```

**Input Schema:**
- **compliance_checklist** (Dict): Lista de verificações de conformidade com a LGPD
- **data_inventory** (Dict): Inventário dos dados pessoais armazenados no sistema
- **privacy_settings** (Dict): Configurações de privacidade ativas no sistema

**Process Steps:**
1. Percorrer o compliance_checklist e verificar cada item com base no data_inventory e privacy_settings
2. Verificar a gestão de consentimento dos usuários
3. Avaliar os mecanismos de portabilidade de dados e notificação de violações
4. Utilizar as ferramentas gdpr_validator_tool, consent_manager_tool e breach_notifier_tool para realizar as verificações
5. Realizar uma avaliação de riscos e listar itens de ação necessários

**Output Function:**
```python
def verify_gdpr_compliance_output_func(state: ProjectState, result: Any) -> ProjectState:
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
        "task": "verify_gdpr_compliance",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "checklist_items": len(output_data.get("compliance_report", {}).get("itens_verificados", [])),
        "compliance_score": output_data.get("compliance_report", {}).get("percentual_conformidade", 0.0)
    })

    return {
        **state,
        "gdpr_compliance_json": output_json,
        "gdpr_compliance_data": output_data,
        "execution_log": execution_log,
        "current_task": "verify_gdpr_compliance",
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "compliance_report": {
    "itens_verificados": [
      {
        "item": "Consentimento explícito para coleta",
        "status": "conforme",
        "evidencias": ["Formulário de consentimento ativo"]
      },
      {
        "item": "Portabilidade de dados",
        "status": "nao_conforme",
        "evidencias": ["Mecanismo de exportação não implementado"]
      }
    ],
    "total_itens": 15,
    "itens_conformes": 13,
    "itens_nao_conformes": 2,
    "percentual_conformidade": 0.87
  },
  "risk_assessment": {
    "risco_total": "medio",
    "riscos_identificados": [
      {
        "descricao": "Falta de mecanismo de portabilidade",
        "impacto": "medio",
        "probabilidade": "alta"
      }
    ]
  },
  "action_items": [
    {
      "descricao": "Implementar funcionalidade de exportação de dados pessoais",
      "responsavel": "Equipe de desenvolvimento",
      "prazo": "2024-04-30",
      "prioridade": "alta"
    }
  ]
}
```

**Tools Necessárias:**
- gdpr_validator_tool
- consent_manager_tool
- breach_notifier_tool

**Campos do State Produzidos:**
- gdpr_compliance_json
- gdpr_compliance_data

**Campos do State Requeridos:**
- gdpr_checklist
- data_inventory
- privacy_settings

**Dependências:**
- Nenhuma (fluxo de auditoria independente)

---

## 4. Grafo de Dependências

```
Fluxo Principal de Análise de Edital e Geração de Petição:
T-001 (upload_extract_edital)
    ↓ produz: edital_extraction_data
T-002 (identify_applicable_laws)
    ↓ produz: laws_identification_data
T-003 (compare_edital_laws)
    ↓ produz: comparison_report_data
T-004 (detect_legal_inconsistencies)
    ↓ produz: inconsistencies_data
T-005 (classify_inconsistency_severity)
    ↓ produz: classified_inconsistencies_data
T-006 (suggest_petition_type)
    ↓ produz: suggestions_data
T-007 (generate_petition_auto)
    ↓ produz: petition_draft_data
T-008 (apply_specific_template)
    ↓ produz: templated_draft_data
T-009 (manage_document_editing)
    ↓ produz: edited_document_data
T-010 (register_change_log)
    ↓ produz: change_log_data

Fluxo de Monitoramento e Notificação:
T-011 (monitor_portal_status)
    ↓ produz: portal_status_data
T-012 (detect_status_change)
    ↓ produz: status_change_data
T-013 (trigger_multi_channel_notification)
    ↓ produz: notifications_data

Fluxo de Análise de Proposta Vencedora:
T-005 (classify_inconsistency_severity)  [reutilizado do fluxo principal]
    ↓ produz: classified_inconsistencies_data
T-014 (analyze_winning_proposal)
    ↓ produz: proposal_analysis_data
T-015 (manage_analysis_checklist)
    ↓ produz: checklist_data
T-016 (suggest_recurso_motivations)
    ↓ produz: motivations_data
T-017 (legal_assistance_chat)
    ↓ produz: legal_assistance_data

Fluxo de Submissão:
T-009 (manage_document_editing)  [reutilizado do fluxo principal]
    ↓ produz: edited_document_data
T-018 (prepare_portal_submission)
    ↓ produz: submission_prep_data
T-019 (execute_automatic_submission)
    ↓ produz: submission_result_data

Fluxo de Disputas:
T-020 (manage_open_bid_dispute)
    ↓ produz: dispute_state_data
T-021 (manage_open_closed_bid_dispute)
    ↓ produz: dispute_result_data

Fluxo Administrativo - Gestão de Usuários:
T-022 (manage_users_and_profiles)
    ↓ produz: user_management_data
T-023 (configure_mfa)
    ↓ produz: mfa_config_data

Fluxo Administrativo - Configuração:
T-024 (manage_petition_templates)
    ↓ produz: template_management_data
T-025 (configure_analysis_rules)
    ↓ produz: rules_config_data, classification_rules (atualizado)

Fluxo de Auditoria:
T-026 (audit_system_actions)
    ↓ produz: audit_report_data
T-027 (verify_gdpr_compliance)
    ↓ produz: gdpr_compliance_data
```

**Dependências Explícitas:**
- T-002 requires: ["edital_extraction_data"] (de T-001)
- T-003 requires: ["edital_extraction_data", "laws_identification_data"] (de T-001, T-002)
- T-004 requires: ["comparison_report_data", "edital_extraction_data", "laws_identification_data"] (de T-003, T-001, T-002)
- T-005 requires: ["inconsistencies_data", "classification_rules"] (de T-004)
- T-006 requires: ["classified_inconsistencies_data", "process_metadata"] (de T-005)
- T-007 requires: ["suggestions_data", "classified_inconsistencies_data", "template_type", "process_metadata", "motivations_data(opcional)"] (de T-006, T-005, T-016)
- T-008 requires: ["petition_draft_data", "template_type"] (de T-007)
- T-009 requires: ["templated_draft_data", "edit_requests", "user_context"] (de T-008)
- T-010 requires: ["templated_draft_data", "edited_document_data", "change_description"] (de T-008, T-009)
- T-012 requires: ["portal_status_data", "previous_portal_status"] (de T-011)
- T-013 requires: ["status_change_data", "process_metadata", "portal_config", "user_preferences"] (de T-012)
- T-014 requires: ["proposal_file", "edital_extraction_data", "classified_inconsistencies_data", "laws_identification_data"] (de T-001, T-005, T-002)
- T-015 requires: ["proposal_analysis_data", "checklist_template", "checklist_customizations"] (de T-014)
- T-016 requires: ["proposal_analysis_data", "legal_context"] (de T-014)
- T-017 requires: ["user_question", "proposal_analysis_data", "process_metadata", "legal_database"] (de T-014)
- T-018 requires: ["edited_document_data", "portal_config", "process_metadata"] (de T-009)
- T-019 requires: ["submission_prep_data", "portal_config", "process_metadata", "template_type", "user_context"] (de T-018)
- T-021 requires: ["dispute_state_data", "dispute_config", "closed_bids"] (de T-020)
- T-023 requires: ["user_management_data", "mfa_action"] (de T-022)

## 5. TASK_REGISTRY (Estrutura)

```python
TASK_REGISTRY = {
    "upload_extract_edital": {
        "input_func": upload_extract_edital_input_func,
        "output_func": upload_extract_edital_output_func,
        "requires": [],
        "produces": ["edital_extraction_json", "edital_extraction_data"],
        "agent": AG-01,
        "tools": ["pdf_reader", "docx_reader", "text_extraction_tool"],
        "description": "Receber upload de edital, extrair texto completo e metadados básicos"
    },
    "identify_applicable_laws": {
        "input_func": identify_applicable_laws_input_func,
        "output_func": identify_applicable_laws_output_func,
        "requires": ["edital_extraction_data"],
        "produces": ["laws_identification_json", "laws_identification_data"],
        "agent": AG-02,
        "tools": ["vector_search_tool", "legal_database_tool", "pattern_matcher_tool"],
        "description": "Analisar texto do edital para identificar leis, decretos, portarias e normas técnicas explicitamente citadas"
    },
    "compare_edital_laws": {
        "input_func": compare_edital_laws_input_func,
        "output_func": compare_edital_laws_output_func,
        "requires": ["edital_extraction_data", "laws_identification_data"],
        "produces": ["comparison_report_json", "comparison_report_data"],
        "agent": AG-02,
        "tools": ["semantic_comparison_tool", "embedding_tool", "similarity_calculator_tool"],
        "description": "Comparar semanticamente cláusulas do edital com texto das leis identificadas"
    },
    "detect_legal_inconsistencies": {
        "input_func": detect_legal_inconsistencies_input_func,
        "output_func": detect_legal_inconsistencies_output_func,
        "requires": ["comparison_report_data", "edital_extraction_data", "laws_identification_data"],
        "produces": ["inconsistencies_json", "inconsistencies_data"],
        "agent": AG-03,
        "tools": ["inconsistency_detector_tool", "legal_validator_tool", "rule_engine_tool"],
        "description": "Detectar pontos no edital que representem inconsistências com a legislação aplicável"
    },
    "classify_inconsistency_severity": {
        "input_func": classify_inconsistency_severity_input_func,
        "output_func": classify_inconsistency_severity_output_func,
        "requires": ["inconsistencies_data", "classification_rules"],
        "produces": ["classified_inconsistencies_json", "classified_inconsistencies_data"],
        "agent": AG-03,
        "tools": ["classification_tool", "severity_rules_tool", "pattern_analyzer_tool"],
        "description": "Classificar cada inconsistência detectada segundo gravidade (Alta, Média, Baixa)"
    },
    "suggest_petition_type": {
        "input_func": suggest_petition_type_input_func,
        "output_func": suggest_petition_type_output_func,
        "requires": ["classified_inconsistencies_data", "process_metadata"],
        "produces": ["suggestions_json", "suggestions_data"],
        "agent": AG-03,
        "tools": ["suggestion_engine_tool", "business_rules_tool", "decision_tree_tool"],
        "description": "Sugerir tipo de petição mais adequado para cada inconsistência"
    },
    "generate_petition_auto": {
        "input_func": generate_petition_auto_input_func,
        "output_func": generate_petition_auto_output_func,
        "requires": ["suggestions_data", "classified_inconsistencies_data", "template_type", "process_metadata"],
        "produces": ["petition_draft_json", "petition_draft_data"],
        "agent": AG-04,
        "tools": ["template_engine_tool", "content_generator_tool", "structure_validator_tool"],
        "description": "Gerar automaticamente texto completo de petição preenchendo template padrão"
    },
    "apply_specific_template": {
        "input_func": apply_specific_template_input_func,
        "output_func": apply_specific_template_output_func,
        "requires": ["petition_draft_data", "template_type"],
        "produces": ["templated_draft_json", "templated_draft_data"],
        "agent": AG-04,
        "tools": ["template_selector_tool", "section_enforcer_tool", "legal_structure_tool"],
        "description": "Aplicar template específico (Recurso vs Contrarrazões) conforme tipo de petição"
    },
    "manage_document_editing": {
        "input_func": manage_document_editing_input_func,
        "output_func": manage_document_editing_output_func,
        "requires": ["templated_draft_data", "edit_requests", "user_context"],
        "produces": ["edited_document_json", "edited_document_data"],
        "agent": AG-05,
        "tools": ["wysiwyg_editor_tool", "variable_injector_tool", "format_manager_tool"],
        "description": "Fornecer ambiente de edição WYSIWYG para petição gerada"
    },
    "register_change_log": {
        "input_func": register_change_log_input_func,
        "output_func": register_change_log_output_func,
        "requires": ["templated_draft_data", "edited_document_data", "change_description"],
        "produces": ["change_log_json", "change_log_data"],
        "agent": AG-05,
        "tools": ["change_tracker_tool", "diff_analyzer_tool", "log_storage_tool"],
        "description": "Registrar automaticamente todas as alterações feitas no documento"
    },
    "monitor_portal_status": {
        "input_func": monitor_portal_status_input_func,
        "output_func": monitor_portal_status_output_func,
        "requires": ["process_metadata", "portal_config"],
        "produces": ["portal_status_json", "portal_status_data", "last_portal_check"],
        "agent": AG-06,
        "tools": ["api_call_tool", "status_checker_tool", "interval_scheduler_tool"],
        "description": "Consultar API do portal governamental para verificar status da janela de recurso"
    },
    "detect_status_change": {
        "input_func": detect_status_change_input_func,
        "output_func": detect_status_change_output_func,
        "requires": ["portal_status_data", "previous_portal_status"],
        "produces": ["status_change_json", "status_change_data", "previous_portal_status", "portal_status_history"],
        "agent": AG-06,
        "tools": ["change_detector_tool", "pattern_matcher_tool", "state_machine_tool"],
        "description": "Detectar transição de status 'janela fechada' para 'janela aberta/habilitada'"
    },
    "trigger_multi_channel_notification": {
        "input_func": trigger_multi_channel_notification_input_func,
        "output_func": trigger_multi_channel_notification_output_func,
        "requires": ["status_change_data", "process_metadata", "portal_config", "user_preferences"],
        "produces": ["notifications_json", "notifications_data"],
        "agent": AG-07,
        "tools": ["whatsapp_api_tool", "email_api_tool", "push_notification_tool"],
        "description": "Disparar notificações via WhatsApp, e-mail e alerta na UI sobre abertura de janela"
    },
    "analyze_winning_proposal": {
        "input_func": analyze_winning_proposal_input_func,
        "output_func": analyze_winning_proposal_output_func,
        "requires": ["proposal_file", "edital_extraction_data", "classified_inconsistencies_data", "laws_identification_data"],
        "produces": ["proposal_analysis_json", "proposal_analysis_data"],
        "agent": AG-08,
        "tools": ["document_comparison_tool", "technical_validator_tool", "compliance_checker_tool"],
        "description": "Analisar proposta declarada vencedora, comparando com edital, leis e normas técnicas"
    },
    "manage_analysis_checklist": {
        "input_func": manage_analysis_checklist_input_func,
        "output_func": manage_analysis_checklist_output_func,
        "requires": ["proposal_analysis_data", "checklist_template", "checklist_customizations"],
        "produces": ["checklist_json", "checklist_data"],
        "agent": AG-08,
        "tools": ["checklist_manager_tool", "template_editor_tool", "completion_tracker_tool"],
        "description": "Gerenciar checklist parametrizável de pontos de verificação para análise de proposta"
    },
    "suggest_recurso_motivations": {
        "input_func": suggest_recurso_motivations_input_func,
        "output_func": suggest_recurso_motivations_output_func,
        "requires": ["proposal_analysis_data", "legal_context"],
        "produces": ["motivations_json", "motivations_data"],
        "agent": AG-08,
        "tools": ["motivation_generator_tool", "categorization_tool", "argument_strength_calculator_tool"],
        "description": "Sugerir motivações para recurso baseadas em inconsistências da proposta vencedora"
    },
    "legal_assistance_chat": {
        "input_func": legal_assistance_chat_input_func,
        "output_func": legal_assistance_chat_output_func,
        "requires": ["user_question", "proposal_analysis_data", "process_metadata", "legal_database"],
        "produces": ["legal_assistance_json", "legal_assistance_data", "chat_history"],
        "agent": AG-09,
        "tools": ["chat_interface_tool", "context_retriever_tool", "legal_research_tool"],
        "description": "Fornecer interface de chat contextualizada para obter embasamento jurídico"
    },
    "prepare_portal_submission": {
        "input_func": prepare_portal_submission_input_func,
        "output_func": prepare_portal_submission_output_func,
        "requires": ["edited_document_data", "portal_config", "process_metadata"],
        "produces": ["submission_prep_json", "submission_prep_data"],
        "agent": AG-10,
        "tools": ["file_converter_tool", "size_validator_tool", "splitter_tool"],
        "description": "Preparar petição finalizada para submissão: converter formato, validar tamanho"
    },
    "execute_automatic_submission": {
        "input_func": execute_automatic_submission_input_func,
        "output_func": execute_automatic_submission_output_func,
        "requires": ["submission_prep_data", "portal_config", "process_metadata", "template_type", "user_context"],
        "produces": ["submission_result_json", "submission_result_data"],
        "agent": AG-10,
        "tools": ["api_call_tool", "portal_adapter_tool", "response_handler_tool"],
        "description": "Submeter automaticamente petição ao portal governamental via API"
    },
    "manage_open_bid_dispute": {
        "input_func": manage_open_bid_dispute_input_func,
        "output_func": manage_open_bid_dispute_output_func,
        "requires": ["dispute_config", "bid_events", "dispute_rules"],
        "produces": ["dispute_state_json", "dispute_state_data"],
        "agent": AG-11,
        "tools": ["timer_tool", "bid_tracker_tool", "winner_detector_tool"],
        "description": "Gerenciar disputa na modalidade Lance Aberto com tempo de 2 minutos para contra-lance"
    },
    "manage_open_closed_bid_dispute": {
        "input_func": manage_open_closed_bid_dispute_input_func,
        "output_func": manage_open_closed_bid_dispute_output_func,
        "requires": ["dispute_state_data", "dispute_config", "closed_bids"],
        "produces": ["dispute_result_json", "dispute_result_data"],
        "agent": AG-11,
        "tools": ["phase_manager_tool", "secret_bid_tool", "ranking_calculator_tool"],
        "description": "Gerenciar disputa na modalidade Lance Aberto e Fechado com fase de 5 minutos para lances fechados"
    },
    "manage_users_and_profiles": {
        "input_func": manage_users_and_profiles_input_func,
        "output_func": manage_users_and_profiles_output_func,
        "requires": ["user_data", "user_action", "admin_context"],
        "produces": ["user_management_json", "user_management_data"],
        "agent": AG-12,
        "tools": ["user_database_tool", "role_manager_tool", "auth_validator_tool"],
        "description": "Criar, editar, desativar contas de usuário e atribuir perfis"
    },
    "configure_mfa": {
        "input_func": configure_mfa_input_func,
        "output_func": configure_mfa_output_func,
        "requires": ["user_management_data", "mfa_action"],
        "produces": ["mfa_config_json", "mfa_config_data"],
        "agent": AG-12,
        "tools": ["mfa_manager_tool", "totp_generator_tool", "security_policy_tool"],
        "description": "Configurar autenticação multifator (MFA) obrigatória para administradores"
    },
    "manage_petition_templates": {
        "input_func": manage_petition_templates_input_func,
        "output_func": manage_petition_templates_output_func,
        "requires": ["template_data", "template_action", "admin_context"],
        "produces": ["template_management_json", "template_management_data"],
        "agent": AG-13,
        "tools": ["template_manager_tool", "structure_validator_tool", "version_control_tool"],
        "description": "Criar/editar/remover templates de petição com estruturas distintas"
    },
    "configure_analysis_rules": {
        "input_func": configure_analysis_rules_input_func,
        "output_func": configure_analysis_rules_output_func,
        "requires": ["rule_set", "analysis_parameters", "admin_context"],
        "produces": ["rules_config_json", "rules_config_data", "classification_rules"],
        "agent": AG-13,
        "tools": ["rule_editor_tool", "parameter_manager_tool", "validation_tool"],
        "description": "Configurar regras para classificação de gravidade de inconsistências"
    },
    "audit_system_actions": {
        "input_func": audit_system_actions_input_func,
        "output_func": audit_system_actions_output_func,
        "requires": ["audit_period", "audit_action_types", "audit_user_filter"],
        "produces": ["audit_report_json", "audit_report_data"],
        "agent": AG-14,
        "tools": ["log_analyzer_tool", "integrity_checker_tool", "pattern_detector_tool"],
        "description": "Auditar ações críticas do sistema com logs imutáveis"
    },
    "verify_gdpr_compliance": {
        "input_func": verify_gdpr_compliance_input_func,
        "output_func": verify_gdpr_compliance_output_func,
        "requires": ["gdpr_checklist", "data_inventory", "privacy_settings"],
        "produces": ["gdpr_compliance_json", "gdpr_compliance_data"],
        "agent": AG-14,
        "tools": ["gdpr_validator_tool", "consent_manager_tool", "breach_notifier_tool"],
        "description": "Verificar conformidade com LGPD: gestão de consentimento, portabilidade, notificação"
    }
}
```

## 6. Validações

### 6.1 Completude
- [x] Todas as 27 tasks têm input/output definidos
- [x] Todas as dependências são satisfeitas (grafo DAG)
- [x] Não há ciclos no grafo

### 6.2 Consistência
- [x] Campos produzidos são consumidos por tasks subsequentes
- [x] Tipos de dados são compatíveis (JSON strings e Dict objects)
- [x] Tools mencionadas estão disponíveis nos agentes correspondentes

## 7. Métricas

- **Tempo estimado de execução:** Varia por fluxo
  - Fluxo de Impugnação (T-001 a T-010): ~15-20 minutos
  - Fluxo de Recurso (T-011 a T-019 com T-014 a T-016): ~10-15 minutos (crítico)
  - Fluxos administrativos: ~5-10 minutos cada
  
- **Complexidade do grafo:** DAG com múltiplos fluxos paralelos
  - Fluxo principal linear com ramificações
  - 5 fluxos independentes que podem rodar em paralelo
  
- **Paralelismo possível:** Sim
  - Monitoramento (T-011 a T-013) pode rodar independentemente
  - Análise de proposta (T-014 a T-017) pode rodar após notificação
  - Disputas (T-020, T-021) fluxo independente
  - Administração (T-022 a T-025) fluxos independentes
  - Auditoria (T-026, T-027) fluxos independentes