# LangNet Interface - Análise Completa das Telas e Componentes

## 🏗️ Arquitetura Geral

O sistema LangNet é organizado em **módulos funcionais** que seguem o fluxo completo de criação de aplicações baseadas em agentes:

1. **Dashboard** → Visão geral e gestão de projetos
2. **Documentação** → Upload e análise de requisitos  
3. **Especificação** → Geração de documentação funcional
4. **Agentes** → Design e configuração de agentes inteligentes
5. **Tarefas** → Definição de workflows
6. **YAML** → Geração de arquivos de configuração
7. **Redes de Petri** → Modelagem visual de fluxos
8. **Código** → Geração automática de Python
9. **Monitoramento** → Observabilidade via Langfuse
10. **MCP** → Integração com serviços externos

## 📱 Páginas Principais

### Dashboard (`src/pages/Dashboard.tsx`)
- **Interface central** com visão geral do sistema
- **Cards de projetos** recentes com status e progresso
- **Métricas do sistema** (projetos ativos, agentes, tokens)
- **Feed de atividades** em tempo real
- **Modal de criação** de novos projetos
- **Componentes**: ProjectCard, CreateProjectModal, ProjectCreationButton

### Gestão de Agentes

#### AgentsPage (`src/pages/AgentsPage.tsx`)
- **Grid de cards** para cada agente
- **Editor de propriedades** (role, goal, backstory, tools)
- **Especificador inteligente** para criação automática
- **Exportação para YAML** 
- **Status** ativo/inativo/rascunho
- **Componentes**: AgentCard, AgentFormModal, AgentSpecifierModal

#### AgentDesignerPage (`src/pages/AgentDesignerPage.tsx`)
- **Preview em tempo real** da interface dos agentes
- **AI Assistant** com sugestões de design
- **Análise de acessibilidade** (WCAG compliance)
- **Configuração de temas** e layouts
- **Geração de código React** otimizado
- **Componentes**: AIDesignAssistant

### Documentos (`src/pages/DocumentsPage.tsx`)
- **Upload com drag-and-drop** de PDFs, DOCs, etc.
- **Análise automática** de requisitos e entidades
- **Extração inteligente** de funcionalidades
- **Status de processamento** com progresso
- **Visualização** de resultados estruturados
- **Componentes**: DocumentCard, DocumentUploadModal, DocumentViewModal

### Especificação Funcional (`src/pages/SpecificationPage.tsx`)
- **Editor rich-text** para documentação técnica
- **Estrutura modular** (introdução, requisitos, modelo de dados)
- **Tabelas de requisitos** funcionais e não-funcionais
- **Validação automática** e controle de qualidade
- **Sistema de versões** e aprovações
- **Componentes**: SpecificationGenerationModal, SpecificationEditorModal, RequirementsTable, DataModelViewer

### YAML (`src/pages/YamlPage.tsx`)
- **Geração automática** de arquivos de configuração
- **Editor com syntax highlighting**
- **Validação em tempo real** de sintaxe
- **Suporte a agents.yaml, tasks.yaml, tools.yaml**
- **Import/export** de configurações
- **Componentes**: YamlFileCard, YamlGenerationModal, YamlEditorModal

### Código Python (`src/pages/CodePage.tsx`)
- **Geração completa** de aplicação Python
- **Editor integrado** (Monaco Editor)
- **Console de execução** em tempo real
- **Métricas de qualidade** e cobertura de testes
- **Deploy automático** e monitoramento
- **Componentes**: CodeGenerationModal, CodeEditor, FileExplorer, ExecutionConsole, DeploymentPanel

### Tarefas (`src/pages/TasksPage.tsx`)
- **Definição de workflows** e sequências
- **Mapeamento para agentes**
- **Configuração de entradas/saídas**
- **Componentes**: TaskCard, TaskFormModal, TaskSpecifierModal

### MCP (Model Context Protocol)
#### McpGlobalConfigPage (`src/pages/McpGlobalConfigPage.tsx`)
- **Configuração global** do protocolo MCP
- **Descoberta automática** de serviços
- **Gestão de servidores** e conexões

#### McpServiceDiscoveryPage (`src/pages/McpServiceDiscoveryPage.tsx`)
- **Descoberta de serviços** disponíveis
- **Monitoramento de status** e performance
- **Catálogo de integrações**

#### McpProjectIntegrationPage (`src/pages/McpProjectIntegrationPage.tsx`)
- **Integração específica** por projeto
- **Configuração de endpoints** customizados
- **Sincronização de estados**

### Monitoramento (`src/pages/MonitoringPage.tsx`)
- **Dashboard de métricas** em tempo real
- **Integração com Langfuse**
- **Alertas e notificações**
- **Componentes**: MetricsPanel, AlertsPanel, TraceViewer, SystemOverview, LangfuseConnectionModal

### Chat com Agentes (`src/pages/AgentChatPage.tsx`)
- **Interface de chat** interativa
- **Comunicação direta** com agentes
- **Histórico de conversas**
- **Componentes**: ChatInterface

## 🔄 Fluxo de Navegação

### Contexto de Navegação
O sistema usa **contexto inteligente** através do `NavigationContext`:

1. **Modo Global**: Acesso a todas as páginas principais
2. **Modo Projeto**: Contexto específico com ID do projeto
3. **Sidebar dinâmica**: Menu muda com base no contexto
4. **Breadcrumbs visuais**: Progresso no fluxo

### Rotas Principais
```
/                                    # Dashboard
/projects                           # Lista de projetos  
/projects/:id                       # Detalhes do projeto
/projects/:id/documents             # Documentos
/projects/:id/spec                  # Especificação
/projects/:id/agents                # Agentes
/projects/:id/tasks                 # Tarefas
/projects/:id/yaml                  # Configurações YAML
/projects/:id/petri                 # Redes de Petri
/projects/:id/code                  # Código gerado
/projects/:id/monitor               # Monitoramento
/projects/:id/chat                  # Chat com agentes
/interactive/agent-designer         # Designer avançado
/mcp/config                         # Configuração MCP
/mcp/services                       # Serviços MCP
/settings                           # Configurações
```

## 🎨 Componentes de Interface

### Layout Base
- **AppLayout** (`src/components/layout/AppLayout.tsx`): Container principal responsivo
- **Sidebar** (`src/components/layout/Sidebar.tsx`): Menu colapsável com contexto
- **Header** (`src/components/layout/Header.tsx`): Título, busca, notificações, perfil

### Componentes por Categoria

#### Agentes (`src/components/agents/`)
- **AgentCard**: Visualização de agentes com ações
- **AgentFormModal**: Editor completo de propriedades
- **AgentSpecifierModal**: Criação automática via IA
- **AgentMonitoringTable**: Monitoramento de performance
- **AgentPerformanceDashboard**: Métricas detalhadas
- **ChatInterface**: Interface de chat
- **InterventionControls**: Controles de intervenção

#### AI (`src/components/ai/`)
- **AIDesignAssistant**: Assistente para design de interfaces

#### Código (`src/components/code/`)
- **CodeEditor**: Editor com Monaco
- **CodeGenerationModal**: Configuração de geração
- **FileExplorer**: Navegador de arquivos
- **ExecutionConsole**: Console em tempo real
- **DeploymentPanel**: Painel de deploy

#### Dashboard (`src/components/dashboard/`)
- **ProjectCard**: Cards de projetos

#### Documentos (`src/components/documents/`)
- **DocumentCard**: Preview com análise
- **DocumentUploadModal**: Upload com drag-and-drop
- **DocumentViewModal**: Visualização detalhada

#### Especificação (`src/components/specification/`)
- **SpecificationGenerationModal**: Configuração de geração
- **SpecificationEditorModal**: Editor rich-text
- **RequirementsTable**: Tabela de requisitos
- **DataModelViewer**: Visualização de modelo de dados

#### Tarefas (`src/components/tasks/`)
- **TaskCard**: Cards de tarefas
- **TaskFormModal**: Editor de tarefas
- **TaskSpecifierModal**: Especificação automática

#### YAML (`src/components/yaml/`)
- **YamlFileCard**: Editor inline
- **YamlGenerationModal**: Configuração de geração
- **YamlEditorModal**: Editor completo

#### Projetos (`src/components/projects/`)
- **ProjectCard**: Visualização de projetos
- **CreateProjectModal**: Wizard de criação
- **ProjectCreationButton**: Botão de criação

#### Monitoramento (`src/components/monitoring/`)
- **MetricsPanel**: Métricas do sistema
- **AlertsPanel**: Alertas e notificações
- **TraceViewer**: Visualização de traces
- **SystemOverview**: Visão geral do sistema
- **LangfuseConnectionModal**: Configuração Langfuse

