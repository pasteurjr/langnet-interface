import React from 'react';
import { Database, Cpu, HardDrive, Wifi, Users, Clock, Activity, AlertCircle } from 'lucide-react';
import { SystemMetrics, LangfuseConnection, MonitoringStatus } from '../../types/monitoring';
import './monitoring.css';
interface SystemOverviewProps {
  systemMetrics: SystemMetrics;
  connection: LangfuseConnection;
}

export const SystemOverview: React.FC<SystemOverviewProps> = ({
  systemMetrics,
  connection
}) => {
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getConnectionStatusColor = (status: MonitoringStatus) => {
    switch (status) {
      case MonitoringStatus.CONNECTED: return '#16a34a';
      case MonitoringStatus.CONNECTING: return '#f59e0b';
      case MonitoringStatus.DISCONNECTED: return '#dc2626';
      case MonitoringStatus.ERROR: return '#dc2626';
      case MonitoringStatus.SYNCING: return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getConnectionStatusText = (status: MonitoringStatus) => {
    switch (status) {
      case MonitoringStatus.CONNECTED: return 'Conectado';
      case MonitoringStatus.CONNECTING: return 'Conectando';
      case MonitoringStatus.DISCONNECTED: return 'Desconectado';
      case MonitoringStatus.ERROR: return 'Erro';
      case MonitoringStatus.SYNCING: return 'Sincronizando';
      default: return 'Desconhecido';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getMetricColor = (value: number, type: 'cpu' | 'memory' | 'disk') => {
    if (type === 'disk') {
      // Disk usage - green is good for low usage
      if (value < 50) return '#16a34a';
      if (value < 80) return '#f59e0b';
      return '#dc2626';
    } else {
      // CPU and Memory - moderate usage is optimal
      if (value < 30) return '#16a34a';
      if (value < 70) return '#f59e0b';
      return '#dc2626';
    }
  };

  return (
    <div className="system-overview">
      <div className="connection-status-section">
        <h5>Conexão Langfuse</h5>
        <div className={`connection-status ${connection.status}`}>
          <div className="connection-info">
            <div className="connection-details">
              <div className="connection-host">
                <Database size={16} />
                {new URL(connection.host).hostname}
              </div>
              <div className="connection-last-sync">
                Última sync: {formatDate(connection.lastSync)}
              </div>
            </div>
            <div 
              className="connection-badge"
              style={{ 
                backgroundColor: getConnectionStatusColor(connection.status) + '20',
                color: getConnectionStatusColor(connection.status)
              }}
            >
              {getConnectionStatusText(connection.status)}
            </div>
          </div>
        </div>

        <div className="connection-settings">
          <div className="setting-item">
            <span>Tracing:</span>
            <span className={connection.settings.enableTracing ? 'enabled' : 'disabled'}>
              {connection.settings.enableTracing ? 'Ativo' : 'Inativo'}
            </span>
          </div>
          <div className="setting-item">
            <span>Taxa de Amostragem:</span>
            <span>{(connection.settings.sampleRate * 100).toFixed(0)}%</span>
          </div>
          <div className="setting-item">
            <span>Buffer:</span>
            <span>{connection.settings.bufferSize.toLocaleString()} eventos</span>
          </div>
        </div>
      </div>

      <div className="system-metrics-section">
        <h5>Métricas do Sistema</h5>
        <div className="system-metrics-grid">
          <div className="system-metric">
            <div className="metric-header">
              <Cpu size={16} color={getMetricColor(systemMetrics.cpu, 'cpu')} />
              <span>CPU</span>
            </div>
            <div 
              className="system-metric-value"
              style={{ color: getMetricColor(systemMetrics.cpu, 'cpu') }}
            >
              {formatPercentage(systemMetrics.cpu)}
            </div>
            <div className="metric-bar">
              <div 
                className="metric-fill"
                style={{ 
                  width: `${systemMetrics.cpu}%`,
                  backgroundColor: getMetricColor(systemMetrics.cpu, 'cpu')
                }}
              />
            </div>
          </div>

          <div className="system-metric">
            <div className="metric-header">
              <HardDrive size={16} color={getMetricColor(systemMetrics.memory, 'memory')} />
              <span>Memória</span>
            </div>
            <div 
              className="system-metric-value"
              style={{ color: getMetricColor(systemMetrics.memory, 'memory') }}
            >
              {formatPercentage(systemMetrics.memory)}
            </div>
            <div className="metric-bar">
              <div 
                className="metric-fill"
                style={{ 
                  width: `${systemMetrics.memory}%`,
                  backgroundColor: getMetricColor(systemMetrics.memory, 'memory')
                }}
              />
            </div>
          </div>

          <div className="system-metric">
            <div className="metric-header">
              <Database size={16} color={getMetricColor(systemMetrics.disk, 'disk')} />
              <span>Disco</span>
            </div>
            <div 
              className="system-metric-value"
              style={{ color: getMetricColor(systemMetrics.disk, 'disk') }}
            >
              {formatPercentage(systemMetrics.disk)}
            </div>
            <div className="metric-bar">
              <div 
                className="metric-fill"
                style={{ 
                  width: `${systemMetrics.disk}%`,
                  backgroundColor: getMetricColor(systemMetrics.disk, 'disk')
                }}
              />
            </div>
          </div>

          <div className="system-metric">
            <div className="metric-header">
              <Wifi size={16} color="#3b82f6" />
              <span>Rede</span>
            </div>
            <div className="system-metric-value network-metric">
              <div className="network-stat">
                ↓ {formatBytes(systemMetrics.network.bytesIn)}
              </div>
              <div className="network-stat">
                ↑ {formatBytes(systemMetrics.network.bytesOut)}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="activity-metrics-section">
        <h5>Atividade do Sistema</h5>
        <div className="activity-metrics-grid">
          <div className="activity-metric">
            <div className="activity-icon">
              <Users size={16} color="#4a90e2" />
            </div>
            <div className="activity-content">
              <div className="activity-value">{systemMetrics.activeAgents}</div>
              <div className="activity-label">Agentes Ativos</div>
            </div>
          </div>

          <div className="activity-metric">
            <div className="activity-icon">
              <Activity size={16} color="#f59e0b" />
            </div>
            <div className="activity-content">
              <div className="activity-value">{systemMetrics.queueDepth}</div>
              <div className="activity-label">Fila de Processos</div>
            </div>
          </div>

          <div className="activity-metric">
            <div className="activity-icon">
              <Clock size={16} color="#8b5cf6" />
            </div>
            <div className="activity-content">
              <div className="activity-value">{systemMetrics.requestsPerMinute}</div>
              <div className="activity-label">Req/min</div>
            </div>
          </div>

          <div className="activity-metric">
            <div className="activity-icon">
              <AlertCircle size={16} color="#16a34a" />
            </div>
            <div className="activity-content">
              <div className="activity-value">{systemMetrics.responseTime}s</div>
              <div className="activity-label">Tempo Resposta</div>
            </div>
          </div>
        </div>
      </div>

      <div className="system-info-section">
        <h5>Informações do Sistema</h5>
        <div className="system-info-grid">
          <div className="info-item">
            <span className="info-label">Timestamp:</span>
            <span className="info-value">{formatDate(systemMetrics.timestamp)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Project ID:</span>
            <span className="info-value">{connection.projectId}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Conectado desde:</span>
            <span className="info-value">{formatDate(connection.connectedAt)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};