
// src/hooks/useNavigation.ts (NOVO ARQUIVO)
import { useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MenuItem } from '../types';
import { ProjectContext } from '../types/navigation';

const GLOBAL_MENU_ITEMS: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: '📊',
    path: '/'
  },
  {
    id: 'projects',
    label: 'Projetos',
    icon: '📁',
    path: '/projects'
  },
  {
    id: 'settings',
    label: 'Configurações',
    icon: '⚙️',
    path: '/settings'
  },
  {
    id: 'help',
    label: 'Ajuda',
    icon: '❓',
    path: '/help'
  }
];

const PROJECT_MENU_ITEMS: MenuItem[] = [
  {
    id: 'documents',
    label: 'Documentos',
    icon: '📄',
    path: '/documents'
  },
  {
    id: 'spec',
    label: 'Especificação',
    icon: '📝',
    path: '/spec'
  },
  {
    id: 'agents',
    label: 'Agentes',
    icon: '🤖',
    path: '/agents'
  },
  {
    id: 'tasks',
    label: 'Tarefas',
    icon: '📋',
    path: '/tasks'
  },
  {
    id: 'yaml',
    label: 'YAML',
    icon: '📄',
    path: '/yaml'
  },
  {
    id: 'petri-net',
    label: 'Rede de Petri',
    icon: '🔗',
    path: '/petri-net'
  },
  {
    id: 'code',
    label: 'Código',
    icon: '💻',
    path: '/code'
  },
  {
    id: 'deploy',
    label: 'Deploy',
    icon: '🚀',
    path: '/deploy'
  },
  {
    id: 'monitoring',
    label: 'Monitoramento',
    icon: '📊',
    path: '/monitoring'
  }
];

export const useNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [projectContext, setProjectContext] = useState<ProjectContext>({
    projectId: '',
    projectName: '',
    isInProject: false,
  });

  const enterProjectContext = useCallback((projectId: string, projectName: string) => {
    setProjectContext({
      projectId,
      projectName,
      isInProject: true,
    });
    // Não navegar automaticamente - deixar que o usuário clique na sidebar
  }, []);

  const exitProjectContext = useCallback(() => {
    setProjectContext({
      projectId: '',
      projectName: '',
      isInProject: false,
    });
    // Voltar para o dashboard principal
    navigate('/');
  }, [navigate]);

  const getMenuItems = useCallback((): MenuItem[] => {
    if (projectContext.isInProject) {
      return PROJECT_MENU_ITEMS.map(item => ({
        ...item,
        path: `/project/${projectContext.projectId}${item.path}`,
      }));
    }
    return GLOBAL_MENU_ITEMS;
  }, [projectContext]);

  return {
    projectContext,
    menuItems: getMenuItems(),
    enterProjectContext,
    exitProjectContext,
  };
};