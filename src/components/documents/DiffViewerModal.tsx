import React from 'react';
import ReactDiffViewer from 'react-diff-viewer-continued';
import './DiffViewerModal.css';

interface DiffViewerModalProps {
  isOpen: boolean;
  oldDocument: string;
  newDocument: string;
  onClose: () => void;
}

const DiffViewerModal: React.FC<DiffViewerModalProps> = ({
  isOpen,
  oldDocument,
  newDocument,
  onClose
}) => {
  if (!isOpen) return null;

  return (
    <div className="diff-modal-overlay" onClick={onClose}>
      <div className="diff-modal-fullscreen" onClick={(e) => e.stopPropagation()}>
        <div className="diff-modal-header">
          <h2>📊 Comparação de Alterações</h2>
          <button className="btn-modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="diff-modal-body">
          <ReactDiffViewer
            oldValue={oldDocument}
            newValue={newDocument}
            splitView={true}
            showDiffOnly={false}
            leftTitle="📄 Antes do Refinamento"
            rightTitle="✨ Depois do Refinamento"
            styles={{
              variables: {
                light: {
                  diffViewerBackground: '#fff',
                  diffViewerColor: '#212529',
                  addedBackground: '#e6ffed',
                  addedColor: '#24292e',
                  removedBackground: '#ffeef0',
                  removedColor: '#24292e',
                  wordAddedBackground: '#acf2bd',
                  wordRemovedBackground: '#fdb8c0',
                  addedGutterBackground: '#cdffd8',
                  removedGutterBackground: '#ffdce0',
                  gutterBackground: '#f6f8fa',
                  gutterBackgroundDark: '#f3f4f6',
                  highlightBackground: '#fffbdd',
                  highlightGutterBackground: '#fff5b1',
                },
              },
              line: {
                padding: '10px 2px',
                fontSize: '14px',
                lineHeight: '20px',
                fontFamily: 'monospace',
              },
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default DiffViewerModal;
