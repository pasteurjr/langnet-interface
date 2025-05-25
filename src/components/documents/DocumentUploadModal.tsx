import React, { useState, useRef } from 'react';
import './DocumentUploadModal.css';

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (files: FileList, instructions?: string) => void;
  isUploading?: boolean;
}

const DocumentUploadModal: React.FC<DocumentUploadModalProps> = ({
  isOpen,
  onClose,
  onUpload,
  isUploading = false
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [instructions, setInstructions] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFiles(e.target.files);
    }
  };

  const handleUpload = () => {
    if (selectedFiles) {
      onUpload(selectedFiles, instructions);
      setSelectedFiles(null);
      setInstructions('');
    }
  };

  const removeFile = (indexToRemove: number) => {
    if (selectedFiles) {
      const dt = new DataTransfer();
      Array.from(selectedFiles).forEach((file, index) => {
        if (index !== indexToRemove) {
          dt.items.add(file);
        }
      });
      setSelectedFiles(dt.files);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('doc')) return '📝';
    if (type.includes('text')) return '📃';
    if (type.includes('markdown')) return '📋';
    return '📄';
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="upload-modal">
        <div className="modal-header">
          <h2>Upload de Documentos</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          <div className="upload-section">
            <div 
              className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="drop-zone-content">
                <div className="upload-icon">📁</div>
                <div className="upload-text">
                  <p>Arraste e solte arquivos aqui ou clique para selecionar</p>
                  <p className="upload-hint">
                    Formatos suportados: PDF, DOC, DOCX, TXT, MD
                  </p>
                  <p className="upload-limit">
                    Tamanho máximo: 50MB por arquivo
                  </p>
                </div>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {selectedFiles && selectedFiles.length > 0 && (
            <div className="selected-files">
              <h3>Arquivos Selecionados</h3>
              <div className="files-list">
                {Array.from(selectedFiles).map((file, index) => (
                  <div key={index} className="file-item">
                    <div className="file-info">
                      <span className="file-icon">{getFileIcon(file.type)}</span>
                      <div className="file-details">
                        <span className="file-name">{file.name}</span>
                        <span className="file-size">{formatFileSize(file.size)}</span>
                      </div>
                    </div>
                    <button 
                      className="remove-file"
                      onClick={() => removeFile(index)}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="instructions-section">
            <h3>Instruções Adicionais para Análise</h3>
            <textarea
              className="instructions-textarea"
              placeholder="Adicione instruções específicas para orientar a análise dos documentos. Por exemplo: 'Focar em requisitos de segurança', 'Identificar integrações com sistemas externos', etc."
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              rows={4}
            />
            <div className="instructions-help">
              <p>💡 Dicas para melhores resultados:</p>
              <ul>
                <li>Mencione o domínio da aplicação (ex: e-commerce, saúde, financeiro)</li>
                <li>Especifique aspectos importantes (performance, segurança, usabilidade)</li>
                <li>Indique se há padrões ou frameworks específicos a seguir</li>
                <li>Destaque integrações ou sistemas legados existentes</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {selectedFiles && selectedFiles.length > 0 && (
              <span className="files-count">
                {selectedFiles.length} arquivo(s) selecionado(s)
              </span>
            )}
          </div>
          <div className="footer-actions">
            <button 
              className="btn-cancel" 
              onClick={onClose}
              disabled={isUploading}
            >
              Cancelar
            </button>
            <button 
              className="btn-upload" 
              onClick={handleUpload}
              disabled={!selectedFiles || selectedFiles.length === 0 || isUploading}
            >
              {isUploading ? (
                <>
                  <span className="spinner"></span>
                  Enviando...
                </>
              ) : (
                <>
                  📤 Enviar e Analisar
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadModal;