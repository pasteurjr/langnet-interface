/**
 * ExecutionEngine - ETAPA 1 Motor Genérico
 * Classe para executar Petri Nets de forma genérica
 * Sistema genérico para qualquer projeto
 */

export class ExecutionEngine {
  constructor(projectConfig, contextStateManager, webSocketClient = null) {
    this.projectConfig = projectConfig;
    this.contextStateManager = contextStateManager;
    this.webSocketClient = webSocketClient;
    
    // Estados da execução
    this.isExecuting = false;
    this.currentPlace = null;
    this.executionHistory = [];
    this.pendingPlaces = [];
    
    // Callbacks para eventos
    this.callbacks = {
      onPlaceStarted: null,
      onPlaceCompleted: null,
      onPlaceError: null,
      onExecutionStarted: null,
      onExecutionCompleted: null,
      onExecutionError: null
    };

    console.log('🚀 ExecutionEngine inicializado:', {
      projectId: this.projectConfig?.id,
      adapter: this.projectConfig?.execution_config?.adapter_type,
      websocketUrl: this.projectConfig?.execution_config?.websocket_config?.url
    });
  }

  // Registra callbacks para eventos de execução
  on(eventName, callback) {
    if (this.callbacks.hasOwnProperty(`on${eventName.charAt(0).toUpperCase() + eventName.slice(1)}`)) {
      this.callbacks[`on${eventName.charAt(0).toUpperCase() + eventName.slice(1)}`] = callback;
    }
  }

  // Inicia execução da Petri Net
  async startExecution(startPlaceId = null) {
    try {
      if (this.isExecuting) {
        throw new Error('Execução já está em andamento');
      }

      console.log('▶️ Iniciando execução da Petri Net');
      this.isExecuting = true;
      this.executionHistory = [];
      
      // Callback de início
      if (this.callbacks.onExecutionStarted) {
        this.callbacks.onExecutionStarted(this.projectConfig);
      }

      // Inicializa Context State
      this.contextStateManager.initializeContextState(this.projectConfig);

      // Encontra Place inicial
      const startPlace = this.findStartPlace(startPlaceId);
      if (!startPlace) {
        throw new Error('Place inicial não encontrado');
      }

      console.log('🎯 Place inicial encontrado:', startPlace.nome);

      // Executa sequência de Places
      await this.executePlaceSequence(startPlace);

      // Callback de conclusão
      if (this.callbacks.onExecutionCompleted) {
        this.callbacks.onExecutionCompleted(this.executionHistory);
      }

      console.log('✅ Execução da Petri Net concluída');

    } catch (error) {
      console.error('❌ Erro na execução da Petri Net:', error);
      
      if (this.callbacks.onExecutionError) {
        this.callbacks.onExecutionError(error);
      }
      
      throw error;
    } finally {
      this.isExecuting = false;
      this.currentPlace = null;
    }
  }

  // Encontra Place inicial (com tokens > 0 ou especificado)
  findStartPlace(startPlaceId = null) {
    const places = this.projectConfig.petri_net_data?.lugares || [];
    
    if (startPlaceId) {
      return places.find(place => place.id === startPlaceId);
    }

    // Procura Place com tokens > 0
    const placeWithTokens = places.find(place => place.tokens > 0);
    if (placeWithTokens) {
      return placeWithTokens;
    }

    // Se não encontrar, pega o primeiro Place
    return places[0];
  }

  // Executa sequência de Places seguindo os arcos
  async executePlaceSequence(startPlace) {
    let currentPlace = startPlace;
    const visited = new Set();
    
    while (currentPlace && !visited.has(currentPlace.id)) {
      visited.add(currentPlace.id);
      
      // Executa Place atual
      const result = await this.executePlace(currentPlace);
      
      // Atualiza Context State com resultado
      if (result && typeof result === 'object') {
        this.contextStateManager.propagateToNextPlaces(result);
      }

      // Encontra próximo Place
      const nextPlace = this.findNextPlace(currentPlace);
      currentPlace = nextPlace;

      // Pequeno delay entre execuções
      await this.delay(500);
    }
  }

