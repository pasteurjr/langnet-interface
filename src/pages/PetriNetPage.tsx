import React from 'react';
import { useParams } from 'react-router-dom';
import PetriNetEditor from '../components/petri-net/PetriNetEditor';

const PetriNetPage: React.FC = () => {
  // Routes registradas: "projects/:id/petri" e "/project/:projectId/petri-net"
  const params = useParams<{ projectId?: string; id?: string }>();
  const projectId = params.projectId || params.id || '';

  if (!projectId) {
    return (
      <div className="page-container">
        <h1>🔗 Rede de Petri</h1>
        <p style={{ color: '#c00' }}>Selecione um projeto para acessar a Rede de Petri.</p>
      </div>
    );
  }

  return (
    <div className="page-container" style={{ padding: 0, height: '100%' }}>
      <PetriNetEditor projectId={projectId} />
    </div>
  );
};

export default PetriNetPage;
