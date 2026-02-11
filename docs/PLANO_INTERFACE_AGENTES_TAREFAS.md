# 🎨 PLANO: PÁGINA "AGENTES & TAREFAS" (AgentTaskPage.tsx)

## 📊 BANCO DE DADOS EXISTENTE

✅ **Tabelas já criadas**:
- `agents`: id, project_id, agent_id, name, role, goal, backstory, tools, verbose, allow_delegation, status, metadata
- `tasks`: id, project_id, task_id, name, description, agent_id, expected_output, tools, input_schema, output_schema, metadata
- `yaml_files`: id, project_id, file_type (agents/tasks), filename, content, version, is_valid

✅ **Nova tabela necessária** (criar migration):
```sql
CREATE TABLE execution_agent_task_sessions (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  specification_session_id CHAR(36), -- Link para especificação usada
  session_name VARCHAR(255),
  status ENUM('draft','generating','completed','failed') DEFAULT 'draft',

  -- Contadores de geração
  total_agents_generated INT DEFAULT 0,
  total_tasks_generated INT DEFAULT 0,

  -- YAMLs gerados
  agents_yaml_content LONGTEXT,
  tasks_yaml_content LONGTEXT,

  -- Timestamps
  started_at TIMESTAMP NULL,
  finished_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (specification_session_id) REFERENCES execution_specification_sessions(id)
) ENGINE=InnoDB;

CREATE TABLE execution_agent_task_chat_messages (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  session_id CHAR(36) NOT NULL,
  sender_type ENUM('user','agent','system') NOT NULL,
  message_text LONGTEXT,
  message_type ENUM('chat','refinement','suggestion') DEFAULT 'chat',
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSON,
  FOREIGN KEY (session_id) REFERENCES execution_agent_task_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

---

## 🎨 INTERFACE PROPOSTA

### **LAYOUT GERAL** (3 Colunas)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🤖 AGENTES & TAREFAS - Sistema Multi-Agente                         │
├──────────────────┬──────────────────────────┬─────────────────────┤
│                  │                          │                     │
│  📝 ENTRADA      │   💬 CHAT & REFINAMENTO  │  📊 RESULTADOS      │
│   (Coluna 1)     │     (Coluna 2)           │   (Coluna 3)        │
│                  │                          │                     │
│  [Card Config]   │   [Chat Interface]       │  [Cards Gerados]    │
│                  │   - Instruções detalhadas│  - AgentsSummaryCard│
│  [Botões]        │   - Refinamento          │  - TasksSummaryCard │
│                  │   - Histórico mensagens  │  - YAMLPreviewCard  │
│                  │                          │  - ActionsCard      │
│                  │                          │                     │
└──────────────────┴──────────────────────────┴─────────────────────┘
```

---

## 📝 COLUNA 1: ENTRADA & CONFIGURAÇÃO

### **Card 1: Seleção de Especificação**

```tsx
┌──────────────────────────────────────────┐
│ 📄 ESPECIFICAÇÃO FUNCIONAL               │
├──────────────────────────────────────────┤
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Selecionar Especificação             │ │
│ │ ▼ Especificação v2.0 (15/12/2025)   │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ℹ️ 14 seções completas                   │
│ ℹ️ 25 requisitos funcionais             │
│ ℹ️ 12 casos de uso                      │
│                                          │
│ [📖 Visualizar Especificação]           │
│                                          │
└──────────────────────────────────────────┘
```

**O que o usuário faz:**
- Seleciona uma especificação funcional existente (dropdown com versões)
- Clica para visualizar a especificação antes de gerar

---

### **Card 2: Documentos Complementares (Opcional)**

```tsx
┌──────────────────────────────────────────┐
│ 📎 DOCUMENTOS COMPLEMENTARES (Opcional)  │
├──────────────────────────────────────────┤
│                                          │
│ Adicione docs adicionais para enriquecer│
│ a geração de agentes e tarefas:         │
│                                          │
│ ┌────────────────────────────────────┐   │
│ │ 📄 arquitetura_sistema.pdf         │   │
│ │ 📄 workflow_atual.docx             │   │
│ │ [➕ Adicionar Documento]           │   │
│ └────────────────────────────────────┘   │
│                                          │
└──────────────────────────────────────────┘
```

**O que o usuário faz:**
- (Opcional) Faz upload de documentos extras (arquitetura, diagramas, workflows)
- Esses docs são enviados junto na geração para dar mais contexto ao LLM

---

### **Card 3: Configurações de Geração**

