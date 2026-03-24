import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import pako from 'pako';
import './MarkdownEditorModal.css';

interface MarkdownViewerModalProps {
  isOpen: boolean;
  content: string;
  filename: string;
  onClose: () => void;
  onDownload?: () => void;
}

/**
 * Encode PlantUML text for plantuml.com API
 * Uses DEFLATE compression (pako) + base64 encoding
 * plantuml.com expects deflate-compressed data prefixed with ~1
 */
function encodePlantUML(text: string): string {
  try {
    const data = new TextEncoder().encode(text);
    const compressed = pako.deflate(data, { level: 9 });
    let b64 = '';
    compressed.forEach((byte) => { b64 += String.fromCharCode(byte); });
    const encoded = btoa(b64)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
    return `~1${encoded}`;
  } catch {
    return '';
  }
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
          <div className="markdown-viewer-content">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code(props) {
                  const { children, className, node, ...rest } = props as any;
                  const language = className?.replace('language-', '') || '';
                  const codeText = String(children).trim();

                  if (language === 'plantuml') {
                    const encoded = encodePlantUML(codeText);
                    const url = `https://www.plantuml.com/plantuml/png/${encoded}`;
                    return (
                      <div style={{ margin: '12px 0', textAlign: 'center' }}>
                        <img
                          src={url}
                          alt="Wireframe UI"
                          style={{ maxWidth: '100%', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                            const parent = (e.target as HTMLImageElement).parentElement;
                            if (parent) {
                              parent.innerHTML = `<pre style="background:#f9f9f9;padding:12px;border-radius:6px;font-size:12px">${codeText}</pre>`;
                            }
                          }}
                        />
                      </div>
                    );
                  }

                  return (
                    <code className={className} {...rest}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {content}
            </ReactMarkdown>
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
