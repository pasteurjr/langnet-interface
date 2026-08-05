# Especificação Funcional - a3ae2f89-a7e1-44b2-9ea4-6b8394843c7a

**Versão:** 1.0  
**Data:** 03/08/2026  
**Baseado em:** Requisitos v1

---

## 1. Introdução

### 1.1 Objetivo do Documento
O objetivo deste documento é descrever detalhadamente as funcionalidades e requisitos não-funcionais do sistema de clínica médica com triagem por agentes de IA, fornecendo uma base sólida para a implementação e teste do projeto.

### 1.2 Escopo do Sistema
O escopo do sistema inclui:
- Fluxo completo de triagem utilizando agentes de IA.
- Cadastros de pacientes, médicos, especialidades e agentes.
- Registro de atendimentos/triagens, pré-diagnósticos, encaminhamentos e prontuários.
- Módulos de recepção, triagem, pré-atendimento, encaminhamentos, prontuário, dashboard e cadastros administrativos.
- Fluxo de consulta médica com validação/refutação do pré-diagnóstico e registro do diagnóstico final.

O escopo exclui:
- Integrações com sistemas externos de faturamento, TISS, farmácia, laboratório e telemedicina.
- Internação hospitalar e gestão de leitos.
- Prescrição eletrônica integrada a serviços externos.
- Agendamento online para o paciente.
- Aplicativos mobile nativos.

### 1.3 Definições, Acrônimos e Abreviações

| Termo | Definição |
|-------|-----------|
| IA    | Inteligência Artificial          |
| LGPD  | Lei Geral de Proteção de Dados Pessoais |
| CRM   | Conselho Regional de Medicina        |
| CPF   | Cadastro de Pessoas Físicas          |
| KPI   | Key Performance Indicator            |
| RPO   | Recovery Point Objective             |
| RTO   | Recovery Time Objective              |
| WCAG  | Web Content Accessibility Guidelines |
| RBAC  | Role-Based Access Control            |
| API   | Application Programming Interface    |
| DDoS  | Distributed Denial of Service      |
| XSS   | Cross-Site Scripting               |
| CSRF  | Cross-Site Request Forgery         |
| TLS   | Transport Layer Security           |
| AES   | Advanced Encryption Standard       |

### 1.4 Referências
- Documento de Requisitos v1 (03/08/2026)

---

## 2. Visão Geral do Sistema

### 2.1 Perspectiva do Sistema
O sistema será integrado em uma clínica médica, fornecendo um fluxo automatizado e eficiente para a triagem de pacientes utilizando agentes de IA, seguido por pré-atendimento especializado e encaminhamento para médicos humanos.

### 2.2 Principais Funcionalidades
- Triagem de pacientes com classificação automática de urgência.
- Pré-atendimento dirigido a especialidade com agente especialista.
- Encaminhamento automatizado de pacientes para médicos disponíveis.
- Registro detalhado no prontuário eletrônico do paciente.

### 2.3 Usuários e Características
| ID | Nome               | Papel                                  |
|----|--------------------|----------------------------------------|
| ACTOR-001 | Recepcionista/Atendente | Responsável pelo cadastro de pacientes, abertura de atendimentos, acompanhamento da fila de triagem e confirmação de encaminhamentos. |
| ACTOR-002 | Médico             | Responsável pela decisão clínica final.       |
| ACTOR-003 | Administrador        | Gerencia médicos, especialidades, agentes, agendas e usuários; audita o sistema.  |
| ACTOR-004 | Paciente             | Titular dos dados de saúde.                 |
| ACTOR-005 | Agente Hub de Triagem| Classifica urgência e roteia o paciente.      |
| ACTOR-006 | Agente Especialista  | Conduz pré-atendimento dirigido à especialidade.|
| ACTOR-007 | Agente de Encaminhamento | Seleciona médico disponível e cria encaminhamento.|
| ACTOR-008 | Agente de Registro/Prontuário | Consolida etapas no prontuário e gera resumo. |

### 2.4 Restrições Gerais
- O sistema deve ser compatível com a LGPD, garantindo sigilo médico e auditoria.
- A decisão final sempre será tomada por um médico humano.
- Somente agentes ativos devem participar do fluxo de triagem.

### 2.5 Premissas e Dependências
- Baseado em protocolos clínicos validados e revisados por corpo clínico.
- Uso de algoritmos de IA confiáveis para classificação de urgência e pré-diagnósticos.
- Integração com sistemas internos de agenda e disponibilidade médica.

---

## 3. Requisitos Cobertos por Esta Especificação

### 3.1 Requisitos Funcionais Cobertos

| ID (original) | Nome                                               | Prioridade |
|---------------|----------------------------------------------------|------------|
| FR-001        | Fluxo de Triagem por Agentes de IA                   | Alta       |
| FR-002        | CRUD de Pacientes                                  | Alta       |
| FR-003        | CRUD de Médicos                                    | Alta       |
| FR-004        | CRUD de Especialidades                             | Alta       |
| FR-005        | CRUD de Agentes de IA                              | Alta       |
| FR-006        | CRUD de Atendimentos/Triagens                      | Alta       |
| FR-007        | CRUD de Pré-diagnósticos                           | Alta       |
| FR-008        | CRUD de Encaminhamentos                            | Alta       |
| FR-009        | Agente de Triagem (Hub)                            | Alta       |
| FR-010        | Classificação de Urgência Manchester               | Alta       |
| FR-011        | Roteamento para Agente Especialista                | Alta       |
| FR-012        | Desvio de Casos Vermelhos                          | Alta       |
| FR-013        | Pré-atendimento por Especialista                   | Alta       |
| FR-014        | Geração de Pré-diagnóstico                         | Alta       |
| FR-015        | Agente de Encaminhamento                           | Alta       |
| FR-016        | Agente de Registro/Prontuário                      | Alta       |
| FR-017        | Módulo Recepção                                    | Alta       |
| FR-018        | Tela de Triagem Agentiva                           | Alta       |
| FR-019        | Tela de Pré-atendimento                            | Alta       |
| FR-020        | Tela de Encaminhamentos                            | Média      |
| FR-021        | Tela de Prontuário                                 | Alta       |
| FR-022        | Painel/Dashboard KPIs                              | Média      |
| FR-023        | Cadastros Administrativos                          | Média      |
| FR-024        | Modelo de Dados Relacional                         | Alta       |
| FR-025        | Orquestração de Agentes                            | Alta       |
| FR-026        | Versionamento de Prompts/Roteiros                  | Média      |
| FR-027        | Fallback Manual                                    | Alta       |
| FR-028        | Justificativa da Classificação                     | Alta       |
| FR-029        | Gestão de Consentimento LGPD                         | Alta       |
| FR-030        | Fluxo de Consulta Médica                           | Alta       |
| FR-031        | Agenda e Disponibilidade Médica                    | Alta       |

### 3.2 Requisitos Não-Funcionais Cobertos

| ID (original) | Categoria                | Métrica-chave                                |
|---------------|--------------------------|----------------------------------------------|
| NFR-001       | Confiabilidade           | 100% das etapas persistidas com agente, data/hora e identificador |
| NFR-002       | Segurança                | Registro imutável e recuperável para cada triagem |
| NFR-003       | Usabilidade              | Aviso visível e não dispensável nas telas de pré-diagnóstico |
| NFR-004       | Usabilidade              | Layout funcional em resoluções 320/768/1280 px |
| NFR-005       | Segurança                | Política de privacidade e controles implementados |
| NFR-006       | Segurança                | Matriz de permissões RBAC por papel/módulo     |
| NFR-007       | Segurança                | 100% das ações sensíveis registradas         |
| NFR-008       | Confiabilidade           | Disponibilidade mensal ≥ 99,9%               |
| NFR-009       | Performance              | KPI disponível no dashboard                  |
| NFR-010       | Segurança                | AES-256 em repouso; TLS 1.2+ em trânsito     |
| NFR-011       | Confiabilidade           | RPO ≤ 15 min; RTO ≤ 4 h                      |
| NFR-012       | Manutenibilidade         | Alertas configurados para latência, erro e indisponibilidade |
| NFR-013       | Segurança                | Limites configurados por IP e usuário          |
| NFR-014       | Performance              | 95% das triagens ≤ 10s; 95% pré-diagnósticos ≤ 60s, com escalabilidade horizontal do orquestrador |
| NFR-015       | Segurança                | Prazo de retenção validado com jurídico; descarte seguro após prazo |
| NFR-016       | Usabilidade              | Interface navegável por teclado; compatível com leitores de tela; contraste adequado |

### 3.3 Regras de Negócio Cobertas

| ID (original) | Descrição resumida                                                                                   |
|---------------|----------------------------------------------------------------------------------------------------|
| BR-001        | A classificação de urgência deve seguir protocolo tipo Manchester, com níveis verde, amarelo e vermelho. |
| BR-002        | Todo paciente classificado como vermelho deve ser desviado diretamente para Pronto-Socorro/Emergência.    |
| BR-003        | Pré-diagnósticos são apenas apoio à decisão; a decisão final é sempre do médico humano.                 |
| BR-004        | O Agente de Encaminhamento deve selecionar somente médicos disponíveis da especialidade determinada pelo pré-diagnóstico. |
| BR-005        | Cada especialidade médica deve ter um agente especialista associado.                                   |
| BR-006        | Somente agentes com status ativo devem ser considerados no roteamento e na execução do fluxo.          |
| BR-007        | O pré-diagnóstico deve conter hipóteses, nível de confiança e recomendação de exames.                  |
| BR-008        | A triagem deve registrar a queixa original, a classificação e a justificativa para fins de auditoria.  |
| BR-009        | O recepcionista/atendente deve confirmar os encaminhamentos gerados.                                 |
| BR-010        | O encaminhamento deve conter atendimento, especialidade, médico, prioridade e status.                |
| BR-011        | O processamento de dados de saúde pelos agentes exige consentimento prévio do paciente; em emergência/risco de vida comprovada, o atendimento pode iniciar antes do consentimento, com registro de justificativa no prontuário e solicitação de consentimento assim que possível. |

---

## 4. Detalhamentos Técnicos de RNFs (complementares ao requirements)

### 4.1 Métricas Concretas de Performance
- **NFR-009**: Tempo médio de triagem ≤ 30 segundos para 95% das solicitações.
- **NFR-014**: Latência da API de triagem < 200ms para 95% dos requests, throughput de 200 rps e suporte a 1.000 usuários simultâneos.

### 4.2 Políticas Operacionais
- **NFR-013**: Retry policies: up to 3 retries com backoff exponencial (initial delay 1s, factor 2).
- **NFR-008**: Circuit breaker para APIs de IA, threshold 5 falhas em 1 minuto; timeout de request 30 segundos.
- **NFR-014**: SLA: disponibilidade mensal ≥ 99.9%, resposta dentro do tempo estipulado.

