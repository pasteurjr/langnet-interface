// src/components/settings/IntegrationsSettings.tsx
import React, { useState } from 'react';
import { 
  Zap, 
  Plus, 
  Settings, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  ExternalLink,
  Trash2,
  Edit3,
  Copy,
  Key,
  Globe,
  Database,
  Mail,
  MessageSquare,
  Github,
  Slack
} from 'lucide-react';
import { Integration } from '../../types/settings';
import './settings.css';

// Tipos locais que não existem no settings.ts
interface WebhookConfig {
  id: string;
  name: string;
  url: string;
  events: string[];
  enabled: boolean;
  secret: string;
  createdAt: string;
  lastTriggered: string | null;
}

interface ApiKey {
  id: string;
  name: string;
  description: string;
  key: string;
  permissions: string[];
  expiresAt?: string;
  createdAt: string;
  lastUsed: string | null;
}

interface IntegrationsSettingsProps {
  integrations: Integration[];
  webhooks: WebhookConfig[];
  apiKeys: ApiKey[];
  onUpdateIntegration: (id: string, updates: Partial<Integration>) => void;
  onCreateWebhook: (webhook: Omit<WebhookConfig, 'id'>) => void;
  onCreateApiKey: (apiKey: Omit<ApiKey, 'id'>) => void;
  onDeleteWebhook: (id: string) => void;
  onRevokeApiKey: (id: string) => void;
}

