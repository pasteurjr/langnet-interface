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

// Tipos para Tarefas
export interface Task {
  id: string;
  name: string;
  description: string;
  inputs: TaskIO[];
  outputs: TaskIO[];
  steps: TaskStep[];
  agentId: string;
  projectId: string;
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