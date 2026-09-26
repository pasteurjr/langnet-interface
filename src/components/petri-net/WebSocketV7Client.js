/**
 * WebSocketV7Client - Cliente para integração com WebSocket V7
 * Conecta com websocket_framework_v7 para execução real de tarefas
 * Sistema compatível com TropicalSalesAdapter
 */

export class WebSocketV7Client {
  constructor(config = {}) {
    this.url = config.url || 'ws://localhost:6308';
    this.timeout = config.timeout || 30000;
    this.maxRetries = config.max_retries || 3;
    
    this.ws = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    
    // Sistema de callbacks
    this.callbacks = {
      onConnect: null,
      onDisconnect: null,
      onMessage: null,
      onError: null,
      onVerboseStep: null
    };
    
    // Filas de mensagens
    this.pendingMessages = new Map();
    this.messageId = 0;
    
    console.log('🌐 WebSocketV7Client criado:', {
      url: this.url,
      timeout: this.timeout,
      maxRetries: this.maxRetries
    });
  }
  
  // Registra callbacks
  on(eventName, callback) {
    const callbackKey = `on${eventName.charAt(0).toUpperCase() + eventName.slice(1)}`;
    if (this.callbacks.hasOwnProperty(callbackKey)) {
      this.callbacks[callbackKey] = callback;
    }
  }
  
