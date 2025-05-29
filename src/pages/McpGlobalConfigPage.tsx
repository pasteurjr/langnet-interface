// src/pages/McpGlobalConfigPage.tsx
import React, { useState, useEffect } from 'react';
import { McpServer, McpService, McpGlobalConfig, McpHealthStatus, McpDiscoveryResult } from '../types';
import './McpGlobalConfigPage.css';

const McpGlobalConfigPage: React.FC = () => {
  const [servers, setServers] = useState<McpServer[]>([
    {
      id: 'server_1',
      name: 'Enterprise MCP',
      url: 'wss://mcp.corp.com:8080',
      status: 'online',
      provider: 'Corp Systems',
      description: 'Servidor corporativo principal',
      latency: 45,
      uptime: 99.5,
      lastHealthCheck: '2025-05-27T14:30:00Z'
    },
    {
      id: 'server_2',
      name: 'Public Services',
      url: 'wss://api.mcp.com:8080',
      status: 'online',
      provider: 'MCP Foundation',
      description: 'Serviços públicos MCP',
      latency: 67,
      uptime: 98.2,
      lastHealthCheck: '2025-05-27T14:29:45Z'
    },
    {
      id: 'server_3',
      name: 'Development',
      url: 'ws://localhost:8080',
      status: 'local',
      provider: 'Local Dev',
      description: 'Servidor de desenvolvimento local',
      latency: 12,
      uptime: 95.0,
      lastHealthCheck: '2025-05-27T14:30:15Z'
    },
    {
      id: 'server_4',
      name: 'ML Services',
      url: 'wss://ml.mcp.com:8080',
      status: 'error',
      provider: 'AI Corp',
      description: 'Serviços de Machine Learning',
      latency: 0,
      uptime: 0,
      lastHealthCheck: '2025-05-27T13:45:30Z'
    }
  ]);

  const [globalConfig, setGlobalConfig] = useState<McpGlobalConfig>({
    defaultTimeout: 30,
    retryAttempts: 3,     // ← Este é obrigatório
    maxRetryAttempts: 3,  // ← Pode manter este também se quiser
    circuitBreakerEnabled: true,
    circuitBreakerThreshold: 5,
    healthCheckInterval: 30,
    rateLimitDefault: 1000,
    tlsVersion: '1.3',
    discoveryEnabled: true,
    discoveryInterval: 5,
    discoveryProtocol: 'mDNS + Registry',
    serviceCacheTtl: 60
  });

  const [discoveryResult, setDiscoveryResult] = useState<McpDiscoveryResult>({
    totalServices: 47,
    onlineServices: 42,
    lastScan: '2025-05-27T14:29:00Z',
    networkHealth: 98.7,
    avgLatency: 23,
    servicesByCategory: {
      'auth': 8,
      'storage': 12,
      'ai': 15,
      'communication': 6,
      'analytics': 4,
      'other': 2
    },
    usageStats: {
      'auth_service_1': { projectsUsing: 8, avgLoad: 67, peakUsagePerDay: 2100 },
      'storage_service_1': { projectsUsing: 12, avgLoad: 45, peakUsagePerDay: 8700 },
      'ai_service_1': { projectsUsing: 6, avgLoad: 23, peakUsagePerDay: 456 }
    }
  });

  const [healthStatus, setHealthStatus] = useState<McpHealthStatus>({
    overall: 'healthy',
    services: {},
    connections: {
      total: 47,
      active: 42,
      errors: 5
    },
    performance: {
      avgLatency: 45,
      throughput: 450,
      errorRate: 0.02
    }
  });

  const [showAddServerModal, setShowAddServerModal] = useState(false);
  const [selectedServer, setSelectedServer] = useState<McpServer | null>(null);
  const [newServerData, setNewServerData] = useState({
    name: '',
    url: '',
    provider: '',
    description: ''
  });

  const handleConfigChange = (key: keyof McpGlobalConfig, value: any) => {
    setGlobalConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleAddServer = () => {
    setShowAddServerModal(true);
  };

  const handleCreateServer = () => {
    const newServer: McpServer = {
      id: `server_${Date.now()}`,
      name: newServerData.name,
      url: newServerData.url,
      provider: newServerData.provider,
      description: newServerData.description,
      status: 'offline',
      latency: 0,
      uptime: 0
    };
    
    setServers(prev => [...prev, newServer]);
    setNewServerData({ name: '', url: '', provider: '', description: '' });
    setShowAddServerModal(false);
  };

  const handleServerAction = (serverId: string, action: string) => {
    console.log(`Action ${action} for server ${serverId}`);
    switch (action) {
      case 'test':
        // Implementar teste de conexão
        break;
      case 'delete':
        setServers(prev => prev.filter(s => s.id !== serverId));
        break;
      default:
        break;
    }
  };

  const handleTestAllConnections = () => {
    console.log('Testing all connections...');
    // Implementar teste de todas as conexões
  };

  const handleRefreshServices = () => {
    console.log('Refreshing service discovery...');
    // Implementar refresh dos serviços
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return '🟢';
      case 'offline': return '❌';
      case 'local': return '🟡';
      case 'error': return '🔴';
      default: return '⚪';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#22c55e';
      case 'offline': return '#ef4444';
      case 'local': return '#eab308';
      case 'error': return '#dc2626';
      default: return '#6b7280';
    }
  };

  return (
    <div className="mcp-global-config-container">
      <div className="page-header">
        <h1>Configuração Global MCP</h1>
        <div className="header-actions">
          <button className="btn-secondary" onClick={handleRefreshServices}>
            🔄 Atualizar
          </button>
          <button className="btn-primary" onClick={handleTestAllConnections}>
            🔗 Testar Conexões
          </button>
        </div>
      </div>

      {/* Status Overview */}
      <section className="status-overview">
        <div className="status-cards">
          <div className="status-card">
            <div className="status-icon">🌐</div>
            <div className="status-info">
              <h3>{discoveryResult.totalServices}</h3>
              <p>Serviços Totais</p>
            </div>
          </div>
          <div className="status-card">
            <div className="status-icon">🟢</div>
            <div className="status-info">
              <h3>{discoveryResult.onlineServices}</h3>
              <p>Online</p>
            </div>
          </div>
          <div className="status-card">
            <div className="status-icon">⚡</div>
            <div className="status-info">
              <h3>{discoveryResult.avgLatency}ms</h3>
              <p>Latência Média</p>
            </div>
          </div>
          <div className="status-card">
            <div className="status-icon">📊</div>
            <div className="status-info">
              <h3>{discoveryResult.networkHealth}%</h3>
              <p>Saúde da Rede</p>
            </div>
          </div>
        </div>
      </section>

      {/* MCP Servers Registry */}
      <section className="servers-section">
        <div className="section-header">
          <h2>Registry de Servidores MCP</h2>
          <button className="btn-primary" onClick={handleAddServer}>
            + Adicionar Servidor
          </button>
        </div>
        
        <div className="servers-table">
          <table>
            <thead>
              <tr>
                <th>Nome do Servidor</th>
                <th>URL</th>
                <th>Status</th>
                <th>Provedor</th>
                <th>Latência</th>
                <th>Uptime</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {servers.map(server => (
                <tr key={server.id}>
                  <td>
                    <div className="server-info">
                      <span className="server-name">{server.name}</span>
                      {server.description && (
                        <span className="server-description">{server.description}</span>
                      )}
                    </div>
                  </td>
                  <td className="server-url">{server.url}</td>
                  <td>
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(server.status) }}
                    >
                      {getStatusIcon(server.status)} {server.status}
                    </span>
                  </td>
                  <td>{server.provider}</td>
                  <td>{server.latency ? `${server.latency}ms` : 'N/A'}</td>
                  <td>{server.uptime ? `${server.uptime}%` : 'N/A'}</td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="btn-icon"
                        onClick={() => handleServerAction(server.id, 'test')}
                        title="Testar Conexão"
                      >
                        🔗
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => setSelectedServer(server)}
                        title="Configurar"
                      >
                        ⚙️
                      </button>
                      <button 
                        className="btn-icon"
                        onClick={() => handleServerAction(server.id, 'delete')}
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

      {/* Global Security Settings */}
      <section className="security-section">
        <h2>Configurações Globais de Segurança</h2>
        <div className="config-grid">
          <div className="config-group">
            <label>Versão TLS Padrão:</label>
            <select 
              value={globalConfig.tlsVersion}
              onChange={(e) => handleConfigChange('tlsVersion', e.target.value)}
            >
              <option value="1.2">TLS 1.2</option>
              <option value="1.3">TLS 1.3</option>
            </select>
          </div>
          
          <div className="config-group">
            <label>Timeout Padrão (segundos):</label>
            <input
              type="number"
              value={globalConfig.defaultTimeout}
              onChange={(e) => handleConfigChange('defaultTimeout', parseInt(e.target.value))}
            />
          </div>

          <div className="config-group">
            <label>Máximo de Tentativas:</label>
            <input
              type="number"
              value={globalConfig.maxRetryAttempts}
              onChange={(e) => handleConfigChange('maxRetryAttempts', parseInt(e.target.value))}
            />
          </div>

          <div className="config-group">
            <label>Rate Limit Padrão (req/min):</label>
            <input
              type="number"
              value={globalConfig.rateLimitDefault}
              onChange={(e) => handleConfigChange('rateLimitDefault', parseInt(e.target.value))}
            />
          </div>

          <div className="config-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={globalConfig.circuitBreakerEnabled}
                onChange={(e) => handleConfigChange('circuitBreakerEnabled', e.target.checked)}
              />
              Circuit Breaker Habilitado
            </label>
          </div>

          <div className="config-group">
            <label>Limite Circuit Breaker:</label>
            <input
              type="number"
              value={globalConfig.circuitBreakerThreshold}
              onChange={(e) => handleConfigChange('circuitBreakerThreshold', parseInt(e.target.value))}
              disabled={!globalConfig.circuitBreakerEnabled}
            />
          </div>
        </div>
      </section>

      {/* Service Discovery Settings */}
      <section className="discovery-section">
        <h2>Configurações de Descoberta de Serviços</h2>
        <div className="config-grid">
          <div className="config-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={globalConfig.discoveryEnabled}
                onChange={(e) => handleConfigChange('discoveryEnabled', e.target.checked)}
              />
              Descoberta Automática Habilitada
            </label>
          </div>

          <div className="config-group">
            <label>Intervalo de Descoberta (minutos):</label>
            <input
              type="number"
              value={globalConfig.discoveryInterval}
              onChange={(e) => handleConfigChange('discoveryInterval', parseInt(e.target.value))}
              disabled={!globalConfig.discoveryEnabled}
            />
          </div>

          <div className="config-group">
            <label>Protocolo de Descoberta:</label>
            <select 
              value={globalConfig.discoveryProtocol}
              onChange={(e) => handleConfigChange('discoveryProtocol', e.target.value)}
              disabled={!globalConfig.discoveryEnabled}
            >
              <option value="mDNS">mDNS</option>
              <option value="Registry">Registry API</option>
              <option value="mDNS + Registry">mDNS + Registry</option>
            </select>
          </div>

          <div className="config-group">
            <label>TTL Cache de Serviços (minutos):</label>
            <input
              type="number"
              value={globalConfig.serviceCacheTtl}
              onChange={(e) => handleConfigChange('serviceCacheTtl', parseInt(e.target.value))}
            />
          </div>
        </div>
      </section>

      {/* Service Categories Overview */}
      <section className="categories-section">
        <h2>Catálogo de Serviços Disponíveis</h2>
        <div className="categories-grid">
          {Object.entries(discoveryResult.servicesByCategory).map(([category, count]) => (
            <div key={category} className="category-card">
              <div className="category-header">
                <span className="category-icon">
                  {category === 'auth' && '🔐'}
                  {category === 'storage' && '💾'}
                  {category === 'ai' && '🤖'}
                  {category === 'communication' && '📧'}
                  {category === 'analytics' && '📊'}
                  {category === 'other' && '⚙️'}
                </span>
                <h3>{category.charAt(0).toUpperCase() + category.slice(1)}</h3>
              </div>
              <div className="category-stats">
                <span className="service-count">{count} serviços</span>
                {discoveryResult.usageStats[`${category}_service_1`] && (
                  <span className="usage-info">
                    {discoveryResult.usageStats[`${category}_service_1`].projectsUsing} projetos usando
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Action Buttons */}
      <div className="page-actions">
        <button className="btn-secondary" onClick={() => console.log('Export config')}>
          📤 Exportar Configuração
        </button>
        <button className="btn-secondary" onClick={() => console.log('Import config')}>
          📥 Importar Configuração
        </button>
        <button className="btn-primary" onClick={() => console.log('Save config')}>
          💾 Salvar Configurações
        </button>
      </div>

      {/* Add Server Modal */}
      {showAddServerModal && (
        <div className="modal-overlay" onClick={() => setShowAddServerModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Adicionar Servidor MCP</h3>
              <button 
                className="btn-close"
                onClick={() => setShowAddServerModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome do Servidor:</label>
                <input 
                  type="text" 
                  placeholder="Ex: Servidor Corporativo"
                  value={newServerData.name}
                  onChange={(e) => setNewServerData(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label>URL:</label>
                <input 
                  type="text" 
                  placeholder="wss://mcp.example.com:8080"
                  value={newServerData.url}
                  onChange={(e) => setNewServerData(prev => ({ ...prev, url: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label>Provedor:</label>
                <input 
                  type="text" 
                  placeholder="Nome do provedor"
                  value={newServerData.provider}
                  onChange={(e) => setNewServerData(prev => ({ ...prev, provider: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label>Descrição:</label>
                <textarea 
                  placeholder="Descrição opcional do servidor"
                  value={newServerData.description}
                  onChange={(e) => setNewServerData(prev => ({ ...prev, description: e.target.value }))}
                ></textarea>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn-secondary"
                onClick={() => setShowAddServerModal(false)}
              >
                Cancelar
              </button>
              <button 
                className="btn-primary"
                onClick={handleCreateServer}
                disabled={!newServerData.name || !newServerData.url}
              >
                Adicionar Servidor
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default McpGlobalConfigPage;