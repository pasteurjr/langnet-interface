// src/components/settings/SecuritySettings.tsx
import React, { useState } from 'react';
import { 
  Shield, 
  Lock, 
  Key, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Users, 
  FileText, 
  Eye, 
  EyeOff,
  Download,
  Upload,
  Trash2,
  Plus,
  Settings,
  Globe,
  Database
} from 'lucide-react';
import { AuditLog, BackupConfiguration, BackupFrequency } from '../../types/settings';
import './settings.css';

// Tipos locais que não existem no settings.ts
interface SecurityConfig {
  twoFactorRequired: boolean;
  sessionTimeout: number; // horas
  auditLogging: boolean;
  passwordPolicy: PasswordPolicy;
  rateLimiting: {
    enabled: boolean;
    requestsPerHour: number;
  };
}

interface PasswordPolicy {
  minLength: number;
  requireSpecialChars: boolean;
  requireNumbers: boolean;
  requireUppercase: boolean;
  expirationDays: number;
}

interface SecuritySettingsProps {
  securityConfig: SecurityConfig;
  auditLogs: AuditLog[];
  backupConfig: BackupConfiguration;
  onUpdateSecurity: (updates: Partial<SecurityConfig>) => void;
  onUpdateBackup: (updates: Partial<BackupConfiguration>) => void;
  onDownloadLogs: () => void;
  onClearLogs: () => void;
}

