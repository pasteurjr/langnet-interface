import React, { useState, useEffect } from 'react';
import MDEditor from '@uiw/react-md-editor';
import './MarkdownEditorModal.css';

interface MarkdownEditorModalProps {
  isOpen: boolean;
  content: string;
  filename: string;
  onSave: (content: string) => void;
  onClose: () => void;
}

/**
 * Atualiza a data no cabeçalho do documento markdown
 * Procura por linhas como "**Data:** ..." ou "Data: ..." e atualiza com a data atual
 */
const updateDocumentDate = (content: string): string => {
  const now = new Date();
  const dateStr = now.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  // Padrões de data para substituir
  const patterns = [
    /(\*\*Data:\*\*\s*)([^\n]+)/g,  // **Data:** ...
    /(\*\*Data de Criação:\*\*\s*)([^\n]+)/g,  // **Data de Criação:** ...
    /(\*\*Última Modificação:\*\*\s*)([^\n]+)/g,  // **Última Modificação:** ...
    /(Data:\s*)([^\n]+)/g,  // Data: ...
    /(Criado em:\s*)([^\n]+)/g,  // Criado em: ...
    /(Modificado em:\s*)([^\n]+)/g,  // Modificado em: ...
  ];

  let updatedContent = content;

  // Substituir todas as ocorrências de data encontradas
  patterns.forEach(pattern => {
    updatedContent = updatedContent.replace(pattern, `$1${dateStr}`);
  });

  // Se não encontrou nenhuma data, adiciona no início do documento
  if (updatedContent === content && !content.includes('Data:') && !content.includes('**Data:**')) {
    const header = `**Última Modificação:** ${dateStr}\n\n---\n\n`;
    updatedContent = header + content;
  }

  return updatedContent;
};

const MarkdownEditorModal: React.FC<MarkdownEditorModalProps> = ({
  isOpen,
  content,
  filename,
  onSave,
  onClose
}) => {
  const [editedContent, setEditedContent] = useState(content);

  // Sincronizar estado interno quando prop 'content' ou 'isOpen' mudar
  useEffect(() => {
    console.log('📝 MarkdownEditorModal: Sincronizando conteúdo', {
      contentLength: content.length,
      isOpen
    });
    setEditedContent(content);
  }, [content, isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    // Atualiza a data no documento antes de salvar
    const contentWithUpdatedDate = updateDocumentDate(editedContent);
    onSave(contentWithUpdatedDate);
    onClose();
  };

  const handleCancel = () => {
    setEditedContent(content); // Reset to original
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleCancel}>
      <div className="modal-content editor-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>✏️ Editar Documento</h2>
          <span className="modal-filename">{filename}</span>
          <button className="btn-close" onClick={handleCancel} title="Fechar">
            ✕
          </button>
        </div>

        <div className="modal-body">
          <MDEditor
            value={editedContent}
            onChange={(val) => setEditedContent(val || '')}
            height={500}
            preview="edit"
            hideToolbar={false}
            enableScroll={true}
            visibleDragbar={true}
            textareaProps={{
              placeholder: 'Digite seu conteúdo em Markdown aqui...',
            }}
          />
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={handleCancel}>
            ❌ Cancelar
          </button>
          <button className="btn-save" onClick={handleSave}>
            💾 Salvar Alterações
          </button>
        </div>
      </div>
    </div>
  );
};

export default MarkdownEditorModal;
