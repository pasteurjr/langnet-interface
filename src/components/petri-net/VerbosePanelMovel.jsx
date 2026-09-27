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
import { inscrever } from './utils_exec/distribuidorDeAvisos';


// CABEÇALHO DO PROJETO QUE ESTÁ NA TELA.
// Este painel vinha da máquina de referência com a lista de tarefas do TropicalSales
// escrita à mão ("READ EMAIL", "CHECK STOCK") e com o endereço do servidor dela.
// Num acompanhamento do BioByte aparecia, em cima da rede, o nome das tarefas de
// OUTRO sistema. Agora o cabeçalho é montado com o que a rede da tela declara.
function cabecalhoDoProjeto() {
  const agora = new Date().toLocaleString();
  let projeto = null;
  try { projeto = (typeof window !== 'undefined' && window.V7_PROJECT) || null; } catch (e) { /* sem window */ }
  const rede = (projeto && (projeto.project_data || projeto.petriNet || projeto.petri_net_data)) || null;
  const lugares = (rede && (rede.lugares || rede.places)) || [];
  const tarefas = lugares
    .map((l) => {
      const m = String(l && l.logica || '').match(/const TASK_NAME\s*=\s*['"`]([^'"`]+)/);
      return m ? m[1] : null;
    })
    .filter(Boolean);
  let endereco = '';
  try { endereco = (typeof window !== 'undefined' && window.V7_WS_URI) || ''; } catch (e) { /* sem window */ }

  const linhas = [
    '# ACOMPANHAMENTO DE EXECUÇÃO - INPUTS/EXECUÇÃO/OUTPUTS',
    '',
    `**Projeto:** ${(projeto && projeto.name) || (rede && rede.nome) || 'sem projeto carregado'}`,
    `**Data:** ${agora}`,
    `**Servidor de agentes:** ${endereco || 'não informado'}`,
    '',
    '---',
    '',
    '## 🎯 TAREFAS DESTA REDE',
    '',
  ];
  if (tarefas.length) {
    tarefas.forEach((t, i) => linhas.push(`${i + 1}. **${t}**`));
  } else {
    linhas.push('_A rede carregada não declara tarefas._');
  }
  linhas.push('', '---', '', '## 🚀 EXECUÇÃO EM TEMPO REAL', '');
  return linhas.join('\n');
}

const VerbosePanel = ({ 
  isOpen = false,
  onClose,
  verboseSteps = [], 
  mdContent = '',
  taskCounters = {},
  isExecuting = false,
  position = { x: 20, y: 20 }
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
    const __desinscrever = inscrever(handleVerboseStep);
    console.log('🔗 [VERBOSE PANEL] Callback V8 registrado para receber dados WebSocket');
    
    // CLEANUP
    return () => {
      console.log('🧹 [VERBOSE PANEL] Cleanup callback V8');
      __desinscrever && __desinscrever();
    };
  }, []); // Executar apenas uma vez

  // Se não está aberto, não renderiza
  if (!isOpen) return null;

  // Mapeamento EXATO do teste MD
  // Os nomes vêm da rede carregada; sem rede, o número da tarefa já basta.
  const taskNames = (() => {
    const cab = cabecalhoDoProjeto();
    const achados = (cab.match(/^\d+\. \*\*(.+)\*\*$/gm) || [])
      .map((l) => l.replace(/^\d+\. \*\*|\*\*$/g, ''));
    const mapa = {};
    achados.forEach((nome, i) => { mapa[i + 1] = `${i + 1}. ${nome}`; });
    return mapa;
  })();

  const sectionMap = {
    'inputs': '📥 INPUTS SENDO USADOS',
    'execution': '⚡ EXECUÇÃO/FERRAMENTAS',
    'outputs': '📦 OUTPUTS PRODUZIDOS'
  };

  // ✨ CONTEÚDO MD AGORA VEM VIA PROPS do ExecutorTarefasNew

  const generateHeader = () => cabecalhoDoProjeto();

  const generateTaskSection = (section) => {
    let content = `## ${section.name}
**Status:** ⚡ Executando
**Contadores:** Inputs: ${section.counters.inputs} | Steps: ${section.counters.steps} | Outputs: ${section.counters.outputs}

`;

    // INPUTS
    if (section.inputs.length > 0) {
      content += `### 📥 INPUTS SENDO USADOS\n`;
      section.inputs.forEach(input => {
        content += `**[${input.timestamp}] [${input.type}]** ${input.content}\n`;
      });
      content += '\n';
    }

    // EXECUÇÃO  
    if (section.execution.length > 0) {
      content += `### ⚡ EXECUÇÃO/FERRAMENTAS\n`;
      section.execution.forEach(exec => {
        content += `**[${exec.timestamp}] [${exec.type}]** ${exec.content}\n`;
      });
      content += '\n';
    }

    // OUTPUTS
    if (section.outputs.length > 0) {
      content += `### 📦 OUTPUTS PRODUZIDOS\n`;
      section.outputs.forEach(output => {
        content += `**[${output.timestamp}] [${output.type}]** ${output.content}\n`;
      });
      content += '\n';
    }

    return content;
  };

  const processStepGeneric = (step, section) => {
    const timestamp = new Date(step.timestamp || Date.now()).toLocaleTimeString();

    // INPUTS: EXATAMENTE como o teste MD
    if (step.input_data || step.step_type === 'tool_input') {
      section.counters.inputs++;
      
      let inputDisplay = '';
      let inputType = 'INPUT';
      
      if (step.step_type === 'tool_input') {
        inputType = 'TOOL INPUT';
        inputDisplay = `### 📥 Tool Input

**Tool:** ${step.tool_name || 'Unknown'}
**Agent:** ${step.agent_name || 'Unknown'}

`;
        
        if (step.input_data) {
          if (typeof step.input_data === 'object' || (typeof step.input_data === 'string' && step.input_data.startsWith('{'))) {
            inputDisplay += formatDataForMD(step.input_data, 'json');
          } else {
            inputDisplay += `\`\`\`\n${step.input_data}\n\`\`\``;
          }
        } else {
          inputDisplay += step.step_description;
        }
      } else if (step.input_data) {
        if (typeof step.input_data === 'object' || (typeof step.input_data === 'string' && step.input_data.startsWith('{'))) {
          inputType = 'JSON INPUT';
          inputDisplay = formatDataForMD(step.input_data, 'json');
        } else if (step.input_data.includes('.') && (step.input_data.includes('/') || step.input_data.length < 100)) {
          inputType = 'FILE INPUT';
          inputDisplay = formatDataForMD(step.input_data, 'file');
        } else {
          inputType = 'TEXT INPUT';
          inputDisplay = formatDataForMD(step.input_data, 'text');
        }
      }
      
      section.inputs.push({
        timestamp,
        type: inputType,
        content: inputDisplay || step.step_description
      });
    }

    // EXECUÇÃO: EXATAMENTE como o teste MD
    if (step.step_type === 'agent_start' || step.step_type === 'tool_usage' || 
        step.step_type === 'tool_executing' || step.step_type === 'crew_start' ||
        step.step_type === 'task_executing' || step.step_type === 'task_status') {
      
      section.counters.steps++;
      
      let execType = 'STEP';
      let execContent = step.step_description;
      
      if (step.step_type === 'agent_start' && step.agent_name) {
        execType = 'AGENT STARTED';
        execContent = `### 🤖 Agent Started

**Agent:** ${step.agent_name}

${step.step_description}`;
      } else if (step.step_type === 'tool_executing' && step.tool_name) {
        execType = 'TOOL EXECUTION';
        execContent = `### 🔧 Agent Tool Execution

**Agent:** ${step.agent_name || 'Unknown'}
**Using Tool:** ${step.tool_name}

${step.step_description}`;
      } else if (step.step_type === 'tool_usage' && step.tool_name) {
        execType = 'TOOL USAGE';
        execContent = `### 🔧 Tool Used

**Tool:** ${step.tool_name}
**Agent:** ${step.agent_name || 'Unknown'}

${step.step_description}`;
      } else if (step.step_type === 'crew_start') {
        execType = 'CREW START';
        execContent = `### 🚀 Crew Started

${step.step_description}`;
      } else if (step.step_type === 'task_executing') {
        execType = 'TASK EXECUTION';
        execContent = `### 📋 Task Executing

${step.step_description}`;
      }
      
      section.execution.push({
        timestamp,
        type: execType,
        content: execContent
      });
    }

    // OUTPUTS: EXATAMENTE como o teste MD
    if (step.output_data || step.step_type === 'tool_output' || step.step_type === 'task_completed') {
      section.counters.outputs++;
      
      let outputDisplay = '';
      let outputType = 'OUTPUT';
      
      if (step.step_type === 'tool_output') {
        outputType = 'TOOL OUTPUT';
        outputDisplay = `### 📤 Tool Output

**Tool:** ${step.tool_name || 'Unknown'}
**Agent:** ${step.agent_name || 'Unknown'}

`;
        
        if (step.output_data) {
          if (typeof step.output_data === 'object' || step.output_data.toString().startsWith('{')) {
            outputDisplay += formatDataForMD(step.output_data, 'json');
          } else {
            outputDisplay += `\`\`\`\n${step.output_data}\n\`\`\``;
          }
        } else {
          outputDisplay += step.step_description;
        }
      } else if (step.step_type === 'task_completed') {
        outputType = 'FINAL ANSWER';
        outputDisplay = `### ✅ Final Answer

${step.step_description || step.output_data}`;
      } else if (step.output_data) {
        if (typeof step.output_data === 'object' || step.output_data.toString().startsWith('{')) {
          outputType = 'JSON OUTPUT';
          outputDisplay = formatDataForMD(step.output_data, 'json');
        } else if (step.output_data.toString().includes('.') && step.output_data.toString().length < 100) {
          outputType = 'FILE OUTPUT';
          outputDisplay = formatDataForMD(step.output_data, 'file');
        } else {
          outputType = 'RESULT OUTPUT';
          outputDisplay = formatDataForMD(step.output_data, 'text');
        }
      }
      
      section.outputs.push({
        timestamp,
        type: outputType,
        content: outputDisplay || step.step_description
      });
    }
  };

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
          {(mdContent + '\n' + localMd)
            || (cabecalhoDoProjeto() + '\nAguardando início da execução da rede...')}
        </ReactMarkdown>
        
        {/* Auto-scroll anchor */}
        <div ref={endRef} />
      </div>
    </div>
  );
};

export default VerbosePanel;
