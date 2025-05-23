// src/components/projects/ProjectCard.tsx (SUBSTITUIR ARQUIVO ATUAL)
import React from 'react';
import { Project } from '../../types';
import { useNavigation } from '../../contexts/NavigationContext';
import './ProjectCard.css';

interface ProjectCardProps {
  project: Project;
  onClick: (id: string) => void; // Mantido para compatibilidade
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onClick }) => {
  const { enterProjectContext } = useNavigation();

  const handleClick = () => {
    // Chama o onClick original para compatibilidade
    onClick(project.id);
    
    // E também entra no contexto do projeto
    enterProjectContext(project.id, project.name);
  };

  return (
    <div className="project-card" onClick={handleClick}>
      <div className="project-card-header">
        <h3 className="project-title">{project.name}</h3>
        <span className={`project-status status-${project.status}`}>
          {project.status}
        </span>
      </div>
      <p className="project-description">{project.description}</p>
      <div className="project-meta">
        <span className="project-domain">Domínio: {project.domain}</span>
        <span className="project-date">
          Atualizado: {new Date(project.updatedAt).toLocaleDateString()}
        </span>
      </div>
      <div className="project-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${project.progress}%` }}
          ></div>
        </div>
        <span className="progress-text">{project.progress}% concluído</span>
      </div>
    </div>
  );
};

export default ProjectCard;
