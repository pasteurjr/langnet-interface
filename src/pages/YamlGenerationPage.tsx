/* src/pages/YamlGenerationPage.tsx */
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import './YamlGenerationPage.css';
import AgentsYamlTab from './tabs/AgentsYamlTab';
import TasksYamlTab from './tabs/TasksYamlTab';

type TabType = 'agents' | 'tasks';

const YamlGenerationPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('agents');
  const { projectId } = useParams<{ projectId: string }>();

  // Alternador de abas (agents.yaml / tasks.yaml) injetado no shell de cada aba,
  // logo acima das opções de configuração, para preservar a navegação entre os dois artefatos.
  const tabSwitcher = (
    <div className="yaml-tabs" style={{ marginBottom: '12px' }}>
      <button
        className={`tab-button ${activeTab === 'agents' ? 'active' : ''}`}
        onClick={() => setActiveTab('agents')}
      >
        🤖 Agents YAML
      </button>
      <button
        className={`tab-button ${activeTab === 'tasks' ? 'active' : ''}`}
        onClick={() => setActiveTab('tasks')}
      >
        📋 Tasks YAML
      </button>
    </div>
  );

  return activeTab === 'agents' ? (
    <AgentsYamlTab projectId={projectId} tabSwitcher={tabSwitcher} />
  ) : (
    <TasksYamlTab projectId={projectId} tabSwitcher={tabSwitcher} />
  );
};

export default YamlGenerationPage;
