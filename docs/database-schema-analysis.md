# Análise Detalhada do Esquema de Banco de Dados - LangNet

**Data**: 2025-11-07
**Versão**: 1.0
**Projeto**: LangNet Interface
**Banco de Dados**: MySQL `langnet`

---

## Índice

1. [Introdução](#introdução)
2. [Arquitetura Geral](#arquitetura-geral)
3. [Análise Detalhada das Tabelas](#análise-detalhada-das-tabelas)
   - [1. users](#1-tabela-users)
   - [2. projects](#2-tabela-projects--existente)
   - [3. documents](#3-tabela-documents--faltando)
   - [4. specifications](#4-tabela-specifications--faltando)
   - [5. agents](#5-tabela-agents--faltando)
   - [6. tasks](#6-tabela-tasks--faltando)
   - [7. yaml_files](#7-tabela-yaml_files--faltando)
   - [8. code_generations](#8-tabela-code_generations--faltando)
   - [9. execution_sessions](#9-tabela-execution_sessions--existente)
   - [10. task_executions](#10-tabela-task_executions--existente)
   - [11. execution_outputs](#11-tabela-execution_outputs--existente)
   - [12. verbose_logs](#12-tabela-verbose_logs--existente)
   - [13. mcp_connections](#13-tabela-mcp_connections--faltando)
   - [14. monitoring_metrics](#14-tabela-monitoring_metrics--faltando)
4. [Matriz de Relacionamentos](#matriz-de-relacionamentos)
5. [Resumo Executivo](#resumo-executivo)

---

## Introdução

Este documento apresenta uma análise detalhada campo por campo de todas as tabelas necessárias para o sistema LangNet. Para cada campo, são especificados:

- **Significado**: O que o campo representa
- **Onde é necessário**: Referência aos requisitos (requisitosv0.2.txt)
- **Onde é usado**: Páginas da interface que utilizam o campo

### Legenda de Status

- ✅ **EXISTENTE**: Tabela já criada no banco `langnet`
- ❌ **FALTANDO**: Tabela precisa ser criada

### Conexão com Banco

- **Host**: camerascasas.no-ip.info:3308
- **Database**: `langnet`
- **User**: producao

---

## Arquitetura Geral

O sistema LangNet utiliza uma **arquitetura híbrida**:

1. **Rede de Petri em JSON**: Armazenada em `projects.project_data` (LONGTEXT)
2. **Dados Normalizados**: Tabelas separadas para consultas e relacionamentos
3. **Sincronização**: O JSON da rede e as tabelas normalizadas são mantidos sincronizados

### Fluxo de Dados

```
Documentos → Especificação → Agentes/Tarefas → YAML → Rede de Petri → Código Python → Execução
```

---

## Análise Detalhada das Tabelas

---

## 1. TABELA: `users`

### Propósito
Autenticação e gestão de usuários do sistema.

### Status
✅ **EXISTENTE** - Implementada e funcional

### Estrutura SQL

```sql
CREATE TABLE users (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_name (name),
  INDEX idx_created_at (created_at)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único do usuário | **3.2** Requisitos de Segurança - Controle de acesso baseado em papéis | - SettingsPage (UserManagement)<br>- Header (perfil do usuário)<br>- Todas as operações (audit trail) |
| **name** | VARCHAR(255) | NO | Nome completo do usuário | **3.2** Requisitos de Segurança - Identificação de usuários | - Header (nome exibido)<br>- SettingsPage (perfil)<br>- ProjectList (criador do projeto) |
| **email** | VARCHAR(255) | NO | Email para login e notificações | **3.2** Requisitos de Segurança - Autenticação<br>**2.8.3** Alertas e Notificações - Canais de notificação | - Tela de Login<br>- SettingsPage (NotificationSettings) |
| **password_hash** | VARCHAR(255) | NO | Hash da senha (bcrypt/argon2) | **3.2** Requisitos de Segurança - Criptografia | - Backend apenas (nunca enviado ao frontend) |
| **created_at** | TIMESTAMP | NO | Data de criação da conta | Audit trail | - SettingsPage (informações da conta) |
| **updated_at** | TIMESTAMP | NO | Última atualização do perfil | Audit trail | - SettingsPage (última modificação) |

### Campos Sugeridos para Adicionar

```sql
ALTER TABLE users
  ADD COLUMN role ENUM('admin','user','viewer') DEFAULT 'user',
  ADD COLUMN is_active TINYINT(1) DEFAULT 1,
  ADD COLUMN last_login TIMESTAMP NULL,
  ADD COLUMN preferences LONGTEXT;  -- JSON: {theme, language, notifications}
```

**Justificativa**:
- `role`: Requisito 3.2 (RBAC - Controle de acesso baseado em papéis)
- `is_active`: Controle de acesso (desativar usuários)
- `last_login`: Auditoria e segurança
- `preferences`: Personalização (tema escuro/claro, idioma)

---

## 2. TABELA: `projects` ✅ EXISTENTE

### Propósito
Armazenamento central de projetos com a Rede de Petri completa.

### Status
✅ **EXISTENTE** - Implementada e funcional

### Estrutura SQL

```sql
CREATE TABLE projects (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  user_id CHAR(36) NOT NULL,
  project_data LONGTEXT NOT NULL,  -- JSON completo da Rede de Petri
  INDEX idx_name (name),
  INDEX idx_created_at (created_at),
  INDEX idx_updated_at (updated_at),
  INDEX idx_user_id (user_id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único do projeto | Todas as fases (1.1 - 1.7) | - Dashboard (lista de projetos)<br>- ProjectList<br>- ProjectDetail<br>- Todas as páginas internas (/project/:id/*) |
| **name** | VARCHAR(255) | NO | Nome do projeto | **2.1.1** Criação de projeto | - CreateProjectModal (campo obrigatório)<br>- Dashboard (ProjectCard)<br>- ProjectList<br>- Header (título do projeto ativo) |
| **description** | TEXT | YES | Descrição detalhada | **2.1.1** Criação de projeto | - CreateProjectModal<br>- ProjectDetail (resumo)<br>- ProjectCard (tooltip) |
| **created_at** | TIMESTAMP | NO | Data de criação | Audit trail | - ProjectList (ordenação)<br>- ProjectDetail (metadados) |
| **updated_at** | TIMESTAMP | NO | Última modificação | Audit trail | - ProjectList (indicador de atividade)<br>- ProjectDetail ("Modificado há X dias") |
| **user_id** | CHAR(36) FK | NO | Dono do projeto | **3.2** Controle de acesso | - ProjectList (filtro "Meus projetos")<br>- ProjectDetail (compartilhamento) |
| **project_data** | LONGTEXT JSON | NO | **REDE DE PETRI COMPLETA** | **2.5** Modelagem de Redes de Petri<br>**2.5.2** Mapeamento para JSON | **PetriNetPage** (carrega/salva rede completa) |

### Estrutura JSON de `project_data`

Formato compatível com o Editor de Petri Net existente:

```json
{
  "nome": "Nome do Projeto",
  "version": "2.1",
  "description": "Descrição do projeto",
  "lugares": [
    {
      "id": "P1",
      "nome": "Nome do Place",
      "tokens": 1,
      "coordenadas": {"x": 100, "y": 200},
      "delay": 1000,
      "subnet": {},
      "agentId": "email_reader_agent",
      "input_data": {
        "max_emails": 5,
        "imap_server": "imap.gmail.com"
      },
      "output_data": {},
      "logica": "const output = utils.clone(input); return output;"
    }
  ],
  "transicoes": [
    {
      "id": "T1",
      "nome": "Nome da Transição",
      "orientacao": "vert",
      "coordenadas": {"x": 225, "y": 200},
      "prioridade": 1,
      "probabilidade": 1,
      "tempo": 0,
      "guard": "tokens.P1 > 0 && places.P1.input_data.status === 'ready'"
    }
  ],
  "arcos": [
    {"origem": "P1", "destino": "T1", "peso": 1},
    {"origem": "T1", "destino": "P2", "peso": 1}
  ],
  "agentes": [
    {
      "id": "email_reader_agent",
      "nome": "Email Reader Agent",
      "coordenadas": {"x": 290, "y": 0},
      "width": 150,
      "height": 327
    }
  ]
}
```

### Campos Sugeridos para Adicionar

```sql
ALTER TABLE projects
  ADD COLUMN status ENUM('draft','active','archived') DEFAULT 'draft',
  ADD COLUMN framework ENUM('crewai','langchain','autogen') DEFAULT 'crewai',
  ADD COLUMN llm_config LONGTEXT,  -- JSON: configuração de LLM
  ADD COLUMN deployment_status ENUM('not_deployed','deploying','deployed','error') DEFAULT 'not_deployed';
```

**Justificativa**:
- `status`: Ciclo de vida do projeto
- `framework`: Requisito 2.6.2 (Integração com framework)
- `llm_config`: Configuração de LLMs por projeto
- `deployment_status`: Requisito 2.12 (Deployment)

---

## 3. TABELA: `documents` ❌ FALTANDO

### Propósito
**Requisito 2.1** - Módulo de Leitura e Análise de Documentação

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE documents (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  file_type VARCHAR(50),  -- pdf, docx, txt, md
  file_size BIGINT UNSIGNED,
  file_path VARCHAR(1000),
  storage_type ENUM('local','s3','gcs','azure') DEFAULT 'local',
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status ENUM('uploaded','analyzing','analyzed','error') NOT NULL DEFAULT 'uploaded',
  analysis_results LONGTEXT,  -- JSON: requisitos extraídos
  extracted_entities LONGTEXT,  -- JSON: entidades identificadas
  requirements LONGTEXT,  -- JSON: lista de requisitos funcionais
  metadata LONGTEXT,
  INDEX idx_project_id (project_id),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_uploaded_at (uploaded_at),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único do documento | **2.1.1** Tipos de documentação suportados | - DocumentsPage (lista de docs)<br>- DocumentCard (identificação) |
| **project_id** | CHAR(36) FK | NO | Projeto ao qual pertence | **2.1** Análise documental por projeto | - DocumentsPage (carrega docs do projeto ativo)<br>- /project/:id/documents |
| **user_id** | CHAR(36) FK | NO | Quem fez upload | Audit trail | - DocumentsPage (filtro "Enviados por mim") |
| **filename** | VARCHAR(255) | NO | Nome interno do arquivo | **2.1.1** Gestão de arquivos | - Backend (armazenamento físico) |
| **original_filename** | VARCHAR(255) | NO | Nome original do arquivo | **2.1.1** Exibição para usuário | - DocumentCard (título do documento)<br>- DocumentUploadModal (lista de uploads) |
| **file_type** | VARCHAR(50) | YES | Extensão: pdf, docx, txt, md | **2.1.1** Documentos estruturados e não-estruturados | - DocumentCard (ícone apropriado)<br>- DocumentViewModal (renderizador específico) |
| **file_size** | BIGINT UNSIGNED | YES | Tamanho em bytes | Validação de upload | - DocumentUploadModal (progresso)<br>- DocumentCard ("2.5 MB") |
| **file_path** | VARCHAR(1000) | YES | Path no storage | Recuperação do arquivo | - Backend (download/visualização) |
| **storage_type** | ENUM | YES | local, s3, gcs, azure | **3.4** Integrações - S3, GCS | - SettingsPage (IntegrationsSettings) |
| **uploaded_at** | TIMESTAMP | NO | Data do upload | **2.1** Timeline de análise | - DocumentsPage (ordenação)<br>- DocumentCard ("Enviado há 2 dias") |
| **status** | ENUM | NO | uploaded, analyzing, analyzed, error | **2.1.2** Análise automática | - DocumentCard (badge de status)<br>- DocumentsPage (filtro por status) |
| **analysis_results** | LONGTEXT JSON | YES | Resultado completo da análise | **2.1.2** Análise documental:<br>- Extração de entidades<br>- Identificação de requisitos<br>- Detecção de relações | - DocumentViewModal (aba "Análise") |
| **extracted_entities** | LONGTEXT JSON | YES | Entidades identificadas | **2.1.2** Extração de entidades relevantes | - DocumentViewModal (lista de entidades)<br>- SpecificationPage (importar entidades) |
| **requirements** | LONGTEXT JSON | YES | Requisitos funcionais/não-funcionais | **2.1.2** Identificação de requisitos | - SpecificationPage (RequirementsTable) |
| **metadata** | LONGTEXT JSON | YES | Metadados adicionais | Extensibilidade | - Informações extras (autor, versão, tags) |

### Estrutura JSON de `analysis_results`

```json
{
  "entities": [
    {
      "type": "actor",
      "name": "User",
      "description": "System user"
    },
    {
      "type": "system",
      "name": "Email Service",
      "description": "Email processing system"
    }
  ],
  "requirements": [
    {
      "id": "RF001",
      "type": "functional",
      "description": "System must read emails",
      "priority": "high"
    }
  ],
  "relationships": [
    {
      "from": "User",
      "to": "Email Service",
      "type": "uses"
    }
  ],
  "workflows": [
    {
      "name": "Email Processing",
      "steps": ["Read", "Classify", "Respond"]
    }
  ],
  "business_rules": [
    "Emails must be processed within 5 minutes"
  ]
}
```

### Páginas que Utilizam

- **DocumentsPage.tsx** (lista, upload, status)
- **DocumentCard.tsx** (visualização individual)
- **DocumentUploadModal.tsx** (drag-and-drop)
- **DocumentViewModal.tsx** (preview + análise)
- **SpecificationPage.tsx** (importação de requisitos)

---

## 4. TABELA: `specifications` ❌ FALTANDO

### Propósito
**Requisito 2.2** - Módulo de Geração de Especificação Funcional

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE specifications (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL UNIQUE,
  user_id CHAR(36) NOT NULL,
  content LONGTEXT NOT NULL,  -- Markdown/HTML da especificação
  version VARCHAR(50) DEFAULT '1.0',
  status ENUM('draft','generated','reviewing','approved','needs_revision') NOT NULL DEFAULT 'draft',
  requirements_functional LONGTEXT,  -- JSON: requisitos funcionais
  requirements_nonfunctional LONGTEXT,  -- JSON: requisitos não-funcionais
  data_model LONGTEXT,  -- JSON: modelo de dados
  workflows LONGTEXT,  -- JSON: fluxos de trabalho
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  approved_at TIMESTAMP NULL,
  approved_by CHAR(36),
  INDEX idx_project_id (project_id),
  INDEX idx_status (status),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único | **2.2** Especificação funcional | - SpecificationPage (identificação) |
| **project_id** | CHAR(36) FK UNIQUE | NO | Um spec por projeto | **2.2** Especificação por projeto | - SpecificationPage (carrega spec do projeto ativo) |
| **user_id** | CHAR(36) FK | NO | Criador original | Audit trail | - SpecificationPage (metadados) |
| **content** | LONGTEXT | NO | Markdown/HTML da especificação | **2.2.2** Documento de especificação funcional completo | - SpecificationEditorModal (editor rich-text) |
| **version** | VARCHAR(50) | YES | Versionamento (1.0, 1.1, etc) | **2.4.3** Controle de versão e metadados | - SpecificationPage (histórico de versões) |
| **status** | ENUM | NO | draft, generated, reviewing, approved, needs_revision | **2.2** Workflow de aprovação | - SpecificationPage (badge de status) |
| **requirements_functional** | LONGTEXT JSON | YES | Lista de requisitos funcionais | **2.2.1** Classificação de requisitos | - RequirementsTable (aba "Funcionais") |
| **requirements_nonfunctional** | LONGTEXT JSON | YES | Requisitos não-funcionais | **2.2.1** Classificação | - RequirementsTable (aba "Não-Funcionais") |
| **data_model** | LONGTEXT JSON | YES | Modelo de dados/entidades | **2.2.4** Análise de arquitetura preliminar | - DataModelViewer (diagrama de entidades) |
| **workflows** | LONGTEXT JSON | YES | Fluxos de trabalho | **2.2.2** Diagramas ilustrativos | - SpecificationPage (seção "Fluxos") |
| **created_at** | TIMESTAMP | NO | Data de criação | Audit trail | - SpecificationPage (metadados) |
| **updated_at** | TIMESTAMP | NO | Última modificação | **2.2** Rastreamento de mudanças | - SpecificationPage ("Atualizado há X horas") |
| **approved_at** | TIMESTAMP | YES | Data de aprovação | **2.2** Workflow | - SpecificationPage (status de aprovação) |
| **approved_by** | CHAR(36) FK | YES | Quem aprovou | **3.2** Controle de acesso | - SpecificationPage (informação de aprovação) |

### Estrutura Markdown de `content`

```markdown
# 1. Introdução
Descrição geral do projeto...

# 2. Requisitos Funcionais
## RF001: Leitura de Emails
O sistema deve...

# 3. Requisitos Não-Funcionais
## RNF001: Performance
O sistema deve processar...

# 4. Modelo de Dados
## Entidades
- User
- Email
- Classification

# 5. Fluxos de Trabalho
## Fluxo: Processamento de Email
1. Receber email
2. Classificar
3. Responder
```

### Páginas que Utilizam

- **SpecificationPage.tsx** (visualização completa)
- **SpecificationGenerationModal.tsx** (configuração de geração)
- **SpecificationEditorModal.tsx** (edição de conteúdo)
- **RequirementsTable.tsx** (lista de requisitos)
- **DataModelViewer.tsx** (visualização do modelo)

---

## 5. TABELA: `agents` ❌ FALTANDO

### Propósito
**Requisito 2.3.1** - Identificação e Design de Agentes

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE agents (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  agent_id VARCHAR(255) NOT NULL,  -- ID usado na rede de Petri
  name VARCHAR(255) NOT NULL,
  role VARCHAR(500),
  goal TEXT,
  backstory TEXT,
  tools LONGTEXT,  -- JSON: lista de ferramentas
  verbose TINYINT(1) DEFAULT 0,
  allow_delegation TINYINT(1) DEFAULT 0,
  max_iter INT DEFAULT 25,
  max_rpm INT,
  status ENUM('active','inactive','draft') NOT NULL DEFAULT 'draft',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  metadata LONGTEXT,
  UNIQUE KEY unique_agent_project (project_id, agent_id),
  INDEX idx_project_id (project_id),
  INDEX idx_agent_id (agent_id),
  INDEX idx_status (status),
  FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único na tabela | Normalização | - AgentsPage (lista de agentes) |
| **project_id** | CHAR(36) FK | NO | Projeto ao qual pertence | **2.3.1** Design de agentes por projeto | - AgentsPage (carrega agentes do projeto ativo) |
| **agent_id** | VARCHAR(255) | NO | ID usado na rede de Petri | **2.5.2** Mapeamento de agentes para transições | - Vinculação: `project_data.lugares[].agentId` |
| **name** | VARCHAR(255) | NO | Nome descritivo do agente | **2.3.1** Identificação | - AgentCard (título)<br>- AgentFormModal (campo "Nome") |
| **role** | VARCHAR(500) | YES | Função do agente | **2.3.1** Elaboração de perfis detalhados | - AgentFormModal (campo "Role")<br>- YamlPage (agents.yaml) |
| **goal** | TEXT | YES | Objetivo do agente | **2.3.1** Perfis detalhados | - AgentFormModal (campo "Goal") |
| **backstory** | TEXT | YES | História de fundo | **2.3.1** Perfis detalhados | - AgentFormModal (campo "Backstory") |
| **tools** | LONGTEXT JSON | YES | Ferramentas disponíveis | **2.3.1** Atribuição de ferramentas | - AgentFormModal (multi-select de tools) |
| **verbose** | TINYINT(1) | YES | Modo verbose ativado | **2.9.2** Ferramentas de debugging | - AgentFormModal (checkbox "Verbose") |
| **allow_delegation** | TINYINT(1) | YES | Permitir delegação | **2.3.1** Parâmetros comportamentais | - AgentFormModal (checkbox "Allow Delegation") |
| **max_iter** | INT | YES | Máximo de iterações | **2.3.1** Parâmetros comportamentais | - AgentFormModal (campo "Max Iterations") |
| **max_rpm** | INT | YES | Rate limit (requests/min) | **3.3** Estratégias para rate limiting | - AgentFormModal (campo "Max RPM") |
| **status** | ENUM | NO | active, inactive, draft | **2.3** Estado do agente | - AgentCard (badge de status) |
| **created_at** | TIMESTAMP | NO | Data de criação | Audit trail | - AgentsPage (ordenação) |
| **updated_at** | TIMESTAMP | NO | Última modificação | Audit trail | - AgentCard ("Modificado há X dias") |
| **metadata** | LONGTEXT JSON | YES | Metadados adicionais | Extensibilidade | - Informações customizadas |

### Exemplo de `tools` JSON

```json
[
  "email_reader",
  "classifier",
  "database_query",
  "smtp_sender"
]
```

### Páginas que Utilizam

- **AgentsPage.tsx** (lista de agentes)
- **AgentCard.tsx** (visualização individual)
- **AgentFormModal.tsx** (CRUD completo)
- **AgentSpecifierModal.tsx** (criação automática via IA)
- **YamlPage.tsx** (geração de agents.yaml)
- **PetriNetPage.tsx** (vinculação com places)

---

## 6. TABELA: `tasks` ❌ FALTANDO

### Propósito
**Requisito 2.3.2** - Design de Tarefas

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE tasks (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  task_id VARCHAR(255) NOT NULL,  -- ID usado na rede de Petri
  name VARCHAR(255) NOT NULL,
  description TEXT,
  agent_id CHAR(36),  -- FK para agents table
  expected_output TEXT,
  tools LONGTEXT,  -- JSON: ferramentas específicas
  async_execution TINYINT(1) DEFAULT 0,
  context LONGTEXT,  -- JSON: dependências de outras tasks
  input_schema LONGTEXT,  -- JSON: schema de entrada
  output_schema LONGTEXT,  -- JSON: schema de saída
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  metadata LONGTEXT,
  UNIQUE KEY unique_task_project (project_id, task_id),
  INDEX idx_project_id (project_id),
  INDEX idx_task_id (task_id),
  INDEX idx_agent_id (agent_id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único na tabela | Normalização | - TasksPage (lista de tarefas) |
| **project_id** | CHAR(36) FK | NO | Projeto ao qual pertence | **2.3.2** Design de tarefas por projeto | - TasksPage (carrega tasks do projeto ativo) |
| **task_id** | VARCHAR(255) | NO | ID usado na rede de Petri | **2.5** Mapeamento para rede | - TaskFormModal (campo "Task ID") |
| **name** | VARCHAR(255) | NO | Nome da tarefa | **2.3.2** Identificação | - TaskCard (título) |
| **description** | TEXT | YES | Descrição detalhada | **2.3.2** Decomposição em tarefas atômicas | - TaskFormModal (campo "Description") |
| **agent_id** | CHAR(36) FK | YES | Agente responsável | **2.3.2** Vinculação com agentes | - TaskFormModal (dropdown "Agent") |
| **expected_output** | TEXT | YES | Saída esperada | **2.3.2** Definição de saídas esperadas | - TaskFormModal (campo "Expected Output") |
| **tools** | LONGTEXT JSON | YES | Ferramentas específicas | **2.3.1** Atribuição de ferramentas | - TaskFormModal (multi-select de tools) |
| **async_execution** | TINYINT(1) | YES | Execução assíncrona | **2.3.3** Sequenciamento e paralelismo | - TaskFormModal (checkbox "Async") |
| **context** | LONGTEXT JSON | YES | Dependências de outras tasks | **2.3.3** Gestão de dependências | - TaskFormModal (multi-select "Dependencies") |
| **input_schema** | LONGTEXT JSON | YES | Schema JSON de entrada | **2.3.2** Especificação de formato de entrada | - TaskFormModal (editor JSON Schema) |
| **output_schema** | LONGTEXT JSON | YES | Schema JSON de saída | **2.3.2** Definição de formatos de saída | - TaskFormModal (editor JSON Schema) |
| **created_at** | TIMESTAMP | NO | Data de criação | Audit trail | - TasksPage (ordenação) |
| **updated_at** | TIMESTAMP | NO | Última modificação | Audit trail | - TaskCard ("Modificado há X dias") |
| **metadata** | LONGTEXT JSON | YES | Metadados adicionais | Extensibilidade | - Informações customizadas |

### Páginas que Utilizam

- **TasksPage.tsx** (lista de tarefas)
- **TaskCard.tsx** (visualização individual)
- **TaskFormModal.tsx** (CRUD completo)
- **TaskSpecifierModal.tsx** (criação automática via IA)
- **YamlPage.tsx** (geração de tasks.yaml)
- **PetriNetPage.tsx** (vinculação com places)

---

## 7. TABELA: `yaml_files` ❌ FALTANDO

### Propósito
**Requisito 2.4** - Módulo de Geração de Arquivos YAML

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE yaml_files (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  file_type ENUM('agents','tasks','tools','config') NOT NULL,
  filename VARCHAR(255) NOT NULL,
  content LONGTEXT NOT NULL,  -- Conteúdo YAML
  version VARCHAR(50),
  is_valid TINYINT(1) DEFAULT 1,
  validation_errors LONGTEXT,  -- JSON: erros de validação
  generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_project_id (project_id),
  INDEX idx_file_type (file_type),
  FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único | **2.4** Gestão de YAMLs | - YamlPage (lista de arquivos) |
| **project_id** | CHAR(36) FK | NO | Projeto ao qual pertence | **2.4** YAMLs por projeto | - YamlPage (carrega YAMLs do projeto ativo) |
| **file_type** | ENUM | NO | agents, tasks, tools, config | **2.4.1** agents.yaml<br>**2.4.2** tasks.yaml | - YamlPage (tabs diferentes) |
| **filename** | VARCHAR(255) | NO | Nome do arquivo | **2.4** Nomenclatura | - YamlFileCard (título) |
| **content** | LONGTEXT | NO | Conteúdo YAML completo | **2.4.1** Formatação YAML | - YamlEditorModal (editor) |
| **version** | VARCHAR(50) | YES | Versão do arquivo | **2.4.3** Controle de versão | - YamlPage (histórico de versões) |
| **is_valid** | TINYINT(1) | YES | YAML válido? | **2.4.4** Validação integrada | - YamlFileCard (badge "Valid") |
| **validation_errors** | LONGTEXT JSON | YES | Erros de validação | **2.4.4** Verificação cruzada | - YamlEditorModal (lista de erros) |
| **generated_at** | TIMESTAMP | NO | Data de geração | **2.4** Timeline | - YamlPage (ordenação) |
| **updated_at** | TIMESTAMP | NO | Última edição manual | **2.4.3** Rastreabilidade | - YamlFileCard ("Editado manualmente") |

### Exemplo de `content` (agents.yaml)

```yaml
email_reader:
  role: "Email Processing Specialist"
  goal: "Read and categorize incoming emails"
  backstory: "Experienced email analyst with expertise in classification"
  tools:
    - email_reader_tool
    - classifier_tool
  verbose: true
  allow_delegation: false
```

### Páginas que Utilizam

- **YamlPage.tsx** (lista e gestão de YAMLs)
- **YamlFileCard.tsx** (preview individual)
- **YamlEditorModal.tsx** (edição com syntax highlighting)
- **YamlGenerationModal.tsx** (configuração de geração automática)
- **CodePage.tsx** (usa YAMLs para gerar código Python)

---

## 8. TABELA: `code_generations` ❌ FALTANDO

### Propósito
**Requisito 2.6** - Módulo de Geração de Código Python

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE code_generations (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  framework ENUM('crewai','langchain','autogen','custom') NOT NULL,
  llm_provider VARCHAR(50),  -- openai, anthropic, azure
  status ENUM('pending','generating','ready','error','building','deploying','deployed') NOT NULL DEFAULT 'pending',
  code_structure LONGTEXT,  -- JSON: estrutura de arquivos
  files LONGTEXT,  -- JSON: {filename: content}
  generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  built_at TIMESTAMP NULL,
  deployed_at TIMESTAMP NULL,
  deployment_url VARCHAR(500),
  build_logs LONGTEXT,
  test_results LONGTEXT,  -- JSON: resultados dos testes
  quality_metrics LONGTEXT,  -- JSON: métricas de qualidade
  metadata LONGTEXT,
  INDEX idx_project_id (project_id),
  INDEX idx_status (status),
  FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único | **2.6** Geração de código | - CodePage (identificação) |
| **project_id** | CHAR(36) FK | NO | Projeto ao qual pertence | **2.6** Código por projeto | - CodePage (carrega código do projeto ativo) |
| **framework** | ENUM | NO | crewai, langchain, autogen, custom | **2.6.2** Integração com framework | - CodeGenerationModal (dropdown "Framework") |
| **llm_provider** | VARCHAR(50) | YES | openai, anthropic, azure, local | **3.1** Suporte a LLMs | - CodeGenerationModal (dropdown "LLM Provider") |
| **status** | ENUM | NO | pending, generating, ready, error, building, deploying, deployed | **2.6** Workflow de geração | - CodePage (badge de status) |
| **code_structure** | LONGTEXT JSON | YES | Estrutura de arquivos/pastas | **2.6** Organização do código | - FileExplorer (árvore de arquivos) |
| **files** | LONGTEXT JSON | YES | Mapa {filename: content} | **2.6.1** Implementação da rede | - CodeEditor (conteúdo dos arquivos) |
| **generated_at** | TIMESTAMP | NO | Data de geração | **2.6** Timeline | - CodePage ("Gerado há 1 hora") |
| **built_at** | TIMESTAMP | YES | Data do build | **2.6.4** Pipeline CI/CD | - DeploymentPanel (histórico de builds) |
| **deployed_at** | TIMESTAMP | YES | Data do deploy | **2.12** Deployment completo | - DeploymentPanel (status de deploy) |
| **deployment_url** | VARCHAR(500) | YES | URL do deploy | **2.12** Integração com nuvem | - DeploymentPanel (link clicável) |
| **build_logs** | LONGTEXT | YES | Logs do build | **2.6.4** Debugging | - ExecutionConsole (aba "Build Logs") |
| **test_results** | LONGTEXT JSON | YES | Resultados dos testes | **2.6.4** Testes automatizados | - CodePage (aba "Tests") |
| **quality_metrics** | LONGTEXT JSON | YES | Métricas de qualidade | **2.6** Qualidade do código | - CodePage (painel de métricas) |
| **metadata** | LONGTEXT JSON | YES | Metadados adicionais | Extensibilidade | - Configurações extras |

### Páginas que Utilizam

- **CodePage.tsx** (visualização completa)
- **CodeGenerationModal.tsx** (configuração de geração)
- **CodeEditor.tsx** (edição de arquivos individuais)
- **FileExplorer.tsx** (navegação na estrutura)
- **ExecutionConsole.tsx** (logs e resultados)
- **DeploymentPanel.tsx** (status e histórico)

---

## 9. TABELA: `execution_sessions` ✅ EXISTENTE

### Propósito
**Requisito 2.9.2** + **2.11** - Interface de Chat e Controle + Execução de Redes

### Status
✅ **EXISTENTE** - Implementada e funcional

### Estrutura SQL

```sql
CREATE TABLE execution_sessions (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  session_name VARCHAR(255),
  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP NULL,
  status ENUM('running','completed','failed','cancelled','paused') NOT NULL DEFAULT 'running',
  initial_marking LONGTEXT,  -- JSON: estado inicial dos tokens
  final_marking LONGTEXT,    -- JSON: estado final dos tokens
  execution_log LONGTEXT,    -- JSON: log completo da execução
  total_tasks INT UNSIGNED DEFAULT 0,
  completed_tasks INT UNSIGNED DEFAULT 0,
  failed_tasks INT UNSIGNED DEFAULT 0,
  execution_time_ms BIGINT UNSIGNED,
  execution_metadata LONGTEXT,  -- JSON: metadata adicional
  INDEX idx_project_id (project_id),
  INDEX idx_user_id (user_id),
  INDEX idx_session_name (session_name),
  INDEX idx_started_at (started_at),
  INDEX idx_finished_at (finished_at),
  INDEX idx_status (status),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único da sessão | **2.9.2** Gerenciamento de execuções | - MonitoringPage (lista de sessões) |
| **project_id** | CHAR(36) FK | NO | Projeto sendo executado | Vinculação com projeto | - MonitoringPage (filtro por projeto) |
| **user_id** | CHAR(36) FK | NO | Quem iniciou | Audit trail | - MonitoringPage (filtro "Minhas execuções") |
| **session_name** | VARCHAR(255) | YES | Nome descritivo | **2.10.3** Gestão de sessões persistentes | - AgentChatPage (título da sessão) |
| **started_at** | TIMESTAMP | NO | Início da execução | **2.9.2** Timeline | - MonitoringPage (ordenação) |
| **finished_at** | TIMESTAMP | YES | Fim da execução | **2.9.2** Duração | - MonitoringPage (duração calculada) |
| **status** | ENUM | NO | running, completed, failed, cancelled, paused | **2.9.2** Painéis de controle | - MonitoringPage (badge de status) |
| **initial_marking** | LONGTEXT JSON | YES | Estado inicial dos tokens | **2.5.1** Tokens iniciais | - PetriNetPage (visualização inicial) |
| **final_marking** | LONGTEXT JSON | YES | Estado final dos tokens | **2.5** Resultado da execução | - PetriNetPage (visualização final) |
| **execution_log** | LONGTEXT JSON | YES | Log completo da execução | **2.9.1** Visualização de logs | - ExecutionConsole (log estruturado) |
| **total_tasks** | INT UNSIGNED | YES | Total de tarefas | **2.9.2** Métricas | - MonitoringPage (progresso geral) |
| **completed_tasks** | INT UNSIGNED | YES | Tarefas completadas | **2.9.2** Métricas | - MonitoringPage (barra de progresso) |
| **failed_tasks** | INT UNSIGNED | YES | Tarefas falhadas | **2.9.2** Debugging | - MonitoringPage (alertas) |
| **execution_time_ms** | BIGINT UNSIGNED | YES | Tempo total em ms | **2.9.2** Performance | - MonitoringPage ("Executado em 2.5s") |
| **execution_metadata** | LONGTEXT JSON | YES | Metadata adicional | Extensibilidade | - Informações extras da execução |

### Páginas que Utilizam

- **MonitoringPage.tsx** (lista e detalhes de sessões)
- **AgentChatPage.tsx** (sessão ativa de chat)
- **SystemStatePage.tsx** (dashboard em tempo real)
- **PetriNetPage.tsx** (simulação e estados)

---

## 10. TABELA: `task_executions` ✅ EXISTENTE

### Propósito
**Requisito 2.9.2** - Execução Individual de Tarefas

### Status
✅ **EXISTENTE** - Implementada e funcional

### Estrutura SQL

```sql
CREATE TABLE task_executions (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  session_id CHAR(36) NOT NULL,
  place_id VARCHAR(255) NOT NULL,  -- ID do place na rede de Petri
  transition_id VARCHAR(255),
  task_name VARCHAR(255) NOT NULL,
  agent_id VARCHAR(255),
  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP NULL,
  status ENUM('pending','running','completed','failed','cancelled') NOT NULL DEFAULT 'pending',
  input_data LONGTEXT,   -- JSON: dados de entrada
  output_data LONGTEXT,  -- JSON: resultado da tarefa
  verbose_log LONGTEXT,  -- JSON: logs detalhados
  error_message TEXT,
  execution_time_ms BIGINT UNSIGNED,
  websocket_endpoint VARCHAR(500),
  retry_count INT UNSIGNED DEFAULT 0,
  task_metadata LONGTEXT,  -- JSON: metadata adicional
  INDEX idx_session_id (session_id),
  INDEX idx_place_id (place_id),
  INDEX idx_task_name (task_name),
  INDEX idx_agent_id (agent_id),
  INDEX idx_started_at (started_at),
  INDEX idx_finished_at (finished_at),
  INDEX idx_status (status),
  FOREIGN KEY (session_id) REFERENCES execution_sessions(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único da execução | **2.9.2** Rastreamento de tarefas | - MonitoringPage (detalhes de task) |
| **session_id** | CHAR(36) FK | NO | Sessão pai | Vinculação | - MonitoringPage (agrupa por sessão) |
| **place_id** | VARCHAR(255) | NO | Place da rede de Petri | **2.5** Mapeamento para rede | - PetriNetPage (highlight do place ativo) |
| **transition_id** | VARCHAR(255) | YES | Transição que disparou | **2.5** Mapeamento | - PetriNetPage (animação da transição) |
| **task_name** | VARCHAR(255) | NO | Nome da tarefa | **2.3.2** Identificação | - MonitoringPage (nome na lista) |
| **agent_id** | VARCHAR(255) | YES | Agente responsável | **2.3** Vinculação | - MonitoringPage (filtro por agente) |
| **started_at** | TIMESTAMP | NO | Início da task | Timeline | - MonitoringPage (ordenação) |
| **finished_at** | TIMESTAMP | YES | Fim da task | Duração | - MonitoringPage (duração calculada) |
| **status** | ENUM | NO | pending, running, completed, failed, cancelled | **2.9.2** Estado da task | - MonitoringPage (badge) |
| **input_data** | LONGTEXT JSON | YES | Dados de entrada | **Editor Petri** Place.input_data | - AgentChatPage (visualização de input) |
| **output_data** | LONGTEXT JSON | YES | Resultado da task | **Editor Petri** Place.output_data | - AgentChatPage (visualização de output) |
| **verbose_log** | LONGTEXT JSON | YES | Logs detalhados | **2.9.2** Ferramentas de debugging | - AgentChatPage (painel de debug) |
| **error_message** | TEXT | YES | Mensagem de erro | **2.9.2** Debugging | - MonitoringPage (alertas) |
| **execution_time_ms** | BIGINT UNSIGNED | YES | Tempo de execução | **2.9.2** Performance | - MonitoringPage (métricas) |
| **websocket_endpoint** | VARCHAR(500) | YES | Endpoint WebSocket usado | **Editor Petri** Integração com backend | - Backend (conexão assíncrona) |
| **retry_count** | INT UNSIGNED | YES | Número de retentativas | **2.10.3** Sistema de retry | - MonitoringPage (indicador de retries) |
| **task_metadata** | LONGTEXT JSON | YES | Metadata adicional | Extensibilidade | - Informações extras |

### Páginas que Utilizam

- **MonitoringPage.tsx** (lista detalhada de tasks)
- **AgentChatPage.tsx** (task atual em execução)
- **SystemStatePage.tsx** (métricas agregadas)
- **PetriNetPage.tsx** (animação de execução)

---

## 11. TABELA: `execution_outputs` ✅ EXISTENTE

### Propósito
Armazenamento de Outputs/Artefatos Gerados

### Status
✅ **EXISTENTE** - Implementada e funcional

### Estrutura SQL

```sql
CREATE TABLE execution_outputs (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  session_id CHAR(36) NOT NULL,
  task_execution_id CHAR(36),
  output_name VARCHAR(255) NOT NULL,
  output_type ENUM('task_result','execution_log','report','file','json','other') NOT NULL DEFAULT 'task_result',
  output_format VARCHAR(50),
  file_size BIGINT UNSIGNED,
  file_path VARCHAR(1000),
  output_data LONGTEXT,  -- JSON ou conteúdo do arquivo
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  download_count INT UNSIGNED DEFAULT 0,
  is_downloadable TINYINT(1) DEFAULT 1,
  metadata LONGTEXT,
  INDEX idx_session_id (session_id),
  INDEX idx_task_execution_id (task_execution_id),
  INDEX idx_output_name (output_name),
  INDEX idx_output_type (output_type),
  INDEX idx_created_at (created_at),
  FOREIGN KEY (session_id) REFERENCES execution_sessions(id),
  FOREIGN KEY (task_execution_id) REFERENCES task_executions(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único | Gestão de outputs | - ArtifactManagerPage (lista) |
| **session_id** | CHAR(36) FK | NO | Sessão que gerou | Vinculação | - ArtifactManagerPage (filtro por sessão) |
| **task_execution_id** | CHAR(36) FK | YES | Task específica | Vinculação | - MonitoringPage (outputs da task) |
| **output_name** | VARCHAR(255) | NO | Nome do output | **2.9.1** Suporte a download de artefatos | - ArtifactManagerPage (nome do arquivo) |
| **output_type** | ENUM | NO | task_result, execution_log, report, file, json, other | **2.9.1** Categorização | - ArtifactManagerPage (filtro por tipo) |
| **output_format** | VARCHAR(50) | YES | json, csv, pdf, txt, etc | **2.9.1** Formato do arquivo | - ArtifactManagerPage (extensão) |
| **file_size** | BIGINT UNSIGNED | YES | Tamanho em bytes | Validação | - ArtifactManagerPage ("2.5 MB") |
| **file_path** | VARCHAR(1000) | YES | Path no storage | Download | - Backend (recuperação) |
| **output_data** | LONGTEXT | YES | Conteúdo (se não for arquivo) | **2.9.1** Visualização | - ArtifactManagerPage (preview) |
| **created_at** | TIMESTAMP | NO | Data de criação | Timeline | - ArtifactManagerPage (ordenação) |
| **download_count** | INT UNSIGNED | YES | Contagem de downloads | Estatística | - ArtifactManagerPage (contador) |
| **is_downloadable** | TINYINT(1) | YES | Permitir download | Controle | - ArtifactManagerPage (botão download) |
| **metadata** | LONGTEXT JSON | YES | Metadata adicional | Extensibilidade | - Informações extras |

### Páginas que Utilizam

- **ArtifactManagerPage.tsx** (gestão completa de outputs)
- **MonitoringPage.tsx** (outputs por sessão/task)
- **AgentChatPage.tsx** (downloads de resultados)

---

## 12. TABELA: `verbose_logs` ✅ EXISTENTE

### Propósito
Logs Detalhados de Execução

### Status
✅ **EXISTENTE** - Implementada e funcional

### Estrutura SQL

```sql
CREATE TABLE verbose_logs (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  task_execution_id CHAR(36) NOT NULL,
  timestamp TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  log_level ENUM('debug','info','warning','error','critical') NOT NULL DEFAULT 'info',
  message TEXT NOT NULL,
  step_number INT UNSIGNED,
  component VARCHAR(255),
  metadata LONGTEXT,
  INDEX idx_task_execution_id (task_execution_id),
  INDEX idx_timestamp (timestamp),
  INDEX idx_log_level (log_level),
  INDEX idx_component (component),
  FOREIGN KEY (task_execution_id) REFERENCES task_executions(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único | Gestão de logs | - Backend (indexação) |
| **task_execution_id** | CHAR(36) FK | NO | Task relacionada | Vinculação | - MonitoringPage (logs por task) |
| **timestamp** | TIMESTAMP(3) | NO | Timestamp preciso (ms) | **2.9.1** Logs em tempo real | - ExecutionConsole (ordenação temporal) |
| **log_level** | ENUM | NO | debug, info, warning, error, critical | **2.9.2** Ferramentas de debugging | - ExecutionConsole (filtro por nível) |
| **message** | TEXT | NO | Mensagem do log | **2.9.1** Visualização de logs | - ExecutionConsole (linha de log) |
| **step_number** | INT UNSIGNED | YES | Número do passo | **Editor Petri** Sequência de execução | - ExecutionConsole (numeração) |
| **component** | VARCHAR(255) | YES | Componente que logou | **2.9.2** Identificação de origem | - ExecutionConsole (filtro por componente) |
| **metadata** | LONGTEXT JSON | YES | Metadata adicional | **2.9.2** Debugging avançado | - Informações contextuais extras |

### Páginas que Utilizam

- **ExecutionConsole.tsx** (visualização de logs)
- **MonitoringPage.tsx** (aba "Verbose Logs")
- **AgentChatPage.tsx** (painel de debug lateral)

---

## 13. TABELA: `mcp_connections` ❌ FALTANDO

### Propósito
**Requisito 2.7** - Módulo de Integração com MCP

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE mcp_connections (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36),  -- NULL = global
  server_name VARCHAR(255) NOT NULL,
  server_url VARCHAR(500) NOT NULL,
  auth_type ENUM('none','basic','bearer','apikey') DEFAULT 'none',
  auth_credentials LONGTEXT,  -- JSON criptografado
  services LONGTEXT,  -- JSON: lista de serviços disponíveis
  status ENUM('active','inactive','error') NOT NULL DEFAULT 'inactive',
  last_sync TIMESTAMP NULL,
  health_check_url VARCHAR(500),
  metadata LONGTEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_project_id (project_id),
  INDEX idx_status (status),
  FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único | **2.7** Gestão de conexões | - McpGlobalConfigPage (lista) |
| **project_id** | CHAR(36) FK | YES | NULL = global, senão específico | **2.7** Conexões globais vs por projeto | - McpGlobalConfigPage (globais) |
| **server_name** | VARCHAR(255) | NO | Nome do servidor | **2.7.1** Identificação | - McpGlobalConfigPage (nome na lista) |
| **server_url** | VARCHAR(500) | NO | URL base | **2.7.1** Configuração de conexão | - McpGlobalConfigPage (campo "Server URL") |
| **auth_type** | ENUM | YES | none, basic, bearer, apikey | **2.7.1** Configuração de autenticação | - McpGlobalConfigPage (dropdown "Auth Type") |
| **auth_credentials** | LONGTEXT | YES | Credenciais criptografadas | **3.2** Criptografia em repouso | - McpGlobalConfigPage (campos de credenciais) |
| **services** | LONGTEXT JSON | YES | Lista de serviços disponíveis | **2.7.3** Descoberta dinâmica de serviços | - McpServiceDiscoveryPage (catálogo) |
| **status** | ENUM | NO | active, inactive, error | **2.7.1** Monitoramento de saúde | - McpGlobalConfigPage (badge de status) |
| **last_sync** | TIMESTAMP | YES | Última sincronização | **2.7.2** Sincronização de estados | - McpProjectIntegrationPage ("Sincronizado há 5 min") |
| **health_check_url** | VARCHAR(500) | YES | Endpoint de health check | **2.7.1** Circuit breaker | - Backend (health monitoring) |
| **metadata** | LONGTEXT JSON | YES | Metadata adicional | Extensibilidade | - Configurações extras |
| **created_at** | TIMESTAMP | NO | Data de criação | Audit trail | - McpGlobalConfigPage (ordenação) |

### Páginas que Utilizam

- **McpGlobalConfigPage.tsx** (configuração global)
- **McpServiceDiscoveryPage.tsx** (descoberta de serviços)
- **McpProjectIntegrationPage.tsx** (integração por projeto)
- **McpStateSyncPage.tsx** (sincronização)

---

## 14. TABELA: `monitoring_metrics` ❌ FALTANDO

### Propósito
**Requisito 2.8** - Módulo de Monitoramento via Langfuse

### Status
❌ **FALTANDO** - Precisa ser criada

### Estrutura SQL Proposta

```sql
CREATE TABLE monitoring_metrics (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36),
  session_id CHAR(36),
  task_execution_id CHAR(36),
  metric_type ENUM('llm_call','token_usage','latency','error','cost') NOT NULL,
  metric_name VARCHAR(255) NOT NULL,
  metric_value DECIMAL(20,6),
  metric_unit VARCHAR(50),
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  trace_id VARCHAR(255),  -- Langfuse trace ID
  span_id VARCHAR(255),   -- Langfuse span ID
  metadata LONGTEXT,
  INDEX idx_project_id (project_id),
  INDEX idx_session_id (session_id),
  INDEX idx_task_execution_id (task_execution_id),
  INDEX idx_metric_type (metric_type),
  INDEX idx_timestamp (timestamp),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (session_id) REFERENCES execution_sessions(id),
  FOREIGN KEY (task_execution_id) REFERENCES task_executions(id)
);
```

### Análise de Campos

| Campo | Tipo | Nulo | Significado | Requisito | Interface |
|-------|------|------|-------------|-----------|-----------|
| **id** | CHAR(36) UUID | NO | Identificador único | Gestão de métricas | - Backend (indexação) |
| **project_id** | CHAR(36) FK | YES | Projeto relacionado | Filtragem | - MonitoringPage (filtro por projeto) |
| **session_id** | CHAR(36) FK | YES | Sessão relacionada | Vinculação | - MonitoringPage (métricas por sessão) |
| **task_execution_id** | CHAR(36) FK | YES | Task relacionada | Vinculação | - MonitoringPage (métricas por task) |
| **metric_type** | ENUM | NO | llm_call, token_usage, latency, error, cost | **2.8.1** Captura de métricas | - MonitoringPage (filtro por tipo) |
| **metric_name** | VARCHAR(255) | NO | Nome específico da métrica | **2.8.1** Identificação | - MonitoringPage (label da métrica) |
| **metric_value** | DECIMAL(20,6) | YES | Valor numérico | **2.8.1** Dados | - MetricsPanel (gráficos) |
| **metric_unit** | VARCHAR(50) | YES | Unidade de medida | **2.8.1** Formatação | - MetricsPanel ("tokens", "ms", "USD") |
| **timestamp** | TIMESTAMP | NO | Momento da captura | **2.8.1** Timeline | - MetricsPanel (eixo X dos gráficos) |
| **trace_id** | VARCHAR(255) | YES | ID do trace Langfuse | **2.8.2** Integração com Langfuse | - MonitoringPage (link para Langfuse) |
| **span_id** | VARCHAR(255) | YES | ID do span Langfuse | **2.8.2** Rastreamento de fluxos | - TraceViewer (visualização de spans) |
| **metadata** | LONGTEXT JSON | YES | Metadata adicional | **2.8** Tags e filtros personalizados | - Informações contextuais extras |

### Páginas que Utilizam

- **MonitoringPage.tsx** (dashboard completo)
- **MetricsPanel.tsx** (gráficos e visualizações)
- **TraceViewer.tsx** (traces Langfuse)
- **SystemOverview.tsx** (métricas agregadas)
- **LangfuseConnectionModal.tsx** (configuração)

---

## Matriz de Relacionamentos

### Diagrama ER (Entidade-Relacionamento)

```
┌──────────┐
│  users   │
└────┬─────┘
     │ 1
     │
     │ N
┌────┴────────────┐
│    projects     │◄─────────────────────┐
└────┬────────────┘                      │
     │ 1                                 │
     │                                   │
     ├─────► documents (N)               │
     ├─────► specifications (1)          │
     ├─────► agents (N)                  │
     ├─────► tasks (N)                   │
     ├─────► yaml_files (N)              │
     ├─────► code_generations (N)        │
     ├─────► mcp_connections (N)         │
     ├─────► execution_sessions (N)      │
     └─────► monitoring_metrics (N)      │
                                         │
agents (1) ───► tasks (N)                │
                                         │
execution_sessions (1) ──┬──► task_executions (N)
                         ├──► execution_outputs (N)
                         └──► monitoring_metrics (N)
                                         │
task_executions (1) ──┬──► execution_outputs (N)
                      ├──► verbose_logs (N)
                      └──► monitoring_metrics (N)
```

### Relacionamentos Detalhados

| Tabela Pai | Tabela Filha | Tipo | Campo FK | Descrição |
|------------|--------------|------|----------|-----------|
| **users** | projects | 1:N | user_id | Um usuário pode ter múltiplos projetos |
| **users** | execution_sessions | 1:N | user_id | Um usuário pode iniciar múltiplas execuções |
| **projects** | documents | 1:N | project_id | Um projeto pode ter múltiplos documentos |
| **projects** | specifications | 1:1 | project_id | Um projeto tem uma especificação |
| **projects** | agents | 1:N | project_id | Um projeto pode ter múltiplos agentes |
| **projects** | tasks | 1:N | project_id | Um projeto pode ter múltiplas tarefas |
| **projects** | yaml_files | 1:N | project_id | Um projeto pode ter múltiplos YAMLs |
| **projects** | code_generations | 1:N | project_id | Um projeto pode ter múltiplas gerações de código |
| **projects** | mcp_connections | 1:N | project_id | Um projeto pode ter múltiplas conexões MCP |
| **projects** | execution_sessions | 1:N | project_id | Um projeto pode ter múltiplas execuções |
| **projects** | monitoring_metrics | 1:N | project_id | Um projeto pode ter múltiplas métricas |
| **agents** | tasks | 1:N | agent_id | Um agente pode ter múltiplas tarefas |
| **execution_sessions** | task_executions | 1:N | session_id | Uma sessão pode ter múltiplas execuções de tasks |
| **execution_sessions** | execution_outputs | 1:N | session_id | Uma sessão pode ter múltiplos outputs |
| **execution_sessions** | monitoring_metrics | 1:N | session_id | Uma sessão pode ter múltiplas métricas |
| **task_executions** | execution_outputs | 1:N | task_execution_id | Uma task pode gerar múltiplos outputs |
| **task_executions** | verbose_logs | 1:N | task_execution_id | Uma task pode ter múltiplos logs |
| **task_executions** | monitoring_metrics | 1:N | task_execution_id | Uma task pode ter múltiplas métricas |

---

## Resumo Executivo

### Status das Tabelas

| # | Tabela | Status | Prioridade | Complexidade |
|---|--------|--------|------------|--------------|
| 1 | users | ✅ Existente | - | - |
| 2 | projects | ✅ Existente | - | - |
| 3 | documents | ❌ Faltando | Alta | Média |
| 4 | specifications | ❌ Faltando | Alta | Baixa |
| 5 | agents | ❌ Faltando | Crítica | Média |
| 6 | tasks | ❌ Faltando | Crítica | Média |
| 7 | yaml_files | ❌ Faltando | Média | Baixa |
| 8 | code_generations | ❌ Faltando | Alta | Alta |
| 9 | execution_sessions | ✅ Existente | - | - |
| 10 | task_executions | ✅ Existente | - | - |
| 11 | execution_outputs | ✅ Existente | - | - |
| 12 | verbose_logs | ✅ Existente | - | - |
| 13 | mcp_connections | ❌ Faltando | Média | Média |
| 14 | monitoring_metrics | ❌ Faltando | Média | Baixa |

**Resumo**: 6 tabelas existentes (43%) | 8 tabelas faltando (57%)

### Tabelas por Fase do LangNet

| Fase | Tabelas Necessárias | Status |
|------|---------------------|--------|
| **Fase 1** - Documentação | documents | ❌ Faltando |
| **Fase 2** - Especificação | specifications | ❌ Faltando |
| **Fase 3** - Agentes/Tarefas | agents, tasks | ❌ Faltando |
| **Fase 4** - YAML | yaml_files | ❌ Faltando |
| **Fase 5** - Petri Net | projects.project_data | ✅ Existente |
| **Fase 6** - Código | code_generations | ❌ Faltando |
| **Fase 7** - Execução | execution_sessions, task_executions, execution_outputs, verbose_logs | ✅ Existente |
| **Integrações** | mcp_connections, monitoring_metrics | ❌ Faltando |

### Campos Críticos

#### Campos que DEVEM existir:

1. **projects.project_data** → CORE do sistema (rede de Petri completa)
2. **agents.agent_id** → Vinculação com rede de Petri
3. **tasks.task_id** → Vinculação com rede de Petri
4. **execution_sessions.status** → Monitoramento em tempo real
5. **task_executions.input_data/output_data** → Fluxo de dados entre places
6. **code_generations.files** → Código gerado

#### Campos que podem ser removidos/simplificados:

1. **execution_outputs.download_count** → Pode ser removido (analytics externa)
2. **agents.max_iter, max_rpm** → Podem ir para metadata JSON
3. **tasks.input_schema, output_schema** → Podem ser opcionais

### Campos Sugeridos para Adicionar

#### users:
- `role` ENUM('admin','user','viewer')
- `is_active` TINYINT(1)
- `last_login` TIMESTAMP
- `preferences` LONGTEXT JSON

#### projects:
- `status` ENUM('draft','active','archived')
- `framework` ENUM('crewai','langchain','autogen')
- `llm_config` LONGTEXT JSON
- `deployment_status` ENUM('not_deployed','deploying','deployed','error')

### Arquitetura Híbrida (Recomendada)

**JSON em projects.project_data**:
- ✅ Rede de Petri completa em um único campo
- ✅ Fácil integração com editor existente
- ✅ Versionamento simples
- ✅ Backup/restore facilitado

**Tabelas normalizadas separadas**:
- ✅ Queries SQL eficientes
- ✅ Listagens rápidas
- ✅ Filtros e buscas
- ✅ Relacionamentos explícitos

### Próximos Passos

1. **Criar as 8 tabelas faltantes** (SQL migrations)
2. **Implementar sincronização** project_data ↔ tabelas normalizadas
3. **Criar serviços API REST** para cada entidade
4. **Implementar lógica de negócio** (análise IA, geração de código, etc)

### Índices Recomendados

```sql
-- Índices compostos para queries comuns
CREATE INDEX idx_project_user ON projects(user_id, created_at DESC);
CREATE INDEX idx_session_project_status ON execution_sessions(project_id, status, started_at DESC);
CREATE INDEX idx_task_exec_session_status ON task_executions(session_id, status, started_at);
CREATE INDEX idx_logs_task_timestamp ON verbose_logs(task_execution_id, timestamp DESC);
CREATE INDEX idx_metrics_project_time ON monitoring_metrics(project_id, timestamp DESC);

-- Full-text search
ALTER TABLE projects ADD FULLTEXT INDEX ft_name_description (name, description);
ALTER TABLE documents ADD FULLTEXT INDEX ft_filename (filename, original_filename);
```

---

## Referências

- **Requisitos**: `docs/requisitosv0.2.txt`
- **Banco de Dados**: MySQL `langnet` em camerascasas.no-ip.info:3308
- **Editor de Petri Net**: `/home/pasteurjr/progreact/petri-net-editor`
- **Interface LangNet**: `/home/pasteurjr/progreact/langnet-interface`

---

**Documento criado em**: 2025-11-07
**Versão**: 1.0
**Autor**: Análise automatizada do sistema LangNet
