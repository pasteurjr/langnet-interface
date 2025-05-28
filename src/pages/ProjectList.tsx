// src/pages/ProjectList.tsx (IMPLEMENTAÇÃO COMPLETA)
import React, { useState } from 'react';
import { Project, ProjectStatus } from '../types';
import { useNavigation } from '../contexts/NavigationContext';
import CreateProjectModal from '../components/projects/CreateProjectModal';
import ProjectCreationButton from '../components/projects/ProjectCreationButton';
import './ProjectList.css';

const ProjectList: React.FC = () => {
  const { enterProjectContext } = useNavigation();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [domainFilter, setDomainFilter] = useState<string>('all');

  // Dados de exemplo expandidos para a lista de projetos
  const allProjects: Project[] = [
    {
      id: '1',
      name: 'Assistente de Atendimento ao Cliente',
      description: 'Sistema de agentes para automatizar atendimento ao cliente com integração a múltiplos canais de comunicação.',
      domain: 'Atendimento',
      createdAt: '2025-05-15T10:00:00Z',
      updatedAt: '2025-05-20T14:30:00Z',
      status: ProjectStatus.IN_PROGRESS,
      progress: 65
    },
    {
      id: '2',
      name: 'Análise de Documentos Jurídicos',
      description: 'Fluxo de agentes para extração e análise de informações de contratos e documentos legais.',
      domain: 'Jurídico',
      createdAt: '2025-05-10T08:15:00Z',
      updatedAt: '2025-05-19T16:45:00Z',
      status: ProjectStatus.DRAFT,
      progress: 30
    },
    {
      id: '3',
      name: 'Assistente de Pesquisa Acadêmica',
      description: 'Sistema para auxiliar pesquisadores na análise de artigos científicos e geração de insights.',
      domain: 'Educação',
      createdAt: '2025-04-28T09:20:00Z',
      updatedAt: '2025-05-18T11:10:00Z',
      status: ProjectStatus.COMPLETED,
      progress: 100
    },
    {
      id: '4',
      name: 'Sistema de Análise Financeira',
      description: 'Agentes especializados em análise de relatórios financeiros e geração de projeções automáticas.',
      domain: 'Finanças',
      createdAt: '2025-05-01T14:20:00Z',
      updatedAt: '2025-05-15T09:15:00Z',
      status: ProjectStatus.IN_PROGRESS,
      progress: 45
    },
    {
      id: '5',
      name: 'Chatbot Médico Especializado',
      description: 'Sistema de triagem médica inicial com agentes especializados em diferentes áreas da saúde.',
      domain: 'Saúde',
      createdAt: '2025-04-20T11:30:00Z',
      updatedAt: '2025-05-12T16:20:00Z',
      status: ProjectStatus.IN_PROGRESS,
      progress: 78
    },
    {
      id: '6',
      name: 'Gerador de Conteúdo Marketing',
      description: 'Conjunto de agentes para criação automatizada de conteúdo para redes sociais e campanhas.',
      domain: 'Marketing',
      createdAt: '2025-04-15T08:45:00Z',
      updatedAt: '2025-04-25T12:10:00Z',
      status: ProjectStatus.ARCHIVED,
      progress: 85
    },
    {
      id: '7',
      name: 'Assistente de RH Inteligente',
      description: 'Sistema para automação de processos de recrutamento e avaliação de candidatos.',
      domain: 'Recursos Humanos',
      createdAt: '2025-05-18T10:00:00Z',
      updatedAt: '2025-05-20T15:30:00Z',
      status: ProjectStatus.DRAFT,
      progress: 15
    },
    {
      id: '8',
      name: 'Monitor de Compliance Automatizado',
      description: 'Agentes para monitoramento contínuo de compliance e geração de relatórios de auditoria.',
      domain: 'Compliance',
      createdAt: '2025-05-05T13:15:00Z',
      updatedAt: '2025-05-19T11:45:00Z',
      status: ProjectStatus.COMPLETED,
      progress: 100
    }
  ];

  // Filtros únicos baseados nos dados
  const uniqueDomains = Array.from(new Set(allProjects.map(p => p.domain)));

  // Aplicar filtros
  const filteredProjects = allProjects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    const matchesDomain = domainFilter === 'all' || project.domain === domainFilter;
    
    return matchesSearch && matchesStatus && matchesDomain;
  });

  const handleOpenModal = () => {
    setIsCreateModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsCreateModalOpen(false);
  };

  const handleCreateProject = (projectData: any) => {
    console.log('Novo projeto criado:', projectData);
    // Aqui você implementaria a lógica para adicionar o projeto à lista
    handleCloseModal();
  };

  const handleProjectClick = (projectId: string) => {
    const project = allProjects.find(p => p.id === projectId);
    if (project) {
      console.log(`Entrando no projeto ${projectId}: ${project.name}`);
      enterProjectContext(projectId, project.name);
    }
  };

  const getStatusDisplay = (status: ProjectStatus) => {
    const statusMap = {
      [ProjectStatus.DRAFT]: 'Rascunho',
      [ProjectStatus.IN_PROGRESS]: 'Em Progresso',
      [ProjectStatus.COMPLETED]: 'Concluído',
      [ProjectStatus.ARCHIVED]: 'Arquivado'
    };
    return statusMap[status] || status;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  return (
    <div className="project-list-container">
      {/* Header */}
      <div className="project-list-header">
        <div className="header-left">
          <h1>Projetos</h1>
          <p className="header-subtitle">
            Gerencie e acompanhe todos os seus projetos LangNet
          </p>
        </div>
        <ProjectCreationButton onOpenModal={handleOpenModal} />
      </div>

      {/* Filtros e Busca */}
      <div className="filters-section">
        <div className="search-container">
          <input
            type="text"
            placeholder="Buscar projetos por nome ou descrição..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>

        <div className="filters-container">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todos os Status</option>
            <option value={ProjectStatus.DRAFT}>Rascunho</option>
            <option value={ProjectStatus.IN_PROGRESS}>Em Progresso</option>
            <option value={ProjectStatus.COMPLETED}>Concluído</option>
            <option value={ProjectStatus.ARCHIVED}>Arquivado</option>
          </select>

          <select
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todos os Domínios</option>
            {uniqueDomains.map(domain => (
              <option key={domain} value={domain}>{domain}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Estatísticas */}
      <div className="stats-bar">
        <div className="stat-item">
          <span className="stat-number">{allProjects.length}</span>
          <span className="stat-label">Total de Projetos</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">
            {allProjects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length}
          </span>
          <span className="stat-label">Em Progresso</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">
            {allProjects.filter(p => p.status === ProjectStatus.COMPLETED).length}
          </span>
          <span className="stat-label">Concluídos</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{filteredProjects.length}</span>
          <span className="stat-label">Filtrados</span>
        </div>
      </div>

      {/* Lista de Projetos */}
      <div className="projects-grid">
        {filteredProjects.map(project => (
          <div 
            key={project.id} 
            className="project-list-card"
            onClick={() => handleProjectClick(project.id)}
          >
            <div className="project-card-header">
              <h3 className="project-title">{project.name}</h3>
              <span className={`project-status status-${project.status.toLowerCase().replace('_', '-')}`}>
                {getStatusDisplay(project.status)}
              </span>
            </div>
            
            <p className="project-description">{project.description}</p>
            
            <div className="project-meta">
              <div className="meta-item">
                <span className="meta-label">Domínio:</span>
                <span className="meta-value">{project.domain}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Criado:</span>
                <span className="meta-value">{formatDate(project.createdAt)}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Atualizado:</span>
                <span className="meta-value">{formatDate(project.updatedAt)}</span>
              </div>
            </div>
            
            <div className="project-progress">
              <div className="progress-header">
                <span className="progress-label">Progresso</span>
                <span className="progress-percentage">{project.progress}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${project.progress}%` }}
                ></div>
              </div>
            </div>

            <div className="project-actions">
              <button 
                className="action-button primary"
                onClick={(e) => {
                  e.stopPropagation();
                  handleProjectClick(project.id);
                }}
              >
                Abrir Projeto
              </button>
              <button 
                className="action-button secondary"
                onClick={(e) => {
                  e.stopPropagation();
                  console.log('Editar projeto', project.id);
                }}
              >
                Editar
              </button>
            </div>
          </div>
        ))}

        {/* Card para criar novo projeto */}
        <div className="new-project-card" onClick={handleOpenModal}>
          <div className="new-project-icon">+</div>
          <h3>Criar Novo Projeto</h3>
          <p>Comece um novo projeto LangNet do zero ou usando um modelo</p>
        </div>
      </div>

      {/* Mensagem quando não há resultados */}
      {filteredProjects.length === 0 && (
        <div className="no-results">
          <div className="no-results-icon">🔍</div>
          <h3>Nenhum projeto encontrado</h3>
          <p>Tente ajustar os filtros ou criar um novo projeto</p>
          <button className="create-button" onClick={handleOpenModal}>
            Criar Novo Projeto
          </button>
        </div>
      )}

      {/* Modal de criação */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseModal}
        onCreateProject={handleCreateProject}
      />
    </div>
  );
};

export default ProjectList;