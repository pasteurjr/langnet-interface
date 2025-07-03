// src/pages/McpStateSyncPage.tsx
import React, { useState, useEffect } from 'react';
import './McpStateSyncPage.css';

// Types based on MCP requirements from docs
interface SyncState {
  id: string;
  entityType: 'project' | 'agent' | 'task' | 'document' | 'specification' | 'yaml';
  entityId: string;
  entityName: string;
  localVersion: string;
  remoteVersion: string;
  localTimestamp: string;
  remoteTimestamp: string;
  status: 'synced' | 'conflict' | 'local_newer' | 'remote_newer' | 'error';
  conflictType?: 'content' | 'metadata' | 'structure' | 'permissions';
  lastSyncAttempt?: string;
  syncDirection: 'local_to_remote' | 'remote_to_local' | 'bidirectional';
}

interface SyncConflict {
  id: string;
  entityId: string;
  entityName: string;
  entityType: string;
  conflictFields: ConflictField[];
  createdAt: string;
  resolvedAt?: string;
  resolution?: 'local_wins' | 'remote_wins' | 'manual_merge' | 'skip';
  resolvedBy?: string;
}

interface ConflictField {
  field: string;
  localValue: any;
  remoteValue: any;
  dataType: string;
  importance: 'low' | 'medium' | 'high' | 'critical';
}

interface SyncJob {
  id: string;
  type: 'full_sync' | 'incremental_sync' | 'conflict_resolution' | 'backup' | 'restore';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  startTime?: string;
  endTime?: string;
  entitiesTotal: number;
  entitiesProcessed: number;
  conflicts: number;
  errors: SyncError[];
  settings: SyncSettings;
}

interface SyncError {
  id: string;
  entityId: string;
  entityName: string;
  errorType: 'network' | 'permission' | 'validation' | 'conflict' | 'timeout';
  message: string;
  timestamp: string;
  retryCount: number;
  resolved: boolean;
}

interface SyncSettings {
  autoSync: boolean;
  syncInterval: number; // minutes
  conflictResolution: 'manual' | 'local_wins' | 'remote_wins' | 'newest_wins';
  batchSize: number;
  retryAttempts: number;
  enableBackup: boolean;
  syncFilters: {
    entityTypes: string[];
    projects: string[];
    agents: string[];
  };
}

interface ServerConnection {
  id: string;
  name: string;
  url: string;
  status: 'connected' | 'disconnected' | 'error' | 'connecting';
  lastPing: string;
  latency: number;
  version: string;
  capabilities: string[];
}

