import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './ReviewSuggestionsModal.css';

interface ReviewSuggestionsModalProps {
  isOpen: boolean;
  suggestions: string;
  onClose: () => void;
  onApply: (additionalInstructions?: string) => void;
  isApplying: boolean;
}

const ReviewSuggestionsModal: React.FC<ReviewSuggestionsModalProps> = ({
  isOpen,
  suggestions,
  onClose,
  onApply,
  isApplying
}) => {
  const [additionalInstructions, setAdditionalInstructions] = useState('');

  if (!isOpen) return null;

  const handleApply = () => {
    onApply(additionalInstructions.trim() || undefined);
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="review-modal-overlay" onClick={handleOverlayClick}>
      <div className="review-modal" onClick={(e) => e.stopPropagation()}>
        <div className="review-modal-header">
          <h2>🔍 Sugestões de Revisão</h2>
          <button
            className="review-modal-close-btn"
            onClick={onClose}
            disabled={isApplying}
            aria-label="Fechar"
          >
            ×
          </button>
        </div>

        <div className="review-modal-body">
          <div className="suggestions-preview">
            <ReactMarkdown>{suggestions}</ReactMarkdown>
          </div>

          <div className="additional-instructions">
            <label htmlFor="additional-instructions">
              Instruções Complementares (Opcional)
            </label>
            <textarea
              id="additional-instructions"
              value={additionalInstructions}
              onChange={(e) => setAdditionalInstructions(e.target.value)}
              placeholder="Adicione instruções específicas para aplicar junto com as sugestões acima..."
              rows={4}
              disabled={isApplying}
            />
            <p className="instructions-hint">
              💡 Use este campo para adicionar contexto adicional ou requisitos específicos
              que devem ser considerados ao aplicar as sugestões.
            </p>
          </div>
        </div>

        <div className="review-modal-footer">
          <button
            className="btn-secondary"
            onClick={onClose}
            disabled={isApplying}
          >
            Cancelar
          </button>
          <button
            className="btn-primary"
            onClick={handleApply}
            disabled={isApplying}
          >
            {isApplying ? '⏳ Aplicando Sugestões...' : '✅ Aplicar Sugestões de Melhoria'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReviewSuggestionsModal;
