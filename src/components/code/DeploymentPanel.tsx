/* src/components/code/DeploymentPanel.tsx */
import React from 'react';
import { DeploymentInfo } from '../../types/codeGeneration';

interface DeploymentPanelProps {
  deploymentInfo: DeploymentInfo;
}

const DeploymentPanel: React.FC<DeploymentPanelProps> = ({ deploymentInfo }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'deployed': return '✅';
      case 'deploying': return '🔄';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  return (
    <div className="deployment-panel">
      <div className="deployment-status">
        <div className="deployment-header">
          <h4>🚀 Status do Deploy</h4>
          <span className="deployment-target">{deploymentInfo.target}</span>
        </div>
        
        <div className="deployment-info">
          <div className="deployment-item">
            <div className="deployment-label">Status</div>
            <div className="deployment-value">
              {getStatusIcon(deploymentInfo.status)} {deploymentInfo.status}
            </div>
          </div>
          
          {deploymentInfo.url && (
            <div className="deployment-item">
              <div className="deployment-label">URL</div>
              <div className="deployment-value">
                <a href={deploymentInfo.url} target="_blank" rel="noopener noreferrer">
                  {deploymentInfo.url}
                </a>
              </div>
            </div>
          )}
          
          <div className="deployment-item">
            <div className="deployment-label">Endpoints</div>
            <div className="deployment-value">
              {deploymentInfo.endpoints.join(', ')}
            </div>
          </div>
          
          {deploymentInfo.deployedAt && (
            <div className="deployment-item">
              <div className="deployment-label">Deployed em</div>
              <div className="deployment-value">
                {formatDate(deploymentInfo.deployedAt)}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="deployment-resources">
        <h5>📦 Recursos</h5>
        {deploymentInfo.resources.map((resource, index) => (
          <div key={index} className="resource-item">
            <div className="resource-info">
              <span className="resource-type">{resource.type}</span>
              <span className="resource-name">{resource.name}</span>
            </div>
            <div className="resource-status">{resource.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DeploymentPanel ;