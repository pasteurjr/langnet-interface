/**
 * useProjectLoader Hook - ETAPA 1 Motor Genérico  
 * Hook para carregar projetos do backend_generic:8000
 * Sistema genérico para qualquer projeto
 */

import { useState, useCallback } from 'react';

export const useProjectLoader = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);

  const BACKEND_URL = 'http://localhost:8000';

  // Carrega projeto por ID do backend_generic
  const loadProject = useCallback(async (projectId = null) => {
    try {
      setLoading(true);
      setError(null);

      // Se não for fornecido ID, usa o TropicalSales padrão
      const targetId = projectId || '9a2c56de-ada5-4c49-b4a5-29bc237a590a';

      console.log('🔄 Carregando projeto do backend_generic:', targetId);

      const response = await fetch(`${BACKEND_URL}/api/projects/${targetId}`);
      
      if (!response.ok) {
        throw new Error(`Erro carregando projeto: ${response.status}`);
      }

      const data = await response.json();
      const project = data.project;

      if (!project) {
        throw new Error('Projeto não encontrado na resposta da API');
      }

      // Estrutura genérica de configuração do projeto
      const projectConfig = {
        // Dados básicos
        id: project.id,
        name: project.name,
        description: project.description,
        
        // Petri Net data
        petri_net_data: project.petriNet,
        
        // Context schema (configurável por projeto)
        context_schema: {
          required_fields: ['project_id', 'initialized_timestamp'],
          optional_fields: ['user_id', 'session_id', 'execution_id'],
          field_types: {
            project_id: 'string',
            initialized_timestamp: 'datetime',
            user_id: 'string', 
            session_id: 'string',
            execution_id: 'string'
          }
        },

        // Configuração de execução (configurável por projeto)
        execution_config: {
          adapter_type: 'TropicalSalesAdapter', // Detectado do projeto
          task_naming_pattern: '(.+)_task', // Pattern padrão
          websocket_config: {
            url: 'ws://localhost:6308', // WebSocket V8 com parser melhorado
            timeout: 30000,
            max_retries: 3
          }
        },

        // Metadados
        metadata: project.metadata || {},
        created_at: project.created_at,
        updated_at: project.updated_at
      };

      console.log('✅ Projeto carregado:', {
        id: projectConfig.id,
        name: projectConfig.name,
        places: projectConfig.petri_net_data?.lugares?.length || 0,
        adapter: projectConfig.execution_config.adapter_type
      });

      setCurrentProject(projectConfig);
      return projectConfig;

    } catch (err) {
      console.error('❌ Erro carregando projeto:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Lista todos os projetos disponíveis
  const listProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('📋 Listando projetos disponíveis...');

      const response = await fetch(`${BACKEND_URL}/api/projects`);
      
      if (!response.ok) {
        throw new Error(`Erro listando projetos: ${response.status}`);
      }

      const data = await response.json();
      const projects = data.projects || [];

      console.log(`✅ ${projects.length} projetos encontrados`);

      return projects.map(project => ({
        id: project.id,
        name: project.name,
        description: project.description,
        created_at: project.created_at,
        updated_at: project.updated_at
      }));

    } catch (err) {
      console.error('❌ Erro listando projetos:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Detecta adapter type baseado no projeto
  const detectAdapterType = useCallback((projectData) => {
    const projectName = projectData.name?.toLowerCase() || '';
    const description = projectData.description?.toLowerCase() || '';
    
    // Detectar adapter baseado em nome/descrição
    if (projectName.includes('tropical') || description.includes('tropical')) {
      return 'TropicalSalesAdapter';
    } else if (projectName.includes('valep') || description.includes('valep')) {
      return 'VALEP1Adapter';
    } else {
      return 'GenericAdapter';
    }
  }, []);

  // Extrai task naming pattern do projeto
  const extractTaskNamingPattern = useCallback((petriNetData) => {
    if (!petriNetData?.lugares) return '(.+)_task';

    // Analisa nomes dos Places para detectar pattern
    const placeNames = petriNetData.lugares
      .filter(place => place.agentId) // Só Places com agentId
      .map(place => place.nome);

    // Detecta patterns comuns
    if (placeNames.some(name => name.endsWith('_task'))) {
      return '(.+)_task';
    } else if (placeNames.some(name => name.startsWith('TASK_') && name.endsWith('_EXEC'))) {
      return 'TASK_(.+)_EXEC';
    } else {
      return null; // Nome direto
    }
  }, []);

  // Carrega projeto com configuração automática
  const loadProjectWithAutoConfig = useCallback(async (projectId = null) => {
    try {
      const project = await loadProject(projectId);
      
      // Auto-detecta configurações
      const adapterType = detectAdapterType(project);
      const taskPattern = extractTaskNamingPattern(project.petri_net_data);
      
      // Atualiza configuração
      project.execution_config.adapter_type = adapterType;
      project.execution_config.task_naming_pattern = taskPattern;

      console.log('🔧 Configuração automática aplicada:', {
        adapter: adapterType,
        pattern: taskPattern
      });

      return project;
    } catch (err) {
      throw err;
    }
  }, [loadProject, detectAdapterType, extractTaskNamingPattern]);

  return {
    // States
    loading,
    error,
    currentProject,
    
    // Methods
    loadProject,
    listProjects,
    loadProjectWithAutoConfig,
    detectAdapterType,
    extractTaskNamingPattern
  };
};