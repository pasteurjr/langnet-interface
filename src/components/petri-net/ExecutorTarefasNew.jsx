import React, { useState, useEffect, useRef } from 'react';
import PetriNetEngine from './PetriNetEngine';
import PetriNetEditor from './PetriNetEditorExec';
import { PetriNetSimulator } from './PetriNetSimulator';
import { useProjectLoader } from './useProjectLoader';
import { useContextState } from './useContextState';
import { ExecutionEngine } from './engine_ExecutionEngine';
// WebSocketV7Client removido - usando WebSocket V8 via CentralWSClient
import { CentralWSClient } from './utils_exec/centralWSClient';
import VerbosePanel from './VerbosePanel';
import VerbosePanelV8 from './VerbosePanelEtiquetas';
import { UI_VERSION, BUILD_LOADED_AT } from './version';

// Estados das tarefas
const TASK_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  ERROR: 'error'
};

// Tipos de step internos que não devem ser exibidos
const INTERNAL_STEP_TYPES = [
  'task_detection',
  'box_start',
  'task_input_detection',
  'agent_started',
  'tool_execution',
  'box_end'
];

// Icons usando unicode
const PlayIcon = () => <span>▶️</span>;
const PauseIcon = () => <span>⏸️</span>;
const ResetIcon = () => <span>🔄</span>;
const EyeIcon = () => <span>👁️</span>;
const RobotIcon = () => <span>🤖</span>;
const ChartIcon = () => <span>📊</span>;
const FileIcon = () => <span>📄</span>;
const SettingsIcon = () => <span>⚙️</span>;
const ActivityIcon = () => <span>⚡</span>;

