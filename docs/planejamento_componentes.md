# Planejamento de Componentes React para o Sistema LangNet

## Arquitetura Geral

### Tecnologias Base
- **React** com **TypeScript** como framework principal
- **Material-UI** para componentes de interface
- **React Router** para navegação entre páginas
- **Redux Toolkit** para gerenciamento de estado global
- **React Flow** para o editor de Redes de Petri
- **Monaco Editor** para edição de código e YAML
- **D3.js** para visualizações e gráficos
- **Axios** para requisições HTTP

### Estrutura de Diretórios
```
src/
├── assets/            # Imagens, ícones e recursos estáticos
├── components/        # Componentes reutilizáveis
│   ├── common/        # Componentes genéricos (botões, inputs, etc.)
│   ├── layout/        # Componentes de layout (header, sidebar, etc.)
│   ├── dashboard/     # Componentes específicos do dashboard
│   ├── projects/      # Componentes de gerenciamento de projetos
│   ├── documents/     # Componentes para análise de documentos
│   ├── agents/        # Componentes para definição de agentes
│   ├── petri/         # Componentes do editor de Redes de Petri
│   ├── code/          # Componentes para visualização e edição de código
│   └── monitoring/    # Componentes de monitoramento e analytics
├── pages/             # Páginas principais da aplicação
├── hooks/             # Custom hooks
├── services/          # Serviços e APIs
├── store/             # Configuração do Redux e slices
├── types/             # Definições de tipos TypeScript
├── utils/             # Funções utilitárias
└── App.tsx            # Componente raiz da aplicação
```

## Componentes Principais

### Componentes de Layout

#### `AppLayout`
- Container principal que envolve toda a aplicação
- Gerencia o layout responsivo
- Inclui `Sidebar`, `Header` e área de conteúdo principal

#### `Sidebar`
- Menu de navegação lateral
- Exibe links para as diferentes seções
- Colapsa em telas menores
- Suporta submenus para navegação em projetos

#### `Header`
- Barra superior com título da página atual
- Controles globais (busca, notificações, perfil)
- Ações contextuais baseadas na página atual

#### `ProjectHeader`
- Exibe informações do projeto atual
- Mostra progresso nas etapas do fluxo
- Botões de ação para salvar, exportar, etc.

### Componentes de Dashboard

#### `Dashboard`
- Página inicial com visão geral do sistema
- Organiza e exibe `ProjectCard`, `MetricsPanel` e `ActivityFeed`

#### `ProjectCard`
- Card para exibição de projetos recentes
- Mostra thumbnail, nome, status e progresso
- Ações rápidas (abrir, duplicar, excluir)

#### `MetricsPanel`
- Exibe métricas e estatísticas do sistema
- Gráficos de uso de recursos e atividade
- Indicadores de performance

#### `ActivityFeed`
- Lista de atividades recentes no sistema
- Filtragem por tipo de atividade e projeto
- Ordenação cronológica

### Componentes de Projetos

#### `ProjectCreationWizard`
- Fluxo passo a passo para criação de projetos
- Formulários para informações básicas
- Seleção de templates e configurações

#### `ProjectList`
- Lista paginada de todos os projetos
- Filtros e ordenação
- Visualização em grade ou lista

#### `ProjectSettings`
- Formulário para configurações do projeto
- Gerenciamento de colaboradores
- Configurações de integração

### Componentes de Documentação

#### `DocumentUploader`
- Interface para upload de documentos
- Suporte a drag-and-drop
- Visualização de progresso

#### `DocumentViewer`
- Visualizador de documentos integrado
- Suporte a diferentes formatos
- Ferramentas de anotação e highlight

#### `RequirementsExtractor`
- Exibe requisitos extraídos automaticamente
- Interface para edição e organização
- Validação e categorização

### Componentes de Especificação

#### `SpecificationEditor`
- Editor rich-text para especificação funcional
- Formatação e estruturação de conteúdo
- Histórico de versões

#### `EntityDiagram`
- Visualização de entidades e relacionamentos
- Editor interativo para modelagem de dados
- Exportação de diagramas

### Componentes de Agentes e Tarefas

#### `AgentDesigner`
- Interface tipo card para definição de agentes
- Campos para role, goal, backstory, etc.
- Validação em tempo real

#### `AgentList`
- Lista de agentes definidos no projeto
- Visualização de relações entre agentes
- Ações para editar, duplicar, remover

#### `TaskDesigner`
- Editor para definição de tarefas
- Configuração de entradas, saídas e passos
- Vinculação com agentes

#### `TaskFlow`
- Visualização do fluxo entre tarefas
- Definição de dependências
- Validação de completude

### Componentes de YAML

#### `YamlEditor`
- Editor de código para arquivos YAML
- Syntax highlighting
- Validação em tempo real

#### `YamlPreview`
- Visualização estruturada do conteúdo YAML
- Alternância entre visualização e código
- Feedback visual para erros

### Componentes do Editor de Redes de Petri

