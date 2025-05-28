// src/types/settings.ts
export enum UserRole {
    ADMIN = 'admin',
    DEVELOPER = 'developer',
    OPERATOR = 'operator',
    VIEWER = 'viewer'
  }
  
  export enum NotificationChannel {
    EMAIL = 'email',
    SLACK = 'slack',
    WEBHOOK = 'webhook',
    IN_APP = 'in_app'
  }
  
  export enum LLMProvider {
    OPENAI = 'openai',
    ANTHROPIC = 'anthropic',
    AZURE_OPENAI = 'azure_openai',
    GOOGLE = 'google',
    COHERE = 'cohere'
  }
  
  export enum BackupFrequency {
    DAILY = 'daily',
    WEEKLY = 'weekly',
    MONTHLY = 'monthly'
  }
  
  export enum LogLevel {
    ERROR = 'error',
    WARN = 'warn',
    INFO = 'info',
    DEBUG = 'debug'
  }
  
  export enum IntegrationStatus {
    CONNECTED = 'connected',
    DISCONNECTED = 'disconnected',
    ERROR = 'error',
    CONFIGURING = 'configuring'
  }
  
  export interface SystemSettings {
    id: string;
    projectName: string;
    description: string;
    domain: string;
    version: string;
    environment: 'development' | 'staging' | 'production';
    createdAt: string;
    modifiedAt: string;
    ownerId: string;
    ownerName: string;
  }
  
  export interface LLMConfiguration {
    id: string;
    provider: LLMProvider;
    name: string;
    apiKey: string;
    endpoint?: string;
    model: string;
    temperature: number;
    maxTokens: number;
    timeout: number;
    retryAttempts: number;
    isDefault: boolean;
    enabled: boolean;
    rateLimit?: {
      requestsPerMinute: number;
      tokensPerMinute: number;
    };
    createdAt: string;
    updatedAt: string;
  }
  
  export interface User {
    id: string;
    name: string;
    email: string;
    role: UserRole;
    avatar?: string;
    isActive: boolean;
    lastLogin?: string;
    permissions: string[];
    projects: string[];
    createdAt: string;
    updatedAt: string;
  }
  
  export interface UserPermissions {
    projects: {
      create: boolean;
      read: boolean;
      update: boolean;
      delete: boolean;
    };
    system: {
      settings: boolean;
      users: boolean;
      integrations: boolean;
      analytics: boolean;
      backups: boolean;
    };
    monitoring: {
      view: boolean;
      configure: boolean;
      alerts: boolean;
    };
    deployment: {
      deploy: boolean;
      rollback: boolean;
      configure: boolean;
    };
  }
  
  export interface Integration {
    id: string;
    name: string;
    type: 'llm' | 'monitoring' | 'deployment' | 'communication' | 'storage';
    provider: string;
    status: IntegrationStatus;
    endpoint?: string;
    apiKey?: string;
    configuration: Record<string, any>;
    healthCheck: {
      lastCheck: string;
      isHealthy: boolean;
      latency?: number;
      error?: string;
    };
    usage: {
      requestsToday: number;
      requestsThisMonth: number;
      quota?: number;
      cost?: number;
    };
    createdAt: string;
    updatedAt: string;
  }
  
  export interface NotificationSettings {
    id: string;
    userId?: string;
    isGlobal: boolean;
    channels: NotificationChannel[];
    preferences: {
      projectUpdates: boolean;
      deployments: boolean;
      errors: boolean;
      systemAlerts: boolean;
      weeklyReports: boolean;
    };
    emailSettings?: {
      address: string;
      verified: boolean;
    };
    slackSettings?: {
      workspace: string;
      channel: string;
      webhookUrl: string;
    };
    webhookSettings?: {
      url: string;
      secret: string;
      events: string[];
    };
  }
  
  export interface BackupConfiguration {
    id: string;
    enabled: boolean;
    frequency: BackupFrequency;
    retention: number;
    includeProjects: boolean;
    includeSettings: boolean;
    includeUsers: boolean;
    includeAnalytics: boolean;
    storageProvider: 'local' | 'aws' | 'gcp' | 'azure';
    storageConfig: Record<string, any>;
    encryptionEnabled: boolean;
    lastBackup?: string;
    nextBackup?: string;
    backupSize?: number;
    status: 'active' | 'inactive' | 'error';
  }
  
  export interface AnalyticsSettings {
    id: string;
    enabled: boolean;
    dataRetention: number; // dias
    collectUsageStats: boolean;
    collectPerformanceMetrics: boolean;
    collectErrorLogs: boolean;
    anonymizeData: boolean;
    exportEnabled: boolean;
    reportsEnabled: boolean;
    dashboardUrl?: string;
  }
  
  export interface SystemMetrics {
    timestamp: string;
    server: {
      uptime: number;
      cpu: number;
      memory: number;
      disk: number;
      network: {
        bytesIn: number;
        bytesOut: number;
      };
    };
    application: {
      activeUsers: number;
      activeProjects: number;
      requestsPerMinute: number;
      averageResponseTime: number;
      errorRate: number;
    };
    database: {
      connections: number;
      queryTime: number;
      size: number;
    };
  }
  
  export interface AuditLog {
    id: string;
    timestamp: string;
    userId: string;
    userName: string;
    action: string;
    resource: string;
    resourceId?: string;
    details: Record<string, any>;
    ipAddress: string;
    userAgent: string;
    severity: 'low' | 'medium' | 'high';
  }
  
  export interface SystemHealth {
    overall: 'healthy' | 'warning' | 'error';
    components: {
      database: {
        status: 'healthy' | 'warning' | 'error';
        latency: number;
        connections: number;
      };
      api: {
        status: 'healthy' | 'warning' | 'error';
        responseTime: number;
        errorRate: number;
      };
      integrations: {
        status: 'healthy' | 'warning' | 'error';
        healthyCount: number;
        totalCount: number;
      };
      storage: {
        status: 'healthy' | 'warning' | 'error';
        usage: number;
        available: number;
      };
    };
    lastCheck: string;
  }