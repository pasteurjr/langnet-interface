/* src/pages/SpecificationPage.tsx */
import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText,
  Download,
  RefreshCw,
  Loader,
  AlertCircle,
  CheckCircle,
  Clock,
  Plus,
  ChevronRight,
  History
} from 'lucide-react';
import SpecificationGenerationModal from '../components/specification/SpecificationGenerationModal';
import {
  listSpecifications,
  getSpecification,
  listSpecificationVersions,
  getSpecificationVersion,
  SpecificationSession,
  SpecificationVersion
} from '../services/specificationService';
import { toast } from 'react-toastify';
import ReactMarkdown from 'react-markdown';
import './SpecificationPage.css';

const SpecificationPage: React.FC = () => {
  // List of specifications
  const [specifications, setSpecifications] = useState<SpecificationSession[]>([]);
  const [loadingList, setLoadingList] = useState(true);

  // Selected specification
  const [selectedSpec, setSelectedSpec] = useState<SpecificationSession | null>(null);
  const [loadingSpec, setLoadingSpec] = useState(false);

  // Versions
  const [versions, setVersions] = useState<SpecificationVersion[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<number>(0);
  const [loadingVersions, setLoadingVersions] = useState(false);

  // Document content
  const [documentContent, setDocumentContent] = useState<string>('');

  // Modal
  const [showGenerationModal, setShowGenerationModal] = useState(false);

  // Polling for generating specs
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  const currentProjectId = 'project1'; // TODO: Get from context

  // Load specifications on mount
  useEffect(() => {
    loadSpecifications();
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, []);

  const loadSpecifications = async () => {
    setLoadingList(true);
    try {
      const response = await listSpecifications(undefined, undefined, 50, 0);
      setSpecifications(response.sessions || []);

      // Auto-select first spec if available and none selected
      if (response.sessions && response.sessions.length > 0 && !selectedSpec) {
        handleSelectSpecification(response.sessions[0]);
      }
    } catch (err) {
      console.error('Error loading specifications:', err);
      toast.error('Erro ao carregar especificações');
    } finally {
      setLoadingList(false);
    }
  };

  const handleSelectSpecification = async (spec: SpecificationSession) => {
    setSelectedSpec(spec);
    setLoadingSpec(true);
    setDocumentContent('');

    try {
      // Load full specification details
      const fullSpec = await getSpecification(spec.id);
      setSelectedSpec(fullSpec);

      // Set document content
      if (fullSpec.specification_document) {
        setDocumentContent(fullSpec.specification_document);
      }

      // Load versions
      await loadVersions(spec.id);

      // If status is 'generating', start polling
      if (fullSpec.status === 'generating') {
        startPolling(spec.id);
      } else {
        stopPolling();
      }
    } catch (err) {
      console.error('Error loading specification:', err);
      toast.error('Erro ao carregar especificação');
    } finally {
      setLoadingSpec(false);
    }
  };

  const loadVersions = async (sessionId: string) => {
    setLoadingVersions(true);
    try {
      const response = await listSpecificationVersions(sessionId);
      setVersions(response.versions || []);

      // Auto-select latest version
      if (response.versions && response.versions.length > 0) {
        const latestVersion = Math.max(...response.versions.map((v: SpecificationVersion) => v.version));
        setSelectedVersion(latestVersion);
      }
    } catch (err) {
      console.error('Error loading versions:', err);
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleVersionChange = async (version: number) => {
    if (!selectedSpec) return;

    setSelectedVersion(version);
    try {
      const versionData = await getSpecificationVersion(selectedSpec.id, version);
      if (versionData && versionData.specification_document) {
        setDocumentContent(versionData.specification_document);
      }
    } catch (err) {
      console.error('Error loading version:', err);
      toast.error('Erro ao carregar versão');
    }
  };

  const startPolling = useCallback((sessionId: string) => {
    stopPolling();
    const interval = setInterval(async () => {
      try {
        const spec = await getSpecification(sessionId);
        setSelectedSpec(spec);

        if (spec.status === 'completed' || spec.status === 'failed') {
          stopPolling();
          if (spec.status === 'completed') {
            toast.success('Especificação gerada com sucesso!');
            if (spec.specification_document) {
              setDocumentContent(spec.specification_document);
            }
            await loadVersions(sessionId);
          } else {
            toast.error('Falha na geração da especificação');
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 3000);
    setPollingInterval(interval);
  }, []);

  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  const handleGenerationSuccess = async (sessionId: string) => {
    setShowGenerationModal(false);
    toast.info('Geração de especificação iniciada...');

    // Refresh list and select new spec
    await loadSpecifications();

    // Find and select the new spec
    try {
      const newSpec = await getSpecification(sessionId);
      setSelectedSpec(newSpec);
      setDocumentContent('');

      // Start polling for this spec
      startPolling(sessionId);
    } catch (err) {
      console.error('Error loading new specification:', err);
    }
  };

  const handleDownload = () => {
    if (!documentContent || !selectedSpec) return;

    const blob = new Blob([documentContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedSpec.session_name || 'especificacao'}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'generating':
        return <Loader className="status-icon spinning" size={16} />;
      case 'completed':
        return <CheckCircle className="status-icon success" size={16} />;
      case 'failed':
        return <AlertCircle className="status-icon error" size={16} />;
      default:
        return <Clock className="status-icon" size={16} />;
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      'generating': 'Gerando...',
      'completed': 'Concluído',
      'failed': 'Falhou',
      'cancelled': 'Cancelado',
      'paused': 'Pausado',
      'reviewing': 'Em Revisão'
    };
    return labels[status] || status;
  };

  return (
    <div className="specification-page">
      {/* Header */}
      <div className="specification-header">
        <div className="specification-header-left">
          <h1>
            <FileText size={28} />
            Especificação Funcional
          </h1>
          <p>Gere e gerencie especificações funcionais a partir dos requisitos do projeto</p>
        </div>
        <div className="specification-header-actions">
          <button
            className="spec-action-button secondary"
            onClick={loadSpecifications}
            disabled={loadingList}
          >
            <RefreshCw size={18} className={loadingList ? 'spinning' : ''} />
            Atualizar
          </button>
          <button
            className="spec-action-button primary"
            onClick={() => setShowGenerationModal(true)}
          >
            <Plus size={18} />
            Nova Especificação
          </button>
        </div>
      </div>

      <div className="specification-content">
        {/* Sidebar - List of specifications */}
        <div className="specification-sidebar">
          <div className="spec-sidebar-header">
            <h3>Especificações ({specifications.length})</h3>
          </div>

          <div className="spec-sidebar-content">
            {loadingList ? (
              <div className="spec-loading">
                <Loader className="spinning" size={32} />
                <p>Carregando...</p>
              </div>
            ) : specifications.length === 0 ? (
              <div className="spec-empty-state">
                <FileText size={48} />
                <h4>Nenhuma especificação</h4>
                <p>Clique em "Nova Especificação" para gerar uma</p>
              </div>
            ) : (
              <ul className="spec-list">
                {specifications.map(spec => (
                  <li
                    key={spec.id}
                    className={`spec-list-item ${selectedSpec?.id === spec.id ? 'active' : ''}`}
                    onClick={() => handleSelectSpecification(spec)}
                  >
                    <div className="spec-list-item-header">
                      {getStatusIcon(spec.status)}
                      <span className="spec-list-item-name">
                        {spec.session_name || 'Sem nome'}
                      </span>
                      <ChevronRight size={16} />
                    </div>
                    <div className="spec-list-item-meta">
                      <span className={`spec-status-badge ${spec.status}`}>
                        {getStatusLabel(spec.status)}
                      </span>
                      <span className="spec-list-item-date">
                        {formatDate(spec.created_at)}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Main content - Document viewer */}
        <div className="specification-main">
          {!selectedSpec ? (
            <div className="spec-empty-state large">
              <FileText size={64} />
              <h3>Selecione uma especificação</h3>
              <p>Escolha uma especificação na lista ou gere uma nova</p>
              <button
                className="spec-action-button primary"
                onClick={() => setShowGenerationModal(true)}
              >
                <Plus size={18} />
                Nova Especificação
              </button>
            </div>
          ) : (
            <>
              {/* Document header */}
              <div className="spec-main-header">
                <div className="spec-document-info">
                  <h2>{selectedSpec.session_name || 'Especificação'}</h2>
                  <div className="spec-document-meta">
                    {getStatusIcon(selectedSpec.status)}
                    <span className={`spec-status-badge ${selectedSpec.status}`}>
                      {getStatusLabel(selectedSpec.status)}
                    </span>
                    <span>Criado em {formatDate(selectedSpec.created_at)}</span>
                    {selectedSpec.generation_time_ms && (
                      <span>Tempo: {(selectedSpec.generation_time_ms / 1000).toFixed(1)}s</span>
                    )}
                  </div>
                </div>
                <div className="spec-main-actions">
                  {versions.length > 0 && (
                    <div className="spec-version-selector">
                      <History size={16} />
                      <select
                        value={selectedVersion}
                        onChange={(e) => handleVersionChange(parseInt(e.target.value))}
                        disabled={loadingVersions}
                      >
                        {versions.map(v => (
                          <option key={v.version} value={v.version}>
                            Versão {v.version}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  <button
                    className="spec-action-button secondary"
                    onClick={handleDownload}
                    disabled={!documentContent}
                  >
                    <Download size={16} />
                    Download MD
                  </button>
                </div>
              </div>

              {/* Document content */}
              <div className="spec-document-container">
                {loadingSpec ? (
                  <div className="spec-loading">
                    <Loader className="spinning" size={48} />
                    <p>Carregando especificação...</p>
                  </div>
                ) : selectedSpec.status === 'generating' ? (
                  <div className="spec-generating">
                    <Loader className="spinning" size={64} />
                    <h3>Gerando Especificação...</h3>
                    <p>Isso pode levar alguns minutos. A página será atualizada automaticamente.</p>
                    <div className="spec-generating-progress">
                      <div className="progress-bar">
                        <div className="progress-fill animate"></div>
                      </div>
                    </div>
                  </div>
                ) : selectedSpec.status === 'failed' ? (
                  <div className="spec-error">
                    <AlertCircle size={64} />
                    <h3>Falha na Geração</h3>
                    <p>Ocorreu um erro ao gerar a especificação.</p>
                    {selectedSpec.generation_log && (
                      <pre className="error-log">{selectedSpec.generation_log}</pre>
                    )}
                    <button
                      className="spec-action-button primary"
                      onClick={() => setShowGenerationModal(true)}
                    >
                      Tentar Novamente
                    </button>
                  </div>
                ) : documentContent ? (
                  <div className="spec-markdown-content">
                    <ReactMarkdown>{documentContent}</ReactMarkdown>
                  </div>
                ) : (
                  <div className="spec-empty-state">
                    <FileText size={48} />
                    <h4>Documento vazio</h4>
                    <p>Esta especificação não possui conteúdo</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Generation Modal */}
      {showGenerationModal && (
        <SpecificationGenerationModal
          isOpen={showGenerationModal}
          onClose={() => setShowGenerationModal(false)}
          onSuccess={handleGenerationSuccess}
          projectId={currentProjectId}
        />
      )}
    </div>
  );
};

export default SpecificationPage;
