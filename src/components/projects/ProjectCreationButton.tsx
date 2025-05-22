import React, { useState } from 'react';
import { ProjectFormData } from './CreateProjectModal';

interface ProjectCreationButtonProps {
  onOpenModal: () => void;
}

const ProjectCreationButton: React.FC<ProjectCreationButtonProps> = ({ onOpenModal }) => {
  return (
    <button className="new-project-btn" onClick={onOpenModal}>
      + Novo Projeto
    </button>
  );
};

export default ProjectCreationButton;
