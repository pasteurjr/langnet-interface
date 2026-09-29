# ESPECIFICAÇÃO DE AGENTES E TAREFAS — CREWAI

## SISTEMA BIOBYTE — VIGILÂNCIA DE ICSAC

---

## 0. GAP-ANALYSIS PRELIMINAR

Antes de gerar os agentes e tarefas, registro lacunas e assunções que impactam o desenho:

### 0.1 Requisitos Faltantes / Ambíguos (das 11 perguntas em aberto)

| # | Lacuna | Impacto no desenho | Assunção adotada |
|---|--------|---------------------|-------------------|
| G-01 | Vocabulário do hospital para tradução do laboratório não está formalizado | UC-008 depende de dicionário de termos | Assumo que o vocabulário é um artefato versionado (`vocabulario_hospital.json`) consumido como contexto da task |
| G-02 | Conjunto exato de limiares de cada versão do critério NHSN | UC-009 depende de critério parametrizado | Assumo que os critérios são carregados do banco (`criterio_nhsn`) com versão e vigência; o agente recebe o critério como input |
| G-03 | Formato exato do payload do laboratório | UC-008/UC-025 dependem do formato bruto | Assumo payload JSON com campos `situacao`, `identificador_amostra`, `origem`, `microrganismo`, `antibiograma[]` |
| G-04 | Como apresentar erro de cadastro do laboratório | Afeta fluxo de exceção do agente de tradução | Assumo que o erro vem como `situacao="erro"` com `mensagem_erro` textual |
| G-05 | Fórmula fechada da estimativa de redução de risco | UC-018 é convencional (fora do escopo agêntico) | Não impacta — estimativa é código comum |
| G-06 | Formato e validade exata do token | Afeta autenticação (convencional) | Não impacta — fora do escopo agêntico |

### 0.2 Análise de Sobreposição UC-008 / UC-009 / UC-025

- **UC-008** (traduzir resultado do laboratório) → julgamento de **mapeamento de nomenclatura**.
- **UC-009** (classificar caso pelo critério NHSN) → julgamento de **aplicação de norma**.
- **UC-025** (sinalizar hemocultura pronta e suspeita de ICSAC) → **consolida** UC-008 + UC-009 + detecção de multirresistência em um único julgamento de sinalização clínica. Não é um julgamento novo — é a **síntese** dos julgamentos anteriores em uma decisão de priorização.

**Decisão de consolidação:** UC-008 e UC-009 permanecem como tarefas atômicas (cada uma faz UM julgamento). UC-025 vira uma **terceira tarefa** no mesmo agente de classificação, consumindo os outputs das duas anteriores — é o julgamento de "isso merece sinalização imediata?".

**Total esperado:** 5 tarefas agênticas (UC-008, UC-009, UC-011, UC-013, UC-015) + UC-025 consolidado como síntese = **5 tarefas em 2 agentes**.

Espera — a instrução diz "CINCO tarefas, em DOIS agentes". Vou recontar:

| UC | Julgamento | Tarefa |
|----|-----------|--------|
| UC-008 | Traduzir nomenclatura do laboratório | T-AGN-001 |
| UC-009 | Classificar pelo critério NHSN | T-AGN-002 |
| UC-011 | Avaliar multirresistência | T-AGN-003 |
| UC-013 | Redigir texto do alerta | T-AGN-004 |
| UC-015 | Recomendar bundle com justificativa | T-AGN-005 |

UC-025 (sinalizar suspeita de ICSAC) é **consolidação** de UC-008 + UC-009 + UC-011 — não vira tarefa nova, vira a **orquestração** dos outputs dessas três tarefas no agente de classificação. Portanto: **5 tarefas, 2 agentes**.

### 0.3 Assunções de desenho

- **A-01:** O núcleo convencional (login, cadastro, escore de Cox, estimativa, painel, relatório, auditoria, e-mail) é implementado em código — **não gera agente nem tarefa**.
- **A-02:** O tratamento de erro é caminho de exceção dentro de cada tarefa — **não gera tarefa própria**.
- **A-03:** Toda tarefa agêntica recebe dados **já anonimizados** (FR-069) — a anonimização é feita antes, no código comum.
- **A-04:** Toda decisão agêntica é persistida em `decisao_sistema` com entrada, saída, versão do prompt e justificativa (BR-030) — a persistência é feita pelo código comum que chama a tarefa.

---

## 1. VISÃO GERAL DOS AGENTES

| ID | Nome | Módulo | LLM | Memória |
|----|------|--------|-----|---------|
| AG-01 | clinical_classifier_agent | Classificação Clínica | Claude 3.5 Sonnet | Sim |
| AG-02 | treatment_recommender_agent | Recomendação Terapêutica | Claude 3.5 Sonnet | Sim |

**Justificativa do número de agentes:** apenas 5 tarefas agênticas em 2 domínios de julgamento distintos — **interpretação clínica** (traduzir, classificar, avaliar resistência) e **prescrição assistencial** (recomendar bundle, redigir alerta). Cada agente tem uma responsabilidade coesa; não há fragmentação artificial.

| Agente | Tarefas | Domínio de julgamento |
|--------|---------|------------------------|
| AG-01 | T-AGN-001, T-AGN-002, T-AGN-003 | Interpretar microbiologia e classificar caso |
| AG-02 | T-AGN-004, T-AGN-005 | Prescrever conduta e comunicar |

---

## 2. ESPECIFICAÇÃO DETALHADA DOS AGENTES

### AG-01: Clinical Classifier Agent

| Atributo | Especificação |
|----------|---------------|
| **Nome** | clinical_classifier_agent |
| **Role** | Classificador Clínico de ICSAC |
| **Goal** | Interpretar o resultado microbiológico bruto do laboratório, traduzir para o vocabulário do hospital, classificar o caso pelo critério NHSN vigente à época e determinar a multirresistência do germe — declarando insuficiência quando os dados não sustentarem julgamento. |
| **Backstory** | Você é um infectologista com 15 anos de experiência em vigilância epidemiológica hospitalar e domínio profundo dos critérios NHSN. Você trabalha segundo três princípios inegociáveis:\n1. **Honestidade acima de tudo** — preferir "não consegui" a um número indefensável.\n2. **Nunca inventar dado clínico** — resultado pendente ou com erro não vira microrganismo fictício.\n3. **Rastreabilidade total** — toda decisão precisa citar o critério, a versão e a evidência que a sustentou.\nVocê recebe resultados do laboratório em formato próprio e os traduz para o vocabulário do hospital. Você aplica a norma vigente à ÉPOCA do caso, nunca a norma atual. Você conta classes distintas de antimicrobianos resistentes — nunca confunde "antimicrobiano resistente" com "classe resistente". |
| **LLM** | Claude 3.5 Sonnet |
| **Tools** | `json_parser_tool`, `database_tool`, `vector_search_tool` (para consultar vocabulário do hospital e critérios NHSN versionados) |
| **Delegação** | Pode delegar para AG-02 (Treatment Recommender Agent) quando a classificação estiver concluída como "confirmada" e precisar acionar recomendação de bundle. Não delega para nenhum outro agente. |
| **Memória** | Habilitada — necessária para manter contexto do caso entre as três tarefas (traduzir → classificar → avaliar resistência) e para reconhecer padrões de nomenclatura já vistos. |
| **Verbose** | true |
| **Módulo** | Classificação Clínica |
| **Rationale** | As três tarefas deste agente formam uma cadeia de interpretação clínica coesa: sem tradução não há classificação; sem classificação não há avaliação de resistência contextualizada. Fragmentar em três agentes criaria overhead de handoff sem ganho de especialização. |

**Tarefas Associadas:** T-AGN-001, T-AGN-002, T-AGN-003

---

### AG-02: Treatment Recommender Agent

| Atributo | Especificação |
|----------|---------------|
| **Nome** | treatment_recommender_agent |
| **Role** | Recomendador de Conduta Terapêutica e Comunicador de Alerta |
| **Goal** | Recomendar o bundle de medidas preventivas aplicável ao caso confirmado, com justificativa textual que cite NHSN e multirresistência, e redigir o texto do alerta de multirresistência em linguagem clara para a equipe assistencial — declarando insuficiência quando os dados não sustentarem recomendação. |
| **Backstory** | Você é um médico infectologista da CCIH com 12 anos de experiência em prevenção de infecção de corrente sanguínea associada a cateter. Você conhece os bundles de prevenção publicados e sabe que recomendar o bundle errado é tão grave quanto não recomendar nada. Você segue três regras:\n1. **Nunca recomendar bundle incompatível** — bundle de germe multirresistente só para caso com multirresistência registrada.\n2. **Sempre justificar** — a justificativa cita o resultado do NHSN e a situação de multirresistência; justificativa genérica é descartada.\n3. **Escrever para quem lê** — o alerta é lido por enfermeiro na UTI, com luva na mão; o texto diz o que houve e por que importa, sem jargão.\nQuando os dados não sustentam, você declara insuficiência em vez de recomendar por aproximação. |
| **LLM** | Claude 3.5 Sonnet |
| **Tools** | `json_parser_tool`, `database_tool` (para consultar bundles cadastrados e o caso) |
| **Delegação** | Não delega. Recebe contexto de AG-01 e devolve recomendação/alerta para o código comum persistir. |
| **Memória** | Habilitada — necessária para manter contexto do caso entre redação do alerta e recomendação de bundle quando ambas ocorrem na mesma execução. |
| **Verbose** | true |
| **Módulo** | Recomendação Terapêutica |
| **Rationale** | Recomendar bundle e redigir alerta são dois julgamentos de **comunicação clínica** — ambos traduzem decisão técnica em ação assistencial. Compartilham o mesmo contexto (caso confirmado, multirresistência, NHSN) e o mesmo destinatário (equipe assistencial). |

**Tarefas Associadas:** T-AGN-004, T-AGN-005

---

## 3. ESPECIFICAÇÃO DETALHADA DAS TAREFAS

### T-AGN-001: Translate Lab Result to Hospital Vocabulary

