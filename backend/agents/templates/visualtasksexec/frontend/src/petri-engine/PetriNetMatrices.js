/**
 * PetriNetMatrices.js
 * Módulo para criar e gerenciar matrizes de simulação de Redes de Petri novo
 */

export class PetriNetSimulationMatrices {
  constructor(petriNet) {
    this.petriNet = petriNet;
    this.places = [];
    this.transitions = [];
    this.inputMatrix = []; // I- (transições × places)
    this.outputMatrix = []; // I+ (transições × places) 
    this.markingVector = []; // M (places)
    
    this.buildMatrices();
  }

  /**
   * Constrói as matrizes de simulação a partir da estrutura da rede de Petri
   */
  buildMatrices() {
    if (!this.petriNet) return;

    // Coletar todos os places e transições
    this.places = this.petriNet.lugares || [];
    this.transitions = this.petriNet.transicoes || [];
    
    const numPlaces = this.places.length;
    const numTransitions = this.transitions.length;

    // Inicializar matrizes
    this.inputMatrix = Array(numTransitions).fill().map(() => Array(numPlaces).fill(0));
    this.outputMatrix = Array(numTransitions).fill().map(() => Array(numPlaces).fill(0));
    this.markingVector = Array(numPlaces).fill(0);

    // Preencher vetor de marcação inicial
    this.places.forEach((place, placeIndex) => {
      this.markingVector[placeIndex] = place.tokens || 0;
    });

    // Processar arcos para preencher matrizes
    if (this.petriNet.arcos) {
      this.petriNet.arcos.forEach(arco => {
        const placeIndex = this.places.findIndex(p => p.id === arco.origem || p.id === arco.destino);
        const transitionIndex = this.transitions.findIndex(t => t.id === arco.origem || t.id === arco.destino);
        
        if (placeIndex !== -1 && transitionIndex !== -1) {
          const peso = arco.peso ?? 1;
          
          // Se arco vai de place para transição (entrada)
          if (this.places.find(p => p.id === arco.origem)) {
            // Converter peso 0 (arco inibidor) para -1 na matriz
            const matrixValue = peso === 0 ? -1 : peso;
            this.inputMatrix[transitionIndex][placeIndex] = matrixValue;
          }
          // Se arco vai de transição para place (saída)
          else if (this.places.find(p => p.id === arco.destino)) {
            this.outputMatrix[transitionIndex][placeIndex] = peso;
          }
        }
      });
    }
  }

  /**
   * Verifica se uma transição está apta para disparar
   * @param {number} transitionIndex - Índice da transição
   * @returns {boolean} - True se a transição pode disparar
   */
  isTransitionEnabled(transitionIndex) {
    if (transitionIndex < 0 || transitionIndex >= this.transitions.length) {
      return false;
    }

    for (let placeIndex = 0; placeIndex < this.places.length; placeIndex++) {
      const requiredTokens = this.inputMatrix[transitionIndex][placeIndex];
      const availableTokens = this.markingVector[placeIndex];
      
      // Regra especial: -1 significa arco inibidor (place deve ter 0 tokens)
      if (requiredTokens === -1) {
        if (availableTokens !== 0) {
          return false; // Place deve estar vazio para arco inibidor
        }
      } else if (requiredTokens > 0) {
        // Regra normal: deve ter tokens suficientes
        if (availableTokens < requiredTokens) {
          return false;
        }
      }
      // requiredTokens === 0: sem arco, sem verificação
    }
    
    return true;
  }

  /**
   * Retorna todas as transições que estão aptas para disparar
   * @returns {Array} - Array com índices das transições aptas
   */
  getEnabledTransitions() {
    const enabledTransitions = [];
    
    for (let i = 0; i < this.transitions.length; i++) {
      if (this.isTransitionEnabled(i)) {
        enabledTransitions.push(i);
      }
    }
    
    return enabledTransitions;
  }

