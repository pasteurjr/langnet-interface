/**
 * PetriNetSimulator.js
 * 
 * Módulo responsável pela simulação de Redes de Petri
 * Implementa matrizes de incidência, lógica de disparo e controle de simulação
 * corrigido para arcos inibidores 
 * Inclui suporte a guards e processamento de places
 */

import { GuardEvaluator } from './GuardEvaluator';
import { PlaceProcessor } from './PlaceProcessor';

export class PetriNetSimulator {
  constructor(petriNet) {
    this.petriNet = petriNet;
    this.preMatrix = {}; // Matriz de pré-condição (entrada)
    this.postMatrix = {}; // Matriz de pós-condição (saída)
    this.markingVector = {}; // Vetor de marcação (tokens)
    this.simulationLog = []; // Log de disparos
    this.isSimulating = false;
    this.currentHighlightedTransition = null;
    
    // Inicializar módulos auxiliares
    this.guardEvaluator = new GuardEvaluator(petriNet, this.markingVector);
    this.placeProcessor = new PlaceProcessor(petriNet, this.markingVector);
    
    // Configurar callbacks do processador de places
    this.placeProcessor.setCallbacks({
      onPlaceProcessed: (placeId, inputData, outputData) => {
        console.log(`✅ Place ${placeId} processado:`, { inputData, outputData });
      },
      onError: (placeId, error) => {
        console.error(`❌ Erro no processamento do place ${placeId}:`, error);
      }
    });
    
    this.initializeMatrices();
  }

  /**
   * Inicializa as matrizes de incidência e o vetor de marcação
   */
  initializeMatrices() {
    const { lugares, transicoes, arcos } = this.petriNet;
    
    // Inicializar matrizes vazias
    this.preMatrix = {};
    this.postMatrix = {};
    this.markingVector = {};
    
    // Inicializar vetor de marcação com tokens atuais dos lugares
    lugares.forEach(lugar => {
      this.markingVector[lugar.id] = lugar.tokens || 0;
    });
    
    // Inicializar matrizes com zeros
    lugares.forEach(lugar => {
      this.preMatrix[lugar.id] = {};
      this.postMatrix[lugar.id] = {};
      
      transicoes.forEach(transicao => {
        this.preMatrix[lugar.id][transicao.id] = 0;
        this.postMatrix[lugar.id][transicao.id] = 0;
      });
    });
    
    // Preencher matrizes com base nos arcos
    arcos.forEach(arco => {
      const { origem, destino, peso } = arco;
      
      // Verificar se é arco de lugar para transição (pré-condição)
      const lugarOrigem = lugares.find(l => l.id === origem);
      const transicaoDestino = transicoes.find(t => t.id === destino);
      
      if (lugarOrigem && transicaoDestino) {
        this.preMatrix[origem][destino] = peso ?? 1;
      }
      
      // Verificar se é arco de transição para lugar (pós-condição)
      const transicaoOrigem = transicoes.find(t => t.id === origem);
      const lugarDestino = lugares.find(l => l.id === destino);
      
      if (transicaoOrigem && lugarDestino) {
        this.postMatrix[destino][origem] = peso ?? 1;
      }
    });
    
    // Adicionar lugares virtuais para transições de interface de entrada
    this.addVirtualPlacesForInterfaceTransitions();
  }

  /**
   * Adiciona lugares virtuais para transições de interface de entrada
   * para evitar que estejam sempre aptas
   */
  addVirtualPlacesForInterfaceTransitions() {
    const { transicoes } = this.petriNet;
    
    transicoes.forEach(transicao => {
      if (transicao.isInterface && transicao.interfaceType === 'entrada') {
        const virtualPlaceId = `VIRTUAL_${transicao.id}`;
        
        console.log(`🔧 Criando place virtual para transição de interface: ${virtualPlaceId}`);
        
        // Adicionar lugar virtual ao vetor de marcação com 1 token
        this.markingVector[virtualPlaceId] = 1;
        
        // Adicionar entrada na matriz de pré-condição
        this.preMatrix[virtualPlaceId] = {};
        this.postMatrix[virtualPlaceId] = {};
        
        // Inicializar com zeros para todas as transições
        Object.keys(this.preMatrix).forEach(lugarId => {
          if (lugarId !== virtualPlaceId) {
            this.preMatrix[lugarId][transicao.id] = this.preMatrix[lugarId][transicao.id] || 0;
            this.postMatrix[lugarId][transicao.id] = this.postMatrix[lugarId][transicao.id] || 0;
          }
        });
        
        // Configurar o lugar virtual como entrada da transição de interface
        this.preMatrix[virtualPlaceId][transicao.id] = 1;
        
        // Inicializar pós-condição para o lugar virtual
        Object.keys(this.postMatrix[Object.keys(this.postMatrix)[0]] || {}).forEach(transicaoId => {
          this.postMatrix[virtualPlaceId][transicaoId] = 0;
        });
        
        console.log(`✅ Place virtual ${virtualPlaceId} criado com 1 token`);
      }
    });
  }

