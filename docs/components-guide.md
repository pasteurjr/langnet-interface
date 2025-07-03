# LangNet - Guia de Componentes

## 🗂️ Estrutura de Componentes

```
src/components/
├── layout/           # Layout base da aplicação
├── dashboard/        # Componentes do dashboard
├── projects/         # Gestão de projetos
├── agents/          # Componentes de agentes
├── tasks/           # Gestão de tarefas
├── documents/       # Upload e análise de documentos
├── specification/   # Especificação funcional
├── yaml/           # Arquivos YAML
├── code/           # Geração e edição de código
├── monitoring/     # Monitoramento e métricas
├── deployment/     # Deploy e infraestrutura
├── settings/       # Configurações do sistema
└── ai/             # Assistentes de IA
```

## 🏗️ Componentes de Layout

### AppLayout (`src/components/layout/AppLayout.tsx`)
**Container principal** da aplicação
- Gerencia layout responsivo
- Inclui Sidebar + Header + área de conteúdo
- Controla estado de colapso da sidebar

```typescript
interface AppLayoutProps {
  // Outlet para React Router
}
```

### Sidebar (`src/components/layout/Sidebar.tsx`)
**Menu de navegação** lateral inteligente
- Menu colapsável com contexto
- Navegação por projeto vs global
- Botão "Voltar ao Dashboard" em contexto de projeto

```typescript
interface SidebarProps {
  menuItems: MenuItem[];
  collapsed: boolean;
  onToggleCollapse: () => void;
}
```

### Header (`src/components/layout/Header.tsx`)
**Barra superior** com controles globais
- Título da página atual
- Busca global
- Notificações
- Menu de perfil

```typescript
interface HeaderProps {
  title: string;
  notifications: Notification[];
  onNotificationClick: (id: string) => void;
  onProfileClick: () => void;
  onSearchSubmit: (query: string) => void;
}
```

## 📊 Componentes de Dashboard

### ProjectCard (`src/components/dashboard/ProjectCard.tsx`)
**Card de projeto** com informações resumidas
- Status visual e progresso
- Ações rápidas (abrir, duplicar, excluir)
- Preview de agentes e métricas

```typescript
interface ProjectCardProps {
  project: Project;
  onClick: (id: string) => void;
}
```

## 🤖 Componentes de Agentes

### AgentCard (`src/components/agents/AgentCard.tsx`)
**Visualização de agente** com ações
- Status ativo/inativo
- Preview de role e goal
- Botões para editar, excluir, alternar status

```typescript
interface AgentCardProps {
  agent: Agent;
  onEdit: (agent: Agent) => void;
  onDelete: (agentId: string) => void;
  onToggleStatus: (agentId: string) => void;
}
```

### AgentFormModal (`src/components/agents/AgentFormModal.tsx`)
**Editor completo** de propriedades do agente
- Formulário para role, goal, backstory
- Seleção de tools disponíveis
- Configurações avançadas (verbose, delegation, etc.)

```typescript
interface AgentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (agentData: Partial<Agent>) => void;
  agent?: Agent | null;
}
```

### AgentSpecifierModal (`src/components/agents/AgentSpecifierModal.tsx`)
**Criação automática** de agentes via IA
- Análise do projeto para sugerir agentes
- Geração de múltiplos agentes especializados
- Configuração em lote

```typescript
interface AgentSpecifierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSpecify: (agents: Partial<Agent>[]) => void;
  projectId: string;
}
```

### ChatInterface (`src/components/agents/ChatInterface.tsx`)
**Interface de chat** com agentes
- Histórico de mensagens
- Suporte a markdown
- Indicadores de digitação

```typescript
interface ChatInterfaceProps {
  agentId: string;
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isTyping?: boolean;
}
```

## 📋 Componentes de Tarefas

### TaskCard (`src/components/tasks/TaskCard.tsx`)
**Card de tarefa** com informações essenciais
- Descrição e agente responsável
- Status de execução
- Inputs/outputs esperados

```typescript
interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onToggleStatus: (taskId: string) => void;
}
```

### TaskFormModal (`src/components/tasks/TaskFormModal.tsx`)
**Editor de tarefas** completo
- Configuração de description e expected_output
- Vinculação com agente
- Definição de tools e contexto

```typescript
interface TaskFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (taskData: Partial<Task>) => void;
  task?: Task | null;
  agents: Agent[];
}
```

## 📄 Componentes de Documentos

### DocumentCard (`src/components/documents/DocumentCard.tsx`)
**Card de documento** com análise
- Preview do arquivo
- Status de processamento
- Entidades extraídas e requisitos

```typescript
interface DocumentCardProps {
  document: Document;
  onView: (document: Document) => void;
  onDelete: (documentId: string) => void;
  onReanalyze: (documentId: string) => void;
}
```

### DocumentUploadModal (`src/components/documents/DocumentUploadModal.tsx`)
**Modal de upload** com drag-and-drop
- Suporte a múltiplos formatos
- Instruções para análise IA
- Progress de upload

```typescript
interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (files: FileList, instructions?: string) => void;
  isUploading?: boolean;
}
```

### DocumentViewModal (`src/components/documents/DocumentViewModal.tsx`)
**Visualização detalhada** do documento
- Preview do conteúdo
- Entidades e requisitos extraídos
- Opções de exportação

```typescript
interface DocumentViewModalProps {
  isOpen: boolean;
  document: Document | null;
  onClose: () => void;
  onExport: (doc: Document, format: 'json' | 'csv' | 'pdf') => void;
}
```

## 📝 Componentes de Especificação

### SpecificationGenerationModal (`src/components/specification/SpecificationGenerationModal.tsx`)
**Configuração de geração** de especificação
- Seleção de documentos fonte
- Opções de inclusão (data model, user stories, etc.)
- Nível de detalhe e audiência

```typescript
interface SpecificationGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (request: SpecificationGenerationRequest) => void;
  projectId: string;
}
```

### RequirementsTable (`src/components/specification/RequirementsTable.tsx`)
**Tabela de requisitos** funcionais/não-funcionais
- Filtros por prioridade e categoria
- Edição inline
- Export para diferentes formatos

```typescript
interface RequirementsTableProps {
  requirements: (FunctionalRequirement | NonFunctionalRequirement)[];
  onEdit?: (req: any) => void;
  onDelete?: (reqId: string) => void;
}
```

### DataModelViewer (`src/components/specification/DataModelViewer.tsx`)
**Visualização do modelo de dados**
- Entidades e relacionamentos
- Atributos e constraints
- Diagrama visual interativo

```typescript
interface DataModelViewerProps {
  entities: DataEntity[];
  onEntityClick?: (entity: DataEntity) => void;
}
```

## 📄 Componentes YAML

### YamlFileCard (`src/components/yaml/YamlFileCard.tsx`)
**Card de arquivo YAML** com validação
- Status de validação visual
- Preview do conteúdo
- Ações para editar, validar, baixar

```typescript
interface YamlFileCardProps {
  yamlFile: YamlFile;
  onEdit: (file: YamlFile) => void;
  onValidate: (fileId: string) => void;
  onDownload: (file: YamlFile) => void;
  onRegenerate: (fileId: string) => void;
  onPreview: (file: YamlFile) => void;
}
```

### YamlEditorModal (`src/components/yaml/YamlEditorModal.tsx`)
**Editor completo** de YAML
- Syntax highlighting
- Validação em tempo real
- Auto-complete para estruturas

```typescript
interface YamlEditorModalProps {
  isOpen: boolean;
  yamlFile: YamlFile;
  onClose: () => void;
  onSave: (fileId: string, content: string) => void;
  onValidate: (fileId: string, content: string) => ValidationIssue[];
}
```

## 💻 Componentes de Código

### CodeEditor (`src/components/code/CodeEditor.tsx`)
**Editor de código** baseado no Monaco
- Syntax highlighting para Python
- IntelliSense e autocomplete
- Integração com LSP

```typescript
interface CodeEditorProps {
  file: CodeFile;
  onSave: (content: string) => void;
  readOnly?: boolean;
}
```

### CodeGenerationModal (`src/components/code/CodeGenerationModal.tsx`)
**Configuração de geração** de código
- Seleção de framework (CrewAI, LangChain)
- Configuração de LLM e memória
- Opções de deploy e testes

```typescript
interface CodeGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (config: CodeGenerationRequest) => void;
  projectId: string;
}
```

### FileExplorer (`src/components/code/FileExplorer.tsx`)
**Navegador de arquivos** do projeto
- Estrutura em árvore
- Filtros por tipo
- Ações de arquivo

```typescript
interface FileExplorerProps {
  files: CodeFile[];
  structure: ProjectStructure;
  onFileSelect: (file: CodeFile) => void;
  selectedFile?: CodeFile | null;
}
```

### ExecutionConsole (`src/components/code/ExecutionConsole.tsx`)
**Console de execução** em tempo real
- Logs de execução
- Estado da rede de Petri
- Métricas de performance

```typescript
interface ExecutionConsoleProps {
  logs: ExecutionLogEntry[];
  petriNetState?: PetriNetExecutionState;
  isExecuting: boolean;
}
```

## 📊 Componentes de Monitoramento

### MetricsPanel (`src/components/monitoring/MetricsPanel.tsx`)
**Painel de métricas** do sistema
- Gráficos em tempo real
- KPIs principais
- Alertas visuais

```typescript
interface MetricsPanelProps {
  metrics: MonitoringMetrics;
  timeRange: string;
  onTimeRangeChange: (range: string) => void;
}
```

### TraceViewer (`src/components/monitoring/TraceViewer.tsx`)
**Visualização de traces** Langfuse
- Timeline de execução
- Spans aninhados
- Detalhes de LLM calls

```typescript
interface TraceViewerProps {
  traces: TraceData[];
  selectedTrace?: string;
  onTraceSelect: (traceId: string) => void;
}
```

## 🤖 Componentes de IA

### AIDesignAssistant (`src/components/ai/AIDesignAssistant.tsx`)
**Assistente de design** inteligente
- Análise de acessibilidade WCAG
- Sugestões contextuais
- Aplicação automática de melhorias

```typescript
interface AIDesignAssistantProps {
  isOpen: boolean;
  onClose: () => void;
  suggestions: AISuggestion[];
  analysis: AIAnalysis | null;
  isLoading: boolean;
  onApplySuggestion: (suggestion: AISuggestion) => void;
  onGenerateContent: (type: string, context?: any) => void;
  currentConfig: InterfaceConfig;
  agents: Agent[];
  projectId: string;
}
```

## 📦 Componentes de Projetos

### CreateProjectModal (`src/components/projects/CreateProjectModal.tsx`)
**Modal de criação** de projeto
- Formulário com validação
- Seleção de templates
- Configurações iniciais

```typescript
interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateProject: (projectData: Partial<Project>) => void;
}
```

### ProjectCreationButton (`src/components/projects/ProjectCreationButton.tsx`)
**Botão de criação** de projeto
- Design destacado
- Ação principal do dashboard

```typescript
interface ProjectCreationButtonProps {
  onOpenModal: () => void;
}
```

## 🔧 Padrões de Implementação

### Props Interface
```typescript
// Padrão para modais
interface [Component]ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave/onSubmit: (data: any) => void;
  // dados específicos...
}

// Padrão para cards  
interface [Component]CardProps {
  [item]: [Type];
  onEdit: (item: [Type]) => void;
  onDelete: (id: string) => void;
  // ações específicas...
}
```

### Estado e Handlers
```typescript
// Padrão de estado em páginas
const [items, setItems] = useState<Item[]>([]);
const [selectedItem, setSelectedItem] = useState<Item | null>(null);
const [isModalOpen, setIsModalOpen] = useState(false);

// Padrão de handlers
const handleCreate = () => setIsModalOpen(true);
const handleEdit = (item: Item) => {
  setSelectedItem(item);
  setIsModalOpen(true);
};
const handleSave = (data: Partial<Item>) => {
  // lógica de save...
  setIsModalOpen(false);
};
```

### CSS Modules
```typescript
// Importação de estilos
import './ComponentName.css';

// Classes CSS
className="component-name"
className="component-name__element"
className="component-name--modifier"
```

Este guia serve como **referência rápida** para entender e trabalhar com os componentes do sistema LangNet. Cada componente segue padrões consistentes de props, estado e estilização.