import React, { useState } from 'react';
import { YamlFileType, YamlGenerationRequest } from '../../types';
import './YamlGenerationModal.css';

interface YamlGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (request: YamlGenerationRequest) => void;
  isGenerating?: boolean;
  projectId: string;
}

const YamlGenerationModal: React.FC<YamlGenerationModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  isGenerating = false,
  projectId
}) => {
  const [selectedFileTypes, setSelectedFileTypes] = useState<YamlFileType[]>([
    YamlFileType.AGENTS,
    YamlFileType.TASKS
  ]);
  const [instructions, setInstructions] = useState('');
  const [includeComments, setIncludeComments] = useState(true);
  const [formatStyle, setFormatStyle] = useState<'compact' | 'readable' | 'detailed'>('readable');
  const [validationLevel, setValidationLevel] = useState<'basic' | 'strict' | 'comprehensive'>('strict');

  const handleFileTypeToggle = (fileType: YamlFileType) => {
    setSelectedFileTypes(prev => 
      prev.includes(fileType)
        ? prev.filter(type => type !== fileType)
        : [...prev, fileType]
    );
  };

  const handleGenerate = () => {
    const request: YamlGenerationRequest = {
      projectId,
      fileTypes: selectedFileTypes,
      instructions,
      includeComments,
      formatStyle,
      validationLevel
    };
    onGenerate(request);
  };

  const getFileTypeInfo = (type: YamlFileType) => {
    switch (type) {
      case YamlFileType.AGENTS:
        return {
          icon: '🤖',
          title: 'Agentes',
          description: 'Definições dos agentes com roles, goals e backstories'
        };
      case YamlFileType.TASKS:
        return {
          icon: '📋',
          title: 'Tarefas',
          description: 'Especificações das tarefas com descrições e outputs esperados'
        };
      case YamlFileType.TOOLS:
        return {
          icon: '🔧',
          title: 'Ferramentas',
          description: 'Configurações das ferramentas disponíveis para os agentes'
        };
      case YamlFileType.CONFIG:
        return {
          icon: '⚙️',
          title: 'Configuração',
          description: 'Configurações gerais do projeto e parâmetros do sistema'
        };
      default:
        return { icon: '📄', title: 'Arquivo', description: '' };
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="generation-modal">
        <div className="modal-header">
          <h2>🚀 Geração de Arquivos YAML</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          <div className="file-types-section">
            <h3>Selecione os tipos de arquivo para gerar:</h3>
            <div className="file-types-grid">
              {Object.values(YamlFileType).map(fileType => {
                const info = getFileTypeInfo(fileType);
                return (
                  <div
                    key={fileType}
                    className={`file-type-card ${selectedFileTypes.includes(fileType) ? 'selected' : ''}`}
                    onClick={() => handleFileTypeToggle(fileType)}
                  >
                    <div className="file-type-icon">{info.icon}</div>
                    <div className="file-type-info">
                      <div className="file-type-title">{info.title}</div>
                      <div className="file-type-description">{info.description}</div>
                    </div>
                    <div className="file-type-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedFileTypes.includes(fileType)}
                        onChange={() => handleFileTypeToggle(fileType)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="instructions-section">
            <h3>Instruções Específicas</h3>
            <textarea
              className="instructions-textarea"
              placeholder="Adicione instruções específicas para a geração dos arquivos YAML. Por exemplo: 'Incluir validações extras para dados sensíveis', 'Usar nomenclatura específica do domínio', 'Adicionar campos personalizados', etc."
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              rows={4}
            />
            <div className="instructions-help">
              <p>💡 Exemplos de instruções úteis:</p>
              <ul>
                <li>Especificar padrões de nomenclatura (ex: snake_case, camelCase)</li>
                <li>Definir estruturas de dados específicas do domínio</li>
                <li>Incluir campos de metadata adicionais</li>
                <li>Configurar validações específicas</li>
                <li>Adicionar comentários explicativos em pontos específicos</li>
              </ul>
            </div>
          </div>

          <div className="options-section">
            <div className="option-group">
              <h3>Opções de Formatação</h3>
              
              <div className="checkbox-option">
                <label>
                  <input
                    type="checkbox"
                    checked={includeComments}
                    onChange={(e) => setIncludeComments(e.target.checked)}
                  />
                  Incluir comentários explicativos
                </label>
                <p className="option-description">
                  Adiciona comentários no YAML para explicar seções e configurações
                </p>
              </div>

              <div className="select-option">
                <label>Estilo de Formatação:</label>
                <select
                  value={formatStyle}
                  onChange={(e) => setFormatStyle(e.target.value as any)}
                  className="format-select"
                >
                  <option value="compact">Compacto - Mínimo de linhas</option>
                  <option value="readable">Legível - Balanceado</option>
                  <option value="detailed">Detalhado - Máxima clareza</option>
                </select>
                <p className="option-description">
                  Define como o YAML será estruturado e espaçado
                </p>
              </div>

              <div className="select-option">
                <label>Nível de Validação:</label>
                <select
                  value={validationLevel}
                  onChange={(e) => setValidationLevel(e.target.value as any)}
                  className="validation-select"
                >
                  <option value="basic">Básico - Sintaxe e estrutura</option>
                  <option value="strict">Rigoroso - Inclui semântica</option>
                  <option value="comprehensive">Abrangente - Validação completa</option>
                </select>
                <p className="option-description">
                  Define a profundidade da validação aplicada aos arquivos
                </p>
              </div>
            </div>
          </div>

          <div className="preview-section">
            <h3>Resumo da Geração</h3>
            <div className="generation-summary">
              <div className="summary-item">
                <strong>Arquivos selecionados:</strong> {selectedFileTypes.length}
                <div className="selected-files">
                  {selectedFileTypes.map(type => (
                    <span key={type} className="selected-file-tag">
                      {getFileTypeInfo(type).icon} {getFileTypeInfo(type).title}
                    </span>
                  ))}
                </div>
              </div>
              <div className="summary-item">
                <strong>Estilo:</strong> {formatStyle} 
                {includeComments && ' (com comentários)'}
              </div>
              <div className="summary-item">
                <strong>Validação:</strong> {validationLevel}
              </div>
              {instructions && (
                <div className="summary-item">
                  <strong>Instruções personalizadas:</strong> ✅
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {selectedFileTypes.length === 0 && (
              <span className="warning">⚠️ Selecione pelo menos um tipo de arquivo</span>
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
              disabled={selectedFileTypes.length === 0 || isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner"></span>
                  Gerando...
                </>
              ) : (
                <>
                  ✨ Gerar Arquivos YAML
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YamlGenerationModal;