  /**
   * Verifica se uma transição está apta a disparar
   */
  isTransitionEnabled(transitionId) {
    // Primeira verificação: pré-condições estruturais (arcos)
    const { arcos } = this.petriNet;
    
    // Verificar arcos normais da rede
    for (const arco of arcos) {
      if (arco.destino === transitionId) {
        const lugarId = arco.origem;
        const tokens = this.markingVector[lugarId] || 0;
        const peso = arco.peso ?? 1;
        
        if (peso > 0) {
          // Arco normal: lugar deve ter pelo menos 'peso' tokens
          if (tokens < peso) {
            console.log(`❌ ${transitionId} não apta: ${lugarId} tem ${tokens} < ${peso}`);
            return false;
          }
        } else if (peso === 0) {
          // Arco inibidor: lugar deve ter exatamente 0 tokens  
          if (tokens !== 0) {
            console.log(`❌ ${transitionId} não apta: arco inibidor ${lugarId} tem ${tokens} ≠ 0`);
            return false;
          }
        }
      }
    }
    
    // Verificar places virtuais (para transições de interface)
    const virtualPlaceId = `VIRTUAL_${transitionId}`;
    if (this.markingVector[virtualPlaceId] !== undefined) {
      const virtualTokens = this.markingVector[virtualPlaceId];
      if (virtualTokens < 1) {
        console.log(`❌ ${transitionId} não apta: place virtual ${virtualPlaceId} tem ${virtualTokens} < 1`);
        return false;
      }
    }
    
    // Segunda verificação: guard da transição (se existir)
    const transition = this.petriNet.transicoes.find(t => t.id === transitionId);
    if (transition) {
      // Atualizar contexto do avaliador de guards
      this.guardEvaluator.updateContext(this.petriNet, this.markingVector);
      
      // Avaliar guard
      const guardResult = this.guardEvaluator.evaluateGuard(transition);
      if (!guardResult) {
        console.log(`❌ ${transitionId} não apta: guard falhou`);
        return false;
      }
    }
    
    console.log(`✅ ${transitionId} está APTA!`);
    return true;
  }

  /**
   * Retorna todas as transições aptas a disparar
   */
  getEnabledTransitions() {
    const { transicoes } = this.petriNet;
    console.log(`🔍 Verificando ${transicoes.length} transições para aptidão...`);
    
    const enabled = transicoes.filter(transicao => {
      const isEnabled = this.isTransitionEnabled(transicao.id);
      console.log(`🔍 Transição ${transicao.id} (${transicao.nome}): ${isEnabled ? 'APTA' : 'NÃO APTA'}`);
      
      if (transicao.isInterface) {
        console.log(`🏛️ TRANSIÇÃO DE INTERFACE: ${transicao.id}, tipo: ${transicao.interfaceType}, apta: ${isEnabled}`);
        if (transicao.interfaceType === 'entrada') {
          const virtualPlaceId = `VIRTUAL_${transicao.id}`;
          const virtualTokens = this.markingVector[virtualPlaceId];
          console.log(`🔧 Place virtual ${virtualPlaceId}: ${virtualTokens} tokens`);
        }
      }
      
      return isEnabled;
    });
    
    console.log(`✅ ${enabled.length} transições aptas encontradas:`, enabled.map(t => t.id));
    return enabled;
  }

