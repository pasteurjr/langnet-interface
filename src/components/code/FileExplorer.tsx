/* src/components/code/FileExplorer.tsx */
import React from 'react';
import { ProjectStructure, DirectoryNode, CodeFile } from '../../types/codeGeneration';

interface FileExplorerProps {
  structure: ProjectStructure;
  files: CodeFile[];
  selectedFile: CodeFile | null;
  onFileSelect: (file: CodeFile) => void;
}

const FileExplorer: React.FC<FileExplorerProps> = ({
  structure,
  files,
  selectedFile,
  onFileSelect
}) => {
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

  const renderDirectoryNode = (node: DirectoryNode, depth: number = 0) => {
    if (node.type === 'file') {
      const file = files.find(f => f.path === node.path);
      if (!file) return null;

      return (
        <div 
          key={node.path}
          className={`file-tree-node ${selectedFile?.id === file.id ? 'active' : ''}`}
          style={{ paddingLeft: `${depth * 16}px` }}
          onClick={() => onFileSelect(file)}
        >
          <span className="file-tree-icon">{getFileIcon(file.type)}</span>
          <span>{node.name}</span>
        </div>
      );
    }

    return (
      <div key={node.path}>
        <div 
          className="file-tree-node directory"
          style={{ paddingLeft: `${depth * 16}px` }}
        >
          <span className="file-tree-icon">📁</span>
          <span>{node.name}</span>
        </div>
        {node.children?.map(child => renderDirectoryNode(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="file-explorer">
      <div className="file-tree">
        {structure.directories.map(dir => renderDirectoryNode(dir))}
      </div>
    </div>
  );
};
export default FileExplorer;