  // Executa um Place individual
  async executePlace(place) {
    try {
      console.log(`🔄 Executando Place: ${place.nome} (${place.id})`);
      
      this.currentPlace = place;
      
      // Callback de início do Place
      if (this.callbacks.onPlaceStarted) {
        this.callbacks.onPlaceStarted(place);
      }

      // Merge input_data com Context State
      const mergedInput = this.contextStateManager.mergeWithContextState(place.input_data || {});

      let result;

      // Executa baseado na presença de agentId
      if (place.agentId && this.webSocketClient) {
        // Execução via WebSocket V7
        result = await this.executeViaWebSocket(place, mergedInput);
      } else if (place.logica) {
        // Execução via JavaScript local
        result = await this.executeViaJavaScript(place, mergedInput);
      } else {
        // Place sem execução (apenas propagação)
        console.log(`⚪ Place ${place.nome} sem agentId/logica - apenas propagando dados`);
        result = mergedInput;
      }

      // Atualiza output_data do Place
      place.output_data = result || {};

      // Registra na história
      this.executionHistory.push({
        placeId: place.id,
        placeName: place.nome,
        agentId: place.agentId,
        input: mergedInput,
        output: result,
        timestamp: new Date().toISOString(),
        executionType: place.agentId ? 'websocket' : (place.logica ? 'javascript' : 'passthrough')
      });

      // Callback de conclusão do Place
      if (this.callbacks.onPlaceCompleted) {
        this.callbacks.onPlaceCompleted(place, result);
      }

      console.log(`✅ Place ${place.nome} executado com sucesso`);
      return result;

    } catch (error) {
      console.error(`❌ Erro executando Place ${place.nome}:`, error);
      
      // Callback de erro do Place
      if (this.callbacks.onPlaceError) {
        this.callbacks.onPlaceError(place, error);
      }

      throw error;
    }
  }

  // Execução via WebSocket V7
  async executeViaWebSocket(place, inputData) {
    if (!this.webSocketClient) {
      throw new Error('WebSocket client não configurado');
    }

    const taskName = this.extractTaskName(place);
    if (!taskName) {
      throw new Error(`Não foi possível extrair task name do Place ${place.nome}`);
    }

    console.log(`🌐 Executando via WebSocket V7: ${taskName}`);

    // Monta payload para WebSocket
    const payload = {
      task_name: taskName,
      inputs: inputData,
      place_id: place.id,
      agent_id: place.agentId,
      execution_id: `exec_${Date.now()}_${place.id}`
    };

    // Envia para WebSocket e aguarda resposta
    const response = await this.webSocketClient.executeTask(payload);
    
    console.log(`📨 Resposta WebSocket V7 para ${taskName}:`, response);
    
    return response;
  }

  // Execução via JavaScript local
  async executeViaJavaScript(place, inputData) {
    console.log(`⚡ Executando via JavaScript: ${place.nome}`);

    try {
      // Cria contexto seguro para execução
      const context = {
        input: inputData,
        place: place,
        contextState: this.contextStateManager.getContextState(),
        console: {
          log: (...args) => console.log(`[${place.nome}]`, ...args),
          error: (...args) => console.error(`[${place.nome}]`, ...args)
        }
      };

      // Executa código JavaScript do campo logica
      const func = new Function('context', `
        with(context) {
          ${place.logica}
        }
      `);

      const result = func(context);
      
      console.log(`✅ JavaScript executado para ${place.nome}:`, result);
      return result;

    } catch (error) {
      console.error(`❌ Erro executando JavaScript para ${place.nome}:`, error);
      throw new Error(`Erro JavaScript: ${error.message}`);
    }
  }

  // Extrai task name baseado no pattern do projeto
  extractTaskName(place) {
    const pattern = this.projectConfig.execution_config?.task_naming_pattern;
    
    if (!pattern) {
      // Sem pattern, usa nome direto
      return place.nome;
    }

    if (pattern === '(.+)_task') {
      // Pattern padrão: remove '_task' do final
      return place.nome.replace('_task', '');
    } else if (pattern === 'TASK_(.+)_EXEC') {
      // Pattern VALEP1: extrai nome entre TASK_ e _EXEC
      const match = place.nome.match(/^TASK_(.+)_EXEC$/);
      return match ? match[1] : place.nome;
    }

    // Pattern customizado com regex
    try {
      const regex = new RegExp(pattern);
      const match = place.nome.match(regex);
      return match && match[1] ? match[1] : place.nome;
    } catch (error) {
      console.warn(`⚠️ Pattern regex inválido: ${pattern}, usando nome direto`);
      return place.nome;
    }
  }