### 4.3 Detalhes de Segurança/Compliance
- **NFR-010**: Criptografia AES-256-GCM para dados em repouso, TLS 1.3 para comunicações.
- **NFR-011**: Backups criptografados com AES-256; RPO ≤ 15 min, RTO ≤ 4h (restauração testada mensalmente).
- **Modelo de ameaças**: Top 5 riscos - injeção SQL, XSS, CSRF, DDoS, acesso não autorizado. Mitigações incluem validações de entrada, proteção contra força bruta e rate limiting.

---

## 5. Casos de Uso

### 5.1 Atores do Sistema
| ID | Nome               | Papel                                  |
|----|--------------------|----------------------------------------|
| ACTOR-001 | Recepcionista/Atendente | Responsável pelo cadastro de pacientes, abertura de atendimentos, acompanhamento da fila de triagem e confirmação de encaminhamentos. |
| ACTOR-002 | Médico             | Responsável pela decisão clínica final.       |
| ACTOR-003 | Administrador        | Gerencia médicos, especialidades, agentes, agendas e usuários; audita o sistema.  |
| ACTOR-004 | Paciente             | Titular dos dados de saúde.                 |
| ACTOR-005 | Agente Hub de Triagem| Classifica urgência e roteia o paciente.      |
| ACTOR-006 | Agente Especialista  | Conduz pré-atendimento dirigido à especialidade.|
| ACTOR-007 | Agente de Encaminhamento | Seleciona médico disponível e cria encaminhamento.|
| ACTOR-008 | Agente de Registro/Prontuário | Consolida etapas no prontuário e gera resumo. |

### 5.2 Especificação Detalhada de Casos de Uso

**UC-001: Cadastro de Pacientes**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Administrador                                                           |
| **Atores Secundários** | Nenhum                                                                  |
| **Objetivo**         | Cadastrar um novo paciente no sistema.                                  |
| **Pré-condições**    | Usuário está autenticado com permissão para cadastrar pacientes.            |
| **Pós-condições**    | Paciente registrado e dados armazenados no banco de dados.                |
| **RFs Relacionados** | FR-002                                                                  |
| **RNs Aplicáveis**   | Nenhum                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | O administrador acessa a tela de cadastro. | Sistema exibe a tela "Cadastro de Pacientes" com formulário para preenchimento (nome, CPF, data de nascimento etc.). |
| 2  | O administrador preenche todos os dados do paciente e clica em "Salvar". | Sistema valida os dados, grava no banco de dados e exibe mensagem "Paciente cadastrado com sucesso!". |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | O CPF informado já está registrado no sistema. | O administrador preenche os dados novamente. | Sistema exibe mensagem "CPF já cadastrado, tente outro CPF ou procure o paciente existente."              |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos.   | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | Formato de CPF inválido.               | Sistema exibe mensagem "Formato de CPF inválido. Tente novamente."                                       |

#### Wireframe da Interface

**Tela:** Cadastro de Pacientes

```
--- Formulário ---
Nome: [_____________________________]
CPF: [______________________________]
Data de Nascimento: [_________________________]
Contato: (XX) XXXX-XXXX
Convênio: [Selecione um convênio...]

[Salvar] [Cancelar]
```

**UC-002: Recepção & Triagem**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Agente Hub de Triagem                                                   |
| **Atores Secundários** | Recepcionista, Paciente                                                 |
| **Objetivo**         | Classificar urgência do paciente e rotear para especialidade correta.     |
| **Pré-condições**    | Paciente está sendo atendido na recepção; queixa inicial fornecida.       |
| **Pós-condições**    | Paciente classificado com nível de urgência e encaminhado.                |
| **RFs Relacionados** | FR-009, FR-010                                                          |
| **RNs Aplicáveis**   | BR-001                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Recepcionista preenche identificação do paciente (Nome, CPF, Data de Nascimento, Contato, Convênio) e queixa + sinais vitais. | Sistema registra os dados fornecidos pelo atendente/recepcionista.                                |
| 2  | Agente Hub de Triagem clica em "Iniciar Triagem". | Sistema identifica o paciente pelo CPF; se não existir, cadastra automaticamente; abre um Atendimento, gerando o atendimento_id. |
| 3  | Agente Hub de Triagem classifica urgência (verde/amarelo/vermelho) e escolhe especialidade da lista fechada. | Sistema calcula a classificação (verde/amarelo/vermelho) e justificativa; exibe resultado com urgência + especialidade roteada. |
| 4  | Se vermelho: sistema desvia para Pronto-Socorro. | Sistema exibe mensagem "Paciente deve ser encaminhado ao Pronto-Socorro imediatamente."            |
| 5  | Se amarelo/verde: sistema roteia para especialidade correspondente. | Sistema encontra agente especialista disponível e inicia pré-atendimento.                |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Sinais vitais ausentes; triagem continua com queixa em texto livre. | Agente Hub de Triagem classifica urgência apenas com base na queixa. | Sistema calcula a classificação e justificativa sem sinais vitais.                                      |
| A2 | Especialidade não identificada; fluxo de fallback manual. | Recepcionista inicia procedimento manual. | Sistema registra erro e notifica recepção para iniciar fallback.                                          |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Hub indisponível → fallback manual (FR-027). | Sistema registra falha e notifica recepção para iniciar fluxo de fallback.                            |
| E2 | Agente especialista sem resposta → nova tentativa e fallback. | Sistema tenta novamente o agente especialista; se falhar, inicia fallback.               |

#### Wireframe da Interface

**Tela:** Recepção & Triagem

```
┌──────────────────────────────────────────────────────┐
│  [Recepção & Triagem]                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  IDENTIFICAÇÃO DO PACIENTE                           │
│    Nome: [______]                                    │
│    CPF: [______]                                     │
│    Data de Nascimento: [______]                      │
│    Contato: [______]                                 │
│    Convênio: [______]                                │
│                                                      │
│  QUEIXA E SINAIS VITAIS                              │
│    Queixa: [______]                                  │
│    Pressão Arterial: [______ mmHg]                   │
│    Frequência Cardíaca: [______ bpm]                 │
│    Temperatura: [______ °C]                          │
│    SpO2: [______ %]                                  │
│                                                      │
│  AÇÃO EXPLÍCITA                                      │
│    [Iniciar Triagem (Executado pelo Agente Hub de Triagem)] |
│                                                      │
│  RESULTADO DO AGENTE                                 │
│    Classificação: [______]                           │
│    Justificativa: [______]                           │
│    Área de Destino: [Especialidade]                  │
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │ Encaminhar ao    │  │ Cancelar        │           │
│  │ Especialista     │  └─────────────────┘           │
│  └──────────────────┘                                │
└──────────────────────────────────────────────────────┘
```

**UC-003: Pré-atendimento por Especialista**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Agente Especialista                                                     |
| **Atores Secundários** | Paciente, Recepcionista                                                 |
| **Objetivo**         | Conduzir pré-atendimento dirigido à especialidade do paciente.             |
| **Pré-condições**    | Paciente classificado e roteado para especialidade correta pelo Hub.      |
| **Pós-condições**    | Pré-diagnóstico gerado com hipóteses, nível de confiança e recomendação de exames. |
| **RFs Relacionados** | FR-013                                                                  |
| **RNs Aplicáveis**   | BR-007                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Agente Especialista recebe paciente pelo atendimento_id.     | Sistema exibe roteiro de perguntas específico para a especialidade e campos para preenchimento das respostas do paciente.                                    |
| 2  | Agente Especialista conduz o roteiro de perguntas ao paciente e preenche as respostas fornecidas pelo paciente no formulário. | Sistema registra as respostas fornecidas pelo paciente.                                        |
| 3  | Agente Especialista clica em [Gerar Pré-diagnóstico com IA]. | Executado pelo Agente de Pré-atendimento, sistema gera pré-diagnóstico com hipóteses, nível de confiança e recomendação de exames. Sistema registra o pré-diagnóstico no banco de dados e exibe na tela "Pré-Diagnóstico Gerado". |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Paciente não responde a todas as perguntas.  | Agente Especialista solicita novamente.    | Sistema registra o que foi respondido e aguarda novas informações.                                       |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Agente Especialista indisponível → nova tentativa e fallback. | Sistema tenta novamente o agente especialista; se falhar, inicia fallback.               |

#### Wireframe da Interface

**Tela:** Pré-atendimento por Especialista

```
┌──────────────────────────────────────────────────────┐
│  [Pré-atendimento de Cardiologia]                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente: paciente_id                               │
│  Queixa inicial:                                     │
│    - Duração da dor?                                 │
│      [__________]                                    │
│    - Localização exata?                            │
│      [__________]                                    │
│    - Há outros sintomas associados?                  │
│      [__________]                                    │
│                                                      │
│  ┌──────────────────────┐                            │
│  │ Gerar Pré-diagnóstico│                            │
│  │ com IA               │                            │
│  └──────────────────────┘                            │
│                                                      │
│  Executado pelo Agente de Pré-atendimento            │
│                                                      │
│  Pré-Diagnóstico Gerado:                             │
│    - Hipóteses: Infarto agudo do miocárdio           │
│    - Nível de confiança: 85%                       │
│    - Exames sugeridos: ECG, TC coronário             │
│                                                      │
│  ┌──────────────────────┐                            │
│  │ Encaminhar ao Médico   │                            │
│  └──────────────────────┘                            │
└──────────────────────────────────────────────────────┘
```

**UC-004: Geração de Pré-diagnóstico**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Agente Especialista                                                     |
| **Atores Secundários** | Paciente, Recepcionista                                                 |
| **Objetivo**         | Gerar pré-diagnóstico com hipóteses, nível de confiança e recomendação de exames. |
| **Pré-condições**    | Pré-atendimento realizado pelo agente especialista.                       |
| **Pós-condições**    | Pré-diagnóstico gerado e registrado no sistema.                           |
| **RFs Relacionados** | FR-014                                                                  |
| **RNs Aplicáveis**   | BR-007                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Agente Especialista preenche os campos de entrada com base no atendimento_id e paciente_id. | Sistema exibe a interface com os dados do paciente e permite o agente especialista ajustar as informações se necessário. |
| 2  | Agente Especialista clica no botão "Gerar Pré-diagnóstico com IA". | Sistema executa o Agente de Geração de Pré-diagnóstico, exibindo a hipóteses, nível de confiança e recomendação de exames. |
| 3  | Agente Especialista revisa as informações geradas pela IA e ajusta se necessário. | Sistema atualiza os dados conforme as alterações do agente especialista.                                   |
| 4  | Agente Especialista clica no botão "Salvar". | Sistema registra o pré-diagnóstico no banco de dados e exibe na tela "Pré-Diagnóstico Gerado".             |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Paciente apresenta sintomas inconsistentes com hipóteses iniciais. | Agente Especialista ajusta as hipóteses e nível de confiança. | Sistema atualiza o pré-diagnóstico no banco de dados.                                                  |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Agente Especialista indisponível → nova tentativa e fallback. | Sistema tenta novamente o agente especialista; se falhar, inicia fallback.               |

