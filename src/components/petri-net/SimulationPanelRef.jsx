/**
 * SimulationPanel.jsx
 * 
 * Componente React para o painel de simulação de Redes de Petri
 * Fornece interface para controle de simulação passo a passo e automática
 * altura aumentada para acomodar mais conteúdo
 */

import React, { useState, useEffect, forwardRef, useImperativeHandle, useRef } from 'react';

const SimulationPanel = forwardRef(({ 
  simulator, 
  isOpen, 
  onClose, 
  onTransitionFired,
  onTransitionHighlight,
  onSimulationStart,
  pausedByTask = false,
  minimized: minimizedProp,
  onToggleMinimize
}, ref) => {
  // Posição e arraste
  const [pos, setPos] = useState(() => {
    try {
      const raw = localStorage.getItem('simPanel_pos');
      if (raw) {
        const saved = JSON.parse(raw);
        if (saved && typeof saved.x === 'number' && typeof saved.y === 'number') {
          return saved;
        }
      }
    } catch (e) { /* ignore */ }
    return { x: Math.max(window.innerWidth - 420, 20), y: 60 };
  });
  const dragRef = React.useRef(null);
  const onHeaderMouseDown = (e) => {
    dragRef.current = { sx: e.clientX, sy: e.clientY, ox: pos.x, oy: pos.y };
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };
  const onMouseMove = (e) => {
    const drag = dragRef.current;
    if (!drag) return;
    const nx = drag.ox + (e.clientX - drag.sx);
    const ny = drag.oy + (e.clientY - drag.sy);
    setPos({ x: Math.max(0, Math.min(nx, window.innerWidth - 200)), y: Math.max(0, Math.min(ny, window.innerHeight - 40)) });
  };
  const onMouseUp = () => {
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
    dragRef.current = null;
  };
  useEffect(() => {
    try { localStorage.setItem('simPanel_pos', JSON.stringify(pos)); } catch (e) { /* ignore */ }
  }, [pos.x, pos.y]);
  useEffect(() => () => {
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  }, []);

  // Minimizar/restaurar (controlado ou interno)
  const [minimizedInternal, setMinimizedInternal] = useState(() => {
    try {
      const raw = localStorage.getItem('simPanel_min');
      if (raw !== null) {
        const saved = JSON.parse(raw);
        if (typeof saved === 'boolean') return saved;
      }
    } catch (e) { /* ignore */ }
    return false;
  });
  const minimized = typeof minimizedProp === 'boolean' ? minimizedProp : minimizedInternal;
  const toggleMinimize = () => {
    if (typeof onToggleMinimize === 'function') {
      onToggleMinimize();
    } else {
      setMinimizedInternal(!minimizedInternal);
    }
  };
  useEffect(() => {
    // Apenas persiste quando controlado internamente
    if (typeof minimizedProp !== 'boolean') {
      try { localStorage.setItem('simPanel_min', JSON.stringify(minimizedInternal)); } catch (e) { /* ignore */ }
    }
  }, [minimizedInternal, minimizedProp]);
  const [simulationMode, setSimulationMode] = useState('step'); // 'step' ou 'auto'
  const [initialNetState, setInitialNetState] = useState(null); // Estado inicial da rede
  const [forceUpdate, setForceUpdate] = useState(0); // Para forçar re-render
  
  // Quando muda o modo, resetar estado se necessário
  const handleModeChange = (newMode) => {
    setSimulationMode(newMode);
    
    if (simulator) {
      // Parar qualquer execução automática
      setIsAutoRunning(false);
      if (autoInterval) {
        clearInterval(autoInterval);
        setAutoInterval(null);
      }
      
      // Se mudou para modo automático, resetar para estado inicial
      if (newMode === 'auto') {
        simulator.stopSimulation();
        setWasStarted(false); // Reset para estado inicial
        setIsPaused(false);
        setSimulationState(simulator.getSimulationState());
        console.log("🔄 Mudou para modo automático - resetando para 'Iniciar Simulação'");
      }
      // Se mudou para modo passo a passo, iniciar simulação automaticamente
      else if (newMode === 'step') {
        simulator.startSimulation();
        setWasStarted(true);
        setIsPaused(false);
        setSimulationState(simulator.getSimulationState());
        console.log("🔄 Mudou para modo passo a passo - iniciando simulação automaticamente");
      }
    }
  };
  const [isAutoRunning, setIsAutoRunning] = useState(false);
  const [autoInterval, setAutoInterval] = useState(null);
  const [simulationState, setSimulationState] = useState(null);
  const [isPaused, setIsPaused] = useState(false); // Para controlar pausa
  const [wasStarted, setWasStarted] = useState(false); // Para controlar se já foi iniciada

  // Expor controles imperativos para o pai (Editor) iniciar em modo automático
  useImperativeHandle(ref, () => ({
    startAuto() {
      try {
        // Forçar modo automático e iniciar independente do estado assíncrono
        setSimulationMode('auto');
        // Iniciar simulação (liga onSimulationStart e estado interno)
        handleStartSimulation();
        // Garantir que a execução automática comece mesmo se o estado ainda não refletiu 'auto'
        setTimeout(() => {
          handleStartAutoSimulation();
        }, 120);
      } catch (e) {
        console.error('Erro ao iniciar auto pelo ref:', e);
      }
    }
    ,
    pauseAuto() {
      try {
        handleStopAutoSimulation();
      } catch (e) {
        console.error('Erro ao pausar auto pelo ref:', e);
      }
    }
    ,
    resumeAuto() {
      try {
        // Garante que o modo automático esteja ativo e volta a rodar
        setSimulationMode('auto');
        setTimeout(() => {
          handleStartAutoSimulation();
        }, 60);
      } catch (e) {
        console.error('Erro ao retomar auto pelo ref:', e);
      }
    }
  }));

  // Atualizar estado da simulação
  useEffect(() => {
    if (simulator && isOpen) {
      try {
        const state = simulator.getSimulationState();
        setSimulationState(state);
        
        // GUARDAR ESTADO INICIAL da rede quando abre o painel
        if (!initialNetState) {
          const estadoInicial = {
            markingVector: { ...simulator.getMarkingVector() },
            simulationLog: [...simulator.simulationLog]
          };
          setInitialNetState(estadoInicial);
          console.log("💾 Estado inicial da rede guardado:", estadoInicial);
        }
      } catch (error) {
        console.error("Erro ao obter estado da simulação:", error);
        setSimulationState(null);
      }
    } else {
      setSimulationState(null);
    }
  }, [simulator, isOpen]);

  // Escutar mudanças no log do simulator para atualizar painel
  useEffect(() => {
    if (simulator && isOpen) {
      const logLength = simulator.simulationLog ? simulator.simulationLog.length : 0;
      console.log("📝 Log do simulator mudou, tamanho:", logLength);
      
      // Forçar atualização do estado
      setSimulationState(simulator.getSimulationState());
      setForceUpdate(prev => prev + 1);
    }
  }, [simulator?.simulationLog?.length, simulator, isOpen]);

  // Limpar intervalo automático quando componente desmonta
  useEffect(() => {
    return () => {
      if (autoInterval) {
        clearInterval(autoInterval);
      }
    };
  }, [autoInterval]);


  const handleStartSimulation = () => {
    if (simulator) {
      console.log("🚀 Iniciando simulação - modo:", simulationMode);
      
      simulator.startSimulation();
      setIsPaused(false);
      setWasStarted(true); // Marca como iniciada
      setSimulationState(simulator.getSimulationState());
      
      // ✨ CHAMAR CALLBACK PARA ATIVAR VERBOSEPANEL - CORRIGIDO!
      console.log("🔥 DEBUG: handleStartSimulation executado!");
      console.log("🔥 DEBUG: onSimulationStart existe?", !!onSimulationStart);
      if (onSimulationStart) {
        console.log("🔥 DEBUG: Chamando onSimulationStart callback!");
        try {
          onSimulationStart();
          console.log("🔥 DEBUG: onSimulationStart callback executado com sucesso!");
        } catch (error) {
          console.error("🔥 DEBUG: Erro no callback:", error);
        }
      } else {
        console.error("🔥 DEBUG: onSimulationStart callback NÃO está definido!");
      }
      
      // Se estiver no modo automático, iniciar execução automática
      if (simulationMode === 'auto') {
        console.log("🚀 Modo automático: iniciando execução automática");
        // Aguardar um pouco para o estado se atualizar
        setTimeout(() => {
          handleStartAutoSimulation();
        }, 100);
      }
      
      console.log("✅ Simulação iniciada, estado:", simulator.getSimulationState());
    }
  };

  const handleStopSimulation = () => {
    if (simulator) {
      // APENAS pausa a execução automática, NÃO para a simulação
      setIsAutoRunning(false);
      setIsPaused(true); // Marca como pausada
      if (autoInterval) {
        clearInterval(autoInterval);
        setAutoInterval(null);
      }
      // NÃO chama simulator.stopSimulation() - só pausa
      setSimulationState(simulator.getSimulationState());
      onTransitionHighlight(null); // Remove destaque
      console.log("⏸️ Simulação pausada (não parada)");
    }
  };

  const handleResetSimulation = () => {
    if (simulator && initialNetState) {
      console.log("🔄 RESET IDÊNTICO PARA AMBOS OS MODOS");
      console.log("💾 Restaurando estado inicial:", initialNetState);
      
      // Parar execução automática se estiver rodando
      setIsAutoRunning(false);
      setIsPaused(false);
      if (autoInterval) {
        clearInterval(autoInterval);
        setAutoInterval(null);
      }
      
      // RESTAURAR ESTADO INICIAL COMPLETO
      // 1. Restaurar marking vector
      Object.keys(initialNetState.markingVector).forEach(placeId => {
        simulator.markingVector[placeId] = initialNetState.markingVector[placeId];
      });
      
      // 2. Atualizar tokens na Petri Net
      simulator.updatePetriNetTokens();
      
      // 3. Limpar log
      simulator.simulationLog = [];
      simulator.clearSimulationLog();
      
      // 4. Configurar modo apropriado (ÚNICA diferença entre os modos)
      if (simulationMode === 'step') {
        simulator.startSimulation();
        setWasStarted(true);
        console.log("🔄 Modo passo a passo: iniciando após reset");
      } else {
        setWasStarted(false);
        console.log("🔄 Modo automático: aguardando usuário iniciar");
      }
      
      // 5. REDESENHAR IGUAL AO ABRIR O PAINEL
      setSimulationState(simulator.getSimulationState());
      onTransitionHighlight(null);
      onTransitionFired([]); // Primeira passada
      
      setTimeout(() => {
        onTransitionFired([]); // Segunda passada para garantir
      }, 200);
      
      console.log("✅ RESET IDÊNTICO COMPLETO");
    } else {
      console.warn("⚠️ Estado inicial não guardado, reset básico");
      simulator.resetSimulation();
      setSimulationState(simulator.getSimulationState());
      onTransitionFired([]);
    }
  };

  const handleFireTransition = (transitionId) => {
    if (simulator && simulator.isTransitionEnabled(transitionId)) {
      try {
        // Destacar transição
        onTransitionHighlight(transitionId);
        
        // Disparar transição
        const result = simulator.fireTransition(transitionId);
        
        // Atualizar estado
        setSimulationState(simulator.getSimulationState());
        
        // Obter places afetados para destacar em azul escuro
        const lastLogEntry = simulator.simulationLog[simulator.simulationLog.length - 1];
        const affectedPlaces = lastLogEntry ? lastLogEntry.affectedPlaces : [];
        
        // Notificar componente pai com places afetados
        onTransitionFired(affectedPlaces);
        
        // Remover destaque após 2 segundos (mesmo tempo dos disparos)
        setTimeout(() => {
          onTransitionHighlight(null);
        }, 2000);
        
      } catch (error) {
        console.error('Erro ao disparar transição:', error);
        alert(`Erro: ${error.message}`);
      }
    }
  };

  const handleAutoStep = () => {
    // Verificar se ainda deve estar executando
    if (!simulator || !simulator.isSimulating) {
      console.log("🛑 Auto step cancelado - simulador não está ativo");
      return;
    }
    
    // ✅ NOVA VERIFICAÇÃO: Aguardar Places executando JavaScript
    const processingPlaces = simulator.getProcessingPlaces();
    if (processingPlaces.length > 0) {
      console.log("⏳ Auto step aguardando Places processando:", processingPlaces);
      return; // Não continua até todos os Places terminarem
    }
    
    console.log("🎯 Executando auto step...");
    const selectedTransition = simulator.selectRandomEnabledTransition();
    if (selectedTransition) {
      console.log("🎯 Disparando transição:", selectedTransition.id);
      handleFireTransition(selectedTransition.id);
    } else {
      // Não há transições aptas, verificar se ainda há Places processando
      if (processingPlaces.length > 0) {
        console.log("⏳ Aguardando Places processando antes de finalizar:", processingPlaces);
        return;
      }
      
      // Não há transições aptas nem Places processando, parar simulação completamente
      console.log("🛑 Não há mais transições aptas - parando simulação completamente");
      
      // Primeiro para a execução automática e limpa interval
      setIsAutoRunning(false);
      if (autoInterval) {
        clearInterval(autoInterval);
        setAutoInterval(null);
      }
      
      // Para a simulação no simulador
      simulator.stopSimulation();
      setSimulationState(simulator.getSimulationState());
      
      // Remove destaques visuais
      onTransitionHighlight(null);
      
      // Mostra mensagem
      alert('Não há mais transições aptas para disparar. Simulação parada.');
    }
  };

  const handleStartAutoSimulation = () => {
    console.log("🚀 Tentando iniciar execução automática");
    console.log("- isAutoRunning:", isAutoRunning);
    console.log("- simulator exists:", !!simulator);
    console.log("- simulator.isSimulating:", simulator ? simulator.isSimulating : 'N/A');
    
    if (!isAutoRunning && simulator) {
      console.log("✅ Iniciando execução automática");
      
      // 🧹 LIMPAR ESTADOS ANTES DE INICIAR EXECUÇÃO (LOCAL CORRETO)
      console.log('🧹 [SIMULATION PANEL] Forçando limpeza de estados antes da execução...');
      if (typeof window !== 'undefined' && window.__clearAllStates) {
        window.__clearAllStates();
        console.log('✅ [SIMULATION PANEL] Limpeza executada via ExecutorTarefasNew');
      } else {
        console.warn('⚠️ [SIMULATION PANEL] window.__clearAllStates não disponível');
      }
      
      // Limpar interval anterior se existir
      if (autoInterval) {
        clearInterval(autoInterval);
      }
      
      setIsAutoRunning(true);
      const interval = setInterval(() => {
        handleAutoStep();
      }, 2000); // 2 segundos entre disparos
      setAutoInterval(interval);
    } else {
      console.log("❌ Não pode iniciar execução automática");
    }
  };

  const handleStopAutoSimulation = () => {
    setIsAutoRunning(false);
    if (autoInterval) {
      clearInterval(autoInterval);
      setAutoInterval(null);
    }
  };

  if (!isOpen) return null;

  if (minimized) {
    return (
      <div style={{ position: 'fixed', left: pos.x, top: pos.y, zIndex: 1000, background: '#f5f5f5', border: '1px solid #ccc', borderRadius: '6px', padding: '6px 10px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'move' }} onMouseDown={onHeaderMouseDown}>
        <span style={{ fontSize: '12px', color: '#333' }}>🧪 Simulador de Petri Net (minimizado)</span>
        <button onClick={(e) => { e.stopPropagation(); toggleMinimize(); }} style={{ background: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', padding: '4px 8px', fontSize: '12px', cursor: 'pointer' }}>Restaurar</button>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed',
      top: pos.y,
      left: pos.x,
      width: '400px',
      height: '840px',
      backgroundColor: 'white',
      border: '1px solid #ccc',
      borderRadius: '8px',
      boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Cabeçalho */}
      <div style={{
        padding: '10px',
        borderBottom: '1px solid #eee',
        backgroundColor: '#f5f5f5',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }} onMouseDown={onHeaderMouseDown}>
        <h3 style={{ margin: 0, fontSize: '16px', color: '#333333', cursor: 'move' }}>Simulador de Petri Net</h3>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {/* Botões de Aprovação no cabeçalho quando pausado por tarefa */}
          {(() => {
            const isPausedByTask = typeof pausedByTask === 'object' ? !!pausedByTask.paused : !!pausedByTask;
            if (!isPausedByTask) return null;
            return (
              <>
                <button onClick={(e) => { e.stopPropagation(); if (typeof window.__onApproveAndContinue === 'function') window.__onApproveAndContinue(); }} style={{ padding: '4px 8px', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>✅ Aprovar</button>
                <button onClick={(e) => { e.stopPropagation(); if (typeof window.__onResubmitTask === 'function') window.__onResubmitTask(); }} style={{ padding: '4px 8px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>🔁 Re‑submeter</button>
              </>
            );
          })()}
          <button 
            onClick={(e) => { e.stopPropagation(); toggleMinimize(); }}
            title="Minimizar"
            style={{
              background: 'none',
              border: '1px solid #ccc',
              fontSize: '14px',
              cursor: 'pointer',
              padding: '0 6px',
              height: '24px',
              color: '#333333',
              borderRadius: '4px'
            }}
          >
            —
          </button>
          <button 
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '18px',
            cursor: 'pointer',
            padding: '0',
            width: '24px',
            height: '24px',
            color: '#333333'
          }}
        >
          ×
        </button>
        </div>
      </div>

      {/* Controles */}
      <div style={{ padding: '15px', borderBottom: '1px solid #eee' }}>
        <div style={{ marginBottom: '10px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#333333' }}>
            Modo de Execução:
          </label>
          <select 
            value={simulationMode} 
            onChange={(e) => handleModeChange(e.target.value)}
            style={{ width: '100%', padding: '5px', color: '#333333' }}
          >
            <option value="step">Passo a Passo</option>
            <option value="auto">Automático</option>
          </select>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {simulationMode === 'step' ? (
            // MODO PASSO A PASSO: Apenas Reset
            <button 
              onClick={handleResetSimulation}
              style={{
                padding: '8px 12px',
                backgroundColor: '#ff9800',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Reset
            </button>
          ) : (
            // MODO AUTOMÁTICO: Iniciar → Parar → Continuar → Reset
            <>
              {!wasStarted ? (
                // Estado inicial: Botão verde "Iniciar Simulação"
                <button 
                  onClick={handleStartSimulation}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#4CAF50', // Verde
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Iniciar Simulação
                </button>
              ) : isPaused ? (
                // Estado pausado: Botão verde "Continuar Simulação"
                <button 
                  onClick={handleStartSimulation}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#4CAF50', // Verde
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Continuar Simulação
                </button>
              ) : (
                // Estado rodando: Botão vermelho "Parar Simulação"
                <button 
                  onClick={handleStopSimulation}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#f44336', // Vermelho
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Parar Simulação
                </button>
              )}

              <button 
                onClick={handleResetSimulation}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#ff9800',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Reset
              </button>

            </>
          )}
        </div>
        
        {/* Indicadores de Status */}
        {simulationState?.isSimulating && (
          <div style={{ 
            marginTop: '10px', 
            padding: '5px 10px', 
            backgroundColor: '#D4EDDA',
            border: '1px solid #C3E6CB',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold',
            color: '#155724'
          }}>
            ▶️ Simulação Ativa
          </div>
        )}
        {(() => {
          const isPausedByTask = typeof pausedByTask === 'object' ? !!pausedByTask.paused : !!pausedByTask;
          const pausedPlaceName = typeof pausedByTask === 'object' ? (pausedByTask.placeName || null) : null;
          return isPausedByTask ? (
          <div style={{ 
            marginTop: '8px', 
            padding: '5px 10px', 
            backgroundColor: '#FFF3CD',
            border: '1px solid #FFEEBA',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold',
            color: '#856404'
          }}>
            🟡 Pausado por Tarefa{pausedPlaceName ? ` — ${pausedPlaceName}` : ' — aguardando aprovação'}
          </div>
          ) : null;
        })()}
      </div>

      {/* Transições Aptas - AMBOS OS MODOS */}
      {simulationState?.isSimulating && (
        <div style={{ padding: '15px', borderBottom: '1px solid #eee' }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#333333' }}>Transições Aptas:</h4>
          <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
            {!simulationState?.enabledTransitions || simulationState.enabledTransitions.length === 0 ? (
              <p style={{ margin: 0, fontStyle: 'italic', color: '#666' }}>
                Nenhuma transição apta
              </p>
            ) : (
              simulationState.enabledTransitions.map(transition => (
                <button
                  key={`${transition.id}-${forceUpdate}`}
                  onClick={() => handleFireTransition(transition.id)}
                  disabled={simulationMode === 'auto' && isAutoRunning}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '8px',
                    margin: '2px 0',
                    backgroundColor: simulationMode === 'auto' && isAutoRunning ? '#f5f5f5' : '#e3f2fd',
                    border: '1px solid #2196F3',
                    borderRadius: '4px',
                    cursor: simulationMode === 'auto' && isAutoRunning ? 'not-allowed' : 'pointer',
                    textAlign: 'left',
                    opacity: simulationMode === 'auto' && isAutoRunning ? 0.6 : 1,
                    color: '#333333'
                  }}
                >
                  {transition.id} - {transition.nome}
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {/* Estado Atual */}
      {simulationState?.isSimulating && (
        <div style={{ padding: '15px', borderBottom: '1px solid #eee' }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#333333' }}>Estado Atual (Tokens):</h4>
          <div style={{ maxHeight: '100px', overflowY: 'auto', fontSize: '12px' }}>
            {simulationState?.markingVector ? Object.entries(simulationState.markingVector)
              .filter(([placeId]) => !placeId.startsWith('VIRTUAL_'))
              .map(([placeId, tokens]) => {
                // Buscar o nome do place no simulator
                const place = simulator?.petriNet?.lugares?.find(l => l.id === placeId);
                const placeName = place ? place.nome : placeId;
                
                return (
                  <div key={placeId} style={{ margin: '2px 0', color: '#333333' }}>
                    <strong>{placeId}</strong> ({placeName}): <span style={{ color: '#2196F3', fontWeight: 'bold' }}>{tokens} tokens</span>
                  </div>
                );
              }) : (
                <p style={{ margin: 0, fontStyle: 'italic', color: '#666' }}>
                  Dados não disponíveis
                </p>
              )}
          </div>
        </div>
      )}

      {/* Log de Simulação */}
      <div style={{ flex: 1, padding: '15px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#333333' }}>Log de Disparos:</h4>
        <div style={{ flex: 1, overflowY: 'auto', fontSize: '12px', backgroundColor: '#f9f9f9', padding: '8px', borderRadius: '4px' }}>
          {!simulationState?.simulationLog || simulationState.simulationLog.length === 0 ? (
            <p style={{ margin: 0, fontStyle: 'italic', color: '#666' }}>
              Nenhum disparo registrado
            </p>
          ) : (
            simulationState.simulationLog.map((logEntry, index) => (
              <div key={index} style={{ marginBottom: '10px', padding: '8px', backgroundColor: 'white', borderRadius: '4px', border: '1px solid #eee' }}>
                <div style={{ fontWeight: 'bold', color: '#2196F3' }}>
                  [{logEntry.timestamp}] {logEntry.transitionId} - {logEntry.transitionName}
                </div>
                <div style={{ marginTop: '4px', color: '#333333' }}>
                  <strong>Lugares afetados:</strong>
                  {logEntry.affectedPlaces.map((place, placeIndex) => (
                    <div key={placeIndex} style={{ marginLeft: '10px', color: '#666' }}>
                      • {place.id} ({place.name}): {place.previousTokens} → {place.newTokens} tokens
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
});

export default SimulationPanel;