  // Encontra próximo Place seguindo os arcos
  findNextPlace(currentPlace) {
    const arcos = this.projectConfig.petri_net_data?.arcos || [];
    const places = this.projectConfig.petri_net_data?.lugares || [];

    // Encontra arcos que saem do Place atual
    const outgoingArcs = arcos.filter(arco => arco.origem === currentPlace.id);

    if (outgoingArcs.length === 0) {
      console.log(`🏁 Nenhum arco de saída encontrado para ${currentPlace.nome}`);
      return null;
    }

    // Por simplicidade, pega o primeiro arco (em sistemas complexos seria baseado em condições)
    const nextArc = outgoingArcs[0];
    
    // Verifica se destino é transição ou place
    let targetId = nextArc.destino;

    // Se destino é uma transição, encontra o Place conectado à transição
    const transicoes = this.projectConfig.petri_net_data?.transicoes || [];
    const isTransition = transicoes.some(trans => trans.id === targetId);

    if (isTransition) {
      // Encontra arcos que saem da transição
      const transitionOutArcs = arcos.filter(arco => arco.origem === targetId);
      if (transitionOutArcs.length > 0) {
        targetId = transitionOutArcs[0].destino;
      }
    }

    // Encontra o Place de destino
    const nextPlace = places.find(place => place.id === targetId);
    
    if (nextPlace) {
      console.log(`➡️ Próximo Place: ${nextPlace.nome} (${nextPlace.id})`);
    }

    return nextPlace;
  }

  // Pausa execução
  async pauseExecution() {
    console.log('⏸️ Pausando execução');
    this.isExecuting = false;
  }

  // Resume execução
  async resumeExecution() {
    console.log('▶️ Resumindo execução');
    this.isExecuting = true;
  }

  // Para execução
  async stopExecution() {
    console.log('⏹️ Parando execução');
    this.isExecuting = false;
    this.currentPlace = null;
    this.pendingPlaces = [];
  }

  // Reset completo
  async resetExecution() {
    console.log('🔄 Reset da execução');
    await this.stopExecution();
    this.executionHistory = [];
    this.contextStateManager.clearContextState();
  }

  // Utilitários
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Getters para estado atual
  getCurrentPlace() {
    return this.currentPlace;
  }

  getExecutionHistory() {
    return [...this.executionHistory];
  }

  isCurrentlyExecuting() {
    return this.isExecuting;
  }

  getProjectConfig() {
    return this.projectConfig;
  }

  // Validação da configuração
  validateConfiguration() {
    const errors = [];

    if (!this.projectConfig) {
      errors.push('Configuração do projeto não fornecida');
    }

    if (!this.projectConfig?.petri_net_data?.lugares) {
      errors.push('Dados da Petri Net não encontrados');
    }

    if (!this.contextStateManager) {
      errors.push('Context State Manager não fornecido');
    }

    const places = this.projectConfig?.petri_net_data?.lugares || [];
    const placesWithAgent = places.filter(place => place.agentId);
    
    if (placesWithAgent.length > 0 && !this.webSocketClient) {
      errors.push('WebSocket client necessário para Places com agentId');
    }

    if (errors.length > 0) {
      console.error('❌ Erros de configuração:', errors);
      return { valid: false, errors };
    }

    console.log('✅ Configuração válida');
    return { valid: true, errors: [] };
  }

  // Debug info
  getDebugInfo() {
    return {
      projectId: this.projectConfig?.id,
      adapterType: this.projectConfig?.execution_config?.adapter_type,
      taskNamingPattern: this.projectConfig?.execution_config?.task_naming_pattern,
      totalPlaces: this.projectConfig?.petri_net_data?.lugares?.length || 0,
      placesWithAgent: this.projectConfig?.petri_net_data?.lugares?.filter(p => p.agentId)?.length || 0,
      placesWithLogica: this.projectConfig?.petri_net_data?.lugares?.filter(p => p.logica)?.length || 0,
      isExecuting: this.isExecuting,
      currentPlace: this.currentPlace?.nome || null,
      executionHistoryCount: this.executionHistory.length,
      contextStateKeys: Object.keys(this.contextStateManager.getContextState()).length
    };
  }
}