  // Conecta ao WebSocket V7
  async connect() {
    return new Promise((resolve, reject) => {
      try {
        console.log('🔌 Conectando ao WebSocket V7:', this.url);
        
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('✅ WebSocket V7 conectado');
          this.connected = true;
          this.reconnectAttempts = 0;
          
          if (this.callbacks.onConnect) {
            this.callbacks.onConnect();
          }
          
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };
        
        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket V7 desconectado:', event.code, event.reason);
          this.connected = false;
          
          if (this.callbacks.onDisconnect) {
            this.callbacks.onDisconnect(event);
          }
          
          // Auto-reconnect se não foi fechamento intencional
          if (event.code !== 1000 && this.reconnectAttempts < this.maxRetries) {
            this.attemptReconnect();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('❌ Erro WebSocket V7:', error);
          
          if (this.callbacks.onError) {
            this.callbacks.onError(error);
          }
          
          reject(error);
        };
        
      } catch (error) {
        console.error('❌ Erro ao conectar WebSocket V7:', error);
        reject(error);
      }
    });
  }
  
  // Tentativa de reconexão
  async attemptReconnect() {
    this.reconnectAttempts++;
    console.log(`🔄 Tentativa de reconexão ${this.reconnectAttempts}/${this.maxRetries}`);
    
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 10000);
    
    setTimeout(async () => {
      try {
        await this.connect();
      } catch (error) {
        console.error('❌ Falha na reconexão:', error);
        
        if (this.reconnectAttempts >= this.maxRetries) {
          console.error('❌ Máximo de tentativas de reconexão atingido');
        }
      }
    }, delay);
  }
  
  // Processa mensagens recebidas
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      console.log('📨 Mensagem WebSocket V7 recebida:', data);
      
      if (this.callbacks.onMessage) {
        this.callbacks.onMessage(data);
      }
      
      // Processa tipos específicos de mensagem
      if (data.type === 'task_response') {
        this.handleTaskResponse(data);
      } else if (data.type === 'verbose_step') {
        this.handleVerboseStep(data);
      } else if (data.type === 'error') {
        this.handleErrorMessage(data);
      }
      
    } catch (error) {
      console.error('❌ Erro ao processar mensagem WebSocket:', error);
      console.error('Dados da mensagem:', event.data);
    }
  }
  
  // Processa resposta de tarefa
  handleTaskResponse(data) {
    const messageId = data.message_id || data.execution_id;
    
    if (messageId && this.pendingMessages.has(messageId)) {
      const { resolve } = this.pendingMessages.get(messageId);
      
      // Remove da fila
      this.pendingMessages.delete(messageId);
      
      // Resolve a Promise
      resolve(data.result || data);
      
      console.log('✅ Resposta de tarefa processada:', messageId);
    }
  }
  
  // Processa verbose steps
  handleVerboseStep(data) {
    if (this.callbacks.onVerboseStep) {
      this.callbacks.onVerboseStep(data.step_data || data);
    }
  }
  
  // Processa mensagens de erro
  handleErrorMessage(data) {
    console.error('❌ Erro do WebSocket V7:', data);
    
    const messageId = data.message_id || data.execution_id;
    
    if (messageId && this.pendingMessages.has(messageId)) {
      const { reject } = this.pendingMessages.get(messageId);
      
      // Remove da fila
      this.pendingMessages.delete(messageId);
      
      // Rejeita a Promise
      reject(new Error(data.error || data.message || 'Erro desconhecido'));
    }
  }
  
  // Executa uma tarefa via WebSocket V7
  async executeTask(payload) {
    if (!this.connected) {
      throw new Error('WebSocket V7 não está conectado');
    }
    
    // Gera ID único para a mensagem
    const messageId = `msg_${++this.messageId}_${Date.now()}`;
    
    // Monta mensagem para WebSocket V7
    const message = {
      type: 'execute_task',
      message_id: messageId,
      task_name: payload.task_name,
      inputs: payload.inputs,
      metadata: {
        place_id: payload.place_id,
        agent_id: payload.agent_id,
        execution_id: payload.execution_id
      },
      timestamp: new Date().toISOString()
    };
    
    console.log('🚀 Enviando tarefa para WebSocket V7:', message);
    
    return new Promise((resolve, reject) => {
      // Registra Promise pendente
      this.pendingMessages.set(messageId, { resolve, reject });
      
      // Configura timeout
      const timeoutId = setTimeout(() => {
        if (this.pendingMessages.has(messageId)) {
          this.pendingMessages.delete(messageId);
          reject(new Error(`Timeout executando tarefa ${payload.task_name}`));
        }
      }, this.timeout);
      
      // Limpa timeout quando resolver
      const originalResolve = resolve;
      const originalReject = reject;
      
      this.pendingMessages.set(messageId, {
        resolve: (result) => {
          clearTimeout(timeoutId);
          originalResolve(result);
        },
        reject: (error) => {
          clearTimeout(timeoutId);
          originalReject(error);
        }
      });
      
      // Envia mensagem
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        this.pendingMessages.delete(messageId);
        clearTimeout(timeoutId);
        reject(error);
      }
    });
  }
  
  // Envia ping para manter conexão ativa
  ping() {
    if (this.connected) {
      this.send({
        type: 'ping',
        timestamp: new Date().toISOString()
      });
    }
  }
  
  // Envia mensagem genérica
  send(data) {
    if (!this.connected) {
      console.warn('⚠️ Tentativa de enviar mensagem com WebSocket desconectado');
      return false;
    }
    
    try {
      this.ws.send(JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('❌ Erro ao enviar mensagem:', error);
      return false;
    }
  }
  
  // Desconecta do WebSocket
  disconnect() {
    if (this.ws) {
      console.log('🔌 Desconectando WebSocket V7...');
      this.connected = false;
      this.ws.close(1000, 'Desconexão intencional');
      this.ws = null;
    }
    
    // Rejeita todas as mensagens pendentes
    this.pendingMessages.forEach(({ reject }, messageId) => {
      reject(new Error('WebSocket desconectado'));
    });
    this.pendingMessages.clear();
  }
  
  // Status da conexão
  isConnected() {
    return this.connected && this.ws && this.ws.readyState === WebSocket.OPEN;
  }
  
  // Informações de debug
  getDebugInfo() {
    return {
      url: this.url,
      connected: this.connected,
      readyState: this.ws ? this.ws.readyState : 'No WebSocket',
      pendingMessages: this.pendingMessages.size,
      reconnectAttempts: this.reconnectAttempts,
      maxRetries: this.maxRetries
    };
  }
}
