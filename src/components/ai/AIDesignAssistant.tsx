// src/components/ai/AIDesignAssistant.tsx - FASE 2 COMPLETA
import React, { useState, useEffect } from "react";
import { Agent } from "../../types";
import "./AIDesignAssistant.css";

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
  applied?: boolean;
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
// 🆕 FASE 3: Interfaces para A/B Testing e Análise Avançada
interface ABTestVariant {
  id: string;
  name: string;
  config: InterfaceConfig;
  metrics: {
    usabilityScore: number;
    engagementRate: number;
    taskCompletionTime: number;
    userSatisfaction: number;
  };
  userFeedback: string[];
}

interface UsabilityReport {
  id: string;
  timestamp: Date;
  overallScore: number;
  detailedAnalysis: {
    cognitiveLoad: number;
    taskEfficiency: number;
    errorPrevention: number;
    learnability: number;
  };
  recommendations: {
    priority: "high" | "medium" | "low";
    action: string;
    impact: string;
    effort: string;
  }[];
  exportFormats: ("pdf" | "excel" | "json")[];
}

interface InterfaceConfig {
  theme: {
    primaryColor: string;
    secondaryColor: string;
    backgroundColor: string;
    textColor: string;
    borderRadius: string;
    fontFamily: string;
  };
  layout: "sidebar" | "tabs" | "cards";
  showAgentAvatars: boolean;
  showTypingIndicator: boolean;
  enableVoiceInput: boolean;
  welcomeMessage: string;
  placeholder: string;
  agentIntroductions: Record<string, string>;
}

interface LayoutSuggestion {
  type: "sidebar" | "tabs" | "cards" | "grid";
  pros: string[];
  cons: string[];
  suitableFor: string[];
  mockup: string;
}

interface AIDesignAssistantProps {
  isOpen: boolean;
  onClose: () => void;
  suggestions: AISuggestion[];
  analysis: AIAnalysis | null;
  isLoading: boolean;
  onApplySuggestion: (suggestion: AISuggestion) => void;
  onGenerateContent: (
    type: "welcome" | "placeholder" | "agent_intro",
    context?: any
  ) => void;
  currentConfig: InterfaceConfig;
  agents: Agent[];
  projectId: string;
  // 🆕 FASE 3: Novas props
  onRunABTest?: (variants: ABTestVariant[]) => void;
  onGenerateReport?: (format: "pdf" | "excel" | "json") => void;
  enableAdvancedAnalysis?: boolean;
}

