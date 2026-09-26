/**
 * VerbosePanel.jsx
 * 
 * REPLICA EXATA do formato MD gerado pelo teste testar_interface_generica_v7_md.js
 * Mostra INPUTS/EXECUÇÃO/OUTPUTS em tempo real no mesmo formato do teste
 */

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

// IMPORTAÇÃO ADICIONADA PARA CORREÇÕES DO CODEX
import { CentralWSClient } from './utils_exec/centralWSClient';

const VerbosePanel = ({ 
  isOpen = false,
  onClose,
  verboseSteps = [], 
  mdContent = '',
  taskCounters = {},
  isExecuting = false,
  position = { x: 20, y: 20 },
  // Quem é este projeto — a bancada serve a qualquer aplicação gerada, então
  // nada de nome de tarefa nem endereço fixos aqui dentro.
  nomeDoProjeto = '',
  enderecoDoServidor = '',
  tarefasDoProjeto = []
}) => {
  const endRef = React.useRef(null);
  // Janela flutuante: posição/arraste/minimizar
  const [pos, setPos] = useState(() => {
    try {
      const rawPos = localStorage.getItem('verbosePanel_pos');
      if (rawPos) {
        const saved = JSON.parse(rawPos);
        if (saved && typeof saved.x === 'number' && typeof saved.y === 'number') {
          return saved;
        }
      }
    } catch (e) { /* ignore */ }
    return position || { x: 20, y: 60 };
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
  useEffect(() => () => {
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  }, []);
  const [minimized, setMinimized] = useState(() => {
    try {
      const rawMin = localStorage.getItem('verbosePanel_min');
      if (rawMin !== null) {
        const savedMin = JSON.parse(rawMin);
        if (typeof savedMin === 'boolean') return savedMin;
      }
    } catch (e) { /* ignore */ }
    return false;
  });
  useEffect(() => {
    try { localStorage.setItem('verbosePanel_pos', JSON.stringify(pos)); } catch (e) { /* ignore */ }
  }, [pos.x, pos.y]);
  useEffect(() => {
    try { localStorage.setItem('verbosePanel_min', JSON.stringify(minimized)); } catch (e) { /* ignore */ }
  }, [minimized]);

  // Estado local para montar MD incremental quando chegar verbose
  const [localMd, setLocalMd] = useState('');

  // Auto-scroll para o final quando novos steps chegam
  useEffect(() => {
    if (endRef.current && isExecuting) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [mdContent, localMd, isExecuting]);

  // CONEXÃO COM CENTRALWSCLIENT (correção do codex)
  useEffect(() => {
    console.log('🔗 [VERBOSE PANEL] Conectando ao CentralWSClient');
    
    // Obter instância central
    const central = CentralWSClient.getInstance();
    
    // Registrar callback para receber dados WebSocket V8
    const handleVerboseStep = (data) => {
      if (!data) return;
      
      console.log('🔗 [VERBOSE PANEL] Processando dados V8:', data.type, data);
      
      const ts = new Date().toLocaleTimeString();
      let line = '';
      
      // Processar diferentes tipos de mensagem V8
      if (data.type === 'tags_extracted') {
        line = `**[${ts}] [tags_extracted]**\n`;
        if (data.tags) {
          for (const [key, value] of Object.entries(data.tags)) {
            const preview = typeof value === 'string' ? value.substring(0, 100) : JSON.stringify(value).substring(0, 100);
            line += `  • **${key}**: ${preview}${preview.length >= 100 ? '...' : ''}\n`;
          }
        }
        line += '\n';
      } 
      else if (data.type === 'parsing_metrics') {
        line = `**[${ts}] [parsing_metrics]** Métricas do Enhanced Parser V8\n`;
        if (data.metrics) {
          line += `  📈 ${JSON.stringify(data.metrics, null, 2)}\n`;
        }
        line += '\n';
      }
      else if (data.type === 'task_step') {
        const stepInfo = data.step_info || {};
        const stepType = stepInfo.step_type || 'task_step';
        const stepName = stepInfo.step_name || stepInfo.task_name || 'Step';
        const description = stepInfo.description || stepInfo.content || 'Executando step';
        
        line = `**[${ts}] [${stepType}]** ${stepName}\n`;
        line += `  📝 ${description}\n`;
        
        if (stepInfo.tool_name) {
          line += `  🔧 Tool: ${stepInfo.tool_name}\n`;
        }
        if (stepInfo.agent_name) {
          line += `  🤖 Agent: ${stepInfo.agent_name}\n`;
        }
        if (stepInfo.input_data) {
          const inputStr = typeof stepInfo.input_data === 'string' ? stepInfo.input_data : JSON.stringify(stepInfo.input_data);
          const preview = inputStr.substring(0, 200);
          line += `  📥 Input: ${preview}${inputStr.length > 200 ? '...' : ''}\n`;
        }
        if (stepInfo.output_data) {
          const outputStr = typeof stepInfo.output_data === 'string' ? stepInfo.output_data : JSON.stringify(stepInfo.output_data);
          const preview = outputStr.substring(0, 200);
          line += `  📤 Output: ${preview}${outputStr.length > 200 ? '...' : ''}\n`;
        }
        line += '\n';
      }
      else {
        // Fallback para tipos desconhecidos
        line = `**[${ts}] [${data.type || 'unknown'}]** Dados V8\n`;
        const preview = JSON.stringify(data, null, 2).substring(0, 300);
        line += `  📦 ${preview}${preview.length >= 300 ? '...' : ''}\n\n`;
      }
      
      setLocalMd(prev => prev + line);

      // Encaminhar o mesmo step para a aba Operação, se disponível (ponte)
      try { if (window && typeof window.__routeOperationStep === 'function') { window.__routeOperationStep(data); } } catch (_) {}
    };
    
    // ✅ REATIVADO: Receber dados WebSocket V8
    central.setVerboseCallback(handleVerboseStep);
    console.log('🔗 [VERBOSE PANEL] Callback V8 registrado para receber dados WebSocket');
    
    // CLEANUP
    return () => {
      console.log('🧹 [VERBOSE PANEL] Cleanup callback V8');
      central.setVerboseCallback(null);
    };
  }, []); // Executar apenas uma vez

  // Se não está aberto, não renderiza
  if (!isOpen) return null;

  // NOTA: a lista de tarefas e o cabeçalho eram fixos no projeto TropicalSales.
  // Removidos: o conteúdo mostrado vem por propriedade (mdContent), do projeto
  // que estiver sendo executado. A bancada serve a qualquer projeto gerado.

  // ✨ CONTEÚDO MD AGORA VEM VIA PROPS do ExecutorTarefasNew




  const formatDataForMD = (data, type) => {
    switch (type) {
      case 'json':
        if (typeof data === 'object') {
          return `\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\``;
        } else {
          return `\`\`\`json\n${data}\n\`\`\``;
        }
      
      case 'file':
        return `📁 ${data}`;
      
      case 'text':
        return `${data}`;
      
      default:
        return data;
    }
  };



  if (minimized) {
    return (
      <div style={{ position: 'fixed', top: pos.y, left: pos.x, zIndex: 1000, background: '#f5f5f5', border: '1px solid #ccc', borderRadius: '6px', padding: '6px 10px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'move' }} onMouseDown={onHeaderMouseDown}>
        <span style={{ fontSize: '12px', color: '#333' }}>📝 Acompanhamento (minimizado)</span>
        <button onClick={(e) => { e.stopPropagation(); setMinimized(false); }} style={{ background: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', padding: '4px 8px', fontSize: '12px', cursor: 'pointer' }}>Restaurar</button>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed',
      top: pos.y,
      left: pos.x,
      width: '500px',
      height: '600px',
      backgroundColor: 'white',
      border: '1px solid #ccc',
      borderRadius: '8px',
      boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Cabeçalho - IDÊNTICO ao SimulationPanel */}
      <div style={{
        padding: '10px',
        borderBottom: '1px solid #eee',
        backgroundColor: '#f5f5f5',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }} onMouseDown={onHeaderMouseDown}>
        <h3 style={{ margin: 0, fontSize: '16px', color: '#333333', cursor: 'move' }}>Acompanhamento de Execução</h3>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button onClick={(e) => { e.stopPropagation(); setMinimized(true); }} title="Minimizar" style={{ border: '1px solid #ccc', background: 'white', borderRadius: '4px', padding: '2px 8px', cursor: 'pointer' }}>—</button>
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

      {/* Conteúdo MD renderizado - MESMO ESTILO do SimulationPanel */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        padding: '15px',
        backgroundColor: 'white',
        fontFamily: 'Arial, sans-serif',
        fontSize: '14px',
        lineHeight: '1.4',
        color: '#333333'
      }}>
        <ReactMarkdown>
          {(mdContent + '\n' + localMd) || `# ACOMPANHAMENTO DE EXECUÇÃO — ENTRADAS / EXECUÇÃO / SAÍDAS

**Data:** ${new Date().toLocaleString()}
**Projeto:** ${nomeDoProjeto || '(nenhum selecionado)'}
**Servidor de agentes:** ${enderecoDoServidor || '(não informado)'}

---

## 🎯 TAREFAS DESTE PROJETO

${(tarefasDoProjeto && tarefasDoProjeto.length
   ? tarefasDoProjeto.map((t, i) => `${i + 1}. **${t}**`).join('\n')
   : '_a lista aparece quando o projeto é carregado_')}

---

## 🚀 EXECUÇÃO EM TEMPO REAL

Aguardando início da execução da rede...`}
        </ReactMarkdown>
        
        {/* Auto-scroll anchor */}
        <div ref={endRef} />
      </div>
    </div>
  );
};

export default VerbosePanel;
