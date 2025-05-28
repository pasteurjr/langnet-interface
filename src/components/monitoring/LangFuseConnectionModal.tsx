import React, { useState } from 'react';
import { X, Database, Key, Settings, TestTube } from 'lucide-react';
import { LangfuseConnection, MonitoringStatus } from '../../types/monitoring';
import './monitoring.css';

interface LangfuseConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect: (config: Partial<LangfuseConnection>) => void;
  currentConnection?: LangfuseConnection;
  projectId: string;
}

export const LangfuseConnectionModal: React.FC<LangfuseConnectionModalProps> = ({
  isOpen,
  onClose,
  onConnect,
  currentConnection,
  projectId
}) => {
  const [formData, setFormData] = useState({
    publicKey: currentConnection?.publicKey || '',
    secretKey: currentConnection?.secretKey || '',
    host: currentConnection?.host || 'https://cloud.langfuse.com',
    enableTracing: currentConnection?.settings.enableTracing ?? true,
    sampleRate: currentConnection?.settings.sampleRate ?? 1.0,
    bufferSize: currentConnection?.settings.bufferSize ?? 1000,
    flushInterval: currentConnection?.settings.flushInterval ?? 5000,
    enableMetrics: currentConnection?.settings.enableMetrics ?? true,
    enableAlerts: currentConnection?.settings.enableAlerts ?? true
  });

  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setTestResult(null);
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);

    // Simulate connection test
    setTimeout(() => {
      if (formData.publicKey && formData.secretKey) {
        setTestResult({ success: true, message: 'Conexão testada com sucesso!' });
      } else {
        setTestResult({ success: false, message: 'Chaves de API são obrigatórias' });
      }
      setIsTesting(false);
    }, 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const connectionConfig = {
      id: currentConnection?.id || `conn_${Date.now()}`,
      projectId,
      publicKey: formData.publicKey,
      secretKey: formData.secretKey,
      host: formData.host,
      status: MonitoringStatus.CONNECTING,
      settings: {
        enableTracing: formData.enableTracing,
        sampleRate: formData.sampleRate,
        bufferSize: formData.bufferSize,
        flushInterval: formData.flushInterval,
        enableMetrics: formData.enableMetrics,
        enableAlerts: formData.enableAlerts
      }
    };

    onConnect(connectionConfig);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content langfuse-modal">
        <div className="modal-header">
          <h2>
            <Database size={24} />
            Configurar Conexão Langfuse
          </h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-section">
            <h3>
              <Key size={18} />
              Credenciais de API
            </h3>
            
            <div className="form-group">
              <label htmlFor="host">Host Langfuse</label>
              <input
                id="host"
                type="url"
                value={formData.host}
                onChange={(e) => handleInputChange('host', e.target.value)}
                placeholder="https://cloud.langfuse.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="publicKey">Public Key</label>
              <input
                id="publicKey"
                type="text"
                value={formData.publicKey}
                onChange={(e) => handleInputChange('publicKey', e.target.value)}
                placeholder="pk-lf-..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="secretKey">Secret Key</label>
              <input
                id="secretKey"
                type="password"
                value={formData.secretKey}
                onChange={(e) => handleInputChange('secretKey', e.target.value)}
                placeholder="sk-lf-..."
                required
              />
            </div>

            <button
              type="button"
              className="test-connection-btn"
              onClick={handleTestConnection}
              disabled={isTesting || !formData.publicKey || !formData.secretKey}
            >
              <TestTube size={16} />
              {isTesting ? 'Testando...' : 'Testar Conexão'}
            </button>

            {testResult && (
              <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
                {testResult.message}
              </div>
            )}
          </div>

          <div className="form-section">
            <h3>
              <Settings size={18} />
              Configurações de Monitoramento
            </h3>

            <div className="form-row">
              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.enableTracing}
                    onChange={(e) => handleInputChange('enableTracing', e.target.checked)}
                  />
                  Habilitar Tracing
                </label>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.enableMetrics}
                    onChange={(e) => handleInputChange('enableMetrics', e.target.checked)}
                  />
                  Habilitar Métricas
                </label>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="sampleRate">Taxa de Amostragem</label>
                <input
                  id="sampleRate"
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.sampleRate}
                  onChange={(e) => handleInputChange('sampleRate', parseFloat(e.target.value))}
                />
                <small>1.0 = 100% dos traces</small>
              </div>

              <div className="form-group">
                <label htmlFor="bufferSize">Tamanho do Buffer</label>
                <input
                  id="bufferSize"
                  type="number"
                  min="100"
                  max="10000"
                  step="100"
                  value={formData.bufferSize}
                  onChange={(e) => handleInputChange('bufferSize', parseInt(e.target.value))}
                />
                <small>Número de eventos no buffer</small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="flushInterval">Intervalo de Flush (ms)</label>
                <input
                  id="flushInterval"
                  type="number"
                  min="1000"
                  max="60000"
                  step="1000"
                  value={formData.flushInterval}
                  onChange={(e) => handleInputChange('flushInterval', parseInt(e.target.value))}
                />
                <small>Frequência de envio para Langfuse</small>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.enableAlerts}
                    onChange={(e) => handleInputChange('enableAlerts', e.target.checked)}
                  />
                  Habilitar Alertas
                </label>
              </div>
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancelar
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={!formData.publicKey || !formData.secretKey}
            >
              {currentConnection ? 'Atualizar Conexão' : 'Conectar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};