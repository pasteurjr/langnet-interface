/**
 * GuardEvaluator.js
 * 
 * Módulo responsável por avaliar guards (condições) das transições
 * de forma segura e com contexto da rede de Petri
 */

/**
 * Classe para avaliar guards de transições com segurança
 */
export class GuardEvaluator {
  constructor(petriNet, markingVector) {
    this.petriNet = petriNet;
    this.markingVector = markingVector;
  }

  /**
   * Atualiza o contexto do avaliador
   */
  updateContext(petriNet, markingVector) {
    this.petriNet = petriNet;
    this.markingVector = markingVector;
  }

  /**
   * Avalia o guard de uma transição
   * @param {Object} transition - Objeto da transição
   * @returns {boolean} - true se o guard permite o disparo, false caso contrário
   */
  evaluateGuard(transition) {
    // Se não há guard definido, sempre permite o disparo
    if (!transition.guard || transition.guard.trim() === '') {
      console.log(`🛡️ Guard ${transition.id}: sem guard, permitindo disparo`);
      return true;
    }

    try {
      // Criar contexto seguro para execução do guard
      const context = this.createSafeContext();
      
      // Log do contexto para debug
      console.log(`🛡️ Guard ${transition.id} - contexto:`, {
        guard: transition.guard,
        places: Object.keys(context.places).map(id => ({
          id,
          tokens: context.places[id].tokens,
          output_data: context.places[id].output_data
        }))
      });
      
      // Executar o guard de forma segura
      const result = this.executeGuardCode(transition.guard, context);
      
      console.log(`🛡️ Guard ${transition.id} resultado: ${result}`);
      
      // Garantir que o resultado é boolean
      return Boolean(result);
      
    } catch (error) {
      console.error(`Erro ao avaliar guard da transição ${transition.id}:`, error);
      
      // Em caso de erro, log detalhado e retorna false (bloqueia disparo)
      console.error(`Guard code: ${transition.guard}`);
      
      // Opcional: mostrar erro ao usuário em modo de desenvolvimento
      if (process.env.NODE_ENV === 'development') {
        console.warn(`Guard evaluation failed for transition ${transition.id}: ${error.message}`);
      }
      
      return false;
    }
  }

  /**
   * Cria um contexto seguro para execução do guard
   * @returns {Object} - Contexto com dados da rede disponíveis para o guard
   */
  createSafeContext() {
    // Dados básicos da rede
    const tokens = { ...this.markingVector };
    
    // Dados dos places (incluindo input_data, output_data)
    const places = {};
    this.petriNet.lugares.forEach(lugar => {
      places[lugar.id] = {
        id: lugar.id,
        nome: lugar.nome,
        tokens: this.markingVector[lugar.id] || 0,
        input_data: lugar.input_data || {},
        output_data: lugar.output_data || {},
        delay: lugar.delay || 0
      };
    });

    // Dados das transições
    const transitions = {};
    this.petriNet.transicoes.forEach(transicao => {
      transitions[transicao.id] = {
        id: transicao.id,
        nome: transicao.nome,
        prioridade: transicao.prioridade || 1,
        probabilidade: transicao.probabilidade || 0,
        tempo: transicao.tempo || 0
      };
    });

    // Contexto global da rede
    const context = {
      // Acesso direto aos tokens por ID do place
      tokens,
      
      // Acesso aos dados completos dos places
      places,
      
      // Acesso aos dados das transições
      transitions,
      
      // Funções auxiliares úteis
      utils: {
        // Verifica se um place tem pelo menos N tokens
        hasTokens: (placeId, minTokens = 1) => {
          return (tokens[placeId] || 0) >= minTokens;
        },
        
        // Soma tokens de múltiplos places
        sumTokens: (...placeIds) => {
          return placeIds.reduce((sum, placeId) => sum + (tokens[placeId] || 0), 0);
        },
        
        // Verifica se todos os places especificados têm tokens
        allHaveTokens: (...placeIds) => {
          return placeIds.every(placeId => (tokens[placeId] || 0) > 0);
        },
        
        // Verifica se algum dos places especificados tem tokens
        anyHaveTokens: (...placeIds) => {
          return placeIds.some(placeId => (tokens[placeId] || 0) > 0);
        },
        
        // Acesso aos dados de um place específico
        getPlaceData: (placeId) => {
          return places[placeId] || null;
        },
        
        // Verifica propriedade nos dados de entrada de um place
        checkInputData: (placeId, property, expectedValue) => {
          const place = places[placeId];
          if (!place || !place.input_data) return false;
          return place.input_data[property] === expectedValue;
        }
      }
    };

    return context;
  }

  /**
   * Executa o código do guard de forma segura
   * @param {string} guardCode - Código JavaScript do guard
   * @param {Object} context - Contexto para execução
   * @returns {*} - Resultado da execução
   */
  executeGuardCode(guardCode, context) {
    try {
      // Criar escopo restrito sem conflito de variáveis
      const restrictedEval = new Function(
        'context',
        `
          // Disponibilizar contexto no escopo
          const { tokens, places, transitions, utils } = context;
          
          // Executar o código do guard
          return (${guardCode});
        `
      );
      
      const result = restrictedEval(context);
      
      return result;
      
    } catch (error) {
      throw error;
    }
  }

  /**
   * Valida sintaxe do código de um guard
   * @param {string} guardCode - Código do guard para validar
   * @returns {Object} - {valid: boolean, error: string|null}
   */
  static validateGuardSyntax(guardCode) {
    if (!guardCode || guardCode.trim() === '') {
      return { valid: true, error: null };
    }

    try {
      // Tentar compilar o código
      new Function('context', 'tokens', 'places', 'transitions', 'utils', `return (${guardCode});`);
      return { valid: true, error: null };
    } catch (error) {
      return { 
        valid: false, 
        error: `Erro de sintaxe: ${error.message}` 
      };
    }
  }

  /**
   * Exemplos de guards para documentação
   */
  static getGuardExamples() {
    return {
      'Token simples': 'tokens.P1 > 0',
      'Múltiplos tokens': 'tokens.P1 >= 2 && tokens.P2 > 0',
      'Condição com dados': 'places.P1.input_data.status === "ready"',
      'Função auxiliar': 'utils.hasTokens("P1", 3)',
      'Lógica complexa': 'utils.sumTokens("P1", "P2") >= 5 && places.P3.input_data.priority > 2',
      'Verificação temporal': 'places.P1.input_data.timestamp < Date.now() - 60000'
    };
  }
}

/**
 * Função auxiliar para criar um avaliador de guards
 * @param {Object} petriNet - Rede de Petri
 * @param {Object} markingVector - Vetor de marcação atual
 * @returns {GuardEvaluator} - Instância do avaliador
 */
export function createGuardEvaluator(petriNet, markingVector) {
  return new GuardEvaluator(petriNet, markingVector);
}

export default GuardEvaluator;