| Atributo | Especificação |
|----------|---------------|
| **ID** | T-AGN-001 |
| **Nome** | `translate_lab_result_to_hospital_vocabulary` |
| **Descrição** | Ler o resultado bruto do laboratório (microrganismo, origem da amostra, antibiograma com antimicrobiano + classe + resultado), interpretar o que é, traduzir a nomenclatura própria do laboratório para o vocabulário adotado pelo hospital e decidir se o resultado é **aproveitável** para classificação. Quando o resultado estiver pendente ou contiver erro, marcar como NÃO aproveitável e sinalizar a condição — sem gerar valor clínico inventado. |
| **Agent** | AG-01 (Clinical Classifier Agent) |
| **Tools** | `json_parser_tool`, `vector_search_tool` (busca no vocabulário do hospital indexado), `database_tool` (leitura do vocabulário versionado) |
| **Input Schema** | ```json\n{\n  "caso_id": "UUID",\n  "resultado_bruto": {\n    "situacao": "pendente|disponivel|erro",\n    "identificador_amostra": "string",\n    "origem": "hemocultura|ponta_cateter|outra",\n    "microrganismo": "string|null",\n    "antibiograma": [\n      {"antimicrobiano": "string", "classe": "string", "resultado": "sensivel|intermediario|resistente"}\n    ],\n    "mensagem_erro": "string|null"\n  },\n  "vocabulario_hospital_versao": "string"\n}\n``` |
| **Output Schema** | ```json\n{\n  "aproveitavel": true,\n  "resultado_traduzido": {\n    "microrganismo": "string",\n    "origem": "string",\n    "antibiograma": [\n      {"antimicrobiano": "string", "classe": "string", "resultado": "string"}\n    ]\n  },\n  "termos_nao_mapeados": ["string"],\n  "justificativa": "string",\n  "motivo_nao_aproveitavel": "string|null",\n  "versao_prompt": "string"\n}\n``` |
| **Objetivo** | Converter o resultado laboratorial bruto em vocabulário do hospital e marcar aproveitabilidade. |
| **Input format** | JSON com resultado bruto + versão do vocabulário. |
| **Expected output** | JSON com `aproveitavel` (bool), `resultado_traduzido`, `termos_nao_mapeados`, `justificativa`, `motivo_nao_aproveitavel`. |
| **CONSTRAINTS** | • NÃO inventar microrganismo, antibiograma ou classe quando `situacao = "pendente"` ou `"erro"` — marcar `aproveitavel=false`.<br>• NÃO mapear termo ambíguo para correspondência inventada — se não houver correspondência no vocabulário, listar em `termos_nao_mapeados` e marcar `aproveitavel=false`.<br>• NÃO truncar nomes longos de microrganismos ou antimicrobianos.<br>• NÃO consultar tabelas fora do schema `biobyte`.<br>• NÃO persistir nada — apenas retornar o JSON (a persistência é feita pelo código comum).<br>• NÃO chamar serviço externo — o resultado já foi importado antes. |
| **EDGE CASES** | • `resultado_bruto` vazio ou ilegível → retornar `aproveitavel=false`, `motivo_nao_aproveitavel="resultado bruto vazio ou ilegível"`.<br>• `situacao="pendente"` → `aproveitavel=false`, `motivo_nao_aproveitavel="resultado pendente no laboratório"`, sem antibiograma.<br>• `situacao="erro"` → `aproveitavel=false`, `motivo_nao_aproveitavel="erro de cadastro: <mensagem_erro>"`.<br>• Antimicrobiano sem classe → listar em `termos_nao_mapeados`, marcar `aproveitavel=false`.<br>• Termo do laboratório sem correspondência → `termos_nao_mapeados` preenchido, `aproveitavel=false`.<br>• Falha do LLM → retornar erro explícito (não retornar tradução parcial como final). |
| **Dependencies** | None (primeira task da cadeia). |
| **Módulo** | Classificação Clínica |
| **UC Relacionado** | UC-008 (Traduzir Resultado do Laboratório para Nomenclatura do Hospital) |
| **RF Relacionado** | FR-023, FR-076, FR-077 |
| **RN Relacionado** | BR-007 (sem invenção de resultado), BR-023 (escopo restrito do agente), BR-030 (decisão auditável) |
| **Rationale** | Esta é a porta de entrada do núcleo agêntico — sem tradução confiável, todas as decisões seguintes operam sobre dado mal interpretado. O julgamento de "o que é isso?" e "isso é aproveitável?" é exatamente o tipo de tarefa que exige modelo de linguagem. |

---

### T-AGN-002: Classify Case by NHSN Criterion

| Atributo | Especificação |
|----------|---------------|
| **ID** | T-AGN-002 |
| **Nome** | `classify_case_by_nhsn_criterion` |
| **Descrição** | Aplicar o critério NHSN **vigente à época do caso** (não o atual) aos dados microbiológicos traduzidos, decidir se o caso configura infecção de corrente sanguínea associada a cateter, atribuir a classificação **confirmada**, **descartada** ou **pendente**, e registrar qual critério e qual versão sustentaram a decisão. Quando os dados não sustentarem classificação, retornar "pendente" com justificativa explícita. |
| **Agent** | AG-01 (Clinical Classifier Agent) |
| **Tools** | `json_parser_tool`, `database_tool` (leitura de `criterio_nhsn` por vigência), `vector_search_tool` (busca semântica nos limiares) |
| **Input Schema** | ```json\n{\n  "caso_id": "UUID",\n  "data_inicio_caso": "YYYY-MM-DD",\n  "resultado_traduzido": { ... output de T-AGN-001 ... },\n  "criterios_candidatos": [\n    {"criterio_id": "UUID", "versao": "string", "nome": "string", "limiares": {...}, "vigencia_inicio": "YYYY-MM-DD", "vigencia_fim": "YYYY-MM-DD|null"}\n  ]\n}\n``` |
| **Output Schema** | ```json\n{\n  "classificacao": "confirmada|descartada|pendente",\n  "criterio_aplicado": "string",\n  "criterio_id": "UUID",\n  "versao_criterio": "string",\n  "justificativa": "string",\n  "evidencia": {"campo": "valor"},\n  "versao_prompt": "string"\n}\n``` |
| **Objetivo** | Atribuir classificação NHSN ao caso com critério e versão registrados. |
| **Input format** | JSON com caso + resultado traduzido + lista de critérios candidatos (filtrados por vigência). |
| **Expected output** | JSON com `classificacao`, `criterio_aplicado`, `criterio_id`, `versao_criterio`, `justificativa`, `evidencia`. |
| **CONSTRAINTS** | • NÃO aplicar o critério ATUAL a caso antigo — usar sempre o critério cuja vigência cobre `data_inicio_caso`.<br>• NÃO classificar como "confirmada" ou "descartada" sem citar o critério e a versão aplicados.<br>• NÃO usar dados de microbiologia incompletos — se faltar microrganismo ou antibiograma, retornar `classificacao="pendente"`.<br>• NÃO inventar limiar que não esteja no critério fornecido.<br>• NÃO consultar tabelas fora do schema `biobyte`.<br>• NÃO persistir — apenas retornar o JSON. |
| **EDGE CASES** | • Nenhum critério com vigência cobrindo `data_inicio_caso` → retornar `classificacao="pendente"`, `justificativa="Não há critério vigente para a data do caso"`, `criterio_id=null`.<br>• Microbiologia incompleta (sem microrganismo) → `classificacao="pendente"`, `justificativa="Dados de microbiologia insuficientes"`.<br>• Múltiplos critérios cobrindo a data → escolher o de vigência mais recente e citar na justificativa.<br>• `resultado_traduzido.aproveitavel=false` → não classificar; retornar `classificacao="pendente"` com o motivo herdado.<br>• Falha do LLM → retornar erro explícito, sem classificação parcial. |
| **Dependencies** | `translate_lab_result_to_hospital_vocabulary` (T-AGN-001) |
| **Módulo** | Classificação Clínica |
| **UC Relacionado** | UC-009 (Classificar Caso pelo Critério NHSN) |
| **RF Relacionado** | FR-024, FR-025, FR-026, FR-028, FR-078, FR-079, FR-091 |
| **RN Relacionado** | BR-010 (vigência por época), BR-026 (classificação auditável), BR-030 (decisão auditável) |
| **Rationale** | Este é o julgamento central do sistema — decidir se o paciente tem ICSAC. Exige interpretação de critério clínico com limiares, aplicação temporal correta e registro de versão. Nenhum programa comum faz isso com a flexibilidade necessária. |

---

### T-AGN-003: Evaluate Multidrug Resistance

| Atributo | Especificação |
|----------|---------------|
| **ID** | T-AGN-003 |
| **Nome** | `evaluate_multidrug_resistance` |
| **Descrição** | Examinar a lista de antimicrobianos do antibiograma traduzido, agrupar por **classe distinta**, contar quantas classes apresentam resultado **resistente** e decidir se o microrganismo é multirresistente aplicando a regra de **três ou mais classes resistentes**. Resultados "intermediário" NÃO contam como resistência. Produzir justificativa que cita as classes resistentes encontradas. |
| **Agent** | AG-01 (Clinical Classifier Agent) |
| **Tools** | `json_parser_tool`, `database_tool` (leitura do antibiograma se necessário) |
| **Input Schema** | ```json\n{\n  "caso_id": "UUID",\n  "antibiograma": [\n    {"antimicrobiano": "string", "classe": "string", "resultado": "sensivel|intermediario|resistente"}\n  ]\n}\n``` |
| **Output Schema** | ```json\n{\n  "multirresistente": true,\n  "classes_resistentes": ["string"],\n  "contagem_classes_resistentes": 3,\n  "justificativa": "string",\n  "versao_prompt": "string"\n}\n``` |
| **Objetivo** | Decidir se o germe é multirresistente pela regra de três ou mais classes. |
| **Input format** | JSON com antibiograma (lista de antimicrobiano + classe + resultado). |
| **Expected output** | JSON com `multirresistente` (bool), `classes_resistentes`, `contagem_classes_resistentes`, `justificativa`. |
| **CONSTRAINTS** | • NÃO contar "intermediário" como resistência.<br>• NÃO contar o mesmo antimicrobiano duas vezes se aparecer repetido — deduplicar por nome.<br>• NÃO contar "antimicrobiano" como "classe" — agrupar por `classe` distinta.<br>• NÃO emitir decisão quando a classe de um ou mais antimicrobianos estiver ausente — retornar erro explícito.<br>• NÃO consultar tabelas fora do schema `biobyte`.<br>• NÃO persistir — apenas retornar o JSON. |
| **EDGE CASES** | • Antibiograma vazio → retornar erro explícito `"Antibiograma sem antimicrobianos — não foi possível avaliar"`.<br>• Antimicrobiano sem classe → erro explícito `"Classe ausente em um ou mais antimicrobianos"`.<br>• Exatamente 3 classes resistentes → `multirresistente=true` (regra é ≥ 3).<br>• Apenas 2 classes resistentes + 5 intermediárias → `multirresistente=false`, justificativa explicita que intermediário não conta.<br>• Classe repetida com resultados diferentes (ex.: dois carbapenêmicos, um resistente e um sensível) → contar a classe como resistente se QUALQUER representante for resistente; registrar na justificativa.<br>• Falha do LLM → retornar erro explícito, sem decisão parcial. |
| **Dependencies** | `translate_lab_result_to_hospital_vocabulary` (T-AGN-001) |
| **Módulo** | Classificação Clínica |
| **UC Relacionado** | UC-011 (Identificar Multirresistência no Antibiograma) |
| **RF Relacionado** | FR-031, FR-032, FR-080 |
| **RN Relacionado** | BR-009 (regra de três classes), BR-030 (decisão auditável) |
| **Rationale** | A regra parece simples ("três classes"), mas exige julgamento sobre agrupamento, deduplicação e tratamento de intermediários — e a decisão errada dispara alerta falso ou deixa de disparar alerta verdadeiro. É julgamento, não lookup. |

