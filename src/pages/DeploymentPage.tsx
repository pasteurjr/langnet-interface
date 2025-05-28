import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Rocket, 
  Settings, 
  Activity, 
  History, 
  Shield,
  Database,
  Play,
  Pause,
  RotateCcw,
  Download,
  AlertCircle,
  CheckCircle,
  Clock,
  Server,
  Globe
} from 'lucide-react';
import {
  DeploymentEnvironment,
  DeploymentStatus,
  DeploymentTarget,
  CloudProvider,
  InstanceType,
  ScalingType,
  CiCdPipeline,
  DeploymentHistory,
  EnvironmentMetrics
} from '../types/deployment';
import { EnvironmentConfig } from '../components/deployment/EnvironmentConfig';
import { PipelineViewer } from '../components/deployment/PipelineViewer';
import { DeploymentHistory as DeploymentHistoryComponent } from '../components/deployment/DeploymentHistory';
import { InfrastructurePanel } from '../components/deployment/InfrastructurePanel';
import { SecurityPanel } from '../components/deployment/SecurityPanel';
import './DeploymentPage.css';

const DeploymentPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [activeTab, setActiveTab] = useState<'overview' | 'config' | 'pipeline' | 'history' | 'infrastructure' | 'security'>('overview');
  const [isDeploying, setIsDeploying] = useState(false);
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('production');

  // Mock data - seria obtido via API
  const environments: DeploymentEnvironment[] = [
    {
      id: 'prod-1',
      name: 'Production',
      type: 'production',
      status: 'active',
      url: 'https://app.myproject.com',
      currentVersion: 'v1.2.1',
      config: {
        id: 'config-1',
        name: 'Production Config',
        target: DeploymentTarget.KUBERNETES,
        cloudProvider: CloudProvider.AWS,
        region: 'us-east-1',
        instanceType: InstanceType.MEDIUM,
        scalingType: ScalingType.AUTO,
        minInstances: 2,
        maxInstances: 10,
        environmentVariables: {
          NODE_ENV: 'production',
          DATABASE_URL: '***hidden***',
          REDIS_URL: '***hidden***'
        },
        secrets: {
          JWT_SECRET: '***hidden***',
          API_KEY: '***hidden***'
        },
        domain: 'app.myproject.com',
        ssl: true,
        monitoring: true,
        logging: true,
        backup: true,
        createdAt: '2024-01-15T10:00:00Z',
        updatedAt: '2024-03-15T14:30:00Z'
      },
      metrics: {
        timestamp: new Date().toISOString(),
        cpu: 45.2,
        memory: 67.8,
        disk: 23.4,
        network: {
          bytesIn: 1024000000,
          bytesOut: 2048000000,
          requestsPerSecond: 125
        },
        activeInstances: 3,
        healthChecks: {
          total: 6,
          passing: 6,
          failing: 0
        },
        responseTime: 285,
        errorRate: 0.2,
        uptime: 99.97
      },
      security: {
        firewall: {
          enabled: true,
          rules: []
        },
        ssl: {
          enabled: true,
          autoRenewal: true
        },
        accessControl: {
          enabled: true,
          whitelist: [],
          basicAuth: false,
          oauth: true
        },
        secrets: {
          encrypted: true,
          vault: 'aws-secrets-manager',
          rotationEnabled: true
        }
      },
      backup: {
        enabled: true,
        frequency: 'daily',
        retention: 30,
        storage: CloudProvider.AWS,
        encryption: true,
        lastBackup: '2024-03-15T02:00:00Z',
        nextBackup: '2024-03-16T02:00:00Z',
        backupSize: 1024
      },
      resources: [],
      createdAt: '2024-01-15T10:00:00Z',
      updatedAt: '2024-03-15T14:30:00Z'
    },
    {
      id: 'staging-1',
      name: 'Staging',
      type: 'staging',
      status: 'active',
      url: 'https://staging.myproject.com',
      currentVersion: 'v1.3.0-beta',
      config: {
        id: 'config-2',
        name: 'Staging Config',
        target: DeploymentTarget.DOCKER,
        cloudProvider: CloudProvider.AWS,
        region: 'us-east-1',
        instanceType: InstanceType.SMALL,
        scalingType: ScalingType.FIXED,
        minInstances: 1,
        maxInstances: 2,
        environmentVariables: {
          NODE_ENV: 'staging'
        },
        secrets: {},
        ssl: true,
        monitoring: true,
        logging: true,
        backup: false,
        createdAt: '2024-01-15T10:00:00Z',
        updatedAt: '2024-03-15T14:30:00Z'
      },
      metrics: {
        timestamp: new Date().toISOString(),
        cpu: 25.1,
        memory: 42.3,
        disk: 15.7,
        network: {
          bytesIn: 102400000,
          bytesOut: 204800000,
          requestsPerSecond: 12
        },
        activeInstances: 1,
        healthChecks: {
          total: 2,
          passing: 2,
          failing: 0
        },
        responseTime: 320,
        errorRate: 1.2,
        uptime: 98.5
      },
      security: {
        firewall: { enabled: false, rules: [] },
        ssl: { enabled: true, autoRenewal: true },
        accessControl: { enabled: false, whitelist: [], basicAuth: false, oauth: false },
        secrets: { encrypted: true, vault: 'local', rotationEnabled: false }
      },
      backup: {
        enabled: false,
        frequency: 'daily',
        retention: 7,
        storage: CloudProvider.AWS,
        encryption: false
      },
      resources: [],
      createdAt: '2024-01-15T10:00:00Z',
      updatedAt: '2024-03-15T14:30:00Z'
    }
  ];

  const activePipeline: CiCdPipeline = {
    id: 'pipeline-1',
    name: 'Deploy to Production',
    status: DeploymentStatus.DEPLOYING,
    currentStage: 'deploy',
    stages: [
      {
        id: 'build',
        name: 'Build',
        status: 'success',
        startTime: '2024-03-15T14:25:00Z',
        endTime: '2024-03-15T14:27:30Z',
        duration: 150000,
        logs: ['Building Docker image...', 'Image built successfully'],
        artifacts: ['app:v1.2.2']
      },
      {
        id: 'test',
        name: 'Test',
        status: 'success',
        startTime: '2024-03-15T14:27:30Z',
        endTime: '2024-03-15T14:29:00Z',
        duration: 90000,
        logs: ['Running unit tests...', 'All tests passed: 127/127'],
        artifacts: ['test-results.xml']
      },
      {
        id: 'security',
        name: 'Security Scan',
        status: 'success',
        startTime: '2024-03-15T14:29:00Z',
        endTime: '2024-03-15T14:30:15Z',
        duration: 75000,
        logs: ['Running security scan...', 'No vulnerabilities found'],
        artifacts: ['security-report.json']
      },
      {
        id: 'deploy',
        name: 'Deploy',
        status: 'running',
        startTime: '2024-03-15T14:30:15Z',
        logs: ['Deploying to Kubernetes...', 'Rolling update in progress...'],
        artifacts: []
      }
    ],
    triggeredBy: 'admin@myproject.com',
    triggeredAt: '2024-03-15T14:25:00Z',
    branch: 'main',
    commit: 'abc123def456',
    version: 'v1.2.2'
  };

  const deploymentHistory: DeploymentHistory[] = [
    {
      id: 'deploy-1',
      version: 'v1.2.1',
      status: DeploymentStatus.DEPLOYED,
      deployedAt: '2024-03-14T16:20:00Z',
      deployedBy: 'admin@myproject.com',
      duration: 420000,
      commit: 'def456abc789',
      changes: ['Fixed critical bug in authentication', 'Updated dependencies'],
      rollbackAvailable: true,
      logs: []
    },
    {
      id: 'deploy-2',
      version: 'v1.2.0',
      status: DeploymentStatus.DEPLOYED,
      deployedAt: '2024-03-10T09:15:00Z',
      deployedBy: 'dev@myproject.com',
      duration: 380000,
      commit: '789abc123def',
      changes: ['New user dashboard', 'Performance improvements'],
      rollbackAvailable: true,
      logs: []
    }
  ];

  const currentEnvironment = environments.find(env => env.id === selectedEnvironment) || environments[0];

  const handleDeploy = () => {
    setIsDeploying(true);
    // Simular deployment
    setTimeout(() => {
      setIsDeploying(false);
    }, 5000);
  };

  const handleRollback = (deploymentId: string) => {
    console.log('Rolling back to deployment:', deploymentId);
  };

  const handleConfigUpdate = (config: Partial<DeploymentEnvironment>) => {
    console.log('Updating config:', config);
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#16a34a';
      case 'deployed': return '#16a34a';
      case 'deploying': return '#f59e0b';
      case 'building': return '#3b82f6';
      case 'failed': return '#dc2626';
      case 'inactive': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'deployed': return <CheckCircle size={16} />;
      case 'deploying':
      case 'building': return <Clock size={16} />;
      case 'failed': return <AlertCircle size={16} />;
      default: return <Server size={16} />;
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-title-section">
            <div className="page-icon">
              <Rocket size={24} />
            </div>
            <div>
              <h1 className="page-title">Deployment</h1>
              <p className="page-description">
                Gerencie configurações de deployment, pipelines CI/CD e infraestrutura
              </p>
            </div>
          </div>
          <div className="page-actions">
            <button 
              className="btn btn-primary"
              onClick={handleDeploy}
              disabled={isDeploying}
            >
              <Play size={16} />
              {isDeploying ? 'Deployando...' : 'Deploy Now'}
            </button>
          </div>
        </div>
      </div>

      <div className="page-content">
        <div className="page-sidebar">
          <div className="sidebar-section">
            <h3>Environments</h3>
            <div className="environment-list">
              {environments.map(env => (
                <div 
                  key={env.id}
                  className={`environment-item ${selectedEnvironment === env.id ? 'active' : ''}`}
                  onClick={() => setSelectedEnvironment(env.id)}
                >
                  <div className="environment-info">
                    <div className="environment-name">{env.name}</div>
                    <div className="environment-version">{env.currentVersion}</div>
                  </div>
                  <div 
                    className="environment-status"
                    style={{ color: getStatusColor(env.status) }}
                  >
                    {getStatusIcon(env.status)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-section">
            <h3>Navegação</h3>
            <nav className="sidebar-nav">
              <button
                className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <Activity size={16} />
                Visão Geral
              </button>
              <button
                className={`nav-item ${activeTab === 'config' ? 'active' : ''}`}
                onClick={() => setActiveTab('config')}
              >
                <Settings size={16} />
                Configuração
              </button>
              <button
                className={`nav-item ${activeTab === 'pipeline' ? 'active' : ''}`}
                onClick={() => setActiveTab('pipeline')}
              >
                <Rocket size={16} />
                Pipeline CI/CD
              </button>
              <button
                className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
                onClick={() => setActiveTab('history')}
              >
                <History size={16} />
                Histórico
              </button>
              <button
                className={`nav-item ${activeTab === 'infrastructure' ? 'active' : ''}`}
                onClick={() => setActiveTab('infrastructure')}
              >
                <Database size={16} />
                Infraestrutura
              </button>
              <button
                className={`nav-item ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                <Shield size={16} />
                Segurança
              </button>
            </nav>
          </div>
        </div>

        <div className="page-main">
          <div className="main-header">
            <h2>{currentEnvironment.name} Environment</h2>
            <div className="main-actions">
              {currentEnvironment.url && (
                <a 
                  href={currentEnvironment.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  <Globe size={16} />
                  Abrir App
                </a>
              )}
              <button className="btn btn-secondary">
                <Download size={16} />
                Logs
              </button>
              <button className="btn btn-secondary">
                <RotateCcw size={16} />
                Rollback
              </button>
            </div>
          </div>

          <div className="main-content">
            {activeTab === 'overview' && (
              <div className="overview-content">
                <div className="metrics-grid">
                  <div className="metric-card">
                    <div className="metric-header">
                      <Activity size={16} />
                      <span>Status</span>
                    </div>
                    <div className="metric-value" style={{ color: getStatusColor(currentEnvironment.status) }}>
                      {currentEnvironment.status}
                    </div>
                    <div className="metric-detail">
                      Uptime: {currentEnvironment.metrics.uptime}%
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-header">
                      <Server size={16} />
                      <span>Instâncias</span>
                    </div>
                    <div className="metric-value">
                      {currentEnvironment.metrics.activeInstances}
                    </div>
                    <div className="metric-detail">
                      de {currentEnvironment.config.maxInstances} max
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-header">
                      <Clock size={16} />
                      <span>Response Time</span>
                    </div>
                    <div className="metric-value">
                      {currentEnvironment.metrics.responseTime}ms
                    </div>
                    <div className="metric-detail">
                      {currentEnvironment.metrics.network.requestsPerSecond} req/s
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-header">
                      <AlertCircle size={16} />
                      <span>Error Rate</span>
                    </div>
                    <div className="metric-value">
                      {currentEnvironment.metrics.errorRate}%
                    </div>
                    <div className="metric-detail">
                      Últimas 24 horas
                    </div>
                  </div>
                </div>

                <div className="system-metrics">
                  <h3>Métricas do Sistema</h3>
                  <div className="system-metrics-grid">
                    <div className="system-metric">
                      <div className="metric-label">CPU</div>
                      <div className="metric-bar">
                        <div 
                          className="metric-fill"
                          style={{ 
                            width: `${currentEnvironment.metrics.cpu}%`,
                            backgroundColor: currentEnvironment.metrics.cpu > 80 ? '#dc2626' : '#16a34a'
                          }}
                        />
                      </div>
                      <div className="metric-value">{currentEnvironment.metrics.cpu.toFixed(1)}%</div>
                    </div>

                    <div className="system-metric">
                      <div className="metric-label">Memória</div>
                      <div className="metric-bar">
                        <div 
                          className="metric-fill"
                          style={{ 
                            width: `${currentEnvironment.metrics.memory}%`,
                            backgroundColor: currentEnvironment.metrics.memory > 80 ? '#dc2626' : '#16a34a'
                          }}
                        />
                      </div>
                      <div className="metric-value">{currentEnvironment.metrics.memory.toFixed(1)}%</div>
                    </div>

                    <div className="system-metric">
                      <div className="metric-label">Disco</div>
                      <div className="metric-bar">
                        <div 
                          className="metric-fill"
                          style={{ 
                            width: `${currentEnvironment.metrics.disk}%`,
                            backgroundColor: currentEnvironment.metrics.disk > 80 ? '#dc2626' : '#16a34a'
                          }}
                        />
                      </div>
                      <div className="metric-value">{currentEnvironment.metrics.disk.toFixed(1)}%</div>
                    </div>
                  </div>
                </div>

                <div className="network-info">
                  <h3>Tráfego de Rede</h3>
                  <div className="network-stats">
                    <div className="network-stat">
                      <span className="stat-label">Entrada:</span>
                      <span className="stat-value">{formatBytes(currentEnvironment.metrics.network.bytesIn)}</span>
                    </div>
                    <div className="network-stat">
                      <span className="stat-label">Saída:</span>
                      <span className="stat-value">{formatBytes(currentEnvironment.metrics.network.bytesOut)}</span>
                    </div>
                    <div className="network-stat">
                      <span className="stat-label">Requests/s:</span>
                      <span className="stat-value">{currentEnvironment.metrics.network.requestsPerSecond}</span>
                    </div>
                  </div>
                </div>

                <div className="health-checks">
                  <h3>Health Checks</h3>
                  <div className="health-status">
                    <div className="health-summary">
                      <span className="health-passing">
                        {currentEnvironment.metrics.healthChecks.passing} Passing
                      </span>
                      {currentEnvironment.metrics.healthChecks.failing > 0 && (
                        <span className="health-failing">
                          {currentEnvironment.metrics.healthChecks.failing} Failing
                        </span>
                      )}
                    </div>
                    <div className="health-progress">
                      <div 
                        className="health-bar"
                        style={{
                          width: `${(currentEnvironment.metrics.healthChecks.passing / currentEnvironment.metrics.healthChecks.total) * 100}%`
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'config' && (
              <EnvironmentConfig
                environment={currentEnvironment}
                onUpdate={handleConfigUpdate}
              />
            )}

            {activeTab === 'pipeline' && (
              <PipelineViewer
                pipeline={activePipeline}
                isActive={isDeploying}
              />
            )}

            {activeTab === 'history' && (
              <DeploymentHistoryComponent
                history={deploymentHistory}
                onRollback={handleRollback}
              />
            )}

            {activeTab === 'infrastructure' && (
              <InfrastructurePanel
                environment={currentEnvironment}
              />
            )}

            {activeTab === 'security' && (
              <SecurityPanel
                environment={currentEnvironment}
                onUpdate={handleConfigUpdate}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeploymentPage;