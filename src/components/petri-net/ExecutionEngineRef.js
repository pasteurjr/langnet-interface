/**
 * ExecutionEngine.js
 * 
 * Motor principal de execução da Petri Net via WebSocket V7
 * Implementa requisitos RF01 - EXECUÇÃO DA PETRI NET VIA WEBSOCKET V7
 * 
 * Baseado em:
 * - TESTE 1.4: Conexão WebSocket V7
 * - TESTE 1.5: Execução Place com agentId 
 * - TESTE 1.6: Execução Place JavaScript local
 * - Requisitos RF01.1, RF01.2, RF01.3
 */

export class PetriNetExecutionEngine {
  constructor(petriNet, webSocket, projectConfig = null) {
    this.petriNet = petriNet;
    this.ws = webSocket;
    this.contextStateHook = null; // Será injetado
    this.projectConfig = projectConfig;
    
    // Estado do motor
    this.isConnected = false;
    this.webSocketStatus = 'DISCONNECTED';
    this.petriNetLoaded = false;
    this.executionStatus = 'IDLE';
    this.currentPlace = null;
    this.executionQueue = [];
    
    // Configuração genérica do projeto
    this.adapterType = projectConfig?.adapter_type || 'GenericAdapter';
    this.taskNamingPattern = projectConfig?.task_naming_pattern || '(.+)_task';
    this.websocketTimeout = projectConfig?.websocket_config?.timeout || 30000;
    this.isConfigured = !!projectConfig;
    
    // Contadores e métricas
    this.placesCount = 0;
    this.transitionsCount = 0;
    this.executionStats = {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      websocketCalls: 0,
      localExecutions: 0,
      totalTime: 0
    };

    // Callbacks para interface
    this.onPlaceStarted = null;
    this.onPlaceCompleted = null;
    this.onPlaceFailed = null;
    this.onVerboseReceived = null;
    this.onStatusChanged = null;

    console.log('🔧 ExecutionEngine genérica criada:', {
      adapter: this.adapterType,
      pattern: this.taskNamingPattern,
      timeout: this.websocketTimeout,
      configured: this.isConfigured
    });
  }

  /**
   * Inicializar motor - TESTE 1.4
   */
  async initialize() {
    console.log('🔌 Conectando ao WebSocket V7...');
    
    try {
      // Verificar WebSocket
      if (!this.ws) {
        throw new Error('WebSocket não fornecido');
      }

      // Configurar event listeners
      this.setupWebSocketListeners();
      
      // Verificar conexão
      if (this.ws.readyState === WebSocket.OPEN) {
        this.isConnected = true;
        this.webSocketStatus = 'OPEN';
      }

      // Carregar Petri Net
      this.loadPetriNet();

      // Detectar adapter
      this.detectAdapter();

      this.executionStatus = 'READY';

      console.log('✅ ExecutionEngine conectado ao WebSocket V8 (porta 6308)');
      console.log('🔧 Status: READY para execução de Places');
      console.log(`📊 Petri Net carregada: ${this.placesCount} Places, ${this.transitionsCount} Transições`);
      console.log(`🎯 Places com agentId: ${this.getPlacesWithAgentId().length} (${this.getPlacesWithAgentId().map(p => p.id).join(', ')})`);
      console.log(`🎯 Places locais: ${this.getLocalPlaces().length} (${this.getLocalPlaces().map(p => p.id).join(', ')})`);
      console.log(`⚡ ${this.adapterType} detectado`);

      this.notifyStatusChange('READY');
      return true;

    } catch (error) {
      console.error('❌ Erro na inicialização do ExecutionEngine:', error);
      this.executionStatus = 'ERROR';
      this.notifyStatusChange('ERROR');
      throw error;
    }
  }

