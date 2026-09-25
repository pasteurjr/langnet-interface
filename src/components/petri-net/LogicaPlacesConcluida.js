/**
 * LogicaPlacesConcluida.js
 * 
 * Módulo responsável por verificar se TODOS os Places de entrada de uma transição
 * completaram a execução de sua lógica (campo 'logica' ou agentId).
 * 
 * Separado do GuardEvaluator para manter responsabilidades específicas:
 * - LogicaPlacesConcluida: Verifica execução concluída dos Places
 * - GuardEvaluator: Avalia apenas o campo 'guard' das transições
 */

export class LogicaPlacesConcluida {
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
   * Verifica se TODOS os Places de entrada de uma transição completaram execução
   * @param {Object} transition - Objeto da transição
   * @returns {boolean} - true se TODOS Places de entrada completaram execução
   */
  verificarExecucaoConcluida(transition) {
    console.log(`🔍 Verificando execução concluída para transição ${transition.id}`);

    // Encontrar TODOS os Places de entrada da transição
    const inputPlaces = this.findInputPlaces(transition.id);
    
    if (inputPlaces.length === 0) {
      console.warn(`⚠️ Transição ${transition.id}: Nenhum Place de entrada encontrado`);
      return true; // Se não há Places de entrada, permitir
    }

    console.log(`📍 Transição ${transition.id}: Verificando ${inputPlaces.length} Places de entrada: ${inputPlaces.map(p => p.id).join(', ')}`);

    // Verificar CADA Place de entrada
    for (const inputPlace of inputPlaces) {
      const temExecucao = this.placeTemExecucao(inputPlace);
      
      if (temExecucao) {
        const executionStatus = this.verificarStatusExecucao(inputPlace);
        
        if (!executionStatus.concluida) {
          console.log(`❌ Place ${inputPlace.id}: ${executionStatus.motivo}`);
          return false; // BLOQUEAR se algum Place não completou
        } else {
          console.log(`✅ Place ${inputPlace.id}: ${executionStatus.motivo}`);
        }
      } else {
        console.log(`⚪ Place ${inputPlace.id}: Sem execução (agentId e logica vazios)`);
        // Places sem execução são considerados "sempre prontos"
      }
    }

    console.log(`🎉 Transição ${transition.id}: TODOS os Places de entrada completaram execução!`);
    return true; // PERMITIR apenas se TODOS completaram
  }

  /**
   * Verifica se um Place tem execução definida (agentId ou logica)
   * @param {Object} place - Objeto do Place
   * @returns {boolean} - true se o Place tem execução definida
   */
  placeTemExecucao(place) {
    const temAgentId = place.agentId && place.agentId !== null && place.agentId !== undefined;
    const temLogica = place.logica && place.logica.trim() !== '';
    
    return temAgentId || temLogica;
  }

  /**
   * Verifica o status de execução de um Place específico
   * @param {Object} place - Objeto do Place
   * @returns {Object} - {concluida: boolean, motivo: string, detalhes: Object}
   */
  verificarStatusExecucao(place) {
    const status = place.status || 'pending';
    const temAgentId = place.agentId && place.agentId !== null;
    const temLogica = place.logica && place.logica.trim() !== '';
    
    // ✅ CORREÇÃO: Places com tokens mas sem execução prévia são "prontos"
    // Status 'pending' significa "pronto para executar" no início
    if (status === 'completed') {
      return {
        concluida: true,
        motivo: `Execução concluída (${temAgentId ? 'WebSocket' : 'JavaScript'})`,
        detalhes: {
          tipo: temAgentId ? 'websocket' : 'javascript',
          executionTime: place.execution_time || 0,
          lastExecution: place.lastExecution
        }
      };
    }
    
    // ❌ CRÍTICO: Places com erro devem BLOQUEAR próximas transições
    if (status === 'error') {
      return {
        concluida: false,
        motivo: `Place com erro - bloqueando próximas transições (status: ${status})`,
        detalhes: {
          status,
          tokens: this.markingVector[place.id] || 0,
          tipo: temAgentId ? 'websocket' : 'javascript',
          agentId: place.agentId,
          temLogica: temLogica,
          error: place.error || 'WebSocket error'
        }
      };
    }
    
    // ✅ CORREÇÃO: Status 'pending' com tokens = PRONTO para executar
    if (status === 'pending') {
      // Verificar se o Place tem tokens (foi ativado por transição anterior)
      const tokens = this.markingVector[place.id] || 0;
      if (tokens > 0) {
        return {
          concluida: true, // ✅ CONSIDERADO PRONTO se tem tokens
          motivo: `Place ativo com ${tokens} token(s) - pronto para executar`,
          detalhes: {
            status,
            tokens,
            tipo: temAgentId ? 'websocket' : 'javascript',
            agentId: place.agentId,
            temLogica: temLogica
          }
        };
      }
    }

    // Status não é completed nem pending com tokens
    return {
      concluida: false,
      motivo: `Execução não concluída (status: ${status}, tokens: ${this.markingVector[place.id] || 0})`,
      detalhes: {
        status,
        tokens: this.markingVector[place.id] || 0,
        tipo: temAgentId ? 'websocket' : 'javascript',
        agentId: place.agentId,
        temLogica: temLogica
      }
    };
  }

