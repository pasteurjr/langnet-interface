// src/components/settings/NotificationSettings.tsx
import React, { useState } from 'react';
import { 
  Bell, 
  Mail, 
  MessageSquare, 
  Slack,
  Webhook,
  Settings,
  CheckCircle,
  XCircle,
  Plus,
  Edit3,
  Trash2,
  TestTube
} from 'lucide-react';
import { NotificationSettings as NotificationSettingsType, NotificationChannel } from '../../types/settings';
import './settings.css';

interface NotificationSettingsProps {
  settings?: NotificationSettingsType;
  onUpdate?: (updates: Partial<NotificationSettingsType>) => void;
}

export const NotificationSettings: React.FC<NotificationSettingsProps> = ({
  settings,
  onUpdate
}) => {
  // Mock data se não fornecido
  const [localSettings, setLocalSettings] = useState<NotificationSettingsType>(settings || {
    id: 'notif-1',
    userId: undefined,
    isGlobal: true,
    channels: [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
    preferences: {
      projectUpdates: true,
      deployments: true,
      errors: true,
      systemAlerts: true,
      weeklyReports: true
    },
    emailSettings: {
      address: 'admin@langnet.com',
      verified: true
    },
    slackSettings: {
      workspace: 'langnet-team',
      channel: '#alerts',
      webhookUrl: 'https://hooks.slack.com/***'
    },
    webhookSettings: {
      url: 'https://api.example.com/webhook',
      secret: 'webhook_secret_***',
      events: ['deployment.completed', 'system.alert']
    }
  });

  const [testingChannel, setTestingChannel] = useState<string | null>(null);

  const handleSettingChange = (key: keyof NotificationSettingsType, value: any) => {
    const updatedSettings = { ...localSettings, [key]: value };
    setLocalSettings(updatedSettings);
    onUpdate?.(updatedSettings);
  };

  const handlePreferenceChange = (key: keyof NotificationSettingsType['preferences'], value: boolean) => {
    const updatedPreferences = { ...localSettings.preferences, [key]: value };
    handleSettingChange('preferences', updatedPreferences);
  };

  const handleChannelToggle = (channel: NotificationChannel) => {
    const currentChannels = localSettings.channels;
    const updatedChannels = currentChannels.includes(channel)
      ? currentChannels.filter(c => c !== channel)
      : [...currentChannels, channel];
    handleSettingChange('channels', updatedChannels);
  };

  const testNotification = async (channel: string) => {
    setTestingChannel(channel);
    // Simular teste de notificação
    setTimeout(() => {
      setTestingChannel(null);
      console.log(`Testing notification for channel: ${channel}`);
    }, 2000);
  };

  const getChannelIcon = (channel: NotificationChannel) => {
    switch (channel) {
      case NotificationChannel.EMAIL: return <Mail className="w-4 h-4" />;
      case NotificationChannel.SLACK: return <Slack className="w-4 h-4" />;
      case NotificationChannel.WEBHOOK: return <Webhook className="w-4 h-4" />;
      case NotificationChannel.IN_APP: return <Bell className="w-4 h-4" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  const getChannelLabel = (channel: NotificationChannel) => {
    switch (channel) {
      case NotificationChannel.EMAIL: return 'Email';
      case NotificationChannel.SLACK: return 'Slack';
      case NotificationChannel.WEBHOOK: return 'Webhook';
      case NotificationChannel.IN_APP: return 'In-App';
      default: return channel;
    }
  };

  return (
    <div className="settings-section">
      <div className="section-header">
        <h3>Configurações de Notificações</h3>
      </div>

      <div className="settings-cards">
        {/* Canais de Notificação */}
        <div className="settings-card">
          <div className="card-header">
            <Bell className="w-5 h-5" />
            <h4>Canais Ativos</h4>
          </div>
          <div className="card-content">
            <div className="channels-grid">
              {Object.values(NotificationChannel).map(channel => (
                <div key={channel} className="channel-item">
                  <div className="channel-info">
                    {getChannelIcon(channel)}
                    <span className="channel-name">{getChannelLabel(channel)}</span>
                  </div>
                  <div className="channel-controls">
                    <div className="toggle-switch">
                      <input
                        type="checkbox"
                        id={`channel-${channel}`}
                        checked={localSettings.channels.includes(channel)}
                        onChange={() => handleChannelToggle(channel)}
                      />
                      <label htmlFor={`channel-${channel}`}>
                        {localSettings.channels.includes(channel) ? 'Ativo' : 'Inativo'}
                      </label>
                    </div>
                    {localSettings.channels.includes(channel) && (
                      <button
                        className="btn btn-sm btn-outline"
                        onClick={() => testNotification(channel)}
                        disabled={testingChannel === channel}
                      >
                        {testingChannel === channel ? (
                          <Settings className="w-3 h-3 animate-spin" />
                        ) : (
                          <TestTube className="w-3 h-3" />
                        )}
                        Testar
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Preferências de Notificação */}
        <div className="settings-card">
          <div className="card-header">
            <Settings className="w-5 h-5" />
            <h4>Preferências</h4>
          </div>
          <div className="card-content">
            <div className="preferences-grid">
              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={localSettings.preferences.projectUpdates}
                    onChange={(e) => handlePreferenceChange('projectUpdates', e.target.checked)}
                  />
                  Atualizações de projetos
                </label>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={localSettings.preferences.deployments}
                    onChange={(e) => handlePreferenceChange('deployments', e.target.checked)}
                  />
                  Deployments e releases
                </label>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={localSettings.preferences.errors}
                    onChange={(e) => handlePreferenceChange('errors', e.target.checked)}
                  />
                  Erros e problemas críticos
                </label>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={localSettings.preferences.systemAlerts}
                    onChange={(e) => handlePreferenceChange('systemAlerts', e.target.checked)}
                  />
                  Alertas do sistema
                </label>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={localSettings.preferences.weeklyReports}
                    onChange={(e) => handlePreferenceChange('weeklyReports', e.target.checked)}
                  />
                  Relatórios semanais
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Configurações de Email */}
        {localSettings.channels.includes(NotificationChannel.EMAIL) && (
          <div className="settings-card">
            <div className="card-header">
              <Mail className="w-5 h-5" />
              <h4>Configurações de Email</h4>
            </div>
            <div className="card-content">
              <div className="form-group">
                <label>Endereço de email</label>
                <input
                  type="email"
                  value={localSettings.emailSettings?.address || ''}
                  onChange={(e) => handleSettingChange('emailSettings', {
                    ...localSettings.emailSettings,
                    address: e.target.value
                  })}
                  placeholder="email@example.com"
                />
              </div>
              <div className="email-status">
                <span className="status-label">Status:</span>
                <div className="status-indicator">
                  {localSettings.emailSettings?.verified ? (
                    <>
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-green-600">Verificado</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-4 h-4 text-red-500" />
                      <span className="text-red-600">Não verificado</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Configurações do Slack */}
        {localSettings.channels.includes(NotificationChannel.SLACK) && (
          <div className="settings-card">
            <div className="card-header">
              <Slack className="w-5 h-5" />
              <h4>Configurações do Slack</h4>
            </div>
            <div className="card-content">
              <div className="form-group">
                <label>Workspace</label>
                <input
                  type="text"
                  value={localSettings.slackSettings?.workspace || ''}
                  onChange={(e) => handleSettingChange('slackSettings', {
                    ...localSettings.slackSettings,
                    workspace: e.target.value
                  })}
                  placeholder="meu-workspace"
                />
              </div>
              <div className="form-group">
                <label>Canal padrão</label>
                <input
                  type="text"
                  value={localSettings.slackSettings?.channel || ''}
                  onChange={(e) => handleSettingChange('slackSettings', {
                    ...localSettings.slackSettings,
                    channel: e.target.value
                  })}
                  placeholder="#alertas"
                />
              </div>
              <div className="form-group">
                <label>Webhook URL</label>
                <input
                  type="url"
                  value={localSettings.slackSettings?.webhookUrl || ''}
                  onChange={(e) => handleSettingChange('slackSettings', {
                    ...localSettings.slackSettings,
                    webhookUrl: e.target.value
                  })}
                  placeholder="https://hooks.slack.com/..."
                />
              </div>
            </div>
          </div>
        )}

        {/* Configurações de Webhook */}
        {localSettings.channels.includes(NotificationChannel.WEBHOOK) && (
          <div className="settings-card">
            <div className="card-header">
              <Webhook className="w-5 h-5" />
              <h4>Configurações de Webhook</h4>
            </div>
            <div className="card-content">
              <div className="form-group">
                <label>URL do Webhook</label>
                <input
                  type="url"
                  value={localSettings.webhookSettings?.url || ''}
                  onChange={(e) => handleSettingChange('webhookSettings', {
                    ...localSettings.webhookSettings,
                    url: e.target.value
                  })}
                  placeholder="https://api.example.com/webhook"
                />
              </div>
              <div className="form-group">
                <label>Secret</label>
                <input
                  type="password"
                  value={localSettings.webhookSettings?.secret || ''}
                  onChange={(e) => handleSettingChange('webhookSettings', {
                    ...localSettings.webhookSettings,
                    secret: e.target.value
                  })}
                  placeholder="webhook_secret"
                />
              </div>
              <div className="form-group">
                <label>Eventos</label>
                <div className="events-list">
                  {['project.created', 'project.updated', 'deployment.started', 'deployment.completed', 'deployment.failed', 'system.alert', 'error.critical'].map(event => (
                    <div key={event} className="checkbox-group">
                      <label>
                        <input
                          type="checkbox"
                          checked={localSettings.webhookSettings?.events.includes(event) || false}
                          onChange={(e) => {
                            const currentEvents = localSettings.webhookSettings?.events || [];
                            const updatedEvents = e.target.checked
                              ? [...currentEvents, event]
                              : currentEvents.filter(e => e !== event);
                            handleSettingChange('webhookSettings', {
                              ...localSettings.webhookSettings,
                              events: updatedEvents
                            });
                          }}
                        />
                        {event}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Configurações Globais */}
      <div className="settings-card">
        <div className="card-header">
          <Settings className="w-5 h-5" />
          <h4>Configurações Globais</h4>
        </div>
        <div className="card-content">
          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={localSettings.isGlobal}
                onChange={(e) => handleSettingChange('isGlobal', e.target.checked)}
              />
              Aplicar para todos os usuários
            </label>
          </div>
          <p className="help-text">
            Quando habilitado, essas configurações serão aplicadas como padrão para todos os usuários do sistema.
          </p>
        </div>
      </div>
    </div>
  );
};