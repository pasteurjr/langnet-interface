/**
 * Central WebSocket Client - Versão Browser
 * Baseado no trabalho do codex em experimental_petri/central_ws_client.js
 * 
 * FUNCIONALIDADES:
 * - Singleton pattern para client único
 * - Queue para serializar execução de tarefas
 * - Propagação de execution_step para VerbosePanel
 * - Compatibilidade com formato WebSocket V7
 */

class CentralWSClient {
  static _instance;
  
  static getInstance() {
    if (!CentralWSClient._instance) {
      CentralWSClient._instance = new CentralWSClient();
    }
    return CentralWSClient._instance;
  }

  constructor() {
    // Configuração
    // Fonte de configuração em ordem de precedência:
    // 1) window.V7_WS_URI (injetado pela app)
    // 2) localStorage.V7_WS_URI (persistido no browser)
    // 3) fallback default
    let cfgUri = null;
    try { cfgUri = (typeof window !== 'undefined' && window.V7_WS_URI) || null; } catch (_) { cfgUri = null; }
    if (!cfgUri) {
      try { cfgUri = (typeof localStorage !== 'undefined' && localStorage.getItem('V7_WS_URI')) || null; } catch (_) { cfgUri = null; }
    }
    this.uri = cfgUri || 'ws://localhost:6308';
    this.ws = null;
    this.queue = Promise.resolve(); // Serializar execução
    this.connected = false;

    // ✅ CACHE GLOBAL de resultados REAIS como no testar_interface
    this.taskResults = {};
    
    // Callbacks para integração com UI
    this.verboseCallback = null; // Para VerbosePanel
    this.operationCallback = null; // Para ExecutorTarefasNew (aba Operação)
    this.lastResult = {}; // Cache de resultados para encadeamento
    
    console.log('🌐 [CENTRAL WS CLIENT] Inicializado para', this.uri);
  }

  /**
   * Registrar callback para receber execution_step
   * Usado pelo VerbosePanel para receber verbose em tempo real
   */
  setVerboseCallback(callback) {
    this.verboseCallback = callback;
    console.log('🔗 [CENTRAL WS CLIENT] Verbose callback registrado:', typeof callback);
  }

  /**
   * Registrar callback para receber dados na aba Operação
   * Usado pelo ExecutorTarefasNew para processar handleVerboseStep
   */
  setOperationCallback(callback) {
    this.operationCallback = callback;
    console.log('🔗 [CENTRAL WS CLIENT] Operation callback registrado:', typeof callback);
  }

  /**
   * ⭐ V10: Enviar comandos genéricos como iniciar_execucao e finalizar_execucao
   * Usado pelo ExecutorTarefasNew para controles de execução
   * CORRIGIDO: Aguarda conexão estar pronta antes de enviar
   */
  async sendGenericCommand(commandType, data = {}) {
    try {
      // CRÍTICO: Aguardar conexão estar pronta
      await this.connect();

      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        const request = { type: commandType, data };
        console.log(`🌐 [CENTRAL WS CLIENT V10] Enviando comando genérico:`, request);
        this.ws.send(JSON.stringify(request));

        // Para iniciar_execucao, limpar arquivo TAGS_RECEBIDASV10.md e aguardar confirmação
        if (commandType === 'iniciar_execucao') {
          await this._clearTagsRecebidasFile();
          await this.waitForSessionInitialization();
        }
      } else {
        throw new Error(`WebSocket não conectado após tentativa de conexão`);
      }
    } catch (error) {
      console.error(`❌ [CENTRAL WS CLIENT V10] Erro enviando comando ${commandType}:`, error);

      // Retry automático para iniciar_execucao
      if (commandType === 'iniciar_execucao') {
        console.log(`🔄 [CENTRAL WS CLIENT V10] Tentativa de retry para iniciar_execucao...`);
        setTimeout(() => this.sendGenericCommand(commandType, data), 1000);
      }
    }
  }

  /**
   * ⭐ V10: Aguardar confirmação de inicialização da sessão
   * Usado para garantir que iniciar_execucao foi processado com sucesso
   */
  async waitForSessionInitialization() {
    return new Promise((resolve, reject) => {
      // Flag para controlar se já recebemos confirmação
      let initialized = false;

      // Timeout para evitar espera infinita
      const timeout = setTimeout(() => {
        if (!initialized) {
          console.warn('⚠️ [CENTRAL WS CLIENT V10] Timeout aguardando inicialização da sessão');
          resolve(); // Resolver mesmo com timeout para não bloquear
        }
      }, 5000);

      // Handler temporário para capturar resposta
      const initHandler = (event) => {
        try {
          const msg = JSON.parse(event.data);

          // Buscar por confirmação de inicialização
          if (msg.type === 'session_initialized' ||
              msg.type === 'welcome' ||
              (msg.type === 'info' && msg.message && msg.message.includes('iniciada'))) {

            console.log('✅ [CENTRAL WS CLIENT V10] Sessão inicializada confirmada:', msg.type);
            initialized = true;
            clearTimeout(timeout);
            this.ws.removeEventListener('message', initHandler);
            resolve();
          }
        } catch (e) {
          // Ignorar erros de parse
        }
      };

      // Adicionar listener temporário
      if (this.ws) {
        this.ws.addEventListener('message', initHandler);
      } else {
        clearTimeout(timeout);
        resolve();
      }
    });
  }

  /**
   * Conectar ao WebSocket V7
   * Conexão única reutilizada por todos os Places
   */
  async connect() {
    if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
      return;
    }
    
    console.log('🔌 [CENTRAL WS CLIENT] Conectando...', this.uri);
    
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.uri);
        
        this.ws.onopen = () => { 
          this.connected = true; 
          console.log('✅ [CENTRAL WS CLIENT] Conectado');
          resolve(); 
        };
        
        this.ws.onerror = (e) => { 
          console.error('❌ [CENTRAL WS CLIENT] Erro conexão:', e);
          reject(new Error('WS connection error')); 
        };
        
        this.ws.onclose = () => {
          this.connected = false;
          console.log('🔌 [CENTRAL WS CLIENT] Desconectado');
        };
        
      } catch (e) { 
        console.error('❌ [CENTRAL WS CLIENT] Erro ao criar WebSocket:', e);
        reject(e); 
      }
    });
  }

  /**
   * Executar tarefa via WebSocket V8
   * ADAPTADO PARA PARSER V8
   */
  executeTask(taskName, inputData, { onStep } = {}) {
    console.log('📋 [CENTRAL WS CLIENT] Enfileirando tarefa V8:', taskName);
    
    // CRÍTICO: Serializar execução (igual experimental)
    return this.queue = this.queue.then(() => 
      this._runV8(taskName, inputData, { onStep })
    );
  }

  /**
   * Execução real da tarefa - ADAPTADO PARA PARSER V8
   * Baseado no novo parser WebSocket V8
   */
  async _runV8(taskName, inputData, { onStep } = {}) {
    await this.connect();
    
    console.log('🚀 [CENTRAL WS CLIENT V8] Executando:', taskName);
    console.log('📥 [CENTRAL WS CLIENT V8] Input data:', inputData);
    
    return new Promise((resolve, reject) => {
      const handle = (event) => {
        try {
          const msg = JSON.parse(event.data);
          console.log('📨 [CENTRAL WS CLIENT V8] Mensagem recebida:', msg.type);
          
          // PARSER V8: Processar tipos específicos de mensagem V8
          if (msg.type === 'tags_extracted') {
            // ✅ V10: Salvar tags recebidas em arquivo para validação
            this._saveTagsToFile(msg.task_name, msg.tags, msg.timestamp);

            // BRIDGE V8→enhancedParserV8Tags (CRÍTICO)
            if (typeof window !== 'undefined' && window.__setEnhancedParserV8Tags) {
              console.log('🌐 [CENTRAL WS CLIENT V8] Setando enhancedParserV8Tags:', msg.tags);
              
              // Serializar tags para renderização React segura
              const safeTags = {};
              for (const [key, value] of Object.entries(msg.tags || {})) {
                let processedValue = value;
                
                // FILTRO V8: Limpar TASK_NAME incorreto no bridge
                if (key === 'TASK_NAME' && typeof value === 'string' && value.includes('CrewAI team para')) {
                  console.log('🚫 [BRIDGE FILTER] TASK_NAME incorreto detectado:', value);
                  const match = value.match(/'([^']+)'/);
                  processedValue = match ? match[1] : value;
                  console.log('✅ [BRIDGE FILTER] TASK_NAME corrigido para:', processedValue);
                }
                
                if (typeof processedValue === 'string') {
                  safeTags[key] = processedValue;
                } else if (typeof processedValue === 'object' && processedValue !== null) {
                  try {
                    safeTags[key] = JSON.stringify(processedValue, null, 2);
                  } catch (e) {
                    safeTags[key] = '[Objeto não serializável]';
                  }
                } else {
                  safeTags[key] = String(processedValue || '');
                }
              }
              
              // CORREÇÃO: SUBSTITUIR dados em vez de mesclar (fix limpeza)
              window.__setEnhancedParserV8Tags(prev => {
                // Se prev tem tags limpas (todas null), substituir completamente
                const isCleared = Object.values(prev).every(val => val === null);
                if (isCleared) {
                  console.log('🧹 [CENTRAL WS CLIENT V8] Estado limpo detectado, substituindo completamente');
                  return safeTags;
                } else {
                  // Senão, mesclar como antes  
                  return { ...prev, ...safeTags };
                }
              });
              console.log('✅ [CENTRAL WS CLIENT V8] Bridge V8→ExecutorTarefas completo!');
            } else {
              console.warn('⚠️ [CENTRAL WS CLIENT V8] window.__setEnhancedParserV8Tags não disponível');
            }
            
            // Propagar tags V8 para VerbosePanel
            if (this.verboseCallback) {
              this.verboseCallback({
                type: 'tags_extracted', 
                tags: msg.tags
              });
            }
            console.log('🏷️ [CENTRAL WS CLIENT V8] Tags extraídas:', Object.keys(msg.tags || {}));
            
          } else if (msg.type === 'parsing_metrics') {
            // Propagar métricas V8 para VerbosePanel
            if (this.verboseCallback) {
              this.verboseCallback({
                type: 'parsing_metrics', 
                metrics: msg.metrics
              });
            }
            console.log('📊 [CENTRAL WS CLIENT V8] Métricas:', msg.metrics);
            
          } else if (msg.type === 'task_step' || msg.type === 'execution_step') {
            // 🔧 FIX: Suporte para AMBOS os formatos (V8: task_step, V10: execution_step)

            // Normalizar dados dependendo do formato
            const stepData = msg.type === 'execution_step' ? msg.data : msg.step_info;

            if (!stepData) {
              console.warn('⚠️ [CENTRAL WS CLIENT] Step sem dados:', msg.type);
              return;
            }

            // Normalizar campos com nomes diferentes entre V8 e V10
            const normalizedStep = {
              step_type: stepData.step_type,
              description: stepData.description || stepData.step_description || stepData.content || stepData.step_name,
              content: stepData.content || stepData.step_description || stepData.description,
              step_name: stepData.step_name,
              task_name: stepData.task_name,
              agent_name: stepData.agent_name,
              tool_name: stepData.tool_name,
              input_data: stepData.input_data,
              output_data: stepData.output_data,
              timestamp: stepData.timestamp || new Date().toISOString()
            };

            console.log(`🔄 [CENTRAL WS CLIENT] Step recebido (${msg.type}):`, normalizedStep.step_name || normalizedStep.step_type);

            // PROPAGAÇÃO 1: Para callback local (Place)
            onStep && onStep(normalizedStep);

            // PROPAGAÇÃO 2: Para VerbosePanel global
            if (this.verboseCallback) {
              this.verboseCallback({
                type: 'task_step',
                step_info: normalizedStep
              });
            }

            // PROPAGAÇÃO 3: Para aba Operação (ExecutorTarefasNew)
            if (this.operationCallback) {
              // Função para serializar objetos complexos de forma segura
              const safeSerialize = (data) => {
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

              // Adaptar formato normalizado para o formato esperado pelo handleVerboseStep
              const adaptedStep = {
                type: 'execution_step',
                data: {
                  step_type: normalizedStep.step_type || 'task_step',
                  step_description: safeSerialize(normalizedStep.description || 'Step'),
                  step_name: normalizedStep.step_name || normalizedStep.step_type || 'Step',
                  task_name: normalizedStep.task_name,
                  agent_name: normalizedStep.agent_name,
                  tool_name: normalizedStep.tool_name,
                  input_data: normalizedStep.input_data,
                  output_data: normalizedStep.output_data,
                  timestamp: normalizedStep.timestamp,
                  description: safeSerialize(normalizedStep.description || 'Step')
                }
              };
              this.operationCallback(adaptedStep);
            }

            console.log('✅ [CENTRAL WS CLIENT] Step propagado para UI:', normalizedStep.step_name || normalizedStep.step_type);
            
          } else if (msg.type === 'task_completed' || msg.type === 'task_result') {
            this.ws.removeEventListener('message', handle);

            console.log('🔍 [DEBUG] task_completed recebido:', {
              type: msg.type,
              has_data: !!msg.data,
              has_result_in_data: !!msg.data?.result,
              has_result_top_level: !!msg.result,
              msg_keys: Object.keys(msg),
              data_keys: msg.data ? Object.keys(msg.data) : null
            });

            const result = msg.data?.result || msg.result;
            console.log('✅ [CENTRAL WS CLIENT V10] Tarefa completa:', taskName);
            console.log('📤 [CENTRAL WS CLIENT V10] Result REAL recebido:', result);
            console.log('🔍 [DEBUG] Result type:', typeof result, 'isArray:', Array.isArray(result));

            // ✅ SALVAR RESULTADO REAL NO CACHE GLOBAL IDÊNTICO ao testar_interface
            // No testar_interface: taskResults[taskName] = result (usado em startNextTask line 392)
            this.taskResults[taskName] = result;
            console.log('💾 [CENTRAL WS CLIENT V10] Resultado REAL salvo no cache para propagação:', taskName);
            console.log('🔍 [CENTRAL WS CLIENT V10 DEBUG] Cache completo após salvar:', Object.keys(this.taskResults));
            console.log('🔍 [CENTRAL WS CLIENT V10 DEBUG] Instância singleton ID:', this.constructor.name, Date.now());

            // CRÍTICO: Salvar resultado para encadeamento (legado)
            this.lastResult[taskName] = result;

            // ✅ PROPAGAR RESULTADO REAL para ExecutorTarefasNew via bridges
            this.propagateToNextPlace(taskName, result);

            resolve(result);
            
          } else if (msg.type === 'task_error') {
            this.ws.removeEventListener('message', handle);

            const error = msg.error || msg.data?.error || msg.message || 'Task execution error';
            console.error('❌ [CENTRAL WS CLIENT V8] Task error:', error);
            reject(new Error(error));

          } else if (msg.type === 'error') {
            this.ws.removeEventListener('message', handle);

            const error = msg.message || msg.data?.error || 'ws error';
            console.error('❌ [CENTRAL WS CLIENT V8] Erro:', error);
            reject(new Error(error));
          }
        } catch (parseError) {
          console.error('❌ [CENTRAL WS CLIENT V8] Erro parse:', parseError);
        }
      };
      
      // Registrar handler
      this.ws.addEventListener('message', handle);
      
      // FORMATO V10: Enviar mensagem IDÊNTICA ao testar_interface_generica_v10_md.js
      const payload = {
        type: 'execute_task',
        data: {
          task_name: taskName,
          input_data: inputData
        }
      };
      
      console.log('📤 [CENTRAL WS CLIENT V10] Enviando:', payload);
      this.ws.send(JSON.stringify(payload));
    });
  }

  /**
   * ✅ NOVO: Propagar resultado REAL para próximo Place automaticamente
   * @param {string} completedTask - Nome da tarefa completada
   * @param {Object} result - Resultado REAL da tarefa
   */
  propagateToNextPlace(completedTask, result) {
    console.log(`🔄 [CENTRAL WS CLIENT V10] Propagando resultado REAL de ${completedTask}`);

    // Bridge para PetriNetEngine indicar que task foi completa com dados REAIS
    if (typeof window !== 'undefined' && window.__notifyTaskCompletion) {
      console.log(`🌐 [CENTRAL WS CLIENT V10] Notificando PetriNetEngine sobre ${completedTask}`);
      window.__notifyTaskCompletion(completedTask, result);
    }

    // Bridge para ExecutorTarefasNew indicar resultado REAL disponível
    if (typeof window !== 'undefined' && window.__updatePlaceWithRealData) {
      console.log(`📡 [CENTRAL WS CLIENT V10] Atualizando Place com dados REAIS`);
      window.__updatePlaceWithRealData(completedTask, result);
    }
  }

  /**
   * Debug: obter últimos resultados (legado)
   */
  getLastResults() {
    return this.lastResult;
  }

  /**
   * ✅ NOVO: Obter cache de resultados REAIS (como testar_interface)
   */
  getTaskResults() {
    return this.taskResults;
  }

  /**
   * ✅ NOVO: Obter resultado REAL específico
   * @param {string} taskName - Nome da tarefa
   * @returns {Object} - Resultado REAL da tarefa
   */
  getTaskResult(taskName) {
    const result = this.taskResults[taskName] || null;
    console.log(`🔍 [CENTRAL WS CLIENT V10 DEBUG] getTaskResult('${taskName}'):`, result ? 'ENCONTRADO' : 'NÃO ENCONTRADO');
    console.log(`🔍 [CENTRAL WS CLIENT V10 DEBUG] Cache disponível:`, Object.keys(this.taskResults));
    console.log(`🔍 [CENTRAL WS CLIENT V10 DEBUG] Instância singleton ID:`, this.constructor.name, this);
    return result;
  }

  /**
   * Limpar cache de resultados
   */
  clearResults() {
    this.lastResult = {};
    this.taskResults = {}; // ✅ Limpar cache REAL também
    console.log('🗑️ [CENTRAL WS CLIENT V10] Cache de resultados REAIS limpo');
  }

  /**
   * V10: Salvar tags recebidas em arquivo TAGS_RECEBIDASV10.md para validação
   */
  _saveTagsToFile(taskName, tags, timestamp) {
    console.log('📝 [V10] Salvando tags recebidas em TAGS_RECEBIDASV10.md:', taskName);

    // Formatar conteúdo idêntico ao TAGS_OBTIDASV10.md do backend
    let content = `# LOGS RECEBIDAS V10 - ${taskName}\n\n`;
    content += `## Timestamp: ${timestamp}\n\n`;
    content += `## Tags Recebidas no React:\n`;

    const universalTags = [
      'TASK_NAME', 'AGENT_NAME', 'TASK_INPUT', 'USED_TOOL',
      'AGENT_THOUGHT', 'TOOL_INPUT', 'TOOL_OUTPUT',
      'TASK_OUTPUT', 'TASK_OUTPUT_TYPE', 'TASK_STEP',
      'TASK_COMPLETED'
    ];

    for (const tagName of universalTags) {
      const value = tags[tagName] || 'N/A';
      content += `- **${tagName}**: ${value}\n`;
    }

    content += `\n## Parser Version: Enhanced V10 (Cliente React)\n\n`;
    content += `## Verbose Integral:\n`;
    content += `Ver arquivo \`verbosecrewaiintegral.txt\` para verbose completo do CrewAI.\n`;

    // Enviar para backend salvar
    this._sendToBackendForSave(content);
  }

  /**
   * V10: Enviar conteúdo para backend salvar em arquivo
   */
  async _sendToBackendForSave(content) {
    try {
      const response = await fetch('http://localhost:8000/api/save-tags-recebidas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });

      const result = await response.json();
      if (result.success) {
        console.log('✅ [V10] TAGS_RECEBIDASV10.md atualizado com sucesso');
      } else {
        console.error('⚠️ [V10] Erro ao salvar TAGS_RECEBIDASV10.md:', result.error);
      }
    } catch (error) {
      console.error('❌ [V10] Erro ao enviar tags para backend:', error);
    }
  }

  /**
   * V10: Limpar arquivo TAGS_RECEBIDASV10.md ao iniciar nova execução
   */
  async _clearTagsRecebidasFile() {
    try {
      const response = await fetch('http://localhost:8000/api/clear-tags-recebidas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      if (result.success) {
        console.log('🗑️ [V10] TAGS_RECEBIDASV10.md limpo para nova execução');
      } else {
        console.error('⚠️ [V10] Erro ao limpar TAGS_RECEBIDASV10.md:', result.error);
      }
    } catch (error) {
      console.error('❌ [V10] Erro ao limpar arquivo:', error);
    }
  }

}

export { CentralWSClient };
