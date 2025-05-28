import React, { useState } from 'react';
import { Shield, Lock, Key, AlertTriangle, CheckCircle, Eye, EyeOff, Plus, Trash2 } from 'lucide-react';
import { DeploymentEnvironment } from '../../types/deployment';
import './deployment.css';

interface SecurityPanelProps {
  environment: DeploymentEnvironment;
  onUpdate: (config: Partial<DeploymentEnvironment>) => void;
}

export const SecurityPanel: React.FC<SecurityPanelProps> = ({
  environment,
  onUpdate
}) => {
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [newFirewallRule, setNewFirewallRule] = useState({
    name: '',
    protocol: 'tcp' as 'tcp' | 'udp' | 'icmp',
    port: '',
    source: '',
    action: 'allow' as 'allow' | 'deny'
  });
  const [newWhitelistIp, setNewWhitelistIp] = useState('');

  const toggleSecretVisibility = (key: string) => {
    setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const addFirewallRule = () => {
    if (newFirewallRule.name && newFirewallRule.port && newFirewallRule.source) {
      const rule = {
        id: `rule_${Date.now()}`,
        ...newFirewallRule,
        port: newFirewallRule.port.includes('-') ? newFirewallRule.port : parseInt(newFirewallRule.port)
      };
      
      const updatedSecurity = {
        ...environment.security,
        firewall: {
          ...environment.security.firewall,
          rules: [...environment.security.firewall.rules, rule]
        }
      };
      
      onUpdate({ security: updatedSecurity });
      setNewFirewallRule({
        name: '',
        protocol: 'tcp',
        port: '',
        source: '',
        action: 'allow'
      });
    }
  };

  const removeFirewallRule = (ruleId: string) => {
    const updatedSecurity = {
      ...environment.security,
      firewall: {
        ...environment.security.firewall,
        rules: environment.security.firewall.rules.filter(rule => rule.id !== ruleId)
      }
    };
    onUpdate({ security: updatedSecurity });
  };

  const addWhitelistIp = () => {
    if (newWhitelistIp) {
      const updatedSecurity = {
        ...environment.security,
        accessControl: {
          ...environment.security.accessControl,
          whitelist: [...environment.security.accessControl.whitelist, newWhitelistIp]
        }
      };
      onUpdate({ security: updatedSecurity });
      setNewWhitelistIp('');
    }
  };

  const removeWhitelistIp = (ip: string) => {
    const updatedSecurity = {
      ...environment.security,
      accessControl: {
        ...environment.security.accessControl,
        whitelist: environment.security.accessControl.whitelist.filter(item => item !== ip)
      }
    };
    onUpdate({ security: updatedSecurity });
  };

  const updateFirewallStatus = (enabled: boolean) => {
    const updatedSecurity = {
      ...environment.security,
      firewall: {
        ...environment.security.firewall,
        enabled
      }
    };
    onUpdate({ security: updatedSecurity });
  };

  const updateSslStatus = (enabled: boolean) => {
    const updatedSecurity = {
      ...environment.security,
      ssl: {
        ...environment.security.ssl,
        enabled
      }
    };
    onUpdate({ security: updatedSecurity });
  };

  const updateAccessControl = (field: string, value: any) => {
    const updatedSecurity = {
      ...environment.security,
      accessControl: {
        ...environment.security.accessControl,
        [field]: value
      }
    };
    onUpdate({ security: updatedSecurity });
  };

  const getSecurityScore = () => {
    let score = 0;
    if (environment.security.firewall.enabled) score += 25;
    if (environment.security.ssl.enabled) score += 25;
    if (environment.security.accessControl.enabled) score += 25;
    if (environment.security.secrets.encrypted) score += 25;
    return score;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#16a34a';
    if (score >= 60) return '#f59e0b';
    return '#dc2626';
  };

  const securityScore = getSecurityScore();

  return (
    <div className="security-panel">
      <div className="security-overview">
        <div className="security-score-card">
          <div className="score-header">
            <Shield size={24} />
            <h3>Security Score</h3>
          </div>
          <div className="score-display">
            <div 
              className="score-value"
              style={{ color: getScoreColor(securityScore) }}
            >
              {securityScore}%
            </div>
            <div className="score-bar">
              <div 
                className="score-fill"
                style={{ 
                  width: `${securityScore}%`,
                  backgroundColor: getScoreColor(securityScore)
                }}
              />
            </div>
          </div>
          <div className="score-description">
            {securityScore >= 80 && 'Excelente segurança'}
            {securityScore >= 60 && securityScore < 80 && 'Boa segurança'}
            {securityScore < 60 && 'Necessita melhorias'}
          </div>
        </div>

        <div className="security-checklist">
          <h4>Status de Segurança</h4>
          <div className="checklist-items">
            <div className={`checklist-item ${environment.security.firewall.enabled ? 'enabled' : 'disabled'}`}>
              {environment.security.firewall.enabled ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
              <span>Firewall Configurado</span>
            </div>
            <div className={`checklist-item ${environment.security.ssl.enabled ? 'enabled' : 'disabled'}`}>
              {environment.security.ssl.enabled ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
              <span>SSL/TLS Habilitado</span>
            </div>
            <div className={`checklist-item ${environment.security.accessControl.enabled ? 'enabled' : 'disabled'}`}>
              {environment.security.accessControl.enabled ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
              <span>Controle de Acesso</span>
            </div>
            <div className={`checklist-item ${environment.security.secrets.encrypted ? 'enabled' : 'disabled'}`}>
              {environment.security.secrets.encrypted ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
              <span>Secrets Criptografados</span>
            </div>
          </div>
        </div>
      </div>

      <div className="security-section">
        <div className="section-header">
          <h3>
            <Shield size={18} />
            Firewall
          </h3>
          <div className="section-toggle">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={environment.security.firewall.enabled}
                onChange={(e) => updateFirewallStatus(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        {environment.security.firewall.enabled && (
          <div className="firewall-config">
            <div className="firewall-rules">
              <h4>Regras do Firewall</h4>
              <div className="rules-list">
                {environment.security.firewall.rules.map(rule => (
                  <div key={rule.id} className="rule-item">
                    <div className="rule-info">
                      <div className="rule-name">{rule.name}</div>
                      <div className="rule-details">
                        {rule.protocol.toUpperCase()}:{rule.port} from {rule.source} - {rule.action.toUpperCase()}
                      </div>
                    </div>
                    <button
                      className="remove-rule-btn"
                      onClick={() => removeFirewallRule(rule.id)}
                      title="Remover regra"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}

                <div className="add-rule-form">
                  <div className="form-row">
                    <input
                      type="text"
                      placeholder="Nome da regra"
                      value={newFirewallRule.name}
                      onChange={(e) => setNewFirewallRule(prev => ({ ...prev, name: e.target.value }))}
                    />
                    <select
                      value={newFirewallRule.protocol}
                      onChange={(e) => setNewFirewallRule(prev => ({ ...prev, protocol: e.target.value as any }))}
                    >
                      <option value="tcp">TCP</option>
                      <option value="udp">UDP</option>
                      <option value="icmp">ICMP</option>
                    </select>
                  </div>
                  <div className="form-row">
                    <input
                      type="text"
                      placeholder="Porta (ex: 80, 443, 8000-9000)"
                      value={newFirewallRule.port}
                      onChange={(e) => setNewFirewallRule(prev => ({ ...prev, port: e.target.value }))}
                    />
                    <input
                      type="text"
                      placeholder="Origem (IP ou CIDR)"
                      value={newFirewallRule.source}
                      onChange={(e) => setNewFirewallRule(prev => ({ ...prev, source: e.target.value }))}
                    />
                  </div>
                  <div className="form-row">
                    <select
                      value={newFirewallRule.action}
                      onChange={(e) => setNewFirewallRule(prev => ({ ...prev, action: e.target.value as any }))}
                    >
                      <option value="allow">Permitir</option>
                      <option value="deny">Negar</option>
                    </select>
                    <button className="add-btn" onClick={addFirewallRule}>
                      <Plus size={16} />
                      Adicionar Regra
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="security-section">
        <div className="section-header">
          <h3>
            <Lock size={18} />
            SSL/TLS
          </h3>
          <div className="section-toggle">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={environment.security.ssl.enabled}
                onChange={(e) => updateSslStatus(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        {environment.security.ssl.enabled && (
          <div className="ssl-config">
            <div className="ssl-info">
              <div className="ssl-status">
                <CheckCircle size={16} color="#16a34a" />
                <span>Certificado SSL ativo</span>
              </div>
              <div className="ssl-details">
                <div className="ssl-item">
                  <span className="ssl-label">Auto-renovação:</span>
                  <span className={`ssl-value ${environment.security.ssl.autoRenewal ? 'enabled' : 'disabled'}`}>
                    {environment.security.ssl.autoRenewal ? 'Habilitada' : 'Desabilitada'}
                  </span>
                </div>
                {environment.security.ssl.certificate && (
                  <div className="ssl-item">
                    <span className="ssl-label">Certificado:</span>
                    <span className="ssl-value">{environment.security.ssl.certificate}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="security-section">
        <div className="section-header">
          <h3>
            <Key size={18} />
            Controle de Acesso
          </h3>
          <div className="section-toggle">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={environment.security.accessControl.enabled}
                onChange={(e) => updateAccessControl('enabled', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        {environment.security.accessControl.enabled && (
          <div className="access-control-config">
            <div className="auth-methods">
              <h4>Métodos de Autenticação</h4>
              <div className="auth-options">
                <label className="auth-option">
                  <input
                    type="checkbox"
                    checked={environment.security.accessControl.basicAuth}
                    onChange={(e) => updateAccessControl('basicAuth', e.target.checked)}
                  />
                  Basic Authentication
                </label>
                <label className="auth-option">
                  <input
                    type="checkbox"
                    checked={environment.security.accessControl.oauth}
                    onChange={(e) => updateAccessControl('oauth', e.target.checked)}
                  />
                  OAuth 2.0
                </label>
              </div>
            </div>

            <div className="ip-whitelist">
              <h4>Whitelist de IPs</h4>
              <div className="whitelist-items">
                {environment.security.accessControl.whitelist.map(ip => (
                  <div key={ip} className="whitelist-item">
                    <span className="ip-address">{ip}</span>
                    <button
                      className="remove-ip-btn"
                      onClick={() => removeWhitelistIp(ip)}
                      title="Remover IP"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}

                <div className="add-ip-form">
                  <input
                    type="text"
                    placeholder="Endereço IP ou CIDR"
                    value={newWhitelistIp}
                    onChange={(e) => setNewWhitelistIp(e.target.value)}
                  />
                  <button className="add-btn" onClick={addWhitelistIp}>
                    <Plus size={16} />
                    Adicionar IP
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="security-section">
        <div className="section-header">
          <h3>
            <Lock size={18} />
            Gerenciamento de Secrets
          </h3>
        </div>

        <div className="secrets-config">
          <div className="secrets-info">
            <div className="secrets-status">
              <div className="status-item">
                <span className="status-label">Criptografia:</span>
                <span className={`status-value ${environment.security.secrets.encrypted ? 'enabled' : 'disabled'}`}>
                  {environment.security.secrets.encrypted ? 'Habilitada' : 'Desabilitada'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Vault:</span>
                <span className="status-value">{environment.security.secrets.vault}</span>
              </div>
              <div className="status-item">
                <span className="status-label">Rotação:</span>
                <span className={`status-value ${environment.security.secrets.rotationEnabled ? 'enabled' : 'disabled'}`}>
                  {environment.security.secrets.rotationEnabled ? 'Habilitada' : 'Desabilitada'}
                </span>
              </div>
            </div>

            <div className="secrets-list">
              <h4>Secrets Configurados</h4>
              {Object.entries(environment.config.secrets).map(([key, value]) => (
                <div key={key} className="secret-item">
                  <div className="secret-key">{key}</div>
                  <div className="secret-value">
                    {showSecrets[key] ? value : '••••••••••••••••'}
                    <button
                      className="toggle-secret-btn"
                      onClick={() => toggleSecretVisibility(key)}
                      title={showSecrets[key] ? 'Ocultar' : 'Mostrar'}
                    >
                      {showSecrets[key] ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  </div>
                  <div className="secret-status">
                    <Lock size={12} />
                    Criptografado
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="security-actions">
        <button className="btn btn-primary">
          Aplicar Configurações
        </button>
        <button className="btn btn-secondary">
          Executar Scan de Segurança
        </button>
        <button className="btn btn-secondary">
          Gerar Relatório
        </button>
      </div>
    </div>
  );
};