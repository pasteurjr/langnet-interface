// src/components/settings/AnalyticsPanel.tsx
import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Activity, 
  Download,
  Settings,
  Eye,
  EyeOff,
  Calendar,
  Database
} from 'lucide-react';
import { AnalyticsSettings, SystemMetrics } from '../../types/settings';
import './settings.css';

interface AnalyticsPanelProps {
  settings: AnalyticsSettings;
  metrics: SystemMetrics;
  onUpdate?: (updates: Partial<AnalyticsSettings>) => void;
}

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({
  settings,
  metrics,
  onUpdate
}) => {
  const [localSettings, setLocalSettings] = useState(settings);

  const handleSettingChange = (key: keyof AnalyticsSettings, value: any) => {
    const updatedSettings = { ...localSettings, [key]: value };
    setLocalSettings(updatedSettings);
    onUpdate?.(updatedSettings);
  };

  return (
    <div className="settings-section">
      <div className="section-header">
        <h3>Configurações de Analytics</h3>
      </div>

      <div className="settings-cards">
        <div className="settings-card">
          <div className="card-header">
            <BarChart3 className="w-5 h-5" />
            <h4>Coleta de Dados</h4>
          </div>
          <div className="card-content">
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localSettings.enabled}
                  onChange={(e) => handleSettingChange('enabled', e.target.checked)}
                />
                Habilitar analytics
              </label>
            </div>
            
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localSettings.collectUsageStats}
                  onChange={(e) => handleSettingChange('collectUsageStats', e.target.checked)}
                />
                Coletar estatísticas de uso
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localSettings.collectPerformanceMetrics}
                  onChange={(e) => handleSettingChange('collectPerformanceMetrics', e.target.checked)}
                />
                Coletar métricas de performance
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localSettings.collectErrorLogs}
                  onChange={(e) => handleSettingChange('collectErrorLogs', e.target.checked)}
                />
                Coletar logs de erro
              </label>
            </div>

            <div className="form-group">
              <label>Retenção de dados (dias)</label>
              <input
                type="number"
                min="7"
                max="365"
                value={localSettings.dataRetention}
                onChange={(e) => handleSettingChange('dataRetention', Number(e.target.value))}
              />
            </div>
          </div>
        </div>

        <div className="settings-card">
          <div className="card-header">
            <Database className="w-5 h-5" />
            <h4>Privacidade e Segurança</h4>
          </div>
          <div className="card-content">
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localSettings.anonymizeData}
                  onChange={(e) => handleSettingChange('anonymizeData', e.target.checked)}
                />
                Anonimizar dados pessoais
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localSettings.exportEnabled}
                  onChange={(e) => handleSettingChange('exportEnabled', e.target.checked)}
                />
                Permitir exportação de dados
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={localSettings.reportsEnabled}
                  onChange={(e) => handleSettingChange('reportsEnabled', e.target.checked)}
                />
                Habilitar relatórios automáticos
              </label>
            </div>
          </div>
        </div>

        <div className="settings-card">
          <div className="card-header">
            <Activity className="w-5 h-5" />
            <h4>Métricas Atuais</h4>
          </div>
          <div className="card-content">
            <div className="metrics-grid">
              <div className="metric-item">
                <Users className="w-4 h-4" />
                <span className="metric-value">{metrics.application.activeUsers}</span>
                <span className="metric-label">Usuários Ativos</span>
              </div>
              
              <div className="metric-item">
                <Activity className="w-4 h-4" />
                <span className="metric-value">{metrics.application.activeProjects}</span>
                <span className="metric-label">Projetos Ativos</span>
              </div>

              <div className="metric-item">
                <TrendingUp className="w-4 h-4" />
                <span className="metric-value">{metrics.application.requestsPerMinute}</span>
                <span className="metric-label">Req/min</span>
              </div>

              <div className="metric-item">
                <BarChart3 className="w-4 h-4" />
                <span className="metric-value">{metrics.application.averageResponseTime}ms</span>
                <span className="metric-label">Tempo Médio</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {localSettings.dashboardUrl && (
        <div className="settings-card">
          <div className="card-header">
            <Eye className="w-5 h-5" />
            <h4>Dashboard Externo</h4>
          </div>
          <div className="card-content">
            <div className="form-group">
              <label>URL do Dashboard</label>
              <input
                type="url"
                value={localSettings.dashboardUrl}
                onChange={(e) => handleSettingChange('dashboardUrl', e.target.value)}
                placeholder="https://analytics.example.com"
              />
            </div>
            <div className="form-actions">
              <button 
                className="btn btn-outline btn-sm"
                onClick={() => window.open(localSettings.dashboardUrl, '_blank')}
              >
                Abrir Dashboard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};