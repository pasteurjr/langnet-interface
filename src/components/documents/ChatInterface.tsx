import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './ChatInterface.css';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent' | 'system';
  text: string;
  timestamp: Date;
  type?: 'status' | 'progress' | 'result' | 'document';
  data?: any;
}

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isProcessing?: boolean;
  executionId?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isProcessing = false,
  executionId
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isProcessing) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.sender === 'user';
    const isSystem = message.sender === 'system';

    return (
      <div
        key={message.id}
        className={`chat-message ${isUser ? 'user-message' : isSystem ? 'system-message' : 'agent-message'}`}
      >
        <div className="message-header">
          <span className="message-sender">
            {isUser ? '👤 Você' : isSystem ? '⚙️ Sistema' : '🤖 Agente IA'}
          </span>
          <span className="message-timestamp">{formatTimestamp(message.timestamp)}</span>
        </div>
        <div className="message-content">
          {message.type === 'document' ? (
            <div className="document-preview">
              <div className="document-header">
                <span className="document-icon">📋</span>
                <h4>Documento de Requisitos Gerado</h4>
              </div>
              <div className="document-body">
                <ReactMarkdown>{message.text}</ReactMarkdown>
              </div>
              {executionId && (
                <div className="document-actions">
                  <button
                    className="btn-view-full"
                    onClick={() => window.open(`/project/${message.data?.projectId}/requirements/${executionId}`, '_blank')}
                  >
                    📄 Ver Documento Completo
                  </button>
                  <button className="btn-refine">
                    💬 Refinar Requisitos
                  </button>
                </div>
              )}
            </div>
          ) : (
            <ReactMarkdown>{message.text}</ReactMarkdown>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>💬 Conversa com Agente IA</h2>
        {executionId && (
          <span className="execution-badge">
            ID: <code>{executionId.substring(0, 8)}...</code>
          </span>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <div className="empty-icon">🤖</div>
            <h3>Bem-vindo ao Assistente de Requisitos</h3>
            <p>
              Faça upload de documentos na barra lateral e inicie a análise.
              <br />
              Você pode refinar os requisitos através desta conversa.
            </p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}

        {isProcessing && (
          <div className="chat-message agent-message typing">
            <div className="message-header">
              <span className="message-sender">🤖 Agente IA</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-container" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Digite sua mensagem para refinar a análise..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isProcessing}
        />
        <button
          type="submit"
          className="btn-send"
          disabled={isProcessing || !inputValue.trim()}
        >
          {isProcessing ? '⏳' : '📤'} Enviar
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
