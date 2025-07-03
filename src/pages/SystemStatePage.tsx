// src/pages/SystemStatePage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './SystemStatePage.css';

// Types based on requirements from docs
interface SystemMetrics {
  cpu: {
    usage: number;
    cores: number;
    temperature?: number;
  };
  memory: {
    used: number;
    total: number;
    usage: number;
  };
  disk: {
    used: number;
    total: number;
    usage: number;
  };
  network: {
    uploadSpeed: number;
    downloadSpeed: number;
    latency: number;
  };
}

interface AgentState {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'error' | 'stopped';
  lastActivity: string;
  tasksCompleted: number;
  averageResponseTime: number;
  memoryUsage: number;
  cpuUsage: number;
}

interface TaskExecution {
  id: string;
  name: string;
  agentId: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  startTime: string;
  endTime?: string;
  duration?: number;
  progress: number;
  logs: LogEntry[];
}

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  source: string;
  details?: any;
}

interface SystemAlert {
  id: string;
  type: 'warning' | 'error' | 'info';
  title: string;
  description: string;
  timestamp: string;
  resolved: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

const SystemStatePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [agentStates, setAgentStates] = useState<AgentState[]>([]);
  const [taskExecutions, setTaskExecutions] = useState<TaskExecution[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedLogLevel, setSelectedLogLevel] = useState<string>('all');