#### `PetriNetEditor`
- Canvas principal para edição da rede
- Integração com React Flow
- Ferramentas de zoom, pan e seleção

#### `PetriToolbar`
- Barra de ferramentas para o editor
- Botões para adicionar places, transitions, arcs
- Controles de simulação

#### `PetriProperties`
- Painel lateral para propriedades do elemento selecionado
- Formulários para edição de atributos
- Validação contextual

#### `PetriSimulator`
- Controles para simulação da rede
- Visualização de tokens em movimento
- Histórico de estados

### Componentes de Código

#### `CodeGenerator`
- Interface para configuração da geração de código
- Opções de frameworks e componentes
- Visualização da estrutura a ser gerada

#### `CodeEditor`
- Editor baseado em Monaco
- Suporte a múltiplas linguagens
- Funcionalidades de IDE (autocomplete, etc.)

#### `FileExplorer`
- Navegador de arquivos do projeto
- Estrutura em árvore
- Ações para criar, renomear, excluir arquivos

### Componentes de Monitoramento

#### `MonitoringDashboard`
- Visão geral de métricas e performance
- Gráficos em tempo real
- Filtros por período e componentes

#### `AgentMonitor`
- Visualização da atividade dos agentes
- Logs e eventos
- Métricas de performance

#### `LangfuseIntegration`
- Visualização de traces do Langfuse
- Análise detalhada de operações de LLM
- Filtros e busca avançada

### Componentes de Chat e Interação

#### `AgentChat`
- Interface de chat para comunicação com agentes
- Histórico de mensagens
- Visualização do "pensamento" do agente

#### `ExecutionVisualizer`
- Visualização do fluxo de execução
- Estado atual destacado
- Navegação entre estados

## Rotas Principais

```
/                       # Dashboard principal
/projects               # Lista de projetos
/projects/new           # Criação de novo projeto
/projects/:id           # Visão geral do projeto
/projects/:id/documents # Documentação e análise
/projects/:id/spec      # Especificação funcional
/projects/:id/agents    # Definição de agentes
/projects/:id/tasks     # Definição de tarefas
/projects/:id/yaml      # Edição de YAML
/projects/:id/petri     # Editor de Redes de Petri
/projects/:id/code      # Geração e edição de código
/projects/:id/monitor   # Monitoramento e analytics
/projects/:id/chat      # Interface de chat com agentes
/settings               # Configurações do sistema
/help                   # Documentação e ajuda
```

## Fluxos de Interação Principais

### Fluxo de Criação de Projeto
1. Usuário acessa dashboard e clica em "Novo Projeto"
2. `ProjectCreationWizard` guia o usuário pelos passos:
   - Informações básicas (nome, descrição)
   - Seleção de template ou início em branco
   - Configurações avançadas
3. Após criação, redireciona para visão geral do projeto

### Fluxo de Análise de Documentos
1. Usuário navega para seção de documentos do projeto
2. Utiliza `DocumentUploader` para carregar arquivos
3. `DocumentViewer` exibe o conteúdo dos documentos
4. `RequirementsExtractor` processa e exibe requisitos extraídos
5. Usuário revisa, edita e confirma os requisitos

### Fluxo de Modelagem de Rede de Petri
1. Usuário acessa o editor de Redes de Petri
2. Visualiza rede inicial gerada automaticamente
3. Utiliza `PetriToolbar` para adicionar/editar elementos
4. Configura propriedades via `PetriProperties`
5. Valida e simula a rede com `PetriSimulator`
6. Salva e exporta o modelo finalizado

### Fluxo de Geração de Código
1. Usuário navega para seção de código
2. Configura opções via `CodeGenerator`
3. Inicia processo de geração
4. Visualiza e edita código gerado com `CodeEditor`
5. Navega entre arquivos com `FileExplorer`
6. Executa e testa o código gerado

## Considerações de Implementação

### Responsividade
- Layout fluido com breakpoints para diferentes tamanhos de tela
- Sidebar colapsável em telas menores
- Reorganização de componentes em layouts mobile
- Suporte a gestos touch para editor de Petri

### Acessibilidade
- Contraste adequado e temas claro/escuro
- Suporte a navegação por teclado
- Atributos ARIA para screen readers
- Mensagens de erro e feedback claros

### Performance
- Carregamento lazy de componentes pesados
- Virtualização para listas longas
- Memoização de componentes e cálculos custosos
- Otimização de renderização para o editor de Petri

### Estado Global
- Slices Redux para diferentes áreas funcionais:
  - `projectsSlice`: gerenciamento de projetos
  - `documentsSlice`: documentos e requisitos
  - `agentsSlice`: definição de agentes e tarefas
  - `petriSlice`: estado do editor de Petri
  - `uiSlice`: estado da interface (tema, sidebar, etc.)
  - `authSlice`: autenticação e permissões

### Integração com Backend
- Serviços API organizados por domínio
- Hooks personalizados para operações comuns
- Tratamento consistente de erros e loading states
- Cache e invalidação inteligente de dados