---

### T-AGN-004: Draft Alert Text for Care Team

| Atributo | Especificação |
|----------|---------------|
| **ID** | T-AGN-004 |
| **Nome** | `draft_alert_text_for_care_team` |
| **Descrição** | Redigir, em linguagem clara e legível por enfermeiro na UTI, o texto do alerta de multirresistência que informa **o que houve** (microrganismo multirresistente identificado no antibiograma, com origem da amostra) e **por que importa** (risco para o paciente com cateter venoso central). O texto é acompanhado da fundamentação (critério e versão) e da versão do prompt usada. Quando os dados não sustentarem texto afirmativo, retornar mensagem de insuficiência — nunca inventar. |
| **Agent** | AG-02 (Treatment Recommender Agent) |
| **Tools** | `json_parser_tool`, `database_tool` (leitura do alerta aberto) |
| **Input Schema** | ```json\n{\n  "alerta_id": "UUID",\n  "caso_id": "UUID",\n  "microrganismo": "string",\n  "origem_amostra": "string",\n  "antibiograma": [{"antimicrobiano": "string", "classe": "string", "resultado": "string"}],\n  "classificacao_nhsn": {"resultado": "confirmada|descartada|pendente", "criterio": "string", "versao": "string"},\n  "multirresistencia": {"multirresistente": true, "classes_resistentes": ["string"]}\n}\n``` |
| **Output Schema** | ```json\n{\n  "texto_alerta": "string",\n  "fundamentacao": {"criterio": "string", "versao": "string", "multirresistencia": "string"},\n  "completo": true,\n  "motivo_insuficiencia": "string|null",\n  "versao_prompt": "string"\n}\n``` |
| **Objetivo** | Produzir texto do alerta que diga o que houve e por que importa. |
| **Input format** | JSON com dados do caso + resultado NHSN + multirresistência. |
| **Expected output** | JSON com `texto_alerta`, `fundamentacao`, `completo` (bool), `motivo_insuficiencia`. |
| **CONSTRAINTS** | • NÃO redigir texto afirmativo quando `multirresistencia.multirresistente=false` ou quando o antibiograma estiver pendente/com erro.<br>• NÃO omitir o microrganismo nem a origem da amostra — texto sem esses dois campos é incompleto e deve ser descartado.<br>• NÃO usar jargão técnico incompreensível para enfermeiro (ex.: "preditor linear", "coeficiente de Cox").<br>• NÃO persistir — apenas retornar o JSON.<br>• NÃO inventar dado clínico que não esteja no input.<br>• NÃO consultar tabelas fora do schema `biobyte`. |
| **EDGE CASES** | • `multirresistencia.multirresistente=false` → `completo=false`, `motivo_insuficiencia="Caso sem multirresistência registrada"`.<br>• Antibiograma pendente/erro → `completo=false`, `motivo_insuficiencia="Resultado do laboratório pendente ou com erro"`.<br>• Texto gerado sem microrganismo ou sem origem → descartar, `completo=false`, `motivo_insuficiencia="Texto incompleto — redação não aceita"`.<br>• Falha do LLM → retornar erro explícito, sem texto parcial. |
| **Dependencies** | `evaluate_multidrug_resistance` (T-AGN-003), `classify_case_by_nhsn_criterion` (T-AGN-002) |
| **Módulo** | Recomendação Terapêutica |
| **UC Relacionado** | UC-013 (Redigir Texto do Alerta para a Equipe) |
| **RF Relacionado** | FR-035, FR-083 |
| **RN Relacionado** | BR-023 (escopo restrito), BR-025 (tratamento de erro é comportamental), BR-030 (decisão auditável) |
| **Rationale** | Redigir para leitor específico (enfermeiro na UTI, com luva) exige julgamento de linguagem e foco no que importa — não é template. E a decisão de "os dados sustentam texto afirmativo?" é julgamento clínico, não lookup. |

---

### T-AGN-005: Recommend Bundle with Justification

| Atributo | Especificação |
|----------|---------------|
| **ID** | T-AGN-005 |
| **Nome** | `recommend_bundle_with_justification` |
| **Descrição** | Selecionar, entre os bundles cadastrados, o pacote de medidas preventivas aplicável ao caso **confirmado**, considerando o resultado do NHSN e a presença/ausência de multirresistência, e redigir justificativa textual que **cite explicitamente o resultado do NHSN e a situação de multirresistência**. Nunca recomendar bundle de germe multirresistente para caso sem multirresistência registrada. Quando os dados não sustentarem recomendação, declarar insuficiência. |
| **Agent** | AG-02 (Treatment Recommender Agent) |
| **Tools** | `json_parser_tool`, `database_tool` (leitura de `bundle` cadastrados) |
| **Input Schema** | ```json\n{\n  "caso_id": "UUID",\n  "classificacao_nhsn": {"resultado": "confirmada|descartada|pendente", "criterio": "string", "versao": "string"},\n  "multirresistencia": {"multirresistente": true, "classes_resistentes": ["string"]},\n  "bundles_disponiveis": [\n    {"bundle_id": "UUID", "nome": "string", "indicacao": "string", "reducao_media_risco": 0.35, "intervalo_confianca": "string", "para_germe_multirresistente": true}\n  ]\n}\n``` |
| **Output Schema** | ```json\n{\n  "decisao": "recomendar|insuficiente",\n  "bundle_recomendado_id": "UUID|null",\n  "bundle_recomendado_nome": "string|null",\n  "justificativa": "string",\n  "cita_nhsn": true,\n  "cita_multirresistencia": true,\n  "motivo_insuficiencia": "string|null",\n  "versao_prompt": "string"\n}\n``` |
| **Objetivo** | Recomendar bundle compatível com justificativa que cite NHSN e multirresistência. |
| **Input format** | JSON com caso + classificação NHSN + multirresistência + bundles disponíveis. |
| **Expected output** | JSON com `decisao`, `bundle_recomendado_id`, `justificativa`, `cita_nhsn`, `cita_multirresistencia`. |
| **CONSTRAINTS** | • NÃO recomendar bundle quando `classificacao_nhsn.resultado != "confirmada"` — retornar `decisao="insuficiente"`.<br>• NÃO recomendar bundle com `para_germe_multirresistente=true` quando `multirresistencia.multirresistente=false` (BR-012).<br>• NÃO produzir justificativa que não cite explicitamente o resultado do NHSN e a situação de multirresistência — justificativa genérica é descartada.<br>• NÃO recomendar bundle que não esteja em `bundles_disponiveis`.<br>• NÃO persistir — apenas retornar o JSON.<br>• NÃO consultar tabelas fora do schema `biobyte`. |
| **EDGE CASES** | • `classificacao_nhsn.resultado="descartada"` ou `"pendente"` → `decisao="insuficiente"`, `motivo_insuficiencia="Recomendação disponível apenas para caso confirmado"`.<br>• Nenhum bundle compatível → `decisao="insuficiente"`, `motivo_insuficiencia="Nenhum bundle compatível cadastrado"`.<br>• Justificativa gerada sem citar NHSN ou sem citar multirresistência → descartar, `decisao="insuficiente"`, `motivo_insuficiencia="Justificativa incompleta — recomendação não aceita"`.<br>• `bundles_disponiveis` vazio → `decisao="insuficiente"`.<br>• Falha do LLM → retornar erro explícito, sem recomendação parcial. |
| **Dependencies** | `classify_case_by_nhsn_criterion` (T-AGN-002), `evaluate_multidrug_resistance` (T-AGN-003) |
| **Módulo** | Recomendação Terapêutica |
| **UC Relacionado** | UC-015 (Recomendar Bundle ao Caso Confirmado) |
| **RF Relacionado** | FR-039, FR-041, FR-043, FR-044, FR-045, FR-081, FR-082 |
| **RN Relacionado** | BR-012 (proibição de bundle incompatível), BR-023 (escopo restrito), BR-030 (decisão auditável), BR-031 (sobrescrita médica preserva original) |
| **Rationale** | Recomendar bundle exige cruzar três variáveis (classificação, multirresistência, indicação do bundle) e produzir justificativa auditável. A regra de incompatibilidade (BR-012) é uma armadilha clássica que exige julgamento contextualizado. |

---

## 4. MATRIZ DE RASTREABILIDADE

#### T-001-001: Autenticar usuário com e-mail e senha

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `autenticar_usuario_email_senha` |
| **Descrição** | Implementar o fluxo de login com e-mail e senha, sem segundo fator. PASSOS: (1) Receber `{email, senha}` via POST /auth/login; (2) Aplicar rate limiting (10 tentativas/IP/15min); (3) Buscar usuário ativo por e-mail; (4) Validar senha com Argon2id (m=64MiB, t=3, p=4) contra `senha_hash`+`senha_sal`; (5) Emitir JWT RS256 com validade 8h contendo `{sub: usuario_id, papel, exp}`; (6) Registrar em auditoria `{usuario_id, acao:"login", resultado, data_hora}`; (7) Retornar token + dados do usuário. Em falha: mensagem genérica "E-mail ou senha inválidos." sem revelar qual campo errou. Senha NUNCA em log/erro/tela. |
| **Agent** | `agente_autenticacao` |
| **Tools** | `tool_hash_argon2id`, `tool_jwt_rs256`, `tool_rate_limiter`, `tool_auditoria_encadeada` |
| **Input Schema** | `{email: string, senha: string, ip: string}` |
| **Output Schema** | `{token: string, usuario: {id, nome, papel}, expira_em: timestamp}` ou `{erro: string}` |
| **Módulo** | `modulo_autenticacao` |
| **UC Relacionado** | UC-001 |
| **RF Relacionado** | FR-001, FR-004, FR-064, FR-065, FR-066, FR-096 |
| **Rationale** | Login é a porta de entrada do sistema; exige hash com sal, token verificado por requisição e rate limiting para mitigar força bruta na ausência de segundo fator. |


