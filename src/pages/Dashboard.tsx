import React from 'react';
import ProjectCard from '../components/dashboard/ProjectCard';
import { Project, ProjectStatus } from '../types';
import './Dashboard.css';
import { useState } from 'react';
import CreateProjectModal from '../components/projects/CreateProjectModal';
import ProjectCreationButton from '../components/projects/ProjectCreationButton';

const Dashboard: React.FC = () => {
  // Adicione este estado:
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  // Dados de exemplo para projetos recentes
  const recentProjects: Project[] = [
    {
      id: '1',
      name: 'Assistente de Atendimento ao Cliente',
      description: 'Sistema de agentes para automatizar atendimento ao cliente com integração a múltiplos canais.',
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
    }
  ];

  // Métricas de exemplo
  const metrics = [
    { label: 'Projetos Ativos', value: 8 },
    { label: 'Agentes Criados', value: 42 },
    { label: 'Chamadas de API', value: '2.5k' },
    { label: 'Uso de Tokens', value: '450k' }
  ];

  // Atividades recentes de exemplo
  const activities = [
    { id: '1', description: 'Projeto "Assistente de Atendimento" atualizado', time: '2h atrás' },
    { id: '2', description: 'Código gerado para "Análise de Documentos"', time: '5h atrás' },
    { id: '3', description: 'Nova rede de Petri criada em "Assistente de Pesquisa"', time: '1d atrás' },
    { id: '4', description: 'Agente "Analisador de Sentimento" adicionado', time: '2d atrás' }
  ];
  const handleOpenModal = () => {
    setIsCreateModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsCreateModalOpen(false);
  };

  const handleCreateProject = (projectData: any) => {
    console.log('Novo projeto:', projectData);
    // Aqui você implementaria a lógica para criar o projeto
    // Por exemplo, adicionar à lista de projetos recentes
    handleCloseModal();
  };

  const handleProjectClick = (id: string) => {
    console.log(`Navegando para o projeto ${id}`);
    // Implementação real usaria useNavigate do react-router-dom
    // navigate(`/projects/${id}`);
  };

  const handleNewProject = () => {
    // Código existente que você quer manter...
    
    // Abrir o modal
    handleOpenModal();
  };

  return (
    <div className="dashboard-container">
      <section className="dashboard-header">
        <h1>Dashboard</h1>
        <ProjectCreationButton onOpenModal={handleOpenModal} />
      </section>

      <section className="metrics-panel">
        <h2>Métricas do Sistema</h2>
        <div className="metrics-grid">
          {metrics.map((metric, index) => (
            <div key={index} className="metric-card">
              <h3 className="metric-value">{metric.value}</h3>
              <p className="metric-label">{metric.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="recent-projects">
        <h2>Projetos Recentes</h2>
        <div className="projects-grid">
          {recentProjects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onClick={handleProjectClick}
            />
          ))}
          <div className="new-project-card" onClick={handleNewProject}>
            <div className="new-project-icon">+</div>
            <p>Criar Novo Projeto</p>
          </div>
        </div>
      </section>

      <section className="activity-feed">
        <h2>Atividades Recentes</h2>
        <ul className="activity-list">
          {activities.map(activity => (
            <li key={activity.id} className="activity-item">
              <p className="activity-description">{activity.description}</p>
              <span className="activity-time">{activity.time}</span>
            </li>
          ))}
        </ul>
      </section>
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseModal}
        onCreateProject={handleCreateProject}
      />
    </div>
  );
};

export default Dashboard;
