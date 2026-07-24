// src/pages/McpProjectIntegrationPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { McpService, McpProjectConfig, McpServiceMapping, McpCustomEndpoint } from '../types';
import McpProjectManager from '../components/mcp/McpProjectManager';
import './McpProjectIntegrationPage.css';

const McpProjectIntegrationPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  
  const [enabledServices, setEnabledServices] = useState<McpService[]>([
    {
        id: 'auth_service_1',
        name: 'AuthService',
        provider: 'Corp Systems',
        version: 'v2.1.0',
        status: 'active' as const,
        category: 'authentication' as const,
        usage: 'high',
        description: 'Autenticação de usuários',
        endpoints: ['/auth/login', '/auth/verify'] // ← ADICIONAR ESTE CAMPO
      },
    {
      id: 'storage_service_1',
      name: 'DataStore',
      provider: 'Corp Systems',
      version: 'v3.0.1',
      status: 'up',
      category: 'storage',
      usage: 'high',
      description: 'Armazenamento de estados',
      endpoints: ['/auth/login', '/auth/verify'] // ← ADICIONAR ESTE CAMPO
    },
    {
      id: 'analytics_service_1',
      name: 'Analytics',
      provider: 'Corp Systems',
      version: 'v1.8.2',
      status: 'slow',
      category: 'analytics',
      usage: 'medium',
      description: 'Métricas de performance',
      endpoints: ['/auth/login', '/auth/verify'] // ← ADICIONAR ESTE CAMPO
    }
  ]);

  const [projectConfig, setProjectConfig] = useState<McpProjectConfig>({
    projectId: projectId || '',
    enabledServices: ['auth_service_1', 'storage_service_1', 'analytics_service_1'],
    serviceMappings: [
      {
        localModel: 'Agent State',
        mcpService: 'DataStore',
        endpoint: '/agents/state',
        format: 'JSON'
      },
      {
        localModel: 'Task Queue',
        mcpService: 'DataStore',
        endpoint: '/tasks/queue',
        format: 'JSON'
      },
      {
        localModel: 'Network State',
        mcpService: 'DataStore',
        endpoint: '/petri/network',
        format: 'JSON'
      },
      {
        localModel: 'User Sessions',
        mcpService: 'AuthService',
        endpoint: '/sessions',
        format: 'JWT'
      }
    ],
    syncRules: {
      frequency: 30,
      conflictResolution: 'merge_local',
      retryPolicy: {
        maxAttempts: 3,
        backoffStrategy: 'exponential'
      },
      batchSize: 100,
      compressionEnabled: true,
      domainRules: {
        customerData: 'encrypt',
        agentConfigs: 'version_on_change',
        performanceData: 'aggregate_hourly',
        errorLogs: 'immediate_sync'
      }
    },
    isolationNamespace: 'proj_cs_001',
    customEndpoints: [
      {
        id: 'endpoint_1',
        name: 'CustomerQueryAPI',
        endpoint: '/api/query',
        method: 'POST',
        status: 'active',
        clientsConnected: 12,
        requestsPerHour: 450,
        authentication: 'bearer_token',
        rateLimiting: {
          enabled: true,
          requestsPerMinute: 100
        },
        monitoring: {
          enabled: true,
          successRate: 98.7,
          avgResponseTime: 1200
        }
      },
      {
        id: 'endpoint_2',
        name: 'SentimentAPI',
        endpoint: '/api/sentiment',
        method: 'POST',
        status: 'active',
        clientsConnected: 8,
        requestsPerHour: 230,
        authentication: 'api_key',
        rateLimiting: {
          enabled: true,
          requestsPerMinute: 50
        },
        monitoring: {
          enabled: true,
          successRate: 95.2,
          avgResponseTime: 800
        }
      }
    ]
  });

  const [availableServices, setAvailableServices] = useState<McpService[]>([
    {
      id: 'ml_service_1',
      name: 'MLModels',
      provider: 'AI Corp',
      version: 'v2.3.0',
      status: 'up',
      category: 'ai',
      usage: 'low',
      description: 'Serviços de Machine Learning',
      endpoints: ['/auth/login', '/auth/verify'] // ← ADICIONAR ESTE CAMPO
    },
    {
      id: 'search_service_1',
      name: 'SearchEngine',
      provider: 'Search Corp',
      version: 'v1.5.3',
      status: 'up',
      category: 'other',
      usage: 'low',
      description: 'Serviço de busca e indexação',
      endpoints: ['/auth/login', '/auth/verify'] // ← ADICIONAR ESTE CAMPO
    }
  ]);

  const [showAddServiceModal, setShowAddServiceModal] = useState(false);
  const [showAddEndpointModal, setShowAddEndpointModal] = useState(false);
  const [selectedService, setSelectedService] = useState<McpService | null>(null);
  const [newEndpointData, setNewEndpointData] = useState({
    name: '',
    endpoint: '',
    method: 'POST' as 'GET' | 'POST' | 'PUT' | 'DELETE',
    authentication: 'none' as 'none' | 'api_key' | 'bearer_token' | 'oauth'
  });

  const handleEnableService = (serviceId: string) => {
    const service = availableServices.find(s => s.id === serviceId);
    if (service) {
      setEnabledServices(prev => [...prev, service]);
      setAvailableServices(prev => prev.filter(s => s.id !== serviceId));
      setProjectConfig(prev => ({
        ...prev,
        enabledServices: [...prev.enabledServices, serviceId]
      }));
    }
  };

  const handleDisableService = (serviceId: string) => {
    const service = enabledServices.find(s => s.id === serviceId);
    if (service) {
      setAvailableServices(prev => [...prev, service]);
      setEnabledServices(prev => prev.filter(s => s.id !== serviceId));
      setProjectConfig(prev => ({
        ...prev,
        enabledServices: prev.enabledServices.filter(id => id !== serviceId)
      }));
    }
  };

  const handleConfigChange = (key: keyof McpProjectConfig['syncRules'], value: any) => {
    setProjectConfig(prev => ({
      ...prev,
      syncRules: {
        ...prev.syncRules,
        [key]: value
      }
    }));
  };

  const handleCreateEndpoint = () => {
    const newEndpoint: McpCustomEndpoint = {
      id: `endpoint_${Date.now()}`,
      name: newEndpointData.name,
      endpoint: newEndpointData.endpoint,
      method: newEndpointData.method,
      status: 'inactive',
      clientsConnected: 0,
      requestsPerHour: 0,
      authentication: newEndpointData.authentication,
      rateLimiting: {
        enabled: false,
        requestsPerMinute: 100
      },
      monitoring: {
        enabled: false,
        successRate: 0,
        avgResponseTime: 0
      }
    };

    setProjectConfig(prev => ({
      ...prev,
      customEndpoints: [...(prev.customEndpoints || []), newEndpoint]
    }));

    setNewEndpointData({
      name: '',
      endpoint: '',
      method: 'POST',
      authentication: 'none'
    });
    setShowAddEndpointModal(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'up': return '🟢';
      case 'down': return '❌';
      case 'slow': return '🟡';
      case 'maintenance': return '🔧';
      default: return '⚪';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'up': return '#22c55e';
      case 'down': return '#ef4444';
      case 'slow': return '#eab308';
      case 'maintenance': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'auth': return '🔐';
      case 'storage': return '💾';
      case 'ai': return '🤖';
      case 'communication': return '📧';
      case 'analytics': return '📊';
      default: return '⚙️';
    }
  };

  return (
    <div className="mcp-project-integration-container">
      <div className="page-header">
        <h1>Integração MCP do Projeto</h1>
        <div className="header-actions">
          <button className="btn-secondary" onClick={() => console.log('View global config')}>
            🌐 Config Global
          </button>
          <button className="btn-primary" onClick={() => console.log('Test integration')}>
            🧪 Testar Integração
          </button>
        </div>
      </div>

      {/* ── Gestão REAL MCP do projeto (F2 Fase 2) ── */}
      <section style={{ padding: '0 24px 8px' }}>
        <McpProjectManager projectId={projectId || ''} />
      </section>

      {/* Project Overview (ilustrativo) */}
      <section className="project-overview">
        <div className="overview-cards">
          <div className="overview-card">
            <div className="card-icon">🔌</div>
            <div className="card-info">
              <h3>{enabledServices.length}</h3>
              <p>Serviços Habilitados</p>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">📡</div>
            <div className="card-info">
            <h3>{projectConfig.customEndpoints?.length || 0}</h3>
              <p>APIs Expostas</p>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">⚡</div>
            <div className="card-info">
              <h3>{projectConfig.serviceMappings.length}</h3>
              <p>Mapeamentos</p>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">🔄</div>
            <div className="card-info">
              <h3>{projectConfig.syncRules.frequency}s</h3>
              <p>Freq. Sync</p>
            </div>
          </div>
        </div>
      </section>

      {/* Enabled Services */}
      <section className="enabled-services-section">
        <div className="section-header">
          <h2>Serviços MCP Habilitados</h2>
          <button className="btn-primary" onClick={() => setShowAddServiceModal(true)}>
            + Habilitar Mais
          </button>
        </div>
        
        <div className="services-table">
          <table>
            <thead>
              <tr>
                <th>Nome do Serviço</th>
                <th>Propósito</th>
                <th>Status</th>
                <th>Uso</th>
                <th>Configuração</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {enabledServices.map(service => (
                <tr key={service.id}>
                  <td>
                    <div className="service-info">
                      <div className="service-header">
                        <span className="service-icon">
                          {getCategoryIcon(service.category)}
                        </span>
                        <span className="service-name">{service.name}</span>
                      </div>
                      <div className="service-provider">{service.provider}</div>
                    </div>
                  </td>
                  <td className="service-purpose">{service.description}</td>
                  <td>
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(service.status) }}
                    >
                      {getStatusIcon(service.status)} {service.status}
                    </span>
                  </td>
                  <td>
                    <div className="usage-stats">
                      <div className="usage-level">{service.usage}</div>
                      <div className="usage-details">
                        {service.id === 'storage_service_1' && '450 calls/h'}
                        {service.id === 'analytics_service_1' && '120 calls/h'}
                        {service.id === 'auth_service_1' && '45 calls/h'}
                      </div>
                    </div>
                  </td>
                  <td>
                    <button 
                      className="btn-icon"
                      onClick={() => setSelectedService(service)}
                      title="Configurar"
                    >
                      ⚙️
                    </button>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('Test service', service.id)}
                        title="Testar"
                      >
                        🧪
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('Monitor service', service.id)}
                        title="Monitorar"
                      >
                        📊
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => handleDisableService(service.id)}
                        title="Desabilitar"
                      >
                        ❌
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Service Mappings */}
      <section className="mappings-section">
        <div className="section-header">
          <h2>Mapeamentos Específicos do Projeto</h2>
          <button className="btn-secondary" onClick={() => console.log('Auto configure')}>
            ✨ Config Inteligente
          </button>
        </div>
        
        <div className="mappings-table">
          <table>
            <thead>
              <tr>
                <th>Modelo Local</th>
                <th>Serviço MCP</th>
                <th>Endpoint</th>
                <th>Formato</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {projectConfig.serviceMappings.map((mapping, index) => (
                <tr key={index}>
                  <td className="local-model">{mapping.localModel}</td>
                  <td className="mcp-service">{mapping.mcpService}</td>
                  <td className="endpoint">
                    <code>{mapping.endpoint}</code>
                  </td>
                  <td className="format">
                    <span className="format-badge">{mapping.format}</span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('Edit mapping', index)}
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('Test mapping', index)}
                        title="Testar"
                      >
                        🧪
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('Delete mapping', index)}
                        title="Remover"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Sync Rules */}
      <section className="sync-rules-section">
        <h2>Regras de Sincronização</h2>
        <div className="config-grid">
          <div className="config-group">
            <label>Frequência de Sincronização (segundos):</label>
            <select 
              value={projectConfig.syncRules.frequency}
              onChange={(e) => handleConfigChange('frequency', parseInt(e.target.value))}
            >
              <option value={10}>10 segundos</option>
              <option value={30}>30 segundos</option>
              <option value={60}>1 minuto</option>
              <option value={300}>5 minutos</option>
            </select>
          </div>
          
          <div className="config-group">
            <label>Resolução de Conflitos:</label>
            <select 
              value={projectConfig.syncRules.conflictResolution}
              onChange={(e) => handleConfigChange('conflictResolution', e.target.value)}
            >
              <option value="merge_local">Mesclar (Prioridade Local)</option>
              <option value="merge_remote">Mesclar (Prioridade Remota)</option>
              <option value="local_wins">Local Sempre Vence</option>
              <option value="remote_wins">Remoto Sempre Vence</option>
              <option value="manual">Resolução Manual</option>
            </select>
          </div>

          <div className="config-group">
            <label>Tamanho do Lote:</label>
            <input
              type="number"
              value={projectConfig.syncRules.batchSize}
              onChange={(e) => handleConfigChange('batchSize', parseInt(e.target.value))}
              min="10"
              max="1000"
            />
          </div>

          <div className="config-group">
            <label>Máximo de Tentativas:</label>
            <input
              type="number"
              value={projectConfig.syncRules.retryPolicy.maxAttempts}
              onChange={(e) => setProjectConfig(prev => ({
                ...prev,
                syncRules: {
                  ...prev.syncRules,
                  retryPolicy: {
                    ...prev.syncRules.retryPolicy,
                    maxAttempts: parseInt(e.target.value)
                  }
                }
              }))}
              min="1"
              max="10"
            />
          </div>

          <div className="config-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={projectConfig.syncRules.compressionEnabled}
                onChange={(e) => handleConfigChange('compressionEnabled', e.target.checked)}
              />
              Compressão Habilitada
            </label>
          </div>
        </div>

        {/* Domain-specific Rules */}
        <div className="domain-rules">
          <h3>Regras Específicas do Domínio</h3>
          <div className="rules-list">
            {Object.entries(projectConfig.syncRules.domainRules).map(([key, value]) => (
              <div key={key} className="rule-item">
                <span className="rule-key">{key}:</span>
                <span className="rule-value">{value}</span>
                <button 
                  className="btn-icon"
                  onClick={() => console.log('Edit rule', key)}
                  title="Editar"
                >
                  ✏️
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Exposed Services */}
      <section className="exposed-services-section">
        <div className="section-header">
          <h2>Serviços Expostos pelo Projeto</h2>
          <button className="btn-primary" onClick={() => setShowAddEndpointModal(true)}>
            + Expor Novo
          </button>
        </div>
        
        <div className="endpoints-table">
          <table>
            <thead>
              <tr>
                <th>Nome do Serviço</th>
                <th>Endpoint</th>
                <th>Método</th>
                <th>Clientes</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
            {(projectConfig.customEndpoints || []).map(endpoint => (
                <tr key={endpoint.id}>
                  <td className="endpoint-name">{endpoint.name}</td>
                  <td className="endpoint-path">
                    <code>{endpoint.endpoint}</code>
                  </td>
                  <td className="endpoint-method">
                    <span className="method-badge">{endpoint.method}</span>
                  </td>
                  <td className="endpoint-clients">{endpoint.clientsConnected}</td>
                  <td>
                    <span 
                      className="status-badge"
                      style={{ 
                        backgroundColor: endpoint.status === 'active' ? '#22c55e' : 
                                       endpoint.status === 'testing' ? '#eab308' : '#6b7280'
                      }}
                    >
                      {endpoint.status === 'active' && '🟢'}
                      {endpoint.status === 'testing' && '🟡'}
                      {endpoint.status === 'inactive' && '⚪'}
                      {endpoint.status}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('Configure endpoint', endpoint.id)}
                        title="Configurar"
                      >
                        ⚙️
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('View analytics', endpoint.id)}
                        title="Analytics"
                      >
                        📊
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => console.log('Test endpoint', endpoint.id)}
                        title="Testar"
                      >
                        🧪
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Project Status */}
      <section className="project-status-section">
        <div className="status-cards">
          <div className="status-card">
            <h3>Status de Sincronização</h3>
            <div className="status-info">
              <div className="status-item">
                <span className="status-label">✅ Tempo Real:</span>
                <span className="status-value">Ativo</span>
              </div>
              <div className="status-item">
                <span className="status-label">Última Sync:</span>
                <span className="status-value">15s atrás</span>
              </div>
              <div className="status-item">
                <span className="status-label">Pendentes:</span>
                <span className="status-value">0</span>
              </div>
              <div className="status-item">
                <span className="status-label">Erros:</span>
                <span className="status-value">0</span>
              </div>
            </div>
          </div>

          <div className="status-card">
            <h3>Uso de Serviços</h3>
            <div className="usage-stats">
              <div className="usage-item">
                <span className="usage-service">DataStore:</span>
                <span className="usage-value">450 calls/h</span>
              </div>
              <div className="usage-item">
                <span className="usage-service">Analytics:</span>
                <span className="usage-value">120 calls/h</span>
              </div>
              <div className="usage-item">
                <span className="usage-service">Auth:</span>
                <span className="usage-value">45 calls/h</span>
              </div>
            </div>
          </div>

          <div className="status-card">
            <h3>Isolamento do Projeto</h3>
            <div className="isolation-info">
              <div className="isolation-item">
                <span className="isolation-label">✅ Habilitado</span>
              </div>
              <div className="isolation-item">
                <span className="isolation-label">Namespace:</span>
                <span className="isolation-value">{projectConfig.isolationNamespace}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Action Buttons */}
      <div className="page-actions">
        <button className="btn-secondary" onClick={() => console.log('Export config')}>
          📤 Exportar Config
        </button>
        <button className="btn-secondary" onClick={() => console.log('View global')}>
          🌐 Ver Global
        </button>
        <button className="btn-primary" onClick={() => console.log('Save config')}>
          💾 Salvar Configurações
        </button>
      </div>

      {/* Add Service Modal */}
      {showAddServiceModal && (
        <div className="modal-overlay" onClick={() => setShowAddServiceModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Habilitar Serviços MCP</h3>
              <button 
                className="btn-close"
                onClick={() => setShowAddServiceModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>Selecione os serviços que deseja habilitar para este projeto:</p>
              <div className="available-services">
                {availableServices.map(service => (
                  <div key={service.id} className="service-option">
                    <div className="service-info">
                      <div className="service-header">
                        <span className="service-icon">
                          {getCategoryIcon(service.category)}
                        </span>
                        <span className="service-name">{service.name}</span>
                        <span 
                          className="status-badge small"
                          style={{ backgroundColor: getStatusColor(service.status) }}
                        >
                          {getStatusIcon(service.status)}
                        </span>
                      </div>
                      <div className="service-description">{service.description}</div>
                      <div className="service-provider">Por: {service.provider}</div>
                    </div>
                    <button 
                      className="btn-primary"
                      onClick={() => {
                        handleEnableService(service.id);
                        setShowAddServiceModal(false);
                      }}
                    >
                      Habilitar
                    </button>
                  </div>
                ))}
                {availableServices.length === 0 && (
                  <div className="no-services">
                    <p>Todos os serviços disponíveis já estão habilitados para este projeto.</p>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn-secondary"
                onClick={() => setShowAddServiceModal(false)}
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Endpoint Modal */}
      {showAddEndpointModal && (
        <div className="modal-overlay" onClick={() => setShowAddEndpointModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Expor Novo Serviço</h3>
              <button 
                className="btn-close"
                onClick={() => setShowAddEndpointModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome do Serviço:</label>
                <input 
                  type="text" 
                  placeholder="Ex: CustomerAnalyticsAPI"
                  value={newEndpointData.name}
                  onChange={(e) => setNewEndpointData(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                />
              </div>
              <div className="form-group">
                <label>Endpoint:</label>
                <input 
                  type="text" 
                  placeholder="/api/analytics"
                  value={newEndpointData.endpoint}
                  onChange={(e) => setNewEndpointData(prev => ({
                    ...prev,
                    endpoint: e.target.value
                  }))}
                />
              </div>
              <div className="form-group">
                <label>Método HTTP:</label>
                <select
                  value={newEndpointData.method}
                  onChange={(e) => setNewEndpointData(prev => ({
                    ...prev,
                    method: e.target.value as 'GET' | 'POST' | 'PUT' | 'DELETE'
                  }))}
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="DELETE">DELETE</option>
                </select>
              </div>
              <div className="form-group">
                <label>Autenticação:</label>
                <select
                  value={newEndpointData.authentication}
                  onChange={(e) => setNewEndpointData(prev => ({
                    ...prev,
                    authentication: e.target.value as 'none' | 'api_key' | 'bearer_token' | 'oauth'
                  }))}
                >
                  <option value="none">Nenhuma</option>
                  <option value="api_key">API Key</option>
                  <option value="bearer_token">Bearer Token</option>
                  <option value="oauth">OAuth</option>
                </select>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn-secondary"
                onClick={() => setShowAddEndpointModal(false)}
              >
                Cancelar
              </button>
              <button 
                className="btn-primary"
                onClick={handleCreateEndpoint}
                disabled={!newEndpointData.name || !newEndpointData.endpoint}
              >
                Expor Serviço
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default McpProjectIntegrationPage;