/* src/components/code/CodeEditor.tsx */
import React, { useState, useEffect } from 'react';
import { CodeFile } from '../../types/codeGeneration';

interface CodeEditorProps {
  file: CodeFile;
  onSave: (content: string) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ file, onSave }) => {
  const [content, setContent] = useState(file.content);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setContent(file.content);
    setHasChanges(false);
  }, [file]);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setHasChanges(newContent !== file.content);
  };

  const handleSave = () => {
    onSave(content);
    setHasChanges(false);
  };

  const getLineNumbers = () => {
    const lines = content.split('\n');
    return lines.map((_, index) => index + 1);
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'python': return '🐍';
      case 'yaml': return '📋';
      case 'json': return '📊';
      case 'markdown': return '📝';
      case 'dockerfile': return '🐳';
      case 'requirements': return '📦';
      default: return '📄';
    }
  };

  return (
    <div className="code-editor-view">
      <div className="code-editor-toolbar">
        <div className="code-editor-toolbar-left">
          <span>{getFileIcon(file.type)} {file.name}</span>
          <span>•</span>
          <span>{content.split('\n').length} linhas</span>
          <span>•</span>
          <span>{content.length} caracteres</span>
          {hasChanges && <span className="unsaved-indicator">● Não salvo</span>}
        </div>
        <div className="code-editor-toolbar-right">
          {hasChanges && (
            <button onClick={handleSave} className="save-button">
              💾 Salvar
            </button>
          )}
          <button className="format-button">
            ✨ Formatar
          </button>
        </div>
      </div>
      
      <div className="code-content-area">
        <div className="code-content">
          <div className="code-line-numbers">
            {getLineNumbers().map(lineNum => (
              <div key={lineNum} className="line-number">
                {lineNum}
              </div>
            ))}
          </div>
          <textarea
            className="code-editor"
            value={content}
            onChange={(e) => handleContentChange(e.target.value)}
            spellCheck={false}
          />
        </div>
      </div>
    </div>
  );
};
export default CodeEditor;