#### T-001-002: Gerenciar cadastro, desativação e reativação de usuários

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `gerenciar_usuarios_cadastro_desativacao` |
| **Descrição** | CRUD de usuários restrito ao papel administrador. PASSOS: (1) POST /usuarios cria usuário com `{nome, email, senha, papel ∈ {medico, enfermeiro, administrador}, ativo}`; (2) Validar e-mail único; (3) Hash Argon2id da senha; (4) PATCH /usuarios/{id}/desativar marca `ativo=false` sem apagar (BR-001); (5) PATCH /usuarios/{id}/reativar marca `ativo=true`; (6) Toda operação grava entrada encadeada em auditoria com `usuario_id` executor. Administrador NÃO acessa dado clínico (FR-067). Enfermeiro NÃO apaga auditoria. |
| **Agent** | `agente_gestao_usuarios` |
| **Tools** | `tool_crud_usuario`, `tool_hash_argon2id`, `tool_auditoria_encadeada`, `tool_controle_acesso_papel` |
| **Input Schema** | `{acao: "criar"\|"editar"\|"desativar"\|"reativar", dados: {nome, email, senha?, papel, ativo}}` |
| **Output Schema** | `{usuario_id, situacao, mensagem}` |
| **Módulo** | `modulo_gestao_usuarios` |
| **UC Relacionado** | UC-002 |
| **RF Relacionado** | FR-002, FR-003, FR-067 |
| **Rationale** | Preserva histórico ao desativar em vez de apagar e restringe papéis a três valores, garantindo rastreabilidade e controle de acesso. |


#### T-003-001: Registrar e consultar trilha de auditoria encadeada

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `gerenciar_trilha_auditoria_encadeada` |
| **Descrição** | Toda ação relevante gera entrada imutável. PASSOS: (1) Interceptar ações (login, cadastro, classificação, sobrescrita, exportação, leitura de paciente) via middleware; (2) Calcular `hash_atual = SHA256(usuario_id + acao + registro_afetado + dados_antes + dados_depois + data_hora + hash_anterior)`; (3) Persistir entrada com `correlation_id` (UUID v4); (4) GET /auditoria aceita filtros `{periodo_inicio, periodo_fim, usuario_id, tipo_acao}` (BR-028); (5) POST /auditoria/verificar-integridade recalcula cadeia e reporta "Encadeamento íntegro" ou "Alteração detectada". Registro de leitura de paciente (FR-098) também gera entrada. |
| **Agent** | `agente_auditoria` |
| **Tools** | `tool_hash_sha256`, `tool_persistir_auditoria`, `tool_filtros_auditoria`, `tool_verificar_cadeia` |
| **Input Schema** | `{acao, usuario_id, registro_afetado, dados_antes?, dados_depois?, correlation_id}` |
| **Output Schema** | `{entrada_id, hash_atual, hash_anterior, data_hora}` |
| **Módulo** | `modulo_auditoria` |
| **UC Relacionado** | UC-003 |
| **RF Relacionado** | FR-005, FR-056, FR-057, FR-058, FR-070, FR-098 |
| **Rationale** | Encadeamento por hash garante imutabilidade e detecção de adulteração; filtros atendem auditoria e LGPD. |


#### T-004-001: Cadastrar paciente com cateter venoso central

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `cadastrar_paciente_cateter` |
| **Descrição** | Cadastro de paciente com cinco campos obrigatórios. PASSOS: (1) POST /pacientes recebe `{nome, data_nascimento, sexo, numero_prontuario, medico_responsavel_id}`; (2) Validar todos preenchidos (FR-006); (3) Validar `medico_responsavel_id` pertence a usuário ativo com papel médico; (4) Gerar `uuid_anonimo` (UUID v4) para chamadas externas; (5) Persistir; (6) Gravar auditoria. Lista de acompanhamento diário de UTI ordenável por "Dias com cateter" ou "Paciente" (FR-087). Visão consolidada reúne prontuário + laboratório + anotação de enfermagem (FR-088). Nenhum campo exibe valor de exemplo (FR-063). |
| **Agent** | `agente_cadastro_paciente` |
| **Tools** | `tool_crud_paciente`, `tool_gerar_uuid_anonimo`, `tool_auditoria_encadeada` |
| **Input Schema** | `{nome, data_nascimento, sexo, numero_prontuario, medico_responsavel_id}` |
| **Output Schema** | `{paciente_id, uuid_anonimo, mensagem}` |
| **Módulo** | `modulo_cadastro_clinico` |
| **UC Relacionado** | UC-004 |
| **RF Relacionado** | FR-006, FR-086, FR-087, FR-088 |
| **Rationale** | Cadastro é base do acompanhamento diário; UUID anônimo viabiliza chamadas externas sem expor identificação. |


#### T-005-001: Registrar episódio e cinco dados de risco do caso

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `registrar_episodio_dados_risco` |
| **Descrição** | Registra episódio clínico com cinco dados de risco obrigatórios. PASSOS: (1) POST /casos/{id}/episodio recebe `{idade_na_data, dias_cateter, apache_ii, sitio_insercao ∈ {jugular_interna, subclavia, femoral}, comorbidades_relevantes, data_inicio, data_encerramento?, estado}`; (2) Validar os cinco dados preenchidos (BR-004); se faltar, retornar "Falta o dado: [nome]" (FR-061); (3) Validar formato de datas; (4) Se `estado="encerrado"`, exigir `data_encerramento`; (5) Persistir; (6) Gravar auditoria. Cálculo de risco só liberado com os cinco dados. |
| **Agent** | `agente_cadastro_episodio` |
| **Tools** | `tool_crud_caso`, `tool_validar_dados_risco`, `tool_auditoria_encadeada` |
| **Input Schema** | `{caso_id, idade_na_data, dias_cateter, apache_ii, sitio_insercao, comorbidades_relevantes, data_inicio, data_encerramento?, estado}` |
| **Output Schema** | `{caso_id, estado, calculo_risco_liberado: boolean, mensagem}` |
| **Módulo** | `modulo_cadastro_clinico` |
| **UC Relacionado** | UC-005 |
| **RF Relacionado** | FR-007, FR-008, FR-009, FR-061 |
| **Rationale** | Os cinco dados são pré-requisito do cálculo de Cox (BR-004); nomear o dado faltante evita cálculo com dado incompleto. |


#### T-006-001: Consultar escore de Cox no serviço externo e persistir retorno

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `consultar_escore_cox_externo` |
| **Descrição** | Consulta o serviço externo de Cox e persiste o retorno. PASSOS: (1) POST /casos/{id}/escore-cox; (2) Validar cinco dados de risco preenchidos (BR-004); (3) Montar payload `{idade: int, apache_ii: int, tipo_cateter: string}` — SEM intervalo de confiança (FR-012); (4) Chamar `POST /cox/escore` com timeout 5s; (5) Em sucesso, persistir `{escore, faixa_risco ∈ {baixo, moderado, alto}, preditor_linear, fatores_peso (jsonb), versao_modelo (varchar 200), data_calculo}`; (6) Em falha/timeout, NÃO gravar escore (BR-017), exibir "O serviço de escore não respondeu. Nenhum escore foi gravado." (FR-060); (7) Gravar auditoria com origem do dado. Sistema NÃO recalcula (BR-024). |
| **Agent** | `agente_integracao_cox` |
| **Tools** | `tool_http_client_cox`, `tool_persistir_escore`, `tool_auditoria_encadeada`, `tool_circuit_breaker` |
| **Input Schema** | `{caso_id}` |
| **Output Schema** | `{escore, faixa_risco, preditor_linear, fatores_peso, versao_modelo, data_calculo}` ou `{erro: "servico_indisponivel"}` |
| **Módulo** | `modulo_integracao_cox` |
| **UC Relacionado** | UC-006 |
| **RF Relacionado** | FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-060, FR-072, FR-084 |
| **Rationale** | Escore é serviço externo (BR-024); não gravar em falha (BR-017) e guardar versão do modelo (BR-006) garantem auditabilidade. |


#### T-007-001: Importar resultado de hemocultura do laboratório

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `importar_hemocultura_laboratorio` |
| **Descrição** | Consulta laboratório por prontuário e importa resultado. PASSOS: (1) POST /casos/{id}/importar-hemocultura; (2) Anonimizar payload com `uuid_anonimo` (FR-069); (3) Chamar `GET /microbiologia/{uuid_anonimo}` com timeout 10s; (4) Receber `{situacao ∈ {pendente, disponivel, erro}, identificador_amostra, origem ∈ {hemocultura, ponta_cateter, outra}, microrganismo?, multirresistente?, antibiograma[], mensagem_erro?}`; (5) Calcular `hash_resultado` para deduplicação (BR-008) — se já existe, retornar "Este resultado já foi importado em [data/hora]"; (6) Se `situacao="pendente"`, registrar estado sem inventar microrganismo (BR-007); (7) Se `situacao="erro"`, registrar mensagem; (8) Persistir; (9) Gravar auditoria. |
| **Agent** | `agente_integracao_laboratorio` |
| **Tools** | `tool_http_client_lab`, `tool_anonimizador`, `tool_deduplicacao_hash`, `tool_persistir_hemocultura`, `tool_auditoria_encadeada` |
| **Input Schema** | `{caso_id, numero_prontuario}` |
| **Output Schema** | `{resultado_id, situacao, identificador_amostra, origem, microrganismo?, antibiograma?, duplicado: boolean}` |
| **Módulo** | `modulo_integracao_laboratorio` |
| **UC Relacionado** | UC-007 |
| **RF Relacionado** | FR-016, FR-017, FR-018, FR-019, FR-020, FR-021, FR-022, FR-059, FR-069, FR-071 |
| **Rationale** | Deduplicação por hash evita contagem incorreta no painel; tratamento explícito de pendente/erro evita invenção de resultado. |


