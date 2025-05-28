/* src/components/specification/RequirementsTable.tsx */
import React, { useState } from 'react';
import { FunctionalRequirement, NonFunctionalRequirement } from '../../types/';
import './RequirementsTable.css';

interface RequirementsTableProps {
  requirements: (FunctionalRequirement | NonFunctionalRequirement)[];
  onEdit?: (requirement: FunctionalRequirement | NonFunctionalRequirement) => void;
  onDelete?: (requirementId: string) => void;
}

const RequirementsTable: React.FC<RequirementsTableProps> = ({
  requirements,
  onEdit,
  onDelete
}) => {
  const [sortBy, setSortBy] = useState<'code' | 'priority' | 'complexity'>('code');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const handleSort = (field: 'code' | 'priority' | 'complexity') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const getPriorityOrder = (priority: string) => {
    const order = { 'must_have': 4, 'should_have': 3, 'could_have': 2, 'wont_have': 1 };
    return order[priority as keyof typeof order] || 0;
  };

  const getComplexityOrder = (complexity?: string) => {
    if (!complexity) return 0;
    const order = { 'high': 3, 'medium': 2, 'low': 1 };
    return order[complexity as keyof typeof order] || 0;
  };

  const filteredAndSortedRequirements = requirements
    .filter(req => {
      const matchesSearch = req.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           req.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           req.code.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesPriority = filterPriority === 'all' || req.priority === filterPriority;
      
      return matchesSearch && matchesPriority;
    })
    .sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'code':
          comparison = a.code.localeCompare(b.code);
          break;
        case 'priority':
          comparison = getPriorityOrder(b.priority) - getPriorityOrder(a.priority);
          break;
        case 'complexity':
          const aComplexity = 'complexity' in a ? a.complexity : undefined;
          const bComplexity = 'complexity' in b ? b.complexity : undefined;
          comparison = getComplexityOrder(bComplexity) - getComplexityOrder(aComplexity);
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
      case 'must_have': return 'priority-must-have';
      case 'should_have': return 'priority-should-have';
      case 'could_have': return 'priority-could-have';
      case 'wont_have': return 'priority-wont-have';
      default: return '';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'must_have': return 'Obrigatório';
      case 'should_have': return 'Importante';
      case 'could_have': return 'Desejável';
      case 'wont_have': return 'Futuro';
      default: return priority;
    }
  };

  const getComplexityBadgeClass = (complexity?: string) => {
    switch (complexity) {
      case 'high': return 'complexity-high';
      case 'medium': return 'complexity-medium';
      case 'low': return 'complexity-low';
      default: return '';
    }
  };

  const getComplexityText = (complexity?: string) => {
    switch (complexity) {
      case 'high': return 'Alta';
      case 'medium': return 'Média';
      case 'low': return 'Baixa';
      default: return '-';
    }
  };

  const getCategoryIcon = (category: string) => {
    // Para requisitos não-funcionais
    switch (category) {
      case 'performance': return '⚡';
      case 'security': return '🔒';
      case 'usability': return '👥';
      case 'reliability': return '🛡️';
      case 'scalability': return '📈';
      case 'maintainability': return '🔧';
      default: return '📋';
    }
  };

  const isNonFunctional = (req: any): req is NonFunctionalRequirement => {
    return 'category' in req && typeof req.category === 'string' && 
           ['performance', 'security', 'usability', 'reliability', 'scalability', 'maintainability'].includes(req.category);
  };

  return (
    <div className="requirements-table-container">
      <div className="requirements-controls">
        <div className="search-filter-row">
          <div className="search-box">
            <input
              type="text"
              placeholder="🔍 Buscar requisitos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="filter-controls">
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="priority-filter"
            >
              <option value="all">Todas as prioridades</option>
              <option value="must_have">Obrigatório</option>
              <option value="should_have">Importante</option>
              <option value="could_have">Desejável</option>
              <option value="wont_have">Futuro</option>
            </select>
          </div>
        </div>
        
        <div className="table-info">
          <span className="results-count">
            {filteredAndSortedRequirements.length} de {requirements.length} requisitos
          </span>
        </div>
      </div>

      <div className="requirements-table-wrapper">
        <table className="requirements-table">
          <thead>
            <tr>
              <th 
                className={`sortable ${sortBy === 'code' ? 'active' : ''}`}
                onClick={() => handleSort('code')}
              >
                Código
                {sortBy === 'code' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th>Título</th>
              <th>Descrição</th>
              <th 
                className={`sortable ${sortBy === 'priority' ? 'active' : ''}`}
                onClick={() => handleSort('priority')}
              >
                Prioridade
                {sortBy === 'priority' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th>Categoria</th>
              <th 
                className={`sortable ${sortBy === 'complexity' ? 'active' : ''}`}
                onClick={() => handleSort('complexity')}
              >
                Complexidade
                {sortBy === 'complexity' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th>Critérios/Métricas</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedRequirements.map((requirement) => (
              <tr key={requirement.id} className="requirement-row">
                <td className="requirement-code">
                  <span className="code-badge">{requirement.code}</span>
                </td>
                
                <td className="requirement-title">
                  <div className="title-container">
                    <span className="title-text">{requirement.title}</span>
                    {'source' in requirement && (
                      <span className="source-indicator" title={`Fonte: ${requirement.source}`}>
                        📄 {requirement.source}
                      </span>
                    )}
                  </div>
                </td>
                
                <td className="requirement-description">
                  <div className="description-text">
                    {requirement.description}
                  </div>
                  {'acceptanceCriteria' in requirement && requirement.acceptanceCriteria.length > 0 && (
                    <details className="acceptance-criteria">
                      <summary>Critérios de Aceitação ({requirement.acceptanceCriteria.length})</summary>
                      <ul>
                        {requirement.acceptanceCriteria.map((criteria, index) => (
                          <li key={index}>{criteria}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </td>
                
                <td className="requirement-priority">
                  <span className={`priority-badge ${getPriorityBadgeClass(requirement.priority)}`}>
                    {getPriorityText(requirement.priority)}
                  </span>
                </td>
                
                <td className="requirement-category">
                  {isNonFunctional(requirement) ? (
                    <span className="category-badge nfr">
                      {getCategoryIcon(requirement.category)} {requirement.category}
                    </span>
                  ) : (
                    <span className="category-badge fr">
                      📋 {'category' in requirement ? requirement.category : 'Funcional'}
                    </span>
                  )}
                </td>
                
                <td className="requirement-complexity">
                  {'complexity' in requirement ? (
                    <span className={`complexity-badge ${getComplexityBadgeClass(requirement.complexity)}`}>
                      {getComplexityText(requirement.complexity)}
                    </span>
                  ) : (
                    <span className="na-indicator">-</span>
                  )}
                </td>
                
                <td className="requirement-metrics">
                  {isNonFunctional(requirement) ? (
                    <div className="metrics-info">
                      <div className="metric-item">
                        <strong>Métrica:</strong> {requirement.metric}
                      </div>
                      <div className="metric-item">
                        <strong>Valor-alvo:</strong> {requirement.targetValue}
                      </div>
                      <div className="metric-item">
                        <strong>Método:</strong> {requirement.testMethod}
                      </div>
                    </div>
                  ) : (
                    'dependencies' in requirement && requirement.dependencies.length > 0 && (
                      <div className="dependencies-info">
                        <strong>Dependências:</strong>
                        <div className="dependency-list">
                          {requirement.dependencies.map(dep => (
                            <span key={dep} className="dependency-tag">{dep}</span>
                          ))}
                        </div>
                      </div>
                    )
                  )}
                </td>
                
                <td className="requirement-actions">
                  <div className="action-buttons">
                    {onEdit && (
                      <button 
                        className="action-btn edit-btn"
                        onClick={() => onEdit(requirement)}
                        title="Editar requisito"
                      >
                        ✏️
                      </button>
                    )}
                    <button 
                      className="action-btn view-btn"
                      title="Ver detalhes"
                    >
                      👁️
                    </button>
                    {onDelete && (
                      <button 
                        className="action-btn delete-btn"
                        onClick={() => onDelete(requirement.id)}
                        title="Excluir requisito"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredAndSortedRequirements.length === 0 && (
          <div className="empty-requirements">
            <div className="empty-icon">📋</div>
            <h4>Nenhum requisito encontrado</h4>
            <p>
              {searchTerm || filterPriority !== 'all' 
                ? 'Tente ajustar os filtros de busca'
                : 'Ainda não há requisitos definidos para este projeto'
              }
            </p>
          </div>
        )}
      </div>
      
      <div className="requirements-summary">
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-number">{requirements.filter(r => r.priority === 'must_have').length}</span>
            <span className="stat-label">Obrigatórios</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{requirements.filter(r => r.priority === 'should_have').length}</span>
            <span className="stat-label">Importantes</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{requirements.filter(r => r.priority === 'could_have').length}</span>
            <span className="stat-label">Desejáveis</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{requirements.filter(r => isNonFunctional(r)).length}</span>
            <span className="stat-label">Não-Funcionais</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RequirementsTable;