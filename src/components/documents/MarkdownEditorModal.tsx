import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
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
  const editorRef = useRef<any>(null);

  // Sincronizar quando abrir modal
  useEffect(() => {
    if (isOpen) {
      setEditedContent(content);
      setPreviewContent(content);
    }
  }, [isOpen, content]);

  if (!isOpen) return null;

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
    editor.focus();
  };

  const handleEditorChange = (value: string | undefined) => {
    setEditedContent(value || '');
  };

  const handleUpdatePreview = () => {
    setPreviewContent(editedContent);
  };

  const handleSave = () => {
    onSave(editedContent);
    onClose();
  };

  const handleCancel = () => {
    setEditedContent(content);
    setPreviewContent(content);
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

        <div className="modal-body monaco-editor-layout">
          {/* Editor Monaco */}
          <div className="editor-panel">
            <div className="panel-header">
              <span>📝 Editor (Monaco)</span>
            </div>
            <div className="monaco-container">
              <Editor
                height="500px"
                defaultLanguage="markdown"
                value={editedContent}
                onChange={handleEditorChange}
                onMount={handleEditorDidMount}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  wordWrap: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 2,
                }}
              />
            </div>
          </div>

          {/* Preview Markdown */}
          <div className="preview-panel">
            <div className="panel-header">
              <span>👁️ Preview</span>
              <button className="btn-update-preview" onClick={handleUpdatePreview} title="Atualizar preview">
                🔄 Renderizar
              </button>
            </div>
            <div className="preview-content markdown-body">
              <ReactMarkdown>{previewContent}</ReactMarkdown>
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