#### T-008-001: Traduzir nomenclatura do laboratório (agêntica)

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `traduzir_resultado_laboratorio` |
| **Descrição** | Agente traduz resultado bruto do laboratório para vocabulário do hospital. PASSOS: (1) Receber resultado bruto; (2) LLM com prompt versionado lê e interpreta; (3) Converte termos para nomenclatura do hospital; (4) Decide `aproveitavel: boolean`; (5) Se `situacao="pendente"` ou `"erro"`, marcar `aproveitavel=false` e não gerar valor clínico (BR-007); (6) Registrar decisão em `Decisao do sistema` com `{entrada, saida, versao_prompt, justificativa}` (BR-030); (7) Manter resultado bruto visível ao lado do traduzido. |
| **Agent** | `agente_traducao_laboratorio` |
| **Tools** | `tool_llm_prompt_versionado`, `tool_registrar_decisao_agente`, `tool_auditoria_encadeada` |
| **Input Schema** | `{resultado_bruto: string, situacao: string}` |
| **Output Schema** | `{resultado_traduzido: string, aproveitavel: boolean, justificativa: string, versao_prompt: string}` |
| **Módulo** | `modulo_agentes_ia` |
| **UC Relacionado** | UC-008 |
| **RF Relacionado** | FR-023, FR-076, FR-077 |
| **Rationale** | Tradução é uma das cinco funções agênticas permitidas (BR-023); registrar entrada/saída/versão garante auditabilidade (BR-030). |


#### T-009-001: Classificar caso pelo critério NHSN (agêntica)

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `classificar_caso_nhsn` |
| **Descrição** | Agente aplica critério NHSN vigente à época do caso. PASSOS: (1) Receber microbiologia do caso; (2) Selecionar critério com `vigencia_inicio ≤ data_inicio < vigencia_fim` (BR-010); (3) LLM com prompt versionado decide `confirmada \| descartada \| pendente`; (4) Registrar `criterio_id`, `criterio_versao`, `assinado_por`, `decidido_por_agente=true` (FR-026, BR-026); (5) Registrar decisão em `Decisao do sistema` com entrada/saída/versão/justificativa (BR-030); (6) Se dados insuficientes, retornar `pendente` com justificativa. |
| **Agent** | `agente_classificacao_nhsn` |
| **Tools** | `tool_llm_prompt_versionado`, `tool_selecionar_criterio_vigente`, `tool_registrar_decisao_agente`, `tool_auditoria_encadeada` |
| **Input Schema** | `{caso_id, microbiologia, data_inicio_caso}` |
| **Output Schema** | `{classificacao, criterio_id, criterio_versao, justificativa, versao_prompt}` |
| **Módulo** | `modulo_agentes_ia` |
| **UC Relacionado** | UC-009 |
| **RF Relacionado** | FR-024, FR-025, FR-026, FR-027, FR-028, FR-078, FR-079, FR-091 |
| **Rationale** | Classificação auditável exige critério e versão (BR-026); aplicar norma da época (BR-010) evita viés retrospectivo. |


#### T-010-001: Sobrescrever classificação automática com justificativa

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `sobrescrever_classificacao_medica` |
| **Descrição** | Médico sobrescreve classificação com justificativa obrigatória. PASSOS: (1) POST /casos/{id}/classificacao/sobrescrever recebe `{nova_classificacao, justificativa}`; (2) Validar papel=médico (FR-067); (3) Validar `justificativa` não vazia (BR-011) — senão bloquear; (4) Persistir nova classificação com `sobrescrita=true`; (5) MANTER classificação original registrada (BR-031); (6) Gravar auditoria encadeada com `{usuario_id, classificacao_anterior, nova_classificacao, justificativa}`. |
| **Agent** | `agente_sobrescrita_classificacao` |
| **Tools** | `tool_crud_classificacao`, `tool_validar_justificativa`, `tool_auditoria_encadeada`, `tool_controle_acesso_papel` |
| **Input Schema** | `{caso_id, nova_classificacao, justificativa, usuario_id}` |
| **Output Schema** | `{classificacao_id, sobrescrita: true, mensagem}` |
| **Módulo** | `modulo_classificacao` |
| **UC Relacionado** | UC-010 |
| **RF Relacionado** | FR-029, FR-030 |
| **Rationale** | Sobrescrita médica prevalece assistencialmente, mas registro original é preservado (BR-031) para auditoria. |


#### T-011-001: Identificar multirresistência no antibiograma (agêntica)

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `avaliar_multirresistencia_antibiograma` |
| **Descrição** | Agente aplica regra de três ou mais classes resistentes. PASSOS: (1) Receber lista de antimicrobianos `[{antimicrobiano, classe, resultado ∈ {sensivel, intermediario, resistente}}]`; (2) LLM com prompt versionado agrupa por classe e conta classes com resultado `resistente` (BR-009); (3) `multirresistente = (classes_resistentes >= 3)`; (4) Registrar decisão em `Decisao do sistema` com `{entrada, saida, classes_resistentes, justificativa, versao_prompt}` (BR-030); (5) Se antibiograma vazio ou classe ausente, retornar erro explícito sem inventar (FR-063). |
| **Agent** | `agente_multirresistencia` |
| **Tools** | `tool_llm_prompt_versionado`, `tool_contar_classes_resistentes`, `tool_registrar_decisao_agente` |
| **Input Schema** | `{antibiograma: [{antimicrobiano, classe, resultado}]}` |
| **Output Schema** | `{multirresistente: boolean, classes_resistentes: int, lista_classes: [], justificativa, versao_prompt}` |
| **Módulo** | `modulo_agentes_ia` |
| **UC Relacionado** | UC-011 |
| **RF Relacionado** | FR-031, FR-032, FR-080 |
| **Rationale** | Regra de três classes (BR-009) é critério objetivo; justificativa com classes citadas permite auditoria. |


#### T-012-001: Abrir e gerenciar alerta de multirresistência

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `gerenciar_alerta_multirresistencia` |
| **Descrição** | Abre alerta automaticamente e gerencia transições. PASSOS: (1) Ao detectar `multirresistente=true`, criar alerta com `{tipo, gravidade, situacao="aberto"}`; (2) Verificar se já existe alerta aberto para o caso — se sim, não duplicar; (3) PATCH /alertas/{id}/reconhecer → `situacao="reconhecido"`; (4) PATCH /alertas/{id}/encerrar → `situacao="encerrado"`; (5) PATCH /alertas/{id}/reabrir → `situacao="aberto"`; (6) Validar transições permitidas (aberto→reconhecido→encerrado; encerrado→aberto); (7) Gravar auditoria em cada transição. |
| **Agent** | `agente_alerta_multirresistencia` |
| **Tools** | `tool_crud_alerta`, `tool_validar_transicao`, `tool_auditoria_encadeada` |
| **Input Schema** | `{caso_id, acao: "abrir"\|"reconhecer"\|"encerrar"\|"reabrir", usuario_id}` |
| **Output Schema** | `{alerta_id, situacao, mensagem}` |
| **Módulo** | `modulo_alertas` |
| **UC Relacionado** | UC-012 |
| **RF Relacionado** | FR-033, FR-034 |
| **Rationale** | Transições controladas e verificação de duplicidade garantem integridade do fluxo de alertas. |


#### T-013-001: Redigir texto do alerta para a equipe (agêntica)

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `redigir_texto_alerta` |
| **Descrição** | Agente redige texto do alerta em linguagem clara. PASSOS: (1) Receber contexto `{antibiograma, microrganismo, origem_amostra, classificacao_nhsn, multirresistente}`; (2) LLM com prompt versionado redige texto explicando "o que houve" e "por que importa"; (3) Validar que texto cita microrganismo e origem — senão descartar e retornar erro; (4) Se dados insuficientes, retornar "Não foi possível redigir o alerta: dados insuficientes" (FR-044); (5) Persistir texto em `Alerta.texto_gerado`; (6) Registrar decisão com entrada/saída/versão/justificativa (BR-030). |
| **Agent** | `agente_redacao_alerta` |
| **Tools** | `tool_llm_prompt_versionado`, `tool_validar_texto_alerta`, `tool_registrar_decisao_agente` |
| **Input Schema** | `{alerta_id, antibiograma, microrganismo, origem_amostra, classificacao_nhsn}` |
| **Output Schema** | `{texto_gerado, versao_prompt}` ou `{erro: "dados_insuficientes"}` |
| **Módulo** | `modulo_agentes_ia` |
| **UC Relacionado** | UC-013 |
| **RF Relacionado** | FR-035, FR-083 |
| **Rationale** | Texto legível pela equipe assistencial reduz tempo de percepção; validação evita texto incompleto. |


#### T-014-001: Notificar coordenadora e enfermeiro por e-mail

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `notificar_alerta_email` |
| **Descrição** | Envia e-mail de alerta com retry e registro de falha. PASSOS: (1) POST /alertas/{id}/notificar; (2) Verificar configuração de e-mail — se ausente, retornar "Envio de e-mail não configurado" e NÃO marcar como enviada (BR-018); (3) Montar payload `{destinatarios: [coordenadora, enfermeiro], assunto, corpo}`; (4) Chamar `POST /email/send` com timeout 10s; (5) Em sucesso, persistir `Notificacao` com `{destinatario, canal="email", status="enviada", tempo_decorrido_ms}`; (6) Em falha, retry com backoff exponencial (1s, 5s, 30s, 5min, 30min); após 5ª falha, `status="falha"` e alerta permanece aberto (FR-038); (7) Gravar auditoria. |
| **Agent** | `agente_notificacao_email` |
| **Tools** | `tool_http_client_email`, `tool_retry_backoff`, `tool_persistir_notificacao`, `tool_auditoria_encadeada` |
| **Input Schema** | `{alerta_id, destinatarios, assunto, corpo}` |
| **Output Schema** | `{notificacao_id, status, tempo_decorrido_ms, tentativas}` |
| **Módulo** | `modulo_notificacao` |
| **UC Relacionado** | UC-014 |
| **RF Relacionado** | FR-036, FR-037, FR-038, FR-062, FR-073 |
| **Rationale** | Retry com backoff e registro de falha garantem que notificação não seja dada por enviada sem confirmação (BR-018). |


