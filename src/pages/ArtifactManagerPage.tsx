// src/pages/ArtifactManagerPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './ArtifactManagerPage.css';

// Types based on requirements from docs
interface Artifact {
  id: string;
  name: string;
  type: 'document' | 'image' | 'code' | 'model' | 'data' | 'configuration';
  size: number;
  uploadedAt: string;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  category: string;
  tags: string[];
  metadata: {
    author?: string;
    description?: string;
    version?: string;
    format?: string;
    checksum?: string;
  };
  url?: string;
  preview?: string;
  dependencies?: string[];
}

interface ArtifactCategory {
  id: string;
  name: string;
  icon: string;
  count: number;
  color: string;
}

const ArtifactManagerPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [categories] = useState<ArtifactCategory[]>([
    { id: 'document', name: 'Documentos', icon: '📄', count: 12, color: '#3B82F6' },
    { id: 'image', name: 'Imagens', icon: '🖼️', count: 8, color: '#10B981' },
    { id: 'code', name: 'Código', icon: '💻', count: 15, color: '#8B5CF6' },
    { id: 'model', name: 'Modelos', icon: '🧠', count: 5, color: '#F59E0B' },
    { id: 'data', name: 'Dados', icon: '📊', count: 7, color: '#EF4444' },
    { id: 'configuration', name: 'Configurações', icon: '⚙️', count: 3, color: '#6B7280' }
  ]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  // Mock data - seguindo padrão das outras páginas
  useEffect(() => {
    const mockArtifacts: Artifact[] = [
      {
        id: '1',
        name: 'requirements_v1.pdf',
        type: 'document',
        size: 2048576,
        uploadedAt: '2025-01-15T10:30:00Z',
        status: 'ready',
        category: 'Requirements',
        tags: ['spec', 'v1', 'functional'],
        metadata: {
          author: 'System Analyst',
          description: 'Functional requirements document',
          version: '1.0',
          format: 'PDF'
        },
        url: '/artifacts/requirements_v1.pdf',
        preview: 'data:image/svg+xml;base64,PHN2Zz48L3N2Zz4='
      },
      {
        id: '2',
        name: 'agent_model.py',
        type: 'code',
        size: 45678,
        uploadedAt: '2025-01-15T14:20:00Z',
        status: 'ready',
        category: 'Implementation',
        tags: ['python', 'agents', 'core'],
        metadata: {
          author: 'Developer',
          description: 'Main agent model implementation',
          version: '2.1',
          format: 'Python'
        },
        url: '/artifacts/agent_model.py'
      },
      {
        id: '3',
        name: 'system_architecture.png',
        type: 'image',
        size: 1234567,
        uploadedAt: '2025-01-15T16:45:00Z',
        status: 'processing',
        category: 'Design',
        tags: ['architecture', 'diagram', 'system'],
        metadata: {
          author: 'Architect',
          description: 'System architecture overview',
          format: 'PNG'
        }
      }
    ];
    setArtifacts(mockArtifacts);
  }, [projectId]);

  const handleFileUpload = (files: FileList | null) => {
    if (!files) return;
    
    setIsUploading(true);
    
    // Simulate upload process
    Array.from(files).forEach((file, index) => {
      setTimeout(() => {
        const newArtifact: Artifact = {
          id: `new-${Date.now()}-${index}`,
          name: file.name,
          type: getFileType(file.name),
          size: file.size,
          uploadedAt: new Date().toISOString(),
          status: 'uploading',
          category: 'Uploaded',
          tags: ['new'],
          metadata: {
            format: file.name.split('.').pop()?.toUpperCase() || 'UNKNOWN'
          }
        };
        
        setArtifacts(prev => [...prev, newArtifact]);
        
        // Simulate processing
        setTimeout(() => {
          setArtifacts(prev => prev.map(a => 
            a.id === newArtifact.id 
              ? { ...a, status: 'ready' as const }
              : a
          ));
        }, 2000);
      }, index * 500);
    });
    
    setTimeout(() => setIsUploading(false), 3000);
  };

  const getFileType = (fileName: string): Artifact['type'] => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (['pdf', 'doc', 'docx', 'txt', 'md'].includes(ext || '')) return 'document';
    if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(ext || '')) return 'image';
    if (['py', 'js', 'ts', 'json', 'yaml', 'yml'].includes(ext || '')) return 'code';
    if (['pkl', 'model', 'bin'].includes(ext || '')) return 'model';
    if (['csv', 'xlsx', 'json'].includes(ext || '')) return 'data';
    return 'configuration';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const filteredArtifacts = artifacts.filter(artifact => {
    const matchesCategory = selectedCategory === 'all' || artifact.type === selectedCategory;
    const matchesSearch = artifact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         artifact.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: Artifact['status']): string => {
    switch (status) {
      case 'ready': return '#10B981';
      case 'processing': return '#F59E0B';
      case 'uploading': return '#3B82F6';
      case 'error': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getTypeIcon = (type: Artifact['type']): string => {
    switch (type) {
      case 'document': return '📄';
      case 'image': return '🖼️';
      case 'code': return '💻';
      case 'model': return '🧠';
      case 'data': return '📊';
      case 'configuration': return '⚙️';
      default: return '📁';
    }
  };

  return (
    <div className="artifact-manager-page">
      <div className="page-header">
        <div className="header-main">
          <h1>📦 Gestão de Artefatos</h1>
          <p>Gerencie todos os artefatos do projeto de forma organizada</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn btn-secondary"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
          >
            {viewMode === 'grid' ? '📋 Lista' : '🔲 Grade'}
          </button>
          <input
            type="file"
            multiple
            onChange={(e) => handleFileUpload(e.target.files)}
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label htmlFor="file-upload" className="btn btn-primary">
            📁 Upload Arquivos
          </label>
        </div>
      </div>

      <div className="page-content">
        {/* Upload Zone */}
        <div 
          className={`upload-zone ${isDragOver ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {isUploading ? (
            <div className="upload-status">
              <div className="spinner"></div>
              <p>Processando arquivos...</p>
            </div>
          ) : (
            <div className="upload-content">
              <div className="upload-icon">📎</div>
              <p>Arraste arquivos aqui ou <label htmlFor="file-upload" className="upload-link">clique para fazer upload</label></p>
              <small>Suporte a documentos, imagens, código, modelos e dados</small>
            </div>
          )}
        </div>

        {/* Categories */}
        <div className="categories">
          <button 
            className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('all')}
          >
            📁 Todos ({artifacts.length})
          </button>
          {categories.map(category => (
            <button
              key={category.id}
              className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category.id)}
              style={{ borderLeftColor: category.color }}
            >
              {category.icon} {category.name} ({category.count})
            </button>
          ))}
        </div>

        {/* Search and Filters */}
        <div className="search-section">
          <div className="search-input">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Buscar artefatos, tags ou categorias..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="filters">
            <select className="filter-select">
              <option>Todos os status</option>
              <option>Prontos</option>
              <option>Processando</option>
              <option>Erro</option>
            </select>
            <select className="filter-select">
              <option>Ordenar por data</option>
              <option>Ordenar por nome</option>
              <option>Ordenar por tamanho</option>
            </select>
          </div>
        </div>

        {/* Artifacts Grid/List */}
        <div className={`artifacts-container ${viewMode}`}>
          {filteredArtifacts.map(artifact => (
            <div key={artifact.id} className="artifact-card">
              <div className="artifact-header">
                <div className="artifact-icon">
                  {getTypeIcon(artifact.type)}
                </div>
                <div 
                  className="artifact-status"
                  style={{ backgroundColor: getStatusColor(artifact.status) }}
                >
                  {artifact.status}
                </div>
              </div>
              
              <div className="artifact-content">
                <h3 className="artifact-name">{artifact.name}</h3>
                <p className="artifact-description">
                  {artifact.metadata.description || 'Sem descrição'}
                </p>
                
                <div className="artifact-meta">
                  <span className="meta-item">
                    📊 {formatFileSize(artifact.size)}
                  </span>
                  <span className="meta-item">
                    📅 {new Date(artifact.uploadedAt).toLocaleDateString('pt-BR')}
                  </span>
                  {artifact.metadata.version && (
                    <span className="meta-item">
                      🏷️ v{artifact.metadata.version}
                    </span>
                  )}
                </div>

                <div className="artifact-tags">
                  {artifact.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>

              <div className="artifact-actions">
                <button className="action-btn" title="Visualizar">👁️</button>
                <button className="action-btn" title="Download">📥</button>
                <button className="action-btn" title="Compartilhar">📤</button>
                <button className="action-btn" title="Editar">✏️</button>
                <button className="action-btn danger" title="Excluir">🗑️</button>
              </div>
            </div>
          ))}
        </div>

        {filteredArtifacts.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📂</div>
            <h3>Nenhum artefato encontrado</h3>
            <p>
              {searchTerm 
                ? `Nenhum artefato corresponde à busca "${searchTerm}"`
                : 'Faça upload de alguns arquivos para começar'
              }
            </p>
          </div>
        )}
      </div>

      {/* Statistics Panel */}
      <div className="statistics-panel">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-number">{artifacts.length}</div>
            <div className="stat-label">Total de Artefatos</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💾</div>
          <div className="stat-content">
            <div className="stat-number">
              {formatFileSize(artifacts.reduce((sum, a) => sum + a.size, 0))}
            </div>
            <div className="stat-label">Espaço Utilizado</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔄</div>
          <div className="stat-content">
            <div className="stat-number">
              {artifacts.filter(a => a.status === 'processing').length}
            </div>
            <div className="stat-label">Processando</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArtifactManagerPage;