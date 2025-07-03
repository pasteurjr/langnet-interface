# LangNet Interface - Referência Rápida

## 📱 Páginas Principais

| Página | Arquivo | Função Principal |
|--------|---------|------------------|
| **Dashboard** | `src/pages/Dashboard.tsx` | Visão geral, projetos, métricas |
| **Agentes** | `src/pages/AgentsPage.tsx` | Lista e edição de agentes |
| **Designer** | `src/pages/AgentDesignerPage.tsx` | Interface visual com IA |
| **Documentos** | `src/pages/DocumentsPage.tsx` | Upload e análise automática |
| **Especificação** | `src/pages/SpecificationPage.tsx` | Documentação funcional |
| **YAML** | `src/pages/YamlPage.tsx` | Configurações de sistema |
| **Código** | `src/pages/CodePage.tsx` | Geração Python + execução |
| **Tarefas** | `src/pages/TasksPage.tsx` | Workflows e sequências |
| **Petri Net** | `src/pages/PetriNetPage.tsx` | Modelagem visual (placeholder) |
| **Monitoramento** | `src/pages/MonitoringPage.tsx` | Métricas + Langfuse |
| **Chat** | `src/pages/AgentChatPage.tsx` | Interface de chat |

## 🎨 Componentes Chave

### Layout
- **AppLayout** → `src/components/layout/AppLayout.tsx`
- **Sidebar** → `src/components/layout/Sidebar.tsx` 
- **Header** → `src/components/layout/Header.tsx`

### Cards Principais
- **ProjectCard** → `src/components/dashboard/ProjectCard.tsx`
- **AgentCard** → `src/components/agents/AgentCard.tsx`
- **DocumentCard** → `src/components/documents/DocumentCard.tsx`
- **YamlFileCard** → `src/components/yaml/YamlFileCard.tsx`
- **TaskCard** → `src/components/tasks/TaskCard.tsx`

### Modais Importantes
- **CreateProjectModal** → `src/components/projects/CreateProjectModal.tsx`
- **AgentFormModal** → `src/components/agents/AgentFormModal.tsx`
- **CodeGenerationModal** → `src/components/code/CodeGenerationModal.tsx`
- **AIDesignAssistant** → `src/components/ai/AIDesignAssistant.tsx`

## 🔄 Fluxo de Navegação

### Rotas Essenciais
```
/                           # Dashboard
/projects/:id               # Projeto específico
/projects/:id/documents     # Upload de requisitos
/projects/:id/agents        # Configuração de agentes
/projects/:id/yaml          # Arquivos de configuração
/projects/:id/code          # Código gerado
/interactive/agent-designer # Designer visual
```

### Contexto de Projeto
- **Global**: Menu completo do sistema
- **Projeto**: Menu focado no projeto atual
- **Navegação**: Via `NavigationContext` + `useNavigation`

## 📊 Estados e Status

### Status de Projeto
```typescript
enum ProjectStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress', 
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}
```

### Status de Agente
```typescript
enum AgentStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DRAFT = 'draft'
}
```

### Status de Documento
```typescript
enum DocumentStatus {
  UPLOADED = 'uploaded',
  ANALYZING = 'analyzing',
  ANALYZED = 'analyzed',
  ERROR = 'error'
}
```

## 🧠 Funcionalidades IA

### AI Design Assistant
- **Análise de acessibilidade** WCAG
- **Sugestões de design** contextuais
- **Otimização automática** de contrastes
- **Geração de conteúdo** personalizado

### Análise Automática
- **Documentos** → Extração de requisitos
- **Agentes** → Especificação inteligente
- **YAML** → Validação em tempo real
- **Código** → Qualidade e cobertura

## 🛠️ Tecnologias Principais

- **React 18** + **TypeScript**
- **React Router** para navegação
- **CSS Modules** para estilo
- **Monaco Editor** para código
- **Lucide React** para ícones
- **Context API** para estado

## 📁 Estrutura de Tipos

### Principais Interfaces
```typescript
interface Project { id, name, status, progress... }
interface Agent { id, name, role, goal, backstory... }
interface Document { id, status, extractedEntities... }
interface YamlFile { id, type, content, validation... }
interface CodeGenerationResult { files, metrics, deployment... }
```

### Localização
- **Tipos principais** → `src/types/index.ts`
- **Tipos específicos** → `src/types/[modulo].ts`

## 🎯 Comandos Úteis

### Para Nova Sessão
```bash
# Ler análise completa
cat docs/interface-analysis.md

# Examinar página específica
cat src/pages/[NomePage].tsx

# Ver componentes de um módulo
ls src/components/[modulo]/

# Verificar tipos
cat src/types/index.ts
```

### Componentes Frequentes
```bash
# Agentes
src/components/agents/AgentCard.tsx
src/components/agents/AgentFormModal.tsx

# Documentos  
src/components/documents/DocumentCard.tsx
src/components/documents/DocumentUploadModal.tsx

# Código
src/components/code/CodeEditor.tsx
src/components/code/CodeGenerationModal.tsx
```

## 🚀 Status de Implementação

### ✅ Completo
- Dashboard e projetos
- Gestão de agentes
- Upload de documentos  
- Especificação funcional
- Geração YAML
- Geração de código
- Designer de interface
- Monitoramento

### 🚧 Placeholder
- Editor de Redes de Petri
- Alguns recursos avançados de MCP

### 💡 Próximos Passos
- Implementar editor visual de Petri Net
- Completar integrações MCP
- Adicionar mais templates
- Otimizar performance