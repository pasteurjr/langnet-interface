import React, { useState, useEffect, useRef, useCallback } from 'react';
import MDEditor from '@uiw/react-md-editor';
import './MarkdownEditorModal.css';

interface MarkdownEditorModalProps {
  isOpen: boolean;
  content: string;
  filename: string;
  onSave: (content: string) => void;
  onClose: () => void;
}

const MarkdownEditorModal: React.FC<MarkdownEditorModalProps> = ({
  isOpen,
  content,
  filename,
  onSave,
  onClose
}) => {
  const [editedContent, setEditedContent] = useState(content);
  const [displayContent, setDisplayContent] = useState(content);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Sincronizar estado interno quando prop 'content' ou 'isOpen' mudar
  useEffect(() => {
    setEditedContent(content);
    setDisplayContent(content);
  }, [content, isOpen]);

  // Cleanup do debounce timer ao desmontar
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  // Handler com debounce para onChange do editor
  const handleEditorChange = useCallback((val: string | undefined) => {
    const newValue = val || '';

    // Atualiza o conteúdo editado imediatamente (para o textarea)
    setEditedContent(newValue);

    // Debounce para atualizar o preview (evita re-render pesado)
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      setDisplayContent(newValue);
    }, 300); // 300ms de delay
  }, []);

  const handleSave = useCallback(() => {
    // Limpa qualquer debounce pendente
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    onSave(editedContent);
    onClose();
  }, [editedContent, onSave, onClose]);

  const handleCancel = useCallback(() => {
    // Limpa qualquer debounce pendente
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    setEditedContent(content);
    setDisplayContent(content);
    onClose();
  }, [content, onClose]);

  if (!isOpen) return null;

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
            onChange={handleEditorChange}
            height={500}
            preview="live"
            hideToolbar={false}
            enableScroll={true}
            visibleDragbar={true}
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