#### Wireframe da Interface

**Tela:** Geração de Pré-diagnóstico

```
┌──────────────────────────────────────────────────────┐
│  [Geração de Pré-diagnóstico]                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ENTRADA                                             │
│  Paciente: paciente_id                               │
│  Queixa inicial: [_____]                             │
│  Sinais vitais: [_____]                              │
│  Outras observações: [_____]                         │
│                                                      │
│  AÇÃO EXPLÍCITA                                      │
│  ┌──────────────────────┐                            │
│  │ Gerar Pré-diagnóstico│                            │
│  │ com IA               │                            │
│  └──────────────────────┘                            │
│                                                      │
│  RESULTADO DO AGENTE                                 │
│  Executado pelo Agente de Geração de Pré-diagnóstico |
│  Hipóteses:                                          │
│    - [_____]                                         │
│    - [_____]                                         │
│    - [_____]                                         │
│                                                      │
│  Nível de Confiança: [___]%                          │
│  Recomendação de Exames:                             │
│    - [_____]                                         │
│    - [_____]                                         │
│    - [_____]                                         │
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │     Salvar       │  │    Cancelar     │           │
│  └──────────────────┘  └─────────────────┘           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UC-005: Agente de Encaminhamento**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Agente de Encaminhamento                                                |
| **Atores Secundários** | Recepcionista, Médico                                                   |
| **Objetivo**         | Selecionar médico disponível e criar encaminhamento para o paciente.      |
| **Pré-condições**    | Pré-diagnóstico gerado e registrado no sistema.                           |
| **Pós-condições**    | Encaminhamento criado e status definido como 'gerado'.                    |
| **RFs Relacionados** | FR-015                                                                  |
| **RNs Aplicáveis**   | BR-004                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Agente de Encaminhamento consulta a disponibilidade dos médicos da especialidade usando os identificadores atendimento_id e paciente_id. | Sistema busca médicos disponíveis e exibe lista na tela "Seleção de Médico".     |
| 2  | Agente seleciona médico disponível com base nos horários atuais. | Sistema registra o médico selecionado no encaminhamento e define status como 'gerado'.|
| 3  | Encaminhamento gerado é vinculado ao paciente, atendimento e pré-diagnóstico usando os identificadores atendimento_id e paciente_id. | Sistema salva o encaminhamento no banco de dados e notifica recepção.           |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Nenhum médico disponível → encaminhamento pendente e fila de espera. | Agente registra encaminhamento com status 'pendente'. | Sistema notifica recepção para monitorar disponibilidade do médico.                                    |
| A2 | Agenda alterada após seleção → validação em tempo real. | Agente verifica novamente a disponibilidade do médico selecionado. | Sistema atualiza lista de médicos disponíveis e permite nova seleção se necessário.                     |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Falha na consulta à disponibilidade dos médicos. | Sistema registra erro e notifica recepção para iniciar procedimento manual de encaminhamento.    |

#### Wireframe da Interface

**Tela:** Seleção de Médico

```
┌──────────────────────────────────────────────────────┐
│  [Seleção de Médico]                                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente ID: 12345678901                            │
│  Especialidade: Cardiologia                          │
│  Pré-diagnóstico: Angina de peito                    │
│                                                      │
│  Busca: [__________]                                 │
│                                                      │
│  | Nome         | Horário    | Ações            |   |
│  | Dr. João Silva | 14h às 15h | Ver Editar Excluir |   |
│  | Dra. Maria Oliveira | 16h às 17h | Ver Editar Excluir |   |
│                                                      │
│  [Selecione um médico...]                            │
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │    Encaminhar    │  │    Cancelar     │           │
│  └──────────────────┘  └─────────────────┘           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UC-006: Agente de Registro/Prontuário**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Agente de Registro/Prontuário                                             |
| **Atores Secundários** | Médico, Recepcionista                                                   |
| **Objetivo**         | Consolidar triagem, pré-diagnóstico e encaminhamento no prontuário do paciente.|
| **Pré-condições**    | Encaminhamento criado e status definido como 'gerado'.                    |
| **Pós-condições**    | Prontuário consolidado com todas as etapas; resumo gerado e acessível ao médico. |
| **RFs Relacionados** | FR-016                                                                  |
| **RNs Aplicáveis**   | Nenhum                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Agente de Registro preencher os dados da triagem, pré-diagnóstico e encaminhamento no prontuário usando atendimento_id e paciente_id. | Sistema registra os dados no prontuário do paciente e gera resumo para o médico. |
| 2  | Resumo gerado é vinculado ao paciente e histórico de atendimentos. | Sistema salva o resumo no banco de dados e notifica médico para revisão.         |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Dados incompletos na triagem ou pré-diagnóstico. | Agente de Registro solicita correções.   | Sistema registra a necessidade de atualização e notifica recepção para fornecer dados corretos.          |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Falha no registro dos dados.             | Sistema registra erro e notifica recepção para iniciar procedimento manual de registro.                 |

#### Wireframe da Interface

**Tela:** Registro/Prontuário

```
┌──────────────────────────────────────────────────────┐
│  [Registro/Prontuário]                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente ID: 12345678901                            │
│  Atendimento ID: ATN-001                             │
│                                                      │
│  Entrada:                                            │
│    - Queixa inicial: [Dor torácica]                  │
│    - Classificação de urgência: [Verde]              │
│    - Area de destino: [Cardiologia]                  │
│                                                      │
│  Pré-diagnóstico:                                    │
│    - Hipóteses: [Angina de peito, Apneia]            │
│    - Nível de confiança: [85%]                       │
│    - Exames sugeridos: [ECG, Teste de colesterol]    │
│                                                      │
│  Encaminhamento:                                     │
│    - Médico ID: MD-001                               │
│    - Prioridade: [Normal]                            │
│    - Status: [Gerado]                                │
│                                                      │
│  Resumo para o médico:                               │
│    - Paciente apresenta sintomas consistentes com angina de peito, recomenda-se realizar ECG e teste de colesterol. |
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │     Salvar       │  │    Cancelar     │           │
│  └──────────────────┘  └─────────────────┘           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UC-007: Consulta Médica**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Médico                                                                  |
| **Atores Secundários** | Paciente, Recepcionista                                                 |
| **Objetivo**         | Realizar consulta médica, validar ou refutar hipóteses do pré-diagnóstico e registrar diagnóstico final.|
| **Pré-condições**    | Prontuário consolidado e resumo gerado pelo agente de registro.             |
| **Pós-condições**    | Diagnóstico final registrado no prontuário; conduta/prescrição definida e atendimento encerrado.|
| **RFs Relacionados** | FR-030                                                                  |
| **RNs Aplicáveis**   | BR-003                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Médico visualiza o resumo do Agente de Registro usando atendimento_id e paciente_id. | Sistema exibe tela "Resumo do Pré-Diagnóstico" com informações consolidadas.                             |
| 2  | Médico valida ou refuta hipóteses apresentadas no pré-diagnóstico. | Sistema registra a validação/refutação das hipóteses.                                                |
| 3  | Médico registra diagnóstico final, conduta e prescrição para o paciente usando atendimento_id e paciente_id. | Sistema salva as informações no prontuário do paciente.                                            |
| 4  | Médico encerra o atendimento e associa ao CRM do médico responsável usando atendimento_id. | Sistema registra a conclusão da consulta no banco de dados e notifica recepção.               |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Médico solicita exames adicionais.           | Médico registra novos exames no prontuário usando atendimento_id e paciente_id. | Sistema salva os novos exames e atualiza o resumo para a próxima consulta.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Falha no registro das informações da consulta. | Sistema registra erro e notifica médico para iniciar procedimento manual de registro.                 |

#### Wireframe da Interface

**Tela:** Consulta Médica

```
┌──────────────────────────────────────────────────────┐
│  [Consulta Médica]                                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente ID: 1234567890                             │
│  Atendimento ID: 98765                               │
│                                                      │
│  Resumo do Pré-Diagnóstico:                          │
│    - Hipóteses: Angina de peito, Apneia              │
│    - Nível de confiança: 85%                         │
│    - Exames sugeridos: ECG, Teste de colesterol      │
│                                                      │
│  Diagnóstico Final:                                  │
│    [_____________________________]                   │
│                                                      │
│  Conduta:                                          │
│    [_____________________________]                   │
│                                                      │
│  Prescrição:                                       │
│    [_____________________________]                   │
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │     Salvar       │  │    Cancelar     │           │
│  └──────────────────┘  └─────────────────┘           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tela:** Resumo do Pré-Diagnóstico

```
┌──────────────────────────────────────────────────────┐
│  [Resumo do Pré-Diagnóstico]                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente ID: 1234567890                             │
│  Atendimento ID: 98765                               │
│                                                      │
│  Resumo do Agente de Registro:                       │
│    - Hipóteses: Angina de peito, Apneia              │
│    - Nível de confiança: 85%                         │
│    - Exames sugeridos: ECG, Teste de colesterol      │
│                                                      │
│  Diagnóstico Final:                                  │
│    [_____________________________]                   │
│                                                      │
│  Conduta:                                          │
│    [_____________________________]                   │
│                                                      │
│  Prescrição:                                       │
│    [_____________________________]                   │
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │     Salvar       │  │    Cancelar     │           │
│  └──────────────────┘  └─────────────────┘           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UC-008: Gestão de Consentimento LGPD**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Recepcionista                                                           |
| **Atores Secundários** | Paciente, Administrador                                                   |
| **Objetivo**         | Capturar e registrar consentimento do paciente para coleta, uso e compartilhamento de dados. |
| **Pré-condições**    | Paciente está sendo atendido na recepção; sistema não possui consentimento válido. |
| **Pós-condições**    | Consentimento registrado no prontuário do paciente.                          |
| **RFs Relacionados** | FR-029                                                                  |
| **RNs Aplicáveis**   | BR-011                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Recepcionista acessa tela de consentimento. | Sistema exibe tela "Consentimentos" com campo para busca por paciente_id e opções para cadastrar novo consentimento.      |
| 2  | Recepcionista seleciona paciente ou clica em [+ Novo] para cadastrar um novo consentimento. | Sistema exibe o formulário de cadastro/edição do consentimento, preenchendo automaticamente os dados do paciente com base no atendimento_id.                                    |
| 3  | Paciente lê os termos e concorda clicando em "Concordo". | Sistema registra o consentimento do paciente no prontuário, incluindo data/hora e versão do termo.     |
| 4  | Recepcionista confirma o registro do consentimento. | Sistema exibe mensagem "Consentimento registrado com sucesso!" e grava dados no banco de dados. |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Paciente revoga o consentimento.               | Recepcionista acessa tela de revogação e justifica a ação. | Sistema registra a revogação no prontuário e bloqueia novos processamentos, exceto em emergência comprovada. |
| A2 | Consentimento pendente por falta de dados do paciente. | Recepcionista solicita informações adicionais ao paciente. | Sistema aguarda preenchimento dos dados necessários para registro do consentimento.                        |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Paciente não concorda com os termos.     | Sistema exibe mensagem "Consentimento não registrado." e finaliza o atendimento sem coleta de dados adicionais.  |

#### Wireframe da Interface

**Tela:** Consentimentos

```
Busca por paciente_id: [__________]  [+ Novo]
| Paciente_ID   | Data/Hora       | Versão Termo | Ações            |
| ...           | ...             | ...          | Ver Editar Excluir |

