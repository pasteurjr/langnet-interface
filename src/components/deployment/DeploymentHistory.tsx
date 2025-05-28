import React from 'react';
import { History, CheckCircle, Clock, AlertCircle, RotateCcw, Eye, GitCommit, User } from 'lucide-react';
import { DeploymentHistory as DeploymentHistoryType } from '../../types/deployment';
import './deployment.css';

interface DeploymentHistoryProps {
  history: DeploymentHistoryType[];
  onRollback: (deploymentId: string) => void;
}

export const DeploymentHistory: React.FC<DeploymentHistoryProps> = ({
  history,
  onRollback
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'deployed': return <CheckCircle size={16} color="#16a34a" />;
      case 'failed': return <AlertCircle size={16} color="#dc2626" />;
      case 'deploying': return <Clock size={16} color="#f59e0b" />;
      default: return <Clock size={16} color="#6b7280" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed': return '#16a34a';
      case 'failed': return '#dc2626';
      case 'deploying': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRelativeTime = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 60) return `${diffMinutes} minutos atrás`;
    if (diffHours < 24) return `${diffHours} horas atrás`;
    if (diffDays < 7) return `${diffDays} dias atrás`;
    return formatDate(dateString);
  };

  return (
    <div className="deployment-history">
      <div className="history-header">
        <h3>
          <History size={18} />
          Histórico de Deployments
        </h3>
        <div className="history-stats">
          <span className="stat-item">
            <span className="stat-value">{history.length}</span>
            <span className="stat-label">Total</span>
          </span>
          <span className="stat-item">
            <span className="stat-value">{history.filter(h => h.status === 'deployed').length}</span>
            <span className="stat-label">Sucessos</span>
          </span>
          <span className="stat-item">
            <span className="stat-value">{history.filter(h => h.status === 'failed').length}</span>
            <span className="stat-label">Falhas</span>
          </span>
        </div>
      </div>

      <div className="history-list">
        {history.length === 0 ? (
          <div className="empty-state">
            <History size={32} color="#ccc" />
            <p>Nenhum deployment encontrado</p>
            <small>Os deployments aparecerão aqui quando forem executados</small>
          </div>
        ) : (
          history.map((deployment, index) => (
            <div key={deployment.id} className="history-item">
              <div className="history-main">
                <div className="deployment-info">
                  <div className="deployment-header">
                    <div className="version-info">
                      <span className="version-tag">{deployment.version}</span>
                      {index === 0 && (
                        <span className="current-badge">ATUAL</span>
                      )}
                    </div>
                    <div 
                      className="deployment-status"
                      style={{ color: getStatusColor(deployment.status) }}
                    >
                      {getStatusIcon(deployment.status)}
                      <span className="status-text">{deployment.status}</span>
                    </div>
                  </div>

                  <div className="deployment-meta">
                    <div className="meta-item">
                      <User size={14} />
                      <span>{deployment.deployedBy}</span>
                    </div>
                    <div className="meta-item">
                      <Clock size={14} />
                      <span>{getRelativeTime(deployment.deployedAt)}</span>
                    </div>
                    <div className="meta-item">
                      <span>Duração: {formatDuration(deployment.duration)}</span>
                    </div>
                    {deployment.commit && (
                      <div className="meta-item">
                        <GitCommit size={14} />
                        <span className="commit-hash">{deployment.commit.substring(0, 8)}</span>
                      </div>
                    )}
                  </div>

                  {deployment.changes && deployment.changes.length > 0 && (
                    <div className="deployment-changes">
                      <h5>Mudanças:</h5>
                      <ul className="changes-list">
                        {deployment.changes.slice(0, 3).map((change, changeIndex) => (
                          <li key={changeIndex} className="change-item">
                            {change}
                          </li>
                        ))}
                        {deployment.changes.length > 3 && (
                          <li className="change-item more">
                            +{deployment.changes.length - 3} mais mudanças
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>

                <div className="deployment-actions">
                  <button className="action-btn" title="Ver detalhes">
                    <Eye size={16} />
                    Detalhes
                  </button>
                  {deployment.rollbackAvailable && deployment.status === 'deployed' && index > 0 && (
                    <button 
                      className="action-btn rollback-btn"
                      onClick={() => onRollback(deployment.id)}
                      title="Fazer rollback para esta versão"
                    >
                      <RotateCcw size={16} />
                      Rollback
                    </button>
                  )}
                </div>
              </div>

              {deployment.status === 'failed' && (
                <div className="deployment-error">
                  <AlertCircle size={16} color="#dc2626" />
                  <span>Deployment falhou. Verifique os logs para mais detalhes.</span>
                </div>
              )}

              {index < history.length - 1 && (
                <div className="history-connector">
                  <div className="connector-line" />
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {history.length > 0 && (
        <div className="history-footer">
          <div className="pagination-info">
            Mostrando {history.length} deployments recentes
          </div>
          <button className="btn btn-secondary">
            Ver Todos os Deployments
          </button>
        </div>
      )}
    </div>
  );
};