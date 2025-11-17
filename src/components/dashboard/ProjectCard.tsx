// src/components/projects/ProjectCard.tsx (SUBSTITUIR ARQUIVO ATUAL)
import React from 'react';
import { Project } from '../../types';
import { useNavigation } from '../../contexts/NavigationContext';
import './ProjectCard.css';

interface ProjectCardProps {
  project: Project;
  onClick: (id: string) => void;
  onEdit?: (project: Project) => void;
  onDelete?: (id: string) => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onClick, onEdit, onDelete }) => {
  const { enterProjectContext } = useNavigation();

  const handleClick = () => {
    onClick(project.id);
    enterProjectContext(project.id, project.name);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEdit) onEdit(project);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) onDelete(project.id);
  };

  return (
    <div className="project-card" onClick={handleClick}>
      <div className="project-card-header">
        <h3 className="project-title">{project.name}</h3>
        <div className="project-actions">
          {onEdit && (
            <button className="btn-edit" onClick={handleEdit} title="Editar">
              ✏️
            </button>
          )}
          {onDelete && (
            <button className="btn-delete" onClick={handleDelete} title="Excluir">
              🗑️
            </button>
          )}
        </div>
      </div>
      <span className={`project-status status-${project.status}`}>
        {project.status}
      </span>
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
