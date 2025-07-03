# Tabela de Telas Restantes - LangNet

| Prioridade     | Tela                        | Localização no Menu                                    | Caminho                                    | Wireframe/Spec                       | Requisitos Implementados                                                                                                                                                                                                                                                                                       |
| -------------- | --------------------------- | ------------------------------------------------------ | ------------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔴 **CRÍTICA** | **AgentChatPage.tsx**       | Projeto → Interface Interativa → Chat com Agentes      | `/project/{id}/interactive/agent-chat`     | **Wireframe 6.11** (versão completa) | **2.9.2** - Interface de Chat e Controle:<br/>• Interface de chat com agentes<br/>• Painéis de controle para monitoramento<br/>• Visualização de métricas e performance<br/>• Ferramentas de debugging e introspection<br/>• Controles para intervenção manual                                                 |
| 🔴 **ALTA**    | **AgentDesignerPage.tsx**   | Projeto → Interface Interativa → Designer de Agentes   | `/project/{id}/interactive/agent-designer` | **Wireframe 2.9.1.1**                | **2.9.1** - Interfaces React:<br/>• Configuração interativa de agentes e tarefas<br/>• Designer visual drag-and-drop<br/>• Formulários para configuração<br/>• Visualização do protótipo da interface                                                                                                          |
| 🟡 **MÉDIA**   | **ArtifactManagerPage.tsx** | Projeto → Interface Interativa → Gestão de Artefatos   | `/project/{id}/interactive/artifacts`      | **Wireframe 2.9.1.2**                | **2.9.1** - Interfaces React:<br/>• Suporte a upload e download de artefatos<br/>• Interface de upload drag-and-drop<br/>• Categorização automática<br/>• Preview de documentos<br/>• Gestão de metadados                                                                                                      |
| 🟡 **MÉDIA**   | **SystemStatePage.tsx**     | Projeto → Interface Interativa → Estado do Sistema     | `/project/{id}/interactive/system-state`   | **Wireframe 2.9.1.3**                | **2.9.1** - Interfaces React:<br/>• Implementação de componentes para visualização de estado<br/>• Visualização de logs e resultados<br/>• Dashboard de estado em tempo real<br/>• Métricas de performance<br/>• Alertas visuais                                                                               |
| 🟢 **BAIXA**   | **DynamicFormsPage.tsx**    | Projeto → Interface Interativa → Formulários Dinâmicos | `/project/{id}/interactive/forms`          | **Wireframe 2.9.1.4**                | **2.9.1** - Interfaces React:<br/>• Criação de formulários para configuração e parametrização<br/>• Wizard de configuração<br/>• Validação em tempo real<br/>• Templates inteligentes<br/>• Save state automático                                                                                              |
| 🟢 **BAIXA**   | **McpStateSyncPage.tsx**    | Global → MCP → Sincronização de Estados                | `/mcp/state-sync`                          | **Wireframe 2.7.2**                  | **2.7.2** - Sincronização de Estados:<br/>• Interface detalhada de sincronização<br/>• Resolução de conflitos manual<br/>• Visualização da fila de sincronização<br/>• Métricas de performance de sync<br/>• Monitor de conflitos em tempo real<br/>**Nota**: 50% já implementado em McpProjectIntegrationPage |

## 📋 Resumo por Categoria de Requisitos

### **2.7 - Módulo de Integração com MCP via FastMCP**

| Requisito                                   | Status              | Implementação                                                           |
| ------------------------------------------- | ------------------- | ----------------------------------------------------------------------- |
| **2.7.1** - Configuração de Conexão         | ✅ **COMPLETO**     | McpGlobalConfigPage.tsx                                                 |
| **2.7.2** - Sincronização de Estados        | ⚠️ **50% COMPLETO** | McpProjectIntegrationPage.tsx (config) + McpStateSyncPage.tsx (monitor) |
| **2.7.3** - Consumo e Exposição de Serviços | ✅ **COMPLETO**     | McpServiceDiscoveryPage.tsx                                             |

### **2.9.1 - Interfaces React**

| Funcionalidade                                            | Status          | Implementação           |
| --------------------------------------------------------- | --------------- | ----------------------- |
| Geração de código React para interfaces interativas       | ❌ **PENDENTE** | AgentDesignerPage.tsx   |
| Implementação de componentes para visualização de estado  | ❌ **PENDENTE** | SystemStatePage.tsx     |
| Criação de formulários para configuração e parametrização | ❌ **PENDENTE** | DynamicFormsPage.tsx    |
| Suporte a upload e download de artefatos                  | ❌ **PENDENTE** | ArtifactManagerPage.tsx |
| Visualização de logs e resultados                         | ❌ **PENDENTE** | SystemStatePage.tsx     |
| Visualização do protótipo da interface de agentes         | ❌ **PENDENTE** | AgentDesignerPage.tsx   |

### **2.9.2 - Interface de Chat e Controle**

| Funcionalidade                                      | Status          | Implementação     |
| --------------------------------------------------- | --------------- | ----------------- |
| Implementação de interface de chat com agentes      | ❌ **PENDENTE** | AgentChatPage.tsx |
| Painéis de controle para monitoramento de agentes   | ❌ **PENDENTE** | AgentChatPage.tsx |
| Visualização de métricas e performance              | ❌ **PENDENTE** | AgentChatPage.tsx |
| Ferramentas de debugging e introspection            | ❌ **PENDENTE** | AgentChatPage.tsx |
| Controles para intervenção manual quando necessário | ❌ **PENDENTE** | AgentChatPage.tsx |

## 🎯 Recomendação de Desenvolvimento

**Ordem de implementação sugerida:**

1. **AgentChatPage.tsx** - Funcionalidade core mais crítica
2. **AgentDesignerPage.tsx** - Interface principal de configuração
3. **ArtifactManagerPage.tsx** - Upload de documentos importante
4. **SystemStatePage.tsx** - Monitoramento essencial
5. **DynamicFormsPage.tsx** - Funcionalidade avançada
6. **McpStateSyncPage.tsx** - Opcional (50% já existe)

**Tempo estimado total: 3-4 sprints (3-4 semanas)**