  /**
   * Dispara uma transição específica
   */
  fireTransition(transitionId) {
    if (!this.isTransitionEnabled(transitionId)) {
      throw new Error(`Transição ${transitionId} não está apta a disparar`);
    }

    const transicao = this.petriNet.transicoes.find(t => t.id === transitionId);
    if (!transicao) {
      throw new Error(`Transição ${transitionId} não encontrada`);
    }

    // Armazenar estado anterior para o log
    const estadoAnterior = { ...this.markingVector };
    
    // Remover tokens dos lugares de entrada usando matriz de pré-condição
    Object.keys(this.preMatrix).forEach(lugarId => {
      const peso = this.preMatrix[lugarId][transitionId];
      if (peso > 0) {
        this.markingVector[lugarId] = (this.markingVector[lugarId] || 0) - peso;
        console.log(`🔥 Removendo ${peso} tokens de ${lugarId}, restam: ${this.markingVector[lugarId]}`);
      }
      // Arco inibidor (peso = 0): NÃO remove tokens
    });
    
    // Adicionar tokens aos lugares de saída usando matriz de pós-condição
    const processedPlaces = [];
    Object.keys(this.postMatrix).forEach(lugarId => {
      const peso = this.postMatrix[lugarId][transitionId];
      if (peso > 0) {
        this.markingVector[lugarId] = (this.markingVector[lugarId] || 0) + peso;
        console.log(`🪙 Adicionando ${peso} tokens a ${lugarId}, total: ${this.markingVector[lugarId]}`);
        
        // Marcar place para processamento
        processedPlaces.push(lugarId);
      }
    });

    // Atualizar tokens nos lugares reais da Petri Net
    this.updatePetriNetTokens();
    
    // Processar places que receberam tokens
    this.processPlacesAfterFiring(processedPlaces, transitionId);
    
    // Adicionar ao log
    this.addToSimulationLog(transitionId, estadoAnterior, { ...this.markingVector });
    
    return {
      transitionId,
      transitionName: transicao.nome,
      previousMarking: estadoAnterior,
      newMarking: { ...this.markingVector }
    };
  }

  /**
   * Atualiza os tokens nos lugares reais da Petri Net
   */
  updatePetriNetTokens() {
    this.petriNet.lugares.forEach(lugar => {
      if (this.markingVector[lugar.id] !== undefined) {
        lugar.tokens = this.markingVector[lugar.id];
      }
    });
  }

  /**
   * Seleciona uma transição aleatoriamente entre as aptas
   */
  selectRandomEnabledTransition() {
    const enabledTransitions = this.getEnabledTransitions();
    
    if (enabledTransitions.length === 0) {
      return null;
    }
    
    if (enabledTransitions.length === 1) {
      return enabledTransitions[0];
    }
    
    // Aplicar regras de seleção aleatória
    const conflictGroups = this.groupTransitionsByConflict(enabledTransitions);
    
    // Selecionar um grupo de conflito aleatoriamente
    const randomGroupIndex = Math.floor(Math.random() * conflictGroups.length);
    const selectedGroup = conflictGroups[randomGroupIndex];
    
    // Selecionar uma transição aleatoriamente dentro do grupo
    const randomTransitionIndex = Math.floor(Math.random() * selectedGroup.length);
    return selectedGroup[randomTransitionIndex];
  }

  /**
   * Agrupa transições por conflito (compartilham lugares de entrada)
   */
  groupTransitionsByConflict(transitions) {
    const groups = [];
    const processed = new Set();
    
    transitions.forEach(transition => {
      if (processed.has(transition.id)) return;
      
      const group = [transition];
      processed.add(transition.id);
      
      // Encontrar lugares de entrada desta transição
      const inputPlaces = Object.keys(this.preMatrix).filter(
        lugarId => this.preMatrix[lugarId][transition.id] > 0
      );
      
      // Encontrar outras transições que compartilham esses lugares
      transitions.forEach(otherTransition => {
        if (processed.has(otherTransition.id)) return;
        
        const otherInputPlaces = Object.keys(this.preMatrix).filter(
          lugarId => this.preMatrix[lugarId][otherTransition.id] > 0
        );
        
        // Verificar se há interseção nos lugares de entrada
        const hasSharedPlace = inputPlaces.some(place => otherInputPlaces.includes(place));
        
        if (hasSharedPlace) {
          group.push(otherTransition);
          processed.add(otherTransition.id);
        }
      });
      
      groups.push(group);
    });
    
    return groups;
  }

