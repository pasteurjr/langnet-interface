// src/contexts/NavigationContext.tsx (NOVO ARQUIVO)
import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MenuItem } from '../types';

import { 
  LayoutDashboard, 
  FolderOpen, 
  Users, 
  ListTodo, 
  FileText,
  FileCode,  // Adicione esta linha
  Settings 
} from 'lucide-react';

interface ProjectContext {
  projectId: string;
  projectName: string;
  isInProject: boolean;
}

interface NavigationContextType {
  projectContext: ProjectContext;
  menuItems: MenuItem[];
  enterProjectContext: (projectId: string, projectName: string) => void;
  exitProjectContext: () => void;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

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

interface NavigationProviderProps {
  children: ReactNode;
}

export const NavigationProvider: React.FC<NavigationProviderProps> = ({ children }) => {
  const navigate = useNavigate();
  
  const [projectContext, setProjectContext] = useState<ProjectContext>({
    projectId: '',
    projectName: '',
    isInProject: false,
  });

  const enterProjectContext = useCallback((projectId: string, projectName: string) => {
    console.log('Entrando no contexto do projeto:', projectId, projectName);
    setProjectContext({
      projectId,
      projectName,
      isInProject: true,
    });
  }, []);

  const exitProjectContext = useCallback(() => {
    console.log('Saindo do contexto do projeto');
    setProjectContext({
      projectId: '',
      projectName: '',
      isInProject: false,
    });
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

  const value: NavigationContextType = {
    projectContext,
    menuItems: getMenuItems(),
    enterProjectContext,
    exitProjectContext,
  };

  return (
    <NavigationContext.Provider value={value}>
      {children}
    </NavigationContext.Provider>
  );
};

export const useNavigation = (): NavigationContextType => {
  const context = useContext(NavigationContext);
  if (context === undefined) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
};