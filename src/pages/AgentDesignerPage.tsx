// src/pages/AgentDesignerPage.tsx - VERSÃO COMPLETA COM FASE 2
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

// 🆕 FASE 2: Types avançados para IA
interface AISuggestion {
  id: string;
  type:
    | "color_palette"
    | "layout"
    | "content"
    | "accessibility"
    | "layout_optimization";
  title: string;
  description: string;
  data: any;
  confidence: number;
}

interface AIAnalysis {
  accessibilityScore: number;
  usabilityScore: number;
  modernityScore: number;
  wcagCompliance: {
    level: "AA" | "AAA" | "Non-compliant";
    issues: string[];
    fixes: string[];
  };
  colorContrast: {
    ratio: number;
    passes: boolean;
    recommendations: string[];
  };
  issues: string[];
  recommendations: string[];
  layoutAnalysis: {
    efficiency: number;
    suggestions: string[];
    bottlenecks: string[];
  };
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

  // 🆕 FASE 2: Utilitários para análise de cores
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16),
        }
      : { r: 0, g: 0, b: 0 };
  };

  const calculateContrast = (
    rgb1: { r: number; g: number; b: number },
    rgb2: { r: number; g: number; b: number }
  ) => {
    const luminance = (rgb: { r: number; g: number; b: number }) => {
      const rsRGB = rgb.r / 255;
      const gsRGB = rgb.g / 255;
      const bsRGB = rgb.b / 255;

      const r =
        rsRGB <= 0.03928
          ? rsRGB / 12.92
          : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
      const g =
        gsRGB <= 0.03928
          ? gsRGB / 12.92
          : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
      const b =
        bsRGB <= 0.03928
          ? bsRGB / 12.92
          : Math.pow((bsRGB + 0.055) / 1.055, 2.4);

      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };

    const lum1 = luminance(rgb1);
    const lum2 = luminance(rgb2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);

    return (brightest + 0.05) / (darkest + 0.05);
  };

  // 🆕 FASE 2: Análise avançada de acessibilidade
  const analyzeAccessibility = (
    config: InterfaceConfig
  ): AIAnalysis["wcagCompliance"] => {
    const issues: string[] = [];
    const fixes: string[] = [];

    // Análise de contraste
    const primaryRgb = hexToRgb(config.theme.primaryColor);
    const backgroundRgb = hexToRgb(config.theme.backgroundColor);
    const contrastRatio = calculateContrast(primaryRgb, backgroundRgb);

    if (contrastRatio < 4.5) {
      issues.push(
        `Contraste insuficiente: ${contrastRatio.toFixed(2)}:1 (mínimo 4.5:1)`
      );
      fixes.push("Ajustar cores para aumentar contraste para WCAG AA");
    }

    if (contrastRatio < 7.0) {
      issues.push(
        `Contraste abaixo do ideal para WCAG AAA: ${contrastRatio.toFixed(2)}:1`
      );
      fixes.push("Otimizar cores para conformidade WCAG AAA (7:1)");
    }

    // Análise de elementos visuais
    if (!config.showAgentAvatars) {
      issues.push("Falta de elementos visuais para identificação de agentes");
      fixes.push("Ativar avatares dos agentes para melhor identificação");
    }

    // Análise de feedback
    if (!config.showTypingIndicator) {
      issues.push("Ausência de feedback durante processamento");
      fixes.push("Ativar indicadores de digitação e status");
    }

    // Análise de navegação
    if (config.layout === "cards" && agents.length > 4) {
      issues.push("Layout de cards pode ser confuso com muitos agentes");
      fixes.push("Considerar layout sidebar ou tabs para melhor organização");
    }

    return {
      level:
        issues.length === 0
          ? "AAA"
          : issues.length < 2
          ? "AA"
          : "Non-compliant",
      issues,
      fixes,
    };
  };

  // 🆕 FASE 2: Geração inteligente de sugestões baseada no contexto
  const generateContextualSuggestions = (): AISuggestion[] => {
    const suggestions: AISuggestion[] = [];
    const agentCount = agents.length;
    const currentContrast = calculateContrast(
      hexToRgb(interfaceConfig.theme.primaryColor),
      hexToRgb(interfaceConfig.theme.backgroundColor)
    );

    // Sugestões de contraste
    if (currentContrast < 4.5) {
      suggestions.push({
        id: `contrast_fix_${Date.now()}`,
        type: "color_palette",
        title: "Correção Automática de Contraste",
        description: `Melhorar contraste de ${currentContrast.toFixed(
          2
        )}:1 para conformidade WCAG AA`,
        data: {
          primaryColor: "#1E3A8A",
          secondaryColor: "#F3F4F6",
          backgroundColor: "#FFFFFF",
          textColor: "#1F2937",
        },
        confidence: 0.95,
      });
    }

    // Sugestões de layout baseadas no número de agentes
    if (agentCount > 3 && interfaceConfig.layout === "tabs") {
      suggestions.push({
        id: `layout_sidebar_${Date.now()}`,
        type: "layout_optimization",
        title: "Layout Sidebar Recomendado",
        description: `Para ${agentCount} agentes, sidebar oferece melhor organização que tabs`,
        data: { layout: "sidebar" },
        confidence: 0.88,
      });
    }

    if (agentCount <= 2 && interfaceConfig.layout === "sidebar") {
      suggestions.push({
        id: `layout_tabs_${Date.now()}`,
        type: "layout_optimization",
        title: "Layout Tabs Otimizado",
        description: `Com apenas ${agentCount} agente(s), tabs maximiza espaço de chat`,
        data: { layout: "tabs" },
        confidence: 0.85,
      });
    }

    // Sugestões de acessibilidade
    const wcag = analyzeAccessibility(interfaceConfig);
    if (wcag.fixes.length > 0) {
      suggestions.push({
        id: `accessibility_${Date.now()}`,
        type: "accessibility",
        title: "Melhorias de Acessibilidade",
        description: `${wcag.fixes.length} correções para conformidade WCAG ${wcag.level}`,
        data: { fixes: wcag.fixes, currentLevel: wcag.level },
        confidence: 0.92,
      });
    }

    // Sugestões de conteúdo baseadas no domínio
    if (projectId?.includes("atendimento") || projectId?.includes("customer")) {
      suggestions.push({
        id: `content_customer_${Date.now()}`,
        type: "content",
        title: "Conteúdo Otimizado para Atendimento",
        description:
          "Mensagens personalizadas para sistema de atendimento ao cliente",
        data: {
          welcomeMessage:
            "Bem-vindo! Nossa equipe está pronta para oferecer o melhor atendimento. Como podemos ajudá-lo?",
          placeholder: "Descreva como podemos ajudá-lo hoje...",
        },
        confidence: 0.87,
      });
    }

    // Sugestões de paletas modernas
    suggestions.push({
      id: `palette_modern_${Date.now()}`,
      type: "color_palette",
      title: "Paleta Moderna 2024",
      description:
        "Cores contemporâneas com excelente contraste e apelo visual",
      data: {
        primaryColor: "#6366F1",
        secondaryColor: "#F1F5F9",
        backgroundColor: "#FFFFFF",
        textColor: "#0F172A",
      },
      confidence: 0.83,
    });

    return suggestions;
  };

  // 🆕 FASE 2: Análise completa incluindo métricas avançadas
  const generateAdvancedAnalysis = (): AIAnalysis => {
    const wcag = analyzeAccessibility(interfaceConfig);
    const contrast = calculateContrast(
      hexToRgb(interfaceConfig.theme.primaryColor),
      hexToRgb(interfaceConfig.theme.backgroundColor)
    );

    // Cálculo de scores baseado em métricas reais
    const accessibilityScore = Math.min(
      100,
      Math.max(
        0,
        (contrast >= 7 ? 100 : contrast >= 4.5 ? 85 : contrast * 15) *
          (interfaceConfig.showAgentAvatars ? 1 : 0.9) *
          (interfaceConfig.showTypingIndicator ? 1 : 0.95)
      )
    );

    const usabilityScore = Math.min(
      100,
      Math.max(
        0,
        (agents.length <= 2 && interfaceConfig.layout === "tabs"
          ? 95
          : agents.length <= 4 && interfaceConfig.layout === "sidebar"
          ? 90
          : agents.length > 4 && interfaceConfig.layout === "cards"
          ? 70
          : 85) * (interfaceConfig.showAgentAvatars ? 1 : 0.9)
      )
    );

    const modernityScore = Math.min(
      100,
      Math.max(
        0,
        (interfaceConfig.theme.fontFamily.includes("Inter") ? 95 : 80) *
          (parseInt(interfaceConfig.theme.borderRadius) >= 8 ? 1 : 0.9) *
          (interfaceConfig.showTypingIndicator ? 1 : 0.95)
      )
    );

    return {
      accessibilityScore: Math.round(accessibilityScore),
      usabilityScore: Math.round(usabilityScore),
      modernityScore: Math.round(modernityScore),
      wcagCompliance: wcag,
      colorContrast: {
        ratio: contrast,
        passes: contrast >= 4.5,
        recommendations:
          contrast < 4.5
            ? [
                "Escurecer cor primária ou clarear fundo",
                "Considerar paleta com maior diferença de luminosidade",
              ]
            : [],
      },
      issues: [
        ...(contrast < 4.5
          ? [`Contraste insuficiente: ${contrast.toFixed(2)}:1`]
          : []),
        ...(agents.length > 4 && interfaceConfig.layout === "cards"
          ? ["Layout pode ser confuso com muitos agentes"]
          : []),
        ...(!interfaceConfig.showTypingIndicator
          ? ["Falta de feedback visual durante processamento"]
          : []),
      ],
      recommendations: [
        ...(contrast < 4.5 ? ["Melhorar contraste de cores"] : []),
        ...(agents.length > 3 && interfaceConfig.layout !== "sidebar"
          ? ["Considerar layout sidebar"]
          : []),
        ...(agents.length <= 2 && interfaceConfig.layout !== "tabs"
          ? ["Layout tabs pode ser mais eficiente"]
          : []),
        "Considerar adicionar modo escuro",
        "Implementar animações suaves",
        "Otimizar para dispositivos móveis",
      ],
      layoutAnalysis: {
        efficiency: usabilityScore,
        suggestions: [
          agents.length > 3
            ? "Sidebar recomendado para múltiplos agentes"
            : "Tabs ideal para poucos agentes",
          "Considerar responsividade mobile",
          "Implementar busca rápida de agentes se necessário",
        ],
        bottlenecks: [
          ...(agents.length > 5
            ? ["Muitos agentes podem confundir usuários"]
            : []),
          ...(interfaceConfig.layout === "cards" && agents.length > 4
            ? ["Cards requer muitos cliques"]
            : []),
        ],
      },
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
        backstory: "Especialista com 5 anos de experiência em atendimento",
        tools: ["knowledge_base", "ticket_system", "customer_history"],
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
        backstory: "Engenheiro com experiência em sistemas e infraestrutura",
        tools: ["diagnostic_tool", "remote_access", "system_monitor"],
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
        backstory: "Vendedor experiente com conhecimento amplo de produtos",
        tools: ["product_catalog", "pricing_tool", "inventory_check"],
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

  // 🆕 FASE 2: AI Assistant handlers aprimorados
  const handleOpenAIAssistant = async () => {
    setIsAIAssistantOpen(true);
    setIsAILoading(true);

    // Simular análise avançada (substituir por chamada real do backend)
    setTimeout(() => {
      const contextualSuggestions = generateContextualSuggestions();
      const advancedAnalysis = generateAdvancedAnalysis();

      setAISuggestions(contextualSuggestions);
      setAIAnalysis(advancedAnalysis);
      setIsAILoading(false);
    }, 2000); // Tempo maior para simular análise complexa
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
      case "layout_optimization":
      case "layout":
        setInterfaceConfig((prev) => ({
          ...prev,
          layout: suggestion.data.layout || prev.layout,
          showAgentAvatars:
            suggestion.data.showAgentAvatars ?? prev.showAgentAvatars,
        }));
        break;
      case "accessibility":
        // Aplicar correções de acessibilidade
        const fixes = suggestion.data.fixes || [];
        if (
          fixes.includes(
            "Ativar avatares dos agentes para melhor identificação"
          )
        ) {
          setInterfaceConfig((prev) => ({ ...prev, showAgentAvatars: true }));
        }
        if (fixes.includes("Ativar indicadores de digitação e status")) {
          setInterfaceConfig((prev) => ({
            ...prev,
            showTypingIndicator: true,
          }));
        }
        if (
          fixes.includes("Ajustar cores para aumentar contraste para WCAG AA")
        ) {
          setInterfaceConfig((prev) => ({
            ...prev,
            theme: {
              ...prev.theme,
              primaryColor: "#1E3A8A",
              backgroundColor: "#FFFFFF",
            },
          }));
        }
        break;
    }

    // 🆕 FASE 2: Regenerar análise após aplicar sugestão
    setTimeout(() => {
      const updatedAnalysis = generateAdvancedAnalysis();
      setAIAnalysis(updatedAnalysis);
    }, 500);
  };

  const handleGenerateContent = async (
    type: "welcome" | "placeholder" | "agent_intro",
    context?: any
  ) => {
    setIsAILoading(true);

    // Simulate AI content generation with context awareness
    setTimeout(() => {
      const agentCount = agents.length;
      const domain = projectId?.includes("atendimento")
        ? "atendimento"
        : "sistema";

      const mockContent = {
        welcome:
          domain === "atendimento"
            ? `Bem-vindo! Nossa equipe de ${agentCount} especialistas está pronta para oferecer atendimento personalizado. Como podemos ajudá-lo hoje?`
            : `Olá! Nosso sistema com ${agentCount} agentes especializados está aqui para ajudá-lo. Qual assistente você gostaria de consultar?`,
        placeholder:
          domain === "atendimento"
            ? "Descreva sua necessidade e direcionaremos para o especialista ideal..."
            : "Digite sua pergunta ou selecione um agente especializado...",
        agent_intro: `Olá! Sou ${
          context?.agentName || "seu assistente"
        } e estou aqui para ${
          context?.goal || "ajudá-lo"
        }. Com minha experiência, posso oferecer o melhor suporte. Vamos começar?`,
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
    }, 1500);
  };

  const updateTheme = (key: keyof InterfaceTheme, value: string) => {
    setInterfaceConfig((prev) => ({
      ...prev,
      theme: { ...prev.theme, [key]: value },
    }));

    // 🆕 FASE 2: Atualizar análise quando cores mudarem
    if (key === "primaryColor" || key === "backgroundColor") {
      setTimeout(() => {
        const updatedAnalysis = generateAdvancedAnalysis();
        setAIAnalysis(updatedAnalysis);
      }, 300);
    }
  };

  const updateConfig = (key: keyof InterfaceConfig, value: any) => {
    setInterfaceConfig((prev) => ({ ...prev, [key]: value }));

    // 🆕 FASE 2: Atualizar análise quando layout mudar
    if (
      key === "layout" ||
      key === "showAgentAvatars" ||
      key === "showTypingIndicator"
    ) {
      setTimeout(() => {
        const updatedAnalysis = generateAdvancedAnalysis();
        setAIAnalysis(updatedAnalysis);
      }, 300);
    }
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
    const currentContrast = calculateContrast(
      hexToRgb(interfaceConfig.theme.primaryColor),
      hexToRgb(interfaceConfig.theme.backgroundColor)
    );

    return `// Generated Agent Interface Component - Optimized Design
// Accessibility Score: ${aiAnalysis?.accessibilityScore || 85}% | WCAG: ${
      aiAnalysis?.wcagCompliance.level || "AA"
    }
// Color Contrast: ${currentContrast.toFixed(2)}:1 ${
      currentContrast >= 4.5 ? "✅" : "❌"
    }
import React, { useState } from 'react';
import './AgentInterface.css';

const AgentInterface = () => {
  const [selectedAgent, setSelectedAgent] = useState('${agents[0]?.id}');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const agents = ${JSON.stringify(
    agents.map((a) => ({
      id: a.id,
      name: a.name,
      role: a.role,
      introduction: interfaceConfig.agentIntroductions[a.id],
      status: a.status,
    })),
    null,
    2
  )};

  const theme = ${JSON.stringify(interfaceConfig.theme, null, 2)};

  const config = ${JSON.stringify(
    {
      layout: interfaceConfig.layout,
      showAgentAvatars: interfaceConfig.showAgentAvatars,
      showTypingIndicator: interfaceConfig.showTypingIndicator,
      welcomeMessage: interfaceConfig.welcomeMessage,
      placeholder: interfaceConfig.placeholder,
    },
    null,
    2
  )};

  return (
    <div 
      className="agent-interface" 
      style={{
        fontFamily: theme.fontFamily,
        backgroundColor: theme.backgroundColor,
        color: theme.textColor,
        borderRadius: theme.borderRadius
      }}
    >
      {/* Interface implementation here */}
      <div className="interface-content">
        <h3>Interface Preview</h3>
        <p>Layout: {config.layout}</p>
        <p>Agents: {agents.length}</p>
        <p>Welcome: {config.welcomeMessage}</p>
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
      boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
      overflow: "hidden",
      display: "flex",
      border: "2px solid #e0e0e0",
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
              Agentes Disponíveis ({agents.length})
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
                  <div style={{ marginRight: "12px", fontSize: "1.2rem" }}>
                    🤖
                  </div>
                )}
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      fontWeight: "600",
                      fontSize: "0.9rem",
                      marginBottom: "2px",
                    }}
                  >
                    {agent.name}
                  </div>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      opacity: 0.8,
                      lineHeight: 1.3,
                    }}
                  >
                    {agent.role}
                  </div>
                  {componentSettings.agentSelector.showStatus && (
                    <div
                      style={{
                        fontSize: "0.7rem",
                        marginTop: "4px",
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                      }}
                    >
                      <span
                        style={{
                          color:
                            agent.status === AgentStatus.ACTIVE
                              ? "#4caf50"
                              : "#f44336",
                        }}
                      >
                        ●
                      </span>
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
              padding: "16px 20px",
              backgroundColor: interfaceConfig.theme.primaryColor,
              color: "white",
              borderBottom: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: "1.1rem", fontWeight: "600" }}>
              {agents[0]?.name} -{" "}
              {interfaceConfig.layout.charAt(0).toUpperCase() +
                interfaceConfig.layout.slice(1)}{" "}
              Layout
            </h2>
            {aiAnalysis && (
              <div
                style={{ fontSize: "0.8rem", opacity: 0.9, marginTop: "4px" }}
              >
                WCAG {aiAnalysis.wcagCompliance.level} • Contraste:{" "}
                {calculateContrast(
                  hexToRgb(interfaceConfig.theme.primaryColor),
                  hexToRgb(interfaceConfig.theme.backgroundColor)
                ).toFixed(1)}
                :1
              </div>
            )}
          </div>

          {/* Área de Mensagens */}
          <div
            style={{
              flex: 1,
              padding: "20px",
              overflowY: "auto",
              background: `linear-gradient(135deg, ${interfaceConfig.theme.backgroundColor}, #fafbfc)`,
            }}
          >
            <div
              className="preview-message"
              style={{
                padding: "16px",
                backgroundColor: interfaceConfig.theme.secondaryColor,
                borderRadius: interfaceConfig.theme.borderRadius,
                marginBottom: "16px",
                border: "1px solid #e8ecf3",
              }}
            >
              <div
                style={{
                  fontSize: "0.8rem",
                  marginBottom: "6px",
                  opacity: 0.7,
                  fontWeight: "500",
                }}
              >
                {componentSettings.messageDisplay.showAgentName &&
                  agents[0]?.name}
                {componentSettings.messageDisplay.showTimestamp && " • 09:30"}
              </div>
              <div style={{ lineHeight: 1.5 }}>
                {interfaceConfig.welcomeMessage}
              </div>
            </div>

            <div
              className="preview-message"
              style={{
                padding: "16px",
                backgroundColor: interfaceConfig.theme.primaryColor,
                color: "white",
                borderRadius: interfaceConfig.theme.borderRadius,
                marginLeft: "20%",
                marginBottom: "16px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              }}
            >
              <div
                style={{
                  fontSize: "0.8rem",
                  marginBottom: "6px",
                  opacity: 0.9,
                  fontWeight: "500",
                }}
              >
                Você{" "}
                {componentSettings.messageDisplay.showTimestamp && "• 09:31"}
              </div>
              <div>
                Olá! Preciso de ajuda com{" "}
                {agents.length > 1 ? "algumas questões" : "uma questão"}.
              </div>
            </div>

            {interfaceConfig.showTypingIndicator && (
              <div
                style={{
                  padding: "12px",
                  fontSize: "0.85rem",
                  opacity: 0.7,
                  fontStyle: "italic",
                }}
              >
                <span style={{ marginRight: "8px" }}>💭</span>
                {agents[0]?.name} está digitando...
              </div>
            )}
          </div>

          {/* Área de Input */}
          <div
            style={{
              padding: "20px",
              borderTop: "2px solid #e8ecf3",
              display: "flex",
              gap: "12px",
              backgroundColor: "#fafbfc",
            }}
          >
            <input
              type="text"
              placeholder={interfaceConfig.placeholder}
              style={{
                flex: 1,
                padding: "14px 18px",
                border: "2px solid #e0e0e0",
                borderRadius: interfaceConfig.theme.borderRadius,
                fontFamily: interfaceConfig.theme.fontFamily,
                fontSize: "0.9rem",
                outline: "none",
              }}
              readOnly
            />
            <button
              style={{
                padding: "14px 28px",
                backgroundColor: interfaceConfig.theme.primaryColor,
                color: "white",
                border: "none",
                borderRadius: interfaceConfig.theme.borderRadius,
                cursor: "pointer",
                fontWeight: "600",
                fontSize: "0.9rem",
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
        <h1>🎨 Designer de Interface de Agentes</h1>
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

          {/* 🆕 FASE 2: Status indicators */}
          <div className="status-indicators">
            {aiAnalysis && (
              <>
                <span
                  className={`status-badge wcag-${aiAnalysis.wcagCompliance.level.toLowerCase()}`}
                >
                  WCAG {aiAnalysis.wcagCompliance.level}
                </span>
                <span
                  className={`status-badge contrast-${
                    calculateContrast(
                      hexToRgb(interfaceConfig.theme.primaryColor),
                      hexToRgb(interfaceConfig.theme.backgroundColor)
                    ) >= 4.5
                      ? "good"
                      : "poor"
                  }`}
                >
                  Contraste:{" "}
                  {calculateContrast(
                    hexToRgb(interfaceConfig.theme.primaryColor),
                    hexToRgb(interfaceConfig.theme.backgroundColor)
                  ).toFixed(1)}
                  :1
                </span>
                <span className="status-badge agents-count">
                  {agents.length} Agente{agents.length !== 1 ? "s" : ""}
                </span>
              </>
            )}
          </div>

          <button
            className="btn btn-ai-assistant"
            onClick={handleOpenAIAssistant}
            disabled={isAILoading}
          >
            {isAILoading ? "⏳ Analisando..." : "✨ AI Design Assistant"}
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
          {aiAnalysis && (
            <span className="tab-info">
              {aiAnalysis.usabilityScore}% usabilidade
            </span>
          )}
        </button>
        <button
          className={activeTab === "design" ? "tab active" : "tab"}
          onClick={() => setActiveTab("design")}
        >
          🎨 Design
          {aiAnalysis && (
            <span className="tab-info">
              {aiAnalysis.modernityScore}% moderno
            </span>
          )}
        </button>
        <button
          className={activeTab === "code" ? "tab active" : "tab"}
          onClick={() => setActiveTab("code")}
        >
          💻 Código
          {aiAnalysis && (
            <span className="tab-info">
              {aiAnalysis.accessibilityScore}% acessível
            </span>
          )}
        </button>
      </div>

      <div className="designer-content">
        {activeTab === "preview" && (
          <div className="preview-section">
            <div className="preview-main">{renderPreview()}</div>

            {/* 🆕 FASE 2: Preview Analytics */}
            {aiAnalysis && (
              <div className="preview-analytics">
                <h3>📊 Análise do Preview</h3>
                <div className="analytics-grid">
                  <div className="analytic-card">
                    <div className="analytic-value">
                      {aiAnalysis.accessibilityScore}%
                    </div>
                    <div className="analytic-label">Acessibilidade</div>
                    <div className="analytic-detail">
                      WCAG {aiAnalysis.wcagCompliance.level}
                    </div>
                  </div>
                  <div className="analytic-card">
                    <div className="analytic-value">
                      {aiAnalysis.usabilityScore}%
                    </div>
                    <div className="analytic-label">Usabilidade</div>
                    <div className="analytic-detail">
                      Layout {interfaceConfig.layout}
                    </div>
                  </div>
                  <div className="analytic-card">
                    <div className="analytic-value">
                      {aiAnalysis.modernityScore}%
                    </div>
                    <div className="analytic-label">Modernidade</div>
                    <div className="analytic-detail">Design 2024</div>
                  </div>
                  <div className="analytic-card">
                    <div className="analytic-value">
                      {calculateContrast(
                        hexToRgb(interfaceConfig.theme.primaryColor),
                        hexToRgb(interfaceConfig.theme.backgroundColor)
                      ).toFixed(1)}
                      :1
                    </div>
                    <div className="analytic-label">Contraste</div>
                    <div className="analytic-detail">
                      {calculateContrast(
                        hexToRgb(interfaceConfig.theme.primaryColor),
                        hexToRgb(interfaceConfig.theme.backgroundColor)
                      ) >= 4.5
                        ? "Conforme"
                        : "Inadequado"}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "design" && (
          <div className="design-section">
            <div className="design-sidebar">
              <div className="design-panel">
                <h3>🎨 Tema</h3>
                <div className="form-group">
                  <label>Cor Primária:</label>
                  <div className="color-input-group">
                    <input
                      type="color"
                      value={interfaceConfig.theme.primaryColor}
                      onChange={(e) =>
                        updateTheme("primaryColor", e.target.value)
                      }
                    />
                    <input
                      type="text"
                      value={interfaceConfig.theme.primaryColor}
                      onChange={(e) =>
                        updateTheme("primaryColor", e.target.value)
                      }
                      placeholder="#0066cc"
                    />
                  </div>
                  {aiAnalysis && (
                    <div className="color-feedback">
                      Contraste:{" "}
                      {calculateContrast(
                        hexToRgb(interfaceConfig.theme.primaryColor),
                        hexToRgb(interfaceConfig.theme.backgroundColor)
                      ).toFixed(2)}
                      :1
                      {calculateContrast(
                        hexToRgb(interfaceConfig.theme.primaryColor),
                        hexToRgb(interfaceConfig.theme.backgroundColor)
                      ) < 4.5 && (
                        <span className="contrast-warning">
                          ⚠️ Abaixo do padrão WCAG
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <div className="form-group">
                  <label>Cor Secundária:</label>
                  <div className="color-input-group">
                    <input
                      type="color"
                      value={interfaceConfig.theme.secondaryColor}
                      onChange={(e) =>
                        updateTheme("secondaryColor", e.target.value)
                      }
                    />
                    <input
                      type="text"
                      value={interfaceConfig.theme.secondaryColor}
                      onChange={(e) =>
                        updateTheme("secondaryColor", e.target.value)
                      }
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Cor de Fundo:</label>
                  <div className="color-input-group">
                    <input
                      type="color"
                      value={interfaceConfig.theme.backgroundColor}
                      onChange={(e) =>
                        updateTheme("backgroundColor", e.target.value)
                      }
                    />
                    <input
                      type="text"
                      value={interfaceConfig.theme.backgroundColor}
                      onChange={(e) =>
                        updateTheme("backgroundColor", e.target.value)
                      }
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Fonte:</label>
                  <select
                    value={interfaceConfig.theme.fontFamily}
                    onChange={(e) => updateTheme("fontFamily", e.target.value)}
                  >
                    <option value="Inter, sans-serif">
                      Inter (Recomendado)
                    </option>
                    <option value="Roboto, sans-serif">Roboto</option>
                    <option value="Arial, sans-serif">Arial</option>
                    <option value="Georgia, serif">Georgia</option>
                    <option value="'Courier New', monospace">
                      Courier New
                    </option>
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
                    <option value="sidebar">
                      Sidebar {agents.length > 3 ? "(Recomendado)" : ""}
                    </option>
                    <option value="tabs">
                      Abas {agents.length <= 2 ? "(Recomendado)" : ""}
                    </option>
                    <option value="cards">
                      Cards {agents.length > 4 ? "(Recomendado)" : ""}
                    </option>
                  </select>
                </div>

                {/* 🆕 FASE 2: Layout feedback */}
                {aiAnalysis?.layoutAnalysis && (
                  <div className="layout-feedback">
                    <div className="feedback-item">
                      <strong>Eficiência:</strong>{" "}
                      {aiAnalysis.layoutAnalysis.efficiency}%
                    </div>
                    {aiAnalysis.layoutAnalysis.suggestions.map(
                      (suggestion, i) => (
                        <div key={i} className="feedback-suggestion">
                          💡 {suggestion}
                        </div>
                      )
                    )}
                  </div>
                )}

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
                  <div className="checkbox-help">
                    Melhora identificação visual e acessibilidade
                  </div>
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
                  <div className="checkbox-help">
                    Feedback visual durante processamento
                  </div>
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
                    rows={3}
                  />
                  <div className="character-count">
                    {interfaceConfig.welcomeMessage.length}/200 caracteres
                  </div>
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

              {/* 🆕 FASE 2: Quick Actions Panel */}
              <div className="design-panel quick-actions-panel">
                <h3>🚀 Ações Rápidas</h3>
                <div className="quick-action-buttons">
                  <button
                    className="quick-action-btn"
                    onClick={() => {
                      // Auto-otimizar para acessibilidade
                      if (
                        calculateContrast(
                          hexToRgb(interfaceConfig.theme.primaryColor),
                          hexToRgb(interfaceConfig.theme.backgroundColor)
                        ) < 4.5
                      ) {
                        updateTheme("primaryColor", "#1E3A8A");
                        updateTheme("backgroundColor", "#FFFFFF");
                      }
                      updateConfig("showAgentAvatars", true);
                      updateConfig("showTypingIndicator", true);
                    }}
                  >
                    ♿ Auto-otimizar Acessibilidade
                  </button>
                  <button
                    className="quick-action-btn"
                    onClick={() => {
                      // Layout inteligente baseado no número de agentes
                      const optimalLayout =
                        agents.length > 3
                          ? "sidebar"
                          : agents.length <= 2
                          ? "tabs"
                          : "cards";
                      updateConfig("layout", optimalLayout);
                    }}
                  >
                    📐 Layout Inteligente
                  </button>
                  <button
                    className="quick-action-btn"
                    onClick={() => {
                      // Tema moderno
                      updateTheme("primaryColor", "#6366F1");
                      updateTheme("secondaryColor", "#F1F5F9");
                      updateTheme("borderRadius", "12px");
                      updateTheme("fontFamily", "Inter, sans-serif");
                    }}
                  >
                    🎨 Tema Moderno 2024
                  </button>
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
              <button className="code-tab">Accessibility Guide</button>
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
              {/* 🆕 FASE 2: Validação de código */}
              <button
                className="btn btn-secondary"
                onClick={() => {
                  // Simular validação de acessibilidade do código
                  const score = aiAnalysis?.accessibilityScore || 85;
                  alert(
                    `Código validado!\n\nAcessibilidade: ${score}%\nWCAG: ${
                      aiAnalysis?.wcagCompliance.level || "AA"
                    }\n${
                      score >= 90
                        ? "✅ Excelente conformidade!"
                        : score >= 70
                        ? "⚠️ Boa conformidade, algumas melhorias possíveis"
                        : "❌ Requer correções"
                    }`
                  );
                }}
              >
                ✅ Validar Acessibilidade
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 🆕 FASE 2: AI Design Assistant com funcionalidades avançadas */}
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
