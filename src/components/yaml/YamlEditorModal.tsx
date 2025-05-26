import React, { useState, useEffect } from 'react';
import { YamlFile, ValidationIssue } from '../../types';
import './YamlEditorModal.css';

interface YamlEditorModalProps {
  isOpen: boolean;
  yamlFile: YamlFile | null;
  onClose: () => void;
  onSave: (fileId: string, content: string) => void;
  onValidate: (fileId: string, content: string) => ValidationIssue[];
  isSaving?: boolean;
}

const YamlEditorModal: React.FC<YamlEditorModalProps> = ({
  isOpen,
  yamlFile,
  onClose,
  onSave,
  onValidate,
  isSaving = false
}) => {
  const [content, setContent] = useState('');
  const [validationIssues, setValidationIssues] = useState<ValidationIssue[]>([]);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  const [fontSize, setFontSize] = useState(14);
  const [activeTab, setActiveTab] = useState<'editor' | 'validation'>('editor');

  useEffect(() => {
    if (yamlFile) {
      setContent(yamlFile.content);
      setValidationIssues(yamlFile.validationIssues);
      setHasUnsavedChanges(false);
    }
  }, [yamlFile]);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setHasUnsavedChanges(newContent !== yamlFile?.content);
  };

  const handleValidate = () => {
    if (yamlFile) {
      const issues = onValidate(yamlFile.id, content);
      setValidationIssues(issues);
      setActiveTab('validation');
    }
  };

  const handleSave = () => {
    if (yamlFile) {
      onSave(yamlFile.id, content);
      setHasUnsavedChanges(false);
    }
  };

  const handleClose = () => {
    if (hasUnsavedChanges) {
      if (window.confirm('Há alterações não salvas. Deseja realmente fechar?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  const getLineNumbers = () => {
    const lines = content.split('\n');
    return lines.map((_, index) => index + 1);
  };

  const formatValidationIssues = () => {
    const errors = validationIssues.filter(issue => issue.type === 'error');
    const warnings = validationIssues.filter(issue => issue.type === 'warning');
    const suggestions = validationIssues.filter(issue => issue.type === 'suggestion');

    return { errors, warnings, suggestions };
  };

  const getIssueIcon = (type: string) => {
    switch (type) {
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'suggestion': return '💡';
      default: return 'ℹ️';
    }
  };

  const getIssueSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return '#dc2626';
      case 'medium': return '#f59e0b';
      case 'low': return '#2563eb';
      default: return '#6b7280';
    }
  };

  if (!isOpen || !yamlFile) return null;

  const { errors, warnings, suggestions } = formatValidationIssues();

  return (
    <div className="modal-overlay">
      <div className="yaml-editor-modal">
        <div className="modal-header">
          <div className="header-info">
            <h2>✏️ Editor YAML - {yamlFile.name}</h2>
            <div className="file-info">
              <span className="file-type">{yamlFile.type}</span>
              <span className="file-version">v{yamlFile.version}</span>
              {hasUnsavedChanges && (
                <span className="unsaved-indicator">● Não salvo</span>
              )}
            </div>
          </div>
          <div className="header-actions">
            <button 
              className="btn-validate"
              onClick={handleValidate}
              title="Validar YAML"
            >
              🔍 Validar
            </button>
            <button className="close-button" onClick={handleClose}>×</button>
          </div>
        </div>

        <div className="editor-toolbar">
          <div className="editor-options">
            <label className="checkbox-option">
              <input
                type="checkbox"
                checked={showLineNumbers}
                onChange={(e) => setShowLineNumbers(e.target.checked)}
              />
              Números de linha
            </label>
            <div className="font-size-control">
              <label>Tamanho:</label>
              <select
                value={fontSize}
                onChange={(e) => setFontSize(Number(e.target.value))}
              >
                <option value={12}>12px</option>
                <option value={14}>14px</option>
                <option value={16}>16px</option>
                <option value={18}>18px</option>
              </select>
            </div>
          </div>

          <div className="validation-summary">
            {errors.length > 0 && (
              <span className="issue-count error-count">
                ❌ {errors.length} erro(s)
              </span>
            )}
            {warnings.length > 0 && (
              <span className="issue-count warning-count">
                ⚠️ {warnings.length} aviso(s)
              </span>
            )}
            {suggestions.length > 0 && (
              <span className="issue-count suggestion-count">
                💡 {suggestions.length} sugestão(ões)
              </span>
            )}
            {validationIssues.length === 0 && (
              <span className="issue-count success-count">
                ✅ Sem issues
              </span>
            )}
          </div>
        </div>

        <div className="editor-tabs">
          <button 
            className={`tab ${activeTab === 'editor' ? 'active' : ''}`}
            onClick={() => setActiveTab('editor')}
          >
            📝 Editor
          </button>
          <button 
            className={`tab ${activeTab === 'validation' ? 'active' : ''}`}
            onClick={() => setActiveTab('validation')}
          >
            🔍 Validação ({validationIssues.length})
          </button>
        </div>

        <div className="modal-content">
          {activeTab === 'editor' && (
            <div className="editor-container">
              <div className="code-editor">
                {showLineNumbers && (
                  <div className="line-numbers">
                    {getLineNumbers().map(lineNum => (
                      <div key={lineNum} className="line-number">
                        {lineNum}
                      </div>
                    ))}
                  </div>
                )}
                <textarea
                  className="yaml-textarea"
                  value={content}
                  onChange={(e) => handleContentChange(e.target.value)}
                  style={{ fontSize: `${fontSize}px` }}
                  spellCheck={false}
                  wrap="off"
                />
              </div>
            </div>
          )}

          {activeTab === 'validation' && (
            <div className="validation-container">
              {validationIssues.length === 0 ? (
                <div className="no-issues">
                  <div className="success-icon">✅</div>
                  <h3>Nenhuma issue encontrada</h3>
                  <p>O arquivo YAML está válido e bem formatado.</p>
                </div>
              ) : (
                <div className="validation-issues">
                  {errors.length > 0 && (
                    <div className="issue-section">
                      <h3>❌ Erros ({errors.length})</h3>
                      {errors.map((issue, index) => (
                        <div key={index} className="issue-item error">
                          <div className="issue-header">
                            <span className="issue-icon">{getIssueIcon(issue.type)}</span>
                            <span className="issue-location">Linha {issue.line}</span>
                            <span 
                              className="issue-severity"
                              style={{ color: getIssueSeverityColor(issue.severity) }}
                            >
                              {issue.severity}
                            </span>
                          </div>
                          <div className="issue-message">{issue.message}</div>
                          {issue.code && (
                            <div className="issue-code">Código: {issue.code}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {warnings.length > 0 && (
                    <div className="issue-section">
                      <h3>⚠️ Avisos ({warnings.length})</h3>
                      {warnings.map((issue, index) => (
                        <div key={index} className="issue-item warning">
                          <div className="issue-header">
                            <span className="issue-icon">{getIssueIcon(issue.type)}</span>
                            <span className="issue-location">Linha {issue.line}</span>
                            <span 
                              className="issue-severity"
                              style={{ color: getIssueSeverityColor(issue.severity) }}
                            >
                              {issue.severity}
                            </span>
                          </div>
                          <div className="issue-message">{issue.message}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {suggestions.length > 0 && (
                    <div className="issue-section">
                      <h3>💡 Sugestões ({suggestions.length})</h3>
                      {suggestions.map((issue, index) => (
                        <div key={index} className="issue-item suggestion">
                          <div className="issue-header">
                            <span className="issue-icon">{getIssueIcon(issue.type)}</span>
                            <span className="issue-location">Linha {issue.line}</span>
                            <span 
                              className="issue-severity"
                              style={{ color: getIssueSeverityColor(issue.severity) }}
                            >
                              {issue.severity}
                            </span>
                          </div>
                          <div className="issue-message">{issue.message}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            <span className="file-stats">
              {content.split('\n').length} linhas • {content.length} caracteres
            </span>
          </div>
          <div className="footer-actions">
            <button 
              className="btn-cancel" 
              onClick={handleClose}
              disabled={isSaving}
            >
              {hasUnsavedChanges ? 'Cancelar' : 'Fechar'}
            </button>
            <button 
              className="btn-save" 
              onClick={handleSave}
              disabled={!hasUnsavedChanges || isSaving}
            >
              {isSaving ? (
                <>
                  <span className="spinner"></span>
                  Salvando...
                </>
              ) : (
                <>
                  💾 Salvar
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YamlEditorModal;