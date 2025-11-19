import React, { useState } from 'react';
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

  if (!isOpen) return null;

  const handleSave = () => {
    onSave(editedContent);
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