```tsx
┌──────────────────────────────────────────┐
│ ⚙️ CONFIGURAÇÕES                          │
├──────────────────────────────────────────┤
│                                          │
│ Estratégia de Geração:                  │
│ ○ Balanceada (8-12 agentes, 20-30 tasks)│
│ ● Detalhada (12-15 agentes, 30-40 tasks)│
│ ○ Concisa (5-8 agentes, 15-20 tasks)    │
│                                          │
│ Framework Alvo:                          │
│ ☑ CrewAI  ☑ LangChain  ☐ AutoGen       │
│                                          │
│ ☑ Gerar YAMLs automaticamente           │
│ ☑ Incluir metadata de rastreabilidade   │
│                                          │
└──────────────────────────────────────────┘
```

**O que o usuário faz:**
- Escolhe nível de detalhe (determina quantos agentes/tarefas gerar)
- Seleciona framework alvo (YAMLs adaptados ao framework)
- Define se quer YAMLs gerados automaticamente

---

### **Botão Principal**

```tsx
┌──────────────────────────────────────────┐
│                                          │
│   [🚀 GERAR AGENTES & TAREFAS]           │
│                                          │
│   Estimativa: ~2-3 minutos               │
│                                          │
└──────────────────────────────────────────┘
```

---

## 💬 COLUNA 2: CHAT & REFINAMENTO

