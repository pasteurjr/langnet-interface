import React, { useState, useEffect } from 'react';
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
  // G4: revisão da rede pelo agente (padrão das demais etapas — 🔍 Revisar).
  const [reviewing, setReviewing] = useState(false);
  const [reviewSuggestions, setReviewSuggestions] = useState<string | null>(null);

  const handleReview = async () => {
    setReviewing(true);
    setReviewSuggestions(null);
    try {
      const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
      const r = await fetch(`${API_BASE}/petri-net/${projectId}/review`, {
        method: 'POST',
        headers: { 'Authorization': token ? `Bearer ${token}` : '', 'Content-Type': 'application/json' },
      });
      const d = await r.json();
      setReviewSuggestions(d.suggestions || 'Sem sugestões.');
    } catch (e) {
      setReviewSuggestions(`Falha ao revisar: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setReviewing(false);
    }
  };
  // Instruções adicionais: a etapa da Rede não usa (refino é por regeneração),
  // mas o shell exige as props; mantidas para uniformidade visual.
  const [instructions, setInstructions] = useState('');

  // O editor JointJS renderiza a rede com base no tamanho do container. Como o
  // container ganha o tamanho final só depois do layout da casca, disparamos
  // alguns eventos de resize para forçar o redesenho na largura correta.
  useEffect(() => {
    // A rede carrega de forma assíncrona (fetch) e só então o JointJS desenha;
    // disparamos resize em vários momentos (inclusive tardios) e por um intervalo
    // curto para garantir o redesenho na largura correta após o carregamento.
    const ts = [400, 1200, 2500, 4000, 6000].map((d) =>
      setTimeout(() => window.dispatchEvent(new Event('resize')), d)
    );
    const iv = setInterval(() => window.dispatchEvent(new Event('resize')), 1000);
    const stop = setTimeout(() => clearInterval(iv), 8000);
    return () => {
      ts.forEach(clearTimeout);
      clearInterval(iv);
      clearTimeout(stop);
    };
  }, []);

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
      collapsibleSidebar
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
      onReview={handleReview}
      reviewing={reviewing}
      canReview={!generating}
      chat={
        <div style={{ padding: 16, fontSize: 13, color: '#555' }}>
          O refino da rede é por regeneração. Use <b>🔍 Revisar</b> para o agente analisar a
          rede (deadlocks, alcançabilidade, cobertura de tasks) e sugerir melhorias.
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
          {reviewSuggestions !== null && (
            <div
              onClick={() => setReviewSuggestions(null)}
              style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)', display: 'flex',
                       alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}
            >
              <div onClick={(e) => e.stopPropagation()} style={{ background: '#fff', borderRadius: 12,
                     width: 'min(760px,92vw)', maxHeight: '82vh', overflow: 'auto', boxShadow: '0 12px 40px rgba(0,0,0,0.25)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                       padding: '14px 18px', borderBottom: '1px solid #e2e8f0' }}>
                  <b>🔍 Sugestões de revisão da Rede de Petri</b>
                  <button onClick={() => setReviewSuggestions(null)}
                    style={{ border: 'none', background: '#eef2ff', borderRadius: 8, padding: '6px 12px', cursor: 'pointer' }}>Fechar</button>
                </div>
                <div style={{ padding: 18, fontSize: 13.5, lineHeight: 1.55, color: '#334', whiteSpace: 'pre-wrap' }}>
                  {reviewSuggestions}
                </div>
              </div>
            </div>
          )}
        </>
      }
    >
      <PetriNetEditor projectId={projectId} autoconnectUrl={autoconnectUrl} />
    </StagePageLayout>
  );
};

export default PetriNetPage;
