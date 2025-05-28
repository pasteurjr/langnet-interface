// src/types/deployment.ts
export enum DeploymentStatus {
    IDLE = 'idle',
    BUILDING = 'building',
    TESTING = 'testing',
    DEPLOYING = 'deploying',
    DEPLOYED = 'deployed',
    FAILED = 'failed',
    ROLLING_BACK = 'rolling_back'
  }
  
  export enum DeploymentTarget {
    LOCAL = 'local',
    DOCKER = 'docker',
    KUBERNETES = 'kubernetes',
    AWS = 'aws',
    GCP = 'gcp',
    AZURE = 'azure'
  }
  
  export enum CloudProvider {
    AWS = 'aws',
    GCP = 'gcp',
    AZURE = 'azure',
    DIGITAL_OCEAN = 'digital_ocean',
    HEROKU = 'heroku'
  }
  
  export enum InstanceType {
    MICRO = 'micro',
    SMALL = 'small',
    MEDIUM = 'medium',
    LARGE = 'large',
    XLARGE = 'xlarge'
  }
  
  export enum ScalingType {
    FIXED = 'fixed',
    AUTO = 'auto',
    MANUAL = 'manual'
  }
  
  export interface DeploymentConfig {
    id: string;
    name: string;
    target: DeploymentTarget;
    cloudProvider?: CloudProvider;
    region: string;
    instanceType: InstanceType;
    scalingType: ScalingType;
    minInstances: number;
    maxInstances: number;
    environmentVariables: Record<string, string>;
    secrets: Record<string, string>;
    domain?: string;
    ssl: boolean;
    monitoring: boolean;
    logging: boolean;
    backup: boolean;
    createdAt: string;
    updatedAt: string;
  }
  
  export interface DeploymentHistory {
    id: string;
    version: string;
    status: DeploymentStatus;
    deployedAt: string;
    deployedBy: string;
    duration: number;
    commit?: string;
    changes: string[];
    rollbackAvailable: boolean;
    logs: DeploymentLog[];
  }
  
  export interface DeploymentLog {
    id: string;
    timestamp: string;
    level: 'info' | 'warn' | 'error' | 'debug';
    source: string;
    message: string;
    metadata?: Record<string, any>;
  }
  
  export interface InfrastructureResource {
    id: string;
    type: 'loadbalancer' | 'database' | 'cache' | 'storage' | 'network';
    name: string;
    status: 'active' | 'inactive' | 'error';
    provider: CloudProvider;
    region: string;
    configuration: Record<string, any>;
    cost: number;
    createdAt: string;
  }
  
  export interface PipelineStage {
    id: string;
    name: string;
    status: 'pending' | 'running' | 'success' | 'failed' | 'skipped';
    startTime?: string;
    endTime?: string;
    duration?: number;
    logs: string[];
    artifacts?: string[];
  }
  
  export interface CiCdPipeline {
    id: string;
    name: string;
    status: DeploymentStatus;
    currentStage?: string;
    stages: PipelineStage[];
    triggeredBy: string;
    triggeredAt: string;
    completedAt?: string;
    totalDuration?: number;
    branch: string;
    commit: string;
    version: string;
  }
  
  export interface EnvironmentMetrics {
    timestamp: string;
    cpu: number;
    memory: number;
    disk: number;
    network: {
      bytesIn: number;
      bytesOut: number;
      requestsPerSecond: number;
    };
    activeInstances: number;
    healthChecks: {
      total: number;
      passing: number;
      failing: number;
    };
    responseTime: number;
    errorRate: number;
    uptime: number;
  }
  
  export interface SecuritySettings {
    firewall: {
      enabled: boolean;
      rules: Array<{
        id: string;
        name: string;
        protocol: 'tcp' | 'udp' | 'icmp';
        port: number | string;
        source: string;
        action: 'allow' | 'deny';
      }>;
    };
    ssl: {
      enabled: boolean;
      certificate?: string;
      autoRenewal: boolean;
    };
    accessControl: {
      enabled: boolean;
      whitelist: string[];
      basicAuth: boolean;
      oauth: boolean;
    };
    secrets: {
      encrypted: boolean;
      vault: string;
      rotationEnabled: boolean;
    };
  }
  
  export interface BackupConfig {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    retention: number;
    storage: CloudProvider;
    encryption: boolean;
    lastBackup?: string;
    nextBackup?: string;
    backupSize?: number;
  }
  
  export interface DeploymentEnvironment {
    id: string;
    name: string;
    type: 'development' | 'staging' | 'production';
    status: 'active' | 'inactive' | 'maintenance';
    config: DeploymentConfig;
    currentVersion?: string;
    url?: string;
    lastDeployment?: DeploymentHistory;
    metrics: EnvironmentMetrics;
    security: SecuritySettings;
    backup: BackupConfig;
    resources: InfrastructureResource[];
    createdAt: string;
    updatedAt: string;
  }