const SecuritySettings: React.FC<SecuritySettingsProps> = ({
  securityConfig,
  auditLogs,
  backupConfig,
  onUpdateSecurity,
  onUpdateBackup,
  onDownloadLogs,
  onClearLogs
}) => {
  const [activeTab, setActiveTab] = useState<'auth' | 'audit' | 'backup' | 'policies'>('auth');
  const [showPasswordPolicy, setShowPasswordPolicy] = useState(false);

  const toggleTwoFactor = () => {
    onUpdateSecurity({
      twoFactorRequired: !securityConfig.twoFactorRequired
    });
  };

  const toggleAuditLogging = () => {
    onUpdateSecurity({
      auditLogging: !securityConfig.auditLogging
    });
  };

  const updateSessionTimeout = (timeout: number) => {
    onUpdateSecurity({
      sessionTimeout: timeout
    });
  };

  const updatePasswordPolicy = (policy: Partial<PasswordPolicy>) => {
    onUpdateSecurity({
      passwordPolicy: {
        ...securityConfig.passwordPolicy,
        ...policy
      }
    });
  };

  const getSecurityScore = () => {
    let score = 0;
    if (securityConfig.twoFactorRequired) score += 20;
    if (securityConfig.auditLogging) score += 15;
    if (securityConfig.sessionTimeout <= 4) score += 10;
    if (securityConfig.passwordPolicy.minLength >= 12) score += 15;
    if (securityConfig.passwordPolicy.requireSpecialChars) score += 10;
    if (securityConfig.passwordPolicy.requireNumbers) score += 10;
    if (securityConfig.passwordPolicy.requireUppercase) score += 10;
    if (securityConfig.rateLimiting.enabled) score += 10;
    return Math.min(score, 100);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'good';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  const formatLogAction = (action: string) => {
    switch (action.toLowerCase()) {
      case 'login': return 'Login';
      case 'logout': return 'Logout';
      case 'password_change': return 'Alteração de Senha';
      case 'permission_change': return 'Alteração de Permissão';
      case 'data_access': return 'Acesso a Dados';
      case 'system_change': return 'Alteração do Sistema';
      default: return action;
    }
  };

  const getLogIcon = (action: string) => {
    switch (action.toLowerCase()) {
      case 'login':
      case 'logout':
        return <Users className="w-4 h-4" />;
      case 'password_change':
        return <Key className="w-4 h-4" />;
      case 'permission_change':
        return <Shield className="w-4 h-4" />;
      case 'data_access':
        return <Database className="w-4 h-4" />;
      case 'system_change':
        return <Settings className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="settings-section">
      <div className="section-header">
        <h3>Segurança e Auditoria</h3>
        <div className="security-score">
          <div className={`score-circle ${getScoreColor(getSecurityScore())}`}>
            <span className="score-value">{getSecurityScore()}</span>
            <span className="score-label">Score</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'auth' ? 'active' : ''}`}
          onClick={() => setActiveTab('auth')}
        >
          <Lock className="w-4 h-4" />
          Autenticação
        </button>
        <button 
          className={`tab ${activeTab === 'policies' ? 'active' : ''}`}
          onClick={() => setActiveTab('policies')}
        >
          <Shield className="w-4 h-4" />
          Políticas
        </button>
        <button 
          className={`tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <FileText className="w-4 h-4" />
          Auditoria ({auditLogs.length})
        </button>
        <button 
          className={`tab ${activeTab === 'backup' ? 'active' : ''}`}
          onClick={() => setActiveTab('backup')}
        >
          <Database className="w-4 h-4" />
          Backup
        </button>
      </div>

      {activeTab === 'auth' && (
        <div className="auth-section">
          <div className="security-cards">
            <div className="security-card">
              <div className="card-header">
                <Key className="w-5 h-5" />
                <h4>Autenticação de Dois Fatores</h4>
              </div>
              <div className="card-content">
                <p>Requer verificação adicional para todos os usuários</p>
                <div className="toggle-switch">
                  <input
                    type="checkbox"
                    id="two-factor"
                    checked={securityConfig.twoFactorRequired}
                    onChange={toggleTwoFactor}
                  />
                  <label htmlFor="two-factor">
                    {securityConfig.twoFactorRequired ? 'Habilitado' : 'Desabilitado'}
                  </label>
                </div>
              </div>
            </div>

            <div className="security-card">
              <div className="card-header">
                <Clock className="w-5 h-5" />
                <h4>Timeout de Sessão</h4>
              </div>
              <div className="card-content">
                <p>Tempo limite para sessões inativas</p>
                <div className="form-group">
                  <select
                    value={securityConfig.sessionTimeout}
                    onChange={(e) => updateSessionTimeout(Number(e.target.value))}
                  >
                    <option value={1}>1 hora</option>
                    <option value={2}>2 horas</option>
                    <option value={4}>4 horas</option>
                    <option value={8}>8 horas</option>
                    <option value={24}>24 horas</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="security-card">
              <div className="card-header">
                <Globe className="w-5 h-5" />
                <h4>Rate Limiting</h4>
              </div>
              <div className="card-content">
                <p>Limite de requisições por usuário</p>
                <div className="rate-limit-config">
                  <div className="toggle-switch">
                    <input
                      type="checkbox"
                      id="rate-limiting"
                      checked={securityConfig.rateLimiting.enabled}
                      onChange={(e) => onUpdateSecurity({
                        rateLimiting: {
                          ...securityConfig.rateLimiting,
                          enabled: e.target.checked
                        }
                      })}
                    />
                    <label htmlFor="rate-limiting">
                      {securityConfig.rateLimiting.enabled ? 'Habilitado' : 'Desabilitado'}
                    </label>
                  </div>
                  {securityConfig.rateLimiting.enabled && (
                    <div className="rate-inputs">
                      <div className="form-group">
                        <label>Requisições por hora:</label>
                        <input
                          type="number"
                          value={securityConfig.rateLimiting.requestsPerHour}
                          onChange={(e) => onUpdateSecurity({
                            rateLimiting: {
                              ...securityConfig.rateLimiting,
                              requestsPerHour: Number(e.target.value)
                            }
                          })}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="security-card">
              <div className="card-header">
                <FileText className="w-5 h-5" />
                <h4>Log de Auditoria</h4>
              </div>
              <div className="card-content">
                <p>Registrar todas as ações do sistema</p>
                <div className="toggle-switch">
                  <input
                    type="checkbox"
                    id="audit-logging"
                    checked={securityConfig.auditLogging}
                    onChange={toggleAuditLogging}
                  />
                  <label htmlFor="audit-logging">
                    {securityConfig.auditLogging ? 'Habilitado' : 'Desabilitado'}
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'policies' && (
        <div className="policies-section">
          <div className="policy-card">
            <div className="card-header">
              <Lock className="w-5 h-5" />
              <h4>Política de Senhas</h4>
              <button 
                className="btn btn-sm btn-outline"
                onClick={() => setShowPasswordPolicy(!showPasswordPolicy)}
              >
                {showPasswordPolicy ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                {showPasswordPolicy ? 'Ocultar' : 'Editar'}
              </button>
            </div>

            <div className="policy-summary">
              <div className="policy-item">
                <span>Comprimento mínimo:</span>
                <span>{securityConfig.passwordPolicy.minLength} caracteres</span>
              </div>
              <div className="policy-item">
                <span>Caracteres especiais:</span>
                <span>{securityConfig.passwordPolicy.requireSpecialChars ? 'Obrigatório' : 'Opcional'}</span>
              </div>
              <div className="policy-item">
                <span>Números:</span>
                <span>{securityConfig.passwordPolicy.requireNumbers ? 'Obrigatório' : 'Opcional'}</span>
              </div>
              <div className="policy-item">
                <span>Maiúsculas:</span>
                <span>{securityConfig.passwordPolicy.requireUppercase ? 'Obrigatório' : 'Opcional'}</span>
              </div>
              <div className="policy-item">
                <span>Expiração:</span>
                <span>{securityConfig.passwordPolicy.expirationDays} dias</span>
              </div>
            </div>

            {showPasswordPolicy && (
              <div className="policy-editor">
                <div className="form-group">
                  <label>Comprimento mínimo</label>
                  <input
                    type="number"
                    min="6"
                    max="32"
                    value={securityConfig.passwordPolicy.minLength}
                    onChange={(e) => updatePasswordPolicy({ minLength: Number(e.target.value) })}
                  />
                </div>

                <div className="form-group">
                  <label>Expiração (dias)</label>
                  <input
                    type="number"
                    min="30"
                    max="365"
                    value={securityConfig.passwordPolicy.expirationDays}
                    onChange={(e) => updatePasswordPolicy({ expirationDays: Number(e.target.value) })}
                  />
                </div>

                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={securityConfig.passwordPolicy.requireSpecialChars}
                      onChange={(e) => updatePasswordPolicy({ requireSpecialChars: e.target.checked })}
                    />
                    Exigir caracteres especiais (!@#$%)
                  </label>
                </div>

                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={securityConfig.passwordPolicy.requireNumbers}
                      onChange={(e) => updatePasswordPolicy({ requireNumbers: e.target.checked })}
                    />
                    Exigir números (0-9)
                  </label>
                </div>

                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={securityConfig.passwordPolicy.requireUppercase}
                      onChange={(e) => updatePasswordPolicy({ requireUppercase: e.target.checked })}
                    />
                    Exigir letras maiúsculas (A-Z)
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="audit-section">
          <div className="audit-controls">
            <div className="controls-left">
              <span className="logs-count">{auditLogs.length} registros de auditoria</span>
            </div>
            <div className="controls-right">
              <button className="btn btn-outline btn-sm" onClick={onDownloadLogs}>
                <Download className="w-3 h-3" />
                Exportar
              </button>
              <button className="btn btn-danger btn-sm" onClick={onClearLogs}>
                <Trash2 className="w-3 h-3" />
                Limpar
              </button>
            </div>
          </div>

          <div className="audit-logs">
            <div className="logs-table">
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Ação</th>
                    <th>Usuário</th>
                    <th>Recurso</th>
                    <th>IP</th>
                    <th>Severidade</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.slice(0, 50).map(log => (
                    <tr key={log.id}>
                      <td>
                        <div className="timestamp">
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </td>
                      <td>
                        <div className="log-type">
                          {getLogIcon(log.action)}
                          {formatLogAction(log.action)}
                        </div>
                      </td>
                      <td>{log.userName}</td>
                      <td>{log.resource}</td>
                      <td>
                        <code className="ip-address">{log.ipAddress}</code>
                      </td>
                      <td>
                        <span className={`severity-badge ${log.severity}`}>
                          {log.severity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'backup' && (
        <div className="backup-section">
          <div className="backup-cards">
            <div className="backup-card">
              <div className="card-header">
                <Database className="w-5 h-5" />
                <h4>Configuração de Backup</h4>
              </div>
              <div className="card-content">
                <div className="form-group">
                  <label>Frequência de backup</label>
                  <select
                    value={backupConfig.frequency}
                    onChange={(e) => onUpdateBackup({ 
                      frequency: e.target.value as BackupFrequency
                    })}
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
                    min="7"
                    max="365"
                    value={backupConfig.retention}
                    onChange={(e) => onUpdateBackup({ retention: Number(e.target.value) })}
                  />
                </div>

                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={backupConfig.enabled}
                      onChange={(e) => onUpdateBackup({ enabled: e.target.checked })}
                    />
                    Habilitar backup automático
                  </label>
                </div>

                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={backupConfig.encryptionEnabled}
                      onChange={(e) => onUpdateBackup({ encryptionEnabled: e.target.checked })}
                    />
                    Criptografar backups
                  </label>
                </div>
              </div>
            </div>

            <div className="backup-card">
              <div className="card-header">
                <Clock className="w-5 h-5" />
                <h4>Status do Backup</h4>
              </div>
              <div className="card-content">
                <div className="backup-status">
                  <div className="status-item">
                    <span className="status-label">Último backup:</span>
                    <span className="status-value">
                      {backupConfig.lastBackup ? 
                        new Date(backupConfig.lastBackup).toLocaleString() : 
                        'Nunca'
                      }
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Próximo backup:</span>
                    <span className="status-value">
                      {backupConfig.nextBackup ? 
                        new Date(backupConfig.nextBackup).toLocaleString() : 
                        'N/A'
                      }
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Tamanho total:</span>
                    <span className="status-value">
                      {backupConfig.backupSize ? 
                        `${(backupConfig.backupSize / 1024 / 1024).toFixed(2)} MB` : 
                        'Calculando...'
                      }
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Status:</span>
                    <span className={`status-badge ${backupConfig.status}`}>
                      {backupConfig.status === 'active' ? 'Ativo' : 
                       backupConfig.status === 'inactive' ? 'Inativo' : 'Erro'}
                    </span>
                  </div>
                </div>

                <div className="backup-actions">
                  <button className="btn btn-primary btn-sm">
                    <Upload className="w-3 h-3" />
                    Backup Manual
                  </button>
                  <button className="btn btn-outline btn-sm">
                    <Download className="w-3 h-3" />
                    Baixar Último
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecuritySettings;