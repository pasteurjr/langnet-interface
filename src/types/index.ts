// Definições de tipos para o sistema LangNet

// Tipos para Projetos
export interface Project {
  id: string;
  name: string;
  description: string;
  domain: string;
  createdAt: string;
  updatedAt: string;
  status: ProjectStatus;
  progress: number;
}

export enum ProjectStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

// Tipos para Agentes
// src/types/index.ts
export interface Agent {
  id: string;
  name: string;
  role: string;
  goal: string;
  backstory: string;
  tools: string[];
  verbose: boolean;
  allow_delegation: boolean;
  allow_code_execution?: boolean;
  max_iter?: number;
  max_rpm?: number;
  status: AgentStatus;
  createdAt: string;
  updatedAt: string;
}



export interface TaskIO {
  name: string;
  type: string;
  description: string;
}

export interface TaskStep {
  id: string;
  description: string;
  order: number;
}

// Tipos para Redes de Petri
export interface PetriNet {
  id: string;
  name: string;
  places: PetriPlace[];
  transitions: PetriTransition[];
  arcs: PetriArc[];
  projectId: string;
}

export interface PetriPlace {
  id: string;
  name: string;
  tokens: number;
  position: Position;
}

export interface PetriTransition {
  id: string;
  name: string;
  taskId?: string;
  agentId?: string;
  position: Position;
}

export interface PetriArc {
  id: string;
  sourceId: string;
  targetId: string;
  weight: number;
}

export interface Position {
  x: number;
  y: number;
}

// Tipos para UI
export interface MenuItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: MenuItem[];
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
  read: boolean;
}

// Tipos para Monitoramento
export interface Metric {
  id: string;
  name: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface LogEntry {
  id: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  timestamp: string;
  source: string;
  metadata?: Record<string, any>;
}

// src/types/index.ts (ADICIONAR ao arquivo existente)

export enum AgentStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DRAFT = 'draft'
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  goal: string;
  backstory: string;
  tools: string[];
  verbose: boolean;
  allow_delegation: boolean;
  allow_code_execution?: boolean;
  max_iter?: number;
  max_rpm?: number;
  status: AgentStatus;
  createdAt: string;
  updatedAt: string;
}

export interface Tool {
  id: string;
  name: string;
  description: string;
  category: string;
}

// src/types/index.ts (ADICIONAR ao arquivo existente)

export enum TaskStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DRAFT = 'draft'
}



export interface Task {
  id: string;
  projectId: string;
  name: string;
  description: string;
  expected_output: string;
  agentId: string; // ID do agente responsável
  agent: string; // Alias para compatibilidade
  context: string[]; // IDs de outras tarefas que servem como contexto
  tools: string[];
  human_input: boolean;
  async_execution: boolean;
  output_json?: string;
  output_file?: string;
  inputs: TaskIO[];
  outputs: TaskIO[];
  steps: TaskStep[];
  status: TaskStatus;
  createdAt: string;
  updatedAt: string;
}

// Adicionar ao arquivo src/types/index.ts

export enum DocumentStatus {
  UPLOADED = 'uploaded',
  ANALYZING = 'analyzing',
  ANALYZED = 'analyzed',
  ERROR = 'error'
}

export interface ExtractedEntity {
  name: string;
  type: 'actor' | 'system' | 'process' | 'rule' | 'concept';
  description: string;
  confidence: number;
}

export interface RequirementItem {
  id: string;
  type: 'functional' | 'non_functional' | 'business_rule' | 'constraint';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  source: string; // Nome do documento de origem
}

// Backend API Requirement response
export interface Requirement {
  id: number;
  project_id: number;
  document_id: number;
  requirement_id: string;
  description: string;
  type: 'functional' | 'non_functional' | 'business_rule';
  priority: 'high' | 'medium' | 'low';
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  creator_name: string;
}

export interface AnalysisIssue {
  type: 'warning' | 'error' | 'suggestion';
  title: string;
  description: string;
  documentName?: string;
  location?: string;
}

