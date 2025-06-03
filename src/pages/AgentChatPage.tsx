// src/pages/AgentChatPage.tsx - CORRIGIDO erros TypeScript
import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import AgentPerformanceDashboard from "../components/agents/AgentPerformanceDashboard";
import AgentMonitoringTable from "../components/agents/AgentMonitoringTable";
import AgentDebugPanel from "../components/agents/AgentDebugPanel";
import ChatInterface from "../components/agents/ChatInterface";
import InterventionControls from "../components/agents/InterventionControls";
import {
  Agent,
  ChatMessage,
  SystemStatus,
  PetriNetState,
  AgentInternalState,
  AgentChatState,
} from "../types/agentChat";
import "./AgentChatPage.css";

const AgentChatPage: React.FC = () => {
  const { projectId } = useParams<{ projectId?: string }>();

  // Estado principal
  const [chatState, setChatState] = useState<AgentChatState>({
    selectedAgents: [],
    chatMode: "broadcast",
    messages: [],
    agents: [],
    systemStatus: {
      overall: "healthy",
      uptime: "0h 0m",
      activeSessions: 0,
      queueDepth: 0,
      avgResponseTime: 0,
      successRate: 0,
      tokenUsage: 0,
      costPerHour: 0,
    },
    petriNetState: {
      currentState: "Iniciando",
      activeTransitions: 0,
      currentPlace: "P0",
      tokens: 0,
      flowRate: 0,
      bottlenecks: [],
    },
    isConnected: false,
    autoRefresh: true,
  });

  const [selectedAgent, setSelectedAgent] = useState<Agent | undefined>();
  const [agentInternalState, setAgentInternalState] = useState<
    AgentInternalState | undefined
  >();

  // Dados mock para demonstração
  const initializeMockData = useCallback(() => {
    const mockAgents: Agent[] = [
      {
        id: "agent_1",
        name: "Customer Service",
        role: "Agente de atendimento ao cliente",
        status: "active",
        load: 67,
        queue: 5,
        lastActivity: new Date(Date.now() - 120000).toISOString(),
        type: "customer_service",
      },
      {
        id: "agent_2",
        name: "Technical Support",
        role: "Suporte técnico especializado",
        status: "busy",
        load: 89,
        queue: 12,
        lastActivity: new Date(Date.now() - 30000).toISOString(),
        type: "technical_support",
      },
      {
        id: "agent_3",
        name: "Sentiment Analyzer",
        role: "Análise de sentimento",
        status: "active",
        load: 45,
        queue: 8,
        lastActivity: new Date(Date.now() - 5000).toISOString(),
        type: "sentiment_analyzer",
      },
      {
        id: "agent_4",
        name: "Response Generator",
        role: "Geração de respostas",
        status: "error",
        load: 23,
        queue: 3,
        lastActivity: new Date(Date.now() - 300000).toISOString(),
        type: "response_generator",
      },
      {
        id: "agent_5",
        name: "Escalation Manager",
        role: "Gerenciamento de escalações",
        status: "inactive",
        load: 0,
        queue: 0,
        lastActivity: new Date(Date.now() - 600000).toISOString(),
        type: "escalation_manager",
      },
    ];

    const mockSystemStatus: SystemStatus = {
      overall: "healthy",
      uptime: "15d 7h 23m",
      activeSessions: 24,
      queueDepth: 28,
      avgResponseTime: 2.3,
      successRate: 96.5,
      tokenUsage: 15200,
      costPerHour: 4.67,
    };

    const mockPetriNetState: PetriNetState = {
      currentState: "Processando",
      activeTransitions: 3,
      currentPlace: "P2 (Queue)",
      tokens: 5,
      nextTransition: "T2 (Analyze)",
      flowRate: 45,
      bottlenecks: ["Response Generation", "Queue Overflow"],
    };

    const mockMessages: ChatMessage[] = [
      {
        id: "1",
        timestamp: new Date(Date.now() - 300000).toISOString(),
        sender: "system",
        content: "Sistema iniciado com sucesso. 5 agentes carregados.",
        type: "system_notification",
      },
      {
        id: "2",
        timestamp: new Date(Date.now() - 180000).toISOString(),
        sender: "user",
        content: "/status",
        type: "command",
      },
      {
        id: "3",
        timestamp: new Date(Date.now() - 179000).toISOString(),
        sender: "system",
        agentId: "system",
        agentName: "Sistema",
        content: "Status geral: Saudável. 4/5 agentes ativos. Fila: 28 itens.",
        type: "system_notification",
      },
      {
        id: "4",
        timestamp: new Date(Date.now() - 120000).toISOString(),
        sender: "user",
        content:
          'Teste de processamento: "Cliente reclamando de cobrança incorreta"',
        type: "message",
      },
      {
        id: "5",
        timestamp: new Date(Date.now() - 118000).toISOString(),
        sender: "agent",
        agentId: "agent_1",
        agentName: "Customer Service",
        content:
          "Query processada. Sentimento: Negativo (-0.7). Categoria: Billing. Roteando para especialista.",
        type: "message",
        metadata: {
          confidence: 0.92,
          processingTime: 1850,
          tokens: 245,
          reasoning: [
            'Identificada palavra-chave "cobrança"',
            'Detectado sentimento negativo pela palavra "reclamando"',
            "Classificada como categoria: Billing",
            "Decisão: Rotear para Technical Support",
          ],
        },
      },
    ];

    setChatState((prev) => ({
      ...prev,
      agents: mockAgents,
      systemStatus: mockSystemStatus,
      petriNetState: mockPetriNetState,
      messages: mockMessages,
      selectedAgents: [mockAgents[0].id],
      isConnected: true,
    }));

    // Selecionar primeiro agente por padrão
    setSelectedAgent(mockAgents[0]);

    // Mock do estado interno do primeiro agente
    setAgentInternalState({
      currentTask: "Processing customer query",
      memoryUsage: 67,
      contextWindow: {
        used: 1856,
        total: 4096,
      },
      lastDecision: {
        description:
          "Classified query as billing issue with negative sentiment",
        confidence: 0.92,
      },
      reasoningTrace: [
        'Received customer query: "Cliente reclamando de cobrança incorreta"',
        "Tokenized input: 8 tokens",
        'Detected keywords: ["cliente", "reclamando", "cobrança", "incorreta"]',
        "Sentiment analysis: negative (-0.7)",
        "Category classification: billing (confidence: 0.92)",
        "Decision: route to technical support specialist",
      ],
      performance: {
        successRate: 96.5,
        avgResponseTime: 2.1,
        tokensUsed: 4200,
        requestsPerHour: 156,
        errorRate: 3.5,
        confidence: 0.89,
      },
    });
  }, []);

  // Inicialização
  useEffect(() => {
    initializeMockData();
  }, [initializeMockData]);

  // Auto-refresh
  useEffect(() => {
    if (!chatState.autoRefresh) return;

    const interval = setInterval(() => {
      // Simular atualizações em tempo real
      setChatState((prev) => ({
        ...prev,
        systemStatus: {
          ...prev.systemStatus,
          activeSessions:
            prev.systemStatus.activeSessions +
            Math.floor(Math.random() * 3) -
            1,
          queueDepth: Math.max(
            0,
            prev.systemStatus.queueDepth + Math.floor(Math.random() * 5) - 2
          ),
          avgResponseTime: Math.max(
            0.5,
            prev.systemStatus.avgResponseTime + (Math.random() - 0.5) * 0.2
          ),
        },
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, [chatState.autoRefresh]);

  // Handlers
  const handleSendMessage = useCallback(
    (content: string, type: "message" | "command") => {
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        sender: "user",
        content,
        type: type === "command" ? "command" : "message",
      };

      setChatState((prev) => ({
        ...prev,
        messages: [...prev.messages, newMessage],
      }));

      // Simular resposta do sistema
      setTimeout(() => {
        let responseContent = "";
        let responseType: ChatMessage["type"] = "system_notification";
        let agentName = "Sistema";
        let agentId = "system";

        if (type === "command") {
          switch (content.toLowerCase()) {
            case "/status":
              responseContent = `Status: ${
                chatState.agents.filter((a) => a.status === "active").length
              }/${chatState.agents.length} agentes ativos. Fila: ${
                chatState.systemStatus.queueDepth
              } itens.`;
              break;
            case "/debug":
              responseContent =
                "Modo debug ativado. Exibindo informações detalhadas de processamento.";
              break;
            case "/clear":
              setChatState((prev) => ({ ...prev, messages: [] }));
              return;
            case "/help":
              responseContent =
                "Comandos disponíveis: /status, /debug, /clear, /pause, /resume, /restart, /metrics";
              break;
            default:
              responseContent = `Comando "${content}" executado.`;
          }
        } else {
          // Simular processamento de mensagem por um agente
          if (chatState.selectedAgents.length > 0) {
            const agent = chatState.agents.find(
              (a) => a.id === chatState.selectedAgents[0]
            );
            if (agent) {
              agentName = agent.name;
              agentId = agent.id;
              responseContent = `Mensagem processada: "${content}". Análise concluída com sucesso.`;
              responseType = "message";
            }
          }
        }

        const responseMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          timestamp: new Date().toISOString(),
          sender: type === "command" ? "system" : "agent",
          agentId,
          agentName,
          content: responseContent,
          type: responseType,
          metadata:
            type !== "command"
              ? {
                  confidence: 0.85 + Math.random() * 0.15,
                  processingTime: 1500 + Math.random() * 1000,
                  tokens: 150 + Math.floor(Math.random() * 100),
                }
              : undefined,
        };

        setChatState((prev) => ({
          ...prev,
          messages: [...prev.messages, responseMessage],
        }));
      }, 800 + Math.random() * 1200);
    },
    [
      chatState.selectedAgents,
      chatState.agents,
      chatState.systemStatus.queueDepth,
    ]
  );

  const handleChatModeChange = useCallback(
    (mode: "broadcast" | "individual" | "group") => {
      setChatState((prev) => ({ ...prev, chatMode: mode }));
    },
    []
  );

  const handleAgentSelectionChange = useCallback((agentIds: string[]) => {
    setChatState((prev) => ({ ...prev, selectedAgents: agentIds }));
  }, []);

  const handleAgentSelect = useCallback((agent: Agent) => {
    setSelectedAgent(agent);

    // Simular carregamento do estado interno
    setTimeout(() => {
      setAgentInternalState({
        currentTask: `Processing for ${agent.name}`,
        memoryUsage: 45 + Math.random() * 40,
        contextWindow: {
          used: Math.floor(1000 + Math.random() * 2000),
          total: 4096,
        },
        lastDecision: {
          description: `Last decision by ${agent.name}`,
          confidence: 0.7 + Math.random() * 0.3,
        },
        reasoningTrace: [
          `Agent ${agent.name} initialized`,
          "Processing current workload",
          "Analyzing incoming requests",
          "Optimizing response generation",
        ],
        performance: {
          successRate: 90 + Math.random() * 10,
          avgResponseTime: 1 + Math.random() * 3,
          tokensUsed: Math.floor(2000 + Math.random() * 5000),
          requestsPerHour: Math.floor(50 + Math.random() * 150),
          errorRate: Math.random() * 5,
          confidence: 0.8 + Math.random() * 0.2,
        },
      });
    }, 500);
  }, []);

  // ✅ CORREÇÃO 1: Ajustar o tipo do handler para aceitar string genérico
  const handleAgentAction = useCallback((agentId: string, action: string) => {
    // ✅ CORRIGIDO: aceita string genérico
    console.log(`Executando ação ${action} no agente ${agentId}`);

    // Simular ação
    setChatState((prev) => ({
      ...prev,
      messages: [
        ...prev.messages,
        {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          sender: "system",
          content: `Ação "${action}" executada no agente ${agentId}`,
          type: "system_notification",
        },
      ],
    }));
  }, []);

  const handleIntrospectionRequest = useCallback(
    (
      agentId: string,
      type: "reasoning" | "memory" | "performance" | "context"
    ) => {
      console.log(`Solicitando introspecção ${type} do agente ${agentId}`);

      setChatState((prev) => ({
        ...prev,
        messages: [
          ...prev.messages,
          {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            sender: "system",
            content: `Introspecção ${type} solicitada para o agente ${agentId}`,
            type: "debug_info",
          },
        ],
      }));
    },
    []
  );

  const handleSystemRefresh = useCallback(() => {
    console.log("Atualizando sistema...");
    // Simular atualização
    setChatState((prev) => ({
      ...prev,
      systemStatus: {
        ...prev.systemStatus,
        activeSessions:
          prev.systemStatus.activeSessions + Math.floor(Math.random() * 5) - 2,
        queueDepth: Math.max(
          0,
          prev.systemStatus.queueDepth + Math.floor(Math.random() * 10) - 5
        ),
      },
    }));
  }, []);

  // Handlers de controle de intervenção
  const handleEmergencyStop = useCallback(() => {
    console.log("Parada de emergência acionada!");
    setChatState((prev) => ({
      ...prev,
      agents: prev.agents.map((agent) => ({
        ...agent,
        status: "inactive" as const,
      })),
      messages: [
        ...prev.messages,
        {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          sender: "system",
          content:
            "🚨 PARADA DE EMERGÊNCIA ACIONADA - Todos os agentes foram desativados",
          type: "system_notification",
        },
      ],
    }));
  }, []);

  const handlePauseSystem = useCallback(() => {
    console.log("Sistema pausado");
    setChatState((prev) => ({
      ...prev,
      messages: [
        ...prev.messages,
        {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          sender: "system",
          content: "⏸️ Sistema pausado - Processamento suspenso",
          type: "system_notification",
        },
      ],
    }));
  }, []);

  const handleRestartSystem = useCallback(() => {
    console.log("Sistema reiniciado");
    initializeMockData();
    setChatState((prev) => ({
      ...prev,
      messages: [
        ...prev.messages,
        {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          sender: "system",
          content: "🔄 Sistema reiniciado com sucesso",
          type: "system_notification",
        },
      ],
    }));
  }, [initializeMockData]);

  const handleManualIntervention = useCallback((action: string, data?: any) => {
    console.log("Intervenção manual:", action, data);
    setChatState((prev) => ({
      ...prev,
      messages: [
        ...prev.messages,
        {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          sender: "system",
          content: `✋ Intervenção manual: ${action} ${
            data ? JSON.stringify(data) : ""
          }`,
          type: "system_notification",
        },
      ],
    }));
  }, []);

  const handleSystemTuning = useCallback((action: string, params: any) => {
    console.log("Ajuste do sistema:", action, params);
    setChatState((prev) => ({
      ...prev,
      messages: [
        ...prev.messages,
        {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          sender: "system",
          content: `🔧 Ajuste aplicado: ${action}`,
          type: "system_notification",
        },
      ],
    }));
  }, []);

  return (
    <div className="agent-chat-page">
      {/* Header */}
      <div className="page-header">
        <h1>🎛️ Interface de Chat e Controle de Agentes</h1>
        {projectId && (
          <span className="project-context">Projeto: {projectId}</span>
        )}
        <div className="connection-status">
          <span
            className={`status-indicator ${
              chatState.isConnected ? "connected" : "disconnected"
            }`}
          >
            {chatState.isConnected ? "🟢 Conectado" : "🔴 Desconectado"}
          </span>
        </div>
      </div>

      {/* Layout Principal */}
      <div className="page-content">
        {/* Linha Superior */}
        <div className="top-row">
          <div className="performance-section">
            <AgentPerformanceDashboard
              systemStatus={chatState.systemStatus}
              onRefresh={handleSystemRefresh}
            />
          </div>
          <div className="monitoring-section">
            <AgentMonitoringTable
              agents={chatState.agents}
              selectedAgent={selectedAgent}
              onAgentSelect={handleAgentSelect}
              onAgentAction={handleAgentAction}
            />
          </div>
        </div>

        {/* Linha do Meio */}
        <div className="middle-row">
          <div className="debug-section">
            {/* ✅ CORREÇÃO 2: Garantir que selectedAgent não seja undefined */}
            <AgentDebugPanel
              selectedAgent={selectedAgent}
              agentInternalState={agentInternalState}
              onIntrospectionRequest={handleIntrospectionRequest}
            />
          </div>
          <div className="chat-section">
            <ChatInterface
              messages={chatState.messages}
              agents={chatState.agents}
              selectedAgents={chatState.selectedAgents}
              chatMode={chatState.chatMode}
              onSendMessage={handleSendMessage}
              onChatModeChange={handleChatModeChange}
              onAgentSelectionChange={handleAgentSelectionChange}
            />
          </div>
        </div>

        {/* Linha Inferior */}
        <div className="bottom-row">
          <div className="intervention-section">
            <InterventionControls
              petriNetState={chatState.petriNetState}
              onEmergencyStop={handleEmergencyStop}
              onPauseSystem={handlePauseSystem}
              onRestartSystem={handleRestartSystem}
              onManualIntervention={handleManualIntervention}
              onSystemTuning={handleSystemTuning}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentChatPage;
