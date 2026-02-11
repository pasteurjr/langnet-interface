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
  const [previewContent, setPreviewContent] = useState(content);

  // Sincronizar estado interno quando prop 'content' ou 'isOpen' mudar
  useEffect(() => {
    setEditedContent(content);
    setPreviewContent(content);
  }, [content, isOpen]);

  const handleSave = () => {
    onSave(editedContent);
    onClose();
  };

  const handleCancel = () => {
    setEditedContent(content);
    setPreviewContent(content);
    onClose();
  };

  const handleUpdatePreview = () => {
    setPreviewContent(editedContent);
  };

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

        <div className="modal-body editor-with-preview">
          <div className="editor-panel">
            <div className="panel-header">
              <span>📝 Editor</span>
            </div>
            <MDEditor
              value={editedContent}
              onChange={(val) => setEditedContent(val || '')}
              height={500}
              preview="edit"
              hideToolbar={false}
              enableScroll={true}
            />
          </div>

          <div className="preview-panel">
            <div className="panel-header">
              <span>👁️ Preview</span>
              <button className="btn-update-preview" onClick={handleUpdatePreview} title="Atualizar preview">
                🔄 Renderizar
              </button>
            </div>
            <div className="preview-content">
              <MDEditor.Markdown source={previewContent} />
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={handleCancel}>
            ❌ Cancelar
          </button>
          <button className="btn-update-preview" onClick={handleUpdatePreview}>
            🔄 Renderizar Preview
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