export interface Document {
  id: string;
  projectId: string;
  name: string;
  originalName: string;
  size: number;
  type: string; // MIME type
  uploadedAt: string;
  status: DocumentStatus;
  url?: string;
  extractedEntities: ExtractedEntity[];
  requirements: RequirementItem[];
  analysisIssues: AnalysisIssue[];
  analysisInstructions?: string;
  analysisProgress?: number;
  analysisResults?: {
    summary: string;
    keyFindings: string[];
    recommendedActions: string[];
  };
  enableWebResearch?: boolean;
  executionId?: string;
}

// Adicionar ao arquivo src/types/index.ts

export enum YamlFileType {
  AGENTS = 'agents',
  TASKS = 'tasks',
  TOOLS = 'tools',
  CONFIG = 'config'
}

export enum YamlStatus {
  GENERATED = 'generated',
  MODIFIED = 'modified',
  VALIDATED = 'validated',
  ERROR = 'error'
}

export interface ValidationIssue {
  line: number;
  column?: number;
  type: 'error' | 'warning' | 'suggestion';
  message: string;
  severity: 'high' | 'medium' | 'low';
  code?: string;
}

export interface YamlFile {
  id: string;
  projectId: string;
  name: string;
  type: YamlFileType;
  content: string;
  status: YamlStatus;
  lastModified: string;
  lastGenerated: string;
  version: string;
  validationIssues: ValidationIssue[];
  generationInstructions?: string;
  isAutoGenerated: boolean;
  sourceFiles?: string[]; // IDs dos documentos/specs que geraram este YAML
  metadata: {
    agentCount?: number;
    taskCount?: number;
    toolCount?: number;
    configItems?: number;
  };
}
export interface YamlValidationResult {
  type: 'error' | 'warning' | 'info' | 'success';
  message: string;
  line?: number;
  column?: number;
}

export interface YamlGenerationRequest {
  projectId: string;
  fileTypes: YamlFileType[];
  instructions?: string;
  includeComments: boolean;
  formatStyle: 'compact' | 'readable' | 'detailed';
  validationLevel: 'basic' | 'strict' | 'comprehensive';
}
export interface YamlGenerationConfig {
  includeAgents: boolean;
  includeTasks: boolean;
  includeTools: boolean;
  includeConfig: boolean;
  additionalInstructions?: string;
}

// src/types/specification.ts - Tipos específicos para Especificação Funcional

export enum SpecificationStatus {
  DRAFT = 'draft',
  GENERATED = 'generated',
  REVIEWING = 'reviewing',
  APPROVED = 'approved',
  NEEDS_REVISION = 'needs_revision'
}

export enum SpecificationSectionType {
  INTRODUCTION = 'introduction',
  OVERVIEW = 'overview',
  FUNCTIONAL_REQUIREMENTS = 'functional_requirements',
  NON_FUNCTIONAL_REQUIREMENTS = 'non_functional_requirements',
  DATA_MODEL = 'data_model',
  USER_INTERFACE = 'user_interface',
  INTEGRATION = 'integration',
  BUSINESS_RULES = 'business_rules',
  GLOSSARY = 'glossary'
}

export interface SpecificationSection {
  id: string;
  type: SpecificationSectionType;
  title: string;
  content: string;
  order: number;
  isRequired: boolean;
  isGenerated: boolean;
  lastModified: string;
  wordCount: number;
  completeness: number; // 0-100%
  issues: SpecificationIssue[];
}

export interface SpecificationIssue {
  id: string;
  type: 'missing_info' | 'inconsistency' | 'clarity' | 'completeness' | 'validation';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  sectionId: string;
  position?: {
    line: number;
    column: number;
  };
  suggestions?: string[];
  isResolved: boolean;
}

export interface FunctionalRequirement {
  id: string;
  code: string; // FR001, FR002, etc.
  title: string;
  description: string;
  priority: 'must_have' | 'should_have' | 'could_have' | 'wont_have';
  complexity: 'low' | 'medium' | 'high';
  source: string; // documento de origem
  dependencies: string[]; // IDs de outros requisitos
  acceptanceCriteria: string[];
  category: string;
  status: RequirementStatus;
}

export interface NonFunctionalRequirement {
  id: string;
  code: string; // NFR001, NFR002, etc.
  title: string;
  description: string;
  category: 'performance' | 'security' | 'usability' | 'reliability' | 'scalability' | 'maintainability';
  metric: string;
  targetValue: string;
  priority: 'must_have' | 'should_have' | 'could_have' | 'wont_have';
  testMethod: string;
  status: RequirementStatus;
}

export enum RequirementStatus {
  IDENTIFIED = 'identified',
  DEFINED = 'defined',
  APPROVED = 'approved',
  IMPLEMENTED = 'implemented',
  TESTED = 'tested',
  REJECTED = 'rejected'
}

export interface DataEntity {
  id: string;
  name: string;
  description: string;
  attributes: DataAttribute[];
  relationships: DataRelationship[];
  businessRules: string[];
}

export interface DataAttribute {
  id: string;
  name: string;
  type: string;
  isRequired: boolean;
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  description: string;
  constraints: string[];
  defaultValue?: string;
}

export interface DataRelationship {
  id: string;
  sourceEntityId: string;
  targetEntityId: string;
  type: 'one_to_one' | 'one_to_many' | 'many_to_many';
  description: string;
  isRequired: boolean;
}

export interface UserStory {
  id: string;
  title: string;
  description: string;
  asA: string; // Como um...
  iWant: string; // Eu quero...
  soThat: string; // Para que...
  acceptanceCriteria: string[];
  priority: number;
  storyPoints: number;
  epic?: string;
  theme?: string;
  relatedRequirements: string[];
}

export interface BusinessRule {
  id: string;
  code: string; // BR001, BR002, etc.
  name: string;
  description: string;
  type: 'constraint' | 'computation' | 'inference' | 'action_enabler';
  condition: string;
  action: string;
  priority: 'high' | 'medium' | 'low';
  source: string;
  relatedRequirements: string[];
  examples: string[];
}

export interface SpecificationDocument {
  id: string;
  projectId: string;
  title: string;
  version: string;
  status: SpecificationStatus;
  createdAt: string;
  updatedAt: string;
  lastGeneratedAt?: string;
  sections: SpecificationSection[];
  functionalRequirements: FunctionalRequirement[];
  nonFunctionalRequirements: NonFunctionalRequirement[];
  dataEntities: DataEntity[];
  userStories: UserStory[];
  businessRules: BusinessRule[];
  metadata: {
    totalWordCount: number;
    totalPages: number;
    completeness: number; // 0-100%
    qualityScore: number; // 0-100%
    lastReviewDate?: string;
    reviewers: string[];
    approvers: string[];
  };
  generationConfig: {
    includeDataModel: boolean;
    includeUserStories: boolean;
    includeBusinessRules: boolean;
    includeGlossary: boolean;
    detailLevel: 'basic' | 'detailed' | 'comprehensive';
    targetAudience: 'technical' | 'business' | 'mixed';
    templateStyle: 'ieee' | 'agile' | 'custom';
  };
}

export interface SpecificationGenerationRequest {
  projectId: string;
  documentIds: string[]; // documentos fonte
  includeDataModel: boolean;
  includeUserStories: boolean;
  includeBusinessRules: boolean;
  includeGlossary: boolean;
  detailLevel: 'basic' | 'detailed' | 'comprehensive';
  targetAudience: 'technical' | 'business' | 'mixed';
  templateStyle: 'ieee' | 'agile' | 'custom';
  customInstructions?: string;
  sectionsToGenerate: SpecificationSectionType[];
}

export interface SpecificationValidationResult {
  overallScore: number; // 0-100%
  completeness: number; // 0-100%
  consistency: number; // 0-100%
  clarity: number; // 0-100%
  traceability: number; // 0-100%
  issues: SpecificationIssue[];
  recommendations: string[];
  missingElements: string[];
}

export interface SpecificationComment {
  id: string;
  sectionId: string;
  authorId: string;
  authorName: string;
  content: string;
  type: 'comment' | 'suggestion' | 'approval' | 'concern';
  createdAt: string;
  isResolved: boolean;
  resolvedBy?: string;
  resolvedAt?: string;
  parentCommentId?: string; // para respostas
}

export interface SpecificationVersion {
  id: string;
  version: string;
  createdAt: string;
  createdBy: string;
  changes: string[];
  isActive: boolean;
  documentSnapshot: SpecificationDocument;
}
export * from './codeGeneration';
// Re-export dos tipos de geração de código para facilitar importação
export {
  CodeGenerationStatus,
  FrameworkType,
  MemorySystemType,
  LLMProviderType,
  PythonVersionType,
  DeploymentTargetType,
  type CodeFile,
  type CodeValidationIssue,
  type PetriNetImplementation,
  type AgentImplementation,
  type TaskImplementation,
  type ToolImplementation,
  type LLMConfiguration,
  type MemoryConfiguration,
  type ExecutionConfiguration,
  type TestConfiguration,
  type BuildConfiguration,
  type DeploymentConfiguration,
  type MonitoringIntegration,
  type CodeGenerationRequest,
  type CodeGenerationResult,
  type ProjectStructure,
  type BuildLogEntry,
  type TestResults,
  type DeploymentInfo,
  type GenerationMetrics,
  type CodeExecutionSession,
  type ExecutionLogEntry,
  type ExecutionMetrics,
  type PetriNetExecutionState
} from './codeGeneration';

export * from './monitoring';
export {
  MonitoringStatus,
  TraceStatus,
  LogLevel,
  type LangfuseConnection,
  type TraceData,
  type SpanData,
  type GenerationData,
  type MonitoringMetrics,
  type SystemMetrics,
  type AlertRule,
  type AlertEvent,
  type MonitoringDashboard
} from './monitoring';

// Exports de deployment
export * from './deployment';

// Adicionar exports dos tipos de settings
export * from './settings';

// src/types/index.ts - ADICIONAR AO ARQUIVO EXISTENTE

// ========================
// TIPOS MCP COMPLETOS
// ========================

// Configuração de Servidor MCP

// Credenciais de Autenticação
export interface McpCredentials {
  type: 'api_key' | 'oauth' | 'certificate' | 'basic_auth';
  apiKey?: string;
  clientId?: string;
  clientSecret?: string;
  certificate?: string;
  username?: string;
  password?: string;
  scope?: string[];
}

// Configuração de Segurança
export interface McpSecurityConfig {
  tls: boolean;
  validateCertificates: boolean;
  allowedIPs?: string[];
  rateLimiting?: {
    requestsPerMinute: number;
    burstSize: number;
  };
  encryption?: {
    algorithm: string;
    keyRotation: boolean;
  };
}

// Circuit Breaker Configuration
export interface McpCircuitBreakerConfig {
  enabled: boolean;
  failureThreshold: number;
  timeoutMs: number;
  resetTimeoutMs: number;
  monitoringEnabled: boolean;
}

// Serviço MCP
// Corrigir McpServer - adicionar campos faltantes
export interface McpServer {
  id: string;
  name: string;
  url: string;
  status: 'connected' | 'disconnected' | 'error' | 'connecting' | 'online' | 'offline' | 'local';
  type?: 'production' | 'staging' | 'development';
  version?: string;
  description?: string;
  lastPing?: string;
  responseTime?: number;
  services?: McpService[];
  credentials?: McpCredentials;
  security?: McpSecurityConfig;
  circuitBreaker?: McpCircuitBreakerConfig;
  // Campos adicionais que estavam sendo usados:
  provider?: string;
  latency?: number;
  uptime?: number;
  lastHealthCheck?: string;
}

// Corrigir McpService - adicionar campos faltantes
export interface McpService {
  id: string;
  name: string;
  category: McpServiceCategory;
  version: string;
  description: string;
  serverId?: string;
  endpoints: string[] | McpEndpoint[]; // Aceitar tanto string[] quanto McpEndpoint[]
  status: 'active' | 'inactive' | 'deprecated' | 'maintenance' | 'up' | 'down' | 'slow';
  compatibility?: McpCompatibility;
  performance?: McpPerformanceMetrics;
  documentation?: string;
  tags?: string[];
  dependencies?: string[];
  // Campos adicionais que estavam sendo usados:
  provider?: string;
  usage?: 'high' | 'medium' | 'low' | 'none';
  capabilities?: string[];
  rateLimits?: {
    requestsPerMinute: number;
    requestsPerHour: number;
  };
  sla?: {
    uptime: number;
    responseTime: number;
  };
}