  // Mock data generation - seguindo padrão das outras páginas
  useEffect(() => {
    const generateMockData = () => {
      // System Metrics
      const mockMetrics: SystemMetrics = {
        cpu: {
          usage: Math.random() * 80 + 10,
          cores: 8,
          temperature: Math.random() * 20 + 45
        },
        memory: {
          used: Math.random() * 12 + 4,
          total: 16,
          usage: 0
        },
        disk: {
          used: Math.random() * 200 + 100,
          total: 500,
          usage: 0
        },
        network: {
          uploadSpeed: Math.random() * 50 + 10,
          downloadSpeed: Math.random() * 100 + 20,
          latency: Math.random() * 30 + 5
        }
      };
      mockMetrics.memory.usage = (mockMetrics.memory.used / mockMetrics.memory.total) * 100;
      mockMetrics.disk.usage = (mockMetrics.disk.used / mockMetrics.disk.total) * 100;
      
      setSystemMetrics(mockMetrics);

      // Agent States
      const mockAgents: AgentState[] = [
        {
          id: '1',
          name: 'Customer Service Agent',
          status: 'active',
          lastActivity: new Date(Date.now() - Math.random() * 300000).toISOString(),
          tasksCompleted: Math.floor(Math.random() * 50) + 10,
          averageResponseTime: Math.random() * 2000 + 500,
          memoryUsage: Math.random() * 200 + 50,
          cpuUsage: Math.random() * 30 + 5
        },
        {
          id: '2',
          name: 'Data Analysis Agent',
          status: 'idle',
          lastActivity: new Date(Date.now() - Math.random() * 600000).toISOString(),
          tasksCompleted: Math.floor(Math.random() * 30) + 5,
          averageResponseTime: Math.random() * 3000 + 1000,
          memoryUsage: Math.random() * 150 + 30,
          cpuUsage: Math.random() * 20 + 2
        },
        {
          id: '3',
          name: 'Code Generator Agent',
          status: 'error',
          lastActivity: new Date(Date.now() - Math.random() * 900000).toISOString(),
          tasksCompleted: Math.floor(Math.random() * 20) + 3,
          averageResponseTime: Math.random() * 5000 + 2000,
          memoryUsage: Math.random() * 300 + 100,
          cpuUsage: Math.random() * 50 + 10
        }
      ];
      setAgentStates(mockAgents);

      // Task Executions
      const mockTasks: TaskExecution[] = [
        {
          id: '1',
          name: 'Process Customer Query',
          agentId: '1',
          status: 'running',
          startTime: new Date(Date.now() - 120000).toISOString(),
          progress: Math.random() * 80 + 10,
          logs: []
        },
        {
          id: '2',
          name: 'Analyze Sales Data',
          agentId: '2',
          status: 'completed',
          startTime: new Date(Date.now() - 600000).toISOString(),
          endTime: new Date(Date.now() - 300000).toISOString(),
          duration: 300000,
          progress: 100,
          logs: []
        },
        {
          id: '3',
          name: 'Generate API Documentation',
          agentId: '3',
          status: 'failed',
          startTime: new Date(Date.now() - 900000).toISOString(),
          endTime: new Date(Date.now() - 800000).toISOString(),
          duration: 100000,
          progress: 45,
          logs: []
        }
      ];
      setTaskExecutions(mockTasks);

      // System Logs
      const mockLogs: LogEntry[] = [
        {
          id: '1',
          timestamp: new Date(Date.now() - 60000).toISOString(),
          level: 'info',
          message: 'Agent Customer Service Agent completed task successfully',
          source: 'agent-manager'
        },
        {
          id: '2',
          timestamp: new Date(Date.now() - 120000).toISOString(),
          level: 'warning',
          message: 'High memory usage detected for Code Generator Agent',
          source: 'system-monitor'
        },
        {
          id: '3',
          timestamp: new Date(Date.now() - 180000).toISOString(),
          level: 'error',
          message: 'Code Generator Agent failed to process task: timeout error',
          source: 'task-executor'
        },
        {
          id: '4',
          timestamp: new Date(Date.now() - 240000).toISOString(),
          level: 'info',
          message: 'Data Analysis Agent started new task execution',
          source: 'task-scheduler'
        }
      ];
      setLogs(mockLogs);

      // System Alerts
      const mockAlerts: SystemAlert[] = [
        {
          id: '1',
          type: 'warning',
          title: 'High Memory Usage',
          description: 'System memory usage has exceeded 80% for the past 5 minutes',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          resolved: false,
          priority: 'medium'
        },
        {
          id: '2',
          type: 'error',
          title: 'Agent Failure',
          description: 'Code Generator Agent has failed multiple tasks',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          resolved: false,
          priority: 'high'
        },
        {
          id: '3',
          type: 'info',
          title: 'System Update Available',
          description: 'A new system update is available for installation',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          resolved: true,
          priority: 'low'
        }
      ];
      setAlerts(mockAlerts);
    };

    generateMockData();
    
    // Auto refresh
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(generateMockData, 5000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active':
      case 'running':
      case 'completed': return '#10B981';
      case 'idle':
      case 'pending': return '#F59E0B';
      case 'error':
      case 'failed': return '#EF4444';
      case 'stopped': return '#6B7280';
      default: return '#6B7280';
    }
  };

  const getAlertColor = (type: string): string => {
    switch (type) {
      case 'error': return '#EF4444';
      case 'warning': return '#F59E0B';
      case 'info': return '#3B82F6';
      default: return '#6B7280';
    }
  };

  const formatDuration = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const filteredLogs = logs.filter(log => 
    selectedLogLevel === 'all' || log.level === selectedLogLevel
  );

  const unresolvedAlerts = alerts.filter(alert => !alert.resolved);

  return (
    <div className="system-state-page">
      <div className="page-header">
        <div className="header-main">
          <h1>📊 Estado do Sistema</h1>
          <p>Monitoramento em tempo real do sistema e agentes</p>
        </div>
        <div className="header-actions">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="5m">Últimos 5 min</option>
            <option value="1h">Última 1 hora</option>
            <option value="6h">Últimas 6 horas</option>
            <option value="24h">Últimas 24 horas</option>
          </select>
          <button
            className={`refresh-btn ${autoRefresh ? 'active' : ''}`}
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            🔄 Auto Refresh
          </button>
        </div>
      </div>

      <div className="page-content">
        {/* System Overview */}
        <div className="overview-section">
          <h2>Visão Geral do Sistema</h2>
          <div className="metrics-grid">
            {systemMetrics && (
              <>
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-icon">🖥️</span>
                    <span className="metric-title">CPU</span>
                  </div>
                  <div className="metric-value">{systemMetrics.cpu.usage.toFixed(1)}%</div>
                  <div className="metric-details">
                    <span>{systemMetrics.cpu.cores} cores</span>
                    {systemMetrics.cpu.temperature && (
                      <span>{systemMetrics.cpu.temperature.toFixed(1)}°C</span>
                    )}
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ 
                        width: `${systemMetrics.cpu.usage}%`,
                        backgroundColor: systemMetrics.cpu.usage > 80 ? '#EF4444' : '#3B82F6'
                      }}
                    />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-icon">💾</span>
                    <span className="metric-title">Memória</span>
                  </div>
                  <div className="metric-value">{systemMetrics.memory.usage.toFixed(1)}%</div>
                  <div className="metric-details">
                    <span>{systemMetrics.memory.used.toFixed(1)} GB / {systemMetrics.memory.total} GB</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ 
                        width: `${systemMetrics.memory.usage}%`,
                        backgroundColor: systemMetrics.memory.usage > 80 ? '#EF4444' : '#10B981'
                      }}
                    />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-icon">💿</span>
                    <span className="metric-title">Disco</span>
                  </div>
                  <div className="metric-value">{systemMetrics.disk.usage.toFixed(1)}%</div>
                  <div className="metric-details">
                    <span>{systemMetrics.disk.used} GB / {systemMetrics.disk.total} GB</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ 
                        width: `${systemMetrics.disk.usage}%`,
                        backgroundColor: systemMetrics.disk.usage > 90 ? '#EF4444' : '#F59E0B'
                      }}
                    />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-icon">🌐</span>
                    <span className="metric-title">Rede</span>
                  </div>
                  <div className="metric-value">{systemMetrics.network.latency.toFixed(0)}ms</div>
                  <div className="metric-details">
                    <span>↑ {systemMetrics.network.uploadSpeed.toFixed(1)} Mbps</span>
                    <span>↓ {systemMetrics.network.downloadSpeed.toFixed(1)} Mbps</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Alerts Section */}
        {unresolvedAlerts.length > 0 && (
          <div className="alerts-section">
            <h2>⚠️ Alertas Ativos ({unresolvedAlerts.length})</h2>
            <div className="alerts-list">
              {unresolvedAlerts.map(alert => (
                <div 
                  key={alert.id} 
                  className={`alert-card ${alert.type} priority-${alert.priority}`}
                >
                  <div className="alert-header">
                    <span 
                      className="alert-indicator"
                      style={{ backgroundColor: getAlertColor(alert.type) }}
                    />
                    <div className="alert-title">{alert.title}</div>
                    <div className="alert-priority">{alert.priority}</div>
                  </div>
                  <div className="alert-description">{alert.description}</div>
                  <div className="alert-timestamp">
                    {new Date(alert.timestamp).toLocaleString('pt-BR')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="main-content">
          {/* Agents Section */}
          <div className="agents-section">
            <h2>🤖 Estado dos Agentes</h2>
            <div className="agents-list">
              {agentStates.map(agent => (
                <div key={agent.id} className="agent-card">
                  <div className="agent-header">
                    <div className="agent-name">{agent.name}</div>
                    <div 
                      className="agent-status"
                      style={{ backgroundColor: getStatusColor(agent.status) }}
                    >
                      {agent.status}
                    </div>
                  </div>
                  <div className="agent-metrics">
                    <div className="agent-metric">
                      <span className="metric-label">Tarefas Concluídas</span>
                      <span className="metric-value">{agent.tasksCompleted}</span>
                    </div>
                    <div className="agent-metric">
                      <span className="metric-label">Tempo Médio</span>
                      <span className="metric-value">{formatDuration(agent.averageResponseTime)}</span>
                    </div>
                    <div className="agent-metric">
                      <span className="metric-label">Memória</span>
                      <span className="metric-value">{formatBytes(agent.memoryUsage * 1024 * 1024)}</span>
                    </div>
                    <div className="agent-metric">
                      <span className="metric-label">CPU</span>
                      <span className="metric-value">{agent.cpuUsage.toFixed(1)}%</span>
                    </div>
                  </div>
                  <div className="agent-last-activity">
                    Última atividade: {new Date(agent.lastActivity).toLocaleString('pt-BR')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tasks Section */}
          <div className="tasks-section">
            <h2>📋 Execução de Tarefas</h2>
            <div className="tasks-list">
              {taskExecutions.map(task => (
                <div key={task.id} className="task-card">
                  <div className="task-header">
                    <div className="task-name">{task.name}</div>
                    <div 
                      className="task-status"
                      style={{ backgroundColor: getStatusColor(task.status) }}
                    >
                      {task.status}
                    </div>
                  </div>
                  <div className="task-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ 
                          width: `${task.progress}%`,
                          backgroundColor: getStatusColor(task.status)
                        }}
                      />
                    </div>
                    <span className="progress-text">{task.progress.toFixed(0)}%</span>
                  </div>
                  <div className="task-details">
                    <span>Agente: {agentStates.find(a => a.id === task.agentId)?.name}</span>
                    <span>Início: {new Date(task.startTime).toLocaleString('pt-BR')}</span>
                    {task.duration && (
                      <span>Duração: {formatDuration(task.duration)}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Logs Section */}
        <div className="logs-section">
          <div className="logs-header">
            <h2>📜 Logs do Sistema</h2>
            <select 
              value={selectedLogLevel}
              onChange={(e) => setSelectedLogLevel(e.target.value)}
              className="log-level-select"
            >
              <option value="all">Todos os níveis</option>
              <option value="error">Errors</option>
              <option value="warning">Warnings</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
            </select>
          </div>
          <div className="logs-container">
            {filteredLogs.map(log => (
              <div key={log.id} className={`log-entry ${log.level}`}>
                <div className="log-timestamp">
                  {new Date(log.timestamp).toLocaleTimeString('pt-BR')}
                </div>
                <div 
                  className="log-level"
                  style={{ backgroundColor: getStatusColor(log.level) }}
                >
                  {log.level.toUpperCase()}
                </div>
                <div className="log-source">{log.source}</div>
                <div className="log-message">{log.message}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemStatePage;