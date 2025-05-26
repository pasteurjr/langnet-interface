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