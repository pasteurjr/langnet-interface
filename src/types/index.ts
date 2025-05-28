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