// src/components/settings/BackupSettings.tsx
import React, { useState } from 'react';
import { 
  Database, 
  Download, 
  Upload, 
  Clock, 
  Shield,
  HardDrive,
  Cloud,
  AlertTriangle,
  CheckCircle,
  Play,
  Settings
} from 'lucide-react';
import { BackupConfiguration, BackupFrequency } from '../../types/settings';
import './settings.css';

interface BackupSettingsProps {
  configuration: BackupConfiguration;
  onUpdate?: (updates: Partial<BackupConfiguration>) => void;
}

export const BackupSettings: React.FC<BackupSettingsProps> = ({
  configuration,
  onUpdate
}) => {
  const [localConfig, setLocalConfig] = useState(configuration);
  const [isRunningBackup, setIsRunningBackup] = useState(false);

  const handleConfigChange = (key: keyof BackupConfiguration, value: any) => {
    const updatedConfig = { ...localConfig, [key]: value };
    setLocalConfig(updatedConfig);
    onUpdate?.(updatedConfig);
  };

  const runManualBackup = async () => {
    setIsRunningBackup(true);
    // Simular backup manual
    setTimeout(() => {
      setIsRunningBackup(false);
      handleConfigChange('lastBackup', new Date().toISOString());
    }, 3000);
  };

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'inactive': return <Clock className="w-4 h-4 text-gray-400" />;
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStorageProviderIcon = (provider: string) => {
    switch (provider) {
      case 'aws': return <Cloud className="w-4 h-4" />;
      case 'gcp': return <Cloud className="w-4 h-4" />;
      case 'azure': return <Cloud className="w-4 h-4" />;
      case 'local': return <HardDrive className="w-4 h-4" />;
      default: return <Database className="w-4 h-4" />;
    }
  };

  return (
    <div className="settings-section">
      <div className="section-header">
        <h3>Configurações de Backup</h3>
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={runManualBackup}
            disabled={isRunningBackup}
          >
            {isRunningBackup ? (
              <>
                <Settings className="w-4 h-4 animate-spin" />
                Executando...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Backup Manual
              </>
            )}
          </button>
        </div>
      </div>

      <div className="settings-cards">
        {/* Status do Backup */}
        <div className="settings-card">
          <div className="card-header">
            <Database className="w-5 h-5" />
            <h4>Status do Backup</h4>
          </div>
          <div className="card-content">
            <div className="status-grid">
              <div className="status-item">
                <span className="status-label">Status:</span>
                <div className="status-value">
                  {getStatusIcon(localConfig.status)}
                  <span className={`status-text ${localConfig.status}`}>
                    {localConfig.status === 'active' ? 'Ativo' : 
                     localConfig.status === 'inactive' ? 'Inativo' : 'Erro'}
                  </span>
                </div>
              </div>

              <div className="status-item">
                <span className="status-label">Último backup:</span>
                <span className="status-value">
                  {localConfig.lastBackup ? 
                    new Date(localConfig.lastBackup).toLocaleString() : 
                    'Nunca'
                  }
                </span>
              </div>

              <div className="status-item">
                <span className="status-label">Próximo backup:</span>
                <span className="status-value">
                  {localConfig.nextBackup ? 
                    new Date(localConfig.nextBackup).toLocaleString() : 
                    'N/A'
                  }
                </span>
              </div>

              <div className="status-item">
                <span className="status-label">Tamanho:</span>
                <span className="status-value">{formatBytes(localConfig.backupSize)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Configurações de Frequência */}
        <div className="settings-card">
          <div className="card-header">
            <Clock className="w-5 h-5" />
            <h4>Agendamento</h4>
          </div>
          <div className="card-content">
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localConfig.enabled}
                  onChange={(e) => handleConfigChange('enabled', e.target.checked)}
                />
                Habilitar backup automático
              </label>
            </div>

            <div className="form-group">
              <label>Frequência</label>
              <select
                value={localConfig.frequency}
                onChange={(e) => handleConfigChange('frequency', e.target.value as BackupFrequency)}
              >
                <option value={BackupFrequency.DAILY}>Diário</option>
                <option value={BackupFrequency.WEEKLY}>Semanal</option>
                <option value={BackupFrequency.MONTHLY}>Mensal</option>
              </select>
            </div>

            <div className="form-group">
              <label>Retenção (dias)</label>
              <input
                type="number"
                min="1"
                max="365"
                value={localConfig.retention}
                onChange={(e) => handleConfigChange('retention', Number(e.target.value))}
              />
            </div>
          </div>
        </div>

        {/* Conteúdo do Backup */}
        <div className="settings-card">
          <div className="card-header">
            <Upload className="w-5 h-5" />
            <h4>Conteúdo</h4>
          </div>
          <div className="card-content">
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localConfig.includeProjects}
                  onChange={(e) => handleConfigChange('includeProjects', e.target.checked)}
                />
                Incluir projetos
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localConfig.includeSettings}
                  onChange={(e) => handleConfigChange('includeSettings', e.target.checked)}
                />
                Incluir configurações do sistema
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localConfig.includeUsers}
                  onChange={(e) => handleConfigChange('includeUsers', e.target.checked)}
                />
                Incluir usuários e permissões
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localConfig.includeAnalytics}
                  onChange={(e) => handleConfigChange('includeAnalytics', e.target.checked)}
                />
                Incluir dados de analytics
              </label>
            </div>
          </div>
        </div>

        {/* Armazenamento */}
        <div className="settings-card">
          <div className="card-header">
            <HardDrive className="w-5 h-5" />
            <h4>Armazenamento</h4>
          </div>
          <div className="card-content">
            <div className="form-group">
              <label>Provedor de armazenamento</label>
              <select
                value={localConfig.storageProvider}
                onChange={(e) => handleConfigChange('storageProvider', e.target.value)}
              >
                <option value="local">Local</option>
                <option value="aws">Amazon S3</option>
                <option value="gcp">Google Cloud Storage</option>
                <option value="azure">Azure Blob Storage</option>
              </select>
            </div>

            {localConfig.storageProvider !== 'local' && (
              <div className="storage-config">
                <div className="form-group">
                  <label>Configurações do provedor</label>
                  <textarea
                    value={JSON.stringify(localConfig.storageConfig, null, 2)}
                    onChange={(e) => {
                      try {
                        const config = JSON.parse(e.target.value);
                        handleConfigChange('storageConfig', config);
                      } catch (error) {
                        // Invalid JSON, ignore
                      }
                    }}
                    rows={4}
                    placeholder="Configurações em JSON"
                  />
                </div>
              </div>
            )}

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localConfig.encryptionEnabled}
                  onChange={(e) => handleConfigChange('encryptionEnabled', e.target.checked)}
                />
                <Shield className="w-4 h-4" />
                Criptografar backups
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Ações de Backup */}
      <div className="backup-actions">
        <button className="btn btn-outline">
          <Download className="w-4 h-4" />
          Baixar Último Backup
        </button>
        <button className="btn btn-outline">
          <Upload className="w-4 h-4" />
          Restaurar Backup
        </button>
      </div>
    </div>
  );
};