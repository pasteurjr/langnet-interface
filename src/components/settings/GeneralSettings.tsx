import React, { useState } from "react";
import { Save, Globe, Info, Server, Activity, Database } from "lucide-react";
import {
  SystemSettings,
  SystemMetrics,
  SystemHealth,
} from "../../types/settings";
import "./settings.css";

interface GeneralSettingsProps {
  settings: SystemSettings;
  metrics: SystemMetrics;
  health: SystemHealth;
  onUpdate: (settings: Partial<SystemSettings>) => void;
}

export const GeneralSettings: React.FC<GeneralSettingsProps> = ({
  settings,
  metrics,
  health,
  onUpdate,
}) => {
  const [formData, setFormData] = useState({
    projectName: settings.projectName,
    description: settings.description,
    domain: settings.domain,
    environment: settings.environment,
  });

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    onUpdate(formData);
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatUptime = (percentage: number) => {
    const days = Math.floor((percentage / 100) * 30);
    return `${percentage.toFixed(2)}% (${days} dias)`;
  };

  return (
    <div className="general-settings">
      <div className="settings-section">
        <div className="section-header">
          <h3>
            <Info size={18} />
            Informações do Sistema
          </h3>
        </div>

        <div className="settings-form">
          <div className="form-row">
            <div className="form-group">
              <label>Nome do Sistema</label>
              <input
                type="text"
                value={formData.projectName}
                onChange={(e) =>
                  handleInputChange("projectName", e.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label>Versão</label>
              <input
                type="text"
                value={settings.version}
                disabled
                className="readonly-field"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Descrição</label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange("description", e.target.value)}
              placeholder="Descrição do sistema"
              rows={3}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Domínio</label>
              <input
                type="url"
                value={formData.domain}
                onChange={(e) => handleInputChange("domain", e.target.value)}
                placeholder="https://example.com"
              />
            </div>

            <div className="form-group">
              <label>Ambiente</label>
              <select
                value={formData.environment}
                onChange={(e) =>
                  handleInputChange("environment", e.target.value)
                }
              >
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="production">Production</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Criado em</label>
              <input
                type="text"
                value={new Date(settings.createdAt).toLocaleDateString("pt-BR")}
                disabled
                className="readonly-field"
              />
            </div>

            <div className="form-group">
              <label>Última modificação</label>
              <input
                type="text"
                value={new Date(settings.modifiedAt).toLocaleDateString(
                  "pt-BR"
                )}
                disabled
                className="readonly-field"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Proprietário</label>
            <input
              type="text"
              value={settings.ownerName}
              disabled
              className="readonly-field"
            />
          </div>
        </div>
      </div>

      <div className="settings-section">
        <div className="section-header">
          <h3>
            <Server size={18} />
            Status do Servidor
          </h3>
        </div>

        <div className="server-metrics">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-header">
                <Activity size={16} />
                <span>Uptime</span>
              </div>
              <div className="metric-value">
                {formatUptime(metrics.server.uptime)}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <Server size={16} />
                <span>CPU</span>
              </div>
              <div className="metric-value">
                {metrics.server.cpu.toFixed(1)}%
              </div>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${metrics.server.cpu}%`,
                    backgroundColor:
                      metrics.server.cpu > 80 ? "#dc2626" : "#16a34a",
                  }}
                />
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <Database size={16} />
                <span>Memória</span>
              </div>
              <div className="metric-value">
                {metrics.server.memory.toFixed(1)}%
              </div>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${metrics.server.memory}%`,
                    backgroundColor:
                      metrics.server.memory > 80 ? "#dc2626" : "#16a34a",
                  }}
                />
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <Database size={16} />
                <span>Disco</span>
              </div>
              <div className="metric-value">
                {metrics.server.disk.toFixed(1)}%
              </div>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${metrics.server.disk}%`,
                    backgroundColor:
                      metrics.server.disk > 80 ? "#dc2626" : "#16a34a",
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-section">
        <div className="section-header">
          <h3>
            <Activity size={18} />
            Métricas da Aplicação
          </h3>
        </div>

        <div className="application-metrics">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">
                {metrics.application.activeUsers}
              </div>
              <div className="metric-label">Usuários Ativos</div>
            </div>

            <div className="metric-card">
              <div className="metric-value">
                {metrics.application.activeProjects}
              </div>
              <div className="metric-label">Projetos Ativos</div>
            </div>

            <div className="metric-card">
              <div className="metric-value">
                {metrics.application.requestsPerMinute}
              </div>
              <div className="metric-label">Requests/min</div>
            </div>

            <div className="metric-card">
              <div className="metric-value">
                {metrics.application.averageResponseTime}ms
              </div>
              <div className="metric-label">Tempo de Resposta</div>
            </div>

            <div className="metric-card">
              <div className="metric-value">
                {metrics.application.errorRate.toFixed(2)}%
              </div>
              <div className="metric-label">Taxa de Erro</div>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-section">
        <div className="section-header">
          <h3>
            <Database size={18} />
            Base de Dados
          </h3>
        </div>

        <div className="database-info">
          <div className="database-stats">
            <div className="stat-item">
              <span className="stat-label">Conexões Ativas:</span>
              <span className="stat-value">{metrics.database.connections}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Tempo Médio de Query:</span>
              <span className="stat-value">{metrics.database.queryTime}ms</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Tamanho da Base:</span>
              <span className="stat-value">
                {formatBytes(metrics.database.size * 1024 * 1024)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-section">
        <div className="section-header">
          <h3>
            <Globe size={18} />
            Tráfego de Rede
          </h3>
        </div>

        <div className="network-info">
          <div className="network-stats">
            <div className="network-stat">
              <span className="stat-label">Entrada:</span>
              <span className="stat-value">
                {formatBytes(metrics.server.network.bytesIn)}
              </span>
            </div>
            <div className="network-stat">
              <span className="stat-label">Saída:</span>
              <span className="stat-value">
                {formatBytes(metrics.server.network.bytesOut)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button className="btn btn-primary" onClick={handleSave}>
          <Save size={16} />
          Salvar Configurações
        </button>
      </div>
    </div>
  );
};
