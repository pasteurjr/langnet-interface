// src/pages/AgentDesignerPage.tsx - Interface Prototype Designer with AI Assistant
import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Agent, AgentStatus } from "../types";
import AIDesignAssistant from "../components/ai/AIDesignAssistant";
import "./AgentDesignerPage.css";

interface InterfaceTheme {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
  borderRadius: string;
  fontFamily: string;
}

interface InterfaceConfig {
  theme: InterfaceTheme;
  layout: "sidebar" | "tabs" | "cards";
  showAgentAvatars: boolean;
  showTypingIndicator: boolean;
  enableVoiceInput: boolean;
  welcomeMessage: string;
  placeholder: string;
  agentIntroductions: Record<string, string>;
}

interface ComponentSettings {
  chatContainer: {
    width: string;
    height: string;
    position: "center" | "left" | "right";
  };
  agentSelector: {
    style: "dropdown" | "tabs" | "sidebar" | "floating";
    showStatus: boolean;
    showCapabilities: boolean;
  };
  messageDisplay: {
    showTimestamp: boolean;
    showAgentName: boolean;
    bubbleStyle: "modern" | "classic" | "minimal";
    animationSpeed: "slow" | "normal" | "fast";
  };
}

// Types for AI Assistant (ready for backend integration)
interface AISuggestion {
  id: string;
  type: "color_palette" | "layout" | "content" | "accessibility";
  title: string;
  description: string;
  data: any;
  confidence: number;
}

interface AIAnalysis {
  accessibilityScore: number;
  usabilityScore: number;
  modernityScore: number;
  issues: string[];
  recommendations: string[];
}

const AgentDesignerPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();

  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedPreview, setSelectedPreview] = useState<
    "desktop" | "tablet" | "mobile"
  >("desktop");
  const [activeTab, setActiveTab] = useState<"design" | "preview" | "code">(
    "preview"
  );
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);
  const [aiSuggestions, setAISuggestions] = useState<AISuggestion[]>([]);
  const [aiAnalysis, setAIAnalysis] = useState<AIAnalysis | null>(null);
  const [isAILoading, setIsAILoading] = useState(false);

  const [interfaceConfig, setInterfaceConfig] = useState<InterfaceConfig>({
    theme: {
      primaryColor: "#0066cc",
      secondaryColor: "#f0f2f5",
      backgroundColor: "#ffffff",
      textColor: "#333333",
      borderRadius: "8px",
      fontFamily: "Inter, sans-serif",
    },
    layout: "sidebar",
    showAgentAvatars: true,
    showTypingIndicator: true,
    enableVoiceInput: false,
    welcomeMessage: "Olá! Como posso ajudá-lo hoje?",
    placeholder: "Digite sua mensagem...",
    agentIntroductions: {},
  });

  const [componentSettings, setComponentSettings] = useState<ComponentSettings>(
    {
      chatContainer: {
        width: "100%",
        height: "600px",
        position: "center",
      },
      agentSelector: {
        style: "sidebar",
        showStatus: true,
        showCapabilities: true,
      },
      messageDisplay: {
        showTimestamp: true,
        showAgentName: true,
        bubbleStyle: "modern",
        animationSpeed: "normal",
      },
    }
  );

  // Mock data for AI suggestions (ready for backend replacement)
  const getMockAISuggestions = (): AISuggestion[] => {
    return [
      {
        id: "1",
        type: "color_palette",
        title: "Paleta Corporativa",
        description: "Cores que transmitem confiança e profissionalismo",
        data: {
          primaryColor: "#1E3A8A",
          secondaryColor: "#E5E7EB",
          backgroundColor: "#F9FAFB",
          textColor: "#1F2937",
        },
        confidence: 0.92,
      },
      {
        id: "2",
        type: "color_palette",
        title: "Paleta Moderna",
        description: "Design contemporâneo com cores vibrantes",
        data: {
          primaryColor: "#7C3AED",
          secondaryColor: "#F3E8FF",
          backgroundColor: "#FFFFFF",
          textColor: "#374151",
        },
        confidence: 0.88,
      },
      {
        id: "3",
        type: "content",
        title: "Mensagem Personalizada",
        description: "Boas-vindas baseadas no contexto dos agentes",
        data: {
          welcomeMessage:
            "Olá! Nossa equipe de especialistas está pronta para ajudá-lo. Escolha o agente mais adequado para sua necessidade.",
          placeholder: "Descreva como podemos ajudá-lo...",
        },
        confidence: 0.85,
      },
      {
        id: "4",
        type: "layout",
        title: "Layout Otimizado",
        description: "Organização melhorada para múltiplos agentes",
        data: {
          layout: "tabs",
          showAgentAvatars: true,
          showStatus: true,
        },
        confidence: 0.9,
      },
    ];
  };

  const getMockAIAnalysis = (): AIAnalysis => {
    return {
      accessibilityScore: 78,
      usabilityScore: 85,
      modernityScore: 82,
      issues: [
        "Contraste insuficiente entre texto secundário e fundo",
        "Falta de indicadores visuais para estado de loading",
        "Botões pequenos demais para touch devices",
      ],
      recommendations: [
        "Aumentar contraste do texto secundário para 4.5:1",
        "Adicionar animações de loading para melhor feedback",
        "Aumentar área clicável dos botões para 44px mínimo",
        "Considerar modo escuro para uso prolongado",
      ],
    };
  };

  // Dados de exemplo dos agentes
  useEffect(() => {
    const mockAgents: Agent[] = [
      {
        id: "customer_service",
        name: "Atendimento",
        role: "Especialista em atendimento ao cliente",
        goal: "Resolver dúvidas e problemas dos clientes",
        backstory: "Especialista com 5 anos de experiência",
        tools: ["knowledge_base", "ticket_system"],
        verbose: true,
        allow_delegation: false,
        status: AgentStatus.ACTIVE,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: "technical_support",
        name: "Suporte Técnico",
        role: "Especialista em problemas técnicos",
        goal: "Resolver questões técnicas complexas",
        backstory: "Engenheiro com experiência em sistemas",
        tools: ["diagnostic_tool", "remote_access"],
        verbose: true,
        allow_delegation: true,
        status: AgentStatus.ACTIVE,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: "sales_assistant",
        name: "Assistente de Vendas",
        role: "Especialista em vendas e produtos",
        goal: "Ajudar clientes a encontrar produtos ideais",
        backstory: "Vendedor experiente com conhecimento de produtos",
        tools: ["product_catalog", "pricing_tool"],
        verbose: false,
        allow_delegation: false,
        status: AgentStatus.ACTIVE,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];
    setAgents(mockAgents);

    // Configurar introduções padrão dos agentes
    const introductions: Record<string, string> = {};
    mockAgents.forEach((agent) => {
      introductions[agent.id] = `Olá! Sou o ${agent.name}. ${agent.goal}`;
    });
    setInterfaceConfig((prev) => ({
      ...prev,
      agentIntroductions: introductions,
    }));
  }, [projectId]);

  // AI Assistant handlers (ready for backend integration)
  const handleOpenAIAssistant = async () => {
    setIsAIAssistantOpen(true);
    setIsAILoading(true);

    // Simulate API call (replace with real backend call)
    setTimeout(() => {
      setAISuggestions(getMockAISuggestions());
      setAIAnalysis(getMockAIAnalysis());
      setIsAILoading(false);
    }, 1500);

    // Future backend integration:
    // try {
    //   const [suggestions, analysis] = await Promise.all([
    //     aiDesignService.getSuggestions({
    //       projectId,
    //       agents,
    //       currentConfig: interfaceConfig
    //     }),
    //     aiDesignService.analyzeInterface({
    //       interfaceConfig,
    //       componentSettings
    //     })
    //   ]);
    //   setAISuggestions(suggestions);
    //   setAIAnalysis(analysis);
    // } catch (error) {
    //   console.error('AI Assistant error:', error);
    // } finally {
    //   setIsAILoading(false);
    // }
  };

  const handleApplyAISuggestion = (suggestion: AISuggestion) => {
    switch (suggestion.type) {
      case "color_palette":
        setInterfaceConfig((prev) => ({
          ...prev,
          theme: { ...prev.theme, ...suggestion.data },
        }));
        break;
      case "content":
        setInterfaceConfig((prev) => ({
          ...prev,
          welcomeMessage: suggestion.data.welcomeMessage || prev.welcomeMessage,
          placeholder: suggestion.data.placeholder || prev.placeholder,
        }));
        break;
      case "layout":
        setInterfaceConfig((prev) => ({
          ...prev,
          layout: suggestion.data.layout || prev.layout,
          showAgentAvatars:
            suggestion.data.showAgentAvatars ?? prev.showAgentAvatars,
        }));
        break;
    }
  };

  const handleGenerateContent = async (
    type: "welcome" | "placeholder" | "agent_intro",
    context?: any
  ) => {
    setIsAILoading(true);

    // Simulate AI content generation (replace with real backend call)
    setTimeout(() => {
      const mockContent = {
        welcome:
          "Bem-vindo! Nossa equipe especializada está aqui para oferecer o melhor atendimento. Como podemos ajudá-lo hoje?",
        placeholder:
          "Conte-nos como podemos tornar sua experiência excepcional...",
        agent_intro: `Olá! Sou ${
          context?.agentName || "seu assistente"
        } e estou aqui para ${context?.goal || "ajudá-lo"}. Vamos começar?`,
      };

      if (type === "welcome") {
        setInterfaceConfig((prev) => ({
          ...prev,
          welcomeMessage: mockContent.welcome,
        }));
      } else if (type === "placeholder") {
        setInterfaceConfig((prev) => ({
          ...prev,
          placeholder: mockContent.placeholder,
        }));
      }

      setIsAILoading(false);
    }, 1000);

    // Future backend integration:
    // try {
    //   const content = await aiDesignService.generateContent({
    //     type,
    //     context: { agents, projectId, ...context }
    //   });
    //   // Apply generated content based on type
    // } catch (error) {
    //   console.error('Content generation error:', error);
    // } finally {
    //   setIsAILoading(false);
    // }
  };

  const updateTheme = (key: keyof InterfaceTheme, value: string) => {
    setInterfaceConfig((prev) => ({
      ...prev,
      theme: { ...prev.theme, [key]: value },
    }));
  };

  const updateConfig = (key: keyof InterfaceConfig, value: any) => {
    setInterfaceConfig((prev) => ({ ...prev, [key]: value }));
  };

  const updateComponentSettings = (
    section: keyof ComponentSettings,
    key: string,
    value: any
  ) => {
    setComponentSettings((prev) => ({
      ...prev,
      [section]: { ...prev[section], [key]: value },
    }));
  };

  const generateReactCode = () => {
    return `// Generated Agent Interface Component
import React, { useState } from 'react';
import './AgentInterface.css';

const AgentInterface = () => {
  const [selectedAgent, setSelectedAgent] = useState('${agents[0]?.id}');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');

  const agents = ${JSON.stringify(
    agents.map((a) => ({
      id: a.id,
      name: a.name,
      role: a.role,
      introduction: interfaceConfig.agentIntroductions[a.id],
    })),
    null,
    2
  )};

  const theme = ${JSON.stringify(interfaceConfig.theme, null, 2)};

  return (
    <div className="agent-interface" style={{
      fontFamily: theme.fontFamily,
      backgroundColor: theme.backgroundColor,
      color: theme.textColor
    }}>
      {/* Agent Interface Implementation */}
      ${
        interfaceConfig.layout === "sidebar"
          ? `
      <div className="interface-sidebar">
        <h3>Agentes Disponíveis</h3>
        {agents.map(agent => (
          <div 
            key={agent.id} 
            className={selectedAgent === agent.id ? 'agent-item active' : 'agent-item'}
            onClick={() => setSelectedAgent(agent.id)}
          >
            ${
              interfaceConfig.showAgentAvatars
                ? '<div className="agent-avatar">🤖</div>'
                : ""
            }
            <div className="agent-info">
              <h4>{agent.name}</h4>
              <p>{agent.role}</p>
            </div>
          </div>
        ))}
      </div>`
          : ""
      }
      
      <div className="chat-container">
        <div className="chat-header">
          <h2>{agents.find(a => a.id === selectedAgent)?.name}</h2>
        </div>
        
        <div className="messages-area">
          <div className="welcome-message">
            ${interfaceConfig.welcomeMessage}
          </div>
        </div>
        
        <div className="input-area">
          <input 
            type="text" 
            placeholder="${interfaceConfig.placeholder}"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
          />
          <button>Enviar</button>
        </div>
      </div>
    </div>
  );
};

export default AgentInterface;`;
  };

  const renderPreview = () => {
    const previewStyle = {
      fontFamily: interfaceConfig.theme.fontFamily,
      backgroundColor: interfaceConfig.theme.backgroundColor,
      color: interfaceConfig.theme.textColor,
      height: componentSettings.chatContainer.height,
      width: componentSettings.chatContainer.width,
      borderRadius: interfaceConfig.theme.borderRadius,
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
      overflow: "hidden",
      display: "flex",
    };

    return (
      <div className="preview-container" style={previewStyle}>
        {/* Sidebar de Agentes */}
        {interfaceConfig.layout === "sidebar" && (
          <div
            className="preview-sidebar"
            style={{
              width: "280px",
              backgroundColor: interfaceConfig.theme.secondaryColor,
              borderRight: "1px solid #e0e0e0",
              padding: "16px",
            }}
          >
            <h3 style={{ margin: "0 0 16px 0", fontSize: "1rem" }}>
              Agentes Disponíveis
            </h3>
            {agents.map((agent, index) => (
              <div
                key={agent.id}
                className="preview-agent-item"
                style={{
                  display: "flex",
                  alignItems: "center",
                  padding: "12px",
                  borderRadius: interfaceConfig.theme.borderRadius,
                  cursor: "pointer",
                  marginBottom: "8px",
                  backgroundColor:
                    index === 0
                      ? interfaceConfig.theme.primaryColor
                      : "transparent",
                  color:
                    index === 0 ? "white" : interfaceConfig.theme.textColor,
                  transition: "all 0.2s",
                }}
              >
                {interfaceConfig.showAgentAvatars && (
                  <div style={{ marginRight: "8px", fontSize: "1.2rem" }}>
                    🤖
                  </div>
                )}
                <div>
                  <div style={{ fontWeight: "500", fontSize: "0.9rem" }}>
                    {agent.name}
                  </div>
                  <div style={{ fontSize: "0.8rem", opacity: 0.8 }}>
                    {agent.role}
                  </div>
                  {componentSettings.agentSelector.showStatus && (
                    <div style={{ fontSize: "0.7rem", marginTop: "2px" }}>
                      ●{" "}
                      {agent.status === AgentStatus.ACTIVE
                        ? "Online"
                        : "Offline"}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Área de Chat */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {/* Header do Chat */}
          <div
            style={{
              padding: "16px",
              backgroundColor: interfaceConfig.theme.primaryColor,
              color: "white",
            }}
          >
            <h2 style={{ margin: 0, fontSize: "1.1rem" }}>{agents[0]?.name}</h2>
          </div>

          {/* Área de Mensagens */}
          <div
            style={{
              flex: 1,
              padding: "16px",
              overflowY: "auto",
            }}
          >
            <div
              className="preview-message"
              style={{
                padding: "12px",
                backgroundColor: interfaceConfig.theme.secondaryColor,
                borderRadius: interfaceConfig.theme.borderRadius,
                marginBottom: "12px",
              }}
            >
              <div
                style={{
                  fontSize: "0.8rem",
                  marginBottom: "4px",
                  opacity: 0.7,
                }}
              >
                {componentSettings.messageDisplay.showAgentName &&
                  agents[0]?.name}
                {componentSettings.messageDisplay.showTimestamp && " • 09:30"}
              </div>
              <div>{interfaceConfig.welcomeMessage}</div>
            </div>

            <div
              className="preview-message"
              style={{
                padding: "12px",
                backgroundColor: interfaceConfig.theme.primaryColor,
                color: "white",
                borderRadius: interfaceConfig.theme.borderRadius,
                marginLeft: "20%",
                marginBottom: "12px",
              }}
            >
              <div
                style={{
                  fontSize: "0.8rem",
                  marginBottom: "4px",
                  opacity: 0.9,
                }}
              >
                Você{" "}
                {componentSettings.messageDisplay.showTimestamp && "• 09:31"}
              </div>
              <div>Olá! Preciso de ajuda com meu pedido.</div>
            </div>

            {interfaceConfig.showTypingIndicator && (
              <div style={{ padding: "8px", fontSize: "0.8rem", opacity: 0.7 }}>
                {agents[0]?.name} está digitando...
              </div>
            )}
          </div>

          {/* Área de Input */}
          <div
            style={{
              padding: "16px",
              borderTop: "1px solid #e0e0e0",
              display: "flex",
              gap: "8px",
            }}
          >
            <input
              type="text"
              placeholder={interfaceConfig.placeholder}
              style={{
                flex: 1,
                padding: "12px",
                border: "1px solid #ddd",
                borderRadius: interfaceConfig.theme.borderRadius,
                fontFamily: interfaceConfig.theme.fontFamily,
              }}
              readOnly
            />
            <button
              style={{
                padding: "12px 24px",
                backgroundColor: interfaceConfig.theme.primaryColor,
                color: "white",
                border: "none",
                borderRadius: interfaceConfig.theme.borderRadius,
                cursor: "pointer",
              }}
            >
              Enviar
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="agent-designer-page">
      <div className="page-header">
        <h1>Designer de Interface de Agentes</h1>
        <div className="header-actions">
          <div className="preview-toggle">
            <button
              className={selectedPreview === "desktop" ? "active" : ""}
              onClick={() => setSelectedPreview("desktop")}
            >
              🖥️ Desktop
            </button>
            <button
              className={selectedPreview === "tablet" ? "active" : ""}
              onClick={() => setSelectedPreview("tablet")}
            >
              📱 Tablet
            </button>
            <button
              className={selectedPreview === "mobile" ? "active" : ""}
              onClick={() => setSelectedPreview("mobile")}
            >
              📱 Mobile
            </button>
          </div>
          <button
            className="btn btn-ai-assistant"
            onClick={handleOpenAIAssistant}
            disabled={isAILoading}
          >
            {isAILoading ? "⏳" : "✨"} AI Design Assistant
          </button>
          <button className="btn btn-secondary">📤 Exportar Componentes</button>
          <button className="btn btn-secondary">❓ Ajuda</button>
        </div>
      </div>

      <div className="designer-tabs">
        <button
          className={activeTab === "preview" ? "tab active" : "tab"}
          onClick={() => setActiveTab("preview")}
        >
          👁️ Preview
        </button>
        <button
          className={activeTab === "design" ? "tab active" : "tab"}
          onClick={() => setActiveTab("design")}
        >
          🎨 Design
        </button>
        <button
          className={activeTab === "code" ? "tab active" : "tab"}
          onClick={() => setActiveTab("code")}
        >
          💻 Código
        </button>
      </div>

      <div className="designer-content">
        {activeTab === "preview" && (
          <div className="preview-section">
            <div className="preview-main">{renderPreview()}</div>
          </div>
        )}

        {activeTab === "design" && (
          <div className="design-section">
            <div className="design-sidebar">
              <div className="design-panel">
                <h3>🎨 Tema</h3>
                <div className="form-group">
                  <label>Cor Primária:</label>
                  <input
                    type="color"
                    value={interfaceConfig.theme.primaryColor}
                    onChange={(e) =>
                      updateTheme("primaryColor", e.target.value)
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Cor Secundária:</label>
                  <input
                    type="color"
                    value={interfaceConfig.theme.secondaryColor}
                    onChange={(e) =>
                      updateTheme("secondaryColor", e.target.value)
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Cor de Fundo:</label>
                  <input
                    type="color"
                    value={interfaceConfig.theme.backgroundColor}
                    onChange={(e) =>
                      updateTheme("backgroundColor", e.target.value)
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Fonte:</label>
                  <select
                    value={interfaceConfig.theme.fontFamily}
                    onChange={(e) => updateTheme("fontFamily", e.target.value)}
                  >
                    <option value="Inter, sans-serif">Inter</option>
                    <option value="Roboto, sans-serif">Roboto</option>
                    <option value="Arial, sans-serif">Arial</option>
                    <option value="Georgia, serif">Georgia</option>
                  </select>
                </div>
              </div>

              <div className="design-panel">
                <h3>📱 Layout</h3>
                <div className="form-group">
                  <label>Estilo:</label>
                  <select
                    value={interfaceConfig.layout}
                    onChange={(e) => updateConfig("layout", e.target.value)}
                  >
                    <option value="sidebar">Sidebar</option>
                    <option value="tabs">Abas</option>
                    <option value="cards">Cards</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={interfaceConfig.showAgentAvatars}
                      onChange={(e) =>
                        updateConfig("showAgentAvatars", e.target.checked)
                      }
                    />
                    Mostrar Avatares dos Agentes
                  </label>
                </div>
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={interfaceConfig.showTypingIndicator}
                      onChange={(e) =>
                        updateConfig("showTypingIndicator", e.target.checked)
                      }
                    />
                    Indicador de Digitação
                  </label>
                </div>
              </div>

              <div className="design-panel">
                <div className="panel-header">
                  <h3>💬 Mensagens</h3>
                  <button
                    className="btn-ai-generate"
                    onClick={() => handleGenerateContent("welcome")}
                    disabled={isAILoading}
                    title="Gerar com IA"
                  >
                    {isAILoading ? "⏳" : "✨"}
                  </button>
                </div>
                <div className="form-group">
                  <label>Mensagem de Boas-vindas:</label>
                  <textarea
                    value={interfaceConfig.welcomeMessage}
                    onChange={(e) =>
                      updateConfig("welcomeMessage", e.target.value)
                    }
                    rows={2}
                  />
                </div>
                <div className="form-group">
                  <label>
                    Placeholder do Input:
                    <button
                      className="btn-ai-generate-inline"
                      onClick={() => handleGenerateContent("placeholder")}
                      disabled={isAILoading}
                    >
                      ✨
                    </button>
                  </label>
                  <input
                    type="text"
                    value={interfaceConfig.placeholder}
                    onChange={(e) =>
                      updateConfig("placeholder", e.target.value)
                    }
                  />
                </div>
              </div>
            </div>

            <div className="design-main">{renderPreview()}</div>
          </div>
        )}

        {activeTab === "code" && (
          <div className="code-section">
            <div className="code-tabs">
              <button className="code-tab active">React Component</button>
              <button className="code-tab">CSS Styles</button>
              <button className="code-tab">Configuration</button>
            </div>
            <div className="code-editor">
              <pre>
                <code>{generateReactCode()}</code>
              </pre>
            </div>
            <div className="code-actions">
              <button className="btn btn-primary">📋 Copiar Código</button>
              <button className="btn btn-secondary">💾 Baixar Arquivos</button>
              <button className="btn btn-secondary">🚀 Gerar Componente</button>
            </div>
          </div>
        )}
      </div>

      {/* AI Design Assistant Modal/Sidebar */}
      <AIDesignAssistant
        isOpen={isAIAssistantOpen}
        onClose={() => setIsAIAssistantOpen(false)}
        suggestions={aiSuggestions}
        analysis={aiAnalysis}
        isLoading={isAILoading}
        onApplySuggestion={handleApplyAISuggestion}
        onGenerateContent={handleGenerateContent}
        currentConfig={interfaceConfig}
        agents={agents}
        projectId={projectId || ""}
      />
    </div>
  );
};

export default AgentDesignerPage;
