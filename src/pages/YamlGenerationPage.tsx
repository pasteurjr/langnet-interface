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

  return (
    <div className="yaml-generation-page">
      <div className="yaml-generation-header">
        <h1>📦 Geração de YAML de Agentes e Tarefas</h1>
        <p>Gere agents.yaml e tasks.yaml a partir de documentos de especificação</p>

        <div className="yaml-tabs">
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
      </div>

      <div className="yaml-tab-content">
        {activeTab === 'agents' && <AgentsYamlTab projectId={projectId} />}
        {activeTab === 'tasks' && <TasksYamlTab projectId={projectId} />}
      </div>
    </div>
  );
};

export default YamlGenerationPage;