--- Formulário ---
Paciente ID: [____] (preenchido automaticamente)
Termos e Condições:
- Coleta, uso e compartilhamento de dados pessoais
- Responsabilidade do paciente pela veracidade
- Direito a revogação do consentimento

Paciente concorda com os termos?
[ ] Concordo

[Savar] [Cancelar]
```

**UC-009: Fallback Manual**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Recepcionista, Administrador                                            |
| **Atores Secundários** | Paciente, Agente de IA                                                  |
| **Objetivo**         | Implementar procedimento alternativo quando um agente de IA estiver indisponível ou retornar erro. |
| **Pré-condições**    | Falha no funcionamento do agente de IA durante triagem/pre-atendimento/encaminhamento. |
| **Pós-condições**    | Procedimento manual iniciado; ação registrada com justificativa.            |
| **RFs Relacionados** | FR-027                                                                  |
| **RNs Aplicáveis**   | Nenhum                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Recepcionista identifica falha no agente de IA. | Sistema registra a falha e notifica administrador para iniciar procedimento manual.                    |
| 2  | Administrador inicia procedimento manual, definindo passos e responsáveis. | Sistema exibe tela "Procedimento Manual" com instruções detalhadas.                          |
| 3  | Recepcionista segue os passos do procedimento manual para atender o paciente. | Sistema registra cada ação realizada durante o fallback, incluindo justificativa.           |
| 4  | Fallback concluído; sistema retorna ao fluxo normal de triagem/pre-atendimento/encaminhamento. | Sistema notifica recepção/administrador sobre conclusão do fallback e restaura funcionalidade normal. |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Paciente não atendeu durante o procedimento manual. | Recepcionista registra a ausência e tenta novamente em uma próxima data. | Sistema salva os dados da ausência no prontuário e notifica administrador para agendar nova consulta.   |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Falha ao registrar o procedimento manual. | Sistema registra erro e notifica administrador para iniciar procedimento novamente.                        |

#### Wireframe da Interface

**Tela:** Procedimento Manual (Entrada)

```
┌──────────────────────────────────────────────────────┐
│  [Procedimento Manual]                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente: Maria Santos                              │
│  Atendimento ID: 12345                               │
│                                                      │
│  Queixa inicial:                                     │
│    [_____________________________]                   │
│                                                      │
│  Sinais vitais:                                      │
│    Pressão arterial: [____] mmHg                     │
│    Frequência cardíaca: [____] bpm                   │
│    Temperatura: [____] °C                            │
│    SpO2: [____] %                                    │
│                                                      │
│  Justificativa do fallback:                          │
│    [_____________________________]                   │
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │     Iniciar      │  │    Cancelar     │           │
│  └──────────────────┘  └─────────────────┘           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tela:** Procedimento Manual (Ação)

```
┌──────────────────────────────────────────────────────┐
│  [Procedimento Manual]                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente: Maria Santos                              │
│  Atendimento ID: 12345                               │
│                                                      │
│  Queixa inicial:                                     │
│    [Queixa informada]                                │
│                                                      │
│  Sinais vitais:                                      │
│    Pressão arterial: [valor] mmHg                    │
│    Frequência cardíaca: [valor] bpm                  │
│    Temperatura: [valor] °C                           │
│    SpO2: [valor] %                                   │
│                                                      │
│  Justificativa do fallback:                          │
│    [Justificativa informada]                         │
│                                                      │
│  ┌──────────────────┐                                │
│  │ Classificar Urgência │                            │
│  └──────────────────┘                                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tela:** Procedimento Manual (Resultado)

```
┌──────────────────────────────────────────────────────┐
│  [Procedimento Manual]                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Paciente: Maria Santos                              │
│  Atendimento ID: 12345                               │
│                                                      │
│  Queixa inicial:                                     │
│    [Queixa informada]                                │
│                                                      │
│  Sinais vitais:                                      │
│    Pressão arterial: [valor] mmHg                    │
│    Frequência cardíaca: [valor] bpm                  │
│    Temperatura: [valor] °C                           │
│    SpO2: [valor] %                                   │
│                                                      │
│  Justificativa do fallback:                          │
│    [Justificativa informada]                         │
│                                                      │
│  Classificação: Verde                                │
│  Especialidade Roteirizada: Gastroenterologia        │
│                                                      │
│  ┌──────────────────┐  ┌─────────────────┐           │
│  │ Encaminhar ao    │  │   Cancelar        │           │
│  │ Especialista     │  └─────────────────┘           │
│  └──────────────────┘                                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UC-010: Visualização de KPIs**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Administrador                                                           |
| **Atores Secundários** | Médico, Recepcionista                                                   |
| **Objetivo**         | Exibir KPIs operacionais do sistema para monitoramento e análise.          |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso ao dashboard.              |
| **Pós-condições**    | KPIs calculados e exibidos na tela.                                        |
| **RFs Relacionados** | FR-022                                                                  |
| **RNs Aplicáveis**   | Nenhum                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Administrador acessa o dashboard.        | Sistema exibe tela "Dashboard KPIs" com gráficos e métricas atualizadas.                                   |
| 2  | Sistema calcula KPIs operacionais baseados nos dados reais de atendimentos do dia. | Sistema exibe os KPIs na tela, incluindo atendimentos do dia, distribuição por especialidade, urgências e tempo médio de triagem. |
| 3  | Administrador visualiza os dados e analisa a performance do sistema. | Sistema permite interação com gráficos para detalhamento adicional dos KPIs.         |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Administrador solicita detalhes adicionais de algum KPI. | Sistema exibe tela com dados detalhados do KPI selecionado. | Sistema permite download dos dados em formato Excel para análise mais aprofundada.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Falha no cálculo dos KPIs.             | Sistema registra erro e notifica administrador para reiniciar o processo de cálculo.                     |

#### Wireframe da Interface

**Tela:** Dashboard KPIs

```
┌──────────────────────────────────────────────────────┐
│  [Dashboard KPIs]                                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Busca: [__________]                                 │
│                                                      │
│  Atendimentos do Dia:                                │
│    - Verde: 100                                      │
│    - Amarelo: 50                                     │
│    - Vermelho: 10                                    │
│                                                      │
│  Distribuição por Especialidade:                     │
│    - Cardiologia: 60%                                │
│    - Pediatria: 20%                                  │
│    - Gastroenterologia: 20%                          │
│                                                      │
│  Urgências:                                          │
│    - Total: 15                                       │
│                                                      │
│  Tempo Médio de Triagem (min):                       │
│    - P95: 28                                         │
│                                                      │
│  ┌──────────────────┐                                │
│  │     Detalhes     │                                │
│  └──────────────────┘                                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UC-011: Gestão de Agenda e Disponibilidade Médica**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Administrador                                                           |
| **Atores Secundários** | Médico, Agente de Encaminhamento                                        |
| **Objetivo**         | Gerenciar agenda e disponibilidade dos médicos para encaminhamentos.     |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de agendas.      |
| **Pós-condições**    | Agenda atualizada no sistema; disponibilidade consultada em tempo real pelo Agente de Encaminhamento.|
| **RFs Relacionados** | FR-031                                                                  |
| **RNs Aplicáveis**   | BR-004                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Administrador acessa tela de gestão de agendas. | Sistema exibe tela "Gestão de Agendas" com lista de médicos e seus horários atuais.                    |
| 2  | Administrador define novos horários ou bloqueios para os médicos. | Sistema registra as alterações na agenda do médico no banco de dados.                          |
| 3  | Agenda atualizada é consultada em tempo real pelo Agente de Encaminhamento para seleção de médicos disponíveis. | Sistema exibe a disponibilidade atualizada dos médicos ao Agente de Encaminhamento.         |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Médico solicita alterações em sua agenda.      | Administrador revisa e aprova as solicitações de alteração. | Sistema atualiza a agenda conforme solicitado pelo médico e notifica o médico sobre os novos horários.   |
| A2 | Agente de Encaminhamento consulta disponibilidade do médico após alterações na agenda. | Sistema fornece dados atualizados da disponibilidade do médico para seleção.                     |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Falha ao registrar alterações na agenda. | Sistema registra erro e notifica administrador para reiniciar o processo de atualização.                     |

#### Wireframe da Interface

**Tela:** Gestão de Agendas (Módulo B - CADASTROS)

```
Busca: [__________]  [+ Novo]
| Médico         | Segunda-feira   | Terça-feira   | Quarta-feira  | Quinta-feira  | Sexta-feira   | Sábado      | Domingo     | Ações            |
| Dr. João Silva | 08h às 12h      | 08h às 12h    | 08h às 12h    | -             | -             | -           | -           | Ver Editar Excluir |
| Dr. Maria Costa| 09h às 13h      | 09h às 13h    | 09h às 13h    | -             | -             | -           | -           | Ver Editar Excluir |

--- Formulário ---
Médico: [Selecionar médico...]
Segunda-feira: [Selecione horário...]  
Terça-feira: [Selecione horário...]    
Quarta-feira: [Selecione horário...]   
Quinta-feira: [Selecione horário...]   
Sexta-feira: [Selecione horário...]    
Sábado: [Selecione horário...]       
Domingo: [Selecione horário...]      
Bloqueios:
  Data: [______/______/______] Motivo: [____________]
[Bloquear]

