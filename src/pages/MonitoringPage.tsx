import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  CheckCircle,
  Clock,
  Database,
  Download,
  Eye,
  Filter,
  RefreshCw,
  Settings,
  TrendingUp,
  Users,
  Zap
} from 'lucide-react';
import './MonitoringPage.css';
import { LangfuseConnectionModal } from '../components/monitoring/LangFuseConnectionModal';
import { TraceViewer } from '../components/monitoring/TraceViewer';
import { MetricsPanel } from '../components/monitoring/MetricsPanel';
import { AlertsPanel } from '../components/monitoring/AlertsPanel';
import { SystemOverview } from '../components/monitoring/SystemOverview';
import {
  MonitoringDashboard,
  MonitoringStatus,
  TraceStatus,
  TraceData,
  SpanData,
  GenerationData,
  MonitoringMetrics,
  SystemMetrics,
  AlertRule,
  AlertEvent,
  LangfuseConnection
} from '../types/monitoring';

const mockDashboard: MonitoringDashboard = {
  id: '1',
  projectId: 'project1',
  name: 'Customer Support System - Monitoring',
  description: 'Real-time monitoring and analytics for the customer support system',
  connection: {
    id: 'conn1',
    projectId: 'project1',
    publicKey: 'pk-lf-1234567890abcdef',
    secretKey: '***hidden***',
    host: 'https://cloud.langfuse.com',
    status: MonitoringStatus.CONNECTED,
    connectedAt: '2024-03-15T09:00:00',
    lastSync: '2024-03-15T14:30:00',
    settings: {
      enableTracing: true,
      sampleRate: 1.0,
      bufferSize: 1000,
      flushInterval: 5000,
      enableMetrics: true,
      enableAlerts: true
    }
  },
  metrics: {
    totalTraces: 1247,
    totalSpans: 4892,
    totalGenerations: 2156,
    totalCost: 45.67,
    totalTokens: 125847,
    averageLatency: 2.3,
    errorRate: 2.1,
    successRate: 97.9,
    timeRange: {
      start: '2024-03-15T00:00:00',
      end: '2024-03-15T23:59:59'
    }
  },
  systemMetrics: [
    {
      timestamp: '2024-03-15T14:30:00',
      cpu: 45,
      memory: 67,
      disk: 23,
      network: {
        bytesIn: 1024000,
        bytesOut: 768000
      },
      activeAgents: 8,
      queueDepth: 12,
      requestsPerMinute: 45,
      responseTime: 2.3
    }
  ],
  recentTraces: [
    {
      id: 'trace1',
      sessionId: 'session1',
      name: 'Customer Query Processing',
      input: { query: 'I need help with billing' },
      output: { response: 'Routing to billing specialist', classification: 'billing' },
      metadata: { userId: 'user123', channel: 'web' },
      startTime: '2024-03-15T14:25:00',
      endTime: '2024-03-15T14:25:03',
      duration: 3000,
      status: TraceStatus.COMPLETED,
      level: 'DEFAULT',
      tags: ['customer-service', 'billing'],
      public: false
    },
    {
      id: 'trace2',
      sessionId: 'session2',
      name: 'Technical Support Query',
      input: { query: 'My account is not working' },
      output: { response: 'Escalated to technical team', priority: 'high' },
      metadata: { userId: 'user456', channel: 'chat' },
      startTime: '2024-03-15T14:20:00',
      endTime: '2024-03-15T14:20:05',
      duration: 5000,
      status: TraceStatus.COMPLETED,
      level: 'DEFAULT',
      tags: ['technical-support', 'escalation'],
      public: false
    }
  ],
  recentSpans: [
    {
      id: 'span1',
      traceId: 'trace1',
      name: 'Sentiment Analysis',
      input: { text: 'I need help with billing' },
      output: { sentiment: 'neutral', score: 0.1 },
      startTime: '2024-03-15T14:25:01',
      endTime: '2024-03-15T14:25:02',
      duration: 1000,
      level: 'DEFAULT',
      tags: ['sentiment', 'analysis']
    }
  ],
  recentGenerations: [
    {
      id: 'gen1',
      traceId: 'trace1',
      name: 'Response Generation',
      model: 'gpt-4',
      modelParameters: {
        temperature: 0.7,
        maxTokens: 150
      },
      prompt: 'Generate helpful response for billing query',
      completion: 'I understand you need help with billing. Let me connect you with our billing specialist.',
      usage: {
        promptTokens: 45,
        completionTokens: 23,
        totalTokens: 68
      },
      startTime: '2024-03-15T14:25:02',
      endTime: '2024-03-15T14:25:03',
      duration: 1000,
      level: 'DEFAULT',
      tags: ['generation', 'gpt-4']
    }
  ],
  alertRules: [
    {
      id: 'alert1',
      name: 'High Error Rate',
      description: 'Alert when error rate exceeds 5%',
      condition: 'error_rate > 5',
      threshold: 5,
      enabled: true,
      channels: ['email', 'slack'],
      triggerCount: 2,
      lastTriggered: '2024-03-14T15:30:00'
    },
    {
      id: 'alert2',
      name: 'Response Time Spike',
      description: 'Alert when average response time exceeds 10 seconds',
      condition: 'avg_response_time > 10',
      threshold: 10,
      enabled: true,
      channels: ['email'],
      triggerCount: 0
    }
  ],
  recentAlerts: [
    {
      id: 'alertevent1',
      ruleId: 'alert1',
      ruleName: 'High Error Rate',
      message: 'Error rate reached 6.2% in the last 10 minutes',
      severity: 'warning',
      triggeredAt: '2024-03-14T15:30:00',
      resolvedAt: '2024-03-14T15:45:00'
    }
  ],
  isRealTime: true,
  refreshInterval: 30000,
  timeRange: {
    start: '2024-03-15T00:00:00',
    end: '2024-03-15T23:59:59',
    preset: '24h'
  }
};