```tsx
┌──────────────────────────────────────────────────────────┐
│ 💬 CHAT & REFINAMENTO                                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ [Sistema] 🤖 Iniciando geração de agentes e tarefas...   │
│                                                          │
│ [Sistema] 📊 Analisando especificação (14 seções)...     │
│                                                          │
│ [Sistema] ✅ 10 agentes gerados                          │
│                                                          │
│ [Sistema] ✅ 28 tarefas geradas                          │
│                                                          │
│ [Sistema] ✅ YAMLs criados (agents.yaml + tasks.yaml)    │
│                                                          │
│ [Sistema] 🎉 Geração concluída!                          │
│                                                          │
│ ┌────────────────────────────────────────────────────┐   │
│ │ Digite instruções para refinar...                  │   │
│ │                                                    │   │
│ │ Ex: "Adicionar agente para monitoramento"         │   │
│ │ Ex: "Remover agente de backup, não é necessário"  │   │
│ │ Ex: "Detalhar tarefa de autenticação"             │   │
│ │                                                    │   │
│ └────────────────────────────────────────────────────┘   │
│ [📤 Enviar] [📝 Sugerir Melhorias]                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**O que o usuário faz:**
- Vê mensagens de progresso durante geração
- Após conclusão: pode enviar mensagens para refinar agentes/tarefas
- Botão "Sugerir Melhorias": LLM analisa e sugere mudanças automaticamente

**Exemplos de refinamento:**
- "Dividir o agente de processamento em 2: um para validação, outro para transformação"
- "Adicionar tarefa de sincronização de dados entre agente A e B"
- "Remover agente de relatórios, não é necessário nesta fase"

---

## 📊 COLUNA 3: RESULTADOS

### **Card 1: Resumo de Agentes**

```tsx
┌──────────────────────────────────────────┐
│ 🤖 AGENTES GERADOS (10)                  │
├──────────────────────────────────────────┤
│                                          │
│ ┌────────────────────────────────────┐   │
│ │ 🔹 data_processor_agent            │   │
│ │    Processar e transformar dados   │   │
│ │    Tools: validator, transformer   │   │
│ └────────────────────────────────────┘   │
│                                          │
│ ┌────────────────────────────────────┐   │
│ │ 🔹 api_integration_agent           │   │
│ │    Integração com APIs externas    │   │
│ │    Tools: http_client, auth_mgr    │   │
│ └────────────────────────────────────┘   │
│                                          │
│ ... (mais 8 agentes)                     │
│                                          │
│ [📋 Ver Todos os Agentes]                │
│ [⚙️ Editar Agentes Individualmente]      │
│                                          │
└──────────────────────────────────────────┘
```

**O que o usuário faz:**
- Vê resumo dos agentes gerados
- Clica para ver lista completa
- Pode editar agentes individuais (abre modal)

---

### **Card 2: Resumo de Tarefas**

```tsx
┌──────────────────────────────────────────┐
│ 📋 TAREFAS GERADAS (28)                  │
├──────────────────────────────────────────┤
│                                          │
│ ┌────────────────────────────────────┐   │
│ │ ✓ validate_input_data              │   │
│ │   Agente: data_processor_agent     │   │
│ │   Dependências: nenhuma            │   │
│ └────────────────────────────────────┘   │
│                                          │
│ ┌────────────────────────────────────┐   │
│ │ ✓ transform_data                   │   │
│ │   Agente: data_processor_agent     │   │
│ │   Dependências: validate_input_data│   │
│ └────────────────────────────────────┘   │
│                                          │
│ ... (mais 26 tarefas)                    │
│                                          │
│ [🔀 Ver Grafo de Dependências]           │
│ [📋 Ver Todas as Tarefas]                │
│ [⚙️ Editar Tarefas Individualmente]      │
│                                          │
└──────────────────────────────────────────┘
```

**O que o usuário faz:**
- Vê resumo das tarefas
- Clica "Ver Grafo" para visualizar fluxo completo (vis.js ou react-flow)
- Edita tarefas individuais

---

### **Card 3: Preview de YAMLs**

```tsx
┌──────────────────────────────────────────┐
│ 📄 CONFIGURAÇÕES YAML                    │
├──────────────────────────────────────────┤
│                                          │
│ ☑ agents.yaml (1.2 KB) - VÁLIDO         │
│ ☑ tasks.yaml (3.5 KB) - VÁLIDO          │
│                                          │
│ ┌────────────────────────────────────┐   │
│ │ # agents.yaml                      │   │
│ │ data_processor_agent:              │   │
│ │   role: >                          │   │
│ │     Especialista em processamento  │   │
│ │   goal: >                          │   │
│ │     Validar e transformar dados... │   │
│ │ ...                                │   │
│ └────────────────────────────────────┘   │
│                                          │
│ [👁️ Visualizar agents.yaml Completo]     │
│ [👁️ Visualizar tasks.yaml Completo]      │
│ [💾 Baixar YAMLs (.zip)]                 │
│                                          │
└──────────────────────────────────────────┘
```

**O que o usuário faz:**
- Vê preview dos YAMLs gerados
- Clica para ver YAMLs completos em modal
- Baixa YAMLs para usar em projeto CrewAI

---

### **Card 4: Ações** (idêntico ao de Requisitos/Especificação)

```tsx
┌──────────────────────────────────────────┐
│ 🎬 AÇÕES                                 │
├──────────────────────────────────────────┤
│                                          │
│ [👁️ Visualizar]   [✏️ Editar]            │
│                                          │
│ [⏱️ Histórico]    [🔄 Comparar Versões]  │
│                                          │
│ [💾 Exportar]     [📊 Relatório]         │
│                                          │
│ [🔗 Rastreabilidade → Especificação]     │
│                                          │
│ ℹ️ v1.0 | Atualizado há 2 horas          │
│                                          │
└──────────────────────────────────────────┘
```

**O que o usuário faz:**
- **Visualizar**: Abre modal read-only com agentes + tarefas + YAMLs
- **Editar**: Abre editor para modificar agentes/tarefas manualmente
- **Histórico**: Lista versões anteriores (como em Requisitos)
- **Comparar**: Diff entre versões
- **Exportar**: Download de JSON, YAML, PDF (relatório)
- **Rastreabilidade**: Mostra quais seções da especificação geraram cada agente/tarefa

---

## 🎯 FLUXO COMPLETO DO USUÁRIO

### **Passo 1: Configuração Inicial**
1. Usuário entra na página "Agentes & Tarefas"
2. Seleciona especificação funcional (v2.0)
3. (Opcional) Adiciona documentos complementares (diagramas, arquitetura)
4. Escolhe estratégia de geração (Detalhada)
5. Seleciona frameworks alvo (CrewAI + LangChain)

### **Passo 2: Geração**
6. Clica "🚀 GERAR AGENTES & TAREFAS"
7. Sistema cria sessão no backend
8. Backend chama LLM com prompt unificado (especificação → agentes + tarefas)
9. Chat mostra progresso em tempo real:
   - "📊 Analisando Seção 2: Visão Geral do Sistema..."
   - "🤖 Identificando agentes necessários..."
   - "✅ 10 agentes gerados"
   - "📋 Gerando tarefas para cada agente..."
   - "✅ 28 tarefas geradas com dependências"
   - "📝 Criando agents.yaml..."
   - "📝 Criando tasks.yaml..."
   - "🎉 Geração concluída!"

### **Passo 3: Revisão dos Resultados**
10. Cards aparecem na Coluna 3:
    - **AgentsSummaryCard**: Mostra 10 agentes com preview
    - **TasksSummaryCard**: Mostra 28 tarefas com dependências
    - **YAMLPreviewCard**: Mostra YAMLs prontos
    - **ActionsCard**: Ações disponíveis
11. Usuário clica "📋 Ver Todos os Agentes" → Modal lista completa
12. Usuário clica "🔀 Ver Grafo de Dependências" → Visualização interativa de tasks

### **Passo 4: Refinamento via Chat**
13. Usuário digita no chat: "Adicionar agente para monitoramento de métricas"
14. Sistema envia para backend `/refine`
15. LLM processa e retorna:
    - Novo agente: `monitoring_agent`
    - Novas tarefas: `collect_metrics`, `analyze_metrics`
    - YAMLs atualizados
16. Chat mostra: "✅ Agente `monitoring_agent` adicionado com 2 novas tarefas"
17. Cards atualizam automaticamente

### **Passo 5: Edição Manual (se necessário)**
18. Usuário clica "⚙️ Editar Agentes Individualmente"
19. Modal abre lista de agentes editáveis
20. Usuário modifica `data_processor_agent`:
    - Altera goal: "Processar até 10,000 registros/segundo"
    - Adiciona tool: `batch_processor`
21. Salva → Agente atualizado + YAML regerado

### **Passo 6: Exportação**
22. Usuário clica "💾 Exportar"
23. Opções:
    - **📦 YAMLs (.zip)**: agents.yaml + tasks.yaml
    - **📄 JSON**: Estrutura completa de agentes + tarefas
    - **📊 PDF**: Relatório com todos os agentes, tarefas, grafo de dependências
    - **🔗 Link de Rastreabilidade**: Planilha Excel vinculando cada agente/tarefa à seção da especificação

### **Passo 7: Próxima Fase**
24. Usuário clica botão "➡️ Próxima Fase: Redes de Petri"
25. Sistema leva para próxima página (PetriNetPage) com agentes + tarefas carregados

---

## 🎨 DIFERENCIAIS CRIATIVOS

### 1. **Grafo Interativo de Tarefas**
- Biblioteca: `react-flow` ou `vis.js`
- Mostra tasks como nós, dependências como setas
- Cores diferentes para agentes
- Clique no nó → detalhes da task
- Drag & drop para reorganizar visualmente

### 2. **Sugestões Inteligentes** (Botão "📝 Sugerir Melhorias")
- LLM analisa agentes + tarefas gerados
- Identifica:
  - Agentes redundantes
  - Tarefas órfãs (sem agente)
  - Dependências circulares
  - Gaps de cobertura (requisitos sem agente/task)
- Retorna sugestões acionáveis

### 3. **Matriz de Rastreabilidade** (Botão no ActionsCard)
- Tabela mostrando:
  - Coluna 1: Requisito da especificação (RF-001, UC-005)
  - Coluna 2: Agentes relacionados
  - Coluna 3: Tarefas relacionadas
- Exportável para Excel

### 4. **Preview YAML em Tempo Real**
- À medida que usuário refina no chat, YAML atualiza em tempo real
- Highlight de mudanças (diff verde/vermelho)

### 5. **Templates de Refinamento**
- Botões rápidos no chat:
  - "➕ Adicionar agente de..."
  - "🔄 Dividir agente X em 2"
  - "🔗 Criar task que conecta agente A e B"
  - "🗑️ Remover agente Y"

---

## 📁 ARQUIVOS A CRIAR

### Backend:
1. `backend/app/routers/agent_task_generation.py` - Endpoint unificado
2. `backend/prompts/agent_task_generation.py` - Prompt template
3. `backend/database/migrations/create_agent_task_sessions.sql` - Novas tabelas
4. `backend/services/agent_task_service.py` - Lógica de negócio

### Frontend:
5. `src/pages/AgentTaskPage.tsx` - Página principal
6. `src/pages/AgentTaskPage.css` - Estilos
7. `src/components/agenttask/AgentsSummaryCard.tsx`
8. `src/components/agenttask/TasksSummaryCard.tsx`
9. `src/components/agenttask/YAMLPreviewCard.tsx`
10. `src/components/agenttask/TaskDependencyGraph.tsx` - Grafo vis.js
11. `src/components/agenttask/AgentTaskChatInterface.tsx` - Chat refinamento
12. `src/components/agenttask/TraceabilityMatrixModal.tsx`
13. `src/components/agenttask/AgentListModal.tsx` - Lista completa de agentes
14. `src/components/agenttask/TaskListModal.tsx` - Lista completa de tarefas
15. `src/services/agentTaskService.ts` - Service único

---

## 🔧 TECNOLOGIAS

### Backend:
- **FastAPI** - Routers e endpoints
- **MySQL** - Armazenamento de agentes, tarefas, YAMLs, sessões
- **LLM (DeepSeek/OpenAI)** - Geração de agentes + tarefas
- **YAML** - Serialização de configurações CrewAI

### Frontend:
- **React 19 + TypeScript**
- **react-flow** ou **vis.js** - Grafo de dependências
- **Markdown** - Visualização de YAMLs
- **React Router** - Navegação
- **Toast** - Notificações

---

## ⚡ DIFERENCIAIS vs. Páginas Anteriores

| Recurso | Requisitos | Especificação | **Agentes & Tarefas** |
|---------|------------|---------------|------------------------|
| Seleção de fonte | ✅ Documentos | ✅ Requisitos | ✅ Especificação |
| Upload complementar | ✅ | ✅ | ✅ |
| Chat refinamento | ✅ | ✅ | ✅ |
| Preview resultado | ✅ Markdown | ✅ Markdown | ✅ YAML + JSON |
| Histórico/Versões | ✅ | ✅ | ✅ |
| **Grafo interativo** | ❌ | ❌ | ✅ **NOVO** |
| **Matriz rastreabilidade** | ❌ | ❌ | ✅ **NOVO** |
| **Sugestões IA** | ❌ | ✅ (Review) | ✅ **NOVO** |
| **Export YAML** | ❌ | ❌ | ✅ **NOVO** |

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Backend (2-3 dias)
- [ ] Criar migration `create_agent_task_sessions.sql`
- [ ] Criar `backend/prompts/agent_task_generation.py` com prompt unificado
- [ ] Criar `backend/app/routers/agent_task_generation.py` com endpoints:
  - `POST /generate` - Gera agentes + tarefas
  - `POST /refine` - Refina via chat
  - `GET /status` - Status da sessão
  - `GET /chat-history` - Histórico do chat
  - `GET /export` - Exporta YAMLs
- [ ] Testar geração end-to-end

### Fase 2: Frontend - Estrutura (2 dias)
- [ ] Criar `src/pages/AgentTaskPage.tsx` com layout 3 colunas
- [ ] Criar `src/pages/AgentTaskPage.css`
- [ ] Criar `src/services/agentTaskService.ts`
- [ ] Integrar com roteamento

### Fase 3: Frontend - Cards Coluna 1 (1 dia)
- [ ] Card de seleção de especificação
- [ ] Card de upload de documentos complementares
- [ ] Card de configurações
- [ ] Botão de geração

### Fase 4: Frontend - Chat Coluna 2 (1 dia)
- [ ] Componente de chat com polling
- [ ] Templates de refinamento
- [ ] Botão "Sugerir Melhorias"

### Fase 5: Frontend - Cards Coluna 3 (2 dias)
- [ ] `AgentsSummaryCard.tsx`
- [ ] `TasksSummaryCard.tsx`
- [ ] `YAMLPreviewCard.tsx`
- [ ] `ActionsCard.tsx` (com todos os botões)

### Fase 6: Frontend - Modais (2 dias)
- [ ] `AgentListModal.tsx` - Lista completa editável
- [ ] `TaskListModal.tsx` - Lista completa editável
- [ ] `TaskDependencyGraph.tsx` - Grafo interativo (react-flow)
- [ ] `TraceabilityMatrixModal.tsx` - Matriz requisitos → agentes → tarefas

### Fase 7: Testes & Polimento (1 dia)
- [ ] Testar fluxo completo
- [ ] Testar refinamento via chat
- [ ] Testar export de YAMLs
- [ ] Ajustes de UX

**Total estimado: 11-12 dias de desenvolvimento**

---

## 🚀 PRÓXIMOS PASSOS APÓS IMPLEMENTAÇÃO

Após implementar esta página, o usuário terá:

1. ✅ **Agentes definidos** (salvos em DB + YAML)
2. ✅ **Tarefas definidas** (salvos em DB + YAML)
3. ✅ **YAMLs prontos** para CrewAI
4. ➡️ **Próxima fase**: Redes de Petri (conversão de tarefas → Petri Net)
5. ➡️ **Depois**: Geração de código Python executável

---

Essa interface unifica a geração de agentes + tarefas seguindo o mesmo padrão visual das páginas anteriores (Requisitos/Especificação), mas adiciona recursos únicos como grafo interativo de dependências, matriz de rastreabilidade e export direto de YAMLs para uso em projetos CrewAI.
