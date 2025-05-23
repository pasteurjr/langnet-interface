// src/pages/AgentsPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Agent, AgentStatus } from '../types';
import AgentCard from '../components/agents/AgentCard';
import AgentFormModal from '../components/agents/AgentFormModal';
import AgentSpecifierModal from '../components/agents/AgentSpecifierModal';
import './AgentsPage.css';

const AgentsPage: React.FC = () => {
  const { projectId } = useParams();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isSpecifierModalOpen, setIsSpecifierModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<AgentStatus | 'all'>('all');

  // Dados de exemplo - substituir por API real
  useEffect(() => {
    // Simular carregamento de agentes
    const mockAgents: Agent[] = [
      {
        id: 'agent_1',
        name: 'customer_service_agent',
        role: 'ESpecialista em atendimento ao cliente responsável por lidar com consultas',
        goal: 'Entender as necessidades do cliente e fornecer soluções apropriadas',
        backstory: 'Você tem 5 anos de experiência em atendimento ao cliente e profundo conhecimento dos produtos e políticas da empresa',
        tools: ['knowledge_base_tool', 'ticket_creation_tool', 'customer_history_tool'],
        verbose: true,
        allow_delegation: false,
        allow_code_execution: false,
        max_iter: 25,
        max_rpm: 15,
        status: AgentStatus.ACTIVE,
        createdAt: '2025-05-20T10:00:00Z',
        updatedAt: '2025-05-20T14:30:00Z'
      },
      {
        id: 'agent_2',
        name: 'technical_support_agent',
        role: 'Especialista em suporte técnico para questões complexas',
        goal: 'Resolver problemas técnicos e fornecer soluções eficazes',
        backstory: 'Engenheiro com vasta experiência em troubleshooting e resolução de problemas complexos',
        tools: ['diagnostic_tool', 'remote_access_tool', 'knowledge_base_tool'],
        verbose: true,
        allow_delegation: true,
        allow_code_execution: true,
        max_iter: 30,
        max_rpm: 10,
        status: AgentStatus.ACTIVE,
        createdAt: '2025-05-19T09:00:00Z',
        updatedAt: '2025-05-20T11:00:00Z'
      }
    ];
    setAgents(mockAgents);
  }, [projectId]);

  const handleCreateAgent = () => {
    setSelectedAgent(null);
    setIsFormModalOpen(true);
  };

  const handleEditAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setIsFormModalOpen(true);
  };

  const handleDeleteAgent = (agentId: string) => {
    if (window.confirm('Tem certeza que deseja excluir este agente?')) {
      setAgents(agents.filter(agent => agent.id !== agentId));
    }
  };

  const handleSaveAgent = (agentData: Partial<Agent>) => {
    if (selectedAgent) {
      // Editar agente existente
      setAgents(agents.map(agent => 
        agent.id === selectedAgent.id 
          ? { ...agent, ...agentData, updatedAt: new Date().toISOString() }
          : agent
      ));
    } else {
      // Criar novo agente
      const newAgent: Agent = {
        ...agentData as Agent,
        id: `agent_${Date.now()}`,
        status: AgentStatus.DRAFT,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      setAgents([...agents, newAgent]);
    }
    setIsFormModalOpen(false);
  };

  const handleSpecifierResult = (specifiedAgents: Partial<Agent>[]) => {
    // Adicionar agentes especificados
    const newAgents = specifiedAgents.map((agentData, index) => ({
      ...agentData as Agent,
      id: `agent_${Date.now()}_${index}`,
      status: AgentStatus.DRAFT,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }));
    setAgents([...agents, ...newAgents]);
    setIsSpecifierModalOpen(false);
  };

  const handleToggleStatus = (agentId: string) => {
    setAgents(agents.map(agent => 
      agent.id === agentId 
        ? { 
            ...agent, 
            status: agent.status === AgentStatus.ACTIVE 
              ? AgentStatus.INACTIVE 
              : AgentStatus.ACTIVE,
            updatedAt: new Date().toISOString()
          }
        : agent
    ));
  };

  const handleExportYAML = () => {
    const yamlContent = generateYAML(agents);
    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'agents.yaml';
    a.click();
    URL.revokeObjectURL(url);
  };

  const generateYAML = (agentsList: Agent[]): string => {
    let yaml = '# agents.yaml - Generated from LangNet\n\n';
    
    agentsList.forEach(agent => {
      yaml += `${agent.name}:\n`;
      yaml += `  role: >\n    ${agent.role}\n`;
      yaml += `  goal: >\n    ${agent.goal}\n`;
      yaml += `  backstory: >\n    ${agent.backstory}\n`;
      yaml += `  tools:\n`;
      agent.tools.forEach(tool => {
        yaml += `    - ${tool}\n`;
      });
      yaml += `  verbose: ${agent.verbose}\n`;
      yaml += `  allow_delegation: ${agent.allow_delegation}\n`;
      if (agent.allow_code_execution !== undefined) {
        yaml += `  allow_code_execution: ${agent.allow_code_execution}\n`;
      }
      if (agent.max_iter !== undefined) {
        yaml += `  max_iter: ${agent.max_iter}\n`;
      }
      if (agent.max_rpm !== undefined) {
        yaml += `  max_rpm: ${agent.max_rpm}\n`;
      }
      yaml += '\n';
    });
    
    return yaml;
  };

  // Filtrar agentes
  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.role.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || agent.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="agents-page">
      <div className="page-header">
        <div className="header-left">
          <h1>Agentes</h1>
          <span className="agent-count">{filteredAgents.length} agentes</span>
        </div>
        <div className="header-actions">
          <button 
            className="btn-specifier"
            onClick={() => setIsSpecifierModalOpen(true)}
          >
            🤖 Especificador de Agentes
          </button>
          <button className="btn-primary" onClick={handleCreateAgent}>
            + Novo Agente
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
            placeholder="Buscar agentes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="status-filter">
          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value as AgentStatus | 'all')}
          >
            <option value="all">Todos os Status</option>
            <option value={AgentStatus.ACTIVE}>Ativo</option>
            <option value={AgentStatus.INACTIVE}>Inativo</option>
            <option value={AgentStatus.DRAFT}>Rascunho</option>
          </select>
        </div>
      </div>

      <div className="agents-grid">
        {filteredAgents.map(agent => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onEdit={handleEditAgent}
            onDelete={handleDeleteAgent}
            onToggleStatus={handleToggleStatus}
          />
        ))}
      </div>

      {filteredAgents.length === 0 && (
        <div className="empty-state">
          <p>Nenhum agente encontrado</p>
          <button className="btn-primary" onClick={handleCreateAgent}>
            Criar Primeiro Agente
          </button>
        </div>
      )}

      <AgentFormModal
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        onSave={handleSaveAgent}
        agent={selectedAgent}
      />

      <AgentSpecifierModal
        isOpen={isSpecifierModalOpen}
        onClose={() => setIsSpecifierModalOpen(false)}
        onSpecify={handleSpecifierResult}
        projectId={projectId || ''}
      />
    </div>
  );
};

export default AgentsPage;