const IntegrationsSettings: React.FC<IntegrationsSettingsProps> = ({
  integrations,
  webhooks,
  apiKeys,
  onUpdateIntegration,
  onCreateWebhook,
  onCreateApiKey,
  onDeleteWebhook,
  onRevokeApiKey
}) => {
  const [activeTab, setActiveTab] = useState<'integrations' | 'webhooks' | 'api-keys'>('integrations');
  const [showWebhookModal, setShowWebhookModal] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);

  const [newWebhook, setNewWebhook] = useState({
    name: '',
    url: '',
    events: [] as string[],
    enabled: true,
    secret: ''
  });

  const [newApiKey, setNewApiKey] = useState({
    name: '',
    description: '',
    permissions: [] as string[],
    expiresAt: ''
  });

  const getIntegrationIcon = (type: string) => {
    switch (type) {
      case 'monitoring': return <Database className="w-5 h-5" />;
      case 'llm': return <Zap className="w-5 h-5" />;
      case 'communication': return <Slack className="w-5 h-5" />;
      case 'deployment': return <Github className="w-5 h-5" />;
      case 'storage': return <Database className="w-5 h-5" />;
      default: return <Globe className="w-5 h-5" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'configuring': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return <XCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'connected': return 'Conectado';
      case 'error': return 'Erro';
      case 'configuring': return 'Configurando';
      default: return 'Desconectado';
    }
  };

  const toggleIntegrationStatus = (id: string, currentHealthy: boolean) => {
    // Como não temos 'enabled', vamos simular mudando o status
    const newStatus = currentHealthy ? 'disconnected' : 'connected';
    onUpdateIntegration(id, { 
      healthCheck: {
        ...integrations.find(i => i.id === id)?.healthCheck!,
        isHealthy: !currentHealthy
      }
    });
  };

  const availableEvents = [
    'project.created',
    'project.updated',
    'project.deleted',
    'deployment.started',
    'deployment.completed',
    'deployment.failed',
    'monitoring.alert',
    'user.created',
    'user.updated'
  ];

  const availablePermissions = [
    'read:projects',
    'write:projects',
    'read:users',
    'write:users',
    'read:monitoring',
    'write:monitoring',
    'read:deployments',
    'write:deployments'
  ];

  const handleCreateWebhook = () => {
    if (newWebhook.name && newWebhook.url) {
      onCreateWebhook({
        ...newWebhook,
        createdAt: new Date().toISOString(),
        lastTriggered: null
      });
      setNewWebhook({
        name: '',
        url: '',
        events: [],
        enabled: true,
        secret: ''
      });
      setShowWebhookModal(false);
    }
  };

  const handleCreateApiKey = () => {
    if (newApiKey.name && newApiKey.description) {
      onCreateApiKey({
        ...newApiKey,
        key: 'sk-' + Math.random().toString(36).substr(2, 32),
        createdAt: new Date().toISOString(),
        lastUsed: null
      });
      setNewApiKey({
        name: '',
        description: '',
        permissions: [],
        expiresAt: ''
      });
      setShowApiKeyModal(false);
    }
  };

  const copyApiKey = (key: string) => {
    navigator.clipboard.writeText(key);
    // Toast notification would go here
  };

  return (
    <div className="settings-section">
      <div className="section-header">
        <h3>Integrações</h3>
        <div className="header-actions">
          <button className="btn btn-outline btn-sm">
            <ExternalLink className="w-4 h-4" />
            Documentação
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'integrations' ? 'active' : ''}`}
          onClick={() => setActiveTab('integrations')}
        >
          <Zap className="w-4 h-4" />
          Serviços ({integrations.length})
        </button>
        <button 
          className={`tab ${activeTab === 'webhooks' ? 'active' : ''}`}
          onClick={() => setActiveTab('webhooks')}
        >
          <Globe className="w-4 h-4" />
          Webhooks ({webhooks.length})
        </button>
        <button 
          className={`tab ${activeTab === 'api-keys' ? 'active' : ''}`}
          onClick={() => setActiveTab('api-keys')}
        >
          <Key className="w-4 h-4" />
          API Keys ({apiKeys.length})
        </button>
      </div>

      {activeTab === 'integrations' && (
        <div className="integrations-section">
          <div className="integrations-grid">
            {integrations.map(integration => (
              <div key={integration.id} className="integration-card">
                <div className="integration-header">
                  <div className="integration-icon">
                    {getIntegrationIcon(integration.type)}
                  </div>
                  <div className="integration-info">
                    <h4>{integration.name}</h4>
                    <p>{integration.provider}</p>
                  </div>
                  <div className="integration-status">
                    {getStatusIcon(integration.status)}
                  </div>
                </div>

                <div className="integration-details">
                  <div className="detail-row">
                    <span className="detail-label">Status:</span>
                    <span className={`status-badge ${integration.status}`}>
                      {getStatusLabel(integration.status)}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Última verificação:</span>
                    <span>{new Date(integration.healthCheck.lastCheck).toLocaleString()}</span>
                  </div>
                  {integration.endpoint && (
                    <div className="detail-row">
                      <span className="detail-label">Endpoint:</span>
                      <span className="endpoint">{integration.endpoint}</span>
                    </div>
                  )}
                  <div className="detail-row">
                    <span className="detail-label">Uso mensal:</span>
                    <span>{integration.usage.requestsThisMonth} requisições</span>
                  </div>
                </div>

                <div className="integration-actions">
                  <div className="toggle-switch">
                    <input
                      type="checkbox"
                      id={`toggle-${integration.id}`}
                      checked={integration.healthCheck.isHealthy}
                      onChange={() => toggleIntegrationStatus(integration.id, integration.healthCheck.isHealthy)}
                    />
                    <label htmlFor={`toggle-${integration.id}`}>
                      {integration.healthCheck.isHealthy ? 'Habilitado' : 'Desabilitado'}
                    </label>
                  </div>
                  <button className="btn btn-sm btn-outline">
                    <Settings className="w-3 h-3" />
                    Configurar
                  </button>
                  {integration.status === 'error' && (
                    <button className="btn btn-sm btn-primary">
                      Reconectar
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'webhooks' && (
        <div className="webhooks-section">
          <div className="section-actions">
            <button className="btn btn-primary" onClick={() => setShowWebhookModal(true)}>
              <Plus className="w-4 h-4" />
              Novo Webhook
            </button>
          </div>

          <div className="webhooks-table">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>URL</th>
                  <th>Eventos</th>
                  <th>Status</th>
                  <th>Último disparo</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {webhooks.map(webhook => (
                  <tr key={webhook.id}>
                    <td>
                      <div className="webhook-name">
                        <Globe className="w-4 h-4" />
                        {webhook.name}
                      </div>
                    </td>
                    <td>
                      <span className="webhook-url">{webhook.url}</span>
                    </td>
                    <td>
                      <div className="events-count">
                        {webhook.events.length} eventos
                      </div>
                    </td>
                    <td>
                      <span className={`status-badge ${webhook.enabled ? 'active' : 'inactive'}`}>
                        {webhook.enabled ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td>
                      {webhook.lastTriggered ? 
                        new Date(webhook.lastTriggered).toLocaleString() : 
                        'Nunca'
                      }
                    </td>
                    <td>
                      <div className="actions">
                        <button className="btn btn-sm btn-outline">
                          <Edit3 className="w-3 h-3" />
                        </button>
                        <button 
                          className="btn btn-sm btn-danger"
                          onClick={() => onDeleteWebhook(webhook.id)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'api-keys' && (
        <div className="api-keys-section">
          <div className="section-actions">
            <button className="btn btn-primary" onClick={() => setShowApiKeyModal(true)}>
              <Plus className="w-4 h-4" />
              Nova API Key
            </button>
          </div>

          <div className="api-keys-grid">
            {apiKeys.map(apiKey => (
              <div key={apiKey.id} className="api-key-card">
                <div className="api-key-header">
                  <div className="key-info">
                    <h4>{apiKey.name}</h4>
                    <p>{apiKey.description}</p>
                  </div>
                  <div className="key-actions">
                    <button 
                      className="btn btn-sm btn-outline"
                      onClick={() => copyApiKey(apiKey.key)}
                      title="Copiar chave"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div className="api-key-details">
                  <div className="key-value">
                    <label>Chave:</label>
                    <code>{apiKey.key.substring(0, 12)}...{apiKey.key.substring(apiKey.key.length - 4)}</code>
                  </div>
                  
                  <div className="key-permissions">
                    <label>Permissões ({apiKey.permissions.length}):</label>
                    <div className="permissions-list">
                      {apiKey.permissions.map((permission: string) => (
                        <span key={permission} className="permission-badge">
                          {permission}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="key-metadata">
                    <div className="metadata-item">
                      <span>Criada:</span>
                      <span>{new Date(apiKey.createdAt).toLocaleDateString()}</span>
                    </div>
                    {apiKey.expiresAt && (
                      <div className="metadata-item">
                        <span>Expira:</span>
                        <span>{new Date(apiKey.expiresAt).toLocaleDateString()}</span>
                      </div>
                    )}
                    <div className="metadata-item">
                      <span>Último uso:</span>
                      <span>{apiKey.lastUsed ? new Date(apiKey.lastUsed).toLocaleString() : 'Nunca'}</span>
                    </div>
                  </div>
                </div>

                <div className="api-key-footer">
                  <button 
                    className="btn btn-sm btn-danger"
                    onClick={() => onRevokeApiKey(apiKey.id)}
                  >
                    <Trash2 className="w-3 h-3" />
                    Revogar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal Novo Webhook */}
      {showWebhookModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Novo Webhook</h3>
              <button onClick={() => setShowWebhookModal(false)}>×</button>
            </div>
            <div className="modal-content">
              <div className="form-group">
                <label>Nome do webhook</label>
                <input
                  type="text"
                  value={newWebhook.name}
                  onChange={(e) => setNewWebhook({...newWebhook, name: e.target.value})}
                  placeholder="Digite o nome do webhook"
                />
              </div>
              <div className="form-group">
                <label>URL de destino</label>
                <input
                  type="url"
                  value={newWebhook.url}
                  onChange={(e) => setNewWebhook({...newWebhook, url: e.target.value})}
                  placeholder="https://example.com/webhook"
                />
              </div>
              <div className="form-group">
                <label>Secret (opcional)</label>
                <input
                  type="password"
                  value={newWebhook.secret}
                  onChange={(e) => setNewWebhook({...newWebhook, secret: e.target.value})}
                  placeholder="Secret para validação"
                />
              </div>
              <div className="form-group">
                <label>Eventos</label>
                <div className="events-checkboxes">
                  {availableEvents.map(event => (
                    <label key={event} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={newWebhook.events.includes(event)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewWebhook({
                              ...newWebhook,
                              events: [...newWebhook.events, event]
                            });
                          } else {
                            setNewWebhook({
                              ...newWebhook,
                              events: newWebhook.events.filter(e => e !== event)
                            });
                          }
                        }}
                      />
                      {event}
                    </label>
                  ))}
                </div>
              </div>
              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={newWebhook.enabled}
                    onChange={(e) => setNewWebhook({...newWebhook, enabled: e.target.checked})}
                  />
                  Habilitar webhook imediatamente
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowWebhookModal(false)}>
                Cancelar
              </button>
              <button className="btn btn-primary" onClick={handleCreateWebhook}>
                Criar Webhook
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Nova API Key */}
      {showApiKeyModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Nova API Key</h3>
              <button onClick={() => setShowApiKeyModal(false)}>×</button>
            </div>
            <div className="modal-content">
              <div className="form-group">
                <label>Nome da chave</label>
                <input
                  type="text"
                  value={newApiKey.name}
                  onChange={(e) => setNewApiKey({...newApiKey, name: e.target.value})}
                  placeholder="Digite o nome da chave"
                />
              </div>
              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  value={newApiKey.description}
                  onChange={(e) => setNewApiKey({...newApiKey, description: e.target.value})}
                  placeholder="Para que será usada esta chave?"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Data de expiração (opcional)</label>
                <input
                  type="date"
                  value={newApiKey.expiresAt}
                  onChange={(e) => setNewApiKey({...newApiKey, expiresAt: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Permissões</label>
                <div className="permissions-checkboxes">
                  {availablePermissions.map((permission: string) => (
                    <label key={permission} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={newApiKey.permissions.includes(permission)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewApiKey({
                              ...newApiKey,
                              permissions: [...newApiKey.permissions, permission]
                            });
                          } else {
                            setNewApiKey({
                              ...newApiKey,
                              permissions: newApiKey.permissions.filter(p => p !== permission)
                            });
                          }
                        }}
                      />
                      {permission}
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowApiKeyModal(false)}>
                Cancelar
              </button>
              <button className="btn btn-primary" onClick={handleCreateApiKey}>
                Gerar API Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrationsSettings;