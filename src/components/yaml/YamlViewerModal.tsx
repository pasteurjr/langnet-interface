import React from 'react';
import './YamlViewerModal.css';

interface YamlViewerModalProps {
  isOpen: boolean;
  content: string;
  filename: string;
  onClose: () => void;
}

const YamlViewerModal: React.FC<YamlViewerModalProps> = ({
  isOpen,
  content,
  filename,
  onClose
}) => {
  if (!isOpen) return null;

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/yaml;charset=utf-8' });
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
      <div className="yaml-viewer-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>Visualizar YAML</h2>
            <span className="modal-filename">{filename}</span>
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <pre className="yaml-content">
            <code>{content}</code>
          </pre>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose}>
            Fechar
          </button>
          <button className="btn-download" onClick={handleDownload}>
            Baixar YAML
          </button>
        </div>
      </div>
    </div>
  );
};

export default YamlViewerModal;
