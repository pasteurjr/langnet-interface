// src/contexts/NavigationContext.tsx (CORRIGIDO - Respeitando estrutura original)
import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { MenuItem } from "../types";

import {
  LayoutDashboard,
  FolderOpen,
  Users,
  ListTodo,
  FileText,
  FileCode,
  Settings,
} from "lucide-react";

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

const NavigationContext = createContext<NavigationContextType | undefined>(
  undefined
);

// ✅ MANTÉM GLOBAL_MENU_ITEMS EXATAMENTE COMO NO ORIGINAL
const GLOBAL_MENU_ITEMS: MenuItem[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: "📊",
    path: "/",
  },
  {
    id: "projects",
    label: "Projetos",
    icon: "📁",
    path: "/projects",
  },
  {
    id: "mcp",
    label: "MCP",
    icon: "🔗",
    path: "/mcp",
    children: [
      {
        id: "mcp-config",
        label: "Configuração Global",
        icon: "🌐",
        path: "/mcp/config", // ✅ McpGlobalConfigPage.tsx
      },
      {
        id: "mcp-services",
        label: "Descoberta de Serviços",
        icon: "🔍",
        path: "/mcp/services", // ✅ McpServiceDiscoveryPage.tsx
      },
      {
        id: "mcp-state-sync",
        label: "Sincronização de Estados",
        icon: "🔄",
        path: "/mcp/state-sync", // 🆕 A implementar
      },
    ],
  },
  {
    id: "settings",
    label: "Configurações",
    icon: "⚙️",
    path: "/settings",
  },
  {
    id: "help",
    label: "Ajuda",
    icon: "❓",
    path: "/help",
  },
];

// ✅ PROJECT_MENU_ITEMS - APENAS ADICIONA Interface Interativa
const PROJECT_MENU_ITEMS: MenuItem[] = [
  {
    id: "documents",
    label: "Documentos",
    icon: "📄",
    path: "/documents",
  },
  {
    id: "spec",
    label: "Especificação",
    icon: "📝",
    path: "/spec",
  },
  {
    id: "agents",
    label: "Agentes",
    icon: "🤖",
    path: "/agents",
  },
  {
    id: "tasks",
    label: "Tarefas",
    icon: "📋",
    path: "/tasks",
  },
  {
    id: "yaml",
    label: "YAML",
    icon: "📄",
    path: "/yaml",
  },
  {
    id: "petri-net",
    label: "Rede de Petri",
    icon: "🔗",
    path: "/petri-net",
  },
  {
    id: "code",
    label: "Código",
    icon: "💻",
    path: "/code",
  },
  {
    id: "mcp-project",
    label: "MCP",
    icon: "🔌",
    path: "/mcp",
    children: [
      {
        id: "mcp-project-integration",
        label: "Integração",
        icon: "🔗",
        path: "/mcp", // ✅ McpProjectIntegrationPage.tsx
      },
      {
        id: "mcp-project-sync",
        label: "Sincronização",
        icon: "🔄",
        path: "/mcp/sync", // 🆕 A implementar
      },
      {
        id: "mcp-project-services",
        label: "Serviços",
        icon: "🛠️",
        path: "/mcp/services", // 🆕 A implementar
      },
    ],
  },
  {
    id: "interactive-ui", // 🆕 APENAS no menu de PROJETO
    label: "Interface Interativa",
    icon: "🎨",
    path: "/interactive",
    children: [
      {
        id: "agent-chat",
        label: "Chat com Agentes",
        icon: "💬",
        path: "/interactive/agent-chat", // ✅ AgentChatPage.tsx
      },
      {
        id: "agent-designer",
        label: "Designer de Agentes",
        icon: "🤖",
        path: "/interactive/agent-designer", // 🆕 A implementar
      },
      {
        id: "artifact-manager",
        label: "Gestão de Artefatos",
        icon: "📦",
        path: "/interactive/artifacts", // 🆕 A implementar
      },
      {
        id: "system-state",
        label: "Estado do Sistema",
        icon: "📊",
        path: "/interactive/system-state", // 🆕 A implementar
      },
      {
        id: "dynamic-forms",
        label: "Formulários Dinâmicos",
        icon: "📝",
        path: "/interactive/forms", // 🆕 A implementar
      },
    ],
  },
  {
    id: "deploy",
    label: "Deploy",
    icon: "🚀",
    path: "/deploy",
  },
  {
    id: "monitoring",
    label: "Monitoramento",
    icon: "📊",
    path: "/monitoring",
  },
];

interface NavigationProviderProps {
  children: ReactNode;
}

export const NavigationProvider: React.FC<NavigationProviderProps> = ({
  children,
}) => {
  const navigate = useNavigate();

  const [projectContext, setProjectContext] = useState<ProjectContext>({
    projectId: "",
    projectName: "",
    isInProject: false,
  });

  const enterProjectContext = useCallback(
    (projectId: string, projectName: string) => {
      console.log("Entrando no contexto do projeto:", projectId, projectName);
      setProjectContext({
        projectId,
        projectName,
        isInProject: true,
      });
    },
    []
  );

  const exitProjectContext = useCallback(() => {
    console.log("Saindo do contexto do projeto");
    setProjectContext({
      projectId: "",
      projectName: "",
      isInProject: false,
    });
    navigate("/");
  }, [navigate]);

  const getMenuItems = useCallback((): MenuItem[] => {
    if (projectContext.isInProject) {
      return PROJECT_MENU_ITEMS.map((item) => ({
        ...item,
        path: `/project/${projectContext.projectId}${item.path}`,
        children: item.children?.map((child) => ({
          ...child,
          path: `/project/${projectContext.projectId}${child.path}`,
        })),
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
    throw new Error("useNavigation must be used within a NavigationProvider");
  }
  return context;
};
