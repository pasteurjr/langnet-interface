import React, { useState } from "react";
import {
  Settings as SettingsIcon,
  Users,
  Zap,
  Shield,
  Link,
  BarChart3,
  Database,
  Bell,
  Save,
  RefreshCw,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  HardDrive,
} from "lucide-react";
import {
  SystemSettings,
  LLMConfiguration,
  User,
  Integration,
  BackupConfiguration,
  AnalyticsSettings,
  SystemMetrics,
  SystemHealth,
  LLMProvider,
  UserRole,
  IntegrationStatus,
  BackupFrequency,
} from "../types/settings";
import { GeneralSettings } from "../components/settings/GeneralSettings";
import { LLMSettings } from "../components/settings/LLMSettings";
import UserManagement from "../components/settings/UserManagement";
import IntegrationsSettings from "../components/settings/IntegrationsSettings";
import SecuritySettings from "../components/settings/SecuritySettings";
import { AnalyticsPanel } from "../components/settings/AnalyticsPanel";
import { BackupSettings } from "../components/settings/BackupSettings";
import { NotificationSettings } from "../components/settings/NotificationSettings";
import "./SettingsPage.css";

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<
    | "general"
    | "llms"
    | "users"
    | "security"
    | "integrations"
    | "analytics"
    | "backup"
    | "notifications"
  >("general");

  // Mock data - seria obtido via API
  const systemSettings: SystemSettings = {
    id: "sys-1",
    projectName: "LangNet",
    description:
      "Sistema de criação de aplicações baseadas em agentes inteligentes",
    domain: "langnet.example.com",
    version: "2.1.0",
    environment: "production",
    createdAt: "2024-01-15T10:00:00Z",
    modifiedAt: "2024-03-15T14:30:00Z",
    ownerId: "user-1",
    ownerName: "Admin User",
  };

  const llmConfigurations: LLMConfiguration[] = [
    {
      id: "llm-1",
      provider: LLMProvider.OPENAI,
      name: "OpenAI GPT-4",
      apiKey: "sk-***************************",
      model: "gpt-4",
      temperature: 0.3,
      maxTokens: 4000,
      timeout: 30000,
      retryAttempts: 3,
      isDefault: true,
      enabled: true,
      rateLimit: {
        requestsPerMinute: 60,
        tokensPerMinute: 150000,
      },
      createdAt: "2024-01-15T10:00:00Z",
      updatedAt: "2024-03-15T14:30:00Z",
    },
    {
      id: "llm-2",
      provider: LLMProvider.ANTHROPIC,
      name: "Claude 3 Sonnet",
      apiKey: "sk-ant-*********************",
      model: "claude-3-sonnet-20240229",
      temperature: 0.3,
      maxTokens: 4000,
      timeout: 30000,
      retryAttempts: 3,
      isDefault: false,
      enabled: true,
      rateLimit: {
        requestsPerMinute: 50,
        tokensPerMinute: 100000,
      },
      createdAt: "2024-02-15T10:00:00Z",
      updatedAt: "2024-03-15T14:30:00Z",
    },
  ];

  const users: User[] = [
    {
      id: "user-1",
      name: "Admin User",
      email: "admin@langnet.com",
      role: UserRole.ADMIN,
      isActive: true,
      lastLogin: "2024-03-15T14:30:00Z",
      permissions: ["*"],
      projects: ["project-1", "project-2"],
      createdAt: "2024-01-15T10:00:00Z",
      updatedAt: "2024-03-15T14:30:00Z",
    },
    {
      id: "user-2",
      name: "Dev Team",
      email: "dev@langnet.com",
      role: UserRole.DEVELOPER,
      isActive: true,
      lastLogin: "2024-03-15T12:00:00Z",
      permissions: [
        "projects.create",
        "projects.read",
        "projects.update",
        "deployment.deploy",
      ],
      projects: ["project-1"],
      createdAt: "2024-01-20T10:00:00Z",
      updatedAt: "2024-03-15T12:00:00Z",
    },
    {
      id: "user-3",
      name: "Operations Team",
      email: "ops@langnet.com",
      role: UserRole.OPERATOR,
      isActive: true,
      lastLogin: "2024-03-15T08:00:00Z",
      permissions: ["monitoring.view", "deployment.view", "system.analytics"],
      projects: [],
      createdAt: "2024-02-01T10:00:00Z",
      updatedAt: "2024-03-15T08:00:00Z",
    },
  ];

  const integrations: Integration[] = [
    {
      id: "int-1",
      name: "Langfuse",
      type: "monitoring",
      provider: "langfuse",
      status: IntegrationStatus.CONNECTED,
      endpoint: "https://cloud.langfuse.com",
      configuration: {
        projectId: "proj_123",
        enableTracing: true,
        sampleRate: 1.0,
      },
      healthCheck: {
        lastCheck: "2024-03-15T14:25:00Z",
        isHealthy: true,
        latency: 120,
      },
      usage: {
        requestsToday: 1250,
        requestsThisMonth: 45000,
        quota: 100000,
        cost: 15.5,
      },
      createdAt: "2024-01-15T10:00:00Z",
      updatedAt: "2024-03-15T14:25:00Z",
    },
    {
      id: "int-2",
      name: "Slack Notifications",
      type: "communication",
      provider: "slack",
      status: IntegrationStatus.CONNECTED,
      configuration: {
        workspace: "langnet-team",
        defaultChannel: "#alerts",
        webhookUrl: "https://hooks.slack.com/***",
      },
      healthCheck: {
        lastCheck: "2024-03-15T14:20:00Z",
        isHealthy: true,
        latency: 85,
      },
      usage: {
        requestsToday: 25,
        requestsThisMonth: 750,
      },
      createdAt: "2024-01-20T10:00:00Z",
      updatedAt: "2024-03-15T14:20:00Z",
    },
    {
      id: "int-3",
      name: "GitHub",
      type: "deployment",
      provider: "github",
      status: IntegrationStatus.CONNECTED,
      configuration: {
        organization: "langnet-org",
        defaultRepo: "langnet-projects",
        autoSync: true,
      },
      healthCheck: {
        lastCheck: "2024-03-15T14:15:00Z",
        isHealthy: true,
        latency: 200,
      },
      usage: {
        requestsToday: 45,
        requestsThisMonth: 1200,
      },
      createdAt: "2024-02-01T10:00:00Z",
      updatedAt: "2024-03-15T14:15:00Z",
    },
  ];

  const backupConfig: BackupConfiguration = {
    id: "backup-1",
    enabled: true,
    frequency: BackupFrequency.DAILY,
    retention: 30,
    includeProjects: true,
    includeSettings: true,
    includeUsers: true,
    includeAnalytics: false,
    storageProvider: "aws",
    storageConfig: {
      bucket: "langnet-backups",
      region: "us-east-1",
    },
    encryptionEnabled: true,
    lastBackup: "2024-03-15T02:00:00Z",
    nextBackup: "2024-03-16T02:00:00Z",
    backupSize: 2048,
    status: "active",
  };

  const analyticsSettings: AnalyticsSettings = {
    id: "analytics-1",
    enabled: true,
    dataRetention: 90,
    collectUsageStats: true,
    collectPerformanceMetrics: true,
    collectErrorLogs: true,
    anonymizeData: true,
    exportEnabled: true,
    reportsEnabled: true,
    dashboardUrl: "https://analytics.langnet.com",
  };

  const systemMetrics: SystemMetrics = {
    timestamp: new Date().toISOString(),
    server: {
      uptime: 99.97,
      cpu: 45.2,
      memory: 67.8,
      disk: 23.4,
      network: {
        bytesIn: 1024000000,
        bytesOut: 2048000000,
      },
    },
    application: {
      activeUsers: 24,
      activeProjects: 12,
      requestsPerMinute: 125,
      averageResponseTime: 285,
      errorRate: 0.2,
    },
    database: {
      connections: 15,
      queryTime: 45,
      size: 5120,
    },
  };

  const systemHealth: SystemHealth = {
    overall: "healthy",
    components: {
      database: {
        status: "healthy",
        latency: 45,
        connections: 15,
      },
      api: {
        status: "healthy",
        responseTime: 285,
        errorRate: 0.2,
      },
      integrations: {
        status: "healthy",
        healthyCount: 3,
        totalCount: 3,
      },
      storage: {
        status: "healthy",
        usage: 23.4,
        available: 76.6,
      },
    },
    lastCheck: new Date().toISOString(),
  };

  const handleSettingsUpdate = (settings: Partial<SystemSettings>) => {
    console.log("Updating system settings:", settings);
  };

  const handleLLMUpdate = (
    llmId: string,
    config: Partial<LLMConfiguration>
  ) => {
    console.log("Updating LLM config:", llmId, config);
  };

  const handleUserUpdate = (userId: string, user: Partial<User>) => {
    console.log("Updating user:", userId, user);
  };

  const handleIntegrationUpdate = (
    integrationId: string,
    integration: Partial<Integration>
  ) => {
    console.log("Updating integration:", integrationId, integration);
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle size={16} color="#16a34a" />;
      case "warning":
        return <AlertTriangle size={16} color="#f59e0b" />;
      case "error":
        return <AlertTriangle size={16} color="#dc2626" />;
      default:
        return <Clock size={16} color="#6b7280" />;
    }
  };

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "#16a34a";
      case "warning":
        return "#f59e0b";
      case "error":
        return "#dc2626";
      default:
        return "#6b7280";
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatUptime = (percentage: number) => {
    const days = Math.floor((percentage / 100) * 30); // Assuming 30 days
    return `${percentage.toFixed(2)}% (${days} dias)`;
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-title-section">
            <div className="page-icon">
              <SettingsIcon size={24} />
            </div>
            <div>
              <h1 className="page-title">Configurações do Sistema</h1>
              <p className="page-description">
                Gerencie configurações gerais, usuários, integrações e
                monitoramento do sistema
              </p>
            </div>
          </div>
          <div className="page-actions">
            <button className="btn btn-secondary">
              <RefreshCw size={16} />
              Atualizar
            </button>
            <button className="btn btn-primary">
              <Save size={16} />
              Salvar Alterações
            </button>
          </div>
        </div>
      </div>

      <div className="page-content">
        <div className="page-sidebar">
          <div className="sidebar-section">
            <h3>Status do Sistema</h3>
            <div className="system-health-summary">
              <div className="health-overview">
                <div
                  className="health-status-indicator"
                  style={{
                    backgroundColor: getHealthStatusColor(systemHealth.overall),
                  }}
                >
                  {getHealthStatusIcon(systemHealth.overall)}
                </div>
                <div className="health-text">
                  <div className="health-status">{systemHealth.overall}</div>
                  <div className="health-time">
                    Verificado há{" "}
                    {new Date(systemHealth.lastCheck).toLocaleTimeString()}
                  </div>
                </div>
              </div>

              <div className="health-components">
                {Object.entries(systemHealth.components).map(
                  ([component, data]) => (
                    <div key={component} className="health-component">
                      <div className="component-name">{component}</div>
                      <div className="component-status">
                        {getHealthStatusIcon(data.status)}
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>

          <div className="sidebar-section">
            <h3>Métricas Rápidas</h3>
            <div className="quick-metrics">
              <div className="quick-metric">
                <Users size={16} />
                <span className="metric-value">
                  {systemMetrics.application.activeUsers}
                </span>
                <span className="metric-label">Usuários Ativos</span>
              </div>
              <div className="quick-metric">
                <Activity size={16} />
                <span className="metric-value">
                  {systemMetrics.application.activeProjects}
                </span>
                <span className="metric-label">Projetos Ativos</span>
              </div>
              <div className="quick-metric">
                <BarChart3 size={16} />
                <span className="metric-value">
                  {systemMetrics.application.requestsPerMinute}
                </span>
                <span className="metric-label">Req/min</span>
              </div>
              <div className="quick-metric">
                <HardDrive size={16} />
                <span className="metric-value">
                  {systemMetrics.server.disk.toFixed(1)}%
                </span>
                <span className="metric-label">Uso de Disco</span>
              </div>
            </div>
          </div>

          <div className="sidebar-section">
            <h3>Navegação</h3>
            <nav className="sidebar-nav">
              <button
                className={`nav-item ${
                  activeTab === "general" ? "active" : ""
                }`}
                onClick={() => setActiveTab("general")}
              >
                <SettingsIcon size={16} />
                Geral
              </button>
              <button
                className={`nav-item ${activeTab === "llms" ? "active" : ""}`}
                onClick={() => setActiveTab("llms")}
              >
                <Zap size={16} />
                LLMs
              </button>
              <button
                className={`nav-item ${activeTab === "users" ? "active" : ""}`}
                onClick={() => setActiveTab("users")}
              >
                <Users size={16} />
                Usuários
              </button>
              <button
                className={`nav-item ${
                  activeTab === "security" ? "active" : ""
                }`}
                onClick={() => setActiveTab("security")}
              >
                <Shield size={16} />
                Segurança
              </button>
              <button
                className={`nav-item ${
                  activeTab === "integrations" ? "active" : ""
                }`}
                onClick={() => setActiveTab("integrations")}
              >
                <Link size={16} />
                Integrações
              </button>
              <button
                className={`nav-item ${
                  activeTab === "analytics" ? "active" : ""
                }`}
                onClick={() => setActiveTab("analytics")}
              >
                <BarChart3 size={16} />
                Analytics
              </button>
              <button
                className={`nav-item ${activeTab === "backup" ? "active" : ""}`}
                onClick={() => setActiveTab("backup")}
              >
                <Database size={16} />
                Backup
              </button>
              <button
                className={`nav-item ${
                  activeTab === "notifications" ? "active" : ""
                }`}
                onClick={() => setActiveTab("notifications")}
              >
                <Bell size={16} />
                Notificações
              </button>
            </nav>
          </div>
        </div>

        <div className="page-main">
          <div className="main-header">
            <h2>
              {activeTab === "general" && "Configurações Gerais"}
              {activeTab === "llms" && "Configuração de LLMs"}
              {activeTab === "users" && "Gerenciamento de Usuários"}
              {activeTab === "security" && "Configurações de Segurança"}
              {activeTab === "integrations" && "Integrações"}
              {activeTab === "analytics" && "Analytics"}
              {activeTab === "backup" && "Backup e Recuperação"}
              {activeTab === "notifications" && "Notificações"}
            </h2>
          </div>

          <div className="main-content">
            {activeTab === "general" && (
              <GeneralSettings
                settings={systemSettings}
                metrics={systemMetrics}
                health={systemHealth}
                onUpdate={handleSettingsUpdate}
              />
            )}

            {activeTab === "llms" && (
              <LLMSettings
                configurations={llmConfigurations}
                onUpdate={handleLLMUpdate}
              />
            )}

            {activeTab === "users" && (
              <UserManagement
                users={users}
                roles={[]} // Precisa adicionar mock data de roles
                onUpdateUser={handleUserUpdate}
                onDeleteUser={(userId: string) =>
                  console.log("Delete user:", userId)
                }
                onCreateUser={(user) => console.log("Create user:", user)}
                onCreateRole={(role) => console.log("Create role:", role)}
              />
            )}

            {activeTab === "security" && (
              <SecuritySettings
                securityConfig={{
                  twoFactorRequired: false,
                  sessionTimeout: 4,
                  auditLogging: true,
                  passwordPolicy: {
                    minLength: 8,
                    requireSpecialChars: true,
                    requireNumbers: true,
                    requireUppercase: true,
                    expirationDays: 90,
                  },
                  rateLimiting: {
                    enabled: true,
                    requestsPerHour: 1000,
                  },
                }}
                auditLogs={[]}
                backupConfig={backupConfig}
                onUpdateSecurity={(updates) =>
                  console.log("Update security:", updates)
                }
                onUpdateBackup={(updates) =>
                  console.log("Update backup:", updates)
                }
                onDownloadLogs={() => console.log("Download logs")}
                onClearLogs={() => console.log("Clear logs")}
              />
            )}

            {activeTab === "integrations" && (
              <IntegrationsSettings
                integrations={integrations}
                webhooks={[]} // Adicionar mock data
                apiKeys={[]} // Adicionar mock data
                onUpdateIntegration={handleIntegrationUpdate}
                onCreateWebhook={(webhook) =>
                  console.log("Create webhook:", webhook)
                }
                onCreateApiKey={(apiKey) =>
                  console.log("Create API key:", apiKey)
                }
                onDeleteWebhook={(id) => console.log("Delete webhook:", id)}
                onRevokeApiKey={(id) => console.log("Revoke API key:", id)}
              />
            )}

            {activeTab === "analytics" && (
              <AnalyticsPanel
                settings={analyticsSettings}
                metrics={systemMetrics}
              />
            )}

            {activeTab === "backup" && (
              <BackupSettings configuration={backupConfig} />
            )}

            {activeTab === "notifications" && <NotificationSettings />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
