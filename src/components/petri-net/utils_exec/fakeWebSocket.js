/**
 * FakeWebSocket - Versão Browser
 * Baseado no trabalho do codex em experimental_petri/fake_websocket.js
 * 
 * FUNCIONALIDADES:
 * - Interface idêntica ao WebSocket real
 * - Intercepta calls dos Places transparentemente
 * - Redireciona para CentralWSClient
 * - Simula eventos onopen/onmessage/onerror
 */

import { CentralWSClient } from './centralWSClient';

class FakeWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 0; // WebSocket.CONNECTING
    
    // Callbacks (interface WebSocket padrão)
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.onclose = null;
    
    console.log('🎭 [FAKE WEBSOCKET] Criado para:', url);
    
    // CRÍTICO: Simular abertura assíncrona (igual experimental)
    setTimeout(() => {
      this.readyState = 1; // WebSocket.OPEN
      console.log('🔓 [FAKE WEBSOCKET] Simulando onopen');
      
      if (typeof this.onopen === 'function') {
        try { 
          this.onopen(); 
        } catch (error) {
          console.error('❌ [FAKE WEBSOCKET] Erro em onopen:', error);
        }
      }
    }, 0);
  }

  /**
   * Simular fechamento
   */
  close() { 
    this.readyState = 3; // WebSocket.CLOSED
    console.log('🔒 [FAKE WEBSOCKET] Fechado');
  }

  /**
   * Interceptar send() e redirecionar para CentralWSClient V10
   * FORMATO IDÊNTICO ao testar_interface_generica_v10_md.js
   */
  async send(data) {
    try {
      console.log('📤 [FAKE WEBSOCKET V10] Send interceptado:', data);

      const parsed = JSON.parse(data);

      // ⭐ V10: SUPORTE COMANDOS GENÉRICOS IDÊNTICO ao testar_interface
      if (parsed.type === 'iniciar_execucao' || parsed.type === 'finalizar_execucao') {
        console.log(`🌐 [FAKE WEBSOCKET V10] Comando genérico detectado: ${parsed.type}`);

        // Obter instância central e repassar comando
        const central = CentralWSClient.getInstance();
        central.sendGenericCommand(parsed.type, parsed.data || {});
        return; // Comando genérico não precisa de resposta
      }

      // ✅ FORMATO EXATO do testar_interface: { type: 'execute_task', data: { task_name, input_data } }
      let taskName, inputData;

      if (parsed.type === 'execute_task' && parsed.data?.task_name !== undefined) {
        // ⭐ V10: Formato oficial IDÊNTICO ao testar_interface (line 408-413)
        taskName = parsed.data.task_name;
        inputData = parsed.data.input_data; // null para read_email, result da tarefa anterior para as demais
        console.log('🆕 [FAKE WEBSOCKET V10] Formato V10 oficial IDÊNTICO ao testar_interface');
      } else {
        throw new Error('unsupported message format - expected testar_interface V10 format: ' + JSON.stringify(parsed));
      }

      console.log('🎯 [FAKE WEBSOCKET V10] Tarefa:', taskName);
      console.log('📥 [FAKE WEBSOCKET V10] Input recebido:', inputData);

      // Obter instância central
      const central = CentralWSClient.getInstance();

      // 🔍 DEBUG: Verificar se singleton mantém cache entre tasks
      console.log(`🔍 [FAKE WEBSOCKET V10 DEBUG] Instância central:`, central.constructor.name);
      console.log(`🔍 [FAKE WEBSOCKET V10 DEBUG] Cache taskResults atual:`, Object.keys(central.taskResults || {}));
      console.log(`🔍 [FAKE WEBSOCKET V10 DEBUG] Cache lastResult atual:`, Object.keys(central.lastResult || {}));

      // 🔧 FIX CRÍTICO: SEMPRE usar cache do CentralWSClient ao invés de inputData do Petri Net
      // O Petri Net pode passar dados antigos/errados, mas o cache tem os dados REAIS do backend
      const tropicalSalesFlow = ['read_email', 'classify_message', 'check_stock_availability', 'generate_response'];
      const currentIndex = tropicalSalesFlow.indexOf(taskName);
      let finalInputData = inputData;

      if (currentIndex === 0) {
        // Primeira task (read_email) - usar inputData do Petri Net
        console.log(`🚀 [FAKE WEBSOCKET V10] ${taskName} é tarefa inicial - input do Petri Net:`, inputData);
        finalInputData = inputData || null;
      } else {
        // Tasks subsequentes - SEMPRE usar resultado REAL do cache, ignorar inputData do Petri Net
        const previousTask = tropicalSalesFlow[currentIndex - 1];
        const previousResult = central.getTaskResult(previousTask);

        if (previousResult) {
          console.log(`✅ [FAKE WEBSOCKET V10 FIX] ${taskName} usando CACHE de ${previousTask}:`, Object.keys(previousResult));
          console.log(`🔍 [FAKE WEBSOCKET V10 FIX] InputData do Petri Net IGNORADO:`, Object.keys(inputData || {}));
          finalInputData = previousResult;
        } else {
          console.error(`❌ [FAKE WEBSOCKET V10 FIX] Cache de ${previousTask} vazio! Usando inputData do Petri Net como fallback`);
          console.error(`⚠️ [FAKE WEBSOCKET V10 FIX] Isso pode causar erro se dados forem antigos!`);
          finalInputData = inputData;
        }
      }

      // ✅ Executar via central client V10 com formato IDÊNTICO ao testar_interface
      const result = await central.executeTask(taskName, finalInputData, {
        onStep: (step) => {
          console.log('👂 [FAKE WEBSOCKET V10] Step recebido:', step.step_type);

          // PROPAGAR para callback do Place
          if (typeof this.onmessage === 'function') {
            try {
              this.onmessage({
                data: JSON.stringify({
                  type: 'execution_step',
                  data: step
                })
              });
            } catch (error) {
              console.error('❌ [FAKE WEBSOCKET V10] Erro propagando step:', error);
            }
          }
        }
      });

      console.log('✅ [FAKE WEBSOCKET V10] Resultado obtido:', result);
      
      // ENVIAR RESULTADO FINAL para Place
      if (typeof this.onmessage === 'function') {
        try { 
          this.onmessage({
            data: JSON.stringify({
              type: 'task_completed',
              data: {
                task_name: taskName,
                result
              }
            })
          });
        } catch (error) {
          console.error('❌ [FAKE WEBSOCKET V10] Erro enviando resultado:', error);
        }
      }

    } catch (error) {
      console.error('❌ [FAKE WEBSOCKET V10] Erro em send:', error);

      // PROPAGAR ERRO para Place
      if (typeof this.onerror === 'function') {
        try {
          this.onerror(error);
        } catch (errorHandlerError) {
          console.error('❌ [FAKE WEBSOCKET V10] Erro no handler de erro:', errorHandlerError);
        }
      }
    }
  }
}

export { FakeWebSocket };