interface MonitoringPageProps {
  // Props podem ser adicionadas conforme necessário
}

export const MonitoringPage: React.FC<MonitoringPageProps> = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [dashboard, setDashboard] = useState<MonitoringDashboard>(mockDashboard);
  const [isConnectionModalOpen, setIsConnectionModalOpen] = useState(false);
  const [selectedTrace, setSelectedTrace] = useState<TraceData | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'traces' | 'metrics' | 'alerts'>('overview');
  const [isRealTime, setIsRealTime] = useState(true);
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');

  const handleConnect = () => {
    setIsConnectionModalOpen(true);
  };

  const handleRefresh = () => {
    console.log('Refreshing monitoring data...');
    // Simulate refresh
  };

  const handleDownloadReport = () => {
    console.log('Downloading monitoring report...');
  };

  const handleTraceSelect = (trace: TraceData) => {
    setSelectedTrace(trace);
  };

  const handleToggleRealTime = () => {
    setIsRealTime(!isRealTime);
  };

  const getStatusIcon = (status: MonitoringStatus) => {
    switch (status) {
      case MonitoringStatus.CONNECTED: return '🟢';
      case MonitoringStatus.CONNECTING: return '🟡';
      case MonitoringStatus.DISCONNECTED: return '🔴';
      case MonitoringStatus.ERROR: return '❌';
      case MonitoringStatus.SYNCING: return '🔄';
      default: return '⚫';
    }
  };

  const getStatusText = (status: MonitoringStatus) => {
    switch (status) {
      case MonitoringStatus.CONNECTED: return 'Conectado';
      case MonitoringStatus.CONNECTING: return 'Conectando';
      case MonitoringStatus.DISCONNECTED: return 'Desconectado';
      case MonitoringStatus.ERROR: return 'Erro';
      case MonitoringStatus.SYNCING: return 'Sincronizando';
      default: return 'Desconhecido';
    }
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

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  useEffect(() => {
    if (isRealTime) {
      const interval = setInterval(() => {
        handleRefresh();
      }, dashboard.refreshInterval);

      return () => clearInterval(interval);
    }
  }, [isRealTime, dashboard.refreshInterval]);

  return (
    <div className="monitoring-page">
      {/* Header - seguindo o padrão da SpecificationPage e CodePage */}
      <div className="monitoring-header">
        <div className="monitoring-header-left">
          <h1>
            {getStatusIcon(dashboard.connection.status)} Monitoramento & Analytics
            <span className={`monitoring-status-badge status-${dashboard.connection.status}`}>
              {getStatusText(dashboard.connection.status)}
            </span>
          </h1>
          <p>Monitoramento em tempo real via Langfuse com métricas e análises detalhadas</p>
        </div>
        <div className="monitoring-header-actions">
          <button className="monitoring-action-button secondary" onClick={handleDownloadReport}>
            <Download size={18} />
            Relatório
          </button>
          <button 
            className={`monitoring-action-button ${isRealTime ? 'primary' : 'secondary'}`}
            onClick={handleToggleRealTime}
          >
            <Activity size={18} />
            {isRealTime ? 'Tempo Real: ON' : 'Tempo Real: OFF'}
          </button>
          <button className="monitoring-action-button secondary" onClick={handleRefresh}>
            <RefreshCw size={18} />
            Atualizar
          </button>
          <button className="monitoring-action-button primary" onClick={handleConnect}>
            <Settings size={18} />
            Configurar Langfuse
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="monitoring-content">
        {/* Sidebar */}
        <div className="monitoring-sidebar">
          <div className="monitoring-sidebar-header">
            <h3>Status do Sistema</h3>
            <div className="monitoring-progress-info">
              <div className="monitoring-stat">
                <span className="monitoring-stat-number">{dashboard.metrics.successRate}%</span>
                <span className="monitoring-stat-label">Sucesso</span>
              </div>
              <div className="monitoring-stat">
                <span className="monitoring-stat-number">{dashboard.metrics.averageLatency}s</span>
                <span className="monitoring-stat-label">Latência</span>
              </div>
              <div className="monitoring-stat">
                <span className="monitoring-stat-number">{dashboard.systemMetrics[0]?.activeAgents || 0}</span>
                <span className="monitoring-stat-label">Agentes</span>
              </div>
              <div className="monitoring-stat">
                <span className="monitoring-stat-number">{formatCurrency(dashboard.metrics.totalCost)}</span>
                <span className="monitoring-stat-label">Custo</span>
              </div>
            </div>
          </div>

          <div className="monitoring-sidebar-tabs">
            <button
              className={`monitoring-sidebar-tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              📊 Visão Geral
            </button>
            <button
              className={`monitoring-sidebar-tab ${activeTab === 'traces' ? 'active' : ''}`}
              onClick={() => setActiveTab('traces')}
            >
              🔍 Traces ({dashboard.recentTraces.length})
            </button>
            <button
              className={`monitoring-sidebar-tab ${activeTab === 'metrics' ? 'active' : ''}`}
              onClick={() => setActiveTab('metrics')}
            >
              📈 Métricas
            </button>
            <button
              className={`monitoring-sidebar-tab ${activeTab === 'alerts' ? 'active' : ''}`}
              onClick={() => setActiveTab('alerts')}
            >
              🚨 Alertas ({dashboard.recentAlerts.length})
            </button>
          </div>

          <div className="monitoring-sidebar-content">
            {activeTab === 'overview' && (
              <SystemOverview
                systemMetrics={dashboard.systemMetrics[0]}
                connection={dashboard.connection}
              />
            )}
            
            {activeTab === 'traces' && (
              <div className="traces-panel">
                <h4>Traces Recentes</h4>
                <div className="traces-list">
                  {dashboard.recentTraces.map((trace: TraceData) => (
                    <div 
                      key={trace.id} 
                      className={`trace-item ${trace.status}`}
                      onClick={() => handleTraceSelect(trace)}
                    >
                      <div className="trace-name">{trace.name}</div>
                      <div className="trace-duration">{trace.duration}ms</div>
                      <div className="trace-status">{trace.status}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'metrics' && (
              <MetricsPanel
                metrics={dashboard.metrics}
                timeRange={timeRange}
                onTimeRangeChange={setTimeRange}
              />
            )}
            
            {activeTab === 'alerts' && (
              <AlertsPanel
                alertRules={dashboard.alertRules}
                recentAlerts={dashboard.recentAlerts}
              />
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="monitoring-main">
          <div className="monitoring-main-header">
            <div className="monitoring-document-info">
              <h2>{dashboard.name}</h2>
              <div className="monitoring-document-meta">
                <div className="monitoring-version-info">
                  <Database size={16} />
                  <span>Langfuse Cloud</span>
                </div>
                <span>Última sync: {formatDate(dashboard.connection.lastSync || '')}</span>
                <span>{dashboard.metrics.totalTraces.toLocaleString()} traces</span>
              </div>
            </div>
            <div className="monitoring-main-actions">
              <div className="time-range-selector">
                <select 
                  value={timeRange} 
                  onChange={(e) => setTimeRange(e.target.value as any)}
                  className="time-range-select"
                >
                  <option value="1h">Última hora</option>
                  <option value="24h">Últimas 24h</option>
                  <option value="7d">Últimos 7 dias</option>
                  <option value="30d">Últimos 30 dias</option>
                </select>
              </div>
              <button className="monitoring-action-button secondary">
                <Filter size={16} />
                Filtros
              </button>
              <button className="monitoring-action-button secondary">
                <Eye size={16} />
                Visualizar
              </button>
            </div>
          </div>

          <div className="monitoring-editor-container">
            {dashboard.connection.status !== MonitoringStatus.CONNECTED ? (
              <div className="monitoring-empty-state">
                <Activity size={64} />
                <h3>Langfuse não conectado</h3>
                <p>Configure a conexão com Langfuse para começar o monitoramento</p>
                <button className="monitoring-action-button primary" onClick={handleConnect}>
                  <Settings size={18} />
                  Conectar Langfuse
                </button>
              </div>
            ) : (
              <div className="monitoring-dashboard-main">
                {/* Métricas Principais */}
                <div className="metrics-grid">
                  <div className="metric-card">
                    <div className="metric-icon">
                      <BarChart3 size={24} />
                    </div>
                    <div className="metric-content">
                      <div className="metric-value">{dashboard.metrics.totalTraces.toLocaleString()}</div>
                      <div className="metric-label">Total de Traces</div>
                      <div className="metric-change">+12% vs ontem</div>
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-icon">
                      <Zap size={24} />
                    </div>
                    <div className="metric-content">
                      <div className="metric-value">{dashboard.metrics.totalTokens.toLocaleString()}</div>
                      <div className="metric-label">Tokens Processados</div>
                      <div className="metric-change">+8% vs ontem</div>
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-icon">
                      <Clock size={24} />
                    </div>
                    <div className="metric-content">
                      <div className="metric-value">{dashboard.metrics.averageLatency}s</div>
                      <div className="metric-label">Latência Média</div>
                      <div className="metric-change success">-5% vs ontem</div>
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-icon">
                      <TrendingUp size={24} />
                    </div>
                    <div className="metric-content">
                      <div className="metric-value">{formatCurrency(dashboard.metrics.totalCost)}</div>
                      <div className="metric-label">Custo Total</div>
                      <div className="metric-change">+15% vs ontem</div>
                    </div>
                  </div>
                </div>

                {/* Trace Viewer */}
                {selectedTrace ? (
                  <TraceViewer
                    trace={selectedTrace}
                    spans={dashboard.recentSpans.filter(s => s.traceId === selectedTrace.id)}
                    generations={dashboard.recentGenerations.filter(g => g.traceId === selectedTrace.id)}
                    onClose={() => setSelectedTrace(null)}
                  />
                ) : (
                  <div className="traces-overview">
                    <h3>Traces Recentes</h3>
                    <div className="traces-table">
                      <div className="table-header">
                        <div>Nome</div>
                        <div>Status</div>
                        <div>Duração</div>
                        <div>Tokens</div>
                        <div>Horário</div>
                      </div>
                      {dashboard.recentTraces.map((trace: TraceData) => (
                        <div 
                          key={trace.id} 
                          className="table-row"
                          onClick={() => handleTraceSelect(trace)}
                        >
                          <div className="trace-name">{trace.name}</div>
                          <div className={`trace-status ${trace.status}`}>
                            {trace.status === TraceStatus.COMPLETED ? (
                              <CheckCircle size={16} />
                            ) : trace.status === TraceStatus.ERROR ? (
                              <AlertTriangle size={16} />
                            ) : (
                              <Clock size={16} />
                            )}
                            {trace.status}
                          </div>
                          <div>{trace.duration}ms</div>
                          <div>{dashboard.recentGenerations
                            .filter(g => g.traceId === trace.id)
                            .reduce((sum, g) => sum + (g.usage?.totalTokens || 0), 0)
                          }</div>
                          <div>{formatDate(trace.startTime)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Connection Modal */}
      {isConnectionModalOpen && (
        <LangfuseConnectionModal
          isOpen={isConnectionModalOpen}
          onClose={() => setIsConnectionModalOpen(false)}
          onConnect={(config) => {
            console.log('Connecting to Langfuse with config:', config);
            setIsConnectionModalOpen(false);
          }}
          currentConnection={dashboard.connection}
          projectId={projectId || ''}
        />
      )}
    </div>
  );
};

export default MonitoringPage;