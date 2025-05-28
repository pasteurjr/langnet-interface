import React, { useState } from 'react';
import { Play, CheckCircle, Clock, AlertCircle, ChevronDown, ChevronRight, Terminal, Package } from 'lucide-react';
import { CiCdPipeline, PipelineStage } from '../../types/deployment';
import './deployment.css';

interface PipelineViewerProps {
  pipeline: CiCdPipeline;
  isActive: boolean;
}

export const PipelineViewer: React.FC<PipelineViewerProps> = ({
  pipeline,
  isActive
}) => {
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set(['deploy']));

  const toggleStageExpansion = (stageId: string) => {
    const newExpanded = new Set(expandedStages);
    if (newExpanded.has(stageId)) {
      newExpanded.delete(stageId);
    } else {
      newExpanded.add(stageId);
    }
    setExpandedStages(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle size={16} color="#16a34a" />;
      case 'running': return <Clock size={16} color="#f59e0b" />;
      case 'failed': return <AlertCircle size={16} color="#dc2626" />;
      case 'pending': return <Clock size={16} color="#6b7280" />;
      case 'skipped': return <AlertCircle size={16} color="#6b7280" />;
      default: return <Clock size={16} color="#6b7280" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#16a34a';
      case 'running': return '#f59e0b';
      case 'failed': return '#dc2626';
      case 'pending': return '#6b7280';
      case 'skipped': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A';
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR');
  };

  const getTotalDuration = () => {
    if (pipeline.totalDuration) {
      return formatDuration(pipeline.totalDuration);
    }
    
    const completed = pipeline.stages.filter(s => s.endTime);
    if (completed.length === 0) return 'N/A';
    
    const total = completed.reduce((sum, stage) => sum + (stage.duration || 0), 0);
    return formatDuration(total);
  };

  return (
    <div className="pipeline-viewer">
      <div className="pipeline-header">
        <div className="pipeline-info">
          <h3>{pipeline.name}</h3>
          <div className="pipeline-meta">
            <span className="pipeline-id">#{pipeline.id}</span>
            <span className="pipeline-branch">Branch: {pipeline.branch}</span>
            <span className="pipeline-commit">Commit: {pipeline.commit.substring(0, 8)}</span>
            <span className="pipeline-version">Version: {pipeline.version}</span>
          </div>
        </div>
        <div className="pipeline-status">
          <div 
            className="status-badge"
            style={{ 
              backgroundColor: getStatusColor(pipeline.status) + '20',
              color: getStatusColor(pipeline.status)
            }}
          >
            {getStatusIcon(pipeline.status)}
            {pipeline.status}
          </div>
        </div>
      </div>

      <div className="pipeline-summary">
        <div className="summary-item">
          <span className="summary-label">Iniciado por:</span>
          <span className="summary-value">{pipeline.triggeredBy}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Horário:</span>
          <span className="summary-value">{formatTimestamp(pipeline.triggeredAt)}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Duração:</span>
          <span className="summary-value">{getTotalDuration()}</span>
        </div>
        {pipeline.currentStage && (
          <div className="summary-item">
            <span className="summary-label">Estágio Atual:</span>
            <span className="summary-value">{pipeline.currentStage}</span>
          </div>
        )}
      </div>

      <div className="pipeline-stages">
        <h4>Estágios do Pipeline</h4>
        <div className="stages-list">
          {pipeline.stages.map((stage, index) => (
            <div key={stage.id} className={`stage-item ${stage.status}`}>
              <div 
                className="stage-header"
                onClick={() => toggleStageExpansion(stage.id)}
              >
                <div className="stage-info">
                  <div className="stage-number">{index + 1}</div>
                  <div className="stage-details">
                    <div className="stage-name">{stage.name}</div>
                    <div className="stage-meta">
                      {stage.duration && (
                        <span className="stage-duration">{formatDuration(stage.duration)}</span>
                      )}
                      {stage.startTime && (
                        <span className="stage-time">{formatTimestamp(stage.startTime)}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="stage-controls">
                  <div className="stage-status">
                    {getStatusIcon(stage.status)}
                    <span className="status-text">{stage.status}</span>
                  </div>
                  {expandedStages.has(stage.id) ? 
                    <ChevronDown size={16} /> : 
                    <ChevronRight size={16} />
                  }
                </div>
              </div>

              {expandedStages.has(stage.id) && (
                <div className="stage-details-expanded">
                  {stage.logs && stage.logs.length > 0 && (
                    <div className="stage-section">
                      <h5>
                        <Terminal size={16} />
                        Logs
                      </h5>
                      <div className="stage-logs">
                        {stage.logs.map((log, logIndex) => (
                          <div key={logIndex} className="log-line">
                            <span className="log-timestamp">
                              {stage.startTime && formatTimestamp(stage.startTime)}
                            </span>
                            <span className="log-message">{log}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {stage.artifacts && stage.artifacts.length > 0 && (
                    <div className="stage-section">
                      <h5>
                        <Package size={16} />
                        Artifacts
                      </h5>
                      <div className="stage-artifacts">
                        {stage.artifacts.map((artifact, artifactIndex) => (
                          <div key={artifactIndex} className="artifact-item">
                            <Package size={14} />
                            <span className="artifact-name">{artifact}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="stage-timeline">
                    <div className="timeline-item">
                      <span className="timeline-label">Início:</span>
                      <span className="timeline-value">
                        {stage.startTime ? formatTimestamp(stage.startTime) : 'Não iniciado'}
                      </span>
                    </div>
                    {stage.endTime && (
                      <div className="timeline-item">
                        <span className="timeline-label">Fim:</span>
                        <span className="timeline-value">{formatTimestamp(stage.endTime)}</span>
                      </div>
                    )}
                    {stage.duration && (
                      <div className="timeline-item">
                        <span className="timeline-label">Duração:</span>
                        <span className="timeline-value">{formatDuration(stage.duration)}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {index < pipeline.stages.length - 1 && (
                <div className="stage-connector">
                  <div className="connector-line" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {isActive && (
        <div className="pipeline-progress">
          <div className="progress-info">
            <Play size={16} />
            <span>Pipeline em execução...</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{
                width: `${(pipeline.stages.filter(s => s.status === 'success').length / pipeline.stages.length) * 100}%`
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};