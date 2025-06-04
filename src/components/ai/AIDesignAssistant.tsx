// src/components/ai/AIDesignAssistant.tsx
import React, { useState } from "react";
import { Agent } from "../../types";
import "./AIDesignAssistant.css";

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
    "suggestions" | "analysis" | "generate"
  >("suggestions");
  const [selectedDomain, setSelectedDomain] = useState("corporativo");
  const [chatMessages, setChatMessages] = useState<
    Array<{ id: string; role: "user" | "assistant"; content: string }>
  >([]);
  const [chatInput, setChatInput] = useState("");

  if (!isOpen) return null;

  const handleSendChatMessage = () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user" as const,
      content: chatInput,
    };

    setChatMessages((prev) => [...prev, userMessage]);

    // Simulate AI response (replace with real backend call)
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        role: "assistant" as const,
        content: generateMockAIResponse(chatInput),
      };
      setChatMessages((prev) => [...prev, aiResponse]);
    }, 1500);

    setChatInput("");
  };

  const generateMockAIResponse = (input: string): string => {
    const lowerInput = input.toLowerCase();

    if (lowerInput.includes("cor") || lowerInput.includes("color")) {
      return "Para escolher cores adequadas, considero o domínio do seu projeto e psicologia das cores. Baseado nos seus agentes, sugiro:\n\n• Azul (#1E3A8A) - transmite confiança e profissionalismo\n• Verde (#065F46) - sugere crescimento e estabilidade\n• Cinza neutro (#F3F4F6) - clean e moderno\n\nQuer que eu aplique uma dessas paletas?";
    }

    if (lowerInput.includes("layout") || lowerInput.includes("design")) {
      return "Para otimizar o layout da sua interface:\n\n• Sidebar: Ideal para múltiplos agentes (como o seu caso)\n• Tabs: Melhor para poucos agentes especializados\n• Cards: Excelente para descoberta de funcionalidades\n\nCom 3 agentes, recomendo manter o sidebar mas adicionar badges de status. Posso implementar isso?";
    }

    if (lowerInput.includes("acessibilidade")) {
      return "Analisando a acessibilidade da sua interface:\n\n✅ Pontos positivos:\n• Contraste adequado nos elementos principais\n• Estrutura hierárquica clara\n\n⚠️ Melhorias sugeridas:\n• Aumentar área clicável dos agentes (44px mínimo)\n• Adicionar indicadores de foco mais visíveis\n• Incluir textos alternativos\n\nQuer que eu implemente essas correções?";
    }

    return "Entendi sua solicitação! Baseado na configuração atual da sua interface e nos agentes do projeto, posso ajudar com:\n\n• Sugestões de cores e tipografia\n• Otimização de layout e usabilidade\n• Geração de conteúdo personalizado\n• Análise de acessibilidade\n\nO que gostaria de melhorar primeiro?";
  };

  const renderSuggestionsTab = () => (
    <div className="ai-suggestions">
      <div className="suggestions-header">
        <h3>💡 Sugestões Inteligentes</h3>
        <p>Baseado na análise dos seus agentes e configuração atual</p>
      </div>

      {isLoading ? (
        <div className="ai-loading">
          <div className="loading-spinner"></div>
          <p>Analisando sua interface e gerando sugestões...</p>
        </div>
      ) : (
        <div className="suggestions-list">
          {suggestions.map((suggestion) => (
            <div key={suggestion.id} className="suggestion-card">
              <div className="suggestion-header">
                <h4>{suggestion.title}</h4>
                <div className="confidence-badge">
                  {Math.round(suggestion.confidence * 100)}% confiança
                </div>
              </div>
              <p className="suggestion-description">{suggestion.description}</p>

              {suggestion.type === "color_palette" && (
                <div className="color-preview">
                  <div
                    className="color-swatch"
                    style={{ backgroundColor: suggestion.data.primaryColor }}
                    title="Cor Primária"
                  ></div>
                  <div
                    className="color-swatch"
                    style={{ backgroundColor: suggestion.data.secondaryColor }}
                    title="Cor Secundária"
                  ></div>
                  <div
                    className="color-swatch"
                    style={{ backgroundColor: suggestion.data.backgroundColor }}
                    title="Cor de Fundo"
                  ></div>
                </div>
              )}

              {suggestion.type === "content" && (
                <div className="content-preview">
                  <div className="preview-text">
                    "{suggestion.data.welcomeMessage}"
                  </div>
                </div>
              )}

              <button
                className="btn-apply-suggestion"
                onClick={() => onApplySuggestion(suggestion)}
              >
                ✨ Aplicar Sugestão
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
            onClick={() => setSelectedDomain("corporativo")}
          >
            🏢 Estilo Corporativo
          </button>
          <button
            className="quick-btn"
            onClick={() => setSelectedDomain("moderno")}
          >
            🎨 Design Moderno
          </button>
          <button
            className="quick-btn"
            onClick={() => setSelectedDomain("acessivel")}
          >
            ♿ Otimizar Acessibilidade
          </button>
          <button
            className="quick-btn"
            onClick={() => setSelectedDomain("mobile")}
          >
            📱 Melhorar Mobile
          </button>
        </div>
      </div>
    </div>
  );

  const renderAnalysisTab = () => (
    <div className="ai-analysis">
      <div className="analysis-header">
        <h3>📊 Análise da Interface</h3>
        <p>Avaliação detalhada da sua configuração atual</p>
      </div>

      {isLoading || !analysis ? (
        <div className="ai-loading">
          <div className="loading-spinner"></div>
          <p>Analisando interface...</p>
        </div>
      ) : (
        <>
          <div className="score-cards">
            <div className="score-card">
              <div className="score-value">{analysis.accessibilityScore}%</div>
              <div className="score-label">Acessibilidade</div>
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

          <div className="analysis-details">
            <div className="issues-section">
              <h4>⚠️ Problemas Identificados</h4>
              <ul className="issues-list">
                {analysis.issues.map((issue, index) => (
                  <li key={index} className="issue-item">
                    <span className="issue-icon">⚠️</span>
                    {issue}
                  </li>
                ))}
              </ul>
            </div>

            <div className="recommendations-section">
              <h4>💡 Recomendações</h4>
              <ul className="recommendations-list">
                {analysis.recommendations.map((recommendation, index) => (
                  <li key={index} className="recommendation-item">
                    <span className="recommendation-icon">💡</span>
                    {recommendation}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderGenerateTab = () => (
    <div className="ai-generate">
      <div className="generate-header">
        <h3>💬 Chat com IA</h3>
        <p>
          Converse diretamente com o assistente para customizações específicas
        </p>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {chatMessages.length === 0 && (
            <div className="chat-welcome">
              <div className="welcome-avatar">🤖</div>
              <div className="welcome-text">
                <h4>Olá! Sou seu assistente de design.</h4>
                <p>Posso ajudar você a:</p>
                <ul>
                  <li>Escolher cores adequadas ao seu domínio</li>
                  <li>Otimizar layout para melhor usabilidade</li>
                  <li>Gerar conteúdo personalizado</li>
                  <li>Melhorar acessibilidade</li>
                </ul>
                <p>Como posso ajudar você hoje?</p>
              </div>
            </div>
          )}

          {chatMessages.map((message) => (
            <div key={message.id} className={`chat-message ${message.role}`}>
              <div className="message-avatar">
                {message.role === "user" ? "👤" : "🤖"}
              </div>
              <div className="message-content">
                {message.content.split("\n").map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="chat-message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input-area">
          <div className="suggested-prompts">
            <button
              className="prompt-btn"
              onClick={() =>
                setChatInput("Sugira cores para um sistema financeiro")
              }
            >
              💰 Cores para sistema financeiro
            </button>
            <button
              className="prompt-btn"
              onClick={() => setChatInput("Como melhorar a acessibilidade?")}
            >
              ♿ Melhorar acessibilidade
            </button>
            <button
              className="prompt-btn"
              onClick={() => setChatInput("Otimize o layout para mobile")}
            >
              📱 Otimizar para mobile
            </button>
          </div>

          <div className="chat-input">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Digite sua solicitação..."
              onKeyPress={(e) => e.key === "Enter" && handleSendChatMessage()}
            />
            <button
              onClick={handleSendChatMessage}
              disabled={!chatInput.trim() || isLoading}
            >
              ➤
            </button>
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
          </button>
          <button
            className={
              activeAssistantTab === "analysis" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("analysis")}
          >
            📊 Análise
          </button>
          <button
            className={
              activeAssistantTab === "generate" ? "ai-tab active" : "ai-tab"
            }
            onClick={() => setActiveAssistantTab("generate")}
          >
            💬 Chat
          </button>
        </div>

        <div className="ai-assistant-content">
          {activeAssistantTab === "suggestions" && renderSuggestionsTab()}
          {activeAssistantTab === "analysis" && renderAnalysisTab()}
          {activeAssistantTab === "generate" && renderGenerateTab()}
        </div>
      </div>
    </div>
  );
};

export default AIDesignAssistant;
