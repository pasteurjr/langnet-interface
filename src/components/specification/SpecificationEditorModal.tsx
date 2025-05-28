/* src/components/specification/SpecificationEditorModal.tsx */
import React, { useState, useEffect } from 'react';
import { SpecificationSection } from '../../types/';

interface SpecificationEditorModalProps {
  isOpen: boolean;
  section: SpecificationSection;
  onClose: () => void;
  onSave: (sectionId: string, content: string) => void;
}

const SpecificationEditorModal: React.FC<SpecificationEditorModalProps> = ({
  isOpen,
  section,
  onClose,
  onSave
}) => {
  const [content, setContent] = useState(section.content);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setContent(section.content);
    setHasChanges(false);
  }, [section]);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setHasChanges(newContent !== section.content);
  };

  const handleSave = () => {
    onSave(section.id, content);
    setHasChanges(false);
  };

  const handleClose = () => {
    if (hasChanges) {
      if (window.confirm('Há alterações não salvas. Deseja realmente fechar?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="spec-editor-modal">
        <div className="modal-header">
          <h2>✏️ Editar Seção - {section.title}</h2>
          <button className="close-button" onClick={handleClose}>×</button>
        </div>
        
        <div className="modal-content">
          <div className="editor-toolbar">
            <div className="toolbar-info">
              <span>📝 Markdown suportado</span>
              <span>📊 {content.split(' ').length} palavras</span>
            </div>
            <div className="toolbar-actions">
              <button onClick={() => handleContentChange(content + '\n\n## Nova Subseção\n\n')}>
                Adicionar Subseção
              </button>
            </div>
          </div>
          
          <textarea
            className="content-editor"
            value={content}
            onChange={(e) => handleContentChange(e.target.value)}
            placeholder="Digite o conteúdo da seção..."
          />
        </div>
        
        <div className="modal-footer">
          <div className="footer-info">
            {hasChanges && <span className="changes-indicator">● Alterações não salvas</span>}
          </div>
          <div className="footer-actions">
            <button className="btn-cancel" onClick={handleClose}>
              Cancelar
            </button>
            <button 
              className="btn-save" 
              onClick={handleSave}
              disabled={!hasChanges}
            >
              💾 Salvar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
export { SpecificationEditorModal}; 