export type McpServiceCategory = 
  | 'authentication'
  | 'data_storage' 
  | 'ml_services'
  | 'analytics'
  | 'communication'
  | 'file_management'
  | 'workflow'
  | 'integration'
  | 'monitoring'
  | 'security'
  | 'custom'
  | 'auth'      // Valores adicionais usados nas páginas
  | 'storage'
  | 'ai'
  | 'other';
// Endpoint de Serviço
export interface McpEndpoint {
  id: string;
  name: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  description: string;
  parameters?: McpParameter[];
  responses?: McpResponse[];
  authentication: boolean;
  rateLimit?: {
    limit: number;
    window: string;
  };
}

// Parâmetros de Endpoint
export interface McpParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required: boolean;
  description: string;
  example?: any;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    enum?: string[];
  };
}

// Respostas de Endpoint
export interface McpResponse {
  statusCode: number;
  description: string;
  schema?: any;
  example?: any;
}

// Compatibilidade de Versões
export interface McpCompatibility {
  minVersion: string;
  maxVersion?: string;
  deprecated: boolean;
  breakingChanges?: string[];
  migrationGuide?: string;
}

// Métricas de Performance
export interface McpPerformanceMetrics {
  averageResponseTime: number;
  successRate: number;
  requestsPerMinute: number;
  errorRate: number;
  uptime: number;
  lastUpdated: string;
}

// Configuração Global MCP
export interface McpGlobalConfig {
  discoveryEnabled: boolean;
  discoveryInterval: number;
  maxConcurrentConnections?: number;
  defaultTimeout: number;
  retryAttempts: number;
  retryDelay?: number;
  healthCheckInterval: number;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
  cache?: McpCacheConfig;
  monitoring?: McpMonitoringConfig;
  // Campos adicionais que estavam sendo usados:
  maxRetryAttempts?: number;
  circuitBreakerEnabled?: boolean;
  circuitBreakerThreshold?: number;
  rateLimitDefault?: number;
  tlsVersion?: string;
  discoveryProtocol?: string;
  serviceCacheTtl?: number;
}

// Configuração de Cache
export interface McpCacheConfig {
  enabled: boolean;
  ttl: number;
  maxSize: number;
  strategy: 'lru' | 'fifo' | 'lfu';
  compression: boolean;
}

// Configuração de Monitoramento
export interface McpMonitoringConfig {
  enabled: boolean;
  metrics: string[];
  alerting: {
    enabled: boolean;
    thresholds: {
      responseTime: number;
      errorRate: number;
      uptime: number;
    };
    channels: ('email' | 'slack' | 'webhook')[];
  };
  tracing: {
    enabled: boolean;
    sampleRate: number;
  };
}

// Configuração de Projeto MCP
export interface McpProjectConfig {
  projectId: string;
  enabledServices: string[];
  serviceMappings: McpServiceMappingSimple[]; // Usar a versão simples
  syncRules: {
    frequency: number;
    conflictResolution: 'merge_local' | 'merge_remote' | 'local_wins' | 'remote_wins' | 'manual';
    retryPolicy: {
      maxAttempts: number;
      backoffStrategy: 'linear' | 'exponential';
    };
    batchSize: number;
    compressionEnabled: boolean;
    domainRules: Record<string, string>;
  };
  exposedEndpoints?: McpExposedEndpoint[];
  namespaceIsolation?: boolean;
  namespace?: string;
  dataRetention?: {
    enabled: boolean;
    days: number;
  };
  // Campos adicionais que estavam sendo usados:
  isolationNamespace?: string;
  customEndpoints?: McpCustomEndpoint[];
}

// Mapeamento de Serviço
export interface McpServiceMapping {
  id: string;
  serviceId: string;
  localModel: string;
  remoteModel: string;
  transformations: McpTransformation[];
  bidirectional: boolean;
  conflictResolution: McpConflictResolution;
  enabled: boolean;
}

// Transformação de Dados
export interface McpTransformation {
  field: string;
  type: 'rename' | 'format' | 'calculate' | 'filter' | 'aggregate';
  source: string;
  target: string;
  expression?: string;
  conditions?: McpCondition[];
}

// Condições para Transformações
export interface McpCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'greater' | 'less' | 'contains' | 'regex';
  value: any;
}

// Resolução de Conflitos
export interface McpConflictResolution {
  strategy: 'local_wins' | 'remote_wins' | 'newest_wins' | 'manual' | 'merge';
  customLogic?: string;
  notifyOnConflict: boolean;
}

// Regras de Sincronização
export interface McpSyncRule {
  id: string;
  name: string;
  sourceType: 'local' | 'remote';
  targetType: 'local' | 'remote';
  schedule: McpSyncSchedule;
  filters: McpSyncFilter[];
  enabled: boolean;
  lastRun?: string;
  nextRun?: string;
  status: 'idle' | 'running' | 'success' | 'error';
}

// Agendamento de Sincronização
export interface McpSyncSchedule {
  type: 'immediate' | 'interval' | 'cron';
  interval?: number; // em minutos
  cronExpression?: string;
  timezone?: string;
}

// Filtros de Sincronização
export interface McpSyncFilter {
  field: string;
  operator: 'equals' | 'not_equals' | 'greater' | 'less' | 'contains' | 'in' | 'not_in';
  value: any;
  logicalOperator?: 'AND' | 'OR';
}

// Endpoint Exposto
export interface McpExposedEndpoint {
  id: string;
  name: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  description: string;
  authentication: boolean;
  rateLimit?: {
    requestsPerMinute: number;
    requestsPerHour: number;
  };
  enabled: boolean;
  handler: string; // referência à função/classe que processa
  documentation?: string;
}

// Status de Conexão MCP
export interface McpConnectionStatus {
  serverId: string;
  status: 'connected' | 'disconnected' | 'error' | 'connecting';
  lastAttempt: string;
  lastSuccess?: string;
  errorMessage?: string;
  connectionCount: number;
  activeRequests: number;
  queuedRequests: number;
}

// Estatísticas de Descoberta
export interface McpDiscoveryStats {
  totalServers: number;
  connectedServers: number;
  totalServices: number;
  activeServices: number;
  lastDiscovery: string;
  discoveryDuration: number;
  errors: McpDiscoveryError[];
}

// Erros de Descoberta
export interface McpDiscoveryError {
  serverId: string;
  serverName: string;
  error: string;
  timestamp: string;
  resolved: boolean;
}

// Log de Atividade MCP
export interface McpActivityLog {
  id: string;
  timestamp: string;
  type: 'connection' | 'sync' | 'error' | 'config_change' | 'service_call';
  serverId?: string;
  serviceId?: string;
  message: string;
  details?: any;
  level: 'info' | 'warn' | 'error' | 'debug';
}

// Configuração de Exportação/Importação
export interface McpExportConfig {
  includeCredentials: boolean;
  includePerformanceData: boolean;
  includeProjectConfigs: boolean;
  format: 'json' | 'yaml' | 'xml';
  encryption: boolean;
}

// Dados de Exportação
export interface McpExportData {
  version: string;
  timestamp: string;
  servers: McpServer[];
  globalConfig: McpGlobalConfig;
  projectConfigs?: McpProjectConfig[];
  checksum: string;
}

// Estado da Interface MCP
export interface McpUIState {
  selectedServer?: string;
  selectedService?: string;
  activeTab: 'servers' | 'services' | 'config' | 'logs' | 'monitoring';
  filters: {
    serverStatus?: string[];
    serviceCategory?: string[];
    searchTerm?: string;
  };
  loading: boolean;
  errors: string[];
}

// Props para Componentes MCP
export interface McpServerFormProps {
  server?: McpServer;
  onSave: (server: McpServer) => void;
  onCancel: () => void;
}

export interface McpServiceListProps {
  services: McpService[];
  onServiceSelect: (service: McpService) => void;
  onServiceToggle: (serviceId: string, enabled: boolean) => void;
  selectedServices: string[];
}

export interface McpConnectionPanelProps {
  connections: McpConnectionStatus[];
  onRefresh: () => void;
  onDisconnect: (serverId: string) => void;
  onConnect: (serverId: string) => void;
}

// Hooks Props
export interface UseMcpConfigProps {
  projectId?: string;
}

export interface UseMcpServicesProps {
  serverId?: string;
  category?: McpServiceCategory;
  enabled?: boolean;
}

// ADICIONAR AO FINAL DO ARQUIVO src/types/index.ts
// ========================
// TIPOS MCP FALTANTES
// ========================

// Conexão MCP (usado em McpServiceDiscoveryPage)
export interface McpConnection {
  id: string;
  serviceId: string;
  serviceName: string;
  status: 'connected' | 'disconnected' | 'error' | 'connecting';
  latency: number;
  lastActivity: string;
  requestsPerHour: number;
  errorRate: number;
}

// Status de saúde MCP (usado em McpGlobalConfigPage)
export interface McpHealthStatus {
  overall: 'healthy' | 'warning' | 'critical';
  services: Record<string, string>;
  connections: {
    total: number;
    active: number;
    errors: number;
  };
  performance: {
    avgLatency: number;
    throughput: number;
    errorRate: number;
  };
}

// Resultado da descoberta (usado em McpGlobalConfigPage e McpServiceDiscoveryPage)
export interface McpDiscoveryResult {
  totalServices: number;
  onlineServices: number;
  lastScan: string;
  networkHealth: number;
  avgLatency: number;
  servicesByCategory: Record<string, number>;
  usageStats: Record<string, {
    projectsUsing: number;
    avgLoad: number;
    peakUsagePerDay: number;
  }>;
}

// Endpoint customizado (usado em McpProjectIntegrationPage)
export interface McpCustomEndpoint {
  id: string;
  name: string;
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  status: 'active' | 'inactive' | 'testing';
  clientsConnected: number;
  requestsPerHour: number;
  authentication: 'none' | 'api_key' | 'bearer_token' | 'oauth';
  rateLimiting: {
    enabled: boolean;
    requestsPerMinute: number;
    requestsPerHour?: number;
  };
  monitoring: {
    enabled: boolean;
    successRate: number;
    avgResponseTime: number;
  };
}

// Estender interfaces existentes com campos que estavam faltando

// Campos adicionais para McpServer
export interface McpServerExtended extends McpServer {
  provider?: string;
  latency?: number;
  uptime?: number;
  lastHealthCheck?: string;
}

// Campos adicionais para McpService
export interface McpServiceExtended extends McpService {
  provider?: string;
  usage?: 'high' | 'medium' | 'low' | 'none';
  capabilities?: string[];
  rateLimits?: {
    requestsPerMinute: number;
    requestsPerHour: number;
  };
  sla?: {
    uptime: number;
    responseTime: number;
  };
  dependencies?: string[];
}

// Campos adicionais para McpGlobalConfig
export interface McpGlobalConfigExtended extends McpGlobalConfig {
  tlsVersion?: string;
  discoveryProtocol?: string;
  serviceCacheTtl?: number;
  circuitBreakerThreshold?: number;
}

// Status de servidor específico (usado nas páginas)
export type McpServerStatus = 'online' | 'offline' | 'local' | 'error' | 'connected' | 'disconnected' | 'connecting';

// Status de serviço específico (usado nas páginas)
export type McpServiceStatus = 'up' | 'down' | 'slow' | 'maintenance' | 'active' | 'inactive' | 'deprecated';

// Atualizar a interface McpProjectConfig com estrutura correta
export interface McpProjectConfigExtended extends Omit<McpProjectConfig, 'syncRules'> {
  syncRules: {
    frequency: number;
    conflictResolution: 'merge_local' | 'merge_remote' | 'local_wins' | 'remote_wins' | 'manual';
    retryPolicy: {
      maxAttempts: number;
      backoffStrategy: 'linear' | 'exponential';
    };
    batchSize: number;
    compressionEnabled: boolean;
    domainRules: Record<string, string>;
  };
  isolationNamespace: string;
  customEndpoints: McpCustomEndpoint[];
}

// Mapeamento de serviço simples (usado em McpProjectIntegrationPage)
export interface McpServiceMappingSimple {
  localModel: string;
  mcpService: string;
  endpoint: string;
  format: string;
}
// Dados para novo servidor (usado em McpGlobalConfigPage)
export interface McpNewServerData {
  name: string;
  url: string;
  provider: string;
  description: string;
}


