import React, { useState } from 'react';
import { X, Clock, User, Tag, ChevronDown, ChevronRight, Zap, MessageCircle } from 'lucide-react';
import { TraceData, SpanData, GenerationData } from '../../types/monitoring';
import './monitoring.css';
interface TraceViewerProps {
  trace: TraceData;
  spans: SpanData[];
  generations: GenerationData[];
  onClose: () => void;
}

export const TraceViewer: React.FC<TraceViewerProps> = ({
  trace,
  spans,
  generations,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'spans' | 'generations' | 'metadata'>('overview');
  const [expandedSpans, setExpandedSpans] = useState<Set<string>>(new Set());
  const [expandedGenerations, setExpandedGenerations] = useState<Set<string>>(new Set());

  const toggleSpanExpansion = (spanId: string) => {
    const newExpanded = new Set(expandedSpans);
    if (newExpanded.has(spanId)) {
      newExpanded.delete(spanId);
    } else {
      newExpanded.add(spanId);
    }
    setExpandedSpans(newExpanded);
  };

  const toggleGenerationExpansion = (generationId: string) => {
    const newExpanded = new Set(expandedGenerations);
    if (newExpanded.has(generationId)) {
      newExpanded.delete(generationId);
    } else {
      newExpanded.add(generationId);
    }
    setExpandedGenerations(newExpanded);
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return '#16a34a';
      case 'error': return '#dc2626';
      case 'running': return '#f59e0b';
      case 'cancelled': return '#6b7280';
      default: return '#3b82f6';
    }
  };

  const totalTokens = generations.reduce((sum, gen) => sum + (gen.usage?.totalTokens || 0), 0);
  const totalCost = generations.reduce((sum, gen) => {
    // Simple cost estimation (this would come from actual pricing)
    const tokens = gen.usage?.totalTokens || 0;
    return sum + (tokens * 0.00003); // Example: $0.03 per 1K tokens
  }, 0);

  return (
    <div className="trace-viewer">
      <div className="trace-viewer-header">
        <div className="trace-header-info">
          <h3>{trace.name}</h3>
          <div className="trace-meta">
            <span className="trace-id">ID: {trace.id}</span>
            <span className="trace-session">Session: {trace.sessionId}</span>
            <span 
              className="trace-status" 
              style={{ color: getStatusColor(trace.status) }}
            >
              {trace.status}
            </span>
          </div>
        </div>
        <button className="trace-viewer-close" onClick={onClose}>
          <X size={20} />
        </button>
      </div>

      <div className="trace-viewer-tabs">
        <button
          className={`trace-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Visão Geral
        </button>
        <button
          className={`trace-tab ${activeTab === 'spans' ? 'active' : ''}`}
          onClick={() => setActiveTab('spans')}
        >
          Spans ({spans.length})
        </button>
        <button
          className={`trace-tab ${activeTab === 'generations' ? 'active' : ''}`}
          onClick={() => setActiveTab('generations')}
        >
          Gerações ({generations.length})
        </button>
        <button
          className={`trace-tab ${activeTab === 'metadata' ? 'active' : ''}`}
          onClick={() => setActiveTab('metadata')}
        >
          Metadata
        </button>
      </div>

      <div className="trace-viewer-content">
        {activeTab === 'overview' && (
          <div className="trace-overview">
            <div className="overview-metrics">
              <div className="metric-item">
                <Clock size={16} />
                <span className="metric-label">Duração:</span>
                <span className="metric-value">{formatDuration(trace.duration)}</span>
              </div>
              <div className="metric-item">
                <Zap size={16} />
                <span className="metric-label">Tokens:</span>
                <span className="metric-value">{totalTokens.toLocaleString()}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Custo Estimado:</span>
                <span className="metric-value">${totalCost.toFixed(4)}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Iniciado:</span>
                <span className="metric-value">{formatTimestamp(trace.startTime)}</span>
              </div>
            </div>

            {trace.input && (
              <div className="trace-section">
                <h4>Input</h4>
                <pre className="trace-data">{JSON.stringify(trace.input, null, 2)}</pre>
              </div>
            )}

            {trace.output && (
              <div className="trace-section">
                <h4>Output</h4>
                <pre className="trace-data">{JSON.stringify(trace.output, null, 2)}</pre>
              </div>
            )}

            {trace.tags && trace.tags.length > 0 && (
              <div className="trace-section">
                <h4>Tags</h4>
                <div className="trace-tags">
                  {trace.tags.map(tag => (
                    <span key={tag} className="trace-tag">
                      <Tag size={12} />
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'spans' && (
          <div className="spans-list">
            {spans.length === 0 ? (
              <div className="empty-state">
                <p>Nenhum span encontrado para este trace.</p>
              </div>
            ) : (
              spans.map(span => (
                <div key={span.id} className="span-item">
                  <div 
                    className="span-header"
                    onClick={() => toggleSpanExpansion(span.id)}
                  >
                    {expandedSpans.has(span.id) ? 
                      <ChevronDown size={16} /> : 
                      <ChevronRight size={16} />
                    }
                    <span className="span-name">{span.name}</span>
                    <span className="span-duration">{formatDuration(span.duration)}</span>
                  </div>
                  
                  {expandedSpans.has(span.id) && (
                    <div className="span-details">
                      <div className="span-meta">
                        <span>ID: {span.id}</span>
                        <span>Iniciado: {formatTimestamp(span.startTime)}</span>
                        {span.endTime && (
                          <span>Finalizado: {formatTimestamp(span.endTime)}</span>
                        )}
                      </div>

                      {span.input && (
                        <div className="span-section">
                          <h5>Input</h5>
                          <pre className="span-data">{JSON.stringify(span.input, null, 2)}</pre>
                        </div>
                      )}

                      {span.output && (
                        <div className="span-section">
                          <h5>Output</h5>
                          <pre className="span-data">{JSON.stringify(span.output, null, 2)}</pre>
                        </div>
                      )}

                      {span.metadata && Object.keys(span.metadata).length > 0 && (
                        <div className="span-section">
                          <h5>Metadata</h5>
                          <pre className="span-data">{JSON.stringify(span.metadata, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'generations' && (
          <div className="generations-list">
            {generations.length === 0 ? (
              <div className="empty-state">
                <p>Nenhuma geração encontrada para este trace.</p>
              </div>
            ) : (
              generations.map(generation => (
                <div key={generation.id} className="generation-item">
                  <div 
                    className="generation-header"
                    onClick={() => toggleGenerationExpansion(generation.id)}
                  >
                    {expandedGenerations.has(generation.id) ? 
                      <ChevronDown size={16} /> : 
                      <ChevronRight size={16} />
                    }
                    <MessageCircle size={16} />
                    <span className="generation-name">{generation.name}</span>
                    <span className="generation-model">{generation.model}</span>
                    <span className="generation-tokens">
                      {generation.usage?.totalTokens || 0} tokens
                    </span>
                    <span className="generation-duration">{formatDuration(generation.duration)}</span>
                  </div>
                  
                  {expandedGenerations.has(generation.id) && (
                    <div className="generation-details">
                      <div className="generation-meta">
                        <span>ID: {generation.id}</span>
                        <span>Modelo: {generation.model}</span>
                        <span>Iniciado: {formatTimestamp(generation.startTime)}</span>
                        {generation.endTime && (
                          <span>Finalizado: {formatTimestamp(generation.endTime)}</span>
                        )}
                      </div>

                      {generation.modelParameters && (
                        <div className="generation-section">
                          <h5>Parâmetros do Modelo</h5>
                          <pre className="generation-data">
                            {JSON.stringify(generation.modelParameters, null, 2)}
                          </pre>
                        </div>
                      )}

                      {generation.prompt && (
                        <div className="generation-section">
                          <h5>Prompt</h5>
                          <pre className="generation-data">
                            {typeof generation.prompt === 'string' 
                              ? generation.prompt 
                              : JSON.stringify(generation.prompt, null, 2)
                            }
                          </pre>
                        </div>
                      )}

                      {generation.completion && (
                        <div className="generation-section">
                          <h5>Resposta</h5>
                          <pre className="generation-data">{generation.completion}</pre>
                        </div>
                      )}

                      {generation.usage && (
                        <div className="generation-section">
                          <h5>Uso de Tokens</h5>
                          <div className="token-usage">
                            <span>Prompt: {generation.usage.promptTokens}</span>
                            <span>Completion: {generation.usage.completionTokens}</span>
                            <span>Total: {generation.usage.totalTokens}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'metadata' && (
          <div className="trace-metadata">
            <div className="metadata-section">
              <h4>Informações do Trace</h4>
              <div className="metadata-grid">
                <div className="metadata-item">
                  <span className="metadata-label">ID:</span>
                  <span className="metadata-value">{trace.id}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Session ID:</span>
                  <span className="metadata-value">{trace.sessionId}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Status:</span>
                  <span className="metadata-value">{trace.status}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Level:</span>
                  <span className="metadata-value">{trace.level}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Público:</span>
                  <span className="metadata-value">{trace.public ? 'Sim' : 'Não'}</span>
                </div>
                {trace.version && (
                  <div className="metadata-item">
                    <span className="metadata-label">Versão:</span>
                    <span className="metadata-value">{trace.version}</span>
                  </div>
                )}
                {trace.release && (
                  <div className="metadata-item">
                    <span className="metadata-label">Release:</span>
                    <span className="metadata-value">{trace.release}</span>
                  </div>
                )}
              </div>
            </div>

            {trace.userProps && Object.keys(trace.userProps).length > 0 && (
              <div className="metadata-section">
                <h4>Propriedades do Usuário</h4>
                <pre className="metadata-data">
                  {JSON.stringify(trace.userProps, null, 2)}
                </pre>
              </div>
            )}

            {trace.metadata && Object.keys(trace.metadata).length > 0 && (
              <div className="metadata-section">
                <h4>Metadata Adicional</h4>
                <pre className="metadata-data">
                  {JSON.stringify(trace.metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};