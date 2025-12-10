/* src/components/specification/SpecificationGenerationModal.tsx */
import React, { useState, useEffect } from 'react';
import { Document } from '../../types';
import './SpecificationGenerationModal.css';
import { listSessions, SessionSummary } from '../../services/requirementsHistoryService';
import { getDocumentVersions } from '../../services/documentService';
import { createSpecificationSession, CreateSpecificationRequest } from '../../services/specificationService';
import { toast } from 'react-toastify';

interface SpecificationGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (sessionId: string) => void;
  projectId: string;
}

interface DocumentVersion {
  version: number;
  created_at: string;
  change_description: string;
  change_type: 'analysis' | 'refinement' | 'manual_edit';
  doc_size: number;
}

const SpecificationGenerationModal: React.FC<SpecificationGenerationModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  projectId
}) => {
  // Requirements selection
  const [requirementsSessions, setRequirementsSessions] = useState<SessionSummary[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [selectedSessionName, setSelectedSessionName] = useState<string>('');
  const [availableVersions, setAvailableVersions] = useState<DocumentVersion[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<number>(0);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [loadingVersions, setLoadingVersions] = useState(false);

  // Optional complementary documents (for future implementation)
  const [complementaryDocs, setComplementaryDocs] = useState<string[]>([]);

  // Configuration options
  const [includeDataModel, setIncludeDataModel] = useState(true);
  const [includeUseCases, setIncludeUseCases] = useState(true);
  const [includeBusinessRules, setIncludeBusinessRules] = useState(true);
  const [includeGlossary, setIncludeGlossary] = useState(true);
  const [detailLevel, setDetailLevel] = useState<'basic' | 'detailed' | 'comprehensive'>('detailed');
  const [targetAudience, setTargetAudience] = useState<'technical' | 'business' | 'mixed'>('mixed');
  const [customInstructions, setCustomInstructions] = useState('');
  const [sessionName, setSessionName] = useState('');

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);

  // Load requirements sessions on modal open
  useEffect(() => {
    if (isOpen) {
      loadRequirementsSessions();
    }
  }, [isOpen]);

  // Load versions when session is selected
  useEffect(() => {
    if (selectedSessionId) {
      loadVersions(selectedSessionId);
    } else {
      setAvailableVersions([]);
      setSelectedVersion(0);
    }
  }, [selectedSessionId]);

  const loadRequirementsSessions = async () => {
    setLoadingSessions(true);
    try {
      const response = await listSessions(50, 0);
      // Filter only completed sessions
      const completedSessions = response.sessions.filter(s => s.status === 'completed');
      setRequirementsSessions(completedSessions);

      // Auto-select first session if available
      if (completedSessions.length > 0 && !selectedSessionId) {
        setSelectedSessionId(completedSessions[0].id);
        setSelectedSessionName(completedSessions[0].session_name);
      }
    } catch (err) {
      console.error('Error loading requirements sessions:', err);
      toast.error('Erro ao carregar sessões de requisitos');
    } finally {
      setLoadingSessions(false);
    }
  };

  const loadVersions = async (sessionId: string) => {
    setLoadingVersions(true);
    try {
      const response = await getDocumentVersions(sessionId);
      setAvailableVersions(response.versions || []);

      // Auto-select latest version (highest version number)
      if (response.versions && response.versions.length > 0) {
        const latestVersion = Math.max(...response.versions.map(v => v.version));
        setSelectedVersion(latestVersion);
      }
    } catch (err) {
      console.error('Error loading versions:', err);
      toast.error('Erro ao carregar versões do documento');
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleSessionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const sessionId = e.target.value;
    setSelectedSessionId(sessionId);

    const session = requirementsSessions.find(s => s.id === sessionId);
    if (session) {
      setSelectedSessionName(session.session_name);
    }
  };

  const handleGenerate = async () => {
    if (!selectedSessionId || !selectedVersion) {
      toast.error('Selecione uma sessão de requisitos e versão');
      return;
    }

    setIsGenerating(true);
    try {
      const request: CreateSpecificationRequest = {
        project_id: projectId,
        requirements_session_id: selectedSessionId,
        requirements_version: selectedVersion,
        complementary_document_ids: complementaryDocs,
        session_name: sessionName.trim() || undefined,
        detail_level: detailLevel,
        target_audience: targetAudience,
        include_data_model: includeDataModel,
        include_use_cases: includeUseCases,
        include_business_rules: includeBusinessRules,
        include_glossary: includeGlossary,
        custom_instructions: customInstructions.trim() || undefined
      };

      console.log('🚀 Creating specification session:', request);
      const response = await createSpecificationSession(request);

      toast.success('Geração de especificação iniciada!');
      console.log('✅ Specification session created:', response);

      if (onSuccess) {
        onSuccess(response.session_id);
      }

      onClose();
    } catch (err: any) {
      console.error('❌ Error generating specification:', err);
      toast.error(err.message || 'Erro ao gerar especificação');
    } finally {
      setIsGenerating(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getChangeTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'analysis': 'Análise Inicial',
      'refinement': 'Refinamento',
      'manual_edit': 'Edição Manual'
    };
    return labels[type] || type;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="spec-generation-modal">
        <div className="modal-header">
          <h2>🚀 Gerar Especificação Funcional</h2>
          <button className="close-button" onClick={onClose} disabled={isGenerating}>×</button>
        </div>

        <div className="modal-content">
          {/* Requirements Source Selection */}
          <div className="generation-step">
            <h3>📄 Documento de Requisitos (Fonte Principal)</h3>
            <p className="step-description">
              Selecione a sessão e versão do documento de requisitos que será usada como <strong>fonte primária</strong> para gerar a especificação funcional.
            </p>

            <div className="selection-group">
              <label className="selection-label">
                <span>Sessão de Requisitos:</span>
                {loadingSessions && <span className="loading-indicator">Carregando...</span>}
              </label>
              <select
                className="selection-input"
                value={selectedSessionId}
                onChange={handleSessionChange}
                disabled={loadingSessions || isGenerating}
              >
                <option value="">Selecione uma sessão...</option>
                {requirementsSessions.map(session => (
                  <option key={session.id} value={session.id}>
                    {session.session_name} ({formatDate(session.created_at)})
                  </option>
                ))}
              </select>
            </div>

            {selectedSessionId && (
              <div className="selection-group">
                <label className="selection-label">
                  <span>Versão do Documento:</span>
                  {loadingVersions && <span className="loading-indicator">Carregando...</span>}
                </label>
                <select
                  className="selection-input"
                  value={selectedVersion}
                  onChange={(e) => setSelectedVersion(parseInt(e.target.value))}
                  disabled={loadingVersions || availableVersions.length === 0 || isGenerating}
                >
                  <option value={0}>Selecione uma versão...</option>
                  {availableVersions.map(version => (
                    <option key={version.version} value={version.version}>
                      Versão {version.version} - {getChangeTypeLabel(version.change_type)} ({formatFileSize(version.doc_size)})
                    </option>
                  ))}
                </select>
                {selectedVersion > 0 && (
                  <div className="version-info">
                    {(() => {
                      const versionData = availableVersions.find(v => v.version === selectedVersion);
                      return versionData ? (
                        <>
                          <p><strong>📅 Data:</strong> {formatDate(versionData.created_at)}</p>
                          <p><strong>📝 Descrição:</strong> {versionData.change_description}</p>
                        </>
                      ) : null;
                    })()}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Optional Session Name */}
          <div className="generation-step">
            <h3>📝 Nome da Especificação (Opcional)</h3>
            <input
              type="text"
              className="session-name-input"
              placeholder="Ex: Especificação Funcional v1.0"
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              disabled={isGenerating}
            />
            <p className="input-hint">Se não especificado, será gerado automaticamente com data/hora</p>
          </div>

          {/* Advanced Configuration */}
          <div className="generation-step">
            <h3>⚙️ Configurações da Geração</h3>
            <div className="config-grid">
              <div className="config-group">
                <h4>Seções a Incluir</h4>
                <div className="checkbox-options">
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeDataModel}
                      onChange={(e) => setIncludeDataModel(e.target.checked)}
                      disabled={isGenerating}
                    />
                    <span>🗃️ Modelo de Dados Conceitual</span>
                  </label>
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeUseCases}
                      onChange={(e) => setIncludeUseCases(e.target.checked)}
                      disabled={isGenerating}
                    />
                    <span>👤 Casos de Uso Detalhados</span>
                  </label>
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeBusinessRules}
                      onChange={(e) => setIncludeBusinessRules(e.target.checked)}
                      disabled={isGenerating}
                    />
                    <span>📋 Regras de Negócio</span>
                  </label>
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeGlossary}
                      onChange={(e) => setIncludeGlossary(e.target.checked)}
                      disabled={isGenerating}
                    />
                    <span>📚 Glossário de Termos</span>
                  </label>
                </div>
              </div>

              <div className="config-group">
                <h4>Nível de Detalhamento</h4>
                <div className="radio-options">
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="detailLevel"
                      value="basic"
                      checked={detailLevel === 'basic'}
                      onChange={(e) => setDetailLevel(e.target.value as any)}
                      disabled={isGenerating}
                    />
                    <div className="radio-info">
                      <span className="radio-title">📝 Básico</span>
                      <span className="radio-description">Visão geral de alto nível</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="detailLevel"
                      value="detailed"
                      checked={detailLevel === 'detailed'}
                      onChange={(e) => setDetailLevel(e.target.value as any)}
                      disabled={isGenerating}
                    />
                    <div className="radio-info">
                      <span className="radio-title">📊 Detalhado</span>
                      <span className="radio-description">Equilíbrio entre visão geral e detalhes</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="detailLevel"
                      value="comprehensive"
                      checked={detailLevel === 'comprehensive'}
                      onChange={(e) => setDetailLevel(e.target.value as any)}
                      disabled={isGenerating}
                    />
                    <div className="radio-info">
                      <span className="radio-title">🔍 Abrangente</span>
                      <span className="radio-description">Máximo nível de detalhamento</span>
                    </div>
                  </label>
                </div>
              </div>

              <div className="config-group">
                <h4>Público-Alvo</h4>
                <div className="radio-options">
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="targetAudience"
                      value="technical"
                      checked={targetAudience === 'technical'}
                      onChange={(e) => setTargetAudience(e.target.value as any)}
                      disabled={isGenerating}
                    />
                    <div className="radio-info">
                      <span className="radio-title">👩‍💻 Técnico</span>
                      <span className="radio-description">Terminologia técnica e detalhes de implementação</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="targetAudience"
                      value="business"
                      checked={targetAudience === 'business'}
                      onChange={(e) => setTargetAudience(e.target.value as any)}
                      disabled={isGenerating}
                    />
                    <div className="radio-info">
                      <span className="radio-title">💼 Negócio</span>
                      <span className="radio-description">Linguagem de negócios clara e acessível</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="targetAudience"
                      value="mixed"
                      checked={targetAudience === 'mixed'}
                      onChange={(e) => setTargetAudience(e.target.value as any)}
                      disabled={isGenerating}
                    />
                    <div className="radio-info">
                      <span className="radio-title">🎯 Misto</span>
                      <span className="radio-description">Equilibrio entre aspectos técnicos e de negócio</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Custom Instructions */}
          <div className="generation-step">
            <h3>💬 Instruções Personalizadas (Opcional)</h3>
            <p>Adicione instruções específicas para personalizar a geração da especificação:</p>
            <textarea
              className="instructions-textarea"
              placeholder="Ex: Incluir diagramas de sequência UML, focar em aspectos de segurança, usar terminologia específica do domínio bancário, incluir métricas de performance detalhadas..."
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              rows={4}
              disabled={isGenerating}
            />
          </div>

          {/* Generation Summary */}
          <div className="generation-summary">
            <h3>📋 Resumo da Geração</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">Requisitos:</span>
                <span className="summary-value">
                  {selectedSessionName || 'Não selecionado'} (v{selectedVersion || '-'})
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Nível de detalhamento:</span>
                <span className="summary-value">{detailLevel}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Público-alvo:</span>
                <span className="summary-value">{targetAudience}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Seções incluídas:</span>
                <span className="summary-value">
                  {[
                    includeDataModel && 'Modelo de Dados',
                    includeUseCases && 'Casos de Uso',
                    includeBusinessRules && 'Regras de Negócio',
                    includeGlossary && 'Glossário'
                  ].filter(Boolean).join(', ') || 'Seções padrão'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {!selectedSessionId && (
              <span className="warning">⚠️ Selecione uma sessão de requisitos</span>
            )}
            {selectedSessionId && !selectedVersion && (
              <span className="warning">⚠️ Selecione uma versão do documento</span>
            )}
          </div>
          <div className="footer-actions">
            <button
              className="btn-cancel"
              onClick={onClose}
              disabled={isGenerating}
            >
              Cancelar
            </button>
            <button
              className="btn-generate"
              onClick={handleGenerate}
              disabled={!selectedSessionId || !selectedVersion || isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner"></span>
                  Gerando Especificação...
                </>
              ) : (
                <>
                  ✨ Gerar Especificação
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpecificationGenerationModal;