  /**
   * Dispara uma transição, atualizando a marcação
   * @param {number} transitionIndex - Índice da transição a disparar
   * @returns {Object} - Resultado do disparo com informações
   */
  fireTransition(transitionIndex) {
    if (!this.isTransitionEnabled(transitionIndex)) {
      return {
        success: false,
        message: "Transição não está apta para disparar"
      };
    }

    const transition = this.transitions[transitionIndex];
    const oldMarking = [...this.markingVector];
    const affectedPlaces = [];

    // Remover tokens dos places de entrada
    for (let placeIndex = 0; placeIndex < this.places.length; placeIndex++) {
      const inputTokens = this.inputMatrix[transitionIndex][placeIndex];
      if (inputTokens > 0) {
        this.markingVector[placeIndex] -= inputTokens;
        affectedPlaces.push({
          place: this.places[placeIndex],
          oldTokens: oldMarking[placeIndex],
          newTokens: this.markingVector[placeIndex],
          type: 'input'
        });
      }
    }

    // Adicionar tokens aos places de saída
    for (let placeIndex = 0; placeIndex < this.places.length; placeIndex++) {
      const outputTokens = this.outputMatrix[transitionIndex][placeIndex];
      if (outputTokens > 0) {
        this.markingVector[placeIndex] += outputTokens;
        
        // Verificar se já foi registrado como entrada
        const existingRecord = affectedPlaces.find(ap => ap.place.id === this.places[placeIndex].id);
        if (existingRecord) {
          existingRecord.newTokens = this.markingVector[placeIndex];
          existingRecord.type = 'both';
        } else {
          affectedPlaces.push({
            place: this.places[placeIndex],
            oldTokens: oldMarking[placeIndex],
            newTokens: this.markingVector[placeIndex],
            type: 'output'
          });
        }
      }
    }

    return {
      success: true,
      transition: transition,
      transitionIndex: transitionIndex,
      affectedPlaces: affectedPlaces,
      oldMarking: oldMarking,
      newMarking: [...this.markingVector]
    };
  }

  /**
   * Seleciona aleatoriamente uma transição apta seguindo as regras especificadas
   * @returns {number|null} - Índice da transição selecionada ou null se nenhuma apta
   */
  selectRandomEnabledTransition() {
    const enabledTransitions = this.getEnabledTransitions();
    
    if (enabledTransitions.length === 0) {
      return null;
    }
    
    if (enabledTransitions.length === 1) {
      return enabledTransitions[0];
    }

    // Implementar lógica de seleção aleatória conforme regras especificadas
    // Regra 1: Se transições estão no mesmo place e place tem apenas 1 token
    // Regra 2: Transições em places diferentes - seleção aleatória

    const randomIndex = Math.floor(Math.random() * enabledTransitions.length);
    return enabledTransitions[randomIndex];
  }

  /**
   * Atualiza o vetor de marcação na estrutura original da rede
   */
  updatePetriNetMarking() {
    this.places.forEach((place, index) => {
      place.tokens = this.markingVector[index];
    });
  }

  /**
   * Restaura a marcação inicial
   */
  resetToInitialMarking() {
    this.places.forEach((place, index) => {
      const initialTokens = place.initialTokens ?? place.tokens ?? 0;
      this.markingVector[index] = initialTokens;
      place.tokens = initialTokens;
    });
  }

  /**
   * Salva a marcação atual como inicial para permitir reset
   */
  saveCurrentAsInitialMarking() {
    this.places.forEach((place, index) => {
      place.initialTokens = this.markingVector[index];
    });
  }

  /**
   * Retorna informações para debug das matrizes
   * @returns {Object} - Objeto com informações das matrizes
   */
  getMatricesInfo() {
    return {
      places: this.places.map(p => ({ id: p.id, nome: p.nome })),
      transitions: this.transitions.map(t => ({ id: t.id, nome: t.nome })),
      inputMatrix: this.inputMatrix,
      outputMatrix: this.outputMatrix,
      markingVector: this.markingVector,
      enabledTransitions: this.getEnabledTransitions()
    };
  }
}

export default PetriNetSimulationMatrices;