  /**
   * Encontra TODOS os Places de entrada de uma transição
   * @param {string} transitionId - ID da transição
   * @returns {Array} - Array com todos os Places de entrada
   */
  findInputPlaces(transitionId) {
    const inputPlaces = [];
    
    // Método 1: Buscar por arcos que chegam na transição (Place → Transição)
    if (this.petriNet.arcos && Array.isArray(this.petriNet.arcos)) {
      this.petriNet.arcos.forEach(arco => {
        if (arco.destino === transitionId) {
          const inputPlace = this.petriNet.lugares.find(p => p.id === arco.origem);
          if (inputPlace && !inputPlaces.find(p => p.id === inputPlace.id)) {
            inputPlaces.push(inputPlace);
          }
        }
      });
    }

    // Método 2: Fallback usando campo 'origem' se não há arcos definidos
    if (inputPlaces.length === 0 && this.petriNet.transicoes) {
      const transitionData = this.petriNet.transicoes.find(t => t.id === transitionId);
      if (transitionData && transitionData.origem) {
        const sourcePlace = this.petriNet.lugares.find(p => p.id === transitionData.origem);
        if (sourcePlace) {
          inputPlaces.push(sourcePlace);
        }
      }
    }

    // Método 3: Busca por naming pattern se ainda não encontrou
    if (inputPlaces.length === 0) {
      console.warn(`⚠️ Nenhum arco encontrado para transição ${transitionId}, tentando busca por padrão...`);
      
      // Assumir padrão sequencial P1→T1→P2→T2→P3...
      const transitionNumber = transitionId.replace(/\D/g, '');
      if (transitionNumber) {
        const prevPlaceId = `P${transitionNumber}`;
        const prevPlace = this.petriNet.lugares.find(p => p.id === prevPlaceId);
        if (prevPlace) {
          inputPlaces.push(prevPlace);
          console.log(`📍 Busca por padrão: ${transitionId} ← ${prevPlaceId}`);
        }
      }
    }

    return inputPlaces;
  }

  /**
   * Obter estatísticas de execução dos Places
   * @returns {Object} - Estatísticas detalhadas
   */
  getExecutionStats() {
    const stats = {
      total: 0,
      withExecution: 0,
      completed: 0,
      pending: 0,
      running: 0,
      error: 0,
      websocket: 0,
      javascript: 0
    };

    if (!this.petriNet.lugares) return stats;

    this.petriNet.lugares.forEach(place => {
      stats.total++;
      
      if (this.placeTemExecucao(place)) {
        stats.withExecution++;
        
        if (place.agentId) {
          stats.websocket++;
        } else if (place.logica) {
          stats.javascript++;
        }

        switch (place.status) {
          case 'completed':
            stats.completed++;
            break;
          case 'running':
            stats.running++;
            break;
          case 'error':
            stats.error++;
            break;
          default:
            stats.pending++;
        }
      }
    });

    return stats;
  }

  /**
   * Log detalhado do estado atual de todos os Places
   */
  logStatusDetalhado() {
    console.log('📊 === STATUS DETALHADO DOS PLACES ===');
    
    if (!this.petriNet.lugares) {
      console.log('⚠️ Nenhum Place encontrado na Petri Net');
      return;
    }

    this.petriNet.lugares.forEach(place => {
      const temExecucao = this.placeTemExecucao(place);
      const status = place.status || 'pending';
      const tipo = place.agentId ? 'WebSocket' : (place.logica ? 'JavaScript' : 'None');
      
      console.log(`${this.getStatusIcon(status)} ${place.id} (${place.nome}): ${status} [${tipo}]${temExecucao ? '' : ' - Sem execução'}`);
      
      if (temExecucao && place.execution_time) {
        console.log(`   ⏱️ Tempo execução: ${place.execution_time}ms`);
      }
    });

    const stats = this.getExecutionStats();
    console.log('📈 Estatísticas:', stats);
    console.log('🏁 === FIM STATUS DETALHADO ===');
  }

  /**
   * Obter ícone para status
   */
  getStatusIcon(status) {
    const icons = {
      'completed': '✅',
      'running': '🔄',
      'error': '❌',
      'pending': '⏳'
    };
    return icons[status] || '⚪';
  }
}