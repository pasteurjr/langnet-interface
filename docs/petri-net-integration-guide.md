# 🎯 Guia de Integração do Editor de Redes de Petri

**Data**: 13/06/2025  
**Status**: Editor pronto para integração no sistema LangNet

## 🚀 Situação Atual

✅ **Editor de Redes de Petri está PRONTO**
- Editor visual completo com drag-and-drop
- Validação matemática (deadlock detection, reachability analysis)
- Engine de simulação com animação de tokens
- Capacidades de integração com agentes/tarefas

❌ **Integração com LangNet Interface pendente**
- Arquivo atual `src/pages/PetriNetPage.tsx` é apenas placeholder
- Necessária integração com design system e fluxo de dados

## 📋 Checklist de Integração

### 1. 🎨 Interface e Design System
- [ ] **Substituir placeholder** - `src/pages/PetriNetPage.tsx`
- [ ] **Aplicar tema LangNet** - CSS variables e design tokens
- [ ] **Header consistente** - Título, breadcrumbs, ações
- [ ] **Sidebar navigation** - Integrar com menu lateral existente
- [ ] **Responsive design** - Mobile/tablet compatibility
- [ ] **Loading states** - Skeleton loaders para dados pesados

### 2. 🔗 Integração de Dados
- [ ] **Project context** - `useParams<{ projectId: string }>()`
- [ ] **Agents integration** - Conectar com dados de `AgentsPage`
- [ ] **Tasks integration** - Conectar com dados de `TasksPage`
- [ ] **State management** - Usar Context API existente
- [ ] **Data persistence** - LocalStorage/API integration
- [ ] **Real-time sync** - WebSocket quando disponível

### 3. 🛠️ Funcionalidades Core
- [ ] **Petri Net CRUD** - Create, Read, Update, Delete redes
- [ ] **Agent mapping** - Vincular transições a agentes específicos
- [ ] **Task mapping** - Vincular places/transitions a tarefas
- [ ] **Simulation controls** - Play/pause/step/reset
- [ ] **Validation feedback** - Alertas visuais para problemas
- [ ] **Export/Import** - JSON, PNML, imagem

### 4. 🔄 Fluxo de Trabalho
- [ ] **From Specification** - Gerar rede a partir de especificação
- [ ] **From Agents/Tasks** - Auto-sugerir estrutura da rede
- [ ] **To YAML** - Exportar para geração de código
- [ ] **To Code** - Integrar com `CodePage` generation
- [ ] **Validation pipeline** - Verificar antes de gerar código
- [ ] **Version control** - Histórico de alterações

### 5. 📊 Monitoramento e Debug
- [ ] **Runtime state** - Mostrar estado atual da execução
- [ ] **Performance metrics** - Tempo de execução, throughput
- [ ] **Debug mode** - Inspeção detalhada de tokens
- [ ] **Logs integration** - Conectar com `MonitoringPage`
- [ ] **Alert system** - Notificar problemas de performance
- [ ] **Analytics** - Métricas de uso do editor

## 🎯 Estrutura de Arquivo Recomendada

```typescript
// src/pages/PetriNetPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import PetriNetEditor from '../components/petri-net/PetriNetEditor';
import { Agent, Task, PetriNet } from '../types';

const PetriNetPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [currentNet, setCurrentNet] = useState<PetriNet | null>(null);
  
  // Integration logic here...
  
  return (
    <div className="petri-net-page">
      <div className="page-header">
        <h1>🔗 Editor de Redes de Petri</h1>
        {/* Header controls */}
      </div>
      
      <div className="page-content">
        <PetriNetEditor 
          projectId={projectId}
          agents={agents}
          tasks={tasks}
          currentNet={currentNet}
          onNetChange={setCurrentNet}
          // ... other props
        />
      </div>
    </div>
  );
};
```

## 🎨 Design System Integration

### Cores e Temas
```css
/* Usar variáveis CSS existentes do LangNet */
.petri-net-editor {
  --primary-color: var(--langnet-primary);
  --secondary-color: var(--langnet-secondary);
  --background-color: var(--langnet-background);
  --text-color: var(--langnet-text);
  --border-radius: var(--langnet-border-radius);
}
```

### Componentes Consistentes
- **Toolbar** - Mesmo estilo de `AgentDesignerPage`
- **Property Panel** - Sidebar similar a outras páginas
- **Modal Dialogs** - Usar componentes existentes
- **Buttons** - Classes CSS padronizadas
- **Form Controls** - Inputs consistentes

## 🔌 Pontos de Integração

### 1. Navigation Context
```typescript
// Integrar com NavigationContext existente
const navigation = useNavigation();
navigation.setCurrentPage('petri-net');
```

### 2. Agents Integration
```typescript
// Buscar agentes do projeto atual
const agents = useAgents(projectId);
const tasks = useTasks(projectId);
```

### 3. Export to YAML
```typescript
// Conectar com YamlPage para geração
const exportToYaml = (petriNet: PetriNet) => {
  const yamlConfig = generateYamlFromPetriNet(petriNet);
  // Integrar com YamlPage...
};
```

## 🚨 Pontos de Atenção

### Performance
- **Large networks** - Virtualização para redes grandes
- **Real-time simulation** - RequestAnimationFrame para animações
- **Memory management** - Cleanup de listeners e observers

### Accessibility
- **Keyboard navigation** - Acessível via teclado
- **Screen readers** - ARIA labels apropriados
- **Color contrast** - Seguir padrões WCAG AA
- **Focus management** - Indicadores visuais claros

### Mobile/Responsive
- **Touch gestures** - Pan, zoom, select em mobile
- **Viewport adaptation** - Layout responsivo
- **Performance** - Otimizações para dispositivos móveis

## 📅 Timeline de Integração

### Semana 1
- ✅ Substituir placeholder `PetriNetPage.tsx`
- ✅ Integração básica com project context
- ✅ Aplicar design system LangNet

### Semana 2  
- ✅ Conectar dados de agents/tasks
- ✅ Implementar CRUD de redes
- ✅ Export/import básico

### Semana 3 (opcional)
- ✅ Simulação em tempo real
- ✅ Integração com monitoring
- ✅ Otimizações de performance

## 🎯 Success Criteria

**MVP Integration (Semana 1):**
- [ ] Editor funcionando dentro da interface LangNet
- [ ] Visual consistency com outras páginas
- [ ] Navegação integrada
- [ ] Dados básicos de projeto carregando

**Full Integration (Semana 2):**
- [ ] Agents/tasks mappings funcionando
- [ ] Export para YAML operacional
- [ ] Validações matemáticas ativas
- [ ] Simulação básica funcionando

**Production Ready (Semana 3):**
- [ ] Performance otimizada
- [ ] Acessibilidade completa
- [ ] Mobile responsive
- [ ] Monitoring integrado

---

**💡 Próximos Passos:**
1. Analisar estrutura do Editor de Redes de Petri existente
2. Planejar pontos de integração com LangNet
3. Implementar substituição do placeholder
4. Testar fluxo completo end-to-end