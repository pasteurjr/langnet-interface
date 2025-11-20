import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import DocumentActionsCard from './DocumentActionsCard';
import MarkdownEditorModal from './MarkdownEditorModal';
import MarkdownViewerModal from './MarkdownViewerModal';
import { exportMarkdownToPDF } from '../../services/pdfExportService';
import { updateRequirementsDocument } from '../../services/requirementsService';
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
  sessionId?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isProcessing = false,
  executionId,
  sessionId
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [editingContent, setEditingContent] = useState('');
  const [currentDocument, setCurrentDocument] = useState<ChatMessage | null>(null);
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

  const handleEdit = (message: ChatMessage) => {
    setCurrentDocument(message);
    setEditingContent(message.text);
    setIsEditorOpen(true);
  };

  const handleView = (message: ChatMessage) => {
    setCurrentDocument(message);
    setIsViewerOpen(true);
  };

  const handleExportPDF = async (message: ChatMessage) => {
    try {
      const filename = message.data?.filename?.replace('.md', '.pdf') || 'requisitos.pdf';
      await exportMarkdownToPDF(message.text, filename);
    } catch (error) {
      console.error('Erro ao exportar PDF:', error);
      alert('Falha ao exportar documento para PDF. Tente novamente.');
    }
  };

  const handleSaveEdit = async (newContent: string) => {
    if (!sessionId) {
      alert('Erro: Session ID não disponível');
      return;
    }

    try {
      await updateRequirementsDocument(sessionId, newContent);

      // Update local message
      setEditingContent(newContent);
      if (currentDocument) {
        currentDocument.text = newContent;
      }

      alert('✅ Documento salvo com sucesso!');
    } catch (error) {
      console.error('Erro ao salvar documento:', error);
      alert('❌ Erro ao salvar documento. Tente novamente.');
    }
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
            <DocumentActionsCard
              filename={message.data?.filename || 'requisitos.md'}
              content={message.text}
              executionId={executionId}
              projectId={message.data?.projectId}
              onEdit={() => handleEdit(message)}
              onView={() => handleView(message)}
              onExportPDF={() => handleExportPDF(message)}
            />
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

      {/* Modais */}
      <MarkdownEditorModal
        isOpen={isEditorOpen}
        content={editingContent}
        filename={currentDocument?.data?.filename || 'requisitos.md'}
        onSave={handleSaveEdit}
        onClose={() => setIsEditorOpen(false)}
      />

      <MarkdownViewerModal
        isOpen={isViewerOpen}
        content={currentDocument?.text || ''}
        filename={currentDocument?.data?.filename || 'requisitos.md'}
        onClose={() => setIsViewerOpen(false)}
        onDownload={currentDocument ? () => handleExportPDF(currentDocument) : undefined}
      />
    </div>
  );
};

export default ChatInterface;
