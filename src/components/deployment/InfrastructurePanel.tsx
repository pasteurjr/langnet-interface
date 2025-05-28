import React from 'react';
import { Database, Server, HardDrive, Wifi, DollarSign, Activity, AlertCircle, CheckCircle } from 'lucide-react';
import { DeploymentEnvironment, InfrastructureResource } from '../../types/deployment';
import './deployment.css';

interface InfrastructurePanelProps {
  environment: DeploymentEnvironment;
}

export const InfrastructurePanel: React.FC<InfrastructurePanelProps> = ({
  environment
}) => {
  // Mock resources - seria obtido via API
  const resources: InfrastructureResource[] = [
    {
      id: 'lb-1',
      type: 'loadbalancer',
      name: 'Application Load Balancer',
      status: 'active',
      provider: environment.config.cloudProvider!,
      region: environment.config.region,
      configuration: {
        scheme: 'internet-facing',
        listeners: 2,
        targets: 3
      },
      cost: 18.50,
      createdAt: '2024-01-15T10:00:00Z'
    },
    {
      id: 'db-1',
      type: 'database',
      name: 'PostgreSQL Database',
      status: 'active',
      provider: environment.config.cloudProvider!,
      region: environment.config.region,
      configuration: {
        engine: 'postgresql',
        version: '14.9',
        instanceClass: 'db.t3.micro',
        storage: '20GB'
      },
      cost: 15.30,
      createdAt: '2024-01-15T10:00:00Z'
    },
    {
      id: 'cache-1',
      type: 'cache',
      name: 'Redis Cache',
      status: 'active',
      provider: environment.config.cloudProvider!,
      region: environment.config.region,
      configuration: {
        engine: 'redis',
        version: '7.0',
        nodeType: 'cache.t3.micro',
        nodes: 1
      },
      cost: 12.20,
      createdAt: '2024-01-15T10:00:00Z'
    },
    {
      id: 'storage-1',
      type: 'storage',
      name: 'File Storage',
      status: 'active',
      provider: environment.config.cloudProvider!,
      region: environment.config.region,
      configuration: {
        type: 'S3',
        storageClass: 'Standard',
        encryption: 'AES-256'
      },
      cost: 8.75,
      createdAt: '2024-01-15T10:00:00Z'
    },
    {
      id: 'network-1',
      type: 'network',
      name: 'VPC Network',
      status: 'active',
      provider: environment.config.cloudProvider!,
      region: environment.config.region,
      configuration: {
        cidr: '10.0.0.0/16',
        subnets: 4,
        natGateways: 2
      },
      cost: 45.00,
      createdAt: '2024-01-15T10:00:00Z'
    }
  ];

  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'loadbalancer': return <Wifi size={20} />;
      case 'database': return <Database size={20} />;
      case 'cache': return <HardDrive size={20} />;
      case 'storage': return <Server size={20} />;
      case 'network': return <Activity size={20} />;
      default: return <Server size={20} />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle size={16} color="#16a34a" />;
      case 'inactive': return <AlertCircle size={16} color="#6b7280" />;
      case 'error': return <AlertCircle size={16} color="#dc2626" />;
      default: return <AlertCircle size={16} color="#6b7280" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#16a34a';
      case 'inactive': return '#6b7280';
      case 'error': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const getResourceTypeLabel = (type: string) => {
    switch (type) {
      case 'loadbalancer': return 'Load Balancer';
      case 'database': return 'Database';
      case 'cache': return 'Cache';
      case 'storage': return 'Storage';
      case 'network': return 'Network';
      default: return 'Resource';
    }
  };

  const formatCost = (cost: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(cost);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const totalCost = resources.reduce((sum, resource) => sum + resource.cost, 0);

  return (
    <div className="infrastructure-panel">
      <div className="infrastructure-summary">
        <div className="summary-cards">
          <div className="summary-card">
            <div className="summary-icon">
              <Server size={24} />
            </div>
            <div className="summary-content">
              <div className="summary-value">{resources.length}</div>
              <div className="summary-label">Recursos Ativos</div>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">
              <DollarSign size={24} />
            </div>
            <div className="summary-content">
              <div className="summary-value">{formatCost(totalCost)}</div>
              <div className="summary-label">Custo Mensal</div>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">
              <CheckCircle size={24} />
            </div>
            <div className="summary-content">
              <div className="summary-value">
                {resources.filter(r => r.status === 'active').length}
              </div>
              <div className="summary-label">Funcionando</div>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">
              <Activity size={24} />
            </div>
            <div className="summary-content">
              <div className="summary-value">{environment.config.region}</div>
              <div className="summary-label">Região</div>
            </div>
          </div>
        </div>
      </div>

      <div className="resources-section">
        <div className="section-header">
          <h3>Recursos de Infraestrutura</h3>
          <div className="resource-types">
            {['all', 'loadbalancer', 'database', 'cache', 'storage', 'network'].map(type => (
              <button
                key={type}
                className={`filter-btn ${type === 'all' ? 'active' : ''}`}
              >
                {type === 'all' ? 'Todos' : getResourceTypeLabel(type)}
              </button>
            ))}
          </div>
        </div>

        <div className="resources-grid">
          {resources.map(resource => (
            <div key={resource.id} className="resource-card">
              <div className="resource-header">
                <div className="resource-icon">
                  {getResourceIcon(resource.type)}
                </div>
                <div className="resource-info">
                  <div className="resource-name">{resource.name}</div>
                  <div className="resource-type">{getResourceTypeLabel(resource.type)}</div>
                </div>
                <div 
                  className="resource-status"
                  style={{ color: getStatusColor(resource.status) }}
                >
                  {getStatusIcon(resource.status)}
                </div>
              </div>

              <div className="resource-details">
                <div className="resource-meta">
                  <div className="meta-item">
                    <span className="meta-label">Provider:</span>
                    <span className="meta-value">{resource.provider.toUpperCase()}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Região:</span>
                    <span className="meta-value">{resource.region}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Criado:</span>
                    <span className="meta-value">{formatDate(resource.createdAt)}</span>
                  </div>
                </div>

                <div className="resource-configuration">
                  <h5>Configuração</h5>
                  <div className="config-list">
                    {Object.entries(resource.configuration).map(([key, value]) => (
                      <div key={key} className="config-item">
                        <span className="config-key">{key}:</span>
                        <span className="config-value">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="resource-cost">
                  <div className="cost-info">
                    <DollarSign size={16} />
                    <span className="cost-label">Custo Mensal:</span>
                    <span className="cost-value">{formatCost(resource.cost)}</span>
                  </div>
                </div>
              </div>

              <div className="resource-actions">
                <button className="resource-action-btn">
                  Ver Detalhes
                </button>
                <button className="resource-action-btn">
                  Configurar
                </button>
                <button className="resource-action-btn danger">
                  Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="cost-breakdown">
        <h3>Breakdown de Custos</h3>
        <div className="cost-chart">
          {resources.map(resource => {
            const percentage = (resource.cost / totalCost) * 100;
            return (
              <div key={resource.id} className="cost-item">
                <div className="cost-bar">
                  <div 
                    className="cost-fill"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <div className="cost-details">
                  <span className="cost-name">{resource.name}</span>
                  <span className="cost-amount">{formatCost(resource.cost)}</span>
                  <span className="cost-percentage">{percentage.toFixed(1)}%</span>
                </div>
              </div>
            );
          })}
        </div>
        <div className="cost-total">
          <strong>Total Mensal: {formatCost(totalCost)}</strong>
        </div>
      </div>

      <div className="infrastructure-actions">
        <button className="btn btn-primary">
          Adicionar Recurso
        </button>
        <button className="btn btn-secondary">
          Otimizar Custos
        </button>
        <button className="btn btn-secondary">
          Exportar Configuração
        </button>
      </div>
    </div>
  );
};