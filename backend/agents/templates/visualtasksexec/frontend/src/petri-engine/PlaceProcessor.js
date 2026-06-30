/**
 * PlaceProcessor.js
 * 
 * Módulo responsável por processar a lógica dos places
 * Executa código JavaScript quando places recebem tokens
 */

/**
 * Classe para processar lógica de places
 */
export class PlaceProcessor {
  constructor(petriNet, markingVector) {
    this.petriNet = petriNet;
    this.markingVector = markingVector;
    this.processingQueue = new Map(); // Place ID -> timeout
    this.callbacks = {
      onPlaceProcessed: null,
      onError: null
    };
  }

  /**
   * Atualiza o contexto do processador
   */
  updateContext(petriNet, markingVector) {
    this.petriNet = petriNet;
    this.markingVector = markingVector;
  }

  /**
   * Registra callbacks para eventos de processamento
   */
  setCallbacks(callbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Processa um place quando recebe tokens
   * @param {string} placeId - ID do place a ser processado
   * @param {Object} newTokens - Tokens recebidos (pode conter dados)
   */
  processPlace(placeId, newTokens = {}) {
    const place = this.petriNet.lugares.find(p => p.id === placeId);
    if (!place) {
      console.error(`Place ${placeId} não encontrado`);
      return;
    }

    // Se place não tem lógica, apenas atualiza tokens
    if (!place.logica || place.logica.trim() === '') {
      this.updatePlaceOutput(place, place.input_data || {});
      return;
    }

    // Cancelar processamento anterior se existir
    if (this.processingQueue.has(placeId)) {
      clearTimeout(this.processingQueue.get(placeId));
    }

    // Atualizar input_data com novos dados recebidos
    this.updatePlaceInput(place, newTokens);

    console.log(`🔄 Iniciando processamento do place ${placeId} com delay ${place.delay || 0}ms`);

    // Aplicar delay antes do processamento
    const delay = place.delay || 0;
    const timeoutId = setTimeout(() => {
      this.executePlaceLogic(place);
      this.processingQueue.delete(placeId);
    }, delay);

    this.processingQueue.set(placeId, timeoutId);
  }

  /**
   * Atualiza os dados de entrada de um place
   * @param {Object} place - Objeto do place
   * @param {Object} newData - Novos dados recebidos
   */
  updatePlaceInput(place, newData) {
    // Merge dos dados existentes com os novos (apenas dados essenciais)
    place.input_data = {
      ...place.input_data || {},
      ...newData
    };

    console.log(`📥 Input data atualizado para ${place.id}:`, place.input_data);
  }

  /**
   * Executa a lógica de processamento de um place
   * @param {Object} place - Objeto do place
   */
  async executePlaceLogic(place) {
    try {
      console.log(`⚙️ Executando lógica do place ${place.id}`);

      // Criar contexto para execução
      const context = this.createProcessingContext(place);

      // Executar lógica
      const result = await this.executeLogicCode(place.logica, context);

      // Atualizar output_data
      this.updatePlaceOutput(place, result);

      // Notificar callback se registrado
      if (this.callbacks.onPlaceProcessed) {
        this.callbacks.onPlaceProcessed(place.id, place.input_data, place.output_data);
      }

    } catch (error) {
      console.error(`Erro ao processar lógica do place ${place.id}:`, error);
      
      // Fallback: copiar input para output em caso de erro
      this.updatePlaceOutput(place, place.input_data || {});

      // Notificar erro se callback registrado
      if (this.callbacks.onError) {
        this.callbacks.onError(place.id, error);
      }
    }
  }

  /**
   * Atualiza os dados de saída de um place
   * @param {Object} place - Objeto do place
   * @param {Object} outputData - Dados de saída processados
   */
  updatePlaceOutput(place, outputData) {
    // Garantir que output_data é um objeto e manter apenas os dados essenciais
    place.output_data = {
      ...(typeof outputData === 'object' && outputData !== null ? outputData : {})
    };

    console.log(`📤 Output data atualizado para ${place.id}:`, place.output_data);
  }

  /**
   * Cria contexto para execução da lógica do place
   * @param {Object} place - Objeto do place sendo processado
   * @returns {Object} - Contexto para execução
   */
  createProcessingContext(place) {
    // Dados básicos da rede
    const tokens = { ...this.markingVector };
    
    // Dados de todos os places
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

    // Input data do place atual
    const input = place.input_data || {};

    const context = {
      // Dados de entrada específicos deste place
      input,
      
      // Acesso aos tokens de todos os places
      tokens,
      
      // Acesso a todos os places
      places,
      
      // Dados específicos do place atual
      self: places[place.id],
      
      // Funções auxiliares
      utils: {
        // Operações matemáticas
        sum: (...values) => values.reduce((a, b) => a + b, 0),
        avg: (values) => values.reduce((a, b) => a + b, 0) / values.length,
        max: (...values) => Math.max(...values),
        min: (...values) => Math.min(...values),
        
        // Operações de tempo
        now: () => Date.now(),
        timeElapsed: (timestamp) => Date.now() - timestamp,
        
        // Operações de dados
        clone: (obj) => JSON.parse(JSON.stringify(obj)),
        merge: (...objects) => Object.assign({}, ...objects),
        
        // Operações de array
        first: (arr) => arr && arr.length > 0 ? arr[0] : null,
        last: (arr) => arr && arr.length > 0 ? arr[arr.length - 1] : null,
        
        // Validações
        isNumber: (value) => typeof value === 'number' && !isNaN(value),
        isString: (value) => typeof value === 'string',
        isObject: (value) => typeof value === 'object' && value !== null,
        
        // Acesso aos dados de outros places
        getPlaceData: (placeId) => places[placeId] || null,
        getPlaceInput: (placeId) => places[placeId]?.input_data || {},
        getPlaceOutput: (placeId) => places[placeId]?.output_data || {},
        
        // Log para debug
        log: (...args) => console.log(`[${place.id}]:`, ...args)
      }
    };

    return context;
  }

  /**
   * Executa o código de lógica de forma segura
   * @param {string} logicCode - Código JavaScript da lógica
   * @param {Object} context - Contexto para execução
   * @returns {Promise<*>} - Resultado da execução
   */
  executeLogicCode(logicCode, context) {
    // Timeout para prevenir loops infinitos
    const timeout = 10000; // 10 segundos
    
    // Usa AsyncFunction para permitir `await` dentro do code (place.logica usa
    // WebSocket com await new Promise(...)). new Function não suporta await.
    const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error('Logic execution timeout'));
      }, timeout);

      try {
        const restrictedEval = new AsyncFunction(
          'context',
          `
            // Disponibilizar contexto no escopo
            const { input, tokens, places, self, utils } = context;

            // Executar a lógica e retornar resultado
            ${logicCode}

            // Se não houve return explícito, retornar input modificado
            return typeof output !== 'undefined' ? output : input;
          `
        );

        // restrictedEval(context) retorna Promise — encadeamos no outer
        Promise.resolve(restrictedEval(context)).then(
          (result) => { clearTimeout(timer); resolve(result); },
          (err)    => { clearTimeout(timer); reject(err); }
        );
      } catch (error) {
        clearTimeout(timer);
        reject(error);
      }
    });
  }

  /**
   * Cancela processamento de um place
   * @param {string} placeId - ID do place
   */
  cancelProcessing(placeId) {
    if (this.processingQueue.has(placeId)) {
      clearTimeout(this.processingQueue.get(placeId));
      this.processingQueue.delete(placeId);
      console.log(`⏹️ Processamento cancelado para place ${placeId}`);
    }
  }

  /**
   * Cancela todos os processamentos pendentes
   */
  cancelAllProcessing() {
    this.processingQueue.forEach((timeoutId, placeId) => {
      clearTimeout(timeoutId);
      console.log(`⏹️ Processamento cancelado para place ${placeId}`);
    });
    this.processingQueue.clear();
  }

  /**
   * Verifica se um place está sendo processado
   * @param {string} placeId - ID do place
   * @returns {boolean} - true se está sendo processado
   */
  isProcessing(placeId) {
    return this.processingQueue.has(placeId);
  }

  /**
   * Obtém lista de places sendo processados
   * @returns {Array<string>} - Array com IDs dos places
   */
  getProcessingPlaces() {
    return Array.from(this.processingQueue.keys());
  }

  /**
   * Valida sintaxe do código de lógica
   * @param {string} logicCode - Código para validar
   * @returns {Object} - {valid: boolean, error: string|null}
   */
  static validateLogicSyntax(logicCode) {
    if (!logicCode || logicCode.trim() === '') {
      return { valid: true, error: null };
    }

    try {
      // Tentar compilar o código
      new Function(
        'context', 'input', 'tokens', 'places', 'self', 'utils',
        logicCode
      );
      return { valid: true, error: null };
    } catch (error) {
      return { 
        valid: false, 
        error: `Erro de sintaxe: ${error.message}` 
      };
    }
  }

  /**
   * Exemplos de lógicas para documentação
   */
  static getLogicExamples() {
    return {
      'Passthrough simples': 'return input;',
      'Modificar propriedade': `
        const output = utils.clone(input);
        output.status = "processed";
        return output;
      `,
      'Calcular soma': `
        const output = utils.clone(input);
        output.total = utils.sum(input.value1, input.value2);
        return output;
      `,
      'Lógica condicional': `
        const output = utils.clone(input);
        if (input.temperature > 100) {
          output.alert = "HIGH_TEMP";
        } else {
          output.alert = "NORMAL";
        }
        return output;
      `,
      'Agregar dados de outros places': `
        const output = utils.clone(input);
        const sensorData = utils.getPlaceOutput("P_SENSOR");
        output.combined = utils.merge(input, sensorData);
        return output;
      `,
      'Cálculo temporal': `
        const output = utils.clone(input);
        const elapsed = utils.timeElapsed(input.timestamp);
        output.processing_time = elapsed;
        output.status = elapsed > 5000 ? "slow" : "fast";
        return output;
      `
    };
  }
}

/**
 * Função auxiliar para criar um processador de places
 * @param {Object} petriNet - Rede de Petri
 * @param {Object} markingVector - Vetor de marcação atual
 * @returns {PlaceProcessor} - Instância do processador
 */
export function createPlaceProcessor(petriNet, markingVector) {
  return new PlaceProcessor(petriNet, markingVector);
}

export default PlaceProcessor;