const ExecutorTarefas = ({ project }) => {
  // ETAPA 2 - Hooks genéricos do motor
  const {
    loading: projectLoading,
    error: projectError,
    currentProject,
    loadProjectWithAutoConfig
  } = useProjectLoader();

  const contextStateManager = useContextState();
  const [executionEngine, setExecutionEngine] = useState(null);
  const [realExecutionMode, setRealExecutionMode] = useState(false);
  const [webSocketClient, setWebSocketClient] = useState(null);
  // Função para serializar dados de forma segura
  const safeStringify = (data) => {
    if (typeof data === 'string') return data;
    if (typeof data === 'object' && data !== null) {
      try {
        return JSON.stringify(data, null, 2);
      } catch (e) {
        return '[Objeto não serializável]';
      }
    }
    return String(data || '');
  };

  // Estados principais
  const [activeTab, setActiveTab] = useState('operacao');
  const [executionState, setExecutionState] = useState('idle');
  const [logs, setLogs] = useState([]);
  // Modo de execução: 'continuous' (padrão) ou 'pause_per_task' (Etapa 1A)
  const [execMode, setExecMode] = useState('continuous');
  const [pendingApproval, setPendingApproval] = useState(null); // { place, result }
  
  // ETAPA 2 - Estados do motor real
  const [motorInitialized, setMotorInitialized] = useState(false);
  const [realTimeExecution, setRealTimeExecution] = useState(false);
  
  // Estados do simulador Petri Net
  const [petriNetSimulator, setPetriNetSimulator] = useState(null);
  const [simulationRunning, setSimulationRunning] = useState(false);
  
  // Estados WebSocket Verbose
  const [verboseSteps, setVerboseSteps] = useState([]);
  const [wsConnected, setWsConnected] = useState(true); // V8 gerenciado via CentralWSClient
  const [verboseByTab, setVerboseByTab] = useState({
    operacao: [], inputs: [], execution: [], outputs: [], logs: []
  });
  
  
  // ✨ NOVO: TaskCounters IDÊNTICOS ao testar_interface_generica_v7_md.js
  const [taskCounters, setTaskCounters] = useState({
    'read_email': { task: 1, inputs: 0, steps: 0, outputs: 0 },
    'classify_message': { task: 2, inputs: 0, steps: 0, outputs: 0 },
    'check_stock_availability': { task: 3, inputs: 0, steps: 0, outputs: 0 },
    'generate_response': { task: 4, inputs: 0, steps: 0, outputs: 0 }
  });
  
  const [mdContent, setMdContent] = useState('');
  const [taskResults, setTaskResults] = useState({});

  // Estado VerbosePanel
  const [verbosePanelVisible, setVerbosePanelVisible] = useState(false);

  // Estados para configuração de Inputs (ETAPA 6)
  const [databaseUrl, setDatabaseUrl] = useState('');
  const [apiEndpoint, setApiEndpoint] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState({});

  // Função para extrair places com tasks da Petri Net (ETAPA 6)
  const getTaskPlacesFromPetriNet = () => {
    if (!petriNetData || !petriNetData.lugares) return [];
    
    return petriNetData.lugares.filter(place => 
      place.agentId && // Tem agente (é uma task)
      place.input_data && // Tem dados de input
      place.nome && place.nome !== "Sistema\nIniciado" // Não é o place inicial
    ).map(place => ({
      id: place.id,
      name: place.nome.replace('\n', ' ').replace('_task', ''),
      agent: place.agentId,
      description: `Tarefa executada pelo agente ${place.agentId}`,
      input_data: place.input_data,
      output_data: place.output_data || {},
      delay: place.delay || 0,
      coordinates: place.coordenadas
    }));
  };

  // Função para extrair external_inputs de um place (ETAPA 6)
  const getExternalInputsFromPlace = (place) => {
    if (!place.input_data || !place.input_data.external_inputs) return [];
    return place.input_data.external_inputs;
  };

  // Função para extrair inputs internos de um place (ETAPA 6)
  const getInternalInputsFromPlace = (place) => {
    if (!place.input_data) return {};
    const { external_inputs, ...internalInputs } = place.input_data;
    return internalInputs;
  };
  
  // Estados da Petri Net
  const [petriNetEngine, setPetriNetEngine] = useState(null);
  const [petriNetData, setPetriNetData] = useState(null);
  const petriNetEditorRef = useRef(null);
  const [taskStates, setTaskStates] = useState({});
  const [executionSummary, setExecutionSummary] = useState(null);
  const [petriNetExpanded, setPetriNetExpanded] = useState(false); // Card colapsável
  const [editorReady, setEditorReady] = useState(false);
  const [startPending, setStartPending] = useState(false);

  // Estados da aba Operação (Etapa 2)
  const [operationInputs, setOperationInputs] = useState([]);
  const [operationSteps, setOperationSteps] = useState([]);
  const [operationOutputs, setOperationOutputs] = useState([]);
  const [expandedDocId, setExpandedDocId] = useState(null); // Para expand/collapse de documentos

  // Novos estados para layout V2
  const [operationTaskProgress, setOperationTaskProgress] = useState(0);
  const [operationOverallProgress, setOperationOverallProgress] = useState(0);
  const [currentTaskName, setCurrentTaskName] = useState('');
  const [currentAgentName, setCurrentAgentName] = useState('');
  const [taskCompleted, setTaskCompleted] = useState(false);
  const [approvalProcessed, setApprovalProcessed] = useState(false); // Flag para evitar re-trigger após aprovação

  // Estados para o modal de edição
  const [showEditOutputModal, setShowEditOutputModal] = useState(false);
  
  // Estado Enhanced Parser V8
  // ⭐ V10: Enhanced Parser V10 com 10 Universal Tags
  const [enhancedParserV8Tags, setEnhancedParserV8Tags] = useState({
    TASK_NAME: null,
    AGENT_NAME: null,
    TASK_INPUT: null,
    USED_TOOL: null,
    TOOL_INPUT: null,
    TASK_OUTPUT: null,
    TASK_OUTPUT_TYPE: null,
    TASK_STEP: null,
    TOOL_OUTPUT: null,    // ⭐ V10: Nova tag
    AGENT_THOUGHT: null   // ⭐ V10: Nova tag
  });

  // 🧹 Helper function: Limpar tags com markdown duplicado do backend
  const cleanTagValue = (value) => {
    if (!value || typeof value !== 'string') return value;

    // Remove linhas que começam com "- **NOME_TAG**:" (prefixos markdown duplicados)
    const lines = value.split('\n');
    const cleanedLines = lines.filter(line => {
      // Se a linha começa com "- **" e contém "**:", é um prefixo duplicado
      return !line.trim().match(/^-\s*\*\*[A-Z_]+\*\*:/);
    });

    return cleanedLines.join('\n').trim();
  };

  // Expor setEnhancedParserV8Tags globalmente para CentralWSClient
  useEffect(() => {
    window.__setEnhancedParserV8Tags = setEnhancedParserV8Tags;
    console.log('🌐 [EXECUTOR] setEnhancedParserV8Tags exposto globalmente');

    return () => {
      delete window.__setEnhancedParserV8Tags;
    };
  }, []);

  // 🔍 DEBUG: Monitorar mudanças no enhancedParserV8Tags
  useEffect(() => {
    console.log('🔍 [DEBUG enhancedParserV8Tags] Estado atual:', {
      TASK_NAME: enhancedParserV8Tags.TASK_NAME || 'NULL',
      AGENT_NAME: enhancedParserV8Tags.AGENT_NAME || 'NULL',
      TASK_INPUT: enhancedParserV8Tags.TASK_INPUT ? `EXISTS (${enhancedParserV8Tags.TASK_INPUT.length} chars)` : 'NULL',
      TOOL_INPUT: enhancedParserV8Tags.TOOL_INPUT ? 'EXISTS' : 'NULL',
      TASK_OUTPUT: enhancedParserV8Tags.TASK_OUTPUT ? `EXISTS (${typeof enhancedParserV8Tags.TASK_OUTPUT === 'string' ? enhancedParserV8Tags.TASK_OUTPUT.length : 'object'} chars)` : 'NULL',
      TOOL_OUTPUT: enhancedParserV8Tags.TOOL_OUTPUT ? `EXISTS (${typeof enhancedParserV8Tags.TOOL_OUTPUT === 'string' ? enhancedParserV8Tags.TOOL_OUTPUT.length : 'object'} chars)` : 'NULL',
      USED_TOOL: enhancedParserV8Tags.USED_TOOL || 'NULL',
      TASK_STEP: enhancedParserV8Tags.TASK_STEP ? 'EXISTS' : 'NULL',
      AGENT_THOUGHT: enhancedParserV8Tags.AGENT_THOUGHT ? 'EXISTS' : 'NULL'
    });
  }, [enhancedParserV8Tags]);

  // 🔥 CRÍTICO: Capturar TASK_OUTPUT para Documentos Gerados
  useEffect(() => {
    if (enhancedParserV8Tags.TASK_OUTPUT && enhancedParserV8Tags.TASK_NAME) {
      console.log('📄 [DOCUMENTOS GERADOS] Novo TASK_OUTPUT detectado:', {
        task: enhancedParserV8Tags.TASK_NAME,
        output: enhancedParserV8Tags.TASK_OUTPUT.substring(0, 100) + '...',
        type: enhancedParserV8Tags.TASK_OUTPUT_TYPE
      });

      // Detectar tipo baseado em TASK_OUTPUT_TYPE ou conteúdo
      const detectDocumentType = (output, outputType) => {
        // 1. Confiar em TASK_OUTPUT_TYPE se fornecido
        if (outputType) {
          const typeLower = outputType.toLowerCase();
          if (typeLower === 'json') {
            return { format: 'json', icon: '📊', color: '#059669' };
          } else if (typeLower === 'markdown' || typeLower === 'md') {
            return { format: 'md', icon: '📝', color: '#8b5cf6' };
          } else if (typeLower === 'csv') {
            return { format: 'csv', icon: '📈', color: '#f59e0b' };
          } else if (typeLower === 'pdf') {
            return { format: 'pdf', icon: '📕', color: '#ef4444' };
          } else if (typeLower === 'text' || typeLower === 'txt') {
            return { format: 'txt', icon: '📄', color: '#6b7280' };
          }
        }

        // 2. Fallback: Analisar conteúdo
        if (typeof output === 'string') {
          const trimmed = output.trim();

          // Check JSON (strict)
          if ((trimmed.startsWith('{') && trimmed.endsWith('}')) ||
              (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
            try {
              JSON.parse(trimmed);
              return { format: 'json', icon: '📊', color: '#059669' };
            } catch (e) {
              // Not valid JSON
            }
          }

          // Check Markdown (score-based)
          let mdScore = 0;
          if (output.includes('# ') || output.includes('## ') || output.includes('### ')) mdScore += 2;
          if (output.includes('**') || output.includes('__')) mdScore++;
          if (output.includes('```')) mdScore += 2;
          if (output.match(/\[.*\]\(.*\)/)) mdScore++; // Links
          if (output.includes('- ') || output.includes('* ') || output.match(/^\d+\./m)) mdScore++; // Lists

          if (mdScore >= 2) {
            return { format: 'md', icon: '📝', color: '#8b5cf6' };
          }

          // Check CSV
          const lines = output.split('\n').filter(l => l.trim());
          if (lines.length > 1) {
            const firstLine = lines[0];
            const secondLine = lines[1];
            const firstCommas = (firstLine.match(/,/g) || []).length;
            const secondCommas = (secondLine.match(/,/g) || []).length;
            if (firstCommas > 0 && firstCommas === secondCommas) {
              return { format: 'csv', icon: '📈', color: '#f59e0b' };
            }
          }
        }

        // 3. Default to text
        return { format: 'txt', icon: '📄', color: '#6b7280' };
      };

      const docType = detectDocumentType(enhancedParserV8Tags.TASK_OUTPUT, enhancedParserV8Tags.TASK_OUTPUT_TYPE);
      
      // Criar documento para a lista
      // FILTRO V8: Limpar TASK_NAME incorreto
      let taskNameClean = enhancedParserV8Tags.TASK_NAME || 'Documento V8';
      if (taskNameClean.includes('CrewAI team para')) {
        console.log('🚫 [DOCUMENT FILTER] TASK_NAME incorreto detectado:', taskNameClean);
        // Extrair o nome real da task (ex: "CrewAI team para 'read_email'" → "read_email")
        const match = taskNameClean.match(/'([^']+)'/);
        taskNameClean = match ? match[1] : 'Documento V8';
        console.log('✅ [DOCUMENT FILTER] TASK_NAME corrigido para:', taskNameClean);
      }
      
      const newDocument = {
        id: `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'task_completed',
        title: taskNameClean,
        agent_name: enhancedParserV8Tags.AGENT_NAME,
        tool_name: enhancedParserV8Tags.USED_TOOL,
        content: enhancedParserV8Tags.TASK_OUTPUT,
        format: docType.format,
        icon: docType.icon,
        color: docType.color,
        output_type: enhancedParserV8Tags.TASK_OUTPUT_TYPE,
        timestamp: new Date().toISOString(),
        size: enhancedParserV8Tags.TASK_OUTPUT.length
      };

      // Adicionar à lista de documentos gerados
      setOperationOutputs(prev => {
        // Evitar duplicatas - verificar se já existe um documento com mesmo conteúdo
        const exists = prev.some(doc => 
          doc.content === newDocument.content && 
          doc.title === newDocument.title
        );
        
        if (exists) {
          console.log('📄 [DOCUMENTOS GERADOS] Documento já existe, ignorando duplicata');
          return prev;
        }

        console.log('📄 [DOCUMENTOS GERADOS] Adicionando novo documento:', newDocument.title);
        return [...prev, newDocument];
      });
    }
  }, [enhancedParserV8Tags.TASK_OUTPUT, enhancedParserV8Tags.TASK_NAME, enhancedParserV8Tags.AGENT_NAME, enhancedParserV8Tags.USED_TOOL, enhancedParserV8Tags.TASK_OUTPUT_TYPE]);

  // 🔴 PAUSA ENTRE TASKS: Monitora taskCompleted e pausa execução se modo pause_per_task
  useEffect(() => {
    if (taskCompleted && execMode === 'pause_per_task') {
      console.log('⏸️ [PAUSA] Task completada - pausando execução...');

      // Pausar simulação Petri Net
      try {
        petriNetEditorRef.current?.pauseAutoSimulation();
        console.log('⏸️ [PAUSA] Simulação Petri Net pausada');
      } catch(e) {
        console.error('❌ [PAUSA] Erro ao pausar simulação:', e);
      }

      // Setar estado como pausado
      setExecutionState('paused');

      addLog('⏸️ Execução pausada - aguardando aprovação para continuar');
    }
  }, [taskCompleted, execMode]);

  // 🔴 PAUSA ENTRE TASKS V2: Monitora tag TASK_COMPLETED do enhancedParserV8Tags
  useEffect(() => {
    const taskCompletedTag = enhancedParserV8Tags.TASK_COMPLETED;

    // Detectar se task foi completada (true, "True", "true", ou qualquer valor truthy)
    const isTaskCompleted = taskCompletedTag &&
                           (taskCompletedTag === true ||
                            taskCompletedTag === 'True' ||
                            taskCompletedTag === 'true' ||
                            taskCompletedTag === 'TRUE');

    // ✅ FIX: Adicionar check approvalProcessed para evitar re-trigger após aprovação
    if (isTaskCompleted && execMode === 'pause_per_task' && !taskCompleted && !approvalProcessed) {
      console.log('⏸️ [PAUSA V2] TASK_COMPLETED tag detectada - pausando execução...', taskCompletedTag);

      // Pausar simulação Petri Net
      try {
        petriNetEditorRef.current?.pauseAutoSimulation();
        console.log('⏸️ [PAUSA V2] Simulação Petri Net pausada');
      } catch(e) {
        console.error('❌ [PAUSA V2] Erro ao pausar simulação:', e);
      }

      // Setar estado como pausado
      setExecutionState('paused');
      setTaskCompleted(true); // Ativa a caixa verde de aprovação

      addLog('⏸️ Execução pausada (TASK_COMPLETED detectada) - aguardando aprovação para continuar');
    }
  }, [enhancedParserV8Tags.TASK_COMPLETED, execMode, taskCompleted, approvalProcessed]);

  // 🔄 RESET approvalProcessed quando nova task começar
  useEffect(() => {
    // Quando TASK_NAME muda (nova task iniciou), resetar flag de aprovação
    if (enhancedParserV8Tags.TASK_NAME) {
      setApprovalProcessed(false);
      console.log('🔄 [RESET] Nova task detectada, resetando approvalProcessed');
    }
  }, [enhancedParserV8Tags.TASK_NAME]);

  // Estados para edição e mensagem ao agente
  const [editingOutput, setEditingOutput] = useState(null);
  const [editedOutputText, setEditedOutputText] = useState('');
  const [agentMessage, setAgentMessage] = useState('');

  // WebSocket V8 agora é gerenciado via CentralWSClient - removido conexão direta
  // Tags V8 são recebidas via callback do CentralWSClient registrado no initializeRealEngine

  // ETAPA 2 - Inicialização do Motor Real
  useEffect(() => {
    const initializeRealEngine = async () => {
      try {
        console.log('🎯 ETAPA 2: Inicializando Motor Real');
        
        // Carrega projeto do backend_generic
        const projectConfig = await loadProjectWithAutoConfig();
        if (!projectConfig) {
          addLog('❌ Falha ao carregar projeto do backend_generic');
          return;
        }
        
        addLog(`✅ Projeto carregado: ${projectConfig.name}`);
        addLog(`🔌 Adapter: ${projectConfig.execution_config.adapter_type}`);
        
        // ✅ WebSocket V8 é gerenciado via CentralWSClient no FakeWebSocket
        // Criar instância do CentralWSClient para ExecutionEngine
        const { CentralWSClient } = await import('./utils_exec/centralWSClient');
        const centralClient = CentralWSClient.getInstance();
        
        // Registrar callback para receber dados V8 na aba Operação
        centralClient.setOperationCallback((stepData) => {
          console.log('🔄 [EXECUTOR] Dados V8 recebidos para aba Operação:', stepData);
          handleVerboseStep(stepData.data);
          handleOperationRouting(stepData.data);
        });
        
        addLog('🌐 Sistema configurado para WebSocket V8 via CentralWSClient');
        addLog('🔗 CentralWSClient configurado para VerbosePanel e aba Operação');
        
        // Cria ExecutionEngine COM CentralWSClient para V8
        const engine = new ExecutionEngine(
          projectConfig,
          contextStateManager,
          centralClient // ✅ Passa CentralWSClient para validação
        );
        
        // Configura callbacks do motor
        engine.on('executionStarted', (config) => {
          setExecutionState('running');
          setRealTimeExecution(true);
          addLog(`🚀 Execução iniciada: ${config.name}`);
        });
        
        engine.on('placeStarted', (place) => {
          setCurrentExecutingTask(place.nome);
          addLog(`🏃 Executando Place: ${place.nome}`);
        });
        
        engine.on('placeCompleted', (place, result) => {
          addLog(`✅ Place concluído: ${place.nome}`);
          console.log('Place result:', result);
          
          // Propaga resultado para verbose steps se é uma tarefa WebSocket
          if (place.agentId && result) {
            const verboseStep = {
              step_type: 'task_completed',
              step_description: `Tarefa ${place.nome} concluída com sucesso`,
              timestamp: new Date().toISOString(),
              task_name: place.nome,
              output_data: result,
              place_id: place.id,
              agent_id: place.agentId
            };
            handleVerboseStep(verboseStep);
          }

          // Etapa 1A — Se modo pausa por tarefa, pausar e aguardar aprovação
          if (execMode === 'pause_per_task') {
            setExecutionState('paused');
            setPendingApproval({ place, result });
            addLog(`⏸️ Modo pausa: aguardando aprovação após ${place.nome}`);
          }
        });
        
        engine.on('placeError', (place, error) => {
          addLog(`❌ Erro no Place ${place.nome}: ${error.message}`);
          setExecutionState('error');
        });
        
        engine.on('executionCompleted', (history) => {
          setExecutionState('completed');
          setRealTimeExecution(false);
          setCurrentExecutingTask(null);
          addLog(`🎉 Execução concluída! ${history.length} places executados`);
        });
        
        // Valida configuração
        const validation = engine.validateConfiguration();
        if (!validation.valid) {
          addLog(`❌ Configuração inválida: ${validation.errors.join(', ')}`);
          return;
        }
        
        setExecutionEngine(engine);
        setMotorInitialized(true);
        addLog('✅ Motor Real inicializado com sucesso!');
        
        // Atualiza dados da Petri Net para visualização
        if (projectConfig.petri_net_data) {
          setPetriNetData(projectConfig.petri_net_data);
        }
        
      } catch (error) {
        console.error('❌ Erro inicializando Motor Real:', error);
        addLog(`❌ Erro no motor: ${error.message}`);
      }
    };
    
    // Inicializa apenas uma vez
    if (!motorInitialized) {
      initializeRealEngine();
    }
    
    // Cleanup WebSocket ao desmontar
    return () => {
      if (webSocketClient) {
        webSocketClient.disconnect();
      }
    };
  }, [motorInitialized, loadProjectWithAutoConfig, contextStateManager]);

  // ✨ FUNÇÕES AUXILIARES IDÊNTICAS ao testar_interface_generica_v7_md.js
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

  const addToMDSection = (sectionType, taskNum, data) => {
    const sectionMap = {
      'inputs': '📥 INPUTS SENDO USADOS',
      'execution': '⚡ EXECUÇÃO/FERRAMENTAS',
      'outputs': '📦 OUTPUTS PRODUZIDOS'
    };
    
    const taskNames = {
      1: '📧 1. READ EMAIL',
      2: '🏷️ 2. CLASSIFY MESSAGE', 
      3: '📊 3. CHECK STOCK',
      4: '📧 4. GENERATE RESPONSE'
    };

    // Verificar se já existe header da task
    const taskHeader = `## ${taskNames[taskNum]}`;
    if (!mdContent.includes(taskHeader)) {
      setMdContent(prev => prev + `${taskHeader}\n**Status:** ⚡ Executando\n**Contadores:** Inputs: 0 | Steps: 0 | Outputs: 0\n\n`);
    }

    // Verificar se já existe header da seção
    const sectionHeader = `### ${sectionMap[sectionType]}`;
    if (!mdContent.includes(sectionHeader)) {
      setMdContent(prev => prev + `${sectionHeader}\n\n`);
    }

    // Adicionar item à seção
    setMdContent(prev => prev + `**[${data.timestamp}] [${data.type}]** ${data.content}\n\n`);
  };

  // ✨ NOVA FUNÇÃO IDÊNTICA ao testar_interface_generica_v7_md.js
  const handleExecutionStep = (step) => {
    const taskName = step.task_name;
    const counter = taskCounters[taskName];
    
    if (!counter) return;

    // Atualizar counter por referência
    const taskNum = counter.task;
    
    // Processa step INPUTS
    if (step.input_data || step.step_type === 'tool_input') {
      counter.inputs++;
      const timestamp = new Date().toLocaleTimeString();
      addToMDSection('inputs', taskNum, {
        timestamp,
        type: 'INPUT DATA',
        content: formatDataForMD(step.input_data, 'json')
      });
    }

    // Processa step EXECUÇÃO  
    if (['agent_start', 'tool_usage', 'tool_executing', 'crew_start', 'task_executing'].includes(step.step_type)) {
      counter.steps++;
      const timestamp = new Date().toLocaleTimeString();
      addToMDSection('execution', taskNum, {
        timestamp,
        type: step.step_type.toUpperCase(),
        content: step.step_description
      });
    }

    // Processa step OUTPUTS
    if (step.output_data || ['tool_output','task_output','final_answer','task_completed'].includes(step.step_type)) {
      counter.outputs++;
      const timestamp = new Date().toLocaleTimeString();
      addToMDSection('outputs', taskNum, {
        timestamp,
        type: 'OUTPUT DATA',
        content: formatDataForMD(step.output_data, 'json')
      });
    }
    
    console.log(`🔷 T${taskNum}: ${step.step_type} - ${step.step_description?.substring(0, 50) || 'N/A'}`);
  };

  // ✨ NOVA FUNÇÃO IDÊNTICA ao testar_interface_generica_v7_md.js  
  const handleTaskCompleted = (taskData) => {
    const taskName = taskData.task_name;
    const counter = taskCounters[taskName];
    
    if (!counter) return;

    // Salva resultado
    setTaskResults(prev => ({
      ...prev,
      [taskName]: taskData.result
    }));

    console.log(`✅ Task ${counter.task}/4 concluída: ${taskName}`);
  };

  // Handler para processar verbose steps do WebSocket - AGORA USA LÓGICA IDÊNTICA
  const handleVerboseStep = (stepData) => {
    console.log('🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨');
    console.log('🚨🚨🚨 VERBOSE CHEGOU NO EXECUTORTAREFASNEW! 🚨🚨🚨');
    console.log('🚨🚨🚨 DADOS COMPLETOS:', stepData);
    console.log('🚨🚨🚨 TIPO:', typeof stepData);
    console.log('🚨🚨🚨 JSON:', JSON.stringify(stepData, null, 2));
    console.log('🚨🚨🚨 TIMESTAMP:', new Date().toISOString());
    console.log('🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨');
    
    console.log('🔍 Processando verbose step IDÊNTICO ao teste:', stepData);
    
    // Compatibilidade V7/V8 - adaptar campos diferentes
    const step_type = stepData.step_type || stepData.type || 'unknown_step';
    const step_description = stepData.step_description || stepData.description || stepData.content || stepData.step_name || 'No description';
    const timestamp = stepData.timestamp;
    const tool_name = stepData.tool_name;
    const input_data = stepData.input_data;
    const output_data = stepData.output_data;
    const task_name = stepData.task_name;
    const agent_name = stepData.agent_name;
    
    if (!step_type) {
      console.warn('⚠️ Dados verbose incompletos - sem step_type:', stepData);
      return;
    }

    // Adicionar aos logs
    const formattedTimestamp = timestamp || new Date().toISOString();
    const logEntry = `[${new Date(formattedTimestamp).toLocaleTimeString()}] ${step_type}: ${step_description}`;
    setLogs(prev => [...prev, logEntry]);
    
    // Criar objeto verbose step estruturado EXATAMENTE como o teste MD
    const verboseStep = {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      step_type: step_type,
      step_description: step_description,
      timestamp: formattedTimestamp,
      task_name: task_name || 'unknown',
      tool_name: tool_name || null,
      agent_name: agent_name || null,
      input_data: input_data || null,
      output_data: output_data || null,
      data: stepData
    };
    
    setVerboseSteps(prev => [...prev, verboseStep]);

    // 🔧 FIX: Cards devem permanecer visíveis após task_completed
    // Limpeza acontece APENAS quando a próxima task inicia (em handleOperationRouting linha 1257)
    if (step_type === 'task_completed' && task_name) {
      console.log(`✅ Task ${task_name} completada - dados permanecem visíveis até próxima task`);
    }

    // Classificar verbose por tipo
    if (['crew_start', 'agent_start', 'task_executing', 'task_status', 'tool_usage', 'tool_executing'].includes(step_type)) {
      setVerboseByTab(prev => ({
        ...prev,
        operacao: [...prev.operacao, verboseStep],
        execution: [...prev.execution, verboseStep]
      }));
    }

    // Logs relevantes de execução (Process steps/Task/Thought/Agent) → seção EXECUÇÃO/OPERAÇÃO
    if (step_type === 'log') {
      const desc = (step_description || '').trim();
      const isExecLog = desc.startsWith('Process steps:') || desc.startsWith('Task:') || desc.startsWith('Thought:') || desc.startsWith('Agent:');
      if (isExecLog) {
        setVerboseByTab(prev => ({
          ...prev,
          operacao: [...prev.operacao, verboseStep],
          execution: [...prev.execution, verboseStep]
        }));
      }
    }
    
    if (step_type === 'tool_input') {
      setVerboseByTab(prev => ({
        ...prev,
        inputs: [...prev.inputs, verboseStep],
        operacao: [...prev.operacao, verboseStep],
        execution: [...prev.execution, verboseStep]
      }));
    }
    
    if (['tool_output', 'final_answer', 'task_output', 'task_completed'].includes(step_type)) {
      setVerboseByTab(prev => ({
        ...prev,
        outputs: [...prev.outputs, verboseStep],
        operacao: [...prev.operacao, verboseStep],
        execution: [...prev.execution, verboseStep]
      }));
    }
  };

  // Adicionar log
  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  // Funções para ETAPA 6 - Inputs
  const handleFileUpload = (placeId, externalInputId) => {
    addLog(`📁 Configurando upload para place ${placeId}: ${externalInputId}`);
    // Simula upload de arquivo
    const timestamp = Date.now();
    const fileName = `${externalInputId}_${timestamp}.pdf`;
    setUploadedFiles(prev => ({
      ...prev,
      [`${placeId}_${externalInputId}`]: {
        fileName,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded'
      }
    }));
    addLog(`✅ Arquivo carregado: ${fileName}`);
  };

  const openConfigModal = (placeId, externalInputId, configType) => {
    addLog(`🔗 Configurando ${configType} para place ${placeId}: ${externalInputId}`);
    // Aqui poderia abrir um modal real de configuração
  };

  const getInputsFromWebSocket = (placeId) => {
    // Retorna inputs gerados entre tarefas baseados nos dados do WebSocket
    return verboseByTab.inputs.filter(input => 
      input.task_name === placeId || input.target_task === placeId
    );
  };

  const isExternalInputConfigured = (placeId, externalInputId) => {
    return uploadedFiles[`${placeId}_${externalInputId}`] !== undefined;
  };

  // Estados para ETAPA 7 - Execution
  const [executionMode, setExecutionMode] = useState('auto'); // 'auto' | 'step'
  const [transitionStates, setTransitionStates] = useState({});
  const [transitionRefs, setTransitionRefs] = useState({});
  const [placeRefs, setPlaceRefs] = useState({});
  
  // Estados para tarefa centralizada (seguindo padrão AgentsModule1Page)
  const [currentExecutingTask, setCurrentExecutingTask] = useState(null);
  const [executionProgress, setExecutionProgress] = useState(0);
  const [executingSteps, setExecutingSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(null);

  // Componente TransitionBox (ETAPA 7)
  const TransitionBox = ({ transitionId, name, status, onClick, wasInConflict }) => {
    const getStatusColor = () => {
      switch (status) {
        case 'firing': return '#f59e0b'; // Amarelo - executando
        case 'fired': return '#10b981'; // Verde - concluído  
        case 'enabled': return '#3b82f6'; // Azul - habilitado
        case 'rejected': return '#ef4444'; // Vermelho - rejeitado
        default: return '#6b7280'; // Cinza - idle
      }
    };

    return (
      <div
        onClick={onClick}
        style={{
          padding: '12px 16px',
          background: getStatusColor(),
          color: 'white',
          borderRadius: '8px',
          fontSize: '12px',
          fontWeight: '600',
          textAlign: 'center',
          cursor: onClick ? 'pointer' : 'default',
          minWidth: '160px',
          border: wasInConflict ? '2px solid #fbbf24' : 'none',
          transition: 'all 0.3s ease',
          transform: status === 'firing' ? 'scale(1.1) translateY(-5px)' : 'scale(1)', // Animação de "pulo"
          boxShadow: status === 'firing' ? '0 8px 16px rgba(0,0,0,0.3)' : '0 2px 4px rgba(0,0,0,0.1)'
        }}
      >
        {name}
        <div style={{ fontSize: '10px', marginTop: '4px', opacity: 0.8 }}>
          {transitionId}
        </div>
      </div>
    );
  };

  // Componente SimpleArrow (ETAPA 7)
  const SimpleArrow = ({ direction = 'down', color = 'blue', animated = false }) => {
    const getArrowStyle = () => {
      const baseStyle = {
        width: '20px',
        height: '20px',
        margin: '8px auto',
        transition: 'all 0.5s ease'
      };

      if (animated) {
        baseStyle.animation = 'pulse 1s infinite';
        baseStyle.transform = 'scale(1.2)';
      }

      return baseStyle;
    };

    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={getArrowStyle()}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M10 2L10 18M10 18L4 12M10 18L16 12"
              stroke={color}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </div>
    );
  };

  // Componente AgentPlace para ETAPA 7
  const AgentPlace = ({ place, showDetails = true }) => {
    const getStatusColor = () => {
      switch (place.status) {
        case 'completed': return { bg: 'rgba(16, 185, 129, 0.1)', border: '#10b981' };
        case 'running': return { bg: 'rgba(59, 130, 246, 0.1)', border: '#3b82f6' };
        case 'error': return { bg: 'rgba(239, 68, 68, 0.1)', border: '#ef4444' };
        default: return { bg: 'rgba(156, 163, 175, 0.1)', border: '#9ca3af' };
      }
    };

    const colors = getStatusColor();
    const wsInputs = getInputsFromWebSocket(place.id);
    const wsOutputs = verboseByTab.outputs.filter(o => o.task_name === place.id);
    const wsExecution = verboseByTab.execution.filter(e => e.task_name === place.id);

    return (
      <div style={{
        background: colors.bg,
        border: `2px solid ${colors.border}`,
        borderRadius: '12px',
        padding: '16px',
        minWidth: '320px',
        maxWidth: '400px',
        transition: 'all 0.3s ease',
        transform: place.status === 'running' ? 'scale(1.02)' : 'scale(1)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--foreground)' }}>
              {place.name}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--muted-foreground)' }}>
              {place.id} • {place.agent}
            </div>
          </div>
          <div style={{
            padding: '4px 8px',
            background: colors.border,
            color: 'white',
            borderRadius: '12px',
            fontSize: '10px',
            fontWeight: '600'
          }}>
            {place.status.toUpperCase()}
          </div>
        </div>

        {showDetails && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
            {/* Inputs */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: '600', marginBottom: '6px', color: 'var(--muted-foreground)' }}>
                📥 INPUTS ({wsInputs.length})
              </div>
              <div style={{ background: 'var(--secondary)', borderRadius: '6px', padding: '8px', minHeight: '30px' }}>
                {wsInputs.length > 0 ? (
                  wsInputs.slice(-2).map(input => (
                    <div key={input.id} style={{ fontSize: '10px', marginBottom: '4px', color: 'var(--muted-foreground)' }}>
                      • {safeStringify(input.description).substring(0, 40)}...
                    </div>
                  ))
                ) : (
                  <div style={{ fontSize: '10px', color: 'var(--muted-foreground)', textAlign: 'center' }}>
                    Aguardando inputs...
                  </div>
                )}
              </div>
            </div>

            {/* Execution */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: '600', marginBottom: '6px', color: 'var(--muted-foreground)' }}>
                ⚙️ EXECUTION ({wsExecution.length})
              </div>
              <div style={{ background: 'var(--secondary)', borderRadius: '6px', padding: '8px', minHeight: '30px' }}>
                {wsExecution.length > 0 ? (
                  wsExecution.slice(-2).map(exec => (
                    <div key={exec.id} style={{ fontSize: '10px', marginBottom: '4px', color: 'var(--muted-foreground)' }}>
                      • {exec.type}: {safeStringify(exec.description).substring(0, 35)}...
                    </div>
                  ))
                ) : (
                  <div style={{ fontSize: '10px', color: 'var(--muted-foreground)', textAlign: 'center' }}>
                    Aguardando execução...
                  </div>
                )}
              </div>
            </div>

            {/* Outputs */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: '600', marginBottom: '6px', color: 'var(--muted-foreground)' }}>
                📦 OUTPUTS ({wsOutputs.length})
              </div>
              <div style={{ background: 'var(--secondary)', borderRadius: '6px', padding: '8px', minHeight: '30px' }}>
                {wsOutputs.length > 0 ? (
                  wsOutputs.slice(-2).map(output => (
                    <div key={output.id} style={{ fontSize: '10px', marginBottom: '4px', color: 'var(--muted-foreground)' }}>
                      • {safeStringify(output.description).substring(0, 35)}...
                    </div>
                  ))
                ) : (
                  <div style={{ fontSize: '10px', color: 'var(--muted-foreground)', textAlign: 'center' }}>
                    Aguardando outputs...
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // ETAPA 2 - Funções de controle do Motor Real
  const executeAllTasks = async () => {
    if (!motorInitialized || !executionEngine) {
      addLog('⚠️ Motor Real não inicializado');
      return;
    }
    
    try {
      addLog('🚀 Iniciando execução REAL do fluxo');
      setRealExecutionMode(true);
      
      // 🧹 LIMPAR ESTADOS ANTES DE INICIAR NOVA EXECUÇÃO
      clearAllStates();
      
      // ✨ ATIVAR VerbosePanel automaticamente - CORRIGIDO  
      console.log('🔥 DEBUG: executeAllTasks - ATIVANDO VerbosePanel!');
      setVerbosePanelVisible(true);
      
      // ⏰ Aguardar um pouco para garantir que limpeza foi processada
      await new Promise(resolve => setTimeout(resolve, 100));
      setVerboseSteps([]); // Limpar verbose steps anteriores
      
      // ✨ INICIALIZAR MD CONTENT IDÊNTICO ao testar_interface_generica_v7_md.js
      const now = new Date().toLocaleString();
      setMdContent(`# ACOMPANHAMENTO DE EXECUÇÃO - INPUTS/EXECUÇÃO/OUTPUTS

**Data:** ${now}
**WebSocket:** ws://localhost:6308
**Adapter:** TropicalSalesAdapter
**Parser:** CrewAIStructuredParser V1

---

## 🎯 TASKS DISPONÍVEIS

1. **📧 READ EMAIL** - Ler e processar emails
2. **🏷️ CLASSIFY MESSAGE** - Classificar mensagens  
3. **📊 CHECK STOCK** - Verificar estoque
4. **📧 GENERATE RESPONSE** - Gerar resposta

---

## 🚀 EXECUÇÃO EM TEMPO REAL

Iniciando execução via ExecutionEngine...`);
      
      // Executa usando ExecutionEngine real
      await executionEngine.startExecution();
      
    } catch (error) {
      addLog(`❌ Erro na execução: ${error.message}`);
      console.error('Erro execução:', error);
    }
  };
  
  // Função para executar por etapas
  const executeNextStep = async () => {
    if (!motorInitialized || !executionEngine) {
      addLog('⚠️ Motor Real não inicializado');
      return;
    }
    
    addLog('👆 Modo passo-a-passo não implementado ainda');
    // TODO: Implementar execução step-by-step
  };

  // Funções de reset e parar
  const resetExecution = async () => {
    if (executionEngine) {
      await executionEngine.resetExecution();
      setRealExecutionMode(false);
      setCurrentExecutingTask(null);
      addLog('🔄 Execução resetada');
    }
  };
  
  const stopExecution = async () => {
    if (executionEngine) {
      await executionEngine.stopExecution();
      setRealExecutionMode(false);
      setCurrentExecutingTask(null);
      addLog('⏹️ Execução parada');
    }
  };


  const resumeExecution = async () => {
    if (executionEngine) {
      await executionEngine.resumeExecution();
      addLog('▶️ Execução resumida');
      setExecutionState('running');
      setPendingApproval(null);
    }
  };

  // Handlers de aprovação/ressubmissão (Etapa 1A)
  const handleApproveAndContinue = () => {
    addLog('✅ Aprovado pelo usuário. Continuando execução...');
    setTaskCompleted(false);
    setApprovalProcessed(true); // ✅ FIX: Marcar como processado para evitar re-trigger
    setPendingApproval(null);
    setExecutionState('running');

    // ✅ FIX: Limpar estados de tarefa e agente anteriores
    setCurrentTaskName('');
    setCurrentAgentName('');

    // ✅ FIX: Limpar tags da tarefa anterior para mostrar "Aguardando tarefa..."
    setEnhancedParserV8Tags(prev => ({
      ...prev,
      TASK_NAME: null,
      AGENT_NAME: null,
      TASK_INPUT: null,
      TASK_OUTPUT: null,
      TASK_OUTPUT_TYPE: null,
      USED_TOOL: null,
      TOOL_INPUT: null,
      TASK_STEP: null,
      TOOL_OUTPUT: null,
      AGENT_THOUGHT: null
    }));

    // Retomar caminho do ExecutionEngine (se ativo)
    resumeExecution();
    // Retomar simulação automática (se ativo)
    try { petriNetEditorRef.current?.resumeAutoSimulation(); } catch(e) { /* noop */ }
  };

  const handleResubmitTask = () => {
    addLog('🔁 Re-submeter tarefa atual (ajuste de inputs pode ser necessário)');
    setTaskCompleted(false);
    setPendingApproval(null);
    // TODO: abrir modal de ajuste de inputs e reexecutar place específico
    resumeExecution();
    try { petriNetEditorRef.current?.resumeAutoSimulation(); } catch(e) { /* noop */ }
  };

  // 🔄 Handler para Refazer Execução (zera tudo e reinicia)
  const handleRefazerExecucao = async () => {
    addLog('🔄 Refazendo execução - zerando todos os dados e reiniciando...');

    // Limpar todos os estados
    setLogs([]);
    setOperationOutputs([]);
    setOperationSteps([]);
    setAgentMessage('');
    setTaskCompleted(false);
    setApprovalProcessed(false); // ✅ FIX: Resetar flag para permitir nova pausa
    setPendingApproval(null);
    setVerboseSteps([]);

    // Limpar cache do WebSocket
    const centralClient = CentralWSClient.getInstance();
    centralClient.clearResults();

    // Enviar comando iniciar_execucao para limpar arquivos no backend
    centralClient.sendGenericCommand('iniciar_execucao', {
      timestamp: new Date().toISOString(),
      session_type: 'tropical_sales_refazer_execution'
    });

    // Reiniciar simulação da Petri Net
    try {
      petriNetEditorRef.current?.resetSimulation();
      petriNetEditorRef.current?.startAutoSimulation();
      addLog('✅ Execução reiniciada com sucesso');
    } catch(e) {
      console.error('Erro ao reiniciar simulação:', e);
      addLog('⚠️ Erro ao reiniciar simulação - verifique a Petri Net');
    }
  };

  // Funções do modal de edição de output
  const openEditOutput = (output) => {
    console.log('🔥 Abrindo output para edição:', output);
    setEditingOutput(output);
    setEditedOutputText(output.content || safeStringify(output.output_data || output.description || ''));
    setShowEditOutputModal(true);
  };

  const closeEditModal = () => {
    setShowEditOutputModal(false);
    setEditingOutput(null);
    setEditedOutputText('');
  };

  const saveEditedOutput = () => {
    console.log('💾 Salvando output editado:', editedOutputText.substring(0, 100) + '...');
    if (editingOutput) {
      // Atualizar o output na lista
      setOperationOutputs(prev =>
        prev.map(output =>
          output.id === editingOutput.id
            ? { ...output, content: editedOutputText }
            : output
        )
      );
      addLog(`✅ Output "${editingOutput.title || editingOutput.tool_name}" foi editado e salvo`);
    }
    closeEditModal();
  };

  // 💾 Função para salvar documento no filesystem
  const saveOutputToFile = async (output) => {
    console.log('💾 Salvando documento no filesystem:', output.title);
    addLog(`📁 Salvando documento: ${output.title}`);

    try {
      const filename = `${output.title}.${output.format}`;

      const response = await fetch('http://localhost:8000/api/save-output', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: filename,
          content: output.content,
          type: output.format.toUpperCase()
        })
      });

      const result = await response.json();

      if (result.success) {
        addLog(`✅ Documento salvo: ${filename}`);
        console.log('✅ Documento salvo com sucesso:', result.path);
        alert(`✅ Documento salvo com sucesso!\n\nArquivo: ${filename}\nLocal: ${result.path}`);
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('❌ Erro ao salvar documento:', error);
      addLog(`❌ Erro ao salvar: ${error.message}`);
      alert(`❌ Erro ao salvar documento:\n${error.message}`);
    }
  };

  // 🧹 Função para limpar estado entre tasks
  const clearAllStates = () => {
    console.log('🧹 [CLEAR STATES] Limpando todos os estados para nova execução...');
    
    // Limpar Enhanced Parser V8 Tags
    console.log('🔧 [CLEAR STATES] Limpando Enhanced Parser V8 Tags...');
    console.log('📊 [CLEAR STATES] Estados antes da limpeza:', {
      TOOL_INPUT: enhancedParserV8Tags.TOOL_INPUT ? 'presente' : 'null',
      TASK_OUTPUT: enhancedParserV8Tags.TASK_OUTPUT ? 'presente' : 'null',
      operationOutputsCount: operationOutputs.length
    });
    
    setEnhancedParserV8Tags({
      TASK_NAME: null,
      AGENT_NAME: null, 
      TASK_INPUT: null,
      TOOL_INPUT: null,
      USED_TOOL: null,
      TASK_STEP: null,
      TASK_OUTPUT: null,
      TASK_OUTPUT_TYPE: null
    });
    
    console.log('✅ [CLEAR STATES] Enhanced Parser V8 Tags limpos');
    
    // Limpar Documentos Gerados
    console.log('📄 [CLEAR STATES] Limpando Documentos Gerados...');
    console.log('📊 [CLEAR STATES] Documentos antes da limpeza:', operationOutputs.length);
    setOperationOutputs([]);
    console.log('✅ [CLEAR STATES] Documentos Gerados limpos');

    // Limpar Verbose da Aba Operação - 🔧 FIX: Manter todos os campos como arrays
    setVerboseByTab({ operacao: [], inputs: [], execution: [], outputs: [], logs: [] });
    
    // Limpar outros estados da operação
    setOperationInputs([]);
    setOperationSteps([]);
    
    // Limpar verbose steps
    setVerboseSteps([]);
    
    // Limpar VerbosePanel se disponível
    if (typeof window !== 'undefined' && window.__clearVerbosePanel) {
      window.__clearVerbosePanel();
    }
    
    // Log de confirmação
    addLog('🧹 Estados limpos para nova execução');
    console.log('✅ [CLEAR STATES] Limpeza completa realizada');
  };

  // Expor função de limpeza globalmente para uso manual
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.__clearAllStates = clearAllStates;
      console.log('🧹 [EXECUTOR] Função clearAllStates exposta globalmente: window.__clearAllStates()');
    }
    
    return () => {
      delete window.__clearAllStates;
    };
  }, []);


  // 📝 Função para renderizar markdown simples
  const renderSimpleMarkdown = (content) => {
    if (!content || typeof content !== 'string') return content;
    
    let html = content
      // Headers
      .replace(/^### (.*$)/gm, '<h3 style="margin: 8px 0 4px 0; font-size: 12px; font-weight: 600; color: #374151;">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 style="margin: 10px 0 6px 0; font-size: 13px; font-weight: 600; color: #374151;">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 style="margin: 12px 0 8px 0; font-size: 14px; font-weight: 700; color: #374151;">$1</h1>')
      
      // Bold text
      .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>')
      
      // Italic text  
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      // Lists
      .replace(/^- (.*$)/gm, '<li style="margin: 2px 0; list-style-type: disc; margin-left: 16px;">$1</li>')
      .replace(/^\* (.*$)/gm, '<li style="margin: 2px 0; list-style-type: disc; margin-left: 16px;">$1</li>')
      
      // Code blocks
      .replace(/```(.*?)```/gs, '<pre style="background: #f3f4f6; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 10px; margin: 4px 0; overflow-x: auto;">$1</pre>')
      
      // Inline code
      .replace(/`(.*?)`/g, '<code style="background: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 10px;">$1</code>')
      
      // Line breaks
      .replace(/\n/g, '<br>');
    
    return <div dangerouslySetInnerHTML={{ __html: html }} />;
  };

  // 💾 Função para salvar documento em arquivo
  const saveDocumentToFile = (document) => {
    console.log('💾 [SAVE] Salvando documento:', document.title);
    
    try {
      const content = document.content || '';
      const filename = `${document.title || 'documento'}.${document.format || 'txt'}`;
      const mimeTypes = {
        'json': 'application/json',
        'md': 'text/markdown',
        'csv': 'text/csv',
        'txt': 'text/plain'
      };
      const mimeType = mimeTypes[document.format] || 'text/plain';
      
      // Criar blob e download
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      addLog(`📁 Documento "${filename}" salvo com sucesso (${Math.floor(content.length/1024)}KB)`);
      
    } catch (error) {
      console.error('❌ Erro ao salvar documento:', error);
      addLog(`❌ Erro ao salvar documento: ${error.message}`);
    }
  };

  // Tornar handlers disponíveis ao SimulationPanel via janela (atalho não-invasivo)
  useEffect(() => {
    window.__onApproveAndContinue = handleApproveAndContinue;
    window.__onResubmitTask = handleResubmitTask;
    return () => {
      try { delete window.__onApproveAndContinue; } catch (e) {}
      try { delete window.__onResubmitTask; } catch (e) {}
    };
  }, [handleApproveAndContinue, handleResubmitTask]);


  const handleTransitionClick = (transitionId) => {
    addLog(`🎯 Transição clicada: ${transitionId}`);
    // Aqui se integrará com o PetriNetEngine para disparar transição específica
  };

  // Função para extrair transições da Petri Net (ETAPA 7)
  const getTransitionsFromPetriNet = () => {
    if (!petriNetData || !petriNetData.transicoes) return [];
    
    return petriNetData.transicoes.map(transition => ({
      id: transition.id,
      name: transition.nome || `Transição ${transition.id}`,
      status: transitionStates[transition.id] || 'idle',
      coordinates: transition.coordenadas
    }));
  };

  // Função para gerar sequência visual da Petri Net (ETAPA 7)
  const generatePetriNetSequence = () => {
    const places = getTaskPlacesFromPetriNet();
    const transitions = getTransitionsFromPetriNet();
    
    if (places.length === 0) return null;

    // Para Tropical Sales: P1 → T1 → P2 → T2 → P3 → T3 → P4 → T4 → P5
    return places.map((place, index) => ({
      place,
      transition: transitions[index],
      hasNext: index < places.length - 1
    }));
  };
  
  // Função de teste para verbose
  const testarVerboseParser = () => {
    console.log('🧪 TESTANDO Verbose Parser...');
    
    const testSteps = [
      {
        step_type: 'crew_start',
        step_description: 'Inicializando crew de vendas tropical',
        timestamp: new Date().toISOString(),
        task_name: 'read_email'
      },
      {
        step_type: 'tool_input',
        step_description: 'Recebendo input para ferramenta de classificação',
        timestamp: new Date().toISOString(),
        tool_name: 'email_classifier',
        input_data: { email_content: 'Olá, tenho interesse em frutas tropicais' },
        task_name: 'read_email'
      },
      {
        step_type: 'tool_usage',
        step_description: 'Executando classificação de mensagem',
        timestamp: new Date().toISOString(),
        tool_name: 'message_classifier',
        task_name: 'classify_message'
      },
      {
        step_type: 'tool_output',
        step_description: 'Classificação concluída com sucesso',
        timestamp: new Date().toISOString(),
        tool_name: 'message_classifier',
        output_data: { category: 'product_inquiry', confidence: 0.95 },
        task_name: 'classify_message'
      },
      {
        step_type: 'task_completed',
        step_description: 'Tarefa de classificação finalizada',
        timestamp: new Date().toISOString(),
        task_name: 'classify_message'
      }
    ];
    
    testSteps.forEach((step, index) => {
      setTimeout(() => {
        console.log(`🎯 Simulando step ${index + 1}:`, step.step_type);
        handleVerboseStep(step);
      }, index * 1000);
    });
    
    console.log('✅ Teste do parser iniciado (5 steps simulados)');
  };

  // Roteamento para a aba Operação (Etapa 2)
  const pushOperationItem = (arrSetter, item) => {
    arrSetter(prev => [...prev, { ...item, id: item.id || `op_${Date.now()}_${Math.random()}` }]);
  };

  // Função para limpeza completa dos cards
  const clearOperationCards = () => {
    setOperationInputs([]);
    setOperationSteps([]);
    setOperationOutputs([]);
    setTaskCompleted(false);
    setOperationTaskProgress(0);
    setCurrentAgentName('');
    // 🔧 FIX CRÍTICO: NÃO zerar enhancedParserV8Tags aqui!
    // Tags vêm do WebSocket e devem permanecer até serem substituídas pelas novas
    // O merge é controlado no CentralWSClient
    console.log('🧹 [CLEAR] Arrays resetados (tags permanecem)');
  };

  const handleOperationRouting = (step) => {
    const t = (step.step_type || '').toLowerCase();
    const stepTask = step.task_name || step.place_id || step.task || null;
    const stepAgent = step.agent_name || null;

    // 🔍 DEBUG: Log all incoming steps
    console.log(`📍 [ROUTING] step_type="${t}", task="${stepTask}", agent="${stepAgent}"`, step);

    // 🔧 FIX: Detect task changes ONLY on specific start types, not on every step
    // Avoid clearing on every tag that comes with task_name
    const isTaskStartStep = ['task_detection', 'agent_started', 'crew_start', 'task_executing'].includes(t);
    if (isTaskStartStep && stepTask && currentTaskName !== stepTask) {
      clearOperationCards();
      setCurrentTaskName(stepTask);
      console.log('🔥 Nova tarefa detectada:', stepTask, 'Agente:', stepAgent);
    }

    // 🔧 FIX: Capture agent name whenever available
    if (stepAgent && (!currentAgentName || stepTask === currentTaskName)) {
      setCurrentAgentName(stepAgent);
      console.log('🤖 Agente detectado:', stepAgent, 'para tarefa:', stepTask);
    }

    // === INPUTS SECTION ===
    // 🔧 FIX: Condições MAIS PERMISSIVAS para capturar qualquer step com input_data
    // Enhanced Parser V10 step types: task_input_detection, tool_input
    const isInputStep = (
      t === 'tool_input' ||
      t === 'task_input' ||
      t === 'task_input_detection' || // ⭐ V10 Enhanced Parser
      t.includes('input') ||
      step.input_data !== undefined // ⚠️ Captura QUALQUER step com input_data, mesmo que vazio
    );

    // === OUTPUTS SECTION ===
    // 🔧 FIX: Condições MAIS PERMISSIVAS para capturar qualquer step com output_data
    // Enhanced Parser V10 step types: tool_output, task_result, task_completed
    const isOutputStep = (
      ['tool_output','task_output','task_completed','task_result'].includes(t) ||
      t.includes('output') ||
      t.includes('result') ||
      t.includes('completed') || // ⚠️ Captura task_completed
      step.output_data !== undefined // ⚠️ Captura QUALQUER step com output_data, mesmo que vazio
    );

    // === EXECUTION SECTION ===
    // 🔧 FIX: Condições MAIS PERMISSIVAS incluindo todos os V10 Enhanced Parser types
    // Enhanced Parser V10 step types: box_start, task_detection, agent_started, tool_execution
    const isExecutionStep = (
      ['box_start','task_detection','agent_started','tool_execution', // ⭐ V10 Enhanced Parser
       'crew_start','task_executing','agent_start','tool_usage','tool_executing','task_status',
       'execution_step','task_step','agent_thinking','tool_start','tool_end',
       'agent_thought','thinking','processing'].includes(t) || // ⚠️ Adicionado agent_thought, thinking, processing
      (t === 'log' && /^(Process steps:|Task:|Thought:|Agent:)/.test(step.step_description || '')) ||
      step.step_description !== undefined || // ⚠️ Captura QUALQUER step com step_description
      (!isInputStep && !isOutputStep) // Fallback
    );

    // 🔍 DEBUG: Log detalhado das condições
    console.log(`🔍 [ROUTING DEBUG] step_type="${t}"`, {
      isInputStep,
      isOutputStep,
      isExecutionStep,
      hasInputData: !!step.input_data,
      hasOutputData: !!step.output_data,
      stepDescription: step.step_description?.substring(0, 50) || 'N/A'
    });

    if (isInputStep) {
      console.log('📥 [INPUT] Adicionando a operationInputs:', t);
      pushOperationItem(setOperationInputs, {
        type: t,
        title: step.tool_name || step.step_description || 'Task Input',
        content: safeStringify(step.input_data || step.step_description || step.content || ''),
        timestamp: step.timestamp || new Date().toISOString(),
        agent: step.agent_name || ''
      });
      return;
    }

    if (isOutputStep) {
      console.log('📤 [OUTPUT] Adicionando a operationOutputs:', t);
      let display = '';
      if (step.output_data) {
        if (typeof step.output_data === 'string') {
          try { display = JSON.stringify(JSON.parse(step.output_data), null, 2); }
          catch { display = step.output_data; }
        } else if (typeof step.output_data === 'object') {
          display = JSON.stringify(step.output_data, null, 2);
        } else {
          display = String(step.output_data);
        }
      } else {
        display = safeStringify(step.step_description || step.content || '');
      }

      // ❌ DESABILITADO: Apenas useEffect de TASK_OUTPUT deve adicionar a Documentos Gerados
      // pushOperationItem(setOperationOutputs, {
      //   type: t,
      //   title: step.tool_name || (t === 'task_output' ? 'Task Output' : t),
      //   content: display,
      //   timestamp: step.timestamp || new Date().toISOString(),
      //   agent: step.agent_name || '',
      //   format: (typeof step.output_data === 'object' ? 'json' : 'text')
      // });

      if (t === 'task_completed') {
        setTaskCompleted(true);
        setOperationTaskProgress(100);
      }
      return;
    }

    if (isExecutionStep) {
      console.log('⚙️ [EXECUTION] Adicionando a operationSteps:', t);

      // Extrair título significativo baseado no tipo de step
      let title = step.tool_name;
      if (!title) {
        if (t === 'final_answer') {
          title = 'Final Answer';
        } else if (t === 'tool_input') {
          title = 'Tool Input';
        } else if (t === 'tool_output') {
          title = 'Tool Output';
        } else if (step.content) {
          title = safeStringify(step.content).substring(0, 50);
        } else {
          title = '';
        }
      }

      pushOperationItem(setOperationSteps, {
        type: t,
        title: title,
        content: safeStringify(step.content || step.step_description || ''),
        timestamp: step.timestamp || new Date().toISOString(),
        agent: step.agent_name || '',
        tool: step.tool_name || ''
      });
      return;
    }

    console.warn('⚠️ [ROUTING] Step não roteado:', t, step);
  };

  // Inicializar com dados do projeto
  useEffect(() => {
    console.log('🔄 USEEFFECT EXECUTADO - Recebendo projeto:', project);
    
    // Configurar ponte para VerbosePanel → Operação
    window.__routeOperationStep = handleOperationRouting;
    
    if (!project || !project.project_data) {
      console.log('❌ NENHUM PROJETO ou PROJECT_DATA encontrado:', {
        project: !!project,
        hasProjectData: !!(project?.project_data),
        projectKeys: project ? Object.keys(project) : 'N/A'
      });
      addLog('❌ Erro: Nenhum projeto ou dados de projeto encontrados');
      return;
    }
    
    if (project && project.project_data) {
      try {
        console.log('✅ PROJETO VÁLIDO - Processando dados...');
        console.log('project_data tipo:', typeof project.project_data);
        console.log('project_data conteúdo:', project.project_data);
        
        let projectData = typeof project.project_data === 'string' 
          ? JSON.parse(project.project_data) 
          : project.project_data;

        // 🔧 Normalização diagnóstica: alinhar WS e aumentar timeout de read_email
        try {
          if (projectData?.lugares?.length) {
            projectData = {
              ...projectData,
              lugares: projectData.lugares.map(pl => {
                if (typeof pl.logica === 'string') {
                  let newLogic = pl.logica;
                  // Alinhar porta do WS
                  newLogic = newLogic.replaceAll('ws://localhost:6306', 'ws://localhost:6308');
                  // Se a lógica é do read_email, aumentar timeout local (30s -> 90s)
                  if (/read_email/.test(newLogic) && /setTimeout\s*\(/.test(newLogic)) {
                    // Substituir apenas timeouts de 30000ms por 90000ms
                    newLogic = newLogic.replace(/(setTimeout\s*\(.*?,\s*)30000(\s*\))/g, '$190000$2');
                  }
                  return { ...pl, logica: newLogic };
                }
                return pl;
              })
            };
          }
        } catch (e) {
          console.warn('⚠️ Falha ao normalizar lógica dos places:', e);
        }
        
        console.log('📊 DADOS PROCESSADOS:', projectData);
        console.log('Inicializando projeto:', project.name);
        setPetriNetData(projectData);
        
        // Criar engine
        const engine = new PetriNetEngine(projectData);
        
        // Callbacks
        engine.setCallbacks({
          onPlaceExecute: (placeId, place) => {
            setTaskStates(prev => ({
              ...prev,
              [placeId]: { ...prev[placeId], status: 'running', ...place }
            }));
          },
          onTransitionFire: (transitionId) => {
            addLog(`Transição ${transitionId} disparada`);
          },
          onExecutionComplete: (summary) => {
            setExecutionSummary(summary);
            setExecutionState('completed');
            addLog('Execução completada');
          },
          onLog: (logEntry) => {
            setLogs(prev => [...prev, logEntry]);
          }
        });
        
        setPetriNetEngine(engine);
        
        // Inicializar task states
        if (projectData.lugares) {
          const tasks = {};
          projectData.lugares.forEach(place => {
            tasks[place.id] = {
              id: place.id,
              name: place.nome,
              agent: place.agentId || 'Sistema',
              status: TASK_STATUS.PENDING,
              tokens: place.tokens || 0,
              inputs: place.inputs || [],
              outputs: [],
              executionTime: 0,
              isTask: !!place.agentId
            };
          });
          setTaskStates(tasks);
        }
        
      } catch (error) {
        console.error('❌ ERRO ao inicializar:', error);
        addLog(`Erro: ${error.message}`);
      }
    } else {
      console.log('❌ PROJETO INVÁLIDO ou SEM project_data:', {
        project: !!project,
        hasProjectData: !!(project?.project_data),
        projectKeys: project ? Object.keys(project) : 'N/A'
      });
    }
  }, [project]);

  // ETAPA 2 - Controles de execução unificados
  const startExecution = () => {
    console.log('🎯 BOTÃO INICIAR CLICADO');
    console.log('🔍 DEBUG Estados:', {
      realExecutionMode,
      motorInitialized,
      petriNetEngine: !!petriNetEngine,
      petriNetData: !!petriNetData
    });
    
    // ✨ MOSTRAR VerbosePanel automaticamente quando execução inicia
    console.log('🔥 DEBUG: ATIVANDO VerbosePanel agora!');
    setVerbosePanelVisible(true);
    console.log('🔥 DEBUG: verbosePanelVisible deveria estar TRUE agora!');
    setVerboseSteps([]); // Limpar verbose steps anteriores
    
    // ⭐ V10: WEBSOCKET GENERICS - IDÊNTICO ao testar_interface_generica_v10_md.js
    console.log('🌐 [V10] Enviando comando inicial: iniciar_execucao');
    const centralClient = CentralWSClient.getInstance();

    // CRÍTICO: Limpar cache ANTES de nova execução (idêntico ao testar_interface)
    centralClient.clearResults();
    console.log('🧹 [V10] Cache de resultados limpo para nova execução');

    // 🧹 Limpar documentos gerados e mensagem ao agente
    setOperationOutputs([]);
    setAgentMessage('');
    console.log('🧹 [V10] Documentos gerados e mensagem ao agente limpos');

    // CRÍTICO: Comando genérico para inicializar sessão WebSocket V10
    centralClient.sendGenericCommand('iniciar_execucao', {
      timestamp: new Date().toISOString(),
      session_type: 'tropical_sales_full_execution'
    });

    // ✨ INICIALIZAR MD CONTENT IDÊNTICO ao testar_interface_generica_v10_md.js
    const now = new Date().toLocaleString();
    setMdContent(`# ACOMPANHAMENTO DE EXECUÇÃO - INPUTS/EXECUÇÃO/OUTPUTS

**Data:** ${now}
**WebSocket:** ws://localhost:6308
**Adapter:** TropicalSalesAdapterV10
**Parser:** Enhanced Parser V10 (10 Universal Tags)

---

## 🎯 TASKS DISPONÍVEIS

1. **📧 READ EMAIL** - Ler e processar emails
2. **🏷️ CLASSIFY MESSAGE** - Classificar mensagens
3. **📊 CHECK STOCK** - Verificar estoque
4. **📧 GENERATE RESPONSE** - Gerar resposta

---

## 🚀 EXECUÇÃO EM TEMPO REAL

`);

    addLog('🔍 VerbosePanel aberto para acompanhar execução em tempo real');
    addLog('🌐 [V10] Comando iniciar_execucao enviado via WebSocket generic');
    
    // Execução deve acionar o mesmo fluxo do PetriNetEditor + SimulationPanel (auto)
    if (!petriNetData) {
      addLog('⚠️ Petri Net não carregada. Aguarde o projeto inicializar.');
      console.warn('⚠️ Petri Net não carregada.');
      return;
    }
    // Garantir visualizador aberto; somente iniciar quando editor sinalizar pronto
    if (!petriNetExpanded) {
      // Abrir editor e aguardar onDataLoad
      setEditorReady(false);
      setStartPending(true);
      setPetriNetExpanded(true);
      return;
    }
    if (!editorReady) {
      setStartPending(true);
      return;
    }
    try {
      petriNetEditorRef.current?.startAutoSimulation();
    } catch (e) {
      console.warn('⚠️ Fallback para execução direta:', e);
      handleExecutePetriNet();
    }
  };
  
  // Botão para alternar entre modo real e simulação
  const toggleExecutionMode = () => {
    setRealExecutionMode(!realExecutionMode);
    addLog(realExecutionMode ? '🎭 Modo simulação ativado' : '🚀 Modo execução real ativado');
  };

  const pauseExecution = () => {
    handlePausePetriNet();
  };

  const resetExecutionLegacy = () => {
    handleResetPetriNet();
  };

  // Calcular estatísticas
  const stats = {
    total: Object.keys(taskStates).length,
    completed: Object.values(taskStates).filter(t => t.status === TASK_STATUS.COMPLETED).length,
    running: Object.values(taskStates).filter(t => t.status === TASK_STATUS.RUNNING).length,
    pending: Object.values(taskStates).filter(t => t.status === TASK_STATUS.PENDING).length
  };
  const progress = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;

  // Get status color
  const getStatusColor = (status) => {
    switch(status) {
      case 'pending': return '#6b7280';
      case 'running': return '#f59e0b';
      case 'completed': return '#10b981';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Função para inicializar e executar simulador Petri Net
  const handleExecutePetriNet = () => {
    try {
      addLog('🚀 Iniciando execução da Petri Net...');
      
      // ✨ ATIVAR VerbosePanel automaticamente TAMBÉM no modo automático
      setVerbosePanelVisible(true);
      setVerboseSteps([]); // Limpar verbose steps anteriores
      
      // ✨ INICIALIZAR MD CONTENT IDÊNTICO ao testar_interface_generica_v7_md.js
      const now = new Date().toLocaleString();
      setMdContent(`# ACOMPANHAMENTO DE EXECUÇÃO - INPUTS/EXECUÇÃO/OUTPUTS

**Data:** ${now}
**WebSocket:** ws://localhost:6308
**Adapter:** TropicalSalesAdapterV2
**Parser:** CrewAIStructuredParser V1

---

## 🎯 TASKS DISPONÍVEIS

1. **📧 READ EMAIL** - Ler e processar emails
2. **🏷️ CLASSIFY MESSAGE** - Classificar mensagens  
3. **📊 CHECK STOCK** - Verificar estoque
4. **📧 GENERATE RESPONSE** - Gerar resposta

---

## 🚀 EXECUÇÃO EM TEMPO REAL

`);
      
      addLog('🔍 VerbosePanel aberto para acompanhar execução em tempo real');
      
      // Verificar se temos dados da Petri Net
      if (!petriNetData) {
        throw new Error('Dados da Petri Net não disponíveis');
      }
      
      // Garantir estruturas necessárias
      const currentNet = {
        ...petriNetData,
        lugares: petriNetData.lugares || [],
        transicoes: petriNetData.transicoes || [],
        arcos: petriNetData.arcos || []
      };
      
      if (currentNet.lugares.length === 0 && currentNet.transicoes.length === 0) {
        throw new Error('A Petri Net está vazia (sem lugares nem transições)');
      }
      
      console.log('🎯 Executando Petri Net com dados:', currentNet);
      addLog(`📊 Rede carregada: ${currentNet.lugares.length} places, ${currentNet.transicoes.length} transições`);
      
      // Criar novo simulador
      const simulator = new PetriNetSimulator(currentNet);
      
      // ETAPA 9.3: Configurar callbacks para interceptar eventos
      simulator.placeProcessor.setCallbacks({
        onPlaceProcessed: (placeId, inputData, outputData) => {
          console.log(`✅ Place ${placeId} processado:`, { inputData, outputData });
          addLog(`✅ Place ${placeId} executado com sucesso`);
          
          // INTERCEPTAR: Atualizar estado da tarefa atual
          const place = currentNet.lugares.find(p => p.id === placeId);
          if (place && place.agentId) {
            setCurrentExecutingTask({
              id: placeId,
              name: place.nome?.replace('\n', ' ') || placeId,
              agent: place.agentId,
              status: 'completed',
              output_data: outputData,
              timestamp: Date.now()
            });
            
            // Aguardar um pouco antes de limpar para visualização
            setTimeout(() => {
              setCurrentExecutingTask(null);
            }, 2000);
          }
          
          // INTERCEPTAR: Capturar outputs para a aba OUTPUTS
          if (outputData && Object.keys(outputData).length > 0) {
            const newOutput = {
              id: `engine_${placeId}_${Date.now()}`,
              task_name: place?.nome?.replace('\n', ' ') || placeId,
              type: 'engine_place_output',
              output_data: outputData,
              timestamp: Date.now(),
              source: 'engine',
              category: 'Engine - Place Output'
            };
            
            setVerboseByTab(prev => ({
              ...prev,
              outputs: [...prev.outputs, newOutput]
            }));
          }
        },
        onError: (placeId, error) => {
          console.error(`❌ Erro no place ${placeId}:`, error);
          addLog(`❌ Erro no place ${placeId}: ${error.message}`);
          
          // INTERCEPTAR: Marcar tarefa como erro
          const place = currentNet.lugares.find(p => p.id === placeId);
          if (place && place.agentId) {
            setCurrentExecutingTask({
              id: placeId,
              name: place.nome?.replace('\n', ' ') || placeId,
              agent: place.agentId,
              status: 'error',
              error: error.message,
              timestamp: Date.now()
            });
          }
        },
        onVerboseStep: (stepData) => {
          // ✨ Callback unificado: atualiza mdContent e a lista de steps
          console.log('🎯 [VERBOSE CALLBACK] Dados WebSocket V8 recebidos:', stepData);

          if (!stepData) {
            console.log('⚠️ [VERBOSE CALLBACK] stepData é null/undefined');
            return;
          }

          // 1) Atualizar MD exatamente como o cliente V7 faz
          try {
            handleExecutionStep(stepData);
          } catch (e) {
            console.warn('⚠️ Falha ao atualizar MD via handleExecutionStep:', e);
          }

          // 2) Também manter a lista de steps estruturados
          const verboseStep = {
            id: `websocket_${Date.now()}_${Math.random()}`,
            timestamp: stepData.timestamp || new Date().toISOString(),
            task_name: stepData.task_name || 'unknown',
            step_type: stepData.step_type || 'unknown',
            step_description: stepData.step_description || '',
            agent_name: stepData.agent_name || '',
            tool_name: stepData.tool_name || '',
            input_data: stepData.input_data,
            output_data: stepData.output_data,
            section: 'execution',
            type: 'websocket_verbose',
            raw_data: stepData
          };

          setVerboseSteps(prev => [...prev, verboseStep]);

          // Abrir VerbosePanel se não estiver aberto
          if (!verbosePanelVisible) {
            setVerbosePanelVisible(true);
          }
        },
        onLog: (logEntry) => {
          // ✨ NOVO: Capturar logs para VerbosePanel
          if (logEntry && logEntry.message) {
            const verboseStep = {
              id: `log_${Date.now()}_${Math.random()}`,
              timestamp: new Date().toISOString(),
              placeId: logEntry.placeId || 'system',
              placeName: logEntry.placeName || 'System',
              section: logEntry.section || 'execution',
              content: logEntry.message,
              data: logEntry.data || {},
              type: logEntry.type || 'log'
            };
            
            setVerboseSteps(prev => [...prev, verboseStep]);
          }
        }
      });

      // ETAPA 9.3: Override do método fireTransition para interceptar transições
      const originalFireTransition = simulator.fireTransition.bind(simulator);
      simulator.fireTransition = async function(transitionId) {
        console.log(`🔥 Interceptando disparo da transição: ${transitionId}`);
        
        // Encontrar a transição
        const transition = currentNet.transicoes.find(t => t.id === transitionId);
        if (transition) {
          addLog(`🔥 Disparando transição: ${transition.nome || transitionId}`);
          
          // INTERCEPTAR: Atualizar progresso da execução
          const progress = ((currentNet.transicoes.findIndex(t => t.id === transitionId) + 1) / currentNet.transicoes.length) * 100;
          setExecutionProgress(progress);
        }
        
        // ✅ CORREÇÃO: Aguardar execução dos Places
        const result = await originalFireTransition(transitionId);
        
        console.log(`✅ Transição ${transitionId} disparada e Places completados:`, result);
        return result;
      };
      
      // ✨ NOVO: Configurar modo EXECUÇÃO ao invés de simulação
      simulator.setExecutionMode('execution');
      
      // Iniciar execução
      simulator.startSimulation();
      
      // ETAPA 9.3: Executar automaticamente a Petri Net aguardando places completarem
      const runAutomaticExecution = async () => {
        // 🧹 LIMPAR ESTADOS NO INÍCIO DA EXECUÇÃO AUTOMÁTICA
        console.log('🚀 [AUTO EXEC] Iniciando execução automática - limpando estados...');
        clearAllStates();
        if (!simulator.isSimulating) {
          console.log('🏁 Execução finalizada');
          addLog('🏁 Execução da Petri Net finalizada');
          setExecutionState('completed');
          setSimulationRunning(false);
          setCurrentExecutingTask(null);
          return;
        }
        
        // Verificar se há places ainda processando
        const processingPlaces = simulator.getProcessingPlaces();
        if (processingPlaces.length > 0) {
          console.log(`⏳ Aguardando ${processingPlaces.length} places completarem: ${processingPlaces.join(', ')}`);
          addLog(`⏳ Aguardando places completarem: ${processingPlaces.join(', ')}`);
          // Aguardar mais tempo e verificar novamente
          setTimeout(runAutomaticExecution, 2000);
          return;
        }
        
        const enabledTransitions = simulator.getEnabledTransitions();
        console.log(`🔍 Transições aptas: ${enabledTransitions.length}`);
        
        if (enabledTransitions.length > 0) {
          const selectedTransition = simulator.selectRandomEnabledTransition();
          if (selectedTransition) {
            console.log(`🎯 Executando transição: ${selectedTransition.id}`);
            addLog(`🎯 Executando transição: ${selectedTransition.nome || selectedTransition.id}`);
            
            // INTERCEPTAR: Marcar place de destino como em execução
            const arcosSaida = currentNet.arcos.filter(a => a.origem === selectedTransition.id);
            arcosSaida.forEach(arco => {
              const place = currentNet.lugares.find(p => p.id === arco.destino);
              if (place && place.agentId) {
                setCurrentExecutingTask({
                  id: place.id,
                  name: place.nome?.replace('\n', ' ') || place.id,
                  agent: place.agentId,
                  status: 'running',
                  timestamp: Date.now()
                });
              }
            });
            
            // ✅ CORREÇÃO: Aguardar transição e execução dos Places completarem
            try {
              await simulator.fireTransition(selectedTransition.id);
              console.log(`✅ Transição ${selectedTransition.id} e todos os Places completados!`);
              
              // Continuar execução após completar
              setTimeout(runAutomaticExecution, 1000);
            } catch (error) {
              console.error(`❌ Erro na execução da transição ${selectedTransition.id}:`, error);
              addLog(`❌ Erro: ${error.message}`);
              setExecutionState('error');
              return;
            }
          }
        } else {
          console.log('🏁 Execução finalizada - nenhuma transição apta');
          addLog('🏁 Execução da Petri Net finalizada');
          setExecutionState('completed');
          setSimulationRunning(false);
          setCurrentExecutingTask(null);
        }
      };
      
      // Atualizar estados
      setPetriNetSimulator(simulator);
      setSimulationRunning(true);
      setExecutionState('running');
      
      addLog('✅ Execução iniciada com sucesso');
      console.log('🚀 Execução Petri Net iniciada!');
      
      // Iniciar execução automática após delay
      setTimeout(runAutomaticExecution, 1000);
      
    } catch (error) {
      console.error('❌ Erro ao iniciar simulação:', error);
      addLog(`❌ Erro na execução: ${error.message}`);
      setExecutionState('error');
    }
  };

  // Função para pausar simulação
  const handlePausePetriNet = () => {
    if (petriNetSimulator) {
      // TODO: Implementar pausa na próxima etapa
      setExecutionState('paused');
      setSimulationRunning(false);
      addLog('⏸️ Simulação pausada');
    }
  };

  // Função para resetar simulação
  const handleResetPetriNet = () => {
    if (petriNetSimulator) {
      petriNetSimulator.stopSimulation();
      setPetriNetSimulator(null);
      setSimulationRunning(false);
      setExecutionState('idle');
      
      // Limpar dados das abas
      setVerboseByTab({
        operacao: [], inputs: [], execution: [], outputs: [], logs: []
      });
      
      addLog('🔄 Simulação reiniciada');
      console.log('🔄 Simulação resetada');
    }
  };

  // Estados para outputs
  const [outputFiles, setOutputFiles] = useState([]); // Arquivos em disco
  const [taskOutputs, setTaskOutputs] = useState({}); // Saídas JSON entre tarefas
  const [currentOutput, setCurrentOutput] = useState(null); // Output sendo visualizado
  const [showOutputModal, setShowOutputModal] = useState(false); // Modal de visualização

  // Função para gerar dados mock de output
  const generateOutputMockData = (output, taskName, index) => {
    const formats = ['PDF', 'JSON', 'CSV', 'MD', 'TXT'];
    const sizes = ['2.4 KB', '15.2 KB', '8.7 KB', '12.1 KB', '5.3 KB'];
    const format = formats[index % formats.length];
    
    const outputName = output.tool_name || output.type === 'task_completed' ? 
      `${taskName.replace(/_/g, '_')}_output_${index + 1}` : 
      `${output.type}_result_${index + 1}`;

    let content = '';
    let preview = '';
    
    // Gerar conteúdo baseado no tipo
    if (output.output_data) {
      content = typeof output.output_data === 'string' ? 
        output.output_data : 
        JSON.stringify(output.output_data, null, 2);
      preview = content.substring(0, 100) + (content.length > 100 ? '...' : '');
    } else if (output.description) {
      content = output.description;
      preview = content.substring(0, 100) + (content.length > 100 ? '...' : '');
    } else {
      content = `Output gerado pela tarefa ${taskName}\nTipo: ${output.type}\nTimestamp: ${output.timestamp}`;
      preview = content.substring(0, 100) + '...';
    }

    return {
      id: output.id || `output_${index}`,
      name: outputName,
      format: format,
      size: sizes[index % sizes.length],
      content: content,
      preview: preview,
      taskId: taskName,
      taskName: taskName,
      timestamp: output.timestamp,
      type: output.type || 'output'
    };
  };

  // Função para mostrar output no modal
  const handleShowOutput = (outputData) => {
    setCurrentOutput(outputData);
    setShowOutputModal(true);
  };

  // Função para download de output
  const handleDownloadOutput = (outputData) => {
    if (!outputData || !outputData.content) {
      addLog('❌ Erro: Dados de output inválidos');
      return;
    }
    
    try {
      const blob = new Blob([outputData.content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${outputData.name.replace(/[^a-zA-Z0-9]/g, '_')}.${outputData.format.toLowerCase()}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      addLog(`💾 Download iniciado: ${outputData.name}`);
    } catch (error) {
      addLog(`❌ Erro no download: ${error.message}`);
    }
  };

  // Função para coletar todos os outputs (verbose + arquivos + JSON entre tarefas)
  const getAllOutputs = () => {
    const allOutputs = [];
    
    // 1. Outputs do verbose WebSocket
    verboseByTab.outputs.forEach(output => {
      allOutputs.push({
        ...output,
        source: 'verbose',
        category: 'WebSocket Verbose'
      });
    });
    
    // 2. Outputs JSON entre tarefas (extrair do taskStates)
    Object.values(taskStates).forEach(task => {
      if (task.output_data && Object.keys(task.output_data).length > 0) {
        allOutputs.push({
          id: `task_output_${task.id}`,
          task_name: task.name || task.id,
          type: 'task_json_output',
          output_data: task.output_data,
          timestamp: task.timestamp || Date.now(),
          source: 'task_json',
          category: 'Saída JSON entre Tarefas'
        });
      }
    });
    
    // 3. Arquivos em disco (mock - em implementação real, seria leitura do filesystem)
    outputFiles.forEach(file => {
      allOutputs.push({
        ...file,
        source: 'file',
        category: 'Arquivos Salvos em Disco'
      });
    });
    
    return allOutputs;
  };

  // Tabs
  const tabs = [
    { id: 'operacao', label: 'Operação', icon: <ActivityIcon /> },
    { id: 'execution', label: 'Execução', icon: <SettingsIcon /> },
    { id: 'inputs', label: 'Inputs', icon: <FileIcon /> },
    { id: 'outputs', label: 'Outputs', icon: <ChartIcon /> },
    { id: 'logs', label: 'Logs', icon: <FileIcon /> },
    { id: 'verbosev8', label: 'VerbosePanel V8', icon: <RobotIcon /> }
  ];

  return (
    <div style={{ color: 'var(--foreground)' }}>
      {/* Header com informações do projeto */}
      <div style={{ 
        background: 'var(--card)', 
        border: '1px solid var(--border)',
        borderRadius: '12px',
        padding: '16px', // Reduzido de 24px para 16px
        marginBottom: '20px' // Reduzido de 24px para 20px
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
          <div>
            <h2 style={{ 
              fontSize: '24px', 
              fontWeight: '700', 
              color: 'var(--foreground)', 
              margin: 0, 
              marginBottom: '8px' 
            }}>
              {project?.name || "Teste Tropical Sales"}
            </h2>
            {project?.description && (
              <p style={{ 
                color: 'var(--muted-foreground)', 
                fontSize: '14px', 
                margin: 0 
              }}>
                {project.description}
              </p>
            )}
            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)', marginTop: '4px' }}>
              Executor de Tarefas v{UI_VERSION} • {BUILD_LOADED_AT}
            </div>
          </div>
          <div style={{ 
            padding: '8px 16px',
            background: executionState === 'running' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(107, 114, 128, 0.1)',
            color: executionState === 'running' ? '#3b82f6' : '#6b7280',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '600',
            textTransform: 'uppercase'
          }}>
            {executionState === 'running' ? 'Em Execução' : 
             executionState === 'completed' ? 'Concluído' :
             executionState === 'paused' ? 'Pausado' : 'Aguardando'}
          </div>
        </div>

        {/* Dashboard com estatísticas */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
          gap: '12px', // Reduzido de 16px para 12px
          marginBottom: '12px' // Reduzido de 16px para 12px
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--foreground)' }}>
              {stats.total}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Total</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#10b981' }}>
              {stats.completed}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Concluídas</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#f59e0b' }}>
              {stats.running}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Executando</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--primary)' }}>
              {progress}%
            </div>
            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Progresso</div>
          </div>
        </div>

        {/* Barra de progresso */}
        <div style={{ marginBottom: '12px' }}> {/* Reduzido de 16px para 12px */}
          <div style={{ 
            background: 'var(--secondary)', 
            height: '8px', 
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{ 
              background: 'linear-gradient(90deg, var(--primary), #3b82f6)',
              height: '100%',
              width: `${progress}%`,
              transition: 'width 0.3s ease'
            }} />
          </div>
        </div>

        {/* ETAPA 2 - Controles do Motor Real */}
        <div style={{ 
          background: 'var(--card)', 
          border: '1px solid var(--border)', 
          borderRadius: '8px', 
          padding: '16px', 
          marginBottom: '16px' 
        }}>
          <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            {motorInitialized ? '🚀' : '⚙️'} 
            {motorInitialized ? 'Motor Real Ativo' : 'Inicializando Motor...'}
            {motorInitialized && (
              <span style={{ 
                fontSize: '10px', 
                background: realExecutionMode ? '#10b981' : '#f59e0b',
                color: 'white',
                padding: '2px 6px',
                borderRadius: '4px'
              }}>
                {realExecutionMode ? 'REAL' : 'SIM'}
              </span>
            )}
          </div>
          
          {motorInitialized && (
            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)', marginBottom: '12px' }}>
              Projeto: {currentProject?.name || 'Carregando...'} | 
              Adapter: {currentProject?.execution_config?.adapter_type || 'N/A'}
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Selector de modo de execução (contínua | pausa por tarefa) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Modo:</span>
            <div style={{ display: 'flex', border: '1px solid var(--border)', borderRadius: '6px', overflow: 'hidden' }}>
              <button
                onClick={() => setExecMode('continuous')}
                disabled={executionState === 'running' && !taskCompleted}
                style={{
                  padding: '8px 10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  background: execMode === 'continuous' ? '#10b981' : 'var(--secondary)',
                  color: execMode === 'continuous' ? 'white' : 'var(--foreground)',
                  border: 'none', cursor: 'pointer',
                  opacity: (executionState === 'running' && !taskCompleted) ? 0.5 : 1
                }}
              >
                Contínua
              </button>
              <button
                onClick={() => setExecMode('pause_per_task')}
                disabled={executionState === 'running' && !taskCompleted}
                style={{
                  padding: '8px 10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  background: execMode === 'pause_per_task' ? '#10b981' : 'var(--secondary)',
                  color: execMode === 'pause_per_task' ? 'white' : 'var(--foreground)',
                  border: 'none', cursor: 'pointer',
                  opacity: (executionState === 'running' && !taskCompleted) ? 0.5 : 1
                }}
              >
                Pausar por Tarefa
              </button>
            </div>
          </div>
          <button
            onClick={executionState === 'running' ? pauseExecution : startExecution}
            disabled={!petriNetData}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 20px',
              background: executionState === 'running' ? '#f59e0b' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {executionState === 'running' ? <PauseIcon /> : <PlayIcon />}
            {executionState === 'running' ? 'Pausar' : 'Iniciar'}
          </button>
          
          <button
            onClick={resetExecution}
            disabled={!motorInitialized && !petriNetEngine}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 20px',
              background: 'var(--secondary)',
              color: 'var(--foreground)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <ResetIcon />
            Reiniciar
            </button>
            
            {motorInitialized && (
              <button onClick={toggleExecutionMode} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 20px',
                background: realExecutionMode ? '#10b981' : '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}>
                {realExecutionMode ? '🚀' : '🎭'}
                {realExecutionMode ? 'Modo Real' : 'Modo Simulação'}
              </button>
            )}
          </div>
        </div>
        
        {/* Status da Tarefa Atual */}
        {currentExecutingTask && (
          <div style={{
            background: 'rgba(59, 130, 246, 0.1)',
            border: '2px solid #3b82f6',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '16px'
          }}>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#3b82f6' }}>
              🏃 Executando: {currentExecutingTask.name || currentExecutingTask.id}
            </div>
          </div>
        )}
        </div>
        
        {/* Botão de Teste Verbose */}
        <div style={{ marginBottom: '16px' }}>
          <button
            onClick={testarVerboseParser}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 20px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            🧪
            Testar Verbose Parser
          </button>
        </div>

      {/* Card Colapsável da Petri Net */}
      {project && petriNetData && (
        <div style={{ 
          marginBottom: '24px' // Usando a mesma largura dos outros cards
        }}>
          {/* Header Colapsável */}
          <div 
            onClick={() => setPetriNetExpanded(!petriNetExpanded)}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '12px 16px',
              cursor: 'pointer',
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: petriNetExpanded ? '8px 8px 0 0' : '8px',
              transition: 'all 0.2s ease',
              marginBottom: petriNetExpanded ? '0' : '0'
            }}
          >
            <h3 style={{ 
              margin: 0, 
              fontSize: '16px', 
              fontWeight: '600',
              color: 'var(--foreground)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              🔗 Petri Net - {project?.name || "Projeto"}
            </h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ 
                fontSize: '12px', 
                background: 'rgba(34, 197, 94, 0.1)',
                color: '#22c55e',
                padding: '2px 8px',
                borderRadius: '12px',
                fontWeight: '500'
              }}>
                5P • 4T • 4A
              </span>
              <span style={{
                transform: petriNetExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s ease',
                fontSize: '14px',
                color: 'var(--muted-foreground)'
              }}>
                ▼
              </span>
            </div>
          </div>

          {/* Conteúdo Colapsável */}
          <div style={{
            overflow: petriNetExpanded ? 'hidden' : 'hidden', // Sem scroll, canvas vai se adaptar
            maxHeight: petriNetExpanded ? '520px' : '0px',
            transition: 'max-height 0.4s ease-out',
            background: 'var(--card)',
            border: petriNetExpanded ? '1px solid var(--border)' : 'none',
            borderTop: 'none',
            borderRadius: '0 0 8px 8px'
          }}>
            <div style={{ padding: petriNetExpanded ? '8px' : '0' }}>
              {petriNetExpanded && (
                <PetriNetEditor 
                  ref={petriNetEditorRef}
                  externalData={petriNetData}
                  onDataLoad={() => {
                    console.log('Petri Net carregada no card (Editor pronto)');
                    setEditorReady(true);
                    if (startPending) {
                      console.log('⏩ startPending=true: iniciando auto agora');
                      setStartPending(false);

                      // ⭐ V10: CRÍTICO - Chamar iniciar_execucao ANTES de startAutoSimulation
                      console.log('🌐 [V10] ONDATA: Enviando comando inicial: iniciar_execucao');
                      const centralClient = CentralWSClient.getInstance();
                      // ❌ CORREÇÃO: NÃO limpar cache durante execução - perde dados entre tasks
                      // centralClient.clearResults();
                      centralClient.sendGenericCommand('iniciar_execucao', {
                        timestamp: new Date().toISOString(),
                        session_type: 'tropical_sales_ondata_execution'
                      });

                      try { petriNetEditorRef.current?.startAutoSimulation(); } catch (e) { console.warn('startAutoSimulation falhou:', e); }
                    }
                  }}
                  compactMode={true}
                  suppressVerbosePanel={true}
                  onSimulationStart={() => {
                    // ✨ CALLBACK DO SIMULATIONPANEL - ATIVAR VERBOSEPANEL
                    console.log('🔥 DEBUG: onSimulationStart callback chamado!');

                    // ⭐ V10: CRÍTICO - Garantir iniciar_execucao no onSimulationStart também
                    console.log('🌐 [V10] ONSIMULATION: Enviando comando inicial: iniciar_execucao');
                    const centralClient = CentralWSClient.getInstance();
                    // ❌ CORREÇÃO: NÃO limpar cache durante execução - perde dados entre tasks
                    // centralClient.clearResults();
                    centralClient.sendGenericCommand('iniciar_execucao', {
                      timestamp: new Date().toISOString(),
                      session_type: 'tropical_sales_simulation_execution'
                    });

                    setVerbosePanelVisible(true);
                    setVerboseSteps([]);
                    const now = new Date().toLocaleString();
                    setMdContent(`# ACOMPANHAMENTO DE EXECUÇÃO - INPUTS/EXECUÇÃO/OUTPUTS

**Data:** ${now}
**WebSocket:** ws://localhost:6308
**Adapter:** TropicalSalesAdapterV10
**Parser:** Enhanced Parser V10 (10 Universal Tags)

---

## 🎯 TASKS DISPONÍVEIS

1. **📧 READ EMAIL** - Ler e processar emails
2. **🏷️ CLASSIFY MESSAGE** - Classificar mensagens
3. **📊 CHECK STOCK** - Verificar estoque
4. **📧 GENERATE RESPONSE** - Gerar resposta

---

## 🚀 EXECUÇÃO EM TEMPO REAL

Iniciando execução via Simulador de Petri Net...`);
                  }}
                  onPlaceProcessed={({ placeId, inputData, outputData }) => {
                    try {
                      if (execMode === 'pause_per_task') {
                        // Pausar auto-run do simulador e abrir controles de aprovação
                        petriNetEditorRef.current?.pauseAutoSimulation();
                        // Montar objeto place mínimo
                        const place = { id: placeId, nome: (petriNetData?.lugares?.find(p => p.id === placeId)?.nome) || placeId };
                        setPendingApproval({ place, result: outputData || {} });
                        setExecutionState('paused');
                        addLog(`⏸️ Modo pausa: aguardando aprovação após ${place.nome}`);
                      }
                    } catch (e) {
                      console.warn('onPlaceProcessed handler falhou:', e);
                    }
                  }}
                  pausedByTaskUI={{
                    paused: execMode === 'pause_per_task' && executionState === 'paused',
                    placeName: (pendingApproval?.place?.nome || pendingApproval?.place?.id || null)
                  }}
                />
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ 
          display: 'flex', 
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: '12px',
          padding: '4px'
        }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '12px 16px',
                background: activeTab === tab.id ? 'var(--primary)' : 'transparent',
                color: activeTab === tab.id ? 'var(--primary-foreground)' : 'var(--muted-foreground)',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div style={{ 
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: '12px',
        padding: '24px'
      }}>
        {activeTab === 'operacao' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Tarefas em Execução
            </h3>
            
            {/* Seletor de Modo de Execução */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
                Modo de Execução:
              </label>
              <select 
                value={execMode} 
                onChange={(e) => setExecMode(e.target.value)}
                style={{
                  padding: '8px 12px',
                  border: '1px solid var(--border)',
                  borderRadius: '6px',
                  background: 'var(--card)',
                  color: 'var(--foreground)',
                  fontSize: '14px',
                  minWidth: '200px'
                }}
              >
                <option value="continuous">⚡ Execução Contínua</option>
                <option value="pause_per_task">⏸️ Pausar por Tarefa</option>
              </select>
            </div>
            
            {/* Painel Progresso da Operação */}
            <div style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--foreground)' }}>Progresso da Tarefa Atual</div>
                  <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>{operationTaskProgress}%</div>
                </div>
                <div style={{ background: 'var(--secondary)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ background: '#3b82f6', width: `${operationTaskProgress}%`, height: '100%', transition: 'width 0.3s ease' }} />
                </div>
              </div>
              
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--foreground)' }}>Progresso Geral</div>
                  <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>{operationOverallProgress}%</div>
                </div>
                <div style={{ background: 'var(--secondary)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ background: '#10b981', width: `${operationOverallProgress}%`, height: '100%', transition: 'width 0.3s ease' }} />
                </div>
              </div>
            </div>
            
            {/* Layout de duas colunas: Card único + Painel outputs */}
            <div style={{ display: 'flex', gap: '24px' }}>
              
              {/* COLUNA ESQUERDA: Card da Tarefa */}
              <div style={{ flex: '2' }}>
                <div
                  style={{
                    background: '#ffffff',
                    border: '2px solid #3b82f6',
                    borderRadius: '12px',
                    padding: '0',
                    transition: 'all 0.3s ease',
                    overflow: 'hidden',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                >
                  {/* Header do Card */}
                  <div style={{
                    background: 'linear-gradient(135deg, #eff6ff, #dbeafe)',
                    padding: '16px',
                    borderBottom: '1px solid #d1d5db'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                      <div style={{ fontSize: '24px' }}>⚡</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: '700', fontSize: '16px', color: '#1f2937' }}>
                          {enhancedParserV8Tags.TASK_NAME || currentTaskName || 'Aguardando tarefa...'}
                        </div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>
                          {enhancedParserV8Tags.AGENT_NAME || currentAgentName || (currentTaskName ? currentTaskName.toUpperCase() : '---')}
                        </div>
                      </div>
                      {taskCompleted && execMode === 'pause_per_task' ? (
                        <div style={{
                          padding: '6px 12px',
                          background: '#10b981',
                          color: 'white',
                          borderRadius: '20px',
                          fontSize: '11px',
                          fontWeight: '600'
                        }}>
                          ✅ AGUARDANDO APROVAÇÃO
                        </div>
                      ) : (
                        <div style={{
                          padding: '6px 12px',
                          background: (enhancedParserV8Tags.TASK_NAME || currentTaskName) ? '#10b981' :
                                     executionState === 'completed' ? '#3b82f6' : '#6b7280',
                          color: 'white',
                          borderRadius: '20px',
                          fontSize: '11px',
                          fontWeight: '600'
                        }}>
                          {(enhancedParserV8Tags.TASK_NAME || currentTaskName) ? '▶️ EXECUTANDO' :
                           executionState === 'completed' ? '✅ COMPLETADO' : '⏸️ AGUARDANDO'}
                        </div>
                      )}
                    </div>
                    
                    {/* Nome do Agente */}
                    {currentAgentName && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '36px', marginBottom: '8px' }}>
                        <div style={{ fontSize: '16px' }}>🤖</div>
                        <div style={{ fontSize: '14px', color: '#374151', fontWeight: '500' }}>
                          {currentAgentName}
                        </div>
                      </div>
                    )}
                  </div>

                  <div style={{ padding: '16px' }}>
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px',
                        fontSize: '14px', 
                        fontWeight: '600', 
                        color: '#374151', 
                        marginBottom: '8px' 
                      }}>
                        📥 Inputs da Tarefa
                        <div style={{ marginLeft: 'auto', fontSize: '11px' }}>({operationInputs.length})</div>
                      </div>
                      <div style={{
                        background: '#f9fafb',
                        borderRadius: '6px',
                        padding: '8px',
                        minHeight: '200px',
                        maxHeight: '800px',
                        overflowY: 'auto',
                        border: '1px solid #d1d5db'
                      }}>
                        {/* Enhanced Parser V8 - TASK_INPUT */}
                        {enhancedParserV8Tags.TASK_INPUT && (
                          <div style={{ 
                            marginBottom: '8px', 
                            padding: '8px', 
                            background: '#f0f9ff', 
                            borderRadius: '6px',
                            border: '1px solid #3b82f6' 
                          }}>
                            <div style={{ fontSize: '11px', fontWeight: '600', color: '#1d4ed8', marginBottom: '4px' }}>
                              🎯 Task Input (Enhanced Parser V8):
                            </div>
                            <div style={{ fontSize: '13px', color: '#374151', whiteSpace: 'pre-wrap', maxHeight: '600px', overflowY: 'auto' }}>
                              {enhancedParserV8Tags.TASK_INPUT}
                            </div>
                          </div>
                        )}
                        
                        {/* Enhanced Parser V8 - TOOL_INPUT */}
                        {enhancedParserV8Tags.TOOL_INPUT && (
                          <div style={{
                            marginBottom: '8px',
                            padding: '8px',
                            background: '#f0fdf4',
                            borderRadius: '6px',
                            border: '1px solid #22c55e'
                          }}>
                            <div style={{ fontSize: '13px', fontWeight: '600', color: '#16a34a', marginBottom: '4px' }}>
                              🔧 Tool Input (Enhanced Parser V8):
                            </div>
                            <div style={{ fontSize: '13px', color: '#374151', whiteSpace: 'pre-wrap', maxHeight: '600px', overflowY: 'auto' }}>
                              {typeof enhancedParserV8Tags.TOOL_INPUT === 'object' ?
                                JSON.stringify(enhancedParserV8Tags.TOOL_INPUT, null, 2) :
                                enhancedParserV8Tags.TOOL_INPUT
                              }
                            </div>
                          </div>
                        )}

                        {/* 🔧 FIX CRÍTICO: Renderizar array SEPARADAMENTE das tags */}
                        {operationInputs.length > 0 && operationInputs.map((input, idx) => (
                          <div key={input.id || idx} style={{
                            background: '#ffffff',
                            padding: '8px',
                            borderRadius: '4px',
                            marginBottom: '6px',
                            fontSize: '11px',
                            border: '1px solid #3b82f6'
                          }}>
                            <div style={{
                              color: '#3b82f6',
                              fontWeight: '600',
                              marginBottom: '4px'
                            }}>
                              {input.title || input.tool || 'Input'}
                            </div>
                            <div style={{
                              background: '#f3f4f6',
                              padding: '4px',
                              borderRadius: '2px',
                              color: '#374151',
                              whiteSpace: 'pre-wrap',
                              fontFamily: 'monospace',
                              fontSize: '13px'
                            }}>
                              {(input.content || '').toString()}
                            </div>
                            <div style={{
                              fontSize: '9px',
                              color: '#6b7280',
                              marginTop: '2px'
                            }}>
                              {input.timestamp && new Date(input.timestamp).toLocaleTimeString()}
                            </div>
                          </div>
                        ))}

                        {/* ⚠️ Mensagem "Aguardando" SOMENTE se NADA existir (nem tags, nem array) */}
                        {operationInputs.length === 0 &&
                         !enhancedParserV8Tags.TASK_INPUT &&
                         !enhancedParserV8Tags.TOOL_INPUT &&
                         !enhancedParserV8Tags.TOOL_OUTPUT && (
                          <div style={{
                            color: '#6b7280',
                            fontSize: '11px',
                            textAlign: 'center',
                            padding: '20px'
                          }}>
                            <div style={{ fontSize: '20px', marginBottom: '4px' }}>📋</div>
                            Aguardando inputs da tarefa...
                          </div>
                        )}
                      </div>
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                      <div style={{ fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                        ⚡ Execução ({operationSteps.length})
                      </div>
                      <div style={{
                        background: '#f9fafb',
                        borderRadius: '6px',
                        padding: '8px',
                        minHeight: '400px',
                        maxHeight: '600px',
                        overflowY: 'auto',
                        border: '1px solid #d1d5db'
                      }}>
                        {/* Enhanced Parser V8 - USED_TOOL */}
                        {enhancedParserV8Tags.USED_TOOL && (
                          <div style={{ 
                            marginBottom: '8px', 
                            padding: '8px', 
                            background: '#fef3c7', 
                            borderRadius: '6px',
                            border: '1px solid #f59e0b' 
                          }}>
                            <div style={{ fontSize: '11px', fontWeight: '600', color: '#d97706', marginBottom: '4px' }}>
                              🔧 Tool Utilizada (Enhanced Parser V8):
                            </div>
                            <div style={{ fontSize: '11px', color: '#374151', whiteSpace: 'pre-wrap' }}>
                              {cleanTagValue(enhancedParserV8Tags.USED_TOOL)}
                            </div>
                          </div>
                        )}
                        
                        {/* Enhanced Parser V8 - TASK_STEP */}
                        {enhancedParserV8Tags.TASK_STEP && (
                          <div style={{
                            marginBottom: '8px',
                            padding: '8px',
                            background: '#ede9fe',
                            borderRadius: '6px',
                            border: '1px solid #8b5cf6'
                          }}>
                            <div style={{ fontSize: '11px', fontWeight: '600', color: '#7c3aed', marginBottom: '4px' }}>
                              🚶 Steps de Execução (Enhanced Parser V8):
                            </div>
                            <div style={{ fontSize: '11px', color: '#374151', whiteSpace: 'pre-wrap' }}>
                              {Array.isArray(enhancedParserV8Tags.TASK_STEP) ?
                                enhancedParserV8Tags.TASK_STEP.join('\n') :
                                enhancedParserV8Tags.TASK_STEP
                              }
                            </div>
                          </div>
                        )}

                        {/* ⭐ V10: Enhanced Parser V10 - AGENT_THOUGHT (MOVIDO PARA EXECUÇÃO) */}
                        {enhancedParserV8Tags.AGENT_THOUGHT && (
                          <div style={{
                            marginBottom: '8px',
                            padding: '8px',
                            background: '#f3e8ff',
                            borderRadius: '6px',
                            border: '1px solid #a855f7'
                          }}>
                            <div style={{ fontSize: '11px', fontWeight: '600', color: '#7c3aed', marginBottom: '4px' }}>
                              🧠 Agent Thought (Enhanced Parser V10):
                            </div>
                            <div style={{ fontSize: '11px', color: '#374151', whiteSpace: 'pre-wrap' }}>
                              {typeof enhancedParserV8Tags.AGENT_THOUGHT === 'object' ?
                                JSON.stringify(enhancedParserV8Tags.AGENT_THOUGHT, null, 2) :
                                enhancedParserV8Tags.AGENT_THOUGHT
                              }
                            </div>
                          </div>
                        )}

                        {/* ⭐ V10: Enhanced Parser V10 - TOOL_OUTPUT (MOVIDO PARA EXECUÇÃO) */}
                        {enhancedParserV8Tags.TOOL_OUTPUT && (
                          <div style={{
                            marginBottom: '8px',
                            padding: '8px',
                            background: '#fef3c7',
                            borderRadius: '6px',
                            border: '1px solid #f59e0b'
                          }}>
                            <div style={{ fontSize: '11px', fontWeight: '600', color: '#d97706', marginBottom: '4px' }}>
                              🔧 Tool Output (Enhanced Parser V10):
                            </div>
                            <div style={{ fontSize: '11px', color: '#374151', whiteSpace: 'pre-wrap', maxHeight: '600px', overflowY: 'auto' }}>
                              {typeof enhancedParserV8Tags.TOOL_OUTPUT === 'object' ?
                                JSON.stringify(enhancedParserV8Tags.TOOL_OUTPUT, null, 2) :
                                enhancedParserV8Tags.TOOL_OUTPUT
                              }
                            </div>
                          </div>
                        )}

                        {operationSteps.length === 0 && !enhancedParserV8Tags.USED_TOOL && !enhancedParserV8Tags.TASK_STEP && !enhancedParserV8Tags.AGENT_THOUGHT ? (
                          <div style={{
                            color: '#6b7280',
                            fontSize: '11px',
                            textAlign: 'center',
                            padding: '20px'
                          }}>
                            <div style={{ fontSize: '20px', marginBottom: '4px' }}>🔄</div>
                            Aguardando execução...
                          </div>
                        ) : (
                          (() => {
                            const filteredSteps = operationSteps.filter(step =>
                              !INTERNAL_STEP_TYPES.includes(step.type) &&
                              (step.title || step.content)
                            );
                            let lastAgent = null;

                            return filteredSteps.map((step, idx) => {
                              const showAgent = step.agent && step.agent !== lastAgent;
                              lastAgent = step.agent;

                              return (
                                <div key={step.id || idx} style={{
                                  borderLeft: '4px solid #10b981',
                                  paddingLeft: '8px',
                                  paddingRight: '8px',
                                  paddingTop: '6px',
                                  paddingBottom: '6px',
                                  marginBottom: '6px',
                                  background: '#ffffff',
                                  borderRadius: '0 4px 4px 0',
                                  fontSize: '11px'
                                }}>
                                  <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    marginBottom: '2px'
                                  }}>
                                    {step.type && (
                                      <div style={{
                                        padding: '1px 4px',
                                        background: '#10b981',
                                        color: 'white',
                                        borderRadius: '6px',
                                        fontSize: '9px',
                                        fontWeight: '600'
                                      }}>
                                        {(step.type || '').replace('_', ' ').toUpperCase()}
                                      </div>
                                    )}
                                    <div style={{ fontSize: '9px', color: '#6b7280' }}>
                                      {step.timestamp && new Date(step.timestamp).toLocaleTimeString()}
                                    </div>
                                  </div>
                                  <div style={{
                                    color: '#374151',
                                    marginTop: '2px',
                                    fontSize: '13px'
                                  }}>
                                    {(step.title || step.content || '').toString()}
                                  </div>
                                  {showAgent && (
                                    <div style={{
                                      fontSize: '9px',
                                      color: '#3b82f6',
                                      marginTop: '2px'
                                    }}>
                                      🤖 {step.agent}
                                    </div>
                                  )}
                              {enhancedParserV8Tags.USED_TOOL && (step.type === 'tool_usage' || step.type === 'tool_executing') && (
                                <div style={{
                                  fontSize: '9px',
                                  color: '#10b981',
                                  marginTop: '2px',
                                  fontWeight: '600'
                                }}>
                                  🔧 {enhancedParserV8Tags.USED_TOOL}
                                </div>
                              )}
                                </div>
                              );
                            });
                          })()
                        )}
                      </div>
                    </div>

                    {/* 🟢 CAIXA VERDE DE APROVAÇÃO - Aparece quando task completa em modo pause_per_task */}
                    {taskCompleted && execMode === 'pause_per_task' && (
                      <div style={{
                        marginTop: '16px',
                        padding: '16px',
                        background: 'linear-gradient(135deg, #d1fae5, #a7f3d0)',
                        border: '2px solid #10b981',
                        borderRadius: '8px'
                      }}>
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          marginBottom: '12px'
                        }}>
                          <div style={{ fontSize: '20px' }}>✅</div>
                          <div style={{ fontSize: '16px', fontWeight: '700', color: '#047857' }}>
                            Tarefa Concluída - Aguardando Aprovação
                          </div>
                        </div>
                        <div style={{
                          fontSize: '13px',
                          color: '#065f46',
                          marginBottom: '16px',
                          lineHeight: '1.5'
                        }}>
                          A tarefa foi concluída com sucesso. Revise os documentos gerados e aprove para continuar com a próxima etapa.
                        </div>
                        <div style={{ display: 'flex', gap: '12px' }}>
                          <button
                            onClick={handleApproveAndContinue}
                            style={{
                              flex: 1,
                              padding: '12px 16px',
                              background: '#10b981',
                              color: 'white',
                              border: 'none',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px'
                            }}
                          >
                            ✅ Aprovar e Continuar
                          </button>
                          <button
                            onClick={handleRefazerExecucao}
                            style={{
                              flex: 1,
                              padding: '12px 16px',
                              background: '#1f2937',
                              color: 'white',
                              border: 'none',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px'
                            }}
                          >
                            🔄 Refazer Execução
                          </button>
                        </div>
                      </div>
                    )}

                  </div>
                </div>
              </div>

              {/* COLUNA DIREITA: Painel Outputs Gerados */}
              <div style={{ flex: '1', minWidth: '300px' }}>
                <div style={{
                  background: '#ffffff',
                  border: '2px solid #10b981',
                  borderRadius: '12px',
                  padding: '0',
                  height: 'fit-content',
                  maxHeight: '600px',
                  overflow: 'hidden',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}>
                  {/* Campo de Mensagem para Agente (movido para o topo) */}
                  <div style={{
                    background: '#eff6ff',
                    padding: '16px',
                    borderBottom: '1px solid #3b82f6'
                  }}>
                    <div style={{ marginBottom: '8px', fontSize: '14px', fontWeight: '600', color: '#1e40af' }}>
                      💬 Mensagem para o Agente (Opcional)
                    </div>
                    <textarea
                      value={agentMessage}
                      onChange={(e) => setAgentMessage(e.target.value)}
                      rows={3}
                      style={{
                        width: '100%',
                        fontSize: '12px',
                        padding: '8px',
                        borderRadius: '6px',
                        border: '1px solid #3b82f6',
                        background: '#ffffff',
                        color: '#1f2937',
                        resize: 'vertical'
                      }}
                      placeholder="Instruções específicas ou ajustes solicitados..."
                    />
                  </div>
                  
                  {/* Header do Painel */}
                  <div style={{
                    background: 'linear-gradient(135deg, #ecfdf5, #d1fae5)',
                    padding: '16px',
                    borderBottom: '1px solid #d1d5db'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ fontSize: '20px' }}>📄</div>
                      <div>
                        <div style={{ fontWeight: '700', fontSize: '16px', color: '#374151' }}>
                          Documentos Gerados
                        </div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>
                          {operationOutputs.length} documento{operationOutputs.length !== 1 ? 's' : ''}
                        </div>
                      </div>
                      <div style={{ 
                        marginLeft: 'auto',
                        padding: '4px 8px',
                        background: '#10b981',
                        color: 'white',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: '600'
                      }}>
                        {operationOutputs.length}
                      </div>
                    </div>
                  </div>

              {/* Controles de aprovação quando em pausa por tarefa - movidos para header do card esquerdo */}

              {/* Lista de Documentos e Outputs Gerados */}
                  <div style={{ 
                    padding: '16px',
                    maxHeight: '400px',
                    overflowY: 'auto'
                  }}>
                    {operationOutputs.length === 0 ? (
                      <div style={{
                        textAlign: 'center',
                        padding: '40px 20px',
                        color: '#6b7280',
                        fontSize: '14px'
                      }}>
                        <div style={{ fontSize: '32px', marginBottom: '8px' }}>📋</div>
                        <div>Nenhum documento gerado ainda</div>
                        <div style={{ fontSize: '12px', marginTop: '4px' }}>Os documentos aparecerão aqui conforme são criados pela tarefa</div>
                      </div>
                    ) : (
                      operationOutputs.map((output, index) => (
                        <div key={output.id || index} style={{
                          background: '#f9fafb',
                          border: '1px solid #d1d5db',
                          borderRadius: '8px',
                          padding: '12px',
                          marginBottom: '12px'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <div style={{ fontSize: '16px' }}>
                                {output.icon || (output.type === 'task_completed' ? '✅' : '📄')}
                              </div>
                              <div>
                                <div style={{ fontWeight: '600', fontSize: '13px', color: '#374151' }}>
                                  {output.type === 'task_completed' ? 'Tarefa Concluída' : (output.title || output.tool_name || 'Documento')}
                                </div>
                                <div style={{ fontSize: '11px', color: '#6b7280' }}>
                                  <div style={{
                                    display: 'inline-block',
                                    padding: '2px 6px',
                                    background: output.format === 'json' ? '#059669' :
                                               output.format === 'md' ? '#8b5cf6' :
                                               output.format === 'csv' ? '#f59e0b' :
                                               output.format === 'pdf' ? '#ef4444' :
                                               output.format === 'txt' ? '#6b7280' :
                                               output.type === 'task_completed' ? '#10b981' : '#8b5cf6',
                                    color: 'white',
                                    borderRadius: '10px',
                                    fontSize: '9px',
                                    fontWeight: '600',
                                    marginRight: '8px'
                                  }}>
                                    {output.format === 'json' ? 'JSON' :
                                     output.format === 'md' ? 'MD' :
                                     output.format === 'csv' ? 'CSV' :
                                     output.format === 'pdf' ? 'PDF' :
                                     output.format === 'txt' ? 'TXT' :
                                     output.type === 'task_completed' ? 'RESULT' : 'DOC'}
                                  </div>
                                  {output.content ? `${Math.floor(output.content.length/1024)}KB` : 'N/A'}
                                </div>
                              </div>
                            </div>
                            <div style={{ display: 'flex', gap: '4px' }}>
                              <button
                                onClick={() => openEditOutput(output)}
                                style={{
                                  padding: '4px 8px',
                                  background: '#7c3aed',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '4px',
                                  fontSize: '10px',
                                  cursor: 'pointer'
                                }}
                              >
                                ✏️
                              </button>
                              <button
                                onClick={() => saveOutputToFile(output)}
                                style={{
                                  padding: '4px 8px',
                                  background: '#10b981',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '4px',
                                  fontSize: '10px',
                                  cursor: 'pointer'
                                }}
                                title="Salvar documento"
                              >
                                💾
                              </button>
                            </div>
                          </div>
                          {/* Preview do conteúdo */}
                          <div style={{
                            background: '#ffffff',
                            padding: '8px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            color: '#374151',
                            maxHeight: expandedDocId === output.id ? 'none' : '120px',
                            overflowY: 'auto',
                            border: '1px solid #e5e7eb',
                            position: 'relative'
                          }}>
                            {(() => {
                              const content = output.content || safeStringify(output.output_data || output.description || 'Sem conteúdo');
                              const isExpanded = expandedDocId === output.id;
                              const hasMore = content.length > 500;

                              // Se é markdown, renderizar
                              if (output.format === 'md') {
                                const previewContent = !isExpanded && hasMore ? content.substring(0, 500) + '...' : content;
                                return (
                                  <div style={{ fontSize: '10px' }}>
                                    <div style={{ marginBottom: '4px', fontWeight: '600', color: '#8b5cf6' }}>
                                      📝 Markdown:
                                    </div>
                                    {renderSimpleMarkdown(previewContent)}
                                  </div>
                                );
                              }

                              // Se é JSON, formatar
                              else if (output.format === 'json') {
                                try {
                                  const parsed = typeof content === 'string' ? JSON.parse(content) : content;
                                  const formatted = JSON.stringify(parsed, null, 2);
                                  const preview = !isExpanded && formatted.length > 500 ? formatted.substring(0, 500) + '...' : formatted;
                                  return (
                                    <pre style={{
                                      margin: 0,
                                      fontSize: '9px',
                                      fontFamily: 'monospace',
                                      whiteSpace: 'pre-wrap'
                                    }}>
                                      {preview}
                                    </pre>
                                  );
                                } catch (e) {
                                  const preview = !isExpanded && content.length > 500 ? content.substring(0, 500) + '...' : content;
                                  return preview;
                                }
                              }

                              // CSV - renderizar como tabela se expandido
                              else if (output.format === 'csv') {
                                if (isExpanded) {
                                  const lines = content.split('\n').filter(l => l.trim());
                                  if (lines.length > 1) {
                                    const headers = lines[0].split(',');
                                    const rows = lines.slice(1).map(line => line.split(','));
                                    return (
                                      <table style={{
                                        width: '100%',
                                        fontSize: '9px',
                                        borderCollapse: 'collapse'
                                      }}>
                                        <thead>
                                          <tr>
                                            {headers.map((h, i) => (
                                              <th key={i} style={{
                                                border: '1px solid #e5e7eb',
                                                padding: '4px',
                                                background: '#f3f4f6'
                                              }}>
                                                {h.trim()}
                                              </th>
                                            ))}
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {rows.map((row, i) => (
                                            <tr key={i}>
                                              {row.map((cell, j) => (
                                                <td key={j} style={{
                                                  border: '1px solid #e5e7eb',
                                                  padding: '4px'
                                                }}>
                                                  {cell.trim()}
                                                </td>
                                              ))}
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    );
                                  }
                                } else {
                                  const preview = content.length > 500 ? content.substring(0, 500) + '...' : content;
                                  return <div style={{ whiteSpace: 'pre-wrap' }}>{preview}</div>;
                                }
                              }

                              // Texto simples
                              const preview = !isExpanded && content.length > 500 ? content.substring(0, 500) + '...' : content;
                              return <div style={{ whiteSpace: 'pre-wrap' }}>{preview}</div>;
                            })()}

                            {/* Botão Expandir/Colapsar */}
                            {output.content && output.content.length > 500 && (
                              <button
                                onClick={() => setExpandedDocId(expandedDocId === output.id ? null : output.id)}
                                style={{
                                  position: 'absolute',
                                  bottom: '4px',
                                  right: '4px',
                                  padding: '4px 8px',
                                  background: '#6b7280',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '4px',
                                  fontSize: '9px',
                                  cursor: 'pointer',
                                  opacity: 0.8
                                }}
                              >
                                {expandedDocId === output.id ? '▲ Menos' : '▼ Mais'}
                              </button>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'execution' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Execução da Petri Net
            </h3>

            {/* Controles de Execução */}
            <div style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
                Controles de Execução
              </div>
              
              {/* Botões de Controle */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <button
                  onClick={executeAllTasks}
                  disabled={executionState === 'running'}
                  style={{
                    padding: '8px 16px',
                    background: executionState === 'running' ? 'var(--muted)' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: executionState === 'running' ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  ▶️ EXECUTAR FLUXO
                </button>
                
                <button
                  onClick={pauseExecution}
                  disabled={executionState !== 'running'}
                  style={{
                    padding: '8px 16px',
                    background: executionState !== 'running' ? 'var(--muted)' : '#f59e0b',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: executionState !== 'running' ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  ⏸️ PAUSAR
                </button>
                
                <button
                  onClick={resetExecution}
                  style={{
                    padding: '8px 16px',
                    background: 'var(--secondary)',
                    color: 'var(--foreground)',
                    border: '1px solid var(--border)',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  🔄 RESET
                </button>
              </div>

              {/* Status de Execução */}
              <div style={{ 
                padding: '12px', 
                background: 'var(--secondary)', 
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: '600' }}>
                    Status: <span style={{ 
                      color: executionState === 'running' ? '#3b82f6' : 
                             executionState === 'paused' ? '#f59e0b' : 
                             executionState === 'completed' ? '#10b981' : 'var(--muted-foreground)' 
                    }}>
                      {executionState === 'running' ? '🟢 EXECUTANDO' :
                       executionState === 'paused' ? '🟡 PAUSADO' :
                       executionState === 'completed' ? '✅ CONCLUÍDO' : '⚪ IDLE'}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                    WebSocket: {wsConnected ? '🟢 Conectado' : '🔴 Desconectado'}
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                  Verbose Steps: {verboseSteps.length}
                </div>
              </div>
            </div>

            {/* Barra de Progresso Geral */}
            <div style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '14px', marginBottom: '8px' }}>
                <span style={{ color: 'var(--muted-foreground)' }}>Progresso Geral:</span>
                <span style={{ fontWeight: '600', color: 'var(--foreground)' }}>
                  {currentExecutingTask ? currentExecutingTask.name : "Aguardando início"}
                </span>
              </div>
              <div style={{ width: '100%', background: 'var(--secondary)', borderRadius: '6px', height: '8px' }}>
                <div style={{
                  background: '#3b82f6',
                  height: '100%',
                  borderRadius: '6px',
                  width: `${executionProgress}%`,
                  transition: 'width 0.5s ease'
                }} />
              </div>
            </div>

            {/* ÁREA PRINCIPAL: TAREFA CENTRALIZADA + SEQUÊNCIA */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '16px' }}>
              
              {/* COLUNA ESQUERDA: Tarefa Centralizada */}
              <div>
                {currentExecutingTask ? (
                  <div style={{
                    background: 'rgba(59, 130, 246, 0.1)',
                    border: '2px solid #3b82f6',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center'
                  }}>
                    {/* Header da Tarefa */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                      <div>
                        <div style={{ fontSize: '18px', fontWeight: '700', color: 'var(--foreground)', marginBottom: '4px' }}>
                          {currentExecutingTask.name}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                          {currentExecutingTask.id} • {currentExecutingTask.agent}
                        </div>
                      </div>
                      <div style={{ fontSize: '24px' }}>🤖</div>
                    </div>

                    {/* Progresso da Tarefa */}
                    <div style={{ 
                      background: 'rgba(59, 130, 246, 0.1)', 
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '8px',
                      padding: '12px',
                      marginBottom: '16px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '13px', marginBottom: '8px' }}>
                        <span style={{ fontWeight: '600', color: '#3b82f6' }}>Progresso da Tarefa:</span>
                        <span style={{ color: '#3b82f6', fontWeight: '700' }}>
                          {executingSteps.length} / {executingSteps.length + 1}
                        </span>
                      </div>
                      <div style={{ width: '100%', background: 'rgba(59, 130, 246, 0.2)', borderRadius: '6px', height: '6px' }}>
                        <div style={{
                          background: '#3b82f6',
                          height: '100%',
                          borderRadius: '6px',
                          width: `${(executingSteps.length / (executingSteps.length + 1)) * 100}%`,
                          transition: 'width 0.5s ease'
                        }} />
                      </div>
                    </div>

                    {/* Seções Inputs/Execution/Outputs */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px', textAlign: 'left' }}>
                      {/* Inputs */}
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--muted-foreground)' }}>
                          📥 INPUTS
                        </div>
                        <div style={{ background: 'var(--secondary)', borderRadius: '6px', padding: '12px', minHeight: '200px' }}>
                          {verboseByTab.inputs.filter(i => i.task_name === currentExecutingTask.id).length > 0 ? (
                            verboseByTab.inputs.filter(i => i.task_name === currentExecutingTask.id).slice(-3).map(input => (
                              <div key={input.id} style={{ fontSize: '11px', marginBottom: '6px', color: 'var(--muted-foreground)' }}>
                                • {safeStringify(input.description).substring(0, 60)}...
                              </div>
                            ))
                          ) : (
                            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)', textAlign: 'center', paddingTop: '12px' }}>
                              Aguardando inputs da tarefa...
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Execution */}
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--muted-foreground)' }}>
                          ⚙️ EXECUÇÃO
                        </div>
                        <div style={{ background: 'var(--secondary)', borderRadius: '6px', padding: '12px', minHeight: '300px' }}>
                          {currentStep ? (
                            <div style={{ 
                              background: 'rgba(245, 158, 11, 0.1)', 
                              border: '1px solid rgba(245, 158, 11, 0.3)',
                              borderRadius: '6px',
                              padding: '8px',
                              marginBottom: '8px'
                            }}>
                              <div style={{ fontSize: '11px', fontWeight: '600', color: '#f59e0b' }}>
                                🔄 EXECUTANDO AGORA
                              </div>
                              <div style={{ fontSize: '12px', color: 'var(--foreground)', marginTop: '4px' }}>
                                {currentStep.description}
                              </div>
                            </div>
                          ) : (
                            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)', textAlign: 'center', paddingTop: '20px' }}>
                              Aguardando início da execução...
                            </div>
                          )}
                          
                          {/* Steps executados */}
                          {executingSteps.slice(-2).map(step => (
                            <div key={step.id} style={{ fontSize: '10px', marginBottom: '4px', color: 'var(--muted-foreground)' }}>
                              {!INTERNAL_STEP_TYPES.includes(step.type) && `✅ ${step.type}: `}
                              {safeStringify(step.description).substring(0, 40)}...
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Outputs */}
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--muted-foreground)' }}>
                          📦 OUTPUTS
                        </div>
                        <div style={{ background: 'var(--secondary)', borderRadius: '6px', padding: '12px', minHeight: '60px' }}>
                          {verboseByTab.outputs.filter(o => o.task_name === currentExecutingTask.id).length > 0 ? (
                            verboseByTab.outputs.filter(o => o.task_name === currentExecutingTask.id).slice(-3).map(output => (
                              <div key={output.id} style={{ fontSize: '11px', marginBottom: '6px', color: 'var(--muted-foreground)' }}>
                                • {safeStringify(output.description).substring(0, 60)}...
                              </div>
                            ))
                          ) : (
                            <div style={{ fontSize: '12px', color: 'var(--muted-foreground)', textAlign: 'center', paddingTop: '12px' }}>
                              Aguardando outputs da tarefa...
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  // Estado quando nenhuma tarefa está em execução
                  <div style={{
                    background: 'rgba(156, 163, 175, 0.1)',
                    border: '2px solid #9ca3af',
                    borderRadius: '12px',
                    padding: '40px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏸️</div>
                    <div style={{ fontSize: '18px', fontWeight: '600', color: 'var(--muted-foreground)', marginBottom: '8px' }}>
                      Nenhuma Tarefa em Execução
                    </div>
                    <div style={{ fontSize: '14px', color: 'var(--muted-foreground)' }}>
                      Clique em "EXECUTAR FLUXO" para iniciar a execução da Petri Net
                    </div>
                  </div>
                )}
              </div>

              {/* COLUNA DIREITA: Sequência da Petri Net */}
              <div style={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                padding: '16px'
              }}>
                <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px' }}>
                  Sequência de Execução
                </div>
                <div style={{ fontSize: '12px', color: 'var(--muted-foreground)', marginBottom: '16px' }}>
                  Ordem das tarefas na Petri Net
                </div>

                {getTaskPlacesFromPetriNet().length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '20px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                      📋 Carregue um projeto para ver a sequência
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '500px', overflowY: 'auto' }}>
                    {getTaskPlacesFromPetriNet().map((place, index) => (
                      <div key={place.id}>
                        {/* Place */}
                        <div style={{
                          background: place.id === currentExecutingTask?.id ? 'rgba(59, 130, 246, 0.1)' : 'var(--secondary)',
                          border: place.id === currentExecutingTask?.id ? '2px solid #3b82f6' : '1px solid var(--border)',
                          borderRadius: '6px',
                          padding: '8px',
                          fontSize: '11px'
                        }}>
                          <div style={{ fontWeight: '600', color: 'var(--foreground)' }}>
                            {place.name}
                          </div>
                          <div style={{ color: 'var(--muted-foreground)', marginTop: '2px' }}>
                            {place.id}
                          </div>
                        </div>
                        
                        {/* Seta */}
                        {index < getTaskPlacesFromPetriNet().length - 1 && (
                          <div style={{ textAlign: 'center', padding: '4px' }}>
                            <SimpleArrow color="#3b82f6" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inputs' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Configuração de Inputs
            </h3>

            {/* Seção de Configuração Global */}
            <div style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                ⚙️ Configuração Global do Sistema
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: '8px' }}>🗄️ URL do Banco de Dados</div>
                  <input
                    type="text"
                    placeholder="postgresql://user:pass@host:port/database"
                    value={databaseUrl}
                    onChange={(e) => setDatabaseUrl(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid var(--border)',
                      borderRadius: '6px',
                      background: 'var(--secondary)',
                      color: 'var(--foreground)',
                      fontSize: '12px'
                    }}
                  />
                  <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginTop: '4px' }}>
                    Conexão com banco de dados do projeto
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: '8px' }}>🌐 Endpoint da API</div>
                  <input
                    type="text"
                    placeholder="https://api.exemplo.com/v1"
                    value={apiEndpoint}
                    onChange={(e) => setApiEndpoint(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid var(--border)',
                      borderRadius: '6px',
                      background: 'var(--secondary)',
                      color: 'var(--foreground)',
                      fontSize: '12px'
                    }}
                  />
                  <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginTop: '4px' }}>
                    API principal para integração com sistemas externos
                  </div>
                </div>
              </div>
            </div>

            {/* Seção de Inputs por Tarefa */}
            <div style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                📥 Inputs Necessários por Tarefa
              </div>
              <div style={{ fontSize: '13px', color: 'var(--muted-foreground)', marginBottom: '16px' }}>
                Configurações específicas extraídas da Petri Net do projeto carregado
              </div>

              {getTaskPlacesFromPetriNet().length === 0 ? (
                <div style={{
                  background: 'rgba(156, 163, 175, 0.1)',
                  border: '1px solid rgba(156, 163, 175, 0.3)',
                  borderRadius: '8px',
                  padding: '16px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '14px', color: 'var(--muted-foreground)', marginBottom: '8px' }}>
                    📋 Nenhum projeto carregado
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                    Carregue um projeto para visualizar os inputs necessários
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {getTaskPlacesFromPetriNet().map((place) => {
                    const externalInputs = getExternalInputsFromPlace(place);
                    const internalInputs = getInternalInputsFromPlace(place);
                    const wsInputs = getInputsFromWebSocket(place.id);

                    return (
                      <div key={place.id} style={{
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        padding: '16px'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                          <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--foreground)' }}>
                            {place.name} ({place.id})
                          </div>
                          <div style={{
                            padding: '4px 8px',
                            background: 'var(--primary)',
                            color: 'white',
                            borderRadius: '10px',
                            fontSize: '11px',
                            fontWeight: '600'
                          }}>
                            {place.agent}
                          </div>
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--muted-foreground)', marginBottom: '16px' }}>
                          {place.description}
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                          {/* COLUNA ESQUERDA: Inputs Internos e Entre Tarefas */}
                          <div>
                            {/* Inputs Internos (configurações da tarefa) */}
                            <div style={{ marginBottom: '16px' }}>
                              <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--foreground)' }}>
                                ⚙️ Configurações Internas
                              </div>
                              {Object.keys(internalInputs).length > 0 ? (
                                Object.entries(internalInputs).map(([key, value]) => (
                                  <div key={key} style={{
                                    background: 'rgba(59, 130, 246, 0.1)',
                                    border: '1px solid rgba(59, 130, 246, 0.3)',
                                    borderRadius: '6px',
                                    padding: '8px',
                                    marginBottom: '8px'
                                  }}>
                                    <div style={{ fontSize: '11px', fontWeight: '600', color: '#3b82f6' }}>
                                      {key}
                                    </div>
                                    <div style={{ fontSize: '10px', color: 'var(--muted-foreground)', marginTop: '2px' }}>
                                      {safeStringify(value)}
                                    </div>
                                  </div>
                                ))
                              ) : (
                                <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic' }}>
                                  Nenhuma configuração interna
                                </div>
                              )}
                            </div>

                            {/* Inputs Entre Tarefas (dados do WebSocket) */}
                            <div>
                              <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--foreground)' }}>
                                🔄 Inputs Entre Tarefas ({wsInputs.length})
                              </div>
                              {wsInputs.length > 0 ? (
                                wsInputs.slice(-3).map((input) => (
                                  <div key={input.id} style={{
                                    background: 'rgba(16, 185, 129, 0.1)',
                                    border: '1px solid rgba(16, 185, 129, 0.3)',
                                    borderRadius: '6px',
                                    padding: '8px',
                                    marginBottom: '8px'
                                  }}>
                                    <div style={{ fontSize: '11px', fontWeight: '600', color: '#10b981' }}>
                                      {input.type || 'Input'}
                                    </div>
                                    <div style={{ fontSize: '10px', color: 'var(--muted-foreground)', marginTop: '2px' }}>
                                      {safeStringify(input.description).substring(0, 60)}...
                                    </div>
                                  </div>
                                ))
                              ) : (
                                <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic' }}>
                                  Aguardando dados de tarefas anteriores...
                                </div>
                              )}
                            </div>
                          </div>

                          {/* COLUNA DIREITA: Documentos Externos */}
                          <div>
                            <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--foreground)' }}>
                              📁 Documentos Externos ({externalInputs.length})
                            </div>
                            {externalInputs.length > 0 ? (
                              externalInputs.map((extInput) => {
                                const isConfigured = isExternalInputConfigured(place.id, extInput.id);
                                return (
                                  <div key={extInput.id} style={{
                                    background: isConfigured ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                                    border: `1px solid ${isConfigured ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                                    borderRadius: '6px',
                                    padding: '12px',
                                    marginBottom: '12px'
                                  }}>
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                                      <div style={{
                                        fontSize: '11px',
                                        fontWeight: '600',
                                        color: isConfigured ? '#10b981' : '#f59e0b'
                                      }}>
                                        {extInput.type.toUpperCase()} - {extInput.required ? 'OBRIGATÓRIO' : 'OPCIONAL'}
                                      </div>
                                      <div style={{
                                        fontSize: '10px',
                                        padding: '2px 6px',
                                        background: isConfigured ? '#10b981' : '#f59e0b',
                                        color: 'white',
                                        borderRadius: '8px'
                                      }}>
                                        {isConfigured ? '✅' : '⚠️'}
                                      </div>
                                    </div>
                                    <div style={{ fontSize: '12px', fontWeight: '500', marginBottom: '8px' }}>
                                      {extInput.description}
                                    </div>
                                    
                                    {/* Botões de ação */}
                                    <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
                                      {extInput.type === 'document' && (
                                        <button
                                          onClick={() => handleFileUpload(place.id, extInput.id)}
                                          style={{
                                            padding: '4px 8px',
                                            background: 'var(--secondary)',
                                            color: 'var(--foreground)',
                                            border: '1px solid var(--border)',
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            cursor: 'pointer'
                                          }}
                                          title="Carregar Arquivo"
                                        >
                                          📁 Upload
                                        </button>
                                      )}
                                      {extInput.type === 'config' && (
                                        <button
                                          onClick={() => openConfigModal(place.id, extInput.id, 'api')}
                                          style={{
                                            padding: '4px 8px',
                                            background: 'var(--secondary)',
                                            color: 'var(--foreground)',
                                            border: '1px solid var(--border)',
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            cursor: 'pointer'
                                          }}
                                          title="Configurar API"
                                        >
                                          🔗 Config
                                        </button>
                                      )}
                                      {extInput.type === 'database' && (
                                        <button
                                          onClick={() => openConfigModal(place.id, extInput.id, 'database')}
                                          style={{
                                            padding: '4px 8px',
                                            background: 'var(--secondary)',
                                            color: 'var(--foreground)',
                                            border: '1px solid var(--border)',
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            cursor: 'pointer'
                                          }}
                                          title="Configurar Banco"
                                        >
                                          💾 DB
                                        </button>
                                      )}
                                    </div>
                                    
                                    {/* Status do arquivo carregado */}
                                    {isConfigured && (
                                      <div style={{ marginTop: '8px', fontSize: '10px', color: 'var(--muted-foreground)' }}>
                                        ✅ {uploadedFiles[`${place.id}_${extInput.id}`].fileName}
                                      </div>
                                    )}
                                  </div>
                                );
                              })
                            ) : (
                              <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic' }}>
                                Nenhum documento externo necessário
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'outputs' && (
          <div>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
                  📤 Outputs Gerados pelo Módulo
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--muted-foreground)', margin: '4px 0 0 0' }}>
                  Arquivos e relatórios produzidos após a execução das tarefas
                </p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  padding: '6px 12px',
                  background: 'var(--secondary)',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: 'var(--foreground)',
                  border: '1px solid var(--border)'
                }}>
                  {getAllOutputs().length} outputs
                </div>
                <button
                  onClick={() => {
                    setVerboseByTab(prev => ({ ...prev, outputs: [] }));
                    setOutputFiles([]);
                    setTaskOutputs({});
                  }}
                  style={{
                    padding: '6px 12px',
                    background: 'var(--secondary)',
                    color: 'var(--foreground)',
                    border: '1px solid var(--border)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                >
                  🗑️ Limpar
                </button>
              </div>
            </div>

            {/* Content */}
            {(() => {
              const allOutputs = getAllOutputs();
              return allOutputs.length === 0 ? (
              <div style={{ 
                background: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: '12px',
                padding: '48px 24px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>📤</div>
                <h4 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--foreground)', marginBottom: '8px' }}>
                  Nenhum output gerado ainda
                </h4>
                <p style={{ fontSize: '14px', color: 'var(--muted-foreground)', marginBottom: '16px' }}>
                  Execute o módulo completamente para gerar os outputs finais
                </p>
                <button
                  onClick={() => setActiveTab('execution')}
                  style={{
                    padding: '8px 16px',
                    background: 'var(--primary)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Ir para Execução
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* Agrupar outputs por categoria */}
                {Object.entries(
                  allOutputs.reduce((acc, output) => {
                    const category = output.category || 'Outros';
                    if (!acc[category]) {
                      acc[category] = {
                        category: category,
                        outputs: [],
                        icon: category === 'WebSocket Verbose' ? '🌐' :
                              category === 'Saída JSON entre Tarefas' ? '🔄' :
                              category === 'Arquivos Salvos em Disco' ? '💾' : '📤',
                        color: category === 'WebSocket Verbose' ? '#3b82f6' :
                               category === 'Saída JSON entre Tarefas' ? '#f59e0b' :
                               category === 'Arquivos Salvos em Disco' ? '#10b981' : '#6b7280'
                      };
                    }
                    acc[category].outputs.push(output);
                    return acc;
                  }, {})
                ).map(([category, categoryData]) => (
                  <div key={category} style={{
                    background: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: '12px',
                    padding: '0',
                    overflow: 'hidden'
                  }}>
                    {/* Category Header */}
                    <div style={{
                      background: 'var(--secondary)',
                      padding: '16px 20px',
                      borderBottom: '1px solid var(--border)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          background: categoryData.color,
                          color: 'white',
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '16px'
                        }}>
                          {categoryData.icon}
                        </div>
                        <div>
                          <h4 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--foreground)', margin: 0 }}>
                            {categoryData.category}
                          </h4>
                          <p style={{ fontSize: '12px', color: 'var(--muted-foreground)', margin: '2px 0 0 0' }}>
                            {categoryData.outputs.length} output{categoryData.outputs.length !== 1 ? 's' : ''} disponível{categoryData.outputs.length !== 1 ? 'is' : ''}
                          </p>
                        </div>
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: 'var(--muted-foreground)',
                        padding: '4px 8px',
                        background: 'var(--card)',
                        borderRadius: '4px',
                        border: '1px solid var(--border)'
                      }}>
                        {categoryData.outputs.length > 0 ? new Date(categoryData.outputs[0].timestamp).toLocaleString() : 'N/A'}
                      </div>
                    </div>

                    {/* Outputs Grid */}
                    <div style={{ padding: '20px' }}>
                      <div style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
                        gap: '16px' 
                      }}>
                        {categoryData.outputs.map((output, index) => {
                          // Gerar dados mock do output baseado no tipo
                          const outputData = generateOutputMockData(output, output.task_name || category, index);
                          
                          return (
                            <div key={output.id || index} style={{
                              background: 'var(--secondary)',
                              border: '1px solid var(--border)',
                              borderRadius: '8px',
                              padding: '16px',
                              transition: 'all 0.2s ease',
                              cursor: 'pointer'
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                              e.currentTarget.style.transform = 'translateY(-1px)';
                              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.background = 'var(--secondary)';
                              e.currentTarget.style.transform = 'translateY(0)';
                              e.currentTarget.style.boxShadow = 'none';
                            }}>
                              {/* Output Header */}
                              <div style={{ marginBottom: '12px' }}>
                                <h5 style={{ 
                                  fontSize: '14px', 
                                  fontWeight: '600', 
                                  color: 'var(--foreground)', 
                                  margin: '0 0 4px 0',
                                  lineHeight: '1.3'
                                }}>
                                  {outputData.name}
                                </h5>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                                  <div style={{
                                    padding: '2px 8px',
                                    fontSize: '10px',
                                    fontWeight: '600',
                                    borderRadius: '12px',
                                    background: outputData.format === 'PDF' ? '#ef4444' :
                                               outputData.format === 'JSON' ? '#10b981' :
                                               outputData.format === 'CSV' ? '#3b82f6' :
                                               outputData.format === 'MD' ? '#8b5cf6' :
                                               outputData.format === 'TXT' ? '#f59e0b' : '#6b7280',
                                    color: 'white'
                                  }}>
                                    {outputData.format}
                                  </div>
                                  <span style={{ fontSize: '11px', color: 'var(--muted-foreground)' }}>
                                    {outputData.size}
                                  </span>
                                </div>
                              </div>

                              {/* Content Preview */}
                              <div style={{
                                background: 'var(--card)',
                                padding: '8px',
                                borderRadius: '4px',
                                fontSize: '11px',
                                color: 'var(--muted-foreground)',
                                marginBottom: '12px',
                                maxHeight: '60px',
                                overflow: 'hidden',
                                border: '1px solid var(--border)',
                                fontFamily: 'monospace'
                              }}>
                                {outputData.preview}
                              </div>

                              {/* Action Buttons */}
                              <div style={{ display: 'flex', gap: '6px' }}>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleShowOutput(outputData);
                                  }}
                                  style={{
                                    flex: 1,
                                    padding: '6px 8px',
                                    background: 'var(--primary)',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '11px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'background 0.2s ease'
                                  }}
                                  onMouseEnter={(e) => e.target.style.background = '#1e40af'}
                                  onMouseLeave={(e) => e.target.style.background = 'var(--primary)'}
                                >
                                  👁️ Visualizar
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDownloadOutput(outputData);
                                  }}
                                  style={{
                                    flex: 1,
                                    padding: '6px 8px',
                                    background: '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '11px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'background 0.2s ease'
                                  }}
                                  onMouseEnter={(e) => e.target.style.background = '#059669'}
                                  onMouseLeave={(e) => e.target.style.background = '#10b981'}
                                >
                                  💾 Download
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            );
            })()}

            {/* Modal de Visualização de Output */}
            {showOutputModal && currentOutput && (
              <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0, 0, 0, 0.7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
              }}
              onClick={() => setShowOutputModal(false)}>
                <div style={{
                  background: 'var(--card)',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  padding: '0',
                  maxWidth: '80vw',
                  maxHeight: '80vh',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column'
                }}
                onClick={(e) => e.stopPropagation()}>
                  {/* Modal Header */}
                  <div style={{
                    padding: '20px',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <div>
                      <h3 style={{ fontSize: '18px', fontWeight: '600', color: 'var(--foreground)', margin: 0 }}>
                        📄 {currentOutput.name}
                      </h3>
                      <p style={{ fontSize: '12px', color: 'var(--muted-foreground)', margin: '4px 0 0 0' }}>
                        Tarefa: {currentOutput.taskName} • {currentOutput.format} • {currentOutput.size}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => handleDownloadOutput(currentOutput)}
                        style={{
                          padding: '8px 12px',
                          background: '#10b981',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '12px',
                          fontWeight: '600',
                          cursor: 'pointer'
                        }}
                      >
                        💾 Download
                      </button>
                      <button
                        onClick={() => setShowOutputModal(false)}
                        style={{
                          padding: '8px 12px',
                          background: 'var(--secondary)',
                          color: 'var(--foreground)',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                      >
                        ✕ Fechar
                      </button>
                    </div>
                  </div>

                  {/* Modal Content */}
                  <div style={{
                    padding: '20px',
                    overflow: 'auto',
                    flex: 1,
                    maxHeight: '60vh'
                  }}>
                    {/* Format-specific rendering */}
                    {currentOutput.format === 'JSON' ? (
                      <pre style={{
                        background: 'var(--secondary)',
                        padding: '16px',
                        borderRadius: '8px',
                        overflow: 'auto',
                        fontSize: '12px',
                        fontFamily: 'monospace',
                        color: 'var(--foreground)',
                        border: '1px solid var(--border)',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {(() => {
                          try {
                            return JSON.stringify(JSON.parse(currentOutput.content), null, 2);
                          } catch (e) {
                            return currentOutput.content;
                          }
                        })()}
                      </pre>
                    ) : currentOutput.format === 'CSV' ? (
                      <div style={{
                        background: 'var(--secondary)',
                        padding: '16px',
                        borderRadius: '8px',
                        overflow: 'auto',
                        border: '1px solid var(--border)'
                      }}>
                        <table style={{ width: '100%', fontSize: '12px', color: 'var(--foreground)' }}>
                          <tbody>
                            {currentOutput.content.split('\n').map((row, index) => (
                              <tr key={index} style={{ borderBottom: index === 0 ? '2px solid var(--border)' : '1px solid var(--border)' }}>
                                {row.split(',').map((cell, cellIndex) => (
                                  <td key={cellIndex} style={{
                                    padding: '8px',
                                    borderRight: '1px solid var(--border)',
                                    fontWeight: index === 0 ? '600' : '400'
                                  }}>
                                    {cell.trim()}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : currentOutput.format === 'MD' ? (
                      <div style={{
                        background: 'var(--secondary)',
                        padding: '20px',
                        borderRadius: '8px',
                        border: '1px solid var(--border)',
                        color: 'var(--foreground)',
                        lineHeight: '1.6'
                      }}
                      dangerouslySetInnerHTML={{
                        __html: currentOutput.content
                          .replace(/^# (.*$)/gm, '<h1 style="font-size: 20px; font-weight: bold; margin: 16px 0 8px 0;">$1</h1>')
                          .replace(/^## (.*$)/gm, '<h2 style="font-size: 18px; font-weight: bold; margin: 14px 0 6px 0;">$1</h2>')
                          .replace(/^### (.*$)/gm, '<h3 style="font-size: 16px; font-weight: bold; margin: 12px 0 4px 0;">$1</h3>')
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\*(.*?)\*/g, '<em>$1</em>')
                          .replace(/\n\n/g, '</p><p style="margin: 8px 0;">')
                          .replace(/^(.+)$/gm, '<p style="margin: 8px 0;">$1</p>')
                      }} />
                    ) : (
                      <pre style={{
                        background: 'var(--secondary)',
                        padding: '16px',
                        borderRadius: '8px',
                        overflow: 'auto',
                        fontSize: '12px',
                        fontFamily: 'monospace',
                        color: 'var(--foreground)',
                        border: '1px solid var(--border)',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {currentOutput.content}
                      </pre>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
                Logs de Execução
              </h3>
              <button
                onClick={() => setLogs([])}
                style={{
                  padding: '8px 16px',
                  background: 'var(--secondary)',
                  color: 'var(--foreground)',
                  border: '1px solid var(--border)',
                  borderRadius: '6px',
                  fontSize: '12px',
                  cursor: 'pointer'
                }}
              >
                Limpar Logs
              </button>
            </div>
            <div style={{
              background: 'var(--secondary)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '16px',
              height: '300px',
              overflowY: 'auto',
              fontFamily: 'monospace',
              fontSize: '13px',
              lineHeight: '1.4'
            }}>
              {logs.length === 0 ? (
                <div style={{ color: 'var(--muted-foreground)', textAlign: 'center', paddingTop: '50px' }}>
                  Nenhum log disponível
                </div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} style={{ marginBottom: '4px', color: 'var(--foreground)' }}>
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'verbosev8' && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0, marginBottom: '8px' }}>
                🚀 VerbosePanel V8 - Enhanced Parser
              </h3>
              <p style={{ color: 'var(--muted-foreground)', fontSize: '14px', margin: 0 }}>
                Interface visual em tempo real para tags universais e métricas do Enhanced Parser V8
              </p>
            </div>
            
            <div style={{
              background: 'transparent',
              borderRadius: '12px',
              overflow: 'hidden'
            }}>
              <VerbosePanelV8 
                wsUrl="ws://localhost:6308"
                maxLogEntries={100}
                autoScroll={true}
              />
            </div>
          </div>
        )}
      </div>

      {/* VerbosePanel - Aparece automaticamente durante execução */}
      {console.log('🔥 DEBUG: verbosePanelVisible =', verbosePanelVisible)}
      {verbosePanelVisible && (
        <VerbosePanel
          verboseSteps={verboseSteps}
          mdContent={mdContent}
          taskCounters={taskCounters}
          isExecuting={executionState === 'running' || simulationRunning}
          isOpen={verbosePanelVisible}
          onClose={() => setVerbosePanelVisible(false)}
          position={{ x: 50, y: 100 }}
        />
      )}

      {/* Modal de Edição de Output */}
      {showEditOutputModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            padding: '24px',
            maxWidth: '800px',
            maxHeight: '80vh',
            width: '90%',
            overflowY: 'auto',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}>
            {/* Header */}
            <div style={{ marginBottom: '20px' }}>
              <h2 style={{ 
                fontSize: '18px', 
                fontWeight: '600', 
                color: '#1f2937',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '8px'
              }}>
                📝 Editar Documento: {editingOutput?.title || editingOutput?.tool_name || 'Output'}
              </h2>
            </div>
            
            {/* Info do documento */}
            <div style={{
              background: '#f9fafb',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  padding: '4px 8px',
                  background: editingOutput?.format === 'json' ? '#059669' : '#8b5cf6',
                  color: 'white',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: '600'
                }}>
                  {editingOutput?.format === 'json' ? 'JSON' : 'MD'}
                </div>
                <span style={{ fontSize: '12px', color: '#6b7280' }}>
                  {editingOutput?.content ? `${Math.floor(editingOutput.content.length/1024)}KB` : 'N/A'}
                </span>
              </div>
              <div style={{ fontSize: '11px', color: '#9ca3af' }}>
                Última modificação: {new Date().toLocaleString('pt-BR')}
              </div>
            </div>

            {/* Editor */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '8px'
              }}>
                Conteúdo do Documento:
              </label>
              <textarea
                value={editedOutputText}
                onChange={(e) => setEditedOutputText(e.target.value)}
                style={{
                  width: '100%',
                  height: '400px',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                  color: '#1f2937',
                  backgroundColor: '#ffffff',
                  resize: 'vertical'
                }}
                placeholder="Conteúdo do documento aparecerá aqui..."
              />
              <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
                💡 Este é o conteúdo editável do documento. Faça suas alterações aqui.
              </div>
            </div>

            {/* Actions */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingTop: '16px',
              borderTop: '1px solid #e5e7eb'
            }}>
              <div style={{ fontSize: '11px', color: '#6b7280' }}>
                💡 Dica: Faça as alterações necessárias e clique em Salvar para aplicar
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  onClick={closeEditModal}
                  style={{
                    padding: '8px 16px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    backgroundColor: '#ffffff',
                    color: '#374151',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                >
                  Cancelar
                </button>
                <button 
                  onClick={saveEditedOutput}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#10b981',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  💾 Salvar Alterações
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ExecutorTarefas;
