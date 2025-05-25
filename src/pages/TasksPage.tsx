// src/pages/TasksPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Task, TaskStatus, Agent, AgentStatus } from '../types';
import TaskCard from '../components/tasks/TaskCard';
import TaskFormModal from '../components/tasks/TaskFormModal';
import TaskSpecifierModal from '../components/tasks/TaskSpecifierModal';
import './TasksPage.css';

const TasksPage: React.FC = () => {
  const { projectId } = useParams();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isSpecifierModalOpen, setIsSpecifierModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<TaskStatus | 'all'>('all');
  const [filterAgent, setFilterAgent] = useState<string>('all');

  // Carregar dados de exemplo
  useEffect(() => {
    // Simular carregamento de agentes
    const mockAgents: Agent[] = [
      {
        id: 'agent_1',
        name: 'customer_service_agent',
        role: 'Especialista em atendimento ao cliente',
        goal: 'Entender e resolver consultas de clientes',
        backstory: 'Experiente em atendimento ao cliente',
        tools: ['knowledge_base_tool', 'ticket_creation_tool'],
        verbose: true,
        allow_delegation: false,
        status: AgentStatus.ACTIVE,
        createdAt: '2025-05-20T10:00:00Z',
        updatedAt: '2025-05-20T14:30:00Z'
      },
      {
        id: 'agent_2',
        name: 'technical_support_agent',
        role: 'Especialista em suporte técnico',
        goal: 'Resolver problemas técnicos',
        backstory: 'Engenheiro experiente',
        tools: ['diagnostic_tool', 'remote_access_tool'],
        verbose: true,
        allow_delegation: true,
        status: AgentStatus.ACTIVE,
        createdAt: '2025-05-19T09:00:00Z',
        updatedAt: '2025-05-20T11:00:00Z'
      }
    ];
    setAgents(mockAgents);

    // Simular carregamento de tarefas
    const mockTasks: Task[] = [
      {
        id: 'task_1',
        projectId: projectId || 'default_project',
        name: 'process_customer_query_task',
        description: 'Analisar e processar consulta de cliente identificando a natureza e urgência',
        expected_output: 'Classificação estruturada da consulta com prioridade e roteamento adequado',
        agentId: 'agent_1',
        agent: 'agent_1', // Alias para compatibilidade
        context: [],
        tools: ['TextAnalysisTool', 'ClassificationModel'],
        human_input: false,
        async_execution: false,
        output_json: undefined,
        output_file: undefined,
        inputs: [
          {
            name: 'customer_query',
            type: 'string',
            description: 'Consulta do cliente em texto livre'
          },
          {
            name: 'customer_data',
            type: 'object',
            description: 'Dados básicos do cliente'
          }
        ],
        outputs: [
          {
            name: 'classification',
            type: 'object',
            description: 'Classificação estruturada da consulta'
          },
          {
            name: 'priority',
            type: 'number',
            description: 'Nível de prioridade (1-5)'
          }
        ],
        steps: [
          {
            id: 'step_1',
            description: 'Extrair texto da consulta',
            order: 1
          },
          {
            id: 'step_2',
            description: 'Classificar tipo de consulta',
            order: 2
          },
          {
            id: 'step_3',
            description: 'Determinar prioridade',
            order: 3
          }
        ],
        status: TaskStatus.ACTIVE,
        createdAt: '2025-05-20T10:00:00Z',
        updatedAt: '2025-05-20T14:30:00Z'
      },
      {
        id: 'task_2',
        projectId: projectId || 'default_project',
        name: 'analyze_sentiment_task',
        description: 'Analisar o sentimento da mensagem do cliente para determinar o nível de satisfação',
        expected_output: 'Score de sentimento com análise detalhada e recomendações de ação',
        agentId: 'agent_1',
        agent: 'agent_1', // Alias para compatibilidade
        context: ['task_1'],
        tools: ['SentimentAnalyzer', 'EmotionDetector'],
        human_input: false,
        async_execution: true,
        output_json: '{ "sentiment": "string", "score": "number", "emotions": "array" }',
        output_file: 'sentiment_analysis.json',
        inputs: [
          {
            name: 'processed_query',
            type: 'object',
            description: 'Consulta processada da tarefa anterior'
          }
        ],
        outputs: [
          {
            name: 'sentiment_score',
            type: 'number',
            description: 'Score do sentimento (-1 a 1)'
          },
          {
            name: 'emotions',
            type: 'array',
            description: 'Lista de emoções detectadas'
          },
          {
            name: 'recommendations',
            type: 'array',
            description: 'Recomendações de ação'
          }
        ],
        steps: [
          {
            id: 'step_1',
            description: 'Preprocessar texto',
            order: 1
          },
          {
            id: 'step_2',
            description: 'Analisar sentimento',
            order: 2
          },
          {
            id: 'step_3',
            description: 'Detectar emoções',
            order: 3
          },
          {
            id: 'step_4',
            description: 'Gerar recomendações',
            order: 4
          }
        ],
        status: TaskStatus.ACTIVE,
        createdAt: '2025-05-20T11:00:00Z',
        updatedAt: '2025-05-20T15:00:00Z'
      }
    ];
    setTasks(mockTasks);
  }, [projectId]);

  const handleCreateTask = () => {
    setSelectedTask(null);
    setIsFormModalOpen(true);
  };

  const handleEditTask = (task: Task) => {
    setSelectedTask(task);
    setIsFormModalOpen(true);
  };

  const handleDeleteTask = (taskId: string) => {
    if (window.confirm('Tem certeza que deseja excluir esta tarefa?')) {
      setTasks(tasks.filter(task => task.id !== taskId));
    }
  };

  const handleSaveTask = (taskData: Partial<Task>) => {
    if (selectedTask) {
      // Editar tarefa existente
      setTasks(tasks.map(task => 
        task.id === selectedTask.id 
          ? { ...task, ...taskData, updatedAt: new Date().toISOString() }
          : task
      ));
    } else {
      // Criar nova tarefa - CORRIGIDO
      const newTask: Task = {
        ...taskData as Task, // Primeiro espalha os dados da tarefa
        id: `task_${Date.now()}`, // Sobrescreve o ID
        projectId: projectId || 'default_project', // Sobrescreve o projectId
        agentId: taskData.agent || '', // Sobrescreve o agentId
        agent: taskData.agent || '', // Sobrescreve o agent
        inputs: taskData.inputs || [], // Usa os inputs fornecidos ou array vazio
        outputs: taskData.outputs || [], // Usa os outputs fornecidos ou array vazio
        steps: taskData.steps || [], // Usa os steps fornecidos ou array vazio
        status: TaskStatus.DRAFT, // Força status como DRAFT
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      setTasks([...tasks, newTask]);
    }
    setIsFormModalOpen(false);
  };
  
  const handleSpecifierResult = (specifiedTasks: Partial<Task>[]) => {
    // Adicionar tarefas especificadas - CORRIGIDO
    const newTasks = specifiedTasks.map((taskData, index) => ({
      ...taskData as Task, // Primeiro espalha os dados da tarefa
      id: `task_${Date.now()}_${index}`, // Sobrescreve o ID
      projectId: projectId || 'default_project', // Sobrescreve o projectId
      agentId: taskData.agent || '', // Sobrescreve o agentId
      agent: taskData.agent || '', // Sobrescreve o agent
      inputs: taskData.inputs || [], // Usa os inputs fornecidos ou array vazio
      outputs: taskData.outputs || [], // Usa os outputs fornecidos ou array vazio
      steps: taskData.steps || [], // Usa os steps fornecidos ou array vazio
      status: TaskStatus.DRAFT, // Força status como DRAFT
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }));
    setTasks([...tasks, ...newTasks]);
    setIsSpecifierModalOpen(false);
  };
  const handleToggleStatus = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { 
            ...task, 
            status: task.status === TaskStatus.ACTIVE 
              ? TaskStatus.INACTIVE 
              : TaskStatus.ACTIVE,
            updatedAt: new Date().toISOString()
          }
        : task
    ));
  };

  const handleDuplicateTask = (taskId: string) => {
    const taskToDuplicate = tasks.find(t => t.id === taskId);
    if (taskToDuplicate) {
      const newTask: Task = {
        ...taskToDuplicate,
        id: `task_${Date.now()}`,
        name: `${taskToDuplicate.name}_copy`,
        status: TaskStatus.DRAFT,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      setTasks([...tasks, newTask]);
    }
  };

  const handleExportYAML = () => {
    const yamlContent = generateYAML(tasks);
    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'tasks.yaml';
    a.click();
    URL.revokeObjectURL(url);
  };

  const generateYAML = (tasksList: Task[]): string => {
    let yaml = '# tasks.yaml - Generated from LangNet\n\n';
    
    tasksList.forEach(task => {
      const agent = agents.find(a => a.id === task.agent);
      
      yaml += `${task.name}:\n`;
      yaml += `  description: >\n    ${task.description}\n`;
      yaml += `  expected_output: >\n    ${task.expected_output}\n`;
      yaml += `  agent: ${agent?.name || task.agent}\n`;
      
      if (task.context && task.context.length > 0) {
        yaml += `  context:\n`;
        task.context.forEach(contextId => {
          const contextTask = tasks.find(t => t.id === contextId);
          yaml += `    - ${contextTask?.name || contextId}\n`;
        });
      }
      
      if (task.tools && task.tools.length > 0) {
        yaml += `  tools:\n`;
        task.tools.forEach(tool => {
          yaml += `    - ${tool}\n`;
        });
      }
      
      yaml += `  human_input: ${task.human_input}\n`;
      yaml += `  async_execution: ${task.async_execution}\n`;
      
      if (task.output_json) {
        yaml += `  output_json: ${task.output_json}\n`;
      }
      
      if (task.output_file) {
        yaml += `  output_file: ${task.output_file}\n`;
      }
      
      yaml += '\n';
    });
    
    return yaml;
  };

  // Filtrar tarefas
  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || task.status === filterStatus;
    const matchesAgent = filterAgent === 'all' || task.agent === filterAgent;
    return matchesSearch && matchesStatus && matchesAgent;
  });

  return (
    <div className="tasks-page">
      <div className="page-header">
        <div className="header-left">
          <h1>Tarefas</h1>
          <span className="task-count">{filteredTasks.length} tarefas</span>
        </div>
        <div className="header-actions">
          <button 
            className="btn-specifier"
            onClick={() => setIsSpecifierModalOpen(true)}
          >
            📋 Especificador de Tarefas
          </button>
          <button className="btn-primary" onClick={handleCreateTask}>
            + Nova Tarefa
          </button>
          <button className="btn-secondary" onClick={handleExportYAML}>
            📥 Exportar YAML
          </button>
        </div>
      </div>

      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar tarefas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="filter-controls">
          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value as TaskStatus | 'all')}
          >
            <option value="all">Todos os Status</option>
            <option value={TaskStatus.ACTIVE}>Ativo</option>
            <option value={TaskStatus.INACTIVE}>Inativo</option>
            <option value={TaskStatus.DRAFT}>Rascunho</option>
          </select>
          
          <select 
            value={filterAgent} 
            onChange={(e) => setFilterAgent(e.target.value)}
          >
            <option value="all">Todos os Agentes</option>
            {agents.map(agent => (
              <option key={agent.id} value={agent.id}>{agent.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="tasks-grid">
        {filteredTasks.map(task => (
          <TaskCard
            key={task.id}
            task={task}
            agent={agents.find(a => a.id === task.agent)}
            allTasks={tasks}
            onEdit={handleEditTask}
            onDelete={handleDeleteTask}
            onToggleStatus={handleToggleStatus}
            onDuplicate={handleDuplicateTask}
          />
        ))}
      </div>

      {filteredTasks.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma tarefa encontrada</p>
          <button className="btn-primary" onClick={handleCreateTask}>
            Criar Primeira Tarefa
          </button>
        </div>
      )}

      <TaskFormModal
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        onSave={handleSaveTask}
        task={selectedTask}
        agents={agents}
        tasks={tasks}
      />

      <TaskSpecifierModal
        isOpen={isSpecifierModalOpen}
        onClose={() => setIsSpecifierModalOpen(false)}
        onSpecify={handleSpecifierResult}
        agents={agents}
        projectId={projectId || ''}
      />
    </div>
  );
};

export default TasksPage;