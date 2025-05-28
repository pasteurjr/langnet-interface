// src/components/projects/ProjectCard.tsx (VERSÃO MELHORADA)
import React from 'react';
import { Project, ProjectStatus } from '../../types';
import { useNavigation } from '../../contexts/NavigationContext';
import './ProjectCard.css';

interface ProjectCardProps {
  project: Project;
  onClick?: (id: string) => void; // Mantido para compatibilidade
  variant?: 'dashboard' | 'list'; // Variante para diferentes layouts
  showActions?: boolean; // Mostrar botões de ação
}

const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  onClick, 
  variant = 'dashboard',
  showActions = false 
}) => {
  const { enterProjectContext } = useNavigation();

  const handleClick = () => {
    // Chama o onClick original para compatibilidade
    if (onClick) {
      onClick(project.id);
    }
    
    // E também entra no contexto do projeto
    enterProjectContext(project.id, project.name);
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

  const cardClassName = `project-card ${variant === 'list' ? 'project-card-list' : 'project-card-dashboard'}`;

  return (
    <div className={cardClassName} onClick={handleClick}>
      <div className="project-card-header">
        <h3 className="project-title">{project.name}</h3>
        <span className={`project-status status-${project.status.toLowerCase().replace('_', '-')}`}>
          {getStatusDisplay(project.status)}
        </span>
      </div>

      <p className="project-description">{project.description}</p>

      {variant === 'list' && (
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
      )}

      {variant === 'dashboard' && (
        <div className="project-meta-simple">
          <span className="project-domain">Domínio: {project.domain}</span>
          <span className="project-date">
            Atualizado: {formatDate(project.updatedAt)}
          </span>
        </div>
      )}

      <div className="project-progress">
        {variant === 'list' && (
          <div className="progress-header">
            <span className="progress-label">Progresso</span>
            <span className="progress-percentage">{project.progress}%</span>
          </div>
        )}
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${project.progress}%` }}
          ></div>
        </div>
        {variant === 'dashboard' && (
          <span className="progress-text">{project.progress}% concluído</span>
        )}
      </div>

      {showActions && (
        <div className="project-actions">
          <button 
            className="action-button primary"
            onClick={(e) => {
              e.stopPropagation();
              handleClick();
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
      )}
    </div>
  );
};

export default ProjectCard;