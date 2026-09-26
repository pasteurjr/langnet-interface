// Motor de Execução da Petri Net - Baseado no petri-net-editor e AgentsModule1Page
// Gerencia estados, transições e execução de tarefas via WebSocket

class PetriNetEngine {
  constructor(petriNetData) {
    this.petriNetData = petriNetData;
    this.places = {};
    this.transitions = {};
    this.marking = {};
    this.executionLog = [];
    this.isRunning = false;
    this.callbacks = {
      onPlaceExecute: null,
      onTransitionFire: null,
      onExecutionComplete: null,
      onLog: null
    };
    
    this.initializeFromData();
  }

  // Inicializa a Petri Net a partir dos dados do projeto
  initializeFromData() {
    if (!this.petriNetData?.lugares || !this.petriNetData?.transicoes) {
      console.error('Dados da Petri Net inválidos');
      return;
    }

    // Inicializar places
    this.petriNetData.lugares.forEach(place => {
      this.places[place.id] = {
        id: place.id,
        nome: place.nome,
        agentId: place.agentId,
        tokens: place.tokens || 0,
        initialTokens: place.tokens || 0,
        coordenadas: place.coordenadas,
        delay: place.delay || 0,
        subnet: place.subnet || {},
        status: 'pending', // pending, running, completed, error
        inputs: place.inputs || [],
        input_data: place.input_data || {},
        outputs: place.outputs || [],
        logica: place.logica || null, // WebSocket endpoint
        executionTime: 0,
        lastExecution: null
      };
      
      this.marking[place.id] = place.tokens || 0;
    });

    // Inicializar transitions
    this.petriNetData.transicoes.forEach(transition => {
      this.transitions[transition.id] = {
        id: transition.id,
        nome: transition.nome,
        origem: transition.origem,
        destino: transition.destino,
        peso: transition.peso || 1,
        condicao: transition.condicao || null,
        coordenadas: transition.coordenadas,
        status: 'idle', // idle, enabled, firing, fired
        lastFired: null
      };
    });

    this.log('Petri Net inicializada', {
      places: Object.keys(this.places).length,
      transitions: Object.keys(this.transitions).length,
      initialMarking: { ...this.marking }
    });
  }

  // Registrar callbacks para eventos
  setCallbacks(callbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  // Logging centralizado
  log(message, data = null) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      message,
      data,
      marking: { ...this.marking }
    };
    
    this.executionLog.push(logEntry);
    
    if (this.callbacks.onLog) {
      this.callbacks.onLog(logEntry);
    }
    