[Salvar] [Cancelar]
```

**UC-012: CRUD de Agentes de IA**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Administrador                                                           |
| **Atores Secundários** | Nenhum                                                                  |
| **Objetivo**         | Gerenciar cadastros, edição e exclusão de agentes de IA.                 |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de agentes.      |
| **Pós-condições**    | Agentes de IA atualizados no sistema conforme ação realizada pelo administrador.|
| **RFs Relacionados** | FR-005                                                                  |
| **RNs Aplicáveis**   | BR-017                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Administrador acessa tela de gestão de agentes. | Sistema exibe tela "Gestão de Agentes" com lista de agentes ativos e inativos.                        |
| 2  | Administrador seleciona ação desejada (Ver/Editar/Excluir) para um agente específico. | Sistema apresenta formulário correspondente à ação selecionada (visualização, edição ou confirmação de exclusão). |
| 3  | Administrador preenche os dados necessários e clica em "Salvar". | Sistema registra as alterações no banco de dados e exibe mensagem de sucesso.             |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Administrador solicita exclusão de um agente ativo. | Sistema exibe mensagem confirmando a exclusão e solicitando justificativa. | Sistema registra a exclusão lógica do agente no banco de dados e notifica administrador sobre conclusão da operação. |
| A2 | Administrador edita o tipo de um agente existente. | Sistema valida as alterações e registra novos parâmetros do agente. | Sistema salva as alterações no banco de dados e exibe mensagem de sucesso.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos durante cadastro ou edição. | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | Tipo de agente inválido ou inconsistente com as regras de negócio. | Sistema exibe mensagem de erro e solicita correção dos dados fornecidos pelo administrador.               |

#### Wireframe da Interface

**Tela:** Gestão de Agentes (Módulo B - Cadastros)

```
Busca: [__________]  [+ Novo]
| Nome             | Tipo           | Status   | Ações            |
| Agente Hub       | Triagem        | Ativo    | Ver Editar Excluir |
| Agente Cardiologia | Especialidade  | Inativo  | Ver Editar Excluir |

--- Formulário ---
Nome: [_____________]  
Tipo: [_____________]  
Status: [Ativo] [Inativo]
[Salvar] [Cancelar]
```

**UC-013: CRUD de Especialidades**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Administrador                                                           |
| **Atores Secundários** | Nenhum                                                                  |
| **Objetivo**         | Gerenciar cadastros, edição e exclusão de especialidades médicas.        |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de especialidades.|
| **Pós-condições**    | Especialidades atualizadas no sistema conforme ação realizada pelo administrador.|
| **RFs Relacionados** | FR-004                                                                  |
| **RNs Aplicáveis**   | BR-018                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Administrador acessa tela de gestão de especialidades. | Sistema exibe tela "Gestão de Especialidades" com lista de especialidades ativas e inativas, campo de busca e ações por linha.    |
| 2  | Administrador seleciona ação desejada (Ver/Editar/Excluir) para uma especialidade específica. | Sistema apresenta formulário correspondente à ação selecionada (edição ou confirmação de exclusão). |
| 3  | Administrador preenche os dados necessários e clica em "Salvar". | Sistema registra as alterações no banco de dados e exibe mensagem de sucesso.             |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Administrador solicita exclusão de uma especialidade ativa. | Sistema exibe mensagem confirmando a exclusão e solicitando justificativa. | Sistema registra a exclusão lógica da especialidade no banco de dados e notifica administrador sobre conclusão da operação. |
| A2 | Administrador edita o nome de uma especialidade existente. | Sistema valida as alterações e registra novos parâmetros da especialidade. | Sistema salva as alterações no banco de dados e exibe mensagem de sucesso.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos durante cadastro ou edição. | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | Nome de especialidade inválido ou inconsistente com as regras de negócio. | Sistema exibe mensagem de erro e solicita correção dos dados fornecidos pelo administrador.               |

#### Wireframe da Interface

**Tela:** Gestão de Especialidades (Módulo B - CADASTROS)

```
Busca: [__________]  [+ Novo]
| Nome         | Status   | Ações            |
| Cardiologia  | Ativa    | Ver Editar Excluir |
| Pediatria    | Inativa  | Ver Editar Excluir |

--- Formulário ---
Nome da Especialidade: [____]  
Status: [Ativo/Inativo]
[Salvar] [Cancelar]
```

**UC-014: CRUD de Médicos**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Administrador                                                           |
| **Atores Secundários** | Nenhum                                                                  |
| **Objetivo**         | Gerenciar cadastros, edição e exclusão de médicos.                     |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de médicos.      |
| **Pós-condições**    | Médicos atualizados no sistema conforme ação realizada pelo administrador. |
| **RFs Relacionados** | FR-003                                                                  |
| **RNs Aplicáveis**   | BR-019                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Administrador acessa tela de gestão de médicos. | Sistema exibe tela "Gestão de Médicos" com lista de médicos ativos e inativos.                          |
| 2  | Administrador seleciona ação desejada (Ver/Editar/Excluir) para um médico específico. | Sistema apresenta formulário correspondente à ação selecionada (visão, edição ou confirmação de exclusão). |
| 3  | Administrador preenche os dados necessários e clica em "Salvar". | Sistema registra as alterações no banco de dados e exibe mensagem de sucesso.             |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Administrador solicita exclusão de um médico ativo com agendamentos futuros. | Sistema exibe mensagem confirmando a exclusão e solicitando justificativa. | Sistema registra a exclusão lógica do médico no banco de dados e notifica administrador sobre conclusão da operação. |
| A2 | Administrador edita o CRM de um médico existente. | Sistema valida as alterações e registra novos parâmetros do médico. | Sistema salva as alterações no banco de dados e exibe mensagem de sucesso.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos durante cadastro ou edição. | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | CRM inválido ou inconsistente com as regras de negócio. | Sistema exibe mensagem de erro e solicita correção dos dados fornecidos pelo administrador.               |

#### Wireframe da Interface

**Tela:** Gestão de Médicos (Módulo B - CADASTROS)

```
Busca: [__________]  [+ Novo]
| Nome           | CRM    | Especialidade      | Ações            |
| Dr. João Silva | 12345  | Cardiologia      | Ver Editar Excluir |
| Dra. Maria Oliveira | 67890 | Pediatria       | Ver Editar Excluir |

--- Formulário ---
Nome: [______________]  
CRM: [_____]   
Especialidade: [________________]
[Salvar] [Cancelar]
```

**UC-015: CRUD de Pacientes**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Recepcionista                                                           |
| **Atores Secundários** | Administrador                                                             |
| **Objetivo**         | Gerenciar cadastros, edição e exclusão de pacientes.                     |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de pacientes.     |
| **Pós-condições**    | Pacientes atualizados no sistema conforme ação realizada pelo ator.        |
| **RFs Relacionados** | FR-002                                                                  |
| **RNs Aplicáveis**   | BR-020                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Recepcionista acessa tela de gestão de pacientes. | Sistema exibe tela "Gestão de Pacientes" com lista de pacientes ativos e inativos, incluindo campo de busca e ações por linha.                       |
| 2  | Recepcionista seleciona ação desejada (Ver/Editar/Excluir) para um paciente específico. | Sistema apresenta formulário correspondente à ação selecionada (visualização, edição ou confirmação de exclusão). |
| 3  | Recepcionista preenche os dados necessários e clica em "Salvar". | Sistema registra as alterações no banco de dados e exibe mensagem de sucesso.             |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Recepcionista solicita exclusão de um paciente com histórico de atendimentos. | Sistema exibe mensagem confirmando a exclusão e solicitando justificativa. | Sistema registra a exclusão lógica do paciente no banco de dados e notifica recepcionista sobre conclusão da operação. |
| A2 | Recepcionista edita o CPF de um paciente existente. | Sistema valida as alterações e registra novos parâmetros do paciente. | Sistema salva as alterações no banco de dados e exibe mensagem de sucesso.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos durante cadastro ou edição. | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | CPF inválido ou inconsistente com as regras de negócio. | Sistema exibe mensagem de erro e solicita correção dos dados fornecidos pelo recepcionista.               |

#### Wireframe da Interface

**Tela:** Gestão de Pacientes

```
Busca: [__________]  [+ Novo]
| Nome         | CPF            | Telefone     | Ações            |
| Maria Santos   | 123.456.789-00 | (11) 98765-4321 | Ver Editar Excluir |
| João Silva     | 987.654.321-11 | (11) 12345-6789 | Ver Editar Excluir |

--- Formulário ---
Nome: [______________]  
CPF: [_______________]  
Telefone: [_________]  
Endereço: [_____________________]  
E-mail: [_____________________]  
[Salvar] [Cancelar]
```

**UC-016: CRUD de Atendimentos/Triagens**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Recepcionista                                                           |
| **Atores Secundários** | Agente Hub                                                              |
| **Objetivo**         | Gerenciar cadastros, edição e exclusão de atendimentos/triagens.          |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de atendimentos.| 
| **Pós-condições**    | Atendimentos/triagens atualizados no sistema conforme ação realizada pelo ator.|
| **RFs Relacionados** | FR-006                                                                  |
| **RNs Aplicáveis**   | BR-021                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Recepcionista acessa tela de "Recepção & Triagem". | Sistema exibe formulário para entrada de dados do paciente e sinais vitais.                            |
| 2  | Recepcionista preenche os campos (Nome, CPF, Data de Nascimento, Contato, Convênio, Queixa, Pressão Arterial, Frequência Cardíaca, Temperatura, SpO2) e clica em "Iniciar Triagem". | Sistema identifica o paciente pelo CPF; se não existir, cadastra automaticamente; abre um atendimento, gera atendimento_id. |
| 3  | Agente de triagem classifica a urgência (verde/amarelo/vermelho) e escolhe especialidade. | Sistema exibe a urgência e a especialidade roteada, redirecionando para o Pré-atendimento da especialidade escolhida. |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Recepcionista solicita exclusão de um atendimento em status concluído ou cancelado. | Sistema exibe mensagem confirmando a exclusão e solicitando justificativa. | Sistema registra a exclusão lógica do atendimento no banco de dados e notifica recepcionista sobre conclusão da operação. |
| A2 | Recepcionista edita a data/hora de um atendimento em status aberto. | Sistema valida as alterações e registra novos parâmetros do atendimento. | Sistema salva as alterações no banco de dados e exibe mensagem de sucesso.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos durante cadastro ou edição. | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | Data/hora inválida ou inconsistente com as regras de negócio. | Sistema exibe mensagem de erro e solicita correção dos dados fornecidos pelo recepcionista.               |

#### Wireframe da Interface

**Tela:** Recepção & Triagem

```
Paciente: [____]  
CPF: [____]
Data de Nascimento: [____]
Contato: [____]
Convênio: [____]
Queixa: [____]
Pressão Arterial: [____]
Frequência Cardíaca: [____]
Temperatura: [____]
SpO2: [____]

[Iniciar Triagem]

