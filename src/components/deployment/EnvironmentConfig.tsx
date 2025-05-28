import React, { useState } from 'react';
import { Settings, Server, Globe, Lock, Save, Eye, EyeOff, Plus, Trash2 } from 'lucide-react';
import { DeploymentEnvironment, DeploymentTarget, CloudProvider, InstanceType, ScalingType } from '../../types/deployment';
import './deployment.css';

interface EnvironmentConfigProps {
  environment: DeploymentEnvironment;
  onUpdate: (config: Partial<DeploymentEnvironment>) => void;
}

export const EnvironmentConfig: React.FC<EnvironmentConfigProps> = ({
  environment,
  onUpdate
}) => {
  const [config, setConfig] = useState(environment.config);
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [newEnvVar, setNewEnvVar] = useState({ key: '', value: '' });
  const [newSecret, setNewSecret] = useState({ key: '', value: '' });

  const handleConfigChange = (field: string, value: any) => {
    const updatedConfig = { ...config, [field]: value };
    setConfig(updatedConfig);
  };

  const handleSave = () => {
    onUpdate({ config });
  };

  const addEnvironmentVariable = () => {
    if (newEnvVar.key && newEnvVar.value) {
      const updatedVars = { ...config.environmentVariables, [newEnvVar.key]: newEnvVar.value };
      handleConfigChange('environmentVariables', updatedVars);
      setNewEnvVar({ key: '', value: '' });
    }
  };

  const removeEnvironmentVariable = (key: string) => {
    const updatedVars = { ...config.environmentVariables };
    delete updatedVars[key];
    handleConfigChange('environmentVariables', updatedVars);
  };

  const addSecret = () => {
    if (newSecret.key && newSecret.value) {
      const updatedSecrets = { ...config.secrets, [newSecret.key]: newSecret.value };
      handleConfigChange('secrets', updatedSecrets);
      setNewSecret({ key: '', value: '' });
    }
  };

  const removeSecret = (key: string) => {
    const updatedSecrets = { ...config.secrets };
    delete updatedSecrets[key];
    handleConfigChange('secrets', updatedSecrets);
  };

  const toggleSecretVisibility = (key: string) => {
    setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="environment-config">
      <div className="config-section">
        <div className="config-section-header">
          <h3>
            <Server size={18} />
            Configuração de Infraestrutura
          </h3>
        </div>

        <div className="config-form">
          <div className="form-row">
            <div className="form-group">
              <label>Target de Deployment</label>
              <select
                value={config.target}
                onChange={(e) => handleConfigChange('target', e.target.value as DeploymentTarget)}
              >
                <option value={DeploymentTarget.LOCAL}>Local</option>
                <option value={DeploymentTarget.DOCKER}>Docker</option>
                <option value={DeploymentTarget.KUBERNETES}>Kubernetes</option>
                <option value={DeploymentTarget.AWS}>AWS</option>
                <option value={DeploymentTarget.GCP}>Google Cloud</option>
                <option value={DeploymentTarget.AZURE}>Azure</option>
              </select>
            </div>

            <div className="form-group">
              <label>Cloud Provider</label>
              <select
                value={config.cloudProvider || ''}
                onChange={(e) => handleConfigChange('cloudProvider', e.target.value as CloudProvider)}
              >
                <option value="">Selecionar</option>
                <option value={CloudProvider.AWS}>AWS</option>
                <option value={CloudProvider.GCP}>Google Cloud</option>
                <option value={CloudProvider.AZURE}>Azure</option>
                <option value={CloudProvider.DIGITAL_OCEAN}>Digital Ocean</option>
                <option value={CloudProvider.HEROKU}>Heroku</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Região</label>
              <input
                type="text"
                value={config.region}
                onChange={(e) => handleConfigChange('region', e.target.value)}
                placeholder="us-east-1"
              />
            </div>

            <div className="form-group">
              <label>Tipo de Instância</label>
              <select
                value={config.instanceType}
                onChange={(e) => handleConfigChange('instanceType', e.target.value as InstanceType)}
              >
                <option value={InstanceType.MICRO}>Micro</option>
                <option value={InstanceType.SMALL}>Small</option>
                <option value={InstanceType.MEDIUM}>Medium</option>
                <option value={InstanceType.LARGE}>Large</option>
                <option value={InstanceType.XLARGE}>XLarge</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Tipo de Scaling</label>
              <select
                value={config.scalingType}
                onChange={(e) => handleConfigChange('scalingType', e.target.value as ScalingType)}
              >
                <option value={ScalingType.FIXED}>Fixo</option>
                <option value={ScalingType.AUTO}>Automático</option>
                <option value={ScalingType.MANUAL}>Manual</option>
              </select>
            </div>

            <div className="form-group">
              <label>Instâncias (Min/Max)</label>
              <div className="instance-range">
                <input
                  type="number"
                  min="1"
                  value={config.minInstances}
                  onChange={(e) => handleConfigChange('minInstances', parseInt(e.target.value))}
                  placeholder="Min"
                />
                <span>até</span>
                <input
                  type="number"
                  min="1"
                  value={config.maxInstances}
                  onChange={(e) => handleConfigChange('maxInstances', parseInt(e.target.value))}
                  placeholder="Max"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="config-section">
        <div className="config-section-header">
          <h3>
            <Globe size={18} />
            Configuração de Domínio
          </h3>
        </div>

        <div className="config-form">
          <div className="form-row">
            <div className="form-group">
              <label>Domínio Customizado</label>
              <input
                type="url"
                value={config.domain || ''}
                onChange={(e) => handleConfigChange('domain', e.target.value)}
                placeholder="app.meudominio.com"
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={config.ssl}
                  onChange={(e) => handleConfigChange('ssl', e.target.checked)}
                />
                Habilitar SSL/TLS
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="config-section">
        <div className="config-section-header">
          <h3>
            <Settings size={18} />
            Variáveis de Ambiente
          </h3>
        </div>

        <div className="env-vars-list">
          {Object.entries(config.environmentVariables).map(([key, value]) => (
            <div key={key} className="env-var-item">
              <div className="env-var-key">{key}</div>
              <div className="env-var-value">{value}</div>
              <button
                className="remove-btn"
                onClick={() => removeEnvironmentVariable(key)}
                title="Remover variável"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}

          <div className="add-env-var">
            <input
              type="text"
              placeholder="Nome da variável"
              value={newEnvVar.key}
              onChange={(e) => setNewEnvVar(prev => ({ ...prev, key: e.target.value }))}
            />
            <input
              type="text"
              placeholder="Valor"
              value={newEnvVar.value}
              onChange={(e) => setNewEnvVar(prev => ({ ...prev, value: e.target.value }))}
            />
            <button className="add-btn" onClick={addEnvironmentVariable}>
              <Plus size={16} />
              Adicionar
            </button>
          </div>
        </div>
      </div>

      <div className="config-section">
        <div className="config-section-header">
          <h3>
            <Lock size={18} />
            Secrets
          </h3>
        </div>

        <div className="secrets-list">
          {Object.entries(config.secrets).map(([key, value]) => (
            <div key={key} className="secret-item">
              <div className="secret-key">{key}</div>
              <div className="secret-value">
                {showSecrets[key] ? value : '••••••••'}
                <button
                  className="toggle-secret-btn"
                  onClick={() => toggleSecretVisibility(key)}
                  title={showSecrets[key] ? 'Ocultar' : 'Mostrar'}
                >
                  {showSecrets[key] ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
              <button
                className="remove-btn"
                onClick={() => removeSecret(key)}
                title="Remover secret"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}

          <div className="add-secret">
            <input
              type="text"
              placeholder="Nome do secret"
              value={newSecret.key}
              onChange={(e) => setNewSecret(prev => ({ ...prev, key: e.target.value }))}
            />
            <input
              type="password"
              placeholder="Valor"
              value={newSecret.value}
              onChange={(e) => setNewSecret(prev => ({ ...prev, value: e.target.value }))}
            />
            <button className="add-btn" onClick={addSecret}>
              <Plus size={16} />
              Adicionar
            </button>
          </div>
        </div>
      </div>

      <div className="config-section">
        <div className="config-section-header">
          <h3>Recursos Opcionais</h3>
        </div>

        <div className="config-form">
          <div className="form-row">
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={config.monitoring}
                  onChange={(e) => handleConfigChange('monitoring', e.target.checked)}
                />
                Habilitar Monitoramento
              </label>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={config.logging}
                  onChange={(e) => handleConfigChange('logging', e.target.checked)}
                />
                Habilitar Logging
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={config.backup}
                  onChange={(e) => handleConfigChange('backup', e.target.checked)}
                />
                Habilitar Backup
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="config-actions">
        <button className="btn btn-primary" onClick={handleSave}>
          <Save size={16} />
          Salvar Configuração
        </button>
      </div>
    </div>
  );
};