#### Deploy (`src/components/deployment/`)
- **DeploymentHistory**: Histórico de deploys
- **EnvironmentConfig**: Configuração de ambientes
- **InfrastructurePanel**: Painel de infraestrutura
- **PipelineViewer**: Visualização de pipelines
- **SecurityPanel**: Painel de segurança

#### Configurações (`src/components/settings/`)
- **GeneralSettings**: Configurações gerais
- **LLMSettings**: Configuração de LLMs
- **IntegrationsSettings**: Integrações
- **SecuritySettings**: Segurança
- **NotificationSettings**: Notificações
- **UserManagement**: Gestão de usuários
- **AnalyticsPanel**: Analytics
- **BackupSettings**: Backup

## 🧠 Funcionalidades Inteligentes

### AI Design Assistant
- **Análise automática** de acessibilidade
- **Sugestões contextuais** baseadas no projeto
- **Otimização de contrastes** e layouts
- **Geração de conteúdo** personalizado
- **Conformidade WCAG** integrada

### Validação em Tempo Real
- **YAML**: Sintaxe e conformidade
- **Especificações**: Completude e consistência  
- **Código**: Qualidade e cobertura
- **Agentes**: Configurações válidas

### Monitoramento Integrado
- **Langfuse**: Traces de LLM
- **Métricas**: Performance e uso
- **Logs**: Execução em tempo real
- **Alertas**: Problemas automáticos

## 📊 Tipos e Interfaces

### Principais Enums e Types (`src/types/index.ts`)
```typescript
// Status de Projetos
enum ProjectStatus { DRAFT, IN_PROGRESS, COMPLETED, ARCHIVED }

// Status de Agentes
enum AgentStatus { ACTIVE, INACTIVE, DRAFT }

// Status de Documentos
enum DocumentStatus { UPLOADED, ANALYZING, ANALYZED, ERROR }

// Tipos de Arquivos YAML
enum YamlFileType { AGENTS, TASKS, TOOLS, CONFIG }

// Status de Especificação
enum SpecificationStatus { DRAFT, GENERATED, REVIEWING, APPROVED, NEEDS_REVISION }

// Status de Geração de Código
enum CodeGenerationStatus { PENDING, GENERATING, READY, ERROR, BUILDING, DEPLOYING, DEPLOYED }
```

### Interfaces Principais
- **Project**: Estrutura de projetos
- **Agent**: Definição de agentes
- **Task**: Configuração de tarefas
- **Document**: Documentos e análise
- **YamlFile**: Arquivos de configuração
- **SpecificationDocument**: Documentação funcional
- **CodeGenerationResult**: Resultado da geração
- **McpServer/McpService**: Protocolo MCP

## 🎯 Pontos Fortes da Interface

1. **Fluxo Linear**: Guia natural do documento ao código
2. **Feedback Visual**: Status claro em cada etapa
3. **Automação Inteligente**: IA reduz trabalho manual
4. **Componentização**: Interface modular e reutilizável
5. **Responsividade**: Funciona em desktop, tablet, mobile
6. **Acessibilidade**: Conformidade WCAG integrada
7. **Contexto Dinâmico**: Navegação inteligente por projeto
8. **Tempo Real**: Updates e monitoramento instantâneo

## 🔧 Estado da Implementação

### ✅ Implementado
- Dashboard e navegação
- Gestão de agentes com IA
- Upload e análise de documentos
- Especificação funcional completa
- Geração de YAML
- Geração de código Python
- Monitoramento integrado
- Interface MCP
- Designer visual de agentes

### 🚧 Em Desenvolvimento
- Editor de Redes de Petri (placeholder)
- Algumas integrações MCP avançadas
- Funcionalidades de deploy automático

### 🎨 Características de Design
- **Material Design** inspirado
- **Temas claro/escuro** preparados
- **CSS Modules** para isolamento
- **Responsividade** mobile-first
- **Acessibilidade WCAG AA**

## 📝 Notas para Desenvolvimento

- Sistema usa **React 18 + TypeScript**
- **React Router** para navegação
- **Context API** para estado global
- **CSS Modules** para estilização
- **Monaco Editor** para código
- **Lucide React** para ícones
- Estrutura preparada para **Redux Toolkit**

O sistema demonstra uma **arquitetura de interface muito bem pensada**, combinando **automação inteligente** com **controle manual detalhado**, permitindo tanto usuários novatos quanto experts aproveitarem todas as funcionalidades.