#### T-015-001: Recomendar bundle ao caso confirmado (agêntica)

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `recomendar_bundle_caso_confirmado` |
| **Descrição** | Agente recomenda bundle com justificativa. PASSOS: (1) Verificar caso `classificacao="confirmada"` — senão não acionar (FR-039); (2) Receber `{resultado_nhsn, multirresistente, bundles_cadastrados}`; (3) LLM com prompt versionado seleciona bundle compatível — se `multirresistente=false`, NÃO recomendar bundle de germe multirresistente (BR-012); (4) Redigir justificativa citando NHSN e multirresistência — senão descartar (FR-045); (5) Se dados insuficientes, retornar `decisao_agente="insuficiente"` (FR-044, FR-082); (6) Persistir `Recomendacao` com `{bundle_recomendado_id, justificativa, decisao_agente}`; (7) Registrar decisão com entrada/saída/versão/justificativa (BR-030). |
| **Agent** | `agente_recomendacao_bundle` |
| **Tools** | `tool_llm_prompt_versionado`, `tool_validar_compatibilidade_bundle`, `tool_registrar_decisao_agente` |
| **Input Schema** | `{caso_id, resultado_nhsn, multirresistente, bundles_cadastrados}` |
| **Output Schema** | `{bundle_recomendado_id?, justificativa, decisao_agente, versao_prompt}` |
| **Módulo** | `modulo_agentes_ia` |
| **UC Relacionado** | UC-015 |
| **RF Relacionado** | FR-039, FR-041, FR-043, FR-044, FR-045, FR-081, FR-082 |
| **Rationale** | Proibir bundle incompatível (BR-012) e declarar insuficiência (FR-082) evitam recomendação sem base. |


#### T-016-001: Cadastrar bundles com dados de risco

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `cadastrar_bundle` |
| **Descrição** | Cadastro de bundles restrito a administrador e coordenadora CCIH. PASSOS: (1) POST /bundles recebe `{nome, indicacao, reducao_media_risco, intervalo_confianca}`; (2) Validar papel ∈ {administrador, coordenadora_ccih} (FR-067); (3) Validar nome único; (4) Validar `reducao_media_risco` numérico; (5) Persistir com `ativo=true`; (6) Gravar auditoria. |
| **Agent** | `agente_cadastro_bundle` |
| **Tools** | `tool_crud_bundle`, `tool_validar_numerico`, `tool_auditoria_encadeada`, `tool_controle_acesso_papel` |
| **Input Schema** | `{nome, indicacao, reducao_media_risco, intervalo_confianca, usuario_id}` |
| **Output Schema** | `{bundle_id, mensagem}` |
| **Módulo** | `modulo_cadastros` |
| **UC Relacionado** | UC-016 |
| **RF Relacionado** | FR-040 |
| **Rationale** | Bundles alimentam a recomendação; validar nome único e valor numérico evita dados inconsistentes. |


#### T-017-001: Registrar escolha médica de outro bundle

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `registrar_escolha_medica_bundle` |
| **Descrição** | Médico escolhe bundle alternativo, preservando recomendação original. PASSOS: (1) POST /casos/{id}/recomendacao/escolher-bundle recebe `{bundle_escolhido_id}`; (2) Validar papel=médico (FR-067); (3) Validar caso `classificacao="confirmada"`; (4) Persistir `escolha_medica_bundle_id` na `Recomendacao`; (5) MANTER `bundle_recomendado_id` original (BR-031); (6) Gravar auditoria com `{usuario_id, bundle_original, bundle_escolhido}`. |
| **Agent** | `agente_escolha_bundle` |
| **Tools** | `tool_crud_recomendacao`, `tool_auditoria_encadeada`, `tool_controle_acesso_papel` |
| **Input Schema** | `{caso_id, bundle_escolhido_id, usuario_id}` |
| **Output Schema** | `{recomendacao_id, bundle_original, bundle_escolhido, mensagem}` |
| **Módulo** | `modulo_recomendacao` |
| **UC Relacionado** | UC-017 |
| **RF Relacionado** | FR-042 |
| **Rationale** | Preservar recomendação original permite auditar divergência entre sistema e decisão médica (BR-031). |


#### T-018-001: Estimar redução de risco do tratamento escolhido

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `estimar_reducao_risco` |
| **Descrição** | Calcula estimativa de redução de risco por horizonte. PASSOS: (1) POST /casos/{id}/estimativa recebe `{horizonte_dias ∈ {30, 90, 180}}` (BR-014); (2) Validar tratamento escolhido — senão bloquear; (3) Buscar `{idade_na_data, apache_ii, sitio_insercao}` do cadastro do caso (BR-013) — NÃO solicitar ao usuário; (4) Se faltar dado, retornar "Falta o dado: [nome]" (FR-061); (5) Aplicar fórmula fechada determinística (NFR-004) usando `reducao_media_risco` do bundle escolhido; (6) Retornar `{reducao_absoluta, reducao_relativa, intervalo_confianca}`; (7) Persistir; (8) Gravar auditoria. |
| **Agent** | `agente_estimativa_risco` |
| **Tools** | `tool_formula_reducao_risco`, `tool_buscar_dados_caso`, `tool_auditoria_encadeada` |
| **Input Schema** | `{caso_id, horizonte_dias}` |
| **Output Schema** | `{reducao_absoluta, reducao_relativa, intervalo_confianca, horizonte_dias}` |
| **Módulo** | `modulo_estimativa` |
| **UC Relacionado** | UC-018 |
| **RF Relacionado** | FR-046, FR-047, FR-048 |
| **Rationale** | Fórmula fechada (NFR-004) e uso de dados do cadastro (BR-013) garantem determinismo e consistência. |


#### T-019-001: Executar ciclo integrado de um caso

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `executar_ciclo_integrado` |
| **Descrição** | Orquestra seis etapas em sequência por comando único. PASSOS: (1) POST /casos/{id}/ciclo-integrado; (2) Validar papel=coordenadora_ccih; (3) Executar em ordem: (a) buscar microbiologia → (b) classificar NHSN → (c) detectar multirresistência → (d) calcular escore Cox → (e) recomendar bundle → (f) estimar redução; (4) Cada etapa retorna `{status: "concluida"\|"falhou"\|"nao_executada", resultado}`; (5) Se etapa falhar, etapas dependentes ficam `nao_executada` (FR-085); (6) Persistir `CicloIntegrado` com `{etapas_status (jsonb), resultado_por_etapa (jsonb)}`; (7) Retornar status de cada etapa (FR-050). |
| **Agent** | `agente_orquestrador_ciclo` |
| **Tools** | `tool_orquestrador_etapas`, `tool_persistir_ciclo`, `tool_auditoria_encadeada` |
| **Input Schema** | `{caso_id, usuario_id}` |
| **Output Schema** | `{ciclo_id, etapas: [{nome, status, resultado}]}` |
| **Módulo** | `modulo_ciclo_integrado` |
| **UC Relacionado** | UC-019 |
| **RF Relacionado** | FR-049, FR-050, FR-085 |
| **Rationale** | Orquestração com status por etapa permite identificar onde falhou e evita gravar valor indefensável (BR-022). |


#### T-020-001: Consultar painel de vigilância por período

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `consultar_painel_vigilancia` |
| **Descrição** | Exibe seis indicadores por período. PASSOS: (1) GET /painel?periodo ∈ {7, 30, 90, 365} (BR-015); (2) Calcular via SQL agregado: `casos_ativos = COUNT(*) WHERE estado='ativo' AND data_inicio >= NOW()-periodo`; `escore_medio = AVG(escore) WHERE data_calculo >= NOW()-periodo`; `classificacoes_nhsn = COUNT(*) WHERE classificacao IS NOT NULL`; `alertas_abertos = COUNT(*) WHERE situacao='aberto'`; `conformidade_mensal = GROUP BY month`; `distribuicao_faixa = GROUP BY faixa_risco`; (3) Se sem dados, exibir "Não há casos registrados neste período" (FR-063); (4) Índices em `caso.data_inicio` e `caso.estado` (P95 < 3s, NFR-006). |
| **Agent** | `agente_painel_vigilancia` |
| **Tools** | `tool_query_agregada_painel`, `tool_cache_painel`, `tool_auditoria_encadeada` |
| **Input Schema** | `{periodo_dias, usuario_id}` |
| **Output Schema** | `{casos_ativos, escore_medio, classificacoes_nhsn, alertas_abertos, conformidade_mensal, distribuicao_faixa}` |
| **Módulo** | `modulo_painel` |
| **UC Relacionado** | UC-020 |
| **RF Relacionado** | FR-051, FR-052 |
| **Rationale** | Agregações indexadas garantem performance (NFR-006); campo vazio com explicação evita valor inventado (BR-016). |


#### T-021-001: Exportar relatório de vigilância em PDF ou CSV

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `exportar_relatorio_vigilancia` |
| **Descrição** | Gera relatório em PDF/CSV por período e filtro. PASSOS: (1) POST /relatorios/exportar recebe `{periodo, formato ∈ {pdf, csv}, filtro_paciente?}` (BR-027); (2) Consultar casos, escores, classificações e alertas do período/filtro; (3) Gerar arquivo no formato escolhido; (4) Retornar `{arquivo_url, quantidade_registros}` (FR-055); (5) Se zero registros, informar "Foram exportados 0 registros" sem gerar arquivo vazio; (6) Gravar auditoria com `{usuario_id, periodo, filtro, quantidade}`. |
| **Agent** | `agente_exportacao_relatorio` |
| **Tools** | `tool_gerar_pdf`, `tool_gerar_csv`, `tool_query_relatorio`, `tool_auditoria_encadeada` |
| **Input Schema** | `{periodo, formato, filtro_paciente?, usuario_id}` |
| **Output Schema** | `{arquivo_url, quantidade_registros, formato}` |
| **Módulo** | `modulo_relatorios` |
| **UC Relacionado** | UC-021 |
| **RF Relacionado** | FR-053, FR-054, FR-055 |
| **Rationale** | Formatos restritos a PDF/CSV (BR-027) e contagem real de registros evitam relatório com dado indefensável. |


#### T-022-001: Sinalizar falhas e dados faltantes ao usuário

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `sinalizar_falhas_dados_faltantes` |
| **Descrição** | Middleware que garante exibição explícita de falhas. PASSOS: (1) Interceptar respostas de serviços externos e banco; (2) Em falha de laboratório, retornar "O laboratório está fora do ar" (FR-059); (3) Em falha de Cox, retornar "O serviço de escore não respondeu" (FR-060); (4) Em dado faltante, retornar "Falta o dado: [nome]" (FR-061); (5) Em e-mail não configurado, retornar "Envio de e-mail não configurado" (FR-062); (6) NUNCA exibir valor numérico em falha (FR-075, BR-022); (7) Campos sem dado aparecem vazios com explicação (FR-063). |
| **Agent** | `agente_tratamento_falhas` |
| **Tools** | `tool_middleware_falhas`, `tool_mensagens_padronizadas`, `tool_auditoria_encadeada` |
| **Input Schema** | `{origem: string, tipo_falha: string, contexto}` |
| **Output Schema** | `{mensagem_explicita, campo_afetado, acao_sugerida}` |
| **Módulo** | `modulo_tratamento_falhas` |
| **UC Relacionado** | UC-022 |
| **RF Relacionado** | FR-063, FR-075, FR-059, FR-060, FR-061, FR-062 |
| **Rationale** | Honestidade acima de tudo (BR-022): preferir "não consegui" a número indefensável em auditoria. |