    console.log(`[PetriNetEngine] ${message}`, data);
  }

  // Extrair Context State dos outputs de um Place
  extractContextStateFromOutputs(outputs) {
    if (!outputs || !Array.isArray(outputs)) {
      return {};
    }

    // Se outputs contém objetos, fazer merge de todos
    let contextData = {};
    
    outputs.forEach(output => {
      if (typeof output === 'object' && output !== null) {
        contextData = { ...contextData, ...output };
      } else if (typeof output === 'string') {
        try {
          // Tentar parsear string como JSON
          const parsed = JSON.parse(output);
          if (typeof parsed === 'object') {
            contextData = { ...contextData, ...parsed };
          }
        } catch {
          // Se não for JSON, ignorar
        }
      }
    });

    return contextData;
  }

  // Obter transições habilitadas
  getEnabledTransitions() {
    const enabled = [];
    
    Object.values(this.transitions).forEach(transition => {
      if (this.isTransitionEnabled(transition.id)) {
        enabled.push(transition.id);
        this.transitions[transition.id].status = 'enabled';
      } else {
        this.transitions[transition.id].status = 'idle';
      }
    });

    return enabled;
  }

  // Verificar se uma transição está habilitada
  isTransitionEnabled(transitionId) {
    const transition = this.transitions[transitionId];
    if (!transition) return false;

    // Verificar se place origem tem tokens suficientes
    const sourcePlace = this.places[transition.origem];
    if (!sourcePlace || this.marking[transition.origem] < transition.peso) {
      return false;
    }

    // NOVA REGRA: Verificar se Place origem completou execução (se tem agentId ou lógica)
    if (sourcePlace.agentId || sourcePlace.logica) {
      if (sourcePlace.status !== 'completed') {
        this.log(`🛡️ Transição ${transitionId} aguardando execução de ${sourcePlace.id} (status: ${sourcePlace.status})`);
        return false;
      }
    }

    // Verificar guard usando GuardEvaluator se existir
    if (transition.guard) {
      // O GuardEvaluator será usado no PetriNetSimulator
      // Por enquanto, permitir transições sempre que chegam aqui
      this.log(`🛡️ Transição ${transitionId} tem guard: ${transition.guard} (será avaliado pelo GuardEvaluator)`);
    }

    // Verificar condição customizada legacy se existir
    if (transition.condicao) {
      try {
        // Avaliar condição (poderia ser JavaScript ou lógica customizada)
        return eval(transition.condicao);
      } catch (e) {
        console.warn(`Erro na condição da transição ${transitionId}:`, e);
        return false;
      }
    }

    return true;
  }

  // Disparar uma transição
  async fireTransition(transitionId) {
    const transition = this.transitions[transitionId];
    if (!transition || !this.isTransitionEnabled(transitionId)) {
      this.log(`Transição ${transitionId} não pode ser disparada`);
      return false;
    }

    this.log(`Disparando transição ${transitionId}`, { transition });
    
    transition.status = 'firing';
    transition.lastFired = new Date().toISOString();

    // Notificar callback
    if (this.callbacks.onTransitionFire) {
      this.callbacks.onTransitionFire(transitionId, transition);
    }

    // ✅ CRÍTICO: Propagar dados EXATAMENTE como no testar_interface (line 392)
    const sourcePlace = this.places[transition.origem];
    const destPlace = this.places[transition.destino];

    // ✅ FORMATO IDÊNTICO ao testar_interface: result da tarefa anterior vira input_data da próxima
    if (sourcePlace && destPlace && sourcePlace.outputs && sourcePlace.outputs.length > 0) {
      // No testar_interface: executeTask(nextTask, result) - result é passado diretamente
      const taskResult = sourcePlace.outputs[0]; // Primeiro output é o resultado principal

      if (taskResult && typeof taskResult === 'object') {
        // ✅ SUBSTITUIR input_data completamente com resultado da tarefa anterior
        // IDÊNTICO ao formato do testar_interface: startNextTask passa result como input_data
        destPlace.input_data = taskResult;

        this.log(`📤 [PETRI ENGINE] Dados REAIS propagados formato testar_interface ${sourcePlace.id} → ${destPlace.id}:`, {
          resultFields: Object.keys(taskResult),
          sourceTask: sourcePlace.nome,
          destTask: destPlace.nome
        });
      } else {
        this.log(`⚠️ [PETRI ENGINE] Resultado inválido de ${sourcePlace.id} - mantendo input_data vazio`);
        destPlace.input_data = {};
      }
    } else {
      // Place de origem não tem outputs ou é tarefa inicial
      if (!sourcePlace?.outputs?.length) {
        this.log(`🚀 [PETRI ENGINE] ${destPlace?.id} é tarefa inicial - input_data será null`);
        if (destPlace) destPlace.input_data = null; // Formato testar_interface para read_email
      }
    }

    // Remover tokens do place origem
    this.marking[transition.origem] -= transition.peso;

    // Adicionar tokens ao place destino
    this.marking[transition.destino] += transition.peso;

    // Atualizar status dos places
    this.places[transition.origem].tokens = this.marking[transition.origem];
    this.places[transition.destino].tokens = this.marking[transition.destino];

    // ✅ CRÍTICO: Executar tarefa DEPOIS da propagação
    if (this.marking[transition.destino] > 0) {
      console.log(`⚡ [PETRI ENGINE] Executando Place ${transition.destino} com dados REAIS propagados`);
      await this.executePlaceTask(transition.destino);
    }

    transition.status = 'fired';
    return true;
  }

  // Executar tarefa de um place
  async executePlaceTask(placeId) {
    const place = this.places[placeId];
    if (!place) return;

    this.log(`Executando tarefa do place ${placeId}`, { place });
    
    place.status = 'running';
    place.lastExecution = new Date().toISOString();
    const startTime = Date.now();

    // Notificar callback
    if (this.callbacks.onPlaceExecute) {
      this.callbacks.onPlaceExecute(placeId, place);
    }

    try {
      let outputs = [];
      
      // Se tem lógica WebSocket, executar
      if (place.logica) {
        outputs = await this.executeWebSocketTask(place);
      } else {
        // Simulação simples com propagação de context state
        await new Promise(resolve => setTimeout(resolve, place.delay || 1000));
        
        const inputData = place.input_data || {};
        const hasContextState = Object.keys(inputData).length > 0;
        
        // Output mantém context state + adiciona novos dados
        outputs = [
          {
            ...inputData,
            placeId: place.id,
            placeName: place.nome,
            executedAt: new Date().toISOString(),
            simulationResult: `Simulation result from ${place.nome}`,
            [`${place.id}_processed`]: true,
            [`${place.id}_timestamp`]: Date.now()
          }
        ];
        
        this.log(`✅ Simulação ${place.id} concluída:`, {
          outputFields: Object.keys(outputs[0]),
          propagatedContext: hasContextState
        });
      }

      place.outputs = outputs;
      place.status = 'completed';
      place.executionTime = Date.now() - startTime;
      
      this.log(`Tarefa ${placeId} concluída`, { 
        outputs, 
        executionTime: place.executionTime 
      });

    } catch (error) {
      place.status = 'error';
      place.executionTime = Date.now() - startTime;
      
      this.log(`Erro na execução da tarefa ${placeId}`, { 
        error: error.message 
      });
    }
  }

  // Executar tarefa via WebSocket
  async executeWebSocketTask(place) {
    return new Promise((resolve, reject) => {
      try {
        // Log dos dados de entrada disponíveis
        const inputData = place.input_data || {};
        const hasContextState = Object.keys(inputData).length > 0;
        
        this.log(`📡 Executando WebSocket ${place.id}:`, {
          inputData: hasContextState ? Object.keys(inputData) : 'vazio',
          contextFields: Object.keys(inputData).length
        });
        
        // Simular execução WebSocket usando dados de entrada
        setTimeout(() => {
          const outputs = [
            {
              // Propagar context state recebido + novos dados
              ...inputData,
              placeId: place.id,
              placeName: place.nome,
              agentId: place.agentId,
              executedAt: new Date().toISOString(),
              webSocketResult: `WebSocket execution result from ${place.nome}`,
              // Adicionar novos campos para próximo Place
              [`${place.id}_processed`]: true,
              [`${place.id}_timestamp`]: Date.now()
            }
          ];
          
          this.log(`✅ WebSocket ${place.id} concluído:`, {
            outputFields: Object.keys(outputs[0]),
            propagatedContext: hasContextState
          });
          
          resolve(outputs);
        }, place.delay || 2000);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  // Executar um passo da Petri Net
  async executeStep() {
    if (!this.isRunning) return false;

    const enabledTransitions = this.getEnabledTransitions();
    
    if (enabledTransitions.length === 0) {
      this.log('Nenhuma transição habilitada - execução pausada');
      return false;
    }

    // Escolher primeira transição habilitada (ou implementar lógica de escolha)
    const chosenTransition = enabledTransitions[0];
    await this.fireTransition(chosenTransition);
    
    return true;
  }

  // Executar automaticamente
  async executeAuto(intervalMs = 2000) {
    this.isRunning = true;
    this.log('Iniciando execução automática');

    while (this.isRunning) {
      const hasStep = await this.executeStep();
      
      if (!hasStep) {
        break; // Não há mais passos possíveis
      }
      
      // Aguardar intervalo antes do próximo passo
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }

    this.isRunning = false;
    this.log('Execução automática finalizada');
    
    if (this.callbacks.onExecutionComplete) {
      this.callbacks.onExecutionComplete(this.getExecutionSummary());
    }
  }

  // Pausar execução
  pause() {
    this.isRunning = false;
    this.log('Execução pausada');
  }

  // Resetar Petri Net
  reset() {
    this.isRunning = false;
    
    // Restaurar marcação inicial
    Object.values(this.places).forEach(place => {
      place.tokens = place.initialTokens;
      place.status = 'pending';
      place.outputs = [];
      place.executionTime = 0;
      place.lastExecution = null;
      this.marking[place.id] = place.initialTokens;
    });

    // Resetar transições
    Object.values(this.transitions).forEach(transition => {
      transition.status = 'idle';
      transition.lastFired = null;
    });

    this.executionLog = [];
    this.log('Petri Net resetada');
  }

  // Obter resumo da execução
  getExecutionSummary() {
    const totalPlaces = Object.keys(this.places).length;
    const completedPlaces = Object.values(this.places).filter(p => p.status === 'completed').length;
    const runningPlaces = Object.values(this.places).filter(p => p.status === 'running').length;
    const errorPlaces = Object.values(this.places).filter(p => p.status === 'error').length;

    return {
      totalPlaces,
      completedPlaces,
      runningPlaces,
      errorPlaces,
      progress: (completedPlaces / totalPlaces) * 100,
      isRunning: this.isRunning,
      marking: { ...this.marking },
      executionLog: [...this.executionLog]
    };
  }

  // Obter estado atual
  getCurrentState() {
    return {
      places: { ...this.places },
      transitions: { ...this.transitions },
      marking: { ...this.marking },
      isRunning: this.isRunning,
      summary: this.getExecutionSummary()
    };
  }
}

export default PetriNetEngine;