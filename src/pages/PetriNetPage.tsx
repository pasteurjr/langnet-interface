import React, { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import PetriNetEditor from '../components/petri-net/PetriNetEditor';
import PetriNetHistoryModal from '../components/petri-net/PetriNetHistoryModal';

const PetriNetPage: React.FC = () => {
  const params = useParams<{ projectId?: string; id?: string }>();
  const [searchParams] = useSearchParams();
  const projectId = params.projectId || params.id || '';
  // ?autoconnect=ws://localhost:5002 — usado quando o usuário acabou de subir o
  // servidor agêntico via "▶ Executar" no CodeGenerationPage.
  const autoconnectUrl = searchParams.get('autoconnect') || undefined;

  const [historyOpen, setHistoryOpen] = useState(false);

  if (!projectId) {
    return (
      <div className="page-container">
        <h1>🔗 Rede de Petri</h1>
        <p style={{ color: '#c00' }}>Selecione um projeto para acessar a Rede de Petri.</p>
      </div>
    );
  }

  return (
    <div className="page-container" style={{ padding: 0, height: '100%', position: 'relative' }}>
      <button
        onClick={() => setHistoryOpen(true)}
        title="Ver histórico de versões da Rede de Petri e restaurar"
        style={{
          position: 'absolute',
          top: 10,
          right: 10,
          zIndex: 1000,
          padding: '6px 12px',
          backgroundColor: '#6a1b9a',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
        }}
      >
        📜 Histórico
      </button>
      <PetriNetEditor projectId={projectId} autoconnectUrl={autoconnectUrl} />
      <PetriNetHistoryModal
        isOpen={historyOpen}
        onClose={() => setHistoryOpen(false)}
        projectId={projectId}
        onRestored={() => window.location.reload()}
      />
    </div>
  );
};

export default PetriNetPage;