#### T-023-001: Proteger credenciais e chamadas externas

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `proteger_credenciais_chamadas_externas` |
| **Descrição** | Credenciais em cofre de segredos; chamadas externas anonimizadas. PASSOS: (1) Credenciais de laboratório, Cox e e-mail residem APENAS em cofre de segredos (FR-068, FR-099); (2) Tela exibe credencial mascarada "••••••••"; (3) Antes de qualquer chamada externa, substituir `{nome, prontuario, data_nascimento}` por `uuid_anonimo` (FR-069, BR-021); (4) Validar que payload não contém dado identificável — senão bloquear e registrar; (5) Toda comunicação via HTTPS/TLS 1.3 (NFR-009); (6) Senha NUNCA em log/erro/tela (FR-066). |
| **Agent** | `agente_seguranca_credenciais` |
| **Tools** | `tool_cofre_segredos`, `tool_anonimizador`, `tool_validar_payload_anonimo`, `tool_auditoria_encadeada` |
| **Input Schema** | `{servico: "laboratorio"\|"cox"\|"email", payload}` |
| **Output Schema** | `{payload_anonimizado, credencial_resolvida: boolean}` |
| **Módulo** | `modulo_seguranca` |
| **UC Relacionado** | UC-023 |
| **RF Relacionado** | FR-068, FR-069, FR-064, FR-065, FR-066, FR-067, FR-070 |
| **Rationale** | Anonimização obrigatória (BR-021) e credenciais em cofre (FR-099) mitigam vazamento de dado de paciente e de credencial. |


#### T-024-001: Padronizar nomes de dados entre telas e banco

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `padronizar_nomes_dados` |
| **Descrição** | Dicionário de dados com nomes canônicos. PASSOS: (1) Manter dicionário com `{nome_canonico, descricao, telas[], tabelas[]}`; (2) Validar que mesmo dado tem mesmo nome em todas as telas e banco (FR-074); (3) Ex.: "Identificador do caso" = `caso_id` no banco em todas as telas; (4) Detectar inconsistências e destacar; (5) Permitir correção de nomenclatura com registro em auditoria; (6) Exportar dicionário em CSV. |
| **Agent** | `agente_dicionario_dados` |
| **Tools** | `tool_crud_dicionario`, `tool_validar_nomenclatura`, `tool_auditoria_encadeada` |
| **Input Schema** | `{acao: "validar"\|"corrigir"\|"exportar", dado?}` |
| **Output Schema** | `{inconsistencias: [], dados_padronizados: int}` |
| **Módulo** | `modulo_dicionario_dados` |
| **UC Relacionado** | UC-024 |
| **RF Relacionado** | FR-074, FR-070, FR-056 |
| **Rationale** | Consistência de nomenclatura (FR-074) evita ambiguidade em relatórios e auditoria. |


#### T-025-001: Sinalizar hemocultura pronta e suspeita de ICSAC

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `sinalizar_hemocultura_suspeita_icsac` |
| **Descrição** | Sinaliza caso com hemocultura pronta e destaca multirresistente. PASSOS: (1) Ao importar resultado disponível, acionar agente de tradução (UC-008); (2) Aplicar critério NHSN (UC-009); (3) Avaliar multirresistência (UC-011); (4) Se suspeita de ICSAC, aplicar rótulo "Hemocultura pronta — suspeita de ICSAC"; (5) Se `multirresistente=true`, aplicar marca "Prioritário — germe multirresistente" (FR-090); (6) Ordenar lista com prioritários primeiro (FR-087); (7) Se `situacao="pendente"` ou `"erro"`, NÃO sinalizar (BR-007); (8) Registrar critério, versão e origem do dado (FR-070). |
| **Agent** | `agente_sinalizacao_icsac` |
| **Tools** | `tool_orquestrador_sinalizacao`, `tool_marcar_prioritario`, `tool_auditoria_encadeada` |
| **Input Schema** | `{caso_id, resultado_hemocultura}` |
| **Output Schema** | `{sinalizacao, prioritario: boolean, criterio_aplicado, versao_criterio}` |
| **Módulo** | `modulo_sinalizacao` |
| **UC Relacionado** | UC-025 |
| **RF Relacionado** | FR-089, FR-090, FR-086, FR-087, FR-088 |
| **Rationale** | Reduzir tempo entre hemocultura pronta e percepção (NFR-016); destaque de multirresistente prioriza atenção clínica. |


#### T-026-001: Executar backup automatizado com RTO e RPO

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `executar_backup_automatizado` |
| **Descrição** | Backup incremental horário e completo diário. PASSOS: (1) Configurar `{periodicidade, horario, destino, retencao_dias, rto_alvo, rpo_alvo}`; (2) Backup incremental a cada 1h; completo diário; (3) RPO ≤ 1h; RTO ≤ 4h; (4) Em falha, manter último conjunto válido íntegro; (5) Teste de restauração trimestral com comparação de registros; (6) Registrar execução e teste em auditoria; (7) Criptografia em repouso AES-256-GCM no destino. |
| **Agent** | `agente_backup` |
| **Tools** | `tool_backup_incremental`, `tool_backup_completo`, `tool_teste_restauracao`, `tool_auditoria_encadeada` |
| **Input Schema** | `{acao: "configurar"\|"executar"\|"testar_restauracao", config?}` |
| **Output Schema** | `{execucao_id, data_hora, escopo, duracao, resultado, rpo_observado}` |
| **Módulo** | `modulo_backup` |
| **UC Relacionado** | UC-026 |
| **RF Relacionado** | FR-092, FR-056, FR-057, FR-070, FR-098 |
| **Rationale** | RTO/RPO definidos e testados garantem continuidade e defesa de classificações em auditoria. |


#### T-027-001: Monitorar disponibilidade dos serviços externos

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `monitorar_servicos_externos` |
| **Descrição** | Health check contínuo de laboratório, Cox e e-mail. PASSOS: (1) Endpoints `/health/lab`, `/health/cox`, `/health/email` respondendo em < 500ms; (2) Verificação no intervalo configurado (default 60s); (3) Após 5 falhas consecutivas em 60s, abrir circuit breaker por 2min (NFR-025); (4) Em indisponibilidade > 2min, enviar alerta à TI; (5) Exibir estado, tempo de resposta e última verificação; (6) Manter histórico de indisponibilidades; (7) Em falha, exibir mensagem explícita nas telas dependentes (FR-059, FR-060, FR-062). |
| **Agent** | `agente_monitoramento_servicos` |
| **Tools** | `tool_health_check`, `tool_circuit_breaker`, `tool_alerta_ti`, `tool_auditoria_encadeada` |
| **Input Schema** | `{servico, intervalo_verificacao, destinatario_ti}` |
| **Output Schema** | `{estado, tempo_resposta_ms, ultima_verificacao, historico_indisponibilidades}` |
| **Módulo** | `modulo_monitoramento` |
| **UC Relacionado** | UC-027 |
| **RF Relacionado** | FR-093, FR-059, FR-060, FR-062, FR-085, FR-094 |
| **Rationale** | Monitoramento contínuo evita falha silenciosa que comprometa classificação e notificação. |


#### T-028-001: Registrar erros com correlação por requisição

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `registrar_erros_correlacao` |
| **Descrição** | Log estruturado com correlation_id por requisição. PASSOS: (1) Gerar `correlation_id` (UUID v4) no início de cada requisição; (2) Propagar em todas as chamadas internas e externas; (3) Registrar erro estruturado `{correlation_id, data_hora, funcao_origem, servico_envolvido, mensagem_falha}`; (4) Painel de diagnóstico com filtros por período e serviço; (5) Exibir cadeia de execução por `correlation_id`; (6) NUNCA registrar senha ou dado de paciente (FR-066, FR-069); (7) Exportar lista de erros. |
| **Agent** | `agente_log_estruturado` |
| **Tools** | `tool_gerar_correlation_id`, `tool_persistir_log_estruturado`, `tool_painel_diagnostico`, `tool_auditoria_encadeada` |
| **Input Schema** | `{correlation_id, funcao_origem, servico_envolvido, mensagem_falha}` |
| **Output Schema** | `{log_id, correlation_id, cadeia_execucao: []}` |
| **Módulo** | `modulo_observabilidade` |
| **UC Relacionado** | UC-028 |
| **RF Relacionado** | FR-094, FR-085, FR-093 |
| **Rationale** | Correlação por requisição permite reconstruir cadeia entre telas, servidor e serviços externos. |


#### T-029-001: Criptografar dados de paciente em repouso

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `criptografar_dados_repouso` |
| **Descrição** | Criptografia AES-256-GCM em banco e arquivos de configuração. PASSOS: (1) Aplicar AES-256-GCM antes de gravar dado de paciente `{nome, data_nascimento, sexo, numero_prontuario}`; (2) Aplicar AES-256-GCM em arquivos de configuração sensíveis (credenciais); (3) Chave gerenciada em cofre de segredos com rotação a cada 24 meses; (4) Verificação periódica de conformidade; (5) Em falha de chave, NÃO gravar em texto aberto — retornar erro; (6) Exportar relatório de conformidade. |
| **Agent** | `agente_criptografia_repouso` |
| **Tools** | `tool_aes_256_gcm`, `tool_cofre_segredos`, `tool_verificar_criptografia`, `tool_auditoria_encadeada` |
| **Input Schema** | `{dados, tipo: "paciente"\|"configuracao"}` |
| **Output Schema** | `{dados_criptografados, status_criptografia, data_verificacao}` |
| **Módulo** | `modulo_seguranca` |
| **UC Relacionado** | UC-029 |
| **RF Relacionado** | FR-095, FR-068, FR-065 |
| **Rationale** | Criptografia em repouso complementa HTTPS em trânsito e protege dado de paciente em caso de acesso indevido ao banco. |


#### T-030-001: Aplicar política de retenção e descarte de dados

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `aplicar_retencao_descarte_dados` |
| **Descrição** | Retenção com prazos e descarte seguro. PASSOS: (1) Configurar `{dados_clinicos: prazo, dados_auditoria: prazo, notificacoes: prazo}`; (2) POST /retencao/simular calcula registros vencidos SEM apagar; (3) POST /retencao/executar exige confirmação e descarta registros vencidos; (4) Gerar relatório de descarte com `{data_execucao, responsavel, quantidade_por_categoria}`; (5) Auditor consulta relatórios em modo somente leitura; (6) Gravar auditoria de toda execução. |
| **Agent** | `agente_retencao_dados` |
| **Tools** | `tool_calcular_registros_vencidos`, `tool_descarte_seguro`, `tool_relatorio_descarte`, `tool_auditoria_encadeada` |
| **Input Schema** | `{acao: "simular"\|"executar"\|"configurar", prazos?}` |
| **Output Schema** | `{registros_descartados_por_categoria, relatorio_id}` |
| **Módulo** | `modulo_retencao` |
| **UC Relacionado** | UC-030 |
| **RF Relacionado** | FR-097, FR-056, FR-075 |
| **Rationale** | Evita retenção indefinida de dado pessoal (LGPD) e garante descarte rastreável. |


#### T-031-001: Gerenciar segredos e rotação de credenciais

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `gerenciar_segredos_rotacao` |
| **Descrição** | Credenciais em cofre com rotação periódica. PASSOS: (1) Cadastrar credencial de serviço externo no cofre de segredos; (2) POST /credenciais/{servico}/rotacionar recebe `{nova_credencial, periodicidade ∈ {30, 60, 90}}`; (3) Gravar diretamente no cofre — NUNCA em banco de aplicação, log ou tela; (4) Atualizar `data_ultima_rotacao`; (5) Rotação automática ao vencer prazo; (6) Testar conexão resolvendo credencial do cofre; (7) Gravar auditoria com `{usuario_id, acao, servico, resultado}` sem valor da credencial. |
| **Agent** | `agente_gestao_segredos` |
| **Tools** | `tool_cofre_segredos`, `tool_rotacao_credencial`, `tool_teste_conexao`, `tool_auditoria_encadeada` |
| **Input Schema** | `{servico, acao: "cadastrar"\|"rotacionar"\|"testar", nova_credencial?, periodicidade?}` |
| **Output Schema** | `{servico, data_ultima_rotacao, proxima_rotacao, status_politica}` |
| **Módulo** | `modulo_seguranca` |
| **UC Relacionado** | UC-031 |
| **RF Relacionado** | FR-099, FR-068 |
| **Rationale** | Rotação periódica e armazenamento em cofre mitigam exposição de credenciais (FR-099). |

### 4.1 Casos de Uso Agênticos → Tarefas

| Task ID | Task Nome | UC | RF | RN | Módulo |
|---------|-----------|-----|-----|-----|--------|
| T-AGN-001 | translate_lab_result_to_hospital_vocabulary | UC-008 | FR-023, FR-076, FR-077 | BR-007, BR-023, BR-030 | Classificação Clínica |
| T-AGN-002 | classify_case_by_nhsn_criterion | UC-009 | FR-024, FR-025, FR-026, FR-028, FR-078, FR-079, FR-091 | BR-010, BR-026, BR-030 | Classificação Clínica |
| T-AGN-003 | evaluate_multidrug_resistance | UC-011 | FR-031, FR-032, FR-080 | BR-009, BR-030 | Classificação Clínica |
| T-AGN-004 | draft_alert_text_for_care_team | UC-013 | FR-035, FR-083 | BR-023, BR-025, BR-030 | Recomendação Terapêutica |
| T-AGN-005 | recommend_bundle_with_justification | UC-015 | FR-039, FR-041, FR-043, FR-044, FR-045, FR-081, FR-082 | BR-012, BR-023, BR-030, BR-031 | Recomendação Terapêutica |

### 4.2 Casos de Uso Convencionais → SEM Agente (anotação obrigatória)

| UC | Título | Natureza | Motivo |
|----|--------|----------|--------|
| UC-001 | Autenticar Usuário com E-mail e Senha | convencional — sem agente | Login, sessão e token: código comum |
| UC-002 | Gerenciar Cadastro e Desativação de Usuários | convencional — sem agente | CRUD de usuário: código comum |
| UC-003 | Registrar Ações Relevantes em Trilha de Auditoria | convencional — sem agente | Gravação e consulta de log: código comum |
| UC-004 | Cadastrar Paciente com Cateter Venoso Central | convencional — sem agente | Cadastro: código comum |
| UC-005 | Registrar Episódio e Dados de Risco do Caso Clínico | convencional — sem agente | Cadastro: código comum |
| UC-006 | Consultar Escore de Risco de Cox no Serviço Externo | convencional — sem agente | Chamada de API externa + persistência: código comum |
| UC-007 | Importar Resultado de Hemocultura do Laboratório | convencional — sem agente | Chamada de API externa + deduplicação: código comum |
| UC-010 | Sobrescrever Classificação Automática com Justificativa | convencional — sem agente | Gravação de sobrescrita: código comum |
| UC-012 | Abrir e Gerenciar Alerta de Multirresistência | convencional — sem agente | Transição de estado do alerta: código comum |
| UC-014 | Notificar Coordenadora e Enfermeiro por E-mail | convencional — sem agente | Envio de e-mail: código comum |
| UC-016 | Cadastrar Bundles com Dados de Risco | convencional — sem agente | Cadastro: código comum |
| UC-017 | Registrar Escolha Médica de Outro Bundle | convencional — sem agente | Gravação de escolha: código comum |
| UC-018 | Estimar Redução de Risco do Tratamento Escolhido | convencional — sem agente | Fórmula fechada determinística: código comum |
| UC-019 | Executar Ciclo Integrado de um Caso | convencional — sem agente | Orquestração de etapas existentes: código comum |
| UC-020 | Consultar Painel de Vigilância por Período | convencional — sem agente | Agregação SQL: código comum |
| UC-021 | Exportar Relatório de Vigilância em PDF ou CSV | convencional — sem agente | Geração de arquivo: código comum |
| UC-022 | Sinalizar Falhas e Dados Faltantes ao Usuário | convencional — sem agente | Tratamento de erro é caminho de exceção dentro das tarefas |
| UC-023 | Proteger Credenciais e Chamadas Externas do Sistema | convencional — sem agente | Configuração de infraestrutura: código comum |
| UC-024 | Padronizar Nomes de Dados entre Telas e Banco | convencional — sem agente | Dicionário de dados: código comum |
| UC-025 | Sinalizar Hemocultura Pronta e Suspeita de ICSAC | agêntica — consolidada | Consolida UC-008 + UC-009 + UC-011 — output é orquestrado pelo código comum a partir de T-AGN-001, T-AGN-002, T-AGN-003 |
| UC-026 | Executar Backup Automatizado com RTO e RPO | convencional — sem agente | Operação de infraestrutura: código comum |
| UC-027 | Monitorar Disponibilidade dos Serviços Externos | convencional — sem agente | Health check: código comum |
| UC-028 | Registrar Erros com Correlação por Requisição | convencional — sem agente | Log estruturado: código comum |
| UC-029 | Criptografar Dados de Paciente em Repouso | convencional — sem agente | Criptografia de banco: código comum |
| UC-030 | Aplicar Política de Retenção e Descarte de Dados | convencional — sem agente | Job de descarte: código comum |
| UC-031 | Gerenciar Segredos e Rotação de Credenciais | convencional — sem agente | Gestão de cofre: código comum |

**Proporção final:** 5 tarefas agênticas / 31 casos de uso = **16,1%** — bem abaixo do limite de um terço. Confirma que o núcleo agêntico está corretamente restrito.

---

## 5. GRAFO DE DEPENDÊNCIAS (RESUMO VISUAL)

```
MÓDULO: Classificação Clínica (AG-01)
├─ T-AGN-001 (Traduzir Resultado do Laboratório)
│  ↓ (aproveitavel=true)
├─ T-AGN-002 (Classificar pelo Critério NHSN)
│  ↓
└─ T-AGN-003 (Avaliar Multirresistência)
   ↓ (multirresistente=true)
   └──→ [código comum abre alerta UC-012]

MÓDULO: Recomendação Terapêutica (AG-02)
├─ T-AGN-004 (Redigir Texto do Alerta)
│  ← depende de T-AGN-002 + T-AGN-003
│  ↓
└─ T-AGN-005 (Recomendar Bundle com Justificativa)
   ← depende de T-AGN-002 + T-AGN-003
   ↓
   └──→ [código comum registra recomendação UC-015]

CONSOLIDAÇÃO UC-025 (Sinalizar Hemocultura Pronta e Suspeita de ICSAC):
  T-AGN-001 → T-AGN-002 → T-AGN-003
       ↓          ↓          ↓
       └──────────┴──────────┘
                  ↓
       [código comum monta a sinalização:
        rótulo "Hemocultura pronta — suspeita de ICSAC"
        + destaque "Prioritário — germe multirresistente"
        + registro de critério/versão/origem em auditoria]

CICLO INTEGRADO (UC-019, convencional):
  [código comum orquestra em sequência:
   1. buscar microbiologia (UC-007, convencional)
   2. T-AGN-001 (traduzir)
   3. T-AGN-002 (classificar)
   4. T-AGN-003 (multirresistência)
   5. consultar escore Cox (UC-006, convencional)
   6. T-AGN-005 (recomendar bundle)
   7. estimar redução (UC-018, convencional)
   → status por etapa retornado ao usuário]
```

---

## 6. NOTA FINAL SOBRE FRONTEIRA AGÊNTICA / CONVENCIONAL

O sistema BioByte tem um núcleo agêntico deliberadamente estreito — **cinco julgamentos** que exigem interpretação contextualizada:

1. **Traduzir** (T-AGN-001) — mapear nomenclatura de laboratório para hospital.
2. **Classificar** (T-AGN-002) — aplicar critério NHSN com vigência temporal.
3. **Avaliar resistência** (T-AGN-003) — contar classes distintas com regra de três.
4. **Redigir alerta** (T-AGN-004) — comunicar para leitor específico.
5. **Recomendar bundle** (T-AGN-005) — cruzar classificação, resistência e compatibilidade.

Tudo o mais — login, cadastro, chamada ao Cox, importação do laboratório, estimativa, painel, relatório, auditoria, e-mail, backup, monitoramento, criptografia, retenção, segredos — é **código comum**. O tratamento de erro de qualquer tarefa agêntica é **caminho de exceção dentro da própria tarefa**, nunca tarefa própria. A consolidação do UC-025 nos outputs de T-AGN-001/002/003 respeita a instrução de não inflar o número de tarefas agênticas com sínteses que o código comum resolve.

A Matriz de Rastreabilidade (Seção 4) cobre os cinco UCs agênticos e anota explicitamente cada UC convencional como "convencional — sem agente", conforme exigido.