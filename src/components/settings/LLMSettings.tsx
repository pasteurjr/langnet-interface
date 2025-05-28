import React, { useState } from 'react';
import { Plus, Edit, Trash2, Eye, EyeOff, TestTube, Star, Zap } from 'lucide-react';
import { LLMConfiguration, LLMProvider } from '../../types/settings';
import './settings.css';

interface LLMSettingsProps {
  configurations: LLMConfiguration[];
  onUpdate: (llmId: string, config: Partial<LLMConfiguration>) => void;
}

export const LLMSettings: React.FC<LLMSettingsProps> = ({
  configurations,
  onUpdate
}) => {
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});
  const [editingLLM, setEditingLLM] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newLLM, setNewLLM] = useState<Partial<LLMConfiguration>>({
    provider: LLMProvider.OPENAI,
    name: '',
    apiKey: '',
    model: '',
    temperature: 0.3,
    maxTokens: 4000,
    timeout: 30000,
    retryAttempts: 3,
    isDefault: false,
    enabled: true
  });

  const toggleApiKeyVisibility = (llmId: string) => {
    setShowApiKeys(prev => ({ ...prev, [llmId]: !prev[llmId] }));
  };

  const handleEditLLM = (llmId: string) => {
    setEditingLLM(llmId);
  };

  const handleSaveLLM = (llmId: string, config: Partial<LLMConfiguration>) => {
    onUpdate(llmId, config);
    setEditingLLM(null);
  };

  const handleAddLLM = () => {
    // Simular adição de novo LLM
    console.log('Adding new LLM:', newLLM);
    setShowAddForm(false);
    setNewLLM({
      provider: LLMProvider.OPENAI,
      name: '',
      apiKey: '',
      model: '',
      temperature: 0.3,
      maxTokens: 4000,
      timeout: 30000,
      retryAttempts: 3,
      isDefault: false,
      enabled: true
    });
  };

  const testConnection = async (llmId: string) => {
    console.log('Testing connection for LLM:', llmId);
    // Simular teste de conexão
  };

  const setAsDefault = (llmId: string) => {
    configurations.forEach(config => {
      onUpdate(config.id, { isDefault: config.id === llmId });
    });
  };

  const getProviderIcon = (provider: LLMProvider) => {
    switch (provider) {
      case LLMProvider.OPENAI: return '🤖';
      case LLMProvider.ANTHROPIC: return '🧠';
      case LLMProvider.GOOGLE: return '🔍';
      case LLMProvider.AZURE_OPENAI: return '☁️';
      case LLMProvider.COHERE: return '📝';
      default: return '⚡';
    }
  };

  const getProviderName = (provider: LLMProvider) => {
    switch (provider) {
      case LLMProvider.OPENAI: return 'OpenAI';
      case LLMProvider.ANTHROPIC: return 'Anthropic';
      case LLMProvider.GOOGLE: return 'Google';
      case LLMProvider.AZURE_OPENAI: return 'Azure OpenAI';
      case LLMProvider.COHERE: return 'Cohere';
      default: return provider;
    }
  };

  const formatApiKey = (apiKey: string, show: boolean) => {
    if (show) return apiKey;
    return apiKey.substring(0, 6) + '*'.repeat(apiKey.length - 10) + apiKey.substring(apiKey.length - 4);
  };

  return (
    <div className="llm-settings">
      <div className="settings-section">
        <div className="section-header">
          <h3>
            <Zap size={18} />
            Configurações de LLM ({configurations.length})
          </h3>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddForm(true)}
          >
            <Plus size={16} />
            Adicionar LLM
          </button>
        </div>

        <div className="llm-list">
          {configurations.map(config => (
            <div key={config.id} className="llm-card">
              <div className="llm-header">
                <div className="llm-info">
                  <div className="llm-provider">
                    <span className="provider-icon">{getProviderIcon(config.provider)}</span>
                    <span className="provider-name">{getProviderName(config.provider)}</span>
                  </div>
                  <div className="llm-name">{config.name}</div>
                  <div className="llm-model">{config.model}</div>
                </div>
                
                <div className="llm-status">
                  {config.isDefault && (
                    <span className="default-badge">
                      <Star size={12} />
                      Padrão
                    </span>
                  )}
                  <span className={`status-badge ${config.enabled ? 'enabled' : 'disabled'}`}>
                    {config.enabled ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
              </div>

              <div className="llm-details">
                <div className="llm-config">
                  <div className="config-row">
                    <div className="config-item">
                      <span className="config-label">API Key:</span>
                      <div className="api-key-field">
                        <span className="api-key-value">
                          {formatApiKey(config.apiKey, showApiKeys[config.id])}
                        </span>
                        <button
                          className="toggle-key-btn"
                          onClick={() => toggleApiKeyVisibility(config.id)}
                        >
                          {showApiKeys[config.id] ? <EyeOff size={14} /> : <Eye size={14} />}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="config-row">
                    <div className="config-item">
                      <span className="config-label">Temperature:</span>
                      <span className="config-value">{config.temperature}</span>
                    </div>
                    <div className="config-item">
                      <span className="config-label">Max Tokens:</span>
                      <span className="config-value">{config.maxTokens.toLocaleString()}</span>
                    </div>
                    <div className="config-item">
                      <span className="config-label">Timeout:</span>
                      <span className="config-value">{config.timeout / 1000}s</span>
                    </div>
                    <div className="config-item">
                      <span className="config-label">Tentativas:</span>
                      <span className="config-value">{config.retryAttempts}</span>
                    </div>
                  </div>

                  {config.rateLimit && (
                    <div className="config-row">
                      <div className="config-item">
                        <span className="config-label">Rate Limit:</span>
                        <span className="config-value">
                          {config.rateLimit.requestsPerMinute} req/min, {config.rateLimit.tokensPerMinute.toLocaleString()} tokens/min
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="llm-actions">
                  <button 
                    className="action-btn test-btn"
                    onClick={() => testConnection(config.id)}
                  >
                    <TestTube size={14} />
                    Testar
                  </button>
                  
                  {!config.isDefault && (
                    <button 
                      className="action-btn default-btn"
                      onClick={() => setAsDefault(config.id)}
                    >
                      <Star size={14} />
                      Definir como Padrão
                    </button>
                  )}
                  
                  <button 
                    className="action-btn edit-btn"
                    onClick={() => handleEditLLM(config.id)}
                  >
                    <Edit size={14} />
                    Editar
                  </button>
                  
                  <button className="action-btn delete-btn">
                    <Trash2 size={14} />
                    Remover
                  </button>
                </div>
              </div>

              <div className="llm-metadata">
                <div className="metadata-item">
                  <span className="metadata-label">Criado:</span>
                  <span className="metadata-value">
                    {new Date(config.createdAt).toLocaleDateString('pt-BR')}
                  </span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Atualizado:</span>
                  <span className="metadata-value">
                    {new Date(config.updatedAt).toLocaleDateString('pt-BR')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content llm-modal">
            <div className="modal-header">
              <h3>Adicionar Novo LLM</h3>
              <button 
                className="modal-close"
                onClick={() => setShowAddForm(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Provider</label>
                <select 
                  value={newLLM.provider}
                  onChange={(e) => setNewLLM(prev => ({ ...prev, provider: e.target.value as LLMProvider }))}
                >
                  {Object.values(LLMProvider).map(provider => (
                    <option key={provider} value={provider}>
                      {getProviderName(provider)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Nome</label>
                <input
                  type="text"
                  value={newLLM.name || ''}
                  onChange={(e) => setNewLLM(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="ex: GPT-4 Production"
                />
              </div>

              <div className="form-group">
                <label>Modelo</label>
                <input
                  type="text"
                  value={newLLM.model || ''}
                  onChange={(e) => setNewLLM(prev => ({ ...prev, model: e.target.value }))}
                  placeholder="ex: gpt-4"
                />
              </div>

              <div className="form-group">
                <label>API Key</label>
                <input
                  type="password"
                  value={newLLM.apiKey || ''}
                  onChange={(e) => setNewLLM(prev => ({ ...prev, apiKey: e.target.value }))}
                  placeholder="Sua API key"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Temperature</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={newLLM.temperature}
                    onChange={(e) => setNewLLM(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                  />
                </div>

                <div className="form-group">
                  <label>Max Tokens</label>
                  <input
                    type="number"
                    min="1"
                    max="32000"
                    value={newLLM.maxTokens}
                    onChange={(e) => setNewLLM(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Timeout (ms)</label>
                  <input
                    type="number"
                    min="1000"
                    max="300000"
                    value={newLLM.timeout}
                    onChange={(e) => setNewLLM(prev => ({ ...prev, timeout: parseInt(e.target.value) }))}
                  />
                </div>

                <div className="form-group">
                  <label>Tentativas</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={newLLM.retryAttempts}
                    onChange={(e) => setNewLLM(prev => ({ ...prev, retryAttempts: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={newLLM.isDefault}
                    onChange={(e) => setNewLLM(prev => ({ ...prev, isDefault: e.target.checked }))}
                  />
                  Definir como LLM padrão
                </label>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={newLLM.enabled}
                    onChange={(e) => setNewLLM(prev => ({ ...prev, enabled: e.target.checked }))}
                  />
                  Habilitar LLM
                </label>
              </div>
            </div>

            <div className="modal-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowAddForm(false)}
              >
                Cancelar
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleAddLLM}
                disabled={!newLLM.name || !newLLM.apiKey || !newLLM.model}
              >
                Adicionar LLM
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};