const McpStateSyncPage: React.FC = () => {
  const [syncStates, setSyncStates] = useState<SyncState[]>([]);
  const [conflicts, setConflicts] = useState<SyncConflict[]>([]);
  const [syncJobs, setSyncJobs] = useState<SyncJob[]>([]);
  const [servers, setServers] = useState<ServerConnection[]>([]);
  const [settings, setSettings] = useState<SyncSettings>({
    autoSync: true,
    syncInterval: 15,
    conflictResolution: 'manual',
    batchSize: 50,
    retryAttempts: 3,
    enableBackup: true,
    syncFilters: {
      entityTypes: ['project', 'agent', 'task'],
      projects: [],
      agents: []
    }
  });
  const [selectedTab, setSelectedTab] = useState<'overview' | 'conflicts' | 'jobs' | 'settings'>('overview');
  const [selectedConflict, setSelectedConflict] = useState<SyncConflict | null>(null);
  const [isManualSync, setIsManualSync] = useState(false);

  // Mock data generation - seguindo padrão das outras páginas
  useEffect(() => {
    const generateMockData = () => {
      // Mock Servers
      const mockServers: ServerConnection[] = [
        {
          id: 'server-1',
          name: 'Production MCP Server',
          url: 'https://mcp.langnet.com',
          status: 'connected',
          lastPing: new Date(Date.now() - 30000).toISOString(),
          latency: 45,
          version: '2.1.0',
          capabilities: ['state-sync', 'conflict-resolution', 'backup', 'versioning']
        },
        {
          id: 'server-2',
          name: 'Staging MCP Server',
          url: 'https://staging-mcp.langnet.com',
          status: 'disconnected',
          lastPing: new Date(Date.now() - 300000).toISOString(),
          latency: 120,
          version: '2.0.8',
          capabilities: ['state-sync', 'backup']
        }
      ];

      // Mock Sync States
      const mockStates: SyncState[] = [
        {
          id: 'sync-1',
          entityType: 'project',
          entityId: 'proj-123',
          entityName: 'Customer Support System',
          localVersion: '1.2.3',
          remoteVersion: '1.2.4',
          localTimestamp: new Date(Date.now() - 600000).toISOString(),
          remoteTimestamp: new Date(Date.now() - 300000).toISOString(),
          status: 'remote_newer',
          lastSyncAttempt: new Date(Date.now() - 120000).toISOString(),
          syncDirection: 'bidirectional'
        },
        {
          id: 'sync-2',
          entityType: 'agent',
          entityId: 'agent-456',
          entityName: 'Customer Service Agent',
          localVersion: '2.1.0',
          remoteVersion: '2.0.8',
          localTimestamp: new Date(Date.now() - 180000).toISOString(),
          remoteTimestamp: new Date(Date.now() - 900000).toISOString(),
          status: 'conflict',
          conflictType: 'content',
          lastSyncAttempt: new Date(Date.now() - 60000).toISOString(),
          syncDirection: 'bidirectional'
        },
        {
          id: 'sync-3',
          entityType: 'task',
          entityId: 'task-789',
          entityName: 'Process Customer Query',
          localVersion: '1.0.0',
          remoteVersion: '1.0.0',
          localTimestamp: new Date(Date.now() - 1200000).toISOString(),
          remoteTimestamp: new Date(Date.now() - 1200000).toISOString(),
          status: 'synced',
          lastSyncAttempt: new Date(Date.now() - 300000).toISOString(),
          syncDirection: 'bidirectional'
        }
      ];

      // Mock Conflicts
      const mockConflicts: SyncConflict[] = [
        {
          id: 'conflict-1',
          entityId: 'agent-456',
          entityName: 'Customer Service Agent',
          entityType: 'agent',
          createdAt: new Date(Date.now() - 3600000).toISOString(),
          conflictFields: [
            {
              field: 'goal',
              localValue: 'Provide excellent customer service with empathy and efficiency',
              remoteValue: 'Deliver outstanding customer support with quick response times',
              dataType: 'string',
              importance: 'high'
            },
            {
              field: 'tools',
              localValue: ['web_search', 'database_query', 'email_send'],
              remoteValue: ['web_search', 'database_query', 'slack_send'],
              dataType: 'array',
              importance: 'medium'
            }
          ]
        },
        {
          id: 'conflict-2',
          entityId: 'proj-123',
          entityName: 'Customer Support System',
          entityType: 'project',
          createdAt: new Date(Date.now() - 7200000).toISOString(),
          resolvedAt: new Date(Date.now() - 3600000).toISOString(),
          resolution: 'local_wins',
          resolvedBy: 'user@example.com',
          conflictFields: [
            {
              field: 'description',
              localValue: 'Advanced AI-powered customer support system',
              remoteValue: 'Customer support automation platform',
              dataType: 'string',
              importance: 'low'
            }
          ]
        }
      ];

      // Mock Sync Jobs
      const mockJobs: SyncJob[] = [
        {
          id: 'job-1',
          type: 'incremental_sync',
          status: 'running',
          progress: 65,
          startTime: new Date(Date.now() - 180000).toISOString(),
          entitiesTotal: 150,
          entitiesProcessed: 98,
          conflicts: 2,
          errors: [],
          settings: settings
        },
        {
          id: 'job-2',
          type: 'full_sync',
          status: 'completed',
          progress: 100,
          startTime: new Date(Date.now() - 3600000).toISOString(),
          endTime: new Date(Date.now() - 3000000).toISOString(),
          entitiesTotal: 500,
          entitiesProcessed: 500,
          conflicts: 5,
          errors: [
            {
              id: 'error-1',
              entityId: 'agent-999',
              entityName: 'Invalid Agent',
              errorType: 'validation',
              message: 'Agent configuration validation failed: missing required field "role"',
              timestamp: new Date(Date.now() - 3300000).toISOString(),
              retryCount: 3,
              resolved: false
            }
          ],
          settings: settings
        }
      ];

      setServers(mockServers);
      setSyncStates(mockStates);
      setConflicts(mockConflicts);
      setSyncJobs(mockJobs);
    };

    generateMockData();
  }, [settings]);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'synced':
      case 'connected':
      case 'completed': return '#10B981';
      case 'conflict':
      case 'remote_newer':
      case 'local_newer': return '#F59E0B';
      case 'error':
      case 'failed':
      case 'disconnected': return '#EF4444';
      case 'running':
      case 'connecting': return '#3B82F6';
      default: return '#6B7280';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'synced': return '✅';
      case 'conflict': return '⚠️';
      case 'remote_newer': return '↓';
      case 'local_newer': return '↑';
      case 'error': return '❌';
      case 'running': return '🔄';
      default: return '⏸️';
    }
  };

  const handleManualSync = (entityId?: string) => {
    setIsManualSync(true);
    
    // Simulate sync process
    setTimeout(() => {
      if (entityId) {
        setSyncStates(prev => prev.map(state => 
          state.entityId === entityId 
            ? { ...state, status: 'synced' as const, lastSyncAttempt: new Date().toISOString() }
            : state
        ));
      } else {
        setSyncStates(prev => prev.map(state => ({ 
          ...state, 
          status: Math.random() > 0.8 ? 'conflict' as const : 'synced' as const,
          lastSyncAttempt: new Date().toISOString()
        })));
      }
      setIsManualSync(false);
    }, 3000);
  };

  const handleConflictResolution = (conflictId: string, resolution: 'local_wins' | 'remote_wins' | 'manual_merge') => {
    setConflicts(prev => prev.map(conflict => 
      conflict.id === conflictId 
        ? { 
            ...conflict, 
            resolvedAt: new Date().toISOString(),
            resolution,
            resolvedBy: 'current_user@example.com'
          }
        : conflict
    ));
    
    // Update corresponding sync state
    const conflict = conflicts.find(c => c.id === conflictId);
    if (conflict) {
      setSyncStates(prev => prev.map(state => 
        state.entityId === conflict.entityId
          ? { ...state, status: 'synced' as const }
          : state
      ));
    }
    
    setSelectedConflict(null);
  };

  const unresolvedConflicts = conflicts.filter(c => !c.resolvedAt);
  const runningJobs = syncJobs.filter(job => job.status === 'running');
  const connectedServers = servers.filter(s => s.status === 'connected');

  return (
    <div className="mcp-state-sync-page">
      <div className="page-header">
        <div className="header-main">
          <h1>🔄 Sincronização de Estados MCP</h1>
          <p>Gerencie a sincronização de estados entre servidores MCP</p>
        </div>
        <div className="header-actions">
          <button
            className={`sync-btn ${isManualSync ? 'syncing' : ''}`}
            onClick={() => handleManualSync()}
            disabled={isManualSync}
          >
            {isManualSync ? '🔄 Sincronizando...' : '🔄 Sincronizar Tudo'}
          </button>
          <button className="btn btn-secondary">
            ⚙️ Configurações
          </button>
        </div>
      </div>

      <div className="page-content">
        {/* Status Overview */}
        <div className="status-overview">
          <div className="overview-cards">
            <div className="overview-card">
              <div className="card-icon">🌐</div>
              <div className="card-content">
                <div className="card-number">{connectedServers.length}/{servers.length}</div>
                <div className="card-label">Servidores Conectados</div>
              </div>
            </div>
            <div className="overview-card">
              <div className="card-icon">⚠️</div>
              <div className="card-content">
                <div className="card-number">{unresolvedConflicts.length}</div>
                <div className="card-label">Conflitos Pendentes</div>
              </div>
            </div>
            <div className="overview-card">
              <div className="card-icon">🔄</div>
              <div className="card-content">
                <div className="card-number">{runningJobs.length}</div>
                <div className="card-label">Jobs Executando</div>
              </div>
            </div>
            <div className="overview-card">
              <div className="card-icon">✅</div>
              <div className="card-content">
                <div className="card-number">
                  {syncStates.filter(s => s.status === 'synced').length}
                </div>
                <div className="card-label">Entidades Sincronizadas</div>
              </div>
            </div>
          </div>
        </div>

        {/* Server Status */}
        <div className="servers-section">
          <h2>🖥️ Status dos Servidores</h2>
          <div className="servers-list">
            {servers.map(server => (
              <div key={server.id} className="server-card">
                <div className="server-header">
                  <div className="server-name">{server.name}</div>
                  <div 
                    className="server-status"
                    style={{ backgroundColor: getStatusColor(server.status) }}
                  >
                    {server.status}
                  </div>
                </div>
                <div className="server-details">
                  <div className="server-url">{server.url}</div>
                  <div className="server-meta">
                    <span>v{server.version}</span>
                    <span>{server.latency}ms</span>
                    <span>{new Date(server.lastPing).toLocaleString('pt-BR')}</span>
                  </div>
                </div>
                <div className="server-capabilities">
                  {server.capabilities.map(cap => (
                    <span key={cap} className="capability-tag">{cap}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs-section">
          <div className="tabs-header">
            <button 
              className={`tab-btn ${selectedTab === 'overview' ? 'active' : ''}`}
              onClick={() => setSelectedTab('overview')}
            >
              📊 Visão Geral
            </button>
            <button 
              className={`tab-btn ${selectedTab === 'conflicts' ? 'active' : ''}`}
              onClick={() => setSelectedTab('conflicts')}
            >
              ⚠️ Conflitos ({unresolvedConflicts.length})
            </button>
            <button 
              className={`tab-btn ${selectedTab === 'jobs' ? 'active' : ''}`}
              onClick={() => setSelectedTab('jobs')}
            >
              🔄 Jobs de Sincronização
            </button>
            <button 
              className={`tab-btn ${selectedTab === 'settings' ? 'active' : ''}`}
              onClick={() => setSelectedTab('settings')}
            >
              ⚙️ Configurações
            </button>
          </div>

          <div className="tab-content">
            {selectedTab === 'overview' && (
              <div className="sync-states-section">
                <h3>Estado das Entidades</h3>
                <div className="states-table">
                  <div className="table-header">
                    <div>Entidade</div>
                    <div>Tipo</div>
                    <div>Status</div>
                    <div>Versão Local</div>
                    <div>Versão Remota</div>
                    <div>Última Sync</div>
                    <div>Ações</div>
                  </div>
                  {syncStates.map(state => (
                    <div key={state.id} className="table-row">
                      <div className="entity-info">
                        <div className="entity-name">{state.entityName}</div>
                        <div className="entity-id">{state.entityId}</div>
                      </div>
                      <div className="entity-type">{state.entityType}</div>
                      <div className="sync-status">
                        <span 
                          className="status-indicator"
                          style={{ backgroundColor: getStatusColor(state.status) }}
                        >
                          {getStatusIcon(state.status)} {state.status}
                        </span>
                      </div>
                      <div className="version">{state.localVersion}</div>
                      <div className="version">{state.remoteVersion}</div>
                      <div className="timestamp">
                        {state.lastSyncAttempt 
                          ? new Date(state.lastSyncAttempt).toLocaleString('pt-BR')
                          : 'Nunca'
                        }
                      </div>
                      <div className="actions">
                        <button 
                          className="action-btn"
                          onClick={() => handleManualSync(state.entityId)}
                          disabled={isManualSync}
                        >
                          🔄
                        </button>
                        {state.status === 'conflict' && (
                          <button 
                            className="action-btn conflict"
                            onClick={() => {
                              const conflict = conflicts.find(c => c.entityId === state.entityId);
                              setSelectedConflict(conflict || null);
                            }}
                          >
                            ⚠️
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedTab === 'conflicts' && (
              <div className="conflicts-section">
                <h3>Resolução de Conflitos</h3>
                {unresolvedConflicts.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">✅</div>
                    <h4>Nenhum conflito pendente</h4>
                    <p>Todas as entidades estão sincronizadas</p>
                  </div>
                ) : (
                  <div className="conflicts-list">
                    {unresolvedConflicts.map(conflict => (
                      <div key={conflict.id} className="conflict-card">
                        <div className="conflict-header">
                          <h4>{conflict.entityName}</h4>
                          <span className="conflict-type">{conflict.entityType}</span>
                        </div>
                        <div className="conflict-details">
                          <div>Criado: {new Date(conflict.createdAt).toLocaleString('pt-BR')}</div>
                          <div>{conflict.conflictFields.length} campo(s) em conflito</div>
                        </div>
                        <button 
                          className="btn btn-primary"
                          onClick={() => setSelectedConflict(conflict)}
                        >
                          Resolver Conflito
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {selectedTab === 'jobs' && (
              <div className="jobs-section">
                <h3>Histórico de Jobs</h3>
                <div className="jobs-list">
                  {syncJobs.map(job => (
                    <div key={job.id} className="job-card">
                      <div className="job-header">
                        <div className="job-type">{job.type}</div>
                        <div 
                          className="job-status"
                          style={{ backgroundColor: getStatusColor(job.status) }}
                        >
                          {job.status}
                        </div>
                      </div>
                      <div className="job-progress">
                        <div className="progress-bar">
                          <div 
                            className="progress-fill"
                            style={{ 
                              width: `${job.progress}%`,
                              backgroundColor: getStatusColor(job.status)
                            }}
                          />
                        </div>
                        <span className="progress-text">{job.progress}%</span>
                      </div>
                      <div className="job-details">
                        <div>Processados: {job.entitiesProcessed}/{job.entitiesTotal}</div>
                        <div>Conflitos: {job.conflicts}</div>
                        <div>Erros: {job.errors.length}</div>
                        {job.startTime && (
                          <div>Início: {new Date(job.startTime).toLocaleString('pt-BR')}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedTab === 'settings' && (
              <div className="settings-section">
                <h3>Configurações de Sincronização</h3>
                <div className="settings-form">
                  <div className="setting-group">
                    <label className="setting-label">
                      <input
                        type="checkbox"
                        checked={settings.autoSync}
                        onChange={(e) => setSettings(prev => ({ ...prev, autoSync: e.target.checked }))}
                      />
                      Sincronização automática
                    </label>
                  </div>
                  
                  <div className="setting-group">
                    <label>Intervalo de sincronização (minutos):</label>
                    <input
                      type="number"
                      value={settings.syncInterval}
                      onChange={(e) => setSettings(prev => ({ ...prev, syncInterval: Number(e.target.value) }))}
                      min="1"
                      max="1440"
                    />
                  </div>

                  <div className="setting-group">
                    <label>Resolução de conflitos:</label>
                    <select
                      value={settings.conflictResolution}
                      onChange={(e) => setSettings(prev => ({ ...prev, conflictResolution: e.target.value as any }))}
                    >
                      <option value="manual">Manual</option>
                      <option value="local_wins">Local sempre ganha</option>
                      <option value="remote_wins">Remoto sempre ganha</option>
                      <option value="newest_wins">Mais recente ganha</option>
                    </select>
                  </div>

                  <div className="setting-group">
                    <label>Tamanho do lote:</label>
                    <input
                      type="number"
                      value={settings.batchSize}
                      onChange={(e) => setSettings(prev => ({ ...prev, batchSize: Number(e.target.value) }))}
                      min="1"
                      max="1000"
                    />
                  </div>

                  <div className="setting-group">
                    <label className="setting-label">
                      <input
                        type="checkbox"
                        checked={settings.enableBackup}
                        onChange={(e) => setSettings(prev => ({ ...prev, enableBackup: e.target.checked }))}
                      />
                      Ativar backup antes da sincronização
                    </label>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Conflict Resolution Modal */}
      {selectedConflict && (
        <div className="modal-overlay">
          <div className="conflict-modal">
            <div className="modal-header">
              <h3>Resolver Conflito: {selectedConflict.entityName}</h3>
              <button 
                className="close-btn"
                onClick={() => setSelectedConflict(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-content">
              <div className="conflict-fields">
                {selectedConflict.conflictFields.map(field => (
                  <div key={field.field} className="conflict-field">
                    <h4>{field.field} <span className={`importance ${field.importance}`}>({field.importance})</span></h4>
                    <div className="field-comparison">
                      <div className="field-version">
                        <h5>💻 Versão Local:</h5>
                        <pre>{JSON.stringify(field.localValue, null, 2)}</pre>
                      </div>
                      <div className="field-version">
                        <h5>🌐 Versão Remota:</h5>
                        <pre>{JSON.stringify(field.remoteValue, null, 2)}</pre>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => handleConflictResolution(selectedConflict.id, 'local_wins')}
              >
                💻 Manter Local
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => handleConflictResolution(selectedConflict.id, 'remote_wins')}
              >
                🌐 Usar Remoto
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => handleConflictResolution(selectedConflict.id, 'manual_merge')}
              >
                🔧 Merge Manual
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default McpStateSyncPage;