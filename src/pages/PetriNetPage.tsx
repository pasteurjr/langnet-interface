import React, { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import PetriNetEditor from '../components/petri-net/PetriNetEditor';
import PetriNetHistoryModal from '../components/petri-net/PetriNetHistoryModal';
import GeneratePetriNetModal from '../components/petri-net/GeneratePetriNetModal';
import StagePageLayout from '../components/stage/StagePageLayout';
import { generatePetriNet } from '../services/petriNetService';

const PetriNetPage: React.FC = () => {
  const params = useParams<{ projectId?: string; id?: string }>();
  const [searchParams] = useSearchParams();
  const projectId = params.projectId || params.id || '';
  // ?autoconnect=ws://localhost:5002 — usado quando o usuário acabou de subir o
  // servidor agêntico via "▶ Executar" no CodeGenerationPage.
  const autoconnectUrl = searchParams.get('autoconnect') || undefined;

  const [historyOpen, setHistoryOpen] = useState(false);
  const [generateOpen, setGenerateOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  // Instruções adicionais: a etapa da Rede não usa (refino é por regeneração),
  // mas o shell exige as props; mantidas para uniformidade visual.
  const [instructions, setInstructions] = useState('');

  if (!projectId) {
    return (
      <div className="page-container">
        <h1>🔗 Rede de Petri</h1>
        <p style={{ color: '#c00' }}>Selecione um projeto para acessar a Rede de Petri.</p>
      </div>
    );
  }

  return (
    <StagePageLayout
      title="🔗 Rede de Petri"
      subtitle="Editor visual da rede de Petri gerada a partir de agents.yaml + tasks.yaml + Sequência de Tarefas."
      sidebarTitle="🔗 Rede"
      wideViewer
      sourceButtons={
        <button
          className="btn-history-compact"
          onClick={() => setGenerateOpen(true)}
          title="Escolher agents.yaml + tasks.yaml + Sequência de Tarefas e gerar a rede"
        >
          🔗 Gerar Rede / Origem
        </button>
      }
      instructions={instructions}
      onInstructionsChange={setInstructions}
      onGenerate={() => setGenerateOpen(true)}
      generating={generating}
      generateLabel="🔗 Gerar Rede"
      onHistory={() => setHistoryOpen(true)}
      chat={
        <div style={{ padding: 16, fontSize: 13, color: '#555' }}>
          O refino da rede é por regeneração (não há chat).
        </div>
      }
      modals={
        <>
          <GeneratePetriNetModal
            isOpen={generateOpen}
            projectId={projectId}
            onClose={() => setGenerateOpen(false)}
            onConfirm={async (sel) => {
              setGenerateOpen(false);
              setGenerating(true);
              try {
                await generatePetriNet(projectId, sel);
                window.location.reload();
              } catch (e) {
                // eslint-disable-next-line no-alert
                alert(`Falha ao gerar a rede: ${e instanceof Error ? e.message : String(e)}`);
              } finally {
                setGenerating(false);
              }
            }}
          />
          <PetriNetHistoryModal
            isOpen={historyOpen}
            onClose={() => setHistoryOpen(false)}
            projectId={projectId}
            onRestored={() => window.location.reload()}
          />
        </>
      }
    >
      <PetriNetEditor projectId={projectId} autoconnectUrl={autoconnectUrl} />
    </StagePageLayout>
  );
};

export default PetriNetPage;
