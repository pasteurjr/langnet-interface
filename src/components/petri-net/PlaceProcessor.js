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
    // Quem abre a conversa dentro da caixa do place. Na bancada e' o
    // interceptador; fora dela, fica nulo e cai para o WebSocket do navegador.
    this.WebSocketClass = null;
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
      return Promise.resolve();
    }

    // Rede temporizada: o token que acaba de chegar está INDISPONÍVEL enquanto
    // o processo do place não termina. O status é a fonte de verdade que a
    // LogicaPlacesConcluida consulta para liberar (ou não) a transição seguinte.
    place.status = 'running';
    place.execution_start = Date.now();
    delete place.error;

    // Se place não tem lógica, apenas atualiza tokens — já nasce disponível
    if (!place.logica || place.logica.trim() === '') {
      this.updatePlaceOutput(place, place.input_data || {});
      place.status = 'completed';
      place.execution_end = Date.now();
      return Promise.resolve();
    }

    // Cancelar processamento anterior se existir
    if (this.processingQueue.has(placeId)) {
      clearTimeout(this.processingQueue.get(placeId));
    }

    // Atualizar input_data com novos dados recebidos
    this.updatePlaceInput(place, newTokens);

    console.log(`🔄 Iniciando processamento do place ${placeId} com delay ${place.delay || 0}ms`);

    // Devolve Promise que só resolve quando a execução termina de fato — antes
    // a lógica era disparada sem espera e a marca de "processando" era apagada
    // na hora, fazendo isProcessing() mentir.
    return new Promise((resolve) => {
      const delay = place.delay || 0;
      const timeoutId = setTimeout(async () => {
        try {
          await this.executePlaceLogic(place);

          // A lógica pode falhar de dois jeitos: lançando, ou DEVOLVENDO uma
          // saída que se declara em erro (é o que o código gerado pela fábrica
          // faz — ele captura a própria falha e retorna status 'error'). Os dois
          // contam como falha; senão o place terminaria como 'completed' e
          // liberaria a transição seguinte.
          const saida = place.output_data || {};
          if (saida.status === 'error' || saida.error) {
            place.status = 'error';
            place.error = saida.error || 'o lugar terminou em erro';
          } else {
            place.status = 'completed';
          }
          place.execution_end = Date.now();
        } catch (error) {
          place.status = 'error';
          place.error = error.message;
          place.execution_end = Date.now();
          console.error(`❌ Erro no place ${placeId}:`, error);
        } finally {
          this.processingQueue.delete(placeId);
          resolve();
        }
      }, delay);

      this.processingQueue.set(placeId, timeoutId);
    });
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

      // Falha é falha. NÃO copiar a entrada para a saída: um place que não
      // conseguiu produzir não pode PARECER que produziu — era assim que o erro
      // atravessava a rede calado e a task seguinte trabalhava sobre o que
      // entrou. A saída passa a ser a marca do erro, que o place seguinte
      // consegue distinguir de um resultado legítimo.
      this.updatePlaceOutput(place, {
        status: 'error',
        error: error.message,
        failed_at: new Date().toISOString()
      });

      // Notificar erro se callback registrado
      if (this.callbacks.onError) {
        this.callbacks.onError(place.id, error);
      }

      // Relançar: é assim que processPlace fica sabendo e marca o place como
      // 'error'. Engolir aqui era o que fazia o place terminar como 'completed'
      // mesmo tendo falhado, liberando a transição seguinte.
      throw error;
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
      // Quem abre a conversa quando o código do place chama "new WebSocket".
      // Na bancada isto é o interceptador, que redireciona para a ligação única
      // do cliente central. Injetado aqui, e NÃO no objeto global, para o
      // próprio cliente central continuar usando o WebSocket de verdade.
      WebSocket: this.WebSocketClass
        || (typeof globalThis !== 'undefined' ? globalThis.WebSocket : undefined),

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
    // Timeout para prevenir loops infinitos.
    // 3 minutos: place.logica chama o servidor de agentes via WebSocket (~45s)
    // e ainda pode aguardar predecessores num JOIN.
    const timeout = 180000;

    // AsyncFunction para permitir `await` dentro do código do place. A logica
    // gerada pela fábrica é toda baseada em espera (WebSocket + laço por
    // predecessor); new Function não suporta await e quebra com SyntaxError.
    const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error('Logic execution timeout'));
      }, timeout);

      try {
        // Criar função com contexto restrito sem conflito de variáveis
        const restrictedEval = new AsyncFunction(
          'context',
          `
            // Disponibilizar contexto no escopo.
            const { input, tokens, places, self, utils } = context;
            // Quem abre a conversa: na bancada e' o interceptador (injetado no
            // contexto), que redireciona para a ligacao unica. Fora dela, cai
            // para o WebSocket do navegador.
            const WebSocket = context.WebSocket
              || (typeof globalThis !== 'undefined' ? globalThis.WebSocket : undefined);

            // Executar a lógica e retornar resultado
            ${logicCode}

            // Se não houve return explícito, retornar input modificado
            return typeof output !== 'undefined' ? output : input;
          `
        );

        // restrictedEval(context) devolve Promise — encadeamos no outer
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