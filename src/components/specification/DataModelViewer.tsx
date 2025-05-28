/* src/components/specification/DataModelViewer.tsx */
import React from 'react';
import { DataEntity } from '../../types/';

interface DataModelViewerProps {
  entities: DataEntity[];
}

const DataModelViewer: React.FC<DataModelViewerProps> = ({ entities }) => {
  return (
    <div className="data-model-viewer">
      <div className="entities-grid">
        {entities.map(entity => (
          <div key={entity.id} className="entity-card">
            <div className="entity-header">
              <h4 className="entity-name">🗃️ {entity.name}</h4>
              <p className="entity-description">{entity.description}</p>
            </div>
            
            <div className="entity-attributes">
              <h5>Atributos:</h5>
              <div className="attributes-list">
                {entity.attributes.map(attr => (
                  <div key={attr.id} className={`attribute-item ${attr.isPrimaryKey ? 'primary-key' : ''} ${attr.isForeignKey ? 'foreign-key' : ''}`}>
                    <span className="attribute-name">{attr.name}</span>
                    <span className="attribute-type">{attr.type}</span>
                    <span className="attribute-flags">
                      {attr.isPrimaryKey && <span className="flag pk">PK</span>}
                      {attr.isForeignKey && <span className="flag fk">FK</span>}
                      {attr.isRequired && <span className="flag required">*</span>}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            {entity.relationships.length > 0 && (
              <div className="entity-relationships">
                <h5>Relacionamentos:</h5>
                <div className="relationships-list">
                  {entity.relationships.map(rel => (
                    <div key={rel.id} className="relationship-item">
                      <span className="relationship-type">{rel.type}</span>
                      <span className="relationship-target">→ {rel.targetEntityId}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {entity.businessRules.length > 0 && (
              <div className="entity-rules">
                <h5>Regras de Negócio:</h5>
                <ul className="rules-list">
                  {entity.businessRules.map((rule, index) => (
                    <li key={index} className="rule-item">{rule}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {entities.length === 0 && (
        <div className="empty-data-model">
          <div className="empty-icon">🗃️</div>
          <h4>Nenhuma entidade definida</h4>
          <p>O modelo de dados será gerado automaticamente a partir dos requisitos</p>
        </div>
      )}
    </div>
  );
};

export { DataModelViewer }; 