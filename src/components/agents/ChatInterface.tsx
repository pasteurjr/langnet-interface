// src/components/agents/ChatInterface.tsx - REFEITO CORRETAMENTE
import React, { useState, useRef, useEffect } from "react";
import {
  ChatMessage,
  Agent,
  QuickCommand,
  ChatTemplate,
} from "../../types/agentChat";
import "./ChatInterface.css";

interface ChatInterfaceProps {
  messages: ChatMessage[];
  agents: Agent[];
  selectedAgents: string[];
  chatMode: "broadcast" | "individual" | "group";
  onSendMessage: (content: string, type: "message" | "command") => void;
  onChatModeChange: (mode: "broadcast" | "individual" | "group") => void;
  onAgentSelectionChange: (agentIds: string[]) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  agents,
  selectedAgents,
  chatMode,
  onSendMessage,
  onChatModeChange,
  onAgentSelectionChange,
}) => {
  const [inputMessage, setInputMessage] = useState("");
  const [showCommands, setShowCommands] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [showAgentSelector, setShowAgentSelector] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll para a última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Comandos rápidos disponíveis
  const quickCommands: QuickCommand[] = [
    {
      id: "1",
      command: "/status",
      description: "Verificar status dos agentes",
      category: "status",
    },
    {
      id: "2",
      command: "/restart",
      description: "Reiniciar agente selecionado",
      category: "control",
    },
    {
      id: "3",
      command: "/debug",
      description: "Ativar modo debug",
      category: "debug",
    },
    {
      id: "4",
      command: "/metrics",
      description: "Mostrar métricas de performance",
      category: "status",
    },
    {
      id: "5",
      command: "/help",
      description: "Mostrar comandos disponíveis",
      category: "status",
    },
    {
      id: "6",
      command: "/clear",
      description: "Limpar histórico de chat",
      category: "control",
    },
    {
      id: "7",
      command: "/pause",
      description: "Pausar processamento",
      category: "control",
    },
    {
      id: "8",
      command: "/resume",
      description: "Retomar processamento",
      category: "control",
    },
  ];

  // Templates de mensagens pré-definidas
  const messageTemplates: ChatTemplate[] = [
    {
      id: "1",
      name: "Teste de Query",
      content:
        'Processe esta query de teste: "Problema com cobrança incorreta"',
      category: "common_queries",
      description: "Template para teste de processamento",
    },
    {
      id: "2",
      name: "Análise de Sentimento",
      content: "Analise o sentimento desta mensagem e classifique",
      category: "debug_scripts",
      description: "Script para análise de sentimento",
    },
    {
      id: "3",
      name: "Debug de Performance",
      content:
        "Mostre estatísticas detalhadas de performance do último processamento",
      category: "debug_scripts",
      description: "Script de debug de performance",
    },
    {
      id: "4",
      name: "Simulação de Carga",
      content: "Execute simulação de carga com 10 queries simultâneas",
      category: "debug_scripts",
      description: "Script para teste de carga",
    },
    {
      id: "5",
      name: "Relatório de Status",
      content:
        "Gere relatório completo do status atual de todos os componentes",
      category: "reports",
      description: "Gerar relatório do sistema",
    },
  ];

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const isCommand = inputMessage.startsWith("/");
    onSendMessage(inputMessage, isCommand ? "command" : "message");
    setInputMessage("");
    setShowCommands(false);
    setShowTemplates(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputMessage(value);

    // Mostrar comandos quando digitar '/'
    if (value.startsWith("/") && value.length > 1) {
      setShowCommands(true);
      setShowTemplates(false);
    } else {
      setShowCommands(false);
    }
  };

  const handleCommandSelect = (command: string) => {
    setInputMessage(command + " ");
    setShowCommands(false);
    inputRef.current?.focus();
  };

  const handleTemplateSelect = (template: ChatTemplate) => {
    setInputMessage(template.content);
    setShowTemplates(false);
    inputRef.current?.focus();
  };

  const handleAgentToggle = (agentId: string) => {
    const newSelection = selectedAgents.includes(agentId)
      ? selectedAgents.filter((id) => id !== agentId)
      : [...selectedAgents, agentId];
    onAgentSelectionChange(newSelection);
  };

  const getMessageTypeIcon = (type: string) => {
    switch (type) {
      case "command":
        return "⚡";
      case "system_notification":
        return "🤖";
      case "debug_info":
        return "🐛";
      default:
        return "💬";
    }
  };

  const getAgentStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "#4caf50";
      case "busy":
        return "#ff9800";
      case "error":
        return "#f44336";
      case "inactive":
        return "#9e9e9e";
      default:
        return "#2196f3";
    }
  };

  const filteredCommands = quickCommands.filter((cmd) =>
    cmd.command.toLowerCase().includes(inputMessage.toLowerCase())
  );

  return (
    <div className="chat-interface">
      {/* Header do Chat */}
      <div className="chat-header">
        <div className="chat-mode-selector">
          <label>Modo de Chat:</label>
          <select
            value={chatMode}
            onChange={(e) => onChatModeChange(e.target.value as any)}
            className="mode-select"
          >
            <option value="broadcast">Broadcast (Todos)</option>
            <option value="individual">Individual</option>
            <option value="group">Grupo Selecionado</option>
          </select>
        </div>

        <div className="agent-selector-toggle">
          <button
            className={`agent-selector-btn ${
              showAgentSelector ? "active" : ""
            }`}
            onClick={() => setShowAgentSelector(!showAgentSelector)}
          >
            🤖 Agentes ({selectedAgents.length}/{agents.length})
          </button>
        </div>

        <div className="chat-controls">
          <button
            className="templates-btn"
            onClick={() => setShowTemplates(!showTemplates)}
            title="Templates de mensagem"
          >
            📝
          </button>
          <button
            className="clear-chat-btn"
            onClick={() => onSendMessage("/clear", "command")}
            title="Limpar chat"
          >
            🗑️
          </button>
        </div>
      </div>

      {/* Seletor de Agentes */}
      {showAgentSelector && (
        <div className="agent-selector-panel">
          <h4>Selecionar Agentes:</h4>
          <div className="agents-grid">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className={`agent-item ${
                  selectedAgents.includes(agent.id) ? "selected" : ""
                }`}
                onClick={() => handleAgentToggle(agent.id)}
              >
                <div
                  className="agent-status-indicator"
                  style={{ backgroundColor: getAgentStatusColor(agent.status) }}
                />
                <span className="agent-name">{agent.name}</span>
                <span className="agent-load">{agent.load}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Área de Mensagens */}
      <div className="messages-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-item ${
              message.sender === "user" ? "user-message" : "agent-message"
            } ${message.type}`}
          >
            <div className="message-header">
              <span className="message-type-icon">
                {getMessageTypeIcon(message.type)}
              </span>
              <span className="message-sender">{message.sender}</span>
              <span className="message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
              {message.agentName && (
                <span className="message-agent">→ {message.agentName}</span>
              )}
            </div>
            <div className="message-content">{message.content}</div>
            {message.metadata && (
              <div className="message-metadata">
                {message.metadata.confidence && (
                  <span className="metadata-item">
                    Confiança: {(message.metadata.confidence * 100).toFixed(1)}%
                  </span>
                )}
                {message.metadata.processingTime && (
                  <span className="metadata-item">
                    Tempo: {message.metadata.processingTime}ms
                  </span>
                )}
                {message.metadata.tokens && (
                  <span className="metadata-item">
                    Tokens: {message.metadata.tokens}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Sugestões de Comandos */}
      {showCommands && filteredCommands.length > 0 && (
        <div className="commands-dropdown">
          <h4>Comandos Disponíveis:</h4>
          {filteredCommands.map((cmd) => (
            <div
              key={cmd.id}
              className="command-item"
              onClick={() => handleCommandSelect(cmd.command)}
            >
              <span className="command-text">{cmd.command}</span>
              <span className="command-description">{cmd.description}</span>
              <span className="command-category">{cmd.category}</span>
            </div>
          ))}
        </div>
      )}

      {/* Templates de Mensagem */}
      {showTemplates && (
        <div className="templates-dropdown">
          <h4>Templates de Mensagem:</h4>
          {messageTemplates.map((template) => (
            <div
              key={template.id}
              className="template-item"
              onClick={() => handleTemplateSelect(template)}
            >
              <span className="template-name">{template.name}</span>
              <span className="template-category">{template.category}</span>
              <div className="template-preview">{template.content}</div>
            </div>
          ))}
        </div>
      )}

      {/* Input de Mensagem */}
      <div className="message-input-container">
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem ou comando (/ para comandos)..."
            className="message-input"
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
          >
            📤
          </button>
        </div>

        <div className="input-helpers">
          <span className="helper-text">
            💡 Digite "/" para comandos rápidos
          </span>
          {selectedAgents.length > 0 && (
            <span className="selected-agents-info">
              Enviando para: {selectedAgents.length} agente(s)
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
