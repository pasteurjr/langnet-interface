// src/types/monitoring.ts - Tipos específicos para Monitoramento via Langfuse

export enum MonitoringStatus {
    CONNECTED = 'connected',
    DISCONNECTED = 'disconnected',
    CONNECTING = 'connecting',
    ERROR = 'error',
    SYNCING = 'syncing'
  }
  
  export enum TraceStatus {
    RUNNING = 'running',
    COMPLETED = 'completed',
    ERROR = 'error',
    CANCELLED = 'cancelled'
  }
  
  export enum LogLevel {
    DEBUG = 'debug',
    INFO = 'info',
    WARNING = 'warning',
    ERROR = 'error'
  }
  
  export interface LangfuseConnection {
    id: string;
    projectId: string;
    publicKey: string;
    secretKey: string;
    host: string;
    status: MonitoringStatus;
    connectedAt?: string;
    lastSync?: string;
    settings: {
      enableTracing: boolean;
      sampleRate: number;
      bufferSize: number;
      flushInterval: number;
      enableMetrics: boolean;
      enableAlerts: boolean;
    };
  }
  
  export interface TraceData {
    id: string;
    sessionId: string;
    name: string;
    input?: any;
    output?: any;
    metadata?: Record<string, any>;
    startTime: string;
    endTime?: string;
    duration?: number;
    status: TraceStatus;
    level: 'DEFAULT' | 'DEBUG' | 'WARNING' | 'ERROR';
    statusMessage?: string;
    version?: string;
    release?: string;
    userId?: string;
    userProps?: Record<string, any>;
    tags?: string[];
    public: boolean;
  }
  
  export interface SpanData {
    id: string;
    traceId: string;
    parentSpanId?: string;
    name: string;
    input?: any;
    output?: any;
    metadata?: Record<string, any>;
    startTime: string;
    endTime?: string;
    duration?: number;
    level: 'DEFAULT' | 'DEBUG' | 'WARNING' | 'ERROR';
    statusMessage?: string;
    version?: string;
    tags?: string[];
  }
  
  export interface GenerationData {
    id: string;
    traceId: string;
    name: string;
    model: string;
    modelParameters?: {
      temperature?: number;
      maxTokens?: number;
      topP?: number;
      frequencyPenalty?: number;
      presencePenalty?: number;
    };
    prompt?: any;
    completion?: string;
    usage?: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
    };
    metadata?: Record<string, any>;
    startTime: string;
    endTime?: string;
    duration?: number;
    level: 'DEFAULT' | 'DEBUG' | 'WARNING' | 'ERROR';
    statusMessage?: string;
    version?: string;
    tags?: string[];
  }
  
  export interface MonitoringMetrics {
    totalTraces: number;
    totalSpans: number;
    totalGenerations: number;
    totalCost: number;
    totalTokens: number;
    averageLatency: number;
    errorRate: number;
    successRate: number;
    timeRange: {
      start: string;
      end: string;
    };
  }
  
  export interface SystemMetrics {
    timestamp: string;
    cpu: number;
    memory: number;
    disk: number;
    network: {
      bytesIn: number;
      bytesOut: number;
    };
    activeAgents: number;
    queueDepth: number;
    requestsPerMinute: number;
    responseTime: number;
  }
  
  export interface AlertRule {
    id: string;
    name: string;
    description: string;
    condition: string;
    threshold: number;
    enabled: boolean;
    channels: ('email' | 'slack' | 'webhook')[];
    lastTriggered?: string;
    triggerCount: number;
  }
  
  export interface AlertEvent {
    id: string;
    ruleId: string;
    ruleName: string;
    message: string;
    severity: 'info' | 'warning' | 'critical';
    triggeredAt: string;
    resolvedAt?: string;
    metadata?: Record<string, any>;
  }
  
  export interface MonitoringDashboard {
    id: string;
    projectId: string;
    name: string;
    description: string;
    connection: LangfuseConnection;
    metrics: MonitoringMetrics;
    systemMetrics: SystemMetrics[];
    recentTraces: TraceData[];
    recentSpans: SpanData[];
    recentGenerations: GenerationData[];
    alertRules: AlertRule[];
    recentAlerts: AlertEvent[];
    isRealTime: boolean;
    refreshInterval: number;
    timeRange: {
      start: string;
      end: string;
      preset: '1h' | '24h' | '7d' | '30d' | 'custom';
    };
  }