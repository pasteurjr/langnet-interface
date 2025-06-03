// src/types/agentChat.ts
export interface Agent {
    id: string;
    name: string;
    role: string;
    status: 'active' | 'inactive' | 'busy' | 'error';
    load: number; // 0-100%
    queue: number;
    lastActivity: string;
    type: 'customer_service' | 'technical_support' | 'sentiment_analyzer' | 'response_generator' | 'escalation_manager' | 'learning_assistant';
  }
  
  export interface ChatMessage {
    id: string;
    timestamp: string;
    sender: 'user' | 'agent' | 'system';
    agentId?: string;
    agentName?: string;
    content: string;
    type: 'message' | 'command' | 'system_notification' | 'debug_info';
    metadata?: {
      reasoning?: string[];
      confidence?: number;
      processingTime?: number;
      tokens?: number;
    };
  }
  
  export interface AgentPerformanceMetrics {
    successRate: number;
    avgResponseTime: number;
    tokensUsed: number;
    requestsPerHour: number;
    errorRate: number;
    confidence: number;
  }
  
  export interface AgentInternalState {
    currentTask?: string;
    memoryUsage: number;
    contextWindow: {
      used: number;
      total: number;
    };
    lastDecision?: {
      description: string;
      confidence: number;
    };
    reasoningTrace: string[];
    performance: AgentPerformanceMetrics;
  }
  
  export interface SystemStatus {
    overall: 'healthy' | 'warning' | 'error';
    uptime: string;
    activeSessions: number;
    queueDepth: number;
    avgResponseTime: number;
    successRate: number;
    tokenUsage: number;
    costPerHour: number;
  }
  
  export interface PetriNetState {
    currentState: string;
    activeTransitions: number;
    currentPlace: string;
    tokens: number;
    nextTransition?: string;
    flowRate: number;
    bottlenecks: string[];
  }
  
  export interface QuickCommand {
    id: string;
    command: string;
    description: string;
    category: 'status' | 'control' | 'debug' | 'test';
  }
  
  export interface ChatTemplate {
    id: string;
    name: string;
    description: string;
    content: string;
    category: 'common_queries' | 'debug_scripts' | 'reports';
  }
  
  export interface AgentChatState {
    selectedAgents: string[];
    chatMode: 'broadcast' | 'individual' | 'group';
    messages: ChatMessage[];
    agents: Agent[];
    systemStatus: SystemStatus;
    petriNetState: PetriNetState;
    selectedAgent?: Agent;
    agentInternalState?: AgentInternalState;
    isConnected: boolean;
    autoRefresh: boolean;
  }