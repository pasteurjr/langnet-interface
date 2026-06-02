import React from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import PetriNetEditor from '../components/petri-net/PetriNetEditor';

const PetriNetPage: React.FC = () => {
  const params = useParams<{ projectId?: string; id?: string }>();
  const [searchParams] = useSearchParams();
  const projectId = params.projectId || params.id || '';
  // ?autoconnect=ws://localhost:5002 — usado quando o usuário acabou de subir o
  // servidor agêntico via "▶ Executar" no CodeGenerationPage.
  const autoconnectUrl = searchParams.get('autoconnect') || undefined;

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
      <PetriNetEditor projectId={projectId} autoconnectUrl={autoconnectUrl} />
    </div>
  );
};

export default PetriNetPage;