  /**
   * Adiciona entrada ao log de simulação
   */
  addToSimulationLog(transitionId, previousMarking, newMarking) {
    const transicao = this.petriNet.transicoes.find(t => t.id === transitionId);
    const timestamp = new Date().toLocaleTimeString();
    
    // Identificar lugares afetados (que tiveram mudança de tokens)
    const affectedPlaces = [];
    Object.keys(previousMarking).forEach(lugarId => {
      if (previousMarking[lugarId] !== newMarking[lugarId]) {
        const lugar = this.petriNet.lugares.find(l => l.id === lugarId);
        if (lugar) { // Só incluir lugares reais (não virtuais)
          affectedPlaces.push({
            id: lugarId,
            name: lugar.nome,
            previousTokens: previousMarking[lugarId],
            newTokens: newMarking[lugarId]
          });
        }
      }
    });
    
    this.simulationLog.push({
      timestamp,
      transitionId,
      transitionName: transicao ? transicao.nome : transitionId,
      affectedPlaces
    });
  }

  /**
   * Limpa o log de simulação
   */
  clearSimulationLog() {
    this.simulationLog = [];
  }

  /**
   * Reseta a simulação para o estado inicial
   */
  resetSimulation() {
    this.clearSimulationLog();
    this.isSimulating = false;
    this.currentHighlightedTransition = null;
    this.initializeMatrices();
  }

  /**
   * Retorna o estado atual da simulação
   */
  getSimulationState() {
    return {
      isSimulating: this.isSimulating,
      markingVector: { ...this.markingVector },
      enabledTransitions: this.getEnabledTransitions(),
      simulationLog: [...this.simulationLog],
      currentHighlightedTransition: this.currentHighlightedTransition
    };
  }

  /**
   * Inicia a simulação
   */
  startSimulation() {
    this.isSimulating = true;
    this.clearSimulationLog();
  }

  /**
   * Para a simulação
   */
  stopSimulation() {
    this.isSimulating = false;
    this.currentHighlightedTransition = null;
  }

  /**
   * Obtém o vetor de marcação atual como objeto
   * @returns {Object} Mapeamento de place ID para número de tokens
   */
  getMarkingVector() {
    return { ...this.markingVector };
  }

  /**
   * Processa places que receberam tokens após disparo de transição
   * @param {Array<string>} placeIds - IDs dos places que receberam tokens
   * @param {string} fromTransitionId - ID da transição que disparou
   */
  processPlacesAfterFiring(placeIds, fromTransitionId) {
    // Atualizar contexto do processador
    this.placeProcessor.updateContext(this.petriNet, this.markingVector);
    
    // Processar cada place que recebeu tokens
    placeIds.forEach(placeId => {
      // Encontrar o place real (não virtual)
      const place = this.petriNet.lugares.find(p => p.id === placeId);
      if (!place || placeId.startsWith('VIRTUAL_')) {
        return; // Pular places virtuais
      }
      
      console.log(`🔄 Processando place ${placeId} após disparo de ${fromTransitionId}`);
      
      // Dados a serem passados para o processamento
      const tokenData = {
        from_transition: fromTransitionId,
        received_at: Date.now(),
        tokens_received: this.markingVector[placeId] || 0
      };
      
      // Processar o place
      this.placeProcessor.processPlace(placeId, tokenData);
    });
  }

  /**
   * Cancela todos os processamentos de places em andamento
   */
  cancelAllProcessing() {
    this.placeProcessor.cancelAllProcessing();
  }

  /**
   * Obtém lista de places sendo processados
   * @returns {Array<string>} - Array com IDs dos places
   */
  getProcessingPlaces() {
    return this.placeProcessor.getProcessingPlaces();
  }

  /**
   * Atualiza a rede de Petri e reinicializa contextos
   * @param {Object} newPetriNet - Nova rede de Petri
   */
  updatePetriNet(newPetriNet) {
    this.petriNet = newPetriNet;
    this.initializeMatrices();
    
    // Atualizar contextos dos módulos auxiliares
    this.guardEvaluator.updateContext(this.petriNet, this.markingVector);
    this.placeProcessor.updateContext(this.petriNet, this.markingVector);
  }
}

export default PetriNetSimulator;

