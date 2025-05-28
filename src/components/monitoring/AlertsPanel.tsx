import React from 'react';
import { Bell, AlertTriangle, CheckCircle, Clock, Mail, MessageSquare, Webhook, Plus } from 'lucide-react';
import { AlertRule, AlertEvent } from '../../types/monitoring';
import './monitoring.css';

interface AlertsPanelProps {
  alertRules: AlertRule[];
  recentAlerts: AlertEvent[];
}

export const AlertsPanel: React.FC<AlertsPanelProps> = ({
  alertRules,
  recentAlerts
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email': return <Mail size={12} />;
      case 'slack': return <MessageSquare size={12} />;
      case 'webhook': return <Webhook size={12} />;
      default: return <Bell size={12} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertTriangle size={16} color="#dc2626" />;
      case 'warning': return <AlertTriangle size={16} color="#f59e0b" />;
      case 'info': return <CheckCircle size={16} color="#3b82f6" />;
      default: return <Bell size={16} color="#6b7280" />;
    }
  };

  return (
    <div className="alerts-panel">
      <div className="alerts-section">
        <div className="alerts-section-header">
          <h4>
            <Bell size={16} />
            Regras de Alerta ({alertRules.length})
          </h4>
          <button className="add-alert-btn">
            <Plus size={14} />
            Nova Regra
          </button>
        </div>

        <div className="alert-rules-list">
          {alertRules.length === 0 ? (
            <div className="empty-state">
              <Bell size={32} color="#ccc" />
              <p>Nenhuma regra de alerta configurada</p>
            </div>
          ) : (
            alertRules.map(rule => (
              <div key={rule.id} className={`alert-rule-item ${rule.enabled ? 'enabled' : 'disabled'}`}>
                <div className="alert-rule-header">
                  <div className="alert-rule-info">
                    <span className="alert-rule-name">{rule.name}</span>
                    <span className={`alert-rule-status ${rule.enabled ? 'enabled' : 'disabled'}`}>
                      {rule.enabled ? 'Ativo' : 'Inativo'}
                    </span>
                  </div>
                  <div className="alert-rule-actions">
                    <button className="rule-action-btn">Editar</button>
                    <button className="rule-action-btn">
                      {rule.enabled ? 'Desativar' : 'Ativar'}
                    </button>
                  </div>
                </div>

                <div className="alert-rule-description">
                  {rule.description}
                </div>

                <div className="alert-rule-condition">
                  <strong>Condição:</strong> {rule.condition} &gt; {rule.threshold}
                </div>

                <div className="alert-rule-meta">
                  <div className="alert-rule-channels">
                    <span className="meta-label">Canais:</span>
                    {rule.channels.map(channel => (
                      <span key={channel} className="alert-channel-tag">
                        {getChannelIcon(channel)}
                        {channel}
                      </span>
                    ))}
                  </div>

                  <div className="alert-rule-triggers">
                    <span className="meta-label">Disparos:</span>
                    <span className="trigger-count">{rule.triggerCount}</span>
                    {rule.lastTriggered && (
                      <span className="last-triggered">
                        Último: {formatDate(rule.lastTriggered)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="alerts-section">
        <div className="alerts-section-header">
          <h4>
            <AlertTriangle size={16} />
            Alertas Recentes ({recentAlerts.length})
          </h4>
        </div>

        <div className="recent-alerts-list">
          {recentAlerts.length === 0 ? (
            <div className="empty-state">
              <CheckCircle size={32} color="#16a34a" />
              <p>Nenhum alerta recente</p>
              <small>Tudo funcionando normalmente!</small>
            </div>
          ) : (
            recentAlerts.map(alert => (
              <div 
                key={alert.id} 
                className={`alert-event-item ${alert.severity}`}
                style={{ borderLeftColor: getSeverityColor(alert.severity) }}
              >
                <div className="alert-event-header">
                  <div className="alert-event-severity">
                    {getSeverityIcon(alert.severity)}
                    <span className="severity-text">{alert.severity.toUpperCase()}</span>
                  </div>
                  <div className="alert-event-time">
                    <Clock size={12} />
                    {formatDate(alert.triggeredAt)}
                  </div>
                </div>

                <div className="alert-event-content">
                  <div className="alert-event-rule">
                    <strong>{alert.ruleName}</strong>
                  </div>
                  <div className="alert-event-message">
                    {alert.message}
                  </div>
                </div>

                <div className="alert-event-footer">
                  {alert.resolvedAt ? (
                    <div className="alert-event-resolved">
                      <CheckCircle size={12} />
                      Resolvido em {formatDate(alert.resolvedAt)}
                    </div>
                  ) : (
                    <div className="alert-event-active">
                      <AlertTriangle size={12} />
                      Alerta ativo
                    </div>
                  )}
                  
                  <div className="alert-event-actions">
                    <button className="alert-action-btn">Ver Detalhes</button>
                    {!alert.resolvedAt && (
                      <button className="alert-action-btn primary">Marcar como Resolvido</button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};