Urgência: [Resultado]
Especialidade Roteada: [Resultado]
```

**UC-017: CRUD de Pré-diagnósticos**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Agente Especialista                                                       |
| **Atores Secundários** | Médico                                                                  |
| **Objetivo**         | Gerenciar cadastros, edição e exclusão de pré-diagnósticos.                |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de pré-diagnósticos.|
| **Pós-condições**    | Pré-diagnósticos atualizados no sistema conforme ação realizada pelo ator.   |
| **RFs Relacionados** | FR-007                                                                  |
| **RNs Aplicáveis**   | BR-022                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Agente Especialista acessa a tela de gestão de pré-diagnósticos. | Sistema exibe tela "Gestão de Pré-Diagnósticos" com lista de pré-diagnósticos associados a atendimentos usando os identificadores (atendimento_id e paciente_id). |
| 2  | Agente Especialista seleciona ação desejada (Ver/Editar/Excluir) para um pré-diagnóstico específico. | Sistema apresenta formulário correspondente à ação selecionada (visualização, edição ou confirmação de exclusão), preenchendo campos com os dados do pré-diagnóstico usando os identificadores (atendimento_id e paciente_id). |
| 3  | Agente Especialista preenche os dados necessários e clica em "Salvar". | Sistema registra as alterações no banco de dados, associadas ao atendimento corrente, e exibe mensagem de sucesso.             |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Agente Especialista solicita exclusão de um pré-diagnóstico associado a atendimento em status concluído. | Sistema exibe mensagem confirmando a exclusão e solicitando justificativa. | Sistema registra a exclusão lógica do pré-diagnóstico no banco de dados, associada ao atendimento corrente, e notifica agente sobre conclusão da operação. |
| A2 | Agente Especialista edita as hipóteses de um pré-diagnóstico existente. | Sistema valida as alterações e registra novos parâmetros do pré-diagnóstico. | Sistema salva as alterações no banco de dados, associadas ao atendimento corrente, e exibe mensagem de sucesso.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos durante cadastro ou edição. | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | Hipóteses inválidas ou inconsistente com as regras de negócio. | Sistema exibe mensagem de erro e solicita correção dos dados fornecidos pelo agente especialista.               |

#### Wireframe da Interface

**Tela:** Gestão de Pré-Diagnósticos

```
Busca: [__________]  [+ Novo]
| Atendimento_id | Paciente_id | Hipóteses          | Ações            |
| ...         | ...      | ...                | Ver Editar Excluir |

--- Formulário ---
Atendimento_id: [____]
Paciente_id: [____]
Hipóteses: [___________________________________________________________]
Nível de Confiança: [____]  Exames Sugeridos: [___________________________________________________________]
[Salvar] [Cancelar]
```

**UC-018: CRUD de Encaminhamentos**

| Campo                | Detalhe                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Ator Principal**   | Agente de Encaminhamento                                                  |
| **Atores Secundários** | Recepcionista                                                           |
| **Objetivo**         | Gerenciar cadastros, edição e exclusão de encaminhamentos.               |
| **Pré-condições**    | Usuário está autenticado com permissão de acesso à gestão de encaminhamentos.|
| **Pós-condições**    | Encaminhamentos atualizados no sistema conforme ação realizada pelo ator.   |
| **RFs Relacionados** | FR-008                                                                  |
| **RNs Aplicáveis**   | BR-023                                                                  |

#### Fluxo Principal

| #  | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| 1  | Agente de Encaminhamento acessa tela de gestão de encaminhamentos. | Sistema exibe tela "Gestão de Encaminhamentos" com lista de encaminhamentos associados a atendimentos e campos para busca. |
| 2  | Agente de Encaminhamento seleciona um encaminhamento específico e clica em uma ação (Ver, Editar ou Excluir). | Sistema apresenta formulário correspondente à ação selecionada (visualização, edição ou confirmação de exclusão) com os dados do encaminhamento. |
| 3  | Agente de Encaminhamento preenche os dados necessários e clica em "Salvar". | Sistema registra as alterações no banco de dados e exibe mensagem de sucesso.             |

#### Fluxos Alternativos

| ID | Condição                                     | Ação do Ator                           | Resposta do Sistema                                                                                      |
|----|----------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| A1 | Agente de Encaminhamento solicita exclusão de um encaminhamento associado a atendimento em status concluído. | Sistema exibe mensagem confirmando a exclusão e solicitando justificativa. | Sistema registra a exclusão lógica do encaminhamento no banco de dados e notifica agente sobre conclusão da operação. |
| A2 | Agente de Encaminhamento edita a prioridade de um encaminhamento existente. | Sistema valida as alterações e registra novos parâmetros do encaminhamento. | Sistema salva as alterações no banco de dados e exibe mensagem de sucesso.                             |

#### Fluxos de Exceção

| ID | Erro/Problema                          | Resposta do Sistema                                                                                      |
|----|----------------------------------------|--------------------------------------------------------------------------------------------------------|
| E1 | Campos obrigatórios não preenchidos durante cadastro ou edição. | Sistema exibe mensagem "Por favor, preencha todos os campos obrigatórios."                                  |
| E2 | Prioridade inválida ou inconsistente com as regras de negócio. | Sistema exibe mensagem de erro e solicita correção dos dados fornecidos pelo agente de encaminhamento.               |

#### Wireframe da Interface

**Tela:** Gestão de Encaminhamentos (Módulo B - Cadastros)

```
Busca: [__________]  [+ Novo]
| Atendimento ID | Especialidade | Médico | Prioridade | Ações            |
| ...            | ...           | ...    | ...        | Ver Editar Excluir |

--- Formulário ---
Atendimento ID: [____]  
Especialidade: [____]   
Médico: [____]
Prioridade: [____]   
Motivo do Encaminhamento: [___________________________________________]
[Salvar] [Cancelar]
```

## 6. Modelo de Dados Conceitual

### 6.1 Entidades Principais

- **Paciente:** Pessoa atendida pela clínica.
- **Médico:** Profissional de saúde responsável pelo atendimento final.
- **Especialidade:** Área médica de atendimento.
- **Agente:** Agente de IA configurável para triagem, especialidade, encaminhamento ou registro.
- **Atendimento/Triagem:** Registro de um atendimento do paciente com triagem.
- **Pré-diagnóstico:** Resultado do agente especialista.
- **Encaminhamento:** Registro de encaminhamento para médico/especialidade.
- **Prontuário:** Histórico consolidado do paciente.

### 6.2 Relacionamentos

- **Paciente** possui vários **Atendimentos/Triagens** e **Prontuários**.
- **Médico** é responsável por diversos **Encaminhamentos** e está associado a uma **Especialidade**.
- **Especialidade** classifica diversos **Médicos** e está associada a um **Agente Especialista**.
- **Agente** realiza vários **Atendimentos/Triagens** e produz diversos **Pré-diagnósticos**.
- **Atendimento/Triagem** gera um único **Pré-diagnóstico** e múltipos **Encaminhamentos**, além de ser consolidado em um único **Prontuário**.

### 6.3 Atributos Principais

#### Entidade: Paciente
| Atributo | Tipo       | Descrição                                       |
|----------|------------|---------------------------------------------------|
| id       | Integer    | Identificador único do paciente                   |
| nome     | String     | Nome completo do paciente                         |
| CPF      | String     | Cadastro de Pessoa Física do paciente             |
| data_nascimento | Date | Data de nascimento do paciente                    |
| contato  | String     | Informações de contato do paciente                |
| convenio | String     | Convênio médico associado ao paciente             |
| historico| Text       | Histórico médico anterior                         |
| status   | Enum       | Status atual do paciente (ativo/inativo)          |
| consentimento | Boolean | Indicador de consentimento para processamento de dados |

#### Entidade: Médico
| Atributo         | Tipo       | Descrição                                       |
|------------------|------------|---------------------------------------------------|
| id               | Integer    | Identificador único do médico                   |
| nome             | String     | Nome completo do médico                         |
| CRM              | String     | Registro no Conselho Regional de Medicina (CRM)   |
| especialidade_id | Integer    | Referência para a especialidade médica          |
| contato          | String     | Informações de contato do médico                |
| disponibilidade  | Text       | Agendamento e disponibilidade do médico         |
| status           | Enum       | Status atual do médico (ativo/inativo)            |

#### Entidade: Especialidade
| Atributo             | Tipo       | Descrição                                       |
|----------------------|------------|---------------------------------------------------|
| id                   | Integer    | Identificador único da especialidade            |
| nome                 | String     | Nome da especialidade médica                    |
| descricao            | Text       | Descrição detalhada da especialidade            |
| agente_especialista_id | Integer  | Referência para o agente especialista associado |

#### Entidade: Agente
| Atributo             | Tipo       | Descrição                                       |
|----------------------|------------|---------------------------------------------------|
| id                   | Integer    | Identificador único do agente                   |
| nome                 | String     | Nome do agente de IA                            |
| tipo                 | Enum       | Tipo do agente (triagem, especialista, encaminhamento, registro) |
| especialidade_id     | Integer    | Referência para a especialidade associada       |
| prompt/roteiro       | Text       | Prompt ou roteiro configurado para o agente     |
| versao_prompt        | String     | Versão atual do prompt/roteiro                |
| status_ativo         | Boolean    | Indicador de ativação do agente                 |

#### Entidade: Atendimento/Triagem
| Atributo             | Tipo       | Descrição                                       |
|----------------------|------------|---------------------------------------------------|
| id                   | Integer    | Identificador único do atendimento              |
| paciente_id          | Integer    | Referência para o paciente                      |
| queixa               | Text       | Queixa inicial fornecida pelo paciente            |
| sinais_vitais        | Text       | Sinais vitais medidos durante a triagem           |
| classificacao_urgencia | Enum     | Classificação de urgência (verde/amarelo/vermelho)|
| justificativa        | Text       | Justificativa para a classificação de urgência    |
| area_destino         | String     | Área médica determinada após triagem            |
| data_hora            | DateTime   | Data e hora em que o atendimento foi aberto      |
| status               | Enum       | Status atual do atendimento                     |

#### Entidade: Pré-diagnóstico
| Atributo             | Tipo       | Descrição                                       |
|----------------------|------------|---------------------------------------------------|
| id                   | Integer    | Identificador único do pré-diagnóstico           |
| atendimento_id       | Integer    | Referência para o atendimento associado         |
| agente_id            | Integer    | Referência para o agente especialista             |
| hipoteses            | JSON       | Lista de hipóteses diagnósticas com justificativas|
| nivel_confianca      | Enum       | Nível de confiança do pré-diagnóstico (baixa/média/alta) |
| exames_sugeridos     | Text       | Exames sugeridos pelo agente especialista         |
| texto                | Text       | Texto detalhado do pré-diagnóstico               |
| versao_prompt        | String     | Versão do prompt/roteiro utilizado              |

#### Entidade: Encaminhamento
| Atributo             | Tipo       | Descrição                                       |
|----------------------|------------|---------------------------------------------------|
| id                   | Integer    | Identificador único do encaminhamento           |
| atendimento_id       | Integer    | Referência para o atendimento associado         |
| especialidade_id     | Integer    | Referência para a especialidade                 |
| medico_id            | Integer    | Referência para o médico                        |
| prioridade           | Enum       | Prioridade do encaminhamento (baixa/média/alta)   |
| status               | Enum       | Status atual do encaminhamento                  |
| data_hora            | DateTime   | Data e hora em que o encaminhamento foi criado    |

#### Entidade: Prontuário
| Atributo             | Tipo       | Descrição                                       |
|----------------------|------------|---------------------------------------------------|
| id                   | Integer    | Identificador único do prontuário               |
| paciente_id          | Integer    | Referência para o paciente                      |
| atendimento_id       | Integer    | Referência para o atendimento consolidado         |
| dados_consolidados   | JSON       | Dados consolidados do atendimento/triagem/pre-diagnóstico/encaminhamento |
| resumo_medico        | Text       | Resumo médico gerado pelo agente de registro      |
| data_atualizacao     | DateTime   | Data e hora da última atualização do prontuário    |

### 6.4 Regras de Integridade

- **Chaves Estrangeiras:**
  - `paciente_id` em `Atendimento/Triagem`, `Prontuário`, `Encaminhamento`.
  - `medico_id` em `Encaminhamento`.
  - `especialidade_id` em `Médico`, `Agente`.
  - `atendimento_id` em `Pré-diagnóstico`, `Encaminhamento`, `Prontuário`.
  - `agente_id` em `Pré-diagnóstico`.

- **Constraints Únicos:**
  - CRM na entidade `Médico`.
  - Agente Especialista associado na entidade `Especialidade`.

- **Exclusões Lógicas:**
  - Status `inativo` nas entidades `Paciente`, `Médico`, `Agente`.

## 7. Interfaces do Sistema

### 7.1 Interfaces de Usuário

#### MÓDULO A — ATENDIMENTO

##### Tela de Recepção & Triagem
**Descrição:** Interface para o atendimento inicial, incluindo cadastro automático e classificação de urgência.

--- ENTRADA ---
Identificação do Paciente:
- Nome: [____]
- CPF: [____]
- Data de Nascimento: [____]
- Contato: [____]
- Convênio: [____]

Queixa + Sinais Vitais:
- Queixa: [____]
- Pressão Arterial: [____]
- Frequência Cardíaca: [____]
- Temperatura: [____]
- SpO2: [____]

--- AÇÃO EXPLÍCITA ---
[Iniciar Triagem]

--- RESULTADO DO AGENTE ---
Classificação de Urgência: [Verde/Amarelo/Vermelho]  
Área de Destino: [Cardiologia/Pediatria/Gastroenterologia/Endocrinologia/Oncologia/Pronto-Socorro]  

##### Tela de Pré-atendimento do Especialista
**Descrição:** Permite que o agente especialista conduza o roteiro de perguntas e exiba o pré-diagnóstico.

--- ENTRADA ---
Respostas do Paciente:
1. [Pergunta 1]: [Resposta]
2. [Pergunta 2]: [Resposta]

--- AÇÃO EXPLÍCITA ---
[Gerar Pré-diagnóstico com IA]

--- RESULTADO DO AGENTE ---
Hipóteses: [Diagnóstico]  
Nível de Confiança: [Baixo/Médio/Alto]  
Exames Sugeridos: [Lista de Exames]

##### Tela de Encaminhamento ao Médico
**Descrição:** Lista encaminhamentos gerados, com o médico selecionado.

Busca: [__________]  [+ Novo]
| atendimento_id | paciente_id | Especialidade | Médico          | Prioridade | Status     | Ações            |
| -------------- | ----------- | ------------- | --------------- | ---------- | ---------- | ---------------- |
| 1              | 101         | Cardiologia   | Dr. João Silva  | Alta       | Confirmado | Ver Editar Excluir |

--- Formulário ---
atendimento_id: [____]  
paciente_id: [____]  
Especialidade: [____]  
Médico: [____]  
Prioridade: [____]  
Status: [____]   [Salvar] [Cancelar]

##### Tela de Prontuário e Consulta Médica
**Descrição:** Exibe o histórico consolidado de atendimentos do paciente.

| Data       | Queixa                | Classificação | Pré-diagnóstico | Encaminhamento         |
| ---------- | --------------------- | ------------- | --------------- | -------------------- |
| 10/08/2026 | Dor abdominal intensa | Vermelho      | Apendicite      | Pronto-Socorro       |

#### MÓDULO B — CADASTROS

##### Tela de Cadastro de Pacientes
**Descrição:** Interface para cadastro/edição de pacientes.

Busca: [__________]  [+ Novo]
| paciente_id | Nome     | Sobrenome | CPF      | Ações            |
| ----------- | -------- | --------- | -------- | ---------------- |
| 101         | Maria    | Santos    | 123456   | Ver Editar Excluir |

--- Formulário ---
paciente_id: [____]  
Nome: [____]  
Sobrenome: [____]  
CPF: [____]  
Data de Nascimento: [____]  
Contato: [____]  
Convênio: [____]   [Salvar] [Cancelar]

##### Tela de Cadastro de Médicos
**Descrição:** Interface para cadastro/edição de médicos.

Busca: [__________]  [+ Novo]
| médico_id | Nome     | Sobrenome | CRM      | Ações            |
| --------- | -------- | --------- | -------- | ---------------- |
| 201       | João     | Silva     | 654321   | Ver Editar Excluir |

--- Formulário ---
médico_id: [____]  
Nome: [____]  
Sobrenome: [____]  
CRM: [____]   [Salvar] [Cancelar]

##### Tela de Cadastro de Especialidades
**Descrição:** Interface para cadastro/edição de especialidades.

Busca: [__________]  [+ Novo]
| especialidade_id | Nome            | Ações            |
| -------------- | --------------- | ---------------- |
| 301            | Cardiologia     | Ver Editar Excluir |

--- Formulário ---
especialidade_id: [____]  
Nome: [____]   [Salvar] [Cancelar]

##### Tela de Cadastro de Agentes de IA
**Descrição:** Interface para cadastro/edição de agentes de IA.

Busca: [__________]  [+ Novo]
| agente_id | Nome     | Sobrenome | Função          | Ações            |
| --------- | -------- | --------- | --------------- | ---------------- |
| 401       | Ana      | Pereira   | Triagem         | Ver Editar Excluir |

--- Formulário ---
agente_id: [____]  
Nome: [____]  
Sobrenome: [____]  
Função: [____]   [Salvar] [Cancelar]

### 7.2 Interfaces de Hardware
[Se aplicável] Integração com hardware específico.

### 7.3 Interfaces de Software
APIs e integrações com sistemas externos.

- **API RESTful:** Para comunicação entre frontend e backend.
- **Webhooks:** Para notificações em tempo real (ex.: novos atendimentos, encaminhamentos).

### 7.4 Interfaces de Comunicação
Protocolos e padrões de comunicação.

- **HTTP/HTTPS:** Protocolo para comunicação web.
- **WebSocket:** Para comunicações em tempo real entre frontend e backend.

## 8. Regras de Negócio

**RN-001: Protocolo Manchester**
- **Descrição:** A classificação de urgência deve seguir protocolo tipo Manchester, com níveis verde, amarelo e vermelho.
- **Condições:** Quando o agente de triagem recebe uma queixa.
- **Ações:** Classificar a urgência com base nos critérios do protocolo Manchester.
- **Validações:** Verificação automática dos sinais vitais e queixas contra matriz clínica.

**RN-002: Desvio de Urgência Vermelha**
- **Descrição:** Todo paciente classificado como vermelho deve ser desviado diretamente para Pronto-Socorro/Emergência.
- **Condições:** Quando a urgência é classificada como vermelho pelo agente de triagem.
- **Ações:** Desviar o atendimento para o Pronto-Socorro/Emergência e notificar a recepção.
- **Validações:** Verificação automática da urgência após classificação.

**RN-003: Pré-diagnóstico como Apoio**
- **Descrição:** Pré-diagnósticos são apenas apoio à decisão; a decisão final é sempre do médico humano.
- **Condições:** Quando o agente especialista gera um pré-diagnóstico.
- **Ações:** Registrar o pré-diagnóstico e apresentá-lo ao médico para validação ou refutação.
- **Validações:** Verificação manual pelo médico antes de registrar o diagnóstico final.

**RN-004: Seleção de Médico Disponível**
- **Descrição:** O agente de encaminhamento deve selecionar somente médicos disponíveis da especialidade determinada pelo pré-diagnóstico.
- **Condições:** Quando o agente de encaminhamento precisa selecionar um médico.
- **Ações:** Consultar a disponibilidade do médico e selecioná-lo se disponível.
- **Validações:** Verificação automática da disponibilidade dos médicos na especialidade.

**RN-005: Agente Especialista por Especialidade**
- **Descrição:** Cada especialidade médica deve ter um agente especialista associado.
- **Condições:** Quando uma nova especialidade é criada ou atualizada.
- **Ações:** Associar um agente especialista à especialidade.
- **Validações:** Verificação automática da associação do agente com a especialidade.

**RN-006: Somente Agentes Ativos**
- **Descrição:** Somente agentes com status ativo devem ser considerados no roteamento e na execução do fluxo.
- **Condições:** Quando um agente está envolvido no fluxo de triagem.
- **Ações:** Verificar se o agente está ativo antes de usá-lo.
- **Validações:** Verificação automática do status do agente.

**RN-007: Estrutura do Pré-diagnóstico**
- **Descrição:** O pré-diagnóstico deve conter hipóteses, nível de confiança e recomendação de exames.
- **Condições:** Quando o agente especialista gera um pré-diagnóstico.
- **Ações:** Estruturar o pré-diagnóstico conforme especificado.
- **Validações:** Verificação automática da estrutura do pré-diagnóstico.

**RN-008: Registro de Justificativa**
- **Descrição:** A triagem deve registrar a queixa original, a classificação e a justificativa para fins de auditoria.
- **Condições:** Quando um atendimento é registrado.
- **Ações:** Registrar todos os detalhes da triagem.
- **Validações:** Verificação automática do registro dos dados.

**RN-009: Confirmação de Encaminhamento**
- **Descrição:** O recepcionista/atendente deve confirmar os encaminhamentos gerados.
- **Condições:** Quando um encaminhamento é criado pelo agente de encaminhamento.
- **Ações:** Solicitar confirmação do recepcionista.
- **Validações:** Verificação manual da confirmação.

**RN-010: Campos do Encaminhamento**
- **Descrição:** O encaminhamento deve conter atendimento, especialidade, médico, prioridade e status.
- **Condições:** Quando um novo encaminhamento é criado.
- **Ações:** Preencher todos os campos obrigatórios.
- **Validações:** Verificação automática da preenchimento dos campos.

**RN-011: Consentimento em Emergência**
- **Descrição:** O processamento de dados de saúde pelos agentes exige consentimento prévio do paciente; em emergência/risco de vida comprovada, o atendimento pode iniciar antes do consentimento, com registro de justificativa no prontuário e solicitação de consentimento assim que possível.
- **Condições:** Quando dados de saúde são processados para um paciente.
- **Ações:** Solicitar e registrar o consentimento; em caso de emergência, registrar a justificativa e solicitar o consentimento posteriormente.
- **Validações:** Verificação automática do consentimento ou registro da justificativa.

## 9. Fluxos de Trabalho

### 9.1 Processos Principais
- **Triagem Agentiva:**
  - Recepção abre atendimento com queixa e sinais vitais.
  - Agente Hub classifica urgência e registra justificativa.
  - Se vermelho → desvio para Pronto-Socorro.
  - Se amarelo/verde → roteia para especialista ativo.
  - Especialista conduz roteiro e gera pré-diagnóstico.

- **Encaminhamento e Confirmação:**
  - Agente de Encaminhamento consulta agenda/disponibilidade.
  - Gera encaminhamento (status gerado).
  - Apresenta encaminhamento para confirmação pela recepção.
  - Recepcionista confirma ou rejeita o encaminhamento.

- **Registro e Consulta Médica:**
  - Agente de Registro consolida triagem + pré-diagnóstico + encaminhamento.
  - Apresenta resumo ao médico.
  - Médico valida ou refuta hipóteses, registra diagnóstico final, conduta e encerra atendimento.

### 9.2 Interações entre Componentes
- **Recepção** comunica com **Agente Hub** para triagem.
- **Agente Hub** roteia para **Agente Especialista** baseado na especialidade.
- **Agente Especialista** gera pré-diagnóstico e comunica com **Agente de Encaminhamento**.
- **Agente de Encaminhamento** seleciona médico disponível e gera encaminhamento para **Recepção**.
- **Recepção** confirma ou rejeita o encaminhamento.
- **Agente de Registro** consolida triagem, pré-diagnóstico e encaminhamento no prontuário.

### 9.3 Sequências Críticas
- **Desvio para Emergência:**
  - Agente Hub classifica como vermelho.
  - Desvia automaticamente para Pronto-Socorro/Emergência.
  - Notifica recepção.

- **Fallback Manual:**
  - Agentes IA falham ou indisponíveis.
  - Procedimento de fallback manual acionado.
  - Ações registradas e justificativas documentadas.

## 10. Análise de Arquitetura Preliminar

### 10.1 Componentes e Serviços Necessários
- **Frontend Web Responsivo:** Interface para usuários (Recepcionista, Médico, Administrador).
- **Backend com API REST:** Orquestração e serviços.
- **Banco Relacional:** Persistência de dados.
- **Fila/Mensageria:** Assincronia e resiliência.
- **Observabilidade:** Métricas, logs e alertas.

### 10.2 Padrões de Interação
- **API RESTful:** Para comunicação entre frontend e backend.
- **Webhooks:** Para notificações em tempo real.

### 10.3 Integrações Externas
- **Pronto-Socorro/Emergência:** Sistema de atendimento para urgências vermelhas.
- **Laboratório:** Sistema de exames médicos.
- **Telemedicina:** Sistema de consultas virtuais (não integrado neste escopo).

### 10.4 Considerações de Performance
- **P95 < 300ms** para respostas do agente Hub.
- **Throughput 100 rps** para triagens simultâneas.
- **Concurrent users 200** durante pico de atendimentos.

### 10.5 Considerações de Segurança
- **Criptografia AES-256-GCM** em repouso.
- **TLS 1.3** em trânsito.
- **Rate Limiting** e proteção contra ataques DDoS.
- **Circuit Breakers** para evitar sobrecarga.

### 10.6 Considerações de Escalabilidade
- **Scalabilidade horizontal** do orquestrador.
- **Sharding** do banco de dados para suportar grande volume de atendimentos.

### 10.7 Tecnologias Recomendadas
- **Frontend:** React.js ou Angular para interface responsiva.
- **Backend:** Node.js com Express ou Spring Boot.
- **Banco Relacional:** PostgreSQL ou MySQL.
- **Fila/Mensageria:** RabbitMQ ou Kafka.
- **Observabilidade:** Prometheus e Grafana.

## 11. Controle de Qualidade

### 11.1 Critérios de Aceitação Gerais
- **Testes Unitários:** Cobertura mínima de 90% para códigos backend.
- **Testes de Integração:** Todos os fluxos principais testados.
- **Testes de Usabilidade:** Interfaces acessíveis e intuitivas.
- **Testes de Segurança:** Verificação de vulnerabilidades com OWASP.

### 11.2 Estratégia de Testes
- **Ambiente de Teste:** Cópia do ambiente produtivo para testes.
- **Casos de Teste:** Documentação detalhada de todos os casos de uso e exceções.
- **Testes de Performance:** Simulação de carga para validação de desempenho.

### 11.3 Riscos Identificados
- **Risco Técnico:**
  - Falha nos agentes de IA durante a triagem.
  - Sobrecarga no sistema durante pico de atendimentos.
- **Risco de Negócio:**
  - Processamento indevido de dados sem consentimento do paciente.
  - Erros críticos na classificação de urgência.

### 11.4 Complexidades Previstas
- **Complexidade Técnica:** Integração e orquestração dos agentes de IA.
- **Complexidade Operacional:** Gerenciamento da disponibilidade dos médicos e especialidades.

## 12. Glossário

**Agente de IA:** Componente de software baseado em IA configurável para tarefas específicas, como triagem, especialista, encaminhamento ou registro.
**Prontuário:** Registro consolidado e histórico dos atendimentos do paciente.
**Encaminhamento:** Registro de direcionamento do paciente a um médico/especialidade.
**Orquestração:** Coordenação da execução sequencial de agentes e persistência de cada etapa.
**Roteamento:** Ação de direcionar o paciente ao agente especialista da área correta.
**Fallback:** Procedimento alternativo quando um agente falha ou está indisponível.
**Consentimento:** Autorização do titular para tratamento de dados pessoais sensíveis.
**Sinais vitais:** Medidas fisiológicas como pressão, frequência cardíaca, saturação e temperatura.
**CRM:** Registro do médico no Conselho Regional de Medicina.
**CID-10:** Classificação Internacional de Doenças.
**RPO:** Recovery Point Objective - perda máxima de dados aceitável.
**RTO:** Recovery Time Objective - tempo máximo para recuperação.
**WCAG:** Diretrizes de acessibilidade para conteúdo web.
**RBAC:** Controle de acesso baseado em papéis.

## 13. Rastreabilidade

### 13.1 Matriz de Rastreabilidade
| Requisito Original | Seção Especificação | RF | UC | RN |
|--------------------|---------------------|----|----|-----|
| FR-001             | 5.2                 | FR-001 | UC-001 | Nenhum |
| FR-002             | 7.1                 | FR-002 | UC-002, UC-015 | Nenhum |
| FR-003             | 7.1                 | FR-003 | UC-003, UC-014 | RN-005 |
| FR-004             | 7.1                 | FR-004 | UC-004, UC-016 | RN-005 |
| FR-005             | 7.1                 | FR-005 | UC-005, UC-017 | Nenhum |
| FR-006             | 7.1                 | FR-006 | UC-006, UC-018 | RN-008 |
| FR-007             | 7.1                 | FR-007 | UC-007, UC-019 | Nenhum |
| FR-008             | 7.1                 | FR-008 | UC-008, UC-020 | RN-009, RN-010 |
| FR-009             | 5.2                 | FR-009 | UC-009 | RN-001 |
| FR-010             | 5.2                 | FR-010 | UC-009 | RN-001 |
| FR-011             | 5.2                 | FR-011 | UC-009 | Nenhum |
| FR-012             | 5.2                 | FR-012 | UC-009 | RN-002 |
| FR-013             | 5.2                 | FR-013 | UC-010 | RN-007 |
| FR-014             | 5.2                 | FR-014 | UC-010 | Nenhum |
| FR-015             | 5.2                 | FR-015 | UC-011 | RN-004, RN-009 |
| FR-016             | 5.2                 | FR-016 | UC-012 | Nenhum |
| FR-017             | 7.1                 | FR-017 | UC-002 | Nenhum |
| FR-018             | 7.1                 | FR-018 | UC-009 | RN-001, RN-002 |
| FR-019             | 7.1                 | FR-019 | UC-010 | Nenhum |
| FR-020             | 7.1                 | FR-020 | UC-011 | RN-009, RN-010 |
| FR-021             | 7.1                 | FR-021 | UC-013 | Nenhum |
| FR-022             | 5.2                 | FR-022 | UC-014 | Nenhum |
| FR-023             | 7.1                 | FR-023 | UC-003, UC-014 | RN-005 |
| FR-024             | 6                   | FR-024 | Nenhum | Nenhum |
| FR-025             | 5.2                 | FR-025 | Nenhum | Nenhum |
| FR-026             | 7.1                 | FR-026 | UC-003, UC-014 | Nenhum |
| FR-027             | 5.2                 | FR-027 | UC-009, UC-011 | Nenhum |
| FR-028             | 7.1                 | FR-028 | UC-006, UC-009 | RN-001, RN-008 |
| FR-029             | 5.2                 | FR-029 | UC-002, UC-006 | RN-011 |
| FR-030             | 7.1                 | FR-030 | UC-013 | Nenhum |
| FR-031             | 5.2                 | FR-031 | UC-011, UC-014 | RN-004 |
| BR-001             | 8                   | Nenhum | UC-009 | RN-001 |
| BR-002             | 8                   | Nenhum | UC-009, UC-011 | RN-002 |
| BR-003             | 8                   | Nenhum | UC-010, UC-013 | RN-003 |
| BR-004             | 8                   | Nenhum | UC-011 | RN-004 |
| BR-005             | 8                   | Nenhum | UC-004, UC-016 | RN-005 |
| BR-006             | 8                   | Nenhum | UC-009, UC-011 | RN-006 |
| BR-007             | 8                   | Nenhum | UC-007, UC-010 | RN-007 |
| BR-008             | 8                   | Nenhum | UC-006, UC-009 | RN-008 |
| BR-009             | 8                   | Nenhum | UC-011 | RN-009 |
| BR-010             | 8                   | Nenhum | UC-008 | RN-010 |
| BR-011             | 8                   | Nenhum | UC-002, UC-006 | RN-011 |

## 14. Apêndices

### 14.1 Histórico de Versões
| Versão | Data | Descrição | Autor |
|--------|------|-----------|-------|
| 1.0 | 03/08/2026 | Versão inicial baseada em Requisitos v1 | Sistema |

### 14.2 Aprovações
[Seção para registrar aprovações futuras]