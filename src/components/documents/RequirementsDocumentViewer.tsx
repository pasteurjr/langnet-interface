import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './RequirementsDocumentViewer.css';
import langnetService from '../../services/langnetService';

interface RequirementsDocumentViewerProps {
  executionId: string;
  projectId: string;
  onClose?: () => void;
}

interface RequirementsDocumentResponse {
  document?: string;
  project_name?: string;
  generated_at?: string;
  execution_id?: string;
}

export const RequirementsDocumentViewer: React.FC<RequirementsDocumentViewerProps> = ({
  executionId,
  projectId,
  onClose
}) => {
  const [markdown, setMarkdown] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<any>(null);

  useEffect(() => {
    loadRequirementsDocument();
  }, [executionId]);

  const loadRequirementsDocument = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await langnetService.getRequirementsDocument(executionId);

      // Handle response - it might be a string or an object
      if (typeof response === 'string') {
        setMarkdown(response);
      } else {
        const docResponse = response as RequirementsDocumentResponse;
        setMarkdown(docResponse.document || '');
        if (docResponse.project_name) {
          setMetadata({
            projectName: docResponse.project_name,
            generatedAt: docResponse.generated_at,
            executionId: docResponse.execution_id
          });
        }
      }
    } catch (err: any) {
      console.error('Failed to load requirements document:', err);
      setError(err.message || 'Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadMD = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `requirements_${metadata?.projectName || 'document'}_${executionId.substring(0, 8)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = () => {
    // TODO: Implement PDF generation
    alert('PDF generation will be implemented in next phase');
  };

  const handleOpenChat = () => {
    // TODO: Navigate to chat with document context
    alert('Chat refinement will be implemented in next phase');
  };

  if (loading) {
    return (
      <div className="requirements-viewer loading">
        <div className="loading-spinner"></div>
        <p>Loading requirements document...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="requirements-viewer error">
        <h2>Error Loading Document</h2>
        <p>{error}</p>
        <button onClick={loadRequirementsDocument}>Retry</button>
        {onClose && <button onClick={onClose}>Close</button>}
      </div>
    );
  }

  return (
    <div className="requirements-viewer">
      <div className="viewer-header">
        <div className="header-info">
          <h1>📄 Documento de Requisitos</h1>
          {metadata && (
            <div className="metadata">
              <span className="project-name">{metadata.projectName}</span>
              <span className="generated-date">
                Generated: {new Date(metadata.generatedAt).toLocaleString()}
              </span>
            </div>
          )}
        </div>

        <div className="viewer-toolbar">
          <button className="btn-download-md" onClick={handleDownloadMD}>
            ⬇️ Download MD
          </button>
          <button className="btn-download-pdf" onClick={handleDownloadPDF}>
            📑 Download PDF
          </button>
          <button className="btn-refine" onClick={handleOpenChat}>
            💬 Refine with Agent
          </button>
          {onClose && (
            <button className="btn-close" onClick={onClose}>
              ✕ Close
            </button>
          )}
        </div>
      </div>

      <div className="viewer-content">
        <div className="markdown-container">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Custom rendering for code blocks (mermaid diagrams)
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '');
                const language = match ? match[1] : '';

                if (!inline && language === 'mermaid') {
                  return (
                    <div className="mermaid-diagram">
                      <pre className="mermaid-code">
                        {String(children).replace(/\n$/, '')}
                      </pre>
                      <p className="mermaid-note">
                        💡 Mermaid diagram - Install mermaid renderer for visualization
                      </p>
                    </div>
                  );
                }

                return !inline ? (
                  <pre className={className}>
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
              // Custom table rendering
              table({ children }: any) {
                return (
                  <div className="table-wrapper">
                    <table>{children}</table>
                  </div>
                );
              },
              // Custom heading with anchor links
              h2({ children }: any) {
                const id = String(children).toLowerCase().replace(/[^\w]+/g, '-');
                return <h2 id={id}>{children}</h2>;
              },
              h3({ children }: any) {
                const id = String(children).toLowerCase().replace(/[^\w]+/g, '-');
                return <h3 id={id}>{children}</h3>;
              }
            }}
          >
            {markdown}
          </ReactMarkdown>
        </div>

        <div className="viewer-sidebar">
          <div className="toc">
            <h3>📑 Table of Contents</h3>
            <div className="toc-content">
              <p>Auto-generated from document headings</p>
              {/* TODO: Generate TOC from markdown headings */}
            </div>
          </div>

          <div className="document-stats">
            <h3>📊 Document Stats</h3>
            <div className="stats-list">
              <div className="stat-item">
                <span className="stat-label">Lines:</span>
                <span className="stat-value">{markdown.split('\n').length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Characters:</span>
                <span className="stat-value">{markdown.length.toLocaleString()}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Sections:</span>
                <span className="stat-value">{(markdown.match(/^##\s/gm) || []).length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