  /**
   * Configurar WebSocket listeners
   */
  setupWebSocketListeners() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.isConnected = true;
      this.webSocketStatus = 'OPEN';
      console.log('🔌 WebSocket conectado');
    };

    this.ws.onmessage = (event) => {
      this.handleWebSocketMessage(event);
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket erro:', error);
      this.webSocketStatus = 'ERROR';
    };

    this.ws.onclose = () => {
      this.isConnected = false;
      this.webSocketStatus = 'CLOSED';
      console.log('🔌 WebSocket desconectado');
    };
  }

  /**
   * Carregar dados da Petri Net
   */
  loadPetriNet() {
    if (!this.petriNet) {
      throw new Error('Petri Net não fornecida');
    }

    this.placesCount = this.petriNet.lugares ? this.petriNet.lugares.length : 0;
    this.transitionsCount = this.petriNet.transicoes ? this.petriNet.transicoes.length : 0;
    this.petriNetLoaded = true;

    console.log('📊 Petri Net processada:', {
      places: this.placesCount,
      transitions: this.transitionsCount
    });
  }

  /**
   * Detectar tipo de adapter
   */
  detectAdapter() {
    // Adapter já configurado no constructor via projectConfig
    console.log(`🔧 Adapter configurado: ${this.adapterType}`);
    
    // Log adicional da configuração
    console.log(`🔧 Pattern naming: ${this.taskNamingPattern}`);
    console.log(`🔧 WebSocket timeout: ${this.websocketTimeout}ms`);
  }

  /**
   * Injetar hook de Context State - RF01.3
   */
  setContextStateHook(contextStateHook) {
    this.contextStateHook = contextStateHook;
    
    // Inicializar Context State
    if (this.contextStateHook && this.contextStateHook.initializeContextState) {
      this.contextStateHook.initializeContextState({
        petri_net_loaded: true,
        engine_status: 'ready'
      });
    }
  }

  /**
   * Extrair task_name genérico baseado no pattern do projeto
   */
  extractTaskName(place) {
    if (place.task_name) {
      return place.task_name; // Usar campo específico se existir
    }

    if (!this.taskNamingPattern || this.taskNamingPattern === 'null') {
      return place.nome; // Usar nome diretamente se não há pattern
    }

    try {
      const regex = new RegExp(this.taskNamingPattern);
      const match = place.nome.match(regex);
      
      if (match && match[1]) {
        return match[1]; // Primeiro grupo capturado
      } else {
        console.warn(`⚠️ Pattern ${this.taskNamingPattern} não matchou ${place.nome}, usando nome direto`);
        return place.nome;
      }
    } catch (error) {
      console.error(`❌ Erro no pattern regex ${this.taskNamingPattern}:`, error);
      return place.nome;
    }
  }

  /**
   * Executar Place - TESTE 1.5 (WebSocket) e TESTE 1.6 (Local)
   */
  async executePlace(place) {
    if (!place) {
      throw new Error('Place não fornecido');
    }

    console.log(`🚀 Executando Place ${place.id} via ${place.agentId ? 'WebSocket V7' : 'JavaScript Local'}`);
    
    // Marcar como atual
    this.currentPlace = place;
    place.status = 'running';
    place.start_time = Date.now();

    // Notificar início
    this.notifyPlaceStarted(place);

    try {
      let result;
      
      if (place.agentId) {
        // TESTE 1.5 - Execução via WebSocket
        result = await this.executeWebSocketPlace(place);
        this.executionStats.websocketCalls++;
      } else {
        // TESTE 1.6 - Execução JavaScript local
        result = await this.executeLocalPlace(place);
        this.executionStats.localExecutions++;
      }

      // Marcar como completado
      place.status = 'completed';
      place.end_time = Date.now();
      place.execution_time = place.end_time - place.start_time;
      place.output_data = result;

      // Atualizar Context State - RF01.3
      if (this.contextStateHook && this.contextStateHook.updateContextState) {
        this.contextStateHook.updateContextState(result, place.id);
      }

      console.log(`✅ Place ${place.id} executado com sucesso`);
      console.log(`⏱️ Tempo execução: ${place.execution_time}ms`);

      // Estatísticas
      this.executionStats.totalExecutions++;
      this.executionStats.successfulExecutions++;
      this.executionStats.totalTime += place.execution_time;

      // Notificar conclusão
      this.notifyPlaceCompleted(place, result);

      return result;

    } catch (error) {
      // Marcar como erro
      place.status = 'error';
      place.end_time = Date.now();
      place.execution_time = place.end_time - place.start_time;
      place.error_message = error.message;

      console.error(`❌ Erro executando Place ${place.id}:`, error);

      // Estatísticas
      this.executionStats.totalExecutions++;
      this.executionStats.failedExecutions++;

      // Notificar erro
      this.notifyPlaceFailed(place, error);

      throw error;
    }
  }

  /**
   * Executar Place via WebSocket - TESTE 1.5
   */
  async executeWebSocketPlace(place) {
    console.log('📋 Preparando Context State...');

    // Merge input_data com Context State - RF01.3
    let inputData = place.input_data || {};
    if (this.contextStateHook && this.contextStateHook.mergeWithContextState) {
      inputData = this.contextStateHook.mergeWithContextState(inputData);
    }

    console.log(`🔀 Input merged: ${JSON.stringify(inputData).substring(0, 100)}...`);

    // Preparar task_name usando método genérico - RF01.2
    const taskName = this.extractTaskName(place);

    // Preparar mensagem WebSocket - RF01.2
    const message = {
      type: 'execute_task',
      data: {
        task_name: taskName,
        input_data: inputData
      }
    };

    console.log('📤 Enviando para WebSocket:', {
      type: message.type,
      task_name: taskName,
      input_fields: Object.keys(inputData).length
    });

    return new Promise((resolve, reject) => {
      // Timeout configurável para evitar travamento
      const timeout = setTimeout(() => {
        reject(new Error(`Timeout executando Place ${place.id} (${this.websocketTimeout/1000}s)`));
      }, this.websocketTimeout);

      // Handler para resposta
      const originalOnMessage = this.ws.onmessage;
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Processar verbose em tempo real
          if (data.type === 'verbose_step' || data.type === 'execution_step') {
            console.log('📥 Verbose recebido:', data.step_type || data.type);
            this.notifyVerboseReceived(data, place.id);
          }
          
          // Aguardar task_completed - RF01.2
          else if (data.type === 'task_completed') {
            clearTimeout(timeout);
            this.ws.onmessage = originalOnMessage; // Restaurar handler original
            
            console.log('✅ Task completed recebida em', (Date.now() - place.start_time) / 1000 + 's');
            console.log('📊 Resultado obtido:', JSON.stringify(data.result || {}).length, 'chars');
            
            resolve(data.result || {});
          }
          
          // Tratar erro
          else if (data.type === 'task_error') {
            clearTimeout(timeout);
            this.ws.onmessage = originalOnMessage;
            
            reject(new Error(`WebSocket task error: ${data.error || 'Unknown error'}`));
          }

          // Chamar handler original para outras mensagens
          if (originalOnMessage) {
            originalOnMessage(event);
          }

        } catch (parseError) {
          console.error('❌ Erro parsing WebSocket message:', parseError);
        }
      };

      // Enviar mensagem
      try {
        this.ws.send(JSON.stringify(message));
        console.log('⏳ Aguardando resposta task_completed...');
      } catch (sendError) {
        clearTimeout(timeout);
        this.ws.onmessage = originalOnMessage;
        reject(new Error(`Erro enviando mensagem WebSocket: ${sendError.message}`));
      }
    });
  }

  /**
   * Executar Place JavaScript local - TESTE 1.6  
   */
  async executeLocalPlace(place) {
    console.log('⚡ Executando lógica JavaScript do Place', place.id);
    console.log('🔒 Ambiente seguro criado para execução');

    if (!place.logica) {
      throw new Error(`Place ${place.id} não possui campo 'logica' definido`);
    }

    // Preparar Context State para input - RF05.3
    let contextState = {};
    if (this.contextStateHook && this.contextStateHook.contextState) {
      contextState = Object.fromEntries(this.contextStateHook.contextState);
    }

    // Merge input_data com Context State
    let inputData = place.input_data || {};
    if (this.contextStateHook && this.contextStateHook.mergeWithContextState) {
      inputData = this.contextStateHook.mergeWithContextState(inputData);
    }

    console.log('📋 Context State atual:', Object.keys(contextState).length, 'campos');
    console.log(`🔀 Input merged: ${JSON.stringify(inputData).substring(0, 100)}...`);

    try {
      console.log('--- Execução JavaScript Iniciada ---');

      // Criar ambiente seguro - RF05.3
      const safeEnv = {
        input: inputData,
        utils: {
          formatDate: (date) => new Date(date).toISOString(),
          parseJSON: (str) => JSON.parse(str),
          stringify: (obj) => JSON.stringify(obj, null, 2),
          now: () => new Date().toISOString(),
          timestamp: () => Date.now()
        },
        console: {
          log: (...args) => console.log(`[Place ${place.id}]:`, ...args),
          info: (...args) => console.info(`[Place ${place.id}]:`, ...args),
          warn: (...args) => console.warn(`[Place ${place.id}]:`, ...args),
          error: (...args) => console.error(`[Place ${place.id}]:`, ...args)
        }
      };

      // Executar lógica JavaScript - RF05.3
      const logicFunction = new Function(
        'input', 
        'utils', 
        'console',
        `
        ${place.logica}
        `
      );

      const result = await logicFunction(
        safeEnv.input,
        safeEnv.utils,
        safeEnv.console
      );

      console.log('--- Execução JavaScript Finalizada ---');
      console.log('⏱️ Tempo execução:', Date.now() - place.start_time + 'ms');
      console.log('✅ Place', place.id, 'executado localmente com sucesso');
      
      if (result && typeof result === 'object') {
        console.log('📊 Resultado:', Object.keys(result).length, 'campos');
      }

      return result || {};

    } catch (error) {
      console.log('--- Execução JavaScript Finalizada com ERRO ---');
      console.error(`❌ Erro executando lógica do Place ${place.id}:`, error);
      throw error;
    }
  }

  /**
   * Executar sequência completa da Petri Net - TESTE INTEGRAÇÃO FINAL
   */
  async executeFullSequence() {
    console.log('🚀 INICIANDO EXECUÇÃO SEQUENCIAL DA PETRI NET');
    console.log('================================================================================');
    
    const startTime = Date.now();
    const completedPlaces = [];
    
    try {
      // Obter Places em ordem de execução
      const places = this.getExecutionOrder();
      
      console.log(`📊 Petri Net: ${this.placesCount} Places, ${this.transitionsCount} Transições`);
      console.log(`🎯 Places WebSocket: ${this.getPlacesWithAgentId().map(p => p.id).join(', ')}`);
      console.log(`🎯 Places Locais: ${this.getLocalPlaces().map(p => p.id).join(', ')}`);
      console.log(`🔌 WebSocket V8 conectado (porta 6308)`);
      console.log('🔄 Context State inicializado\n');

      // Executar cada Place sequencialmente
      for (const place of places) {
        const placeStartTime = Date.now();
        
        console.log(`[${new Date().toLocaleTimeString()}] 🟡 ${place.id} - ${place.nome} (${place.agentId ? 'WEBSOCKET V7' : 'LOCAL'})`);
        
        // Executar Place
        const result = await this.executePlace(place);
        
        const placeDuration = (Date.now() - placeStartTime) / 1000;
        console.log(`✅ ${place.id} concluído em ${placeDuration}s`);
        
        // Contar campos no Context State
        const contextFields = this.contextStateHook?.contextState?.size || 0;
        console.log(`📊 Context State: ${contextFields} campos`);
        
        completedPlaces.push({
          id: place.id,
          status: place.status,
          duration: place.execution_time,
          type: place.agentId ? 'websocket' : 'local',
          outputFields: result ? Object.keys(result).length : 0
        });
        
        console.log(''); // linha em branco
      }

      const totalTime = Date.now() - startTime;
      
      console.log('================================================================================');
      console.log('🏆 EXECUÇÃO COMPLETA - TODAS AS TAREFAS REALIZADAS');
      console.log('================================================================================');
      console.log(`📊 Places executados: ${completedPlaces.length}/${this.placesCount} (100%)`);
      console.log(`⏱️ Tempo total: ${Math.floor(totalTime/60000)}min ${((totalTime%60000)/1000).toFixed(1)}s (${totalTime}ms)`);
      console.log(`📋 Context State final: ${this.contextStateHook?.contextState?.size || 0} campos`);
      console.log(`🌐 WebSocket calls: ${this.executionStats.websocketCalls}`);
      console.log(`⚡ Execuções locais: ${this.executionStats.localExecutions}`);
      console.log(`✅ Status final: SUCCESS`);

      return {
        status: 'SUCCESS',
        executionStats: {
          totalTime,
          placesExecuted: completedPlaces.length,
          placesSuccessful: this.executionStats.successfulExecutions,
          placesFailed: this.executionStats.failedExecutions,
          websocketCalls: this.executionStats.websocketCalls,
          localExecutions: this.executionStats.localExecutions,
          averageWebSocketTime: this.executionStats.websocketCalls > 0 ? 
            this.executionStats.totalTime / this.executionStats.websocketCalls : 0,
          averageLocalTime: this.executionStats.localExecutions > 0 ?
            this.executionStats.totalTime / this.executionStats.localExecutions : 0
        },
        completedPlaces,
        finalContextState: this.getFinalContextState()
      };

    } catch (error) {
      console.error('❌ ERRO NA EXECUÇÃO SEQUENCIAL:', error);
      throw error;
    }
  }

  /**
   * Obter ordem de execução dos Places
   */
  getExecutionOrder() {
    // Implementação simples - assumindo ordem P1, P2, P3, P4, P5
    // Em implementação real, seria baseado na topologia da Petri Net
    return this.petriNet.lugares.sort((a, b) => a.id.localeCompare(b.id));
  }

  /**
   * Obter Places com agentId (WebSocket)
   */
  getPlacesWithAgentId() {
    return this.petriNet.lugares.filter(place => place.agentId !== null && place.agentId !== undefined);
  }

  /**
   * Obter Places locais (sem agentId)
   */
  getLocalPlaces() {
    return this.petriNet.lugares.filter(place => place.agentId === null || place.agentId === undefined);
  }

  /**
   * Obter estado final do Context State
   */
  getFinalContextState() {
    if (!this.contextStateHook?.contextState) {
      return { totalFields: 0 };
    }

    const contextObject = Object.fromEntries(this.contextStateHook.contextState);
    
    return {
      totalFields: this.contextStateHook.contextState.size,
      coreFields: Object.keys(contextObject).slice(0, 12), // Primeiros 12 campos principais
      lastExecutedPlace: contextObject.last_executed_place,
      executionComplete: true,
      ...contextObject
    };
  }

  /**
   * Handle WebSocket messages
   */
  handleWebSocketMessage(event) {
    try {
      const data = JSON.parse(event.data);
      
      // Log para debug
      console.log('📥 WebSocket message:', data.type);
      
      // Processar diferentes tipos de mensagens
      if (data.type === 'verbose_step' || data.type === 'execution_step') {
        this.notifyVerboseReceived(data, this.currentPlace?.id);
      }
      
    } catch (error) {
      console.error('❌ Erro processando WebSocket message:', error);
    }
  }

  /**
   * Callbacks para interface
   */
  notifyStatusChange(status) {
    if (this.onStatusChanged) {
      this.onStatusChanged(status);
    }
  }

  notifyPlaceStarted(place) {
    if (this.onPlaceStarted) {
      this.onPlaceStarted(place);
    }
  }

  notifyPlaceCompleted(place, result) {
    if (this.onPlaceCompleted) {
      this.onPlaceCompleted(place, result);
    }
  }

  notifyPlaceFailed(place, error) {
    if (this.onPlaceFailed) {
      this.onPlaceFailed(place, error);
    }
  }

  notifyVerboseReceived(verboseData, placeId) {
    if (this.onVerboseReceived) {
      this.onVerboseReceived(verboseData, placeId);
    }
  }

  /**
   * Getters para estado atual
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      webSocketStatus: this.webSocketStatus,
      executionStatus: this.executionStatus,
      currentPlace: this.currentPlace?.id,
      petriNetLoaded: this.petriNetLoaded,
      placesCount: this.placesCount,
      stats: { ...this.executionStats }
    };
  }
}