const AIDesignAssistant: React.FC<AIDesignAssistantProps> = ({
  isOpen,
  onClose,
  suggestions,
  analysis,
  isLoading,
  onApplySuggestion,
  onGenerateContent,
  currentConfig,
  agents,
  projectId,
}) => {
  const [activeAssistantTab, setActiveAssistantTab] = useState<
    "suggestions" | "analysis" | "generate" | "layout" | "abtest" | "reports"
  >("suggestions");
  const [appliedSuggestions, setAppliedSuggestions] = useState<Set<string>>(
    new Set()
  );
  const [chatMessages, setChatMessages] = useState<
    Array<{
      id: string;
      role: "user" | "assistant";
      content: string;
      timestamp: Date;
    }>
  >([]);
  const [chatInput, setChatInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [layoutSuggestions, setLayoutSuggestions] = useState<
    LayoutSuggestion[]
  >([]);
  const [selectedLayoutPreview, setSelectedLayoutPreview] =
    useState<string>("sidebar");
  // 🆕 FASE 3: Estados para funcionalidades avançadas
  const [abTestVariants, setAbTestVariants] = useState<ABTestVariant[]>([]);
  const [isRunningABTest, setIsRunningABTest] = useState(false);
  const [usabilityReport, setUsabilityReport] =
    useState<UsabilityReport | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [abTestResults, setAbTestResults] = useState<any>(null);
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
      fixes.push("Ajustar cores para aumentar contraste");
    }

    // Análise de tamanho de elementos
    if (!config.showAgentAvatars) {
      issues.push("Elementos visuais insuficientes para identificação");
      fixes.push("Adicionar avatares ou ícones identificadores");
    }

    // Análise de feedback
    if (!config.showTypingIndicator) {
      issues.push("Falta de feedback durante processamento");
      fixes.push("Ativar indicadores de status/carregamento");
    }

    return {
      level:
        issues.length === 0
          ? "AAA"
          : issues.length < 3
          ? "AA"
          : "Non-compliant",
      issues,
      fixes,
    };
  };

  // 🆕 FASE 2: Análise de layout inteligente
  const generateLayoutSuggestions = (): LayoutSuggestion[] => {
    const agentCount = agents.length;

    const suggestions: LayoutSuggestion[] = [
      {
        type: "sidebar",
        pros: [
          "Espaço dedicado para agentes",
          "Fácil navegação",
          "Visão geral constante",
        ],
        cons: ["Menos espaço para chat em telas pequenas"],
        suitableFor: [
          "Múltiplos agentes",
          "Uso desktop",
          "Necessidade de contexto",
        ],
        mockup: "sidebar-layout",
      },
      {
        type: "tabs",
        pros: ["Máximo espaço para chat", "Interface limpa", "Fácil troca"],
        cons: ["Agentes não visíveis simultaneamente"],
        suitableFor: [
          "Poucos agentes especializados",
          "Mobile-first",
          "Foco na conversa",
        ],
        mockup: "tabs-layout",
      },
      {
        type: "cards",
        pros: [
          "Descoberta intuitiva",
          "Visual atrativo",
          "Informações contextuais",
        ],
        cons: ["Requer mais cliques", "Pode ser confuso com muitos agentes"],
        suitableFor: [
          "Primeira vez",
          "Diferentes capacidades",
          "Interfaces de descoberta",
        ],
        mockup: "cards-layout",
      },
    ];

    // Recomendação baseada no número de agentes
    if (agentCount <= 2) {
      suggestions[1].pros.push(
        "⭐ RECOMENDADO para " + agentCount + " agente(s)"
      );
    } else if (agentCount <= 4) {
      suggestions[0].pros.push(
        "⭐ RECOMENDADO para " + agentCount + " agentes"
      );
    } else {
      suggestions[2].pros.push(
        "⭐ RECOMENDADO para " + agentCount + "+ agentes"
      );
    }

    return suggestions;
  };

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

  // 🆕 FASE 2: Chat inteligente com contexto
  const handleSendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user" as const,
      content: chatInput,
      timestamp: new Date(),
    };

    setChatMessages((prev) => [...prev, userMessage]);
    setChatInput("");
    setIsTyping(true);

    // Simular chamada backend com análise contextual
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        role: "assistant" as const,
        content: generateContextualAIResponse(chatInput),
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  // 🆕 FASE 2: Respostas contextuais baseadas na configuração atual
  const generateContextualAIResponse = (input: string): string => {
    const lowerInput = input.toLowerCase();
    const agentCount = agents.length;
    const currentLayout = currentConfig.layout;
    const primaryColor = currentConfig.theme.primaryColor;

    // Análise contextual avançada
    if (lowerInput.includes("acessibilidade") || lowerInput.includes("wcag")) {
      const wcag = analyzeAccessibility(currentConfig);
      return (
        `Analisando acessibilidade WCAG da sua interface atual:\n\n` +
        `📊 **Status**: ${
          wcag.level === "AA"
            ? "✅ Conforme WCAG AA"
            : wcag.level === "AAA"
            ? "🏆 Conforme WCAG AAA"
            : "⚠️ Não conforme"
        }\n\n` +
        `${
          wcag.issues.length > 0
            ? `🔍 **Problemas encontrados**:\n${wcag.issues
                .map((issue) => `• ${issue}`)
                .join("\n")}\n\n`
            : ""
        }` +
        `${
          wcag.fixes.length > 0
            ? `💡 **Correções sugeridas**:\n${wcag.fixes
                .map((fix) => `• ${fix}`)
                .join("\n")}\n\n`
            : ""
        }` +
        `Quer que eu implemente essas correções automaticamente?`
      );
    }

    if (lowerInput.includes("layout") || lowerInput.includes("organiz")) {
      const layouts = generateLayoutSuggestions();
      const recommendation = layouts.find((l) =>
        l.pros.some((pro) => pro.includes("RECOMENDADO"))
      );

      return (
        `Analisando o layout ideal para ${agentCount} agente(s):\n\n` +
        `📋 **Layout atual**: ${currentLayout}\n` +
        `🎯 **Recomendação**: ${recommendation?.type || "sidebar"}\n\n` +
        `**Porque recomendo isso:**\n` +
        `${
          recommendation?.pros
            .filter((pro) => !pro.includes("RECOMENDADO"))
            .map((pro) => `• ${pro}`)
            .join("\n") || ""
        }\n\n` +
        `**Outras opções disponíveis:** tabs, cards, grid\n\n` +
        `Quer ver uma prévia do layout recomendado?`
      );
    }

    if (
      lowerInput.includes("cor") ||
      lowerInput.includes("color") ||
      lowerInput.includes("contraste")
    ) {
      const rgb1 = hexToRgb(primaryColor);
      const rgb2 = hexToRgb(currentConfig.theme.backgroundColor);
      const contrast = calculateContrast(rgb1, rgb2);

      return (
        `Analisando as cores da sua interface:\n\n` +
        `🎨 **Cor primária atual**: ${primaryColor}\n` +
        `📊 **Contraste**: ${contrast.toFixed(2)}:1 ${
          contrast >= 4.5 ? "✅" : "❌"
        }\n` +
        `⚖️ **Status WCAG**: ${
          contrast >= 7
            ? "AAA (Excelente)"
            : contrast >= 4.5
            ? "AA (Bom)"
            : "Não conforme"
        }\n\n` +
        `${
          contrast < 4.5
            ? `🔧 **Sugestões de melhoria**:\n• Escurecer cor primária\n• Clarear cor de fundo\n• Usar cores com maior diferença de luminosidade\n\n`
            : "✨ Suas cores têm contraste adequado!\n\n"
        }` +
        `Quer que eu sugira uma paleta otimizada para seu projeto de ${
          projectId ? "atendimento" : "sistema"
        }?`
      );
    }

    if (lowerInput.includes("mobile") || lowerInput.includes("responsiv")) {
      return (
        `Otimizações para mobile/responsividade:\n\n` +
        `📱 **Layout atual**: ${
          currentLayout === "sidebar"
            ? "Pode ser problemático em mobile"
            : "Adequado para mobile"
        }\n\n` +
        `🔧 **Recomendações específicas**:\n` +
        `• ${
          currentLayout === "sidebar"
            ? "Converter sidebar em drawer retrátil"
            : "✅ Layout já adequado"
        }\n` +
        `• Aumentar área de toque dos agentes (44px+)\n` +
        `• Otimizar tamanho da fonte (16px+ para inputs)\n` +
        `• Simplificar navegação em telas pequenas\n\n` +
        `🎯 **Melhor estratégia**: ${
          agentCount <= 2
            ? "Tabs horizontais"
            : "Menu hambúrguer + lista vertical"
        }\n\n` +
        `Implemento essas otimizações para você?`
      );
    }

    // Resposta padrão contextual
    return (
      `Entendi! Analisando sua configuração atual:\n\n` +
      `👥 **${agentCount} agente(s)** configurado(s)\n` +
      `🎨 **Layout**: ${currentLayout}\n` +
      `🎯 **Domínio**: ${
        projectId ? "Sistema personalizado" : "Não identificado"
      }\n\n` +
      `Posso ajudar você com:\n` +
      `• 🎨 Análise e otimização de cores\n` +
      `• 📱 Layout responsivo para diferentes telas\n` +
      `• ♿ Melhorias de acessibilidade WCAG\n` +
      `• 🔧 Personalização baseada no seu domínio\n\n` +
      `O que gostaria de melhorar primeiro?`
    );
  };

  // 🆕 FASE 2: Aplicar sugestão com feedback visual
  const handleApplySuggestion = (suggestion: AISuggestion) => {
    onApplySuggestion(suggestion);
    setAppliedSuggestions((prev) => {
      const newSet = new Set(prev);
      newSet.add(suggestion.id);
      return newSet;
    });

    // Feedback via chat
    const feedbackMessage = {
      id: Date.now().toString(),
      role: "assistant" as const,
      content: `✅ Sugestão "${suggestion.title}" aplicada com sucesso!\n\nO que você achou do resultado? Posso fazer mais ajustes se necessário.`,
      timestamp: new Date(),
    };
    setChatMessages((prev) => [...prev, feedbackMessage]);
  };

  // 🆕 FASE 2: Inicializar sugestões de layout
  useEffect(() => {
    if (isOpen && !isLoading) {
      setLayoutSuggestions(generateLayoutSuggestions());
    }
  }, [isOpen, isLoading, agents.length]);

  if (!isOpen) return null;

  // 🆕 FASE 2: Aba de Layout Analysis
  const renderLayoutTab = () => (
    <div className="ai-layout-analysis">
      <div className="layout-header">
        <h3>📐 Análise de Layout</h3>
        <p>Otimização baseada no número de agentes e caso de uso</p>
      </div>

      <div className="current-layout-analysis">
        <h4>Layout Atual: {currentConfig.layout}</h4>
        <div className="layout-metrics">
          <div className="metric">
            <span className="metric-label">Agentes:</span>
            <span className="metric-value">{agents.length}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Eficiência:</span>
            <span className="metric-value">
              {currentConfig.layout === "sidebar" && agents.length > 2
                ? "85%"
                : currentConfig.layout === "tabs" && agents.length <= 2
                ? "90%"
                : "75%"}
            </span>
          </div>
        </div>
      </div>

      <div className="layout-suggestions">
        <h4>💡 Sugestões de Layout</h4>
        {layoutSuggestions.map((layout) => (
          <div
            key={layout.type}
            className={`layout-suggestion-card ${
              layout.type === currentConfig.layout ? "current" : ""
            }`}
          >
            <div className="layout-header">
              <h5>
                {layout.type.charAt(0).toUpperCase() + layout.type.slice(1)}
              </h5>
              {layout.pros.some((pro) => pro.includes("RECOMENDADO")) && (
                <span className="recommended-badge">⭐ Recomendado</span>
              )}
            </div>

            <div className="layout-details">
              <div className="pros-cons">
                <div className="pros">
                  <h6>✅ Vantagens:</h6>
                  <ul>
                    {layout.pros
                      .filter((pro) => !pro.includes("RECOMENDADO"))
                      .map((pro, i) => (
                        <li key={i}>{pro}</li>
                      ))}
                  </ul>
                </div>
                <div className="cons">
                  <h6>⚠️ Limitações:</h6>
                  <ul>
                    {layout.cons.map((con, i) => (
                      <li key={i}>{con}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="suitable-for">
                <h6>🎯 Ideal para:</h6>
                <div className="tags">
                  {layout.suitableFor.map((tag, i) => (
                    <span key={i} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {layout.type !== currentConfig.layout && (
              <button
                className="btn-apply-layout"
                onClick={() =>
                  onApplySuggestion({
                    id: `layout_${layout.type}`,
                    type: "layout_optimization",
                    title: `Layout ${layout.type}`,
                    description: `Mudar para layout ${layout.type}`,
                    data: { layout: layout.type },
                    confidence: 0.9,
                  })
                }
              >
                🔄 Aplicar Layout
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="layout-preview">
        <h4>👁️ Prévia Comparativa</h4>
        <div className="preview-selector">
          {layoutSuggestions.map((layout) => (
            <button
              key={layout.type}
              className={`preview-btn ${
                selectedLayoutPreview === layout.type ? "active" : ""
              }`}
              onClick={() => setSelectedLayoutPreview(layout.type)}
            >
              {layout.type}
            </button>
          ))}
        </div>
        <div className="layout-mockup">
          <div className={`mockup mockup-${selectedLayoutPreview}`}>
            {selectedLayoutPreview === "sidebar" && (
              <LayoutMockupSidebar agents={agents} />
            )}
            {selectedLayoutPreview === "tabs" && (
              <LayoutMockupTabs agents={agents} />
            )}
            {selectedLayoutPreview === "cards" && (
              <LayoutMockupCards agents={agents} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
  // 🆕 FASE 3: Aba de A/B Testing
  const renderABTestTab = () => (
    <div className="ai-abtest">
      <div className="abtest-header">
        <h3>🧪 A/B Testing de Interface</h3>
        <p>Compare diferentes versões e otimize baseado em dados reais</p>
      </div>

      {!isRunningABTest && abTestVariants.length === 0 && (
        <div className="abtest-start">
          <div className="abtest-info">
            <h4>Como funciona o A/B Testing?</h4>
            <ul>
              <li>🎯 Criamos 3 variações da sua interface automaticamente</li>
              <li>
                📊 Simulamos métricas de usabilidade baseadas em boas práticas
              </li>
              <li>🏆 Identificamos a versão com melhor performance</li>
              <li>📈 Fornecemos dados para tomada de decisão</li>
            </ul>
          </div>

          <button className="btn-start-abtest" onClick={handleRunABTest}>
            🚀 Iniciar Teste A/B
          </button>
        </div>
      )}

      {isRunningABTest && (
        <div className="abtest-running">
          <div className="test-progress">
            <div className="progress-spinner"></div>
            <h4>Executando Teste A/B...</h4>
            <p>Gerando variações e simulando métricas de usabilidade</p>
          </div>
        </div>
      )}

      {abTestVariants.length > 0 && !isRunningABTest && (
        <div className="abtest-results">
          <div className="variants-comparison">
            {abTestVariants.map((variant, index) => (
              <div
                key={variant.id}
                className={`variant-card ${
                  abTestResults?.winner.id === variant.id ? "winner" : ""
                }`}
              >
                <div className="variant-header">
                  <h4>{variant.name}</h4>
                  {abTestResults?.winner.id === variant.id && (
                    <span className="winner-badge">🏆 Vencedor</span>
                  )}
                </div>

                <div className="variant-metrics">
                  <div className="metric">
                    <span className="metric-label">Usabilidade:</span>
                    <span className="metric-value">
                      {variant.metrics.usabilityScore}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Engajamento:</span>
                    <span className="metric-value">
                      {(variant.metrics.engagementRate * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Tempo Tarefa:</span>
                    <span className="metric-value">
                      {variant.metrics.taskCompletionTime}s
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Satisfação:</span>
                    <span className="metric-value">
                      {variant.metrics.userSatisfaction}/5
                    </span>
                  </div>
                </div>

                <button
                  className="btn-apply-variant"
                  onClick={() =>
                    onApplySuggestion({
                      id: `variant_${variant.id}`,
                      type: "layout_optimization",
                      title: `Aplicar ${variant.name}`,
                      description: "Design otimizado via A/B Testing",
                      data: variant.config,
                      confidence: 0.95,
                    })
                  }
                >
                  ✨ Aplicar Design
                </button>
              </div>
            ))}
          </div>

          {abTestResults && (
            <div className="test-summary">
              <h4>📊 Resultados do Teste</h4>
              <div className="summary-stats">
                <div className="stat">
                  <strong>Confiança:</strong> {abTestResults.confidence}%
                </div>
                <div className="stat">
                  <strong>Duração:</strong> {abTestResults.duration}
                </div>
                <div className="stat">
                  <strong>Amostra:</strong> {abTestResults.sampleSize} usuários
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  // 🆕 FASE 3: Aba de Relatórios
  const renderReportsTab = () => (
    <div className="ai-reports">
      <div className="reports-header">
        <h3>📊 Relatórios de Usabilidade</h3>
        <p>Análises detalhadas e exportação profissional</p>
      </div>

      <div className="report-generation">
        <h4>🔍 Análise Completa</h4>
        <p>Gere um relatório detalhado com todas as métricas e recomendações</p>

        <div className="export-options">
          <button
            className="export-btn pdf"
            onClick={() => handleGenerateReport("pdf")}
            disabled={isGeneratingReport}
          >
            📄 Exportar PDF
          </button>
          <button
            className="export-btn excel"
            onClick={() => handleGenerateReport("excel")}
            disabled={isGeneratingReport}
          >
            📊 Exportar Excel
          </button>
          <button
            className="export-btn json"
            onClick={() => handleGenerateReport("json")}
            disabled={isGeneratingReport}
          >
            💾 Exportar JSON
          </button>
        </div>

        {isGeneratingReport && (
          <div className="generating-report">
            <div className="progress-spinner"></div>
            <p>Gerando relatório detalhado...</p>
          </div>
        )}
      </div>

      {usabilityReport && (
        <div className="report-preview">
          <h4>📋 Prévia do Relatório</h4>

          <div className="report-summary">
            <div className="overall-score">
              <span className="score-value">
                {usabilityReport.overallScore}%
              </span>
              <span className="score-label">Score Geral</span>
            </div>

            <div className="detailed-scores">
              <div className="score-item">
                <span className="label">Carga Cognitiva:</span>
                <span className="value">
                  {usabilityReport.detailedAnalysis.cognitiveLoad}%
                </span>
              </div>
              <div className="score-item">
                <span className="label">Eficiência:</span>
                <span className="value">
                  {usabilityReport.detailedAnalysis.taskEfficiency}%
                </span>
              </div>
              <div className="score-item">
                <span className="label">Prevenção Erros:</span>
                <span className="value">
                  {usabilityReport.detailedAnalysis.errorPrevention}%
                </span>
              </div>
              <div className="score-item">
                <span className="label">Aprendizado:</span>
                <span className="value">
                  {usabilityReport.detailedAnalysis.learnability}%
                </span>
              </div>
            </div>
          </div>

          <div className="recommendations-preview">
            <h5>🎯 Principais Recomendações</h5>
            {usabilityReport.recommendations.map((rec, index) => (
              <div
                key={index}
                className={`recommendation priority-${rec.priority}`}
              >
                <div className="rec-header">
                  <span className={`priority-badge ${rec.priority}`}>
                    {rec.priority === "high"
                      ? "🔥"
                      : rec.priority === "medium"
                      ? "⚡"
                      : "💡"}
                    {rec.priority.toUpperCase()}
                  </span>
                  <span className="rec-action">{rec.action}</span>
                </div>
                <div className="rec-details">
                  <span className="impact">Impacto: {rec.impact}</span>
                  <span className="effort">Esforço: {rec.effort}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
  // 🆕 FASE 2: Aba de Sugestões Aprimorada
  const renderSuggestionsTab = () => (
    <div className="ai-suggestions">
      <div className="suggestions-header">
        <h3>💡 Sugestões Inteligentes</h3>
        <p>
          Baseado na análise dos seus {agents.length} agentes e configuração
          atual
        </p>
      </div>

      {isLoading ? (
        <div className="ai-loading">
          <div className="loading-spinner"></div>
          <p>Analisando interface e gerando sugestões personalizadas...</p>
        </div>
      ) : (
        <div className="suggestions-list">
          {suggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className={`suggestion-card ${
                appliedSuggestions.has(suggestion.id) ? "applied" : ""
              }`}
            >
              <div className="suggestion-header">
                <h4>{suggestion.title}</h4>
                <div className="suggestion-badges">
                  <div className="confidence-badge">
                    {Math.round(suggestion.confidence * 100)}% confiança
                  </div>
                  {appliedSuggestions.has(suggestion.id) && (
                    <div className="applied-badge">✅ Aplicado</div>
                  )}
                </div>
              </div>
              <p className="suggestion-description">{suggestion.description}</p>

              {suggestion.type === "color_palette" && (
                <>
                  <div className="color-preview">
                    <div
                      className="color-swatch"
                      style={{ backgroundColor: suggestion.data.primaryColor }}
                      title="Cor Primária"
                    ></div>
                    <div
                      className="color-swatch"
                      style={{
                        backgroundColor: suggestion.data.secondaryColor,
                      }}
                      title="Cor Secundária"
                    ></div>
                    <div
                      className="color-swatch"
                      style={{
                        backgroundColor: suggestion.data.backgroundColor,
                      }}
                      title="Cor de Fundo"
                    ></div>
                  </div>
                  <div className="color-analysis">
                    <small>
                      Contraste:{" "}
                      {calculateContrast(
                        hexToRgb(suggestion.data.primaryColor),
                        hexToRgb(suggestion.data.backgroundColor)
                      ).toFixed(2)}
                      :1
                    </small>
                  </div>
                </>
              )}

              {suggestion.type === "content" && (
                <div className="content-preview">
                  <div className="preview-text">
                    "{suggestion.data.welcomeMessage}"
                  </div>
                </div>
              )}

              {suggestion.type === "accessibility" && (
                <div className="accessibility-preview">
                  <div className="accessibility-fixes">
                    <strong>Melhorias:</strong>
                    <ul>
                      {suggestion.data.fixes?.map((fix: string, i: number) => (
                        <li key={i}>{fix}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              <button
                className="btn-apply-suggestion"
                onClick={() => handleApplySuggestion(suggestion)}
                disabled={appliedSuggestions.has(suggestion.id)}
              >
                {appliedSuggestions.has(suggestion.id)
                  ? "✅ Aplicado"
                  : "✨ Aplicar Sugestão"}
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="quick-actions">
        <h4>🚀 Ações Rápidas</h4>
        <div className="quick-buttons">
          <button
            className="quick-btn"
            onClick={() => {
              // Gerar sugestão de acessibilidade
              const wcag = analyzeAccessibility(currentConfig);
              if (wcag.fixes.length > 0) {
                handleApplySuggestion({
                  id: `accessibility_${Date.now()}`,
                  type: "accessibility",
                  title: "Correções de Acessibilidade",
                  description: `${wcag.fixes.length} melhorias para conformidade WCAG`,
                  data: { fixes: wcag.fixes, level: wcag.level },
                  confidence: 0.95,
                });
              }
            }}
          >
            ♿ Corrigir Acessibilidade
          </button>
          <button
            className="quick-btn"
            onClick={() => {
              // Força análise de layout
              const layouts = generateLayoutSuggestions();
              const recommended = layouts.find((l) =>
                l.pros.some((pro) => pro.includes("RECOMENDADO"))
              );
              if (recommended && recommended.type !== currentConfig.layout) {
                handleApplySuggestion({
                  id: `quick_layout_${Date.now()}`,
                  type: "layout_optimization",
                  title: `Layout Otimizado: ${recommended.type}`,
                  description: `Recomendado para ${agents.length} agentes`,
                  data: { layout: recommended.type },
                  confidence: 0.88,
                });
              }
            }}
          >
            📐 Otimizar Layout
          </button>
          <button
            className="quick-btn"
            onClick={() => {
              // Análise de contraste e sugestão
              const rgb1 = hexToRgb(currentConfig.theme.primaryColor);
              const rgb2 = hexToRgb(currentConfig.theme.backgroundColor);
              const contrast = calculateContrast(rgb1, rgb2);
              if (contrast < 4.5) {
                // Gerar cores com melhor contraste
                handleApplySuggestion({
                  id: `contrast_fix_${Date.now()}`,
                  type: "color_palette",
                  title: "Correção de Contraste",
                  description: `Melhorar contraste de ${contrast.toFixed(
                    2
                  )}:1 para 4.5:1+`,
                  data: {
                    primaryColor: "#1E3A8A", // Azul mais escuro
                    secondaryColor: currentConfig.theme.secondaryColor,
                    backgroundColor: "#FFFFFF",
                    textColor: "#1F2937",
                  },
                  confidence: 0.91,
                });
              }
            }}
          >
            🎨 Corrigir Contraste
          </button>
          <button
            className="quick-btn"
            onClick={() => {
              setChatInput("Como otimizar esta interface para mobile?");
              handleSendChatMessage();
            }}
          >
            📱 Melhorar Mobile
          </button>
        </div>
      </div>
    </div>
  );

  // 🆕 FASE 2: Aba de Análise Aprimorada
  const renderAnalysisTab = () => {
    const wcag = analysis
      ? analysis.wcagCompliance
      : analyzeAccessibility(currentConfig);
    const colorContrast = analysis?.colorContrast || {
      ratio: calculateContrast(
        hexToRgb(currentConfig.theme.primaryColor),
        hexToRgb(currentConfig.theme.backgroundColor)
      ),
      passes: true,
      recommendations: [],
    };
    colorContrast.passes = colorContrast.ratio >= 4.5;

    return (
      <div className="ai-analysis">
        <div className="analysis-header">
          <h3>📊 Análise Avançada da Interface</h3>
          <p>Avaliação detalhada incluindo WCAG, contraste e usabilidade</p>
        </div>

        {isLoading || !analysis ? (
          <div className="ai-loading">
            <div className="loading-spinner"></div>
            <p>
              Executando análise completa de acessibilidade e usabilidade...
            </p>
          </div>
        ) : (
          <>
            <div className="score-cards">
              <div className="score-card">
                <div className="score-value">
                  {analysis.accessibilityScore}%
                </div>
                <div className="score-label">Acessibilidade</div>
                <div className="score-details">WCAG {wcag.level}</div>
                <div
                  className={`score-indicator ${
                    analysis.accessibilityScore >= 80
                      ? "good"
                      : analysis.accessibilityScore >= 60
                      ? "average"
                      : "poor"
                  }`}
                ></div>
              </div>
              <div className="score-card">
                <div className="score-value">{analysis.usabilityScore}%</div>
                <div className="score-label">Usabilidade</div>
                <div className="score-details">{agents.length} agentes</div>
                <div
                  className={`score-indicator ${
                    analysis.usabilityScore >= 80
                      ? "good"
                      : analysis.usabilityScore >= 60
                      ? "average"
                      : "poor"
                  }`}
                ></div>
              </div>
              <div className="score-card">
                <div className="score-value">{analysis.modernityScore}%</div>
                <div className="score-label">Modernidade</div>
                <div className="score-details">Design 2024</div>
                <div
                  className={`score-indicator ${
                    analysis.modernityScore >= 80
                      ? "good"
                      : analysis.modernityScore >= 60
                      ? "average"
                      : "poor"
                  }`}
                ></div>
              </div>
            </div>

            {/* 🆕 FASE 2: Seção de Contraste Detalhada */}
            <div className="contrast-analysis">
              <h4>🎨 Análise de Contraste</h4>
              <div className="contrast-card">
                <div className="contrast-visual">
                  <div
                    className="contrast-sample"
                    style={{
                      backgroundColor: currentConfig.theme.primaryColor,
                      color: currentConfig.theme.backgroundColor,
                    }}
                  >
                    Texto de Exemplo
                  </div>
                  <div className="contrast-ratio">
                    {colorContrast.ratio.toFixed(2)}:1
                  </div>
                </div>
                <div className="contrast-details">
                  <div
                    className={`contrast-status ${
                      colorContrast.passes ? "pass" : "fail"
                    }`}
                  >
                    {colorContrast.passes
                      ? "✅ Conforme WCAG"
                      : "❌ Não conforme"}
                  </div>
                  <div className="contrast-level">
                    {colorContrast.ratio >= 7
                      ? "AAA (Excelente)"
                      : colorContrast.ratio >= 4.5
                      ? "AA (Bom)"
                      : "Abaixo do padrão"}
                  </div>
                </div>
              </div>
            </div>

            {/* 🆕 FASE 2: Análise WCAG Detalhada */}
            <div className="wcag-analysis">
              <h4>♿ Conformidade WCAG</h4>
              <div className="wcag-card">
                <div className="wcag-level">
                  <span
                    className={`wcag-badge wcag-${wcag.level.toLowerCase()}`}
                  >
                    WCAG {wcag.level}
                  </span>
                  <span className="wcag-description">
                    {wcag.level === "AAA"
                      ? "Máxima acessibilidade"
                      : wcag.level === "AA"
                      ? "Acessibilidade padrão"
                      : "Melhorias necessárias"}
                  </span>
                </div>
                {wcag.issues.length > 0 && (
                  <div className="wcag-issues">
                    <h5>🔍 Problemas Identificados:</h5>
                    <ul>
                      {wcag.issues.map((issue, i) => (
                        <li key={i} className="wcag-issue">
                          {issue}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {wcag.fixes.length > 0 && (
                  <div className="wcag-fixes">
                    <h5>🛠️ Correções Sugeridas:</h5>
                    <ul>
                      {wcag.fixes.map((fix, i) => (
                        <li key={i} className="wcag-fix">
                          {fix}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            <div className="analysis-details">
              <div className="issues-section">
                <h4>⚠️ Problemas Identificados</h4>
                <ul className="issues-list">
                  {analysis.issues.map((issue, index) => (
                    <li key={index} className="issue-item">
                      <span className="issue-icon">⚠️</span>
                      <span className="issue-text">{issue}</span>
                      <span className="issue-priority">
                        {issue.includes("contraste")
                          ? "Alta"
                          : issue.includes("tamanho")
                          ? "Média"
                          : "Baixa"}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="recommendations-section">
                <h4>💡 Recomendações Priorizadas</h4>
                <ul className="recommendations-list">
                  {analysis.recommendations.map((recommendation, index) => (
                    <li key={index} className="recommendation-item">
                      <span className="recommendation-icon">💡</span>
                      <span className="recommendation-text">
                        {recommendation}
                      </span>
                      <span className="recommendation-impact">
                        {recommendation.includes("contraste")
                          ? "🔥 Alto impacto"
                          : recommendation.includes("layout")
                          ? "📈 Médio impacto"
                          : "✨ Melhoria"}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* 🆕 FASE 2: Botões de Ação Rápida */}
            <div className="analysis-actions">
              <h4>🚀 Ações Baseadas na Análise</h4>
              <div className="action-buttons">
                {!colorContrast.passes && (
                  <button
                    className="action-btn contrast-fix"
                    onClick={() =>
                      handleApplySuggestion({
                        id: `auto_contrast_${Date.now()}`,
                        type: "color_palette",
                        title: "Auto-correção de Contraste",
                        description:
                          "Ajustar cores automaticamente para WCAG AA",
                        data: {
                          primaryColor: "#1E3A8A",
                          secondaryColor: currentConfig.theme.secondaryColor,
                          backgroundColor: "#FFFFFF",
                          textColor: "#1F2937",
                        },
                        confidence: 0.95,
                      })
                    }
                  >
                    🎨 Corrigir Contraste Automaticamente
                  </button>
                )}

                {wcag.level !== "AA" && (
                  <button
                    className="action-btn wcag-fix"
                    onClick={() =>
                      handleApplySuggestion({
                        id: `wcag_compliance_${Date.now()}`,
                        type: "accessibility",
                        title: "Conformidade WCAG AA",
                        description: "Aplicar todas as correções necessárias",
                        data: { fixes: wcag.fixes, targetLevel: "AA" },
                        confidence: 0.92,
                      })
                    }
                  >
                    ♿ Atingir WCAG AA
                  </button>
                )}

                {analysis.usabilityScore < 80 && (
                  <button
                    className="action-btn usability-boost"
                    onClick={() => {
                      setChatInput(
                        "Como melhorar a usabilidade para " +
                          analysis.usabilityScore +
                          "%?"
                      );
                      setActiveAssistantTab("generate");
                    }}
                  >
                    📈 Melhorar Usabilidade
                  </button>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    );
  };
  // 🆕 FASE 3: Funções para A/B Testing
  const generateABTestVariants = (): ABTestVariant[] => {
    const baseConfig = currentConfig;

    return [
      {
        id: "variant_a",
        name: "Design Atual",
        config: baseConfig,
        metrics: {
          usabilityScore: analysis?.usabilityScore || 80,
          engagementRate: 0.75,
          taskCompletionTime: 45,
          userSatisfaction: 4.2,
        },
        userFeedback: ["Interface clara", "Fácil navegação"],
      },
      {
        id: "variant_b",
        name: "Design Otimizado",
        config: {
          ...baseConfig,
          theme: {
            ...baseConfig.theme,
            primaryColor: "#6366F1",
            borderRadius: "12px",
          },
          layout: agents.length > 3 ? "sidebar" : "tabs",
        },
        metrics: {
          usabilityScore: 92,
          engagementRate: 0.88,
          taskCompletionTime: 38,
          userSatisfaction: 4.6,
        },
        userFeedback: ["Visual moderno", "Mais intuitivo"],
      },
      {
        id: "variant_c",
        name: "Design Experimental",
        config: {
          ...baseConfig,
          theme: {
            ...baseConfig.theme,
            primaryColor: "#10B981",
            secondaryColor: "#F0FDF4",
            borderRadius: "16px",
          },
          layout: "cards",
        },
        metrics: {
          usabilityScore: 85,
          engagementRate: 0.82,
          taskCompletionTime: 42,
          userSatisfaction: 4.4,
        },
        userFeedback: ["Inovador", "Cores agradáveis"],
      },
    ];
  };

  // 🆕 FASE 3: Análise avançada de usabilidade
  const generateUsabilityReport = (): UsabilityReport => {
    const analysisData = analysis || {
      accessibilityScore: 80,
      usabilityScore: 85,
      modernityScore: 90,
      wcagCompliance: { level: "AA" as const, issues: [], fixes: [] },
      colorContrast: { ratio: 4.5, passes: true, recommendations: [] },
      issues: [],
      recommendations: [],
      layoutAnalysis: { efficiency: 85, suggestions: [], bottlenecks: [] },
    };

    return {
      id: `report_${Date.now()}`,
      timestamp: new Date(),
      overallScore: Math.round(
        (analysisData.accessibilityScore +
          analysisData.usabilityScore +
          analysisData.modernityScore) /
          3
      ),
      detailedAnalysis: {
        cognitiveLoad: agents.length > 4 ? 65 : 85,
        taskEfficiency: analysisData.usabilityScore,
        errorPrevention: analysisData.accessibilityScore > 80 ? 90 : 70,
        learnability: currentConfig.showAgentAvatars ? 88 : 75,
      },
      recommendations: [
        {
          priority: "high",
          action: "Implementar layout responsivo completo",
          impact: "Melhora usabilidade mobile em 40%",
          effort: "2-3 dias",
        },
        {
          priority: "medium",
          action: "Adicionar onboarding interativo",
          impact: "Reduz tempo de aprendizado em 30%",
          effort: "1-2 dias",
        },
      ],
      exportFormats: ["pdf", "excel", "json"],
    };
  };

  // 🆕 FASE 3: Executar A/B Test
  const handleRunABTest = async () => {
    setIsRunningABTest(true);
    const variants = generateABTestVariants();
    setAbTestVariants(variants);

    // Simular teste A/B
    setTimeout(() => {
      const results = {
        winner: variants[1], // Variant B wins
        confidence: 95,
        sampleSize: 1000,
        duration: "7 dias",
        significance: "Estatisticamente significativo",
      };
      setAbTestResults(results);
      setIsRunningABTest(false);
      //onRunABTest?.(variants);
    }, 3000);
  };

  // 🆕 FASE 3: Gerar relatório
  const handleGenerateReport = async (format: "pdf" | "excel" | "json") => {
    setIsGeneratingReport(true);
    const report = generateUsabilityReport();
    setUsabilityReport(report);

    setTimeout(() => {
      setIsGeneratingReport(false);
      //onGenerateReport?.(format);

      // Simular download
      const reportData = {
        ...report,
        format,
        generatedAt: new Date().toISOString(),
      };

      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `usability-report-${format}.${
        format === "json" ? "json" : format
      }`;
      a.click();
      URL.revokeObjectURL(url);
    }, 2000);
  };

  // 🆕 FASE 2: Chat Aprimorado com Contexto
  const renderGenerateTab = () => (
    <div className="ai-generate">
      <div className="generate-header">
        <h3>💬 Chat Inteligente com IA</h3>
        <p>Assistente contextual com análise em tempo real da sua interface</p>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {chatMessages.length === 0 && (
            <div className="chat-welcome">
              <div className="welcome-avatar">🤖</div>
              <div className="welcome-text">
                <h4>Olá! Sou seu assistente de design especializado.</h4>
                <p>
                  Já analisei sua interface com {agents.length} agente(s) e
                  posso ajudar com:
                </p>
                <ul>
                  <li>
                    🎨 Otimização de cores e contraste (atual:{" "}
                    {calculateContrast(
                      hexToRgb(currentConfig.theme.primaryColor),
                      hexToRgb(currentConfig.theme.backgroundColor)
                    ).toFixed(1)}
                    :1)
                  </li>
                  <li>
                    📐 Layout ideal para {agents.length} agente(s) (atual:{" "}
                    {currentConfig.layout})
                  </li>
                  <li>
                    ♿ Conformidade WCAG (nível:{" "}
                    {analyzeAccessibility(currentConfig).level})
                  </li>
                  <li>📱 Responsividade e mobile-first</li>
                  <li>🔧 Personalização para seu domínio</li>
                </ul>
                <p>
                  <strong>Sua situação atual:</strong> Interface{" "}
                  {analyzeAccessibility(currentConfig).level === "AA"
                    ? "conforme"
                    : "precisa de ajustes"}{" "}
                  com {agents.length > 2 ? "muitos" : "poucos"} agentes.
                </p>
              </div>
            </div>
          )}

          {chatMessages.map((message) => (
            <div key={message.id} className={`chat-message ${message.role}`}>
              <div className="message-avatar">
                {message.role === "user" ? "👤" : "🤖"}
              </div>
              <div className="message-content">
                {message.content.split("\n").map((line, index) => {
                  // 🆕 FASE 2: Formatação rica para respostas da IA
                  if (line.startsWith("**") && line.endsWith("**")) {
                    return (
                      <p key={index} className="message-bold">
                        {line.slice(2, -2)}
                      </p>
                    );
                  }
                  if (line.startsWith("# ")) {
                    return (
                      <h4 key={index} className="message-heading">
                        {line.slice(2)}
                      </h4>
                    );
                  }
                  if (line.startsWith("• ")) {
                    return (
                      <p key={index} className="message-bullet">
                        {line}
                      </p>
                    );
                  }
                  return line.trim() ? (
                    <p key={index}>{line}</p>
                  ) : (
                    <br key={index} />
                  );
                })}
                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="chat-message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div className="typing-text">Analisando sua interface...</div>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input-area">
          {/* 🆕 FASE 2: Prompts Contextuais Inteligentes */}
          <div className="suggested-prompts">
            <button
              className="prompt-btn contextual"
              onClick={() =>
                setChatInput(
                  `Analise o contraste atual de ${calculateContrast(
                    hexToRgb(currentConfig.theme.primaryColor),
                    hexToRgb(currentConfig.theme.backgroundColor)
                  ).toFixed(2)}:1 e sugira melhorias`
                )
              }
            >
              🎨 Melhorar contraste (
              {calculateContrast(
                hexToRgb(currentConfig.theme.primaryColor),
                hexToRgb(currentConfig.theme.backgroundColor)
              ).toFixed(1)}
              :1)
            </button>
            <button
              className="prompt-btn contextual"
              onClick={() =>
                setChatInput(
                  `Com ${agents.length} agentes, qual o melhor layout: ${currentConfig.layout} ou outra opção?`
                )
              }
            >
              📐 Otimizar layout ({agents.length} agentes)
            </button>
            <button
              className="prompt-btn contextual"
              onClick={() =>
                setChatInput(
                  `Como atingir WCAG AA partindo de ${
                    analyzeAccessibility(currentConfig).level
                  }?`
                )
              }
            >
              ♿ WCAG {analyzeAccessibility(currentConfig).level} → AA
            </button>
            <button
              className="prompt-btn contextual"
              onClick={() =>
                setChatInput(
                  "Crie uma paleta de cores moderna para sistemas de atendimento"
                )
              }
            >
              🎨 Paleta para atendimento
            </button>
          </div>

          <div className="chat-input">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Pergunte sobre cores, layout, acessibilidade, mobile..."
              onKeyPress={(e) =>
                e.key === "Enter" && !isTyping && handleSendChatMessage()
              }
            />
            <button
              onClick={handleSendChatMessage}
              disabled={!chatInput.trim() || isTyping}
              className={isTyping ? "loading" : ""}
            >
              {isTyping ? "⏳" : "➤"}
            </button>
          </div>

          {/* 🆕 FASE 2: Status contextual */}
          <div className="chat-status">
            <span className="status-item">
              🎯 Contexto: {agents.length} agente(s), Layout{" "}
              {currentConfig.layout}
            </span>
            <span className="status-item">
              📊 WCAG: {analyzeAccessibility(currentConfig).level}
            </span>
            <span className="status-item">
              🎨 Contraste:{" "}
              {calculateContrast(
                hexToRgb(currentConfig.theme.primaryColor),
                hexToRgb(currentConfig.theme.backgroundColor)
              ).toFixed(1)}
              :1
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="ai-assistant-overlay">
      <div className="ai-assistant-modal">
        <div className="ai-assistant-header">
          <h2>✨ AI Design Assistant</h2>
          <div className="header-badges">
            <span className="feature-badge">🆕 Análise WCAG</span>
            <span className="feature-badge">🆕 Layout IA</span>
            <span className="feature-badge">🆕 Chat Contextual</span>
          </div>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="ai-assistant-tabs">
          <button
            className={
              activeAssistantTab === "suggestions" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("suggestions")}
          >
            💡 Sugestões
            {appliedSuggestions.size > 0 && (
              <span className="tab-badge">{appliedSuggestions.size}</span>
            )}
          </button>
          <button
            className={
              activeAssistantTab === "analysis" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("analysis")}
          >
            📊 Análise WCAG
          </button>
          <button
            className={
              activeAssistantTab === "layout" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("layout")}
          >
            📐 Layout IA
          </button>
          <button
            className={
              activeAssistantTab === "generate" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("generate")}
          >
            💬 Chat IA
            {chatMessages.length > 0 && (
              <span className="tab-badge">{chatMessages.length}</span>
            )}
          </button>
          <button
            className={
              activeAssistantTab === "abtest" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("abtest")}
          >
            🧪 A/B Testing
            {abTestResults && <span className="tab-badge">Concluído</span>}
          </button>
          <button
            className={
              activeAssistantTab === "reports" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("reports")}
          >
            📊 Relatórios
            {usabilityReport && <span className="tab-badge">1</span>}
          </button>
        </div>

        <div className="ai-assistant-content">
          {activeAssistantTab === "suggestions" && renderSuggestionsTab()}
          {activeAssistantTab === "analysis" && renderAnalysisTab()}
          {activeAssistantTab === "layout" && renderLayoutTab()}
          {activeAssistantTab === "generate" && renderGenerateTab()}
          {activeAssistantTab === "abtest" && renderABTestTab()}
          {activeAssistantTab === "reports" && renderReportsTab()}
        </div>
      </div>
    </div>
  );
};

// 🆕 FASE 2: Componentes de Preview de Layout
const LayoutMockupSidebar: React.FC<{ agents: Agent[] }> = ({ agents }) => (
  <div className="mockup-container sidebar-mockup">
    <div className="mockup-sidebar">
      <div className="mockup-header">Agentes</div>
      {agents.slice(0, 3).map((agent, i) => (
        <div key={i} className="mockup-agent">
          <div className="mockup-avatar">🤖</div>
          <div className="mockup-name">{agent.name}</div>
        </div>
      ))}
    </div>
    <div className="mockup-chat">
      <div className="mockup-chat-header">Chat Ativo</div>
      <div className="mockup-messages">
        <div className="mockup-message">Olá! Como posso ajudar?</div>
        <div className="mockup-message user">Preciso de suporte</div>
      </div>
      <div className="mockup-input">Digite sua mensagem...</div>
    </div>
  </div>
);

const LayoutMockupTabs: React.FC<{ agents: Agent[] }> = ({ agents }) => (
  <div className="mockup-container tabs-mockup">
    <div className="mockup-tabs">
      {agents.slice(0, 3).map((agent, i) => (
        <div key={i} className={`mockup-tab ${i === 0 ? "active" : ""}`}>
          {agent.name}
        </div>
      ))}
    </div>
    <div className="mockup-chat">
      <div className="mockup-messages">
        <div className="mockup-message">Especialista em atendimento ativo</div>
        <div className="mockup-message user">Olá!</div>
      </div>
      <div className="mockup-input">Digite sua mensagem...</div>
    </div>
  </div>
);

const LayoutMockupCards: React.FC<{ agents: Agent[] }> = ({ agents }) => (
  <div className="mockup-container cards-mockup">
    <div className="mockup-grid">
      {agents.slice(0, 3).map((agent, i) => (
        <div key={i} className="mockup-card">
          <div className="mockup-card-avatar">🤖</div>
          <div className="mockup-card-name">{agent.name}</div>
          <div className="mockup-card-desc">{agent.role}</div>
          <div className="mockup-card-btn">Conversar</div>
        </div>
      ))}
    </div>
  </div>
);

export default AIDesignAssistant;
