import React from 'react';
import ReactMarkdown from 'react-markdown';
import './MarkdownEditorModal.css';

interface MarkdownViewerModalProps {
  isOpen: boolean;
  content: string;
  filename: string;
  onClose: () => void;
  onDownload?: () => void;
}

const MarkdownViewerModal: React.FC<MarkdownViewerModalProps> = ({
  isOpen,
  content,
  filename,
  onClose,
  onDownload
}) => {
  if (!isOpen) return null;

  console.log('👁️ MarkdownViewerModal: Renderizando com conteúdo', {
    contentLength: content.length,
    filename,
    isOpen
  });

  const handleDownloadMarkdown = () => {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content viewer-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>👁️ Visualizar Documento</h2>
          <span className="modal-filename">{filename}</span>
          <button className="btn-close" onClick={onClose} title="Fechar">
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="viewer-content">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose}>
            ❌ Fechar
          </button>
          <button className="btn-download" onClick={handleDownloadMarkdown}>
            📥 Baixar Markdown
          </button>
          {onDownload && (
            <button className="btn-download" onClick={onDownload}>
              📄 Baixar PDF
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarkdownViewerModal;
