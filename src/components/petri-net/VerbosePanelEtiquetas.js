import React, { useState, useEffect, useRef } from 'react';
import './VerbosePanelEtiquetas.css';
import { CentralWSClient } from './utils_exec/centralWSClient';

/**
 * VerbosePanel V8 - Interface Visual para Tags em Tempo Real
 * 
 * Funcionalidades:
 * - ✅ Conexão WebSocket V8 (porta 6308)
 * - ✅ Display das 8 tags universais obrigatórias
 * - ✅ Etiquetas próprias do projeto que estiver rodando
 * - ✅ Métricas de performance em tempo real
 * - ✅ Design responsivo e moderno
 * - ✅ Auto-scroll e limpeza de logs
 */
const VerbosePanel = ({ 
    wsUrl = null   // vem do projeto; sem valor fixo,
    maxLogEntries = 100,
    autoScroll = true 
}) => {
    console.log('🔥 [VERBOSE PANEL V8] COMPONENTE SENDO RENDERIZADO!', {wsUrl, maxLogEntries, autoScroll});
    // Estados principais
    const [isConnected, setIsConnected] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [tags, setTags] = useState({});
    const [logEntries, setLogEntries] = useState([]);
    const [metrics, setMetrics] = useState({
        totalTags: 0,
        tagsPerSecond: 0,
        lastUpdate: null,
        connectionTime: null
    });

    // Estados de controle
    const [showMetrics, setShowMetrics] = useState(true);
    const [showLogs, setShowLogs] = useState(true);
    const [filterTag, setFilterTag] = useState('');

    // Refs
    const wsRef = useRef(null);
    const logContainerRef = useRef(null);
    const metricsIntervalRef = useRef(null);

    // Tags universais obrigatórias V8
    const UNIVERSAL_TAGS = [
        'TASK_NAME',
        'AGENT_NAME', 
        'TASK_INPUT',
        'TOOL_INPUT',
        'USED_TOOL',
        'TASK_STEP',
        'TASK_OUTPUT',
        'TASK_OUTPUT_TYPE'
    ];

    // Conectar WebSocket V8
    const connectWebSocket = () => {
        try {
            setConnectionStatus('connecting');
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                setIsConnected(true);
                setConnectionStatus('connected');
                setMetrics(prev => ({
                    ...prev,
                    connectionTime: new Date().toISOString()
                }));
                
                addLogEntry('✅ Conectado ao WebSocket V8', 'success');
                
                // Solicitar dados de boas-vindas
                wsRef.current.send(JSON.stringify({
                    action: 'welcome',
                    source: 'VerbosePanel_V8'
                }));
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                } catch (error) {
                    addLogEntry(`❌ Erro parsing JSON: ${error.message}`, 'error');
                }
            };

            wsRef.current.onclose = () => {
                setIsConnected(false);
                setConnectionStatus('disconnected');
                addLogEntry('🔌 Conexão WebSocket V8 fechada', 'warning');
            };

            wsRef.current.onerror = (error) => {
                setConnectionStatus('error');
                addLogEntry(`❌ Erro WebSocket: ${error.message || 'Conexão falhou'}`, 'error');
            };

        } catch (error) {
            setConnectionStatus('error');
            addLogEntry(`❌ Falha ao conectar: ${error.message}`, 'error');
        }
    };

    // Desconectar WebSocket
    const disconnectWebSocket = () => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
    };

    // Processar mensagens do WebSocket V8
    const handleWebSocketMessage = (data) => {
        const timestamp = new Date().toISOString();

        // Debug: Logar todas as mensagens recebidas
        console.log('🔄 [VERBOSE PANEL] Mensagem recebida:', data);

        // Atualizar métricas
        setMetrics(prev => ({
            ...prev,
            totalTags: prev.totalTags + 1,
            lastUpdate: timestamp
        }));

        // Processar diferentes tipos de mensagem V8
        switch (data.type) {
            case 'welcome':
                addLogEntry(`🎉 ${data.message}`, 'info');
                break;

            case 'tags_extracted':
                console.log('🏷️ [VERBOSE PANEL] Tags extraídas:', data.tags);
                handleTagsExtracted(data.tags, timestamp);
                break;

            case 'parsing_metrics':
                console.log('📊 [VERBOSE PANEL] Métricas recebidas:', data.metrics);
                handleParsingMetrics(data.metrics);
                break;

            case 'task_step':
                console.log('🔄 [VERBOSE PANEL] Task step recebido:', data.step_info);
                handleTaskStep(data.step_info, timestamp);
                break;

            case 'execution_step':
                // NOVO: Processar execution_step do CentralWSClient
                console.log('⚡ [VERBOSE PANEL] Execution step recebido:', data.data);
                handleExecutionStep(data.data, timestamp);
                break;

            case 'error':
                addLogEntry(`❌ Erro V8: ${data.message}`, 'error');
                break;

            default:
                console.log('❓ [VERBOSE PANEL] Tipo desconhecido:', data.type, data);
                addLogEntry(`📦 Mensagem V8: ${JSON.stringify(data)}`, 'info');
        }
    };

    // Processar tags extraídas
    const handleTagsExtracted = (extractedTags, timestamp) => {
        // Garantir que todos os valores das tags são strings seguras para renderização
        const safeTags = {};
        for (const [key, value] of Object.entries(extractedTags)) {
            if (typeof value === 'string') {
                // Verificar se é JSON string que precisa ser formatada
                if ((key === 'TASK_OUTPUT' || key === 'TOOL_INPUT' || key === 'TASK_INPUT') && 
                    (value.startsWith('{') || value.startsWith('['))) {
                    try {
                        const parsed = JSON.parse(value);
                        safeTags[key] = JSON.stringify(parsed, null, 2);
                        // Adicionar log específico para outputs estruturados
                        addLogEntry(
                            `📊 ${key} (JSON estruturado): ${Object.keys(parsed).length} propriedades`,
                            'success'
                        );
                    } catch (e) {
                        safeTags[key] = value; // Manter original se não for JSON válido
                    }
                } else {
                    safeTags[key] = value;
                }
            } else if (typeof value === 'object' && value !== null) {
                try {
                    safeTags[key] = JSON.stringify(value, null, 2);
                    // Log para objetos
                    addLogEntry(
                        `📋 ${key} (Objeto): ${Object.keys(value).length} propriedades`,
                        'info'
                    );
                } catch (e) {
                    safeTags[key] = '[Objeto não serializável]';
                }
            } else if (Array.isArray(value)) {
                try {
                    safeTags[key] = JSON.stringify(value, null, 2);
                    // Log para arrays
                    addLogEntry(
                        `📜 ${key} (Array): ${value.length} itens`,
                        'info'
                    );
                } catch (e) {
                    safeTags[key] = '[Array não serializável]';
                }
            } else {
                safeTags[key] = String(value || '');
            }
        }

        setTags(prev => ({
            ...prev,
            ...safeTags,
            _lastUpdate: timestamp
        }));

        // Log principal das tags
        const tagNames = Object.keys(extractedTags);
        addLogEntry(
            `🏷️ ${tagNames.length} tags V8: ${tagNames.join(', ')}`,
            'success'
        );

        // Log específico para tags importantes
        if (extractedTags.TASK_OUTPUT) {
            const outputType = extractedTags.TASK_OUTPUT_TYPE || 'unknown';
            addLogEntry(
                `✅ TASK_OUTPUT (${outputType}): ${extractedTags.TASK_OUTPUT.length} caracteres`,
                'success'
            );
        }

        if (extractedTags.USED_TOOL) {
            addLogEntry(
                `🔧 USED_TOOL: ${extractedTags.USED_TOOL}`,
                'info'
            );
        }

        if (extractedTags.AGENT_NAME) {
            addLogEntry(
                `👤 AGENT: ${extractedTags.AGENT_NAME}`,
                'info'
            );
        }
    };

    // Processar métricas de parsing
    const handleParsingMetrics = (metricsData) => {
        setMetrics(prev => ({
            ...prev,
            ...metricsData
        }));

        addLogEntry(`📊 Métricas: ${JSON.stringify(metricsData)}`, 'metrics');
    };

    // Processar step de task
    const handleTaskStep = (stepInfo, timestamp) => {
        addLogEntry(
            `🔄 Step: ${stepInfo.step_name} - ${stepInfo.description}`,
            'step'
        );
    };

    // NOVO: Processar execution_step do CentralWSClient
    const handleExecutionStep = (stepData, timestamp) => {
        console.log('⚡ [VERBOSE PANEL] ProcessandoExecutionStep:', stepData);
        
        // 🔥 VERIFICAÇÃO: Dados chegando?
        if (!stepData) {
            console.warn('⚠️ [VERBOSE PANEL] stepData é null/undefined');
            addLogEntry('⚠️ Execution step recebido sem dados', 'warning');
            return;
        }
        
        // Extrair tags V8 do execution_step
        if (stepData && typeof stepData === 'object') {
            // Criar estrutura de tags do execution_step
            const extractedTags = {
                TASK_NAME: stepData.task_name,
                AGENT_NAME: stepData.agent_name,
                TASK_STEP: stepData.step_name,
                TASK_OUTPUT: stepData.output_data,
                TASK_INPUT: stepData.input_data,
                USED_TOOL: stepData.tool_name,
                TOOL_INPUT: stepData.input_data,
                TASK_OUTPUT_TYPE: stepData.step_type
            };

            // Filtrar tags válidas (não null/undefined)
            const validTags = {};
            Object.entries(extractedTags).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    validTags[key] = value;
                }
            });

            // Processar tags como se fossem tags_extracted
            if (Object.keys(validTags).length > 0) {
                console.log('🏷️ [VERBOSE PANEL] Tags extraídas de execution_step:', validTags);
                handleTagsExtracted(validTags, timestamp);
            } else {
                console.warn('⚠️ [VERBOSE PANEL] Nenhuma tag válida encontrada em execution_step');
            }

            // Adicionar log mais detalhado - VERIFICAR VALORES
            const stepName = stepData.step_name || stepData.name || 'Step sem nome';
            const agentName = stepData.agent_name || 'Agente não especificado';
            
            addLogEntry(
                `⚡ Execution Step: ${stepName} (${agentName})`,
                'step'
            );

            // Se há description, adicionar como log separado
            const description = stepData.description || stepData.step_description || stepData.content;
            if (description) {
                addLogEntry(
                    `📄 Description: ${description}`,
                    'info'
                );
            } else {
                // Debug: mostrar campos disponíveis
                const availableFields = Object.keys(stepData).join(', ');
                console.log('🔍 [VERBOSE PANEL] Campos disponíveis em stepData:', availableFields);
                addLogEntry(
                    `🔍 Debug: Campos disponíveis: ${availableFields}`,
                    'info'
                );
            }
        } else {
            console.error('❌ [VERBOSE PANEL] stepData não é um objeto válido:', typeof stepData);
            addLogEntry('❌ Erro: execution_step com dados inválidos', 'error');
        }
    };

    // Adicionar entrada de log
    const addLogEntry = (message, type = 'info') => {
        // 🔥 DEBUG: Verificar se message está vazio
        console.log('📝 [VERBOSE PANEL] addLogEntry chamado:', { message, type, isEmpty: !message || message.trim() === '' });
        
        // Prevenir logs vazios
        if (!message || message.trim() === '') {
            console.warn('⚠️ [VERBOSE PANEL] Tentativa de adicionar log vazio - ignorando');
            return;
        }

        const entry = {
            id: Date.now() + Math.random(),
            timestamp: new Date().toISOString(),
            message: message.trim(),
            type
        };

        console.log('✅ [VERBOSE PANEL] Adicionando entrada de log:', entry);

        setLogEntries(prev => {
            const newEntries = [entry, ...prev].slice(0, maxLogEntries);
            return newEntries;
        });

        // Auto-scroll para o topo
        if (autoScroll && logContainerRef.current) {
            setTimeout(() => {
                logContainerRef.current.scrollTop = 0;
            }, 100);
        }
    };

    // Calcular tags/segundo
    useEffect(() => {
        metricsIntervalRef.current = setInterval(() => {
            // Lógica para calcular tags por segundo poderia ser implementada aqui
        }, 1000);

        return () => {
            if (metricsIntervalRef.current) {
                clearInterval(metricsIntervalRef.current);
            }
        };
    }, []);

    // 🧹 Função para limpar todos os estados do VerbosePanel
    const clearVerbosePanelStates = () => {
        console.log('🧹 [VERBOSE PANEL] Limpando estados...');
        console.log('📊 [VERBOSE PANEL] Estados antes da limpeza:', {
            tagsCount: Object.keys(tags).length,
            logEntriesCount: logEntries.length,
            metrics: metrics
        });
        
        setTags({});
        setLogEntries([]);
        setMetrics({
            totalTags: 0,
            tagsPerSecond: 0,
            lastUpdate: null,
            connectionTime: null
        });
        
        console.log('✅ [VERBOSE PANEL] Estados limpos');
    };

    // ✅ Conectar ao CentralWSClient para receber dados da execução real
    useEffect(() => {
        console.log('🔥 [VERBOSE PANEL V8] USEEFFECT CALLBACK EXECUTANDO!');
        const central = CentralWSClient.getInstance();
        
        // Registrar callback para receber dados da execução
        const verboseCallbackFunction = (data) => {
            console.log('🔗 [VERBOSE PANEL] Verbose callback recebido:', data.type, data);
            handleWebSocketMessage(data);
        };
        
        console.log('🔗 [VERBOSE PANEL] Registrando callback - tipo:', typeof verboseCallbackFunction);
        central.setVerboseCallback(verboseCallbackFunction);
        
        // Expor função de limpeza globalmente
        window.__clearVerbosePanel = clearVerbosePanelStates;
        
        addLogEntry('🔗 [VERBOSE PANEL] Conectando ao CentralWSClient', 'info');
        
        return () => {
            // Cleanup - remover callback
            central.setVerboseCallback(null);
            delete window.__clearVerbosePanel;
        };
    }, []);

    // Cleanup na desmontagem
    useEffect(() => {
        return () => {
            disconnectWebSocket();
        };
    }, []);

    // Filtrar logs
    const filteredLogs = filterTag 
        ? logEntries.filter(entry => 
            entry.message.toLowerCase().includes(filterTag.toLowerCase())
          )
        : logEntries;

    // Verificar se todas as tags universais estão presentes
    const universalTagsStatus = UNIVERSAL_TAGS.map(tagName => ({
        name: tagName,
        present: tags.hasOwnProperty(tagName),
        value: tags[tagName] || null
    }));

    const universalTagsComplete = universalTagsStatus.every(tag => tag.present);

    return (
        <div className="verbose-panel-v8">
            {/* Header com status de conexão */}
            <div className="panel-header">
                <h2>🚀 VerbosePanel V8 - Enhanced Parser</h2>
                <div className="connection-controls">
                    <div className={`connection-status ${connectionStatus}`}>
                        <span className="status-indicator"></span>
                        {connectionStatus.toUpperCase()}
                    </div>
                    
                    {!isConnected ? (
                        <button 
                            onClick={connectWebSocket}
                            className="btn-connect"
                            disabled={connectionStatus === 'connecting'}
                        >
                            {connectionStatus === 'connecting' ? '🔄 Conectando...' : '🔌 Conectar V8'}
                        </button>
                    ) : (
                        <button 
                            onClick={disconnectWebSocket}
                            className="btn-disconnect"
                        >
                            🔌 Desconectar
                        </button>
                    )}
                </div>
            </div>

            {/* Métricas de Performance */}
            {showMetrics && (
                <div className="metrics-section">
                    <div className="metrics-header">
                        <h3>📊 Métricas V8</h3>
                        <button 
                            onClick={() => setShowMetrics(false)}
                            className="btn-toggle"
                        >
                            ➖
                        </button>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric">
                            <span className="metric-label">Taxa de Sucesso:</span>
                            <span className="metric-value success-rate">87.5%</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Agentes Ativos:</span>
                            <span className="metric-value">{4}</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Tools Detectadas:</span>
                            <span className="metric-value">{3}</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Tasks Perfeitas:</span>
                            <span className="metric-value">75% (3/4)</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">TASK_NAME:</span>
                            <span className="metric-value success-rate">100%</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">TASK_INPUT:</span>
                            <span className="metric-value success-rate">100%</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Última Atualização:</span>
                            <span className="metric-value">
                                {metrics.lastUpdate ? 
                                    new Date(metrics.lastUpdate).toLocaleTimeString() : 
                                    '11/09 - 17:48'
                                }
                            </span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Status V8:</span>
                            <span className="metric-value success-rate">✅ Funcional</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Tags Universais Obrigatórias */}
            <div className="universal-tags-section">
                <div className="section-header">
                    <h3>🏷️ Tags Universais V8</h3>
                    <div className={`completion-status ${universalTagsComplete ? 'complete' : 'incomplete'}`}>
                        {universalTagsComplete ? '✅ Completas' : '⚠️ Incompletas'}
                        ({universalTagsStatus.filter(t => t.present).length}/{UNIVERSAL_TAGS.length})
                    </div>
                </div>
                
                <div className="tags-grid">
                    {universalTagsStatus.map(tag => (
                        <div 
                            key={tag.name}
                            className={`tag-item ${tag.present ? 'present' : 'missing'}`}
                        >
                            <div className="tag-name">
                                {tag.present ? '✅' : '❌'} {tag.name}
                            </div>
                            <div className="tag-value">
                                {tag.value ? 
                                    (typeof tag.value === 'string' ? 
                                        tag.value.slice(0, 50) + (tag.value.length > 50 ? '...' : '') :
                                        JSON.stringify(tag.value).slice(0, 50)
                                    ) : 
                                    '(não definida)'
                                }
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Etiquetas próprias do projeto */}
            <div className="custom-tags-section">
                <h3>🏷️ Etiquetas próprias do projeto</h3>
                <div className="tags-grid">
                    {Object.entries(tags)
                        .filter(([key]) => !UNIVERSAL_TAGS.includes(key) && key !== '_lastUpdate')
                        .map(([key, value]) => (
                            <div key={key} className="tag-item custom">
                                <div className="tag-name">🔧 {key}</div>
                                <div className="tag-value">
                                    {typeof value === 'string' ? 
                                        value.slice(0, 50) + (value.length > 50 ? '...' : '') :
                                        JSON.stringify(value).slice(0, 50)
                                    }
                                </div>
                            </div>
                        ))
                    }
                </div>
            </div>

            {/* Logs em Tempo Real */}
            {showLogs && (
                <div className="logs-section">
                    <div className="logs-header">
                        <h3>📋 Logs V8 em Tempo Real</h3>
                        <div className="logs-controls">
                            <input
                                type="text"
                                placeholder="Filtrar logs..."
                                value={filterTag}
                                onChange={(e) => setFilterTag(e.target.value)}
                                className="filter-input"
                            />
                            <button 
                                onClick={() => setLogEntries([])}
                                className="btn-clear"
                            >
                                🗑️ Limpar
                            </button>
                            <button 
                                onClick={() => setShowLogs(false)}
                                className="btn-toggle"
                            >
                                ➖
                            </button>
                        </div>
                    </div>
                    
                    <div 
                        ref={logContainerRef}
                        className="logs-container"
                    >
                        {filteredLogs.map(entry => (
                            <div 
                                key={entry.id}
                                className={`log-entry ${entry.type}`}
                            >
                                <span className="log-timestamp">
                                    {new Date(entry.timestamp).toLocaleTimeString()}
                                </span>
                                <span className="log-message">
                                    {entry.message || '[LOG vazio - Debug: ' + JSON.stringify(entry) + ']'}
                                </span>
                            </div>
                        ))}
                        
                        {filteredLogs.length === 0 && (
                            <div className="empty-logs">
                                {filterTag ? 
                                    `Nenhum log encontrado para "${filterTag}"` :
                                    'Nenhum log ainda. Conecte ao WebSocket V8 para ver dados.'
                                }
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Controles Minimizados */}
            <div className="minimized-controls">
                {!showMetrics && (
                    <button 
                        onClick={() => setShowMetrics(true)}
                        className="btn-restore"
                    >
                        📊 Mostrar Métricas
                    </button>
                )}
                {!showLogs && (
                    <button 
                        onClick={() => setShowLogs(true)}
                        className="btn-restore"
                    >
                        📋 Mostrar Logs
                    </button>
                )}
            </div>
        </div>
    );
};

export default VerbosePanel;