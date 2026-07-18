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

// Menu GLOBAL. status:"mock" exibe o selo 🚧 (etapa ainda a implementar).
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
    status: "mock",
    children: [
      { id: "mcp-config", label: "Configuração Global", icon: "🌐", path: "/mcp/config" },
      { id: "mcp-services", label: "Descoberta de Serviços", icon: "🔍", path: "/mcp/services" },
      { id: "mcp-state-sync", label: "Sincronização de Estados", icon: "🔄", path: "/mcp/state-sync" },
    ],
  },
  {
    id: "settings",
    label: "Configurações",
    icon: "⚙️",
    path: "/settings",
    status: "mock",
  },
  {
    id: "help",
    label: "Ajuda",
    icon: "❓",
    path: "/help",
    status: "mock",
  },
];

// Menu de PROJETO — agrupado por seções (section). Duplicados removidos
// (Agentes, Tarefas, YAML avulso, Gerar YAML). Mock/roadmap marcado com status:"mock".
const PROJECT_MENU_ITEMS: MenuItem[] = [
  // ── Pipeline (funcional) ──
  { id: "documents", label: "Documentos", icon: "📄", path: "/documents", section: "Pipeline" },
  { id: "spec", label: "Especificação", icon: "📝", path: "/spec", section: "Pipeline" },
  { id: "data-model", label: "Modelo de Dados", icon: "🗄️", path: "/data-model", section: "Pipeline" },
  { id: "ui-spec", label: "Interface & Protótipo", icon: "🎨", path: "/ui-spec", section: "Pipeline" },
  { id: "agent-task", label: "Agentes & Tarefas", icon: "⚙️", path: "/agent-task", section: "Pipeline" },
  { id: "yaml-generation", label: "YAML de Agentes e Tarefas", icon: "📦", path: "/yaml-generation", section: "Pipeline" },
  { id: "task-execution-flow", label: "Sequência de Tarefas", icon: "🔄", path: "/task-execution-flow", section: "Pipeline" },
  { id: "petri-net", label: "Rede de Petri", icon: "🔗", path: "/petri-net", section: "Pipeline" },
  { id: "code-generation", label: "Geração de Código", icon: "💻", path: "/code-generation", section: "Pipeline" },
  { id: "test-cases", label: "Casos de Teste & Validação", icon: "🧪", path: "/test-cases", section: "Pipeline" },

  // ── Operação (a implementar) ──
  { id: "deploy", label: "Deploy", icon: "🚀", path: "/deploy", section: "Operação", status: "mock" },
  { id: "monitoring", label: "Monitoramento", icon: "📊", path: "/monitoring", section: "Operação", status: "mock" },

  // ── Interação (a implementar) ──
  { id: "agent-chat", label: "Chat com Agentes", icon: "💬", path: "/interactive/agent-chat", section: "Interação", status: "mock" },
  { id: "agent-designer", label: "Designer de Agentes", icon: "🤖", path: "/interactive/agent-designer", section: "Interação", status: "mock" },
  { id: "artifact-manager", label: "Gestão de Artefatos", icon: "📦", path: "/interactive/artifacts", section: "Interação", status: "mock" },
  { id: "system-state", label: "Estado do Sistema", icon: "📊", path: "/interactive/system-state", section: "Interação", status: "mock" },
  { id: "dynamic-forms", label: "Formulários Dinâmicos", icon: "📝", path: "/interactive/forms", section: "Interação", status: "mock" },

  // ── Integração & Config (a implementar) ──
  {
    id: "mcp-project",
    label: "MCP do Projeto",
    icon: "🔌",
    path: "/mcp",
    section: "Integração & Config",
    status: "mock",
    children: [
      { id: "mcp-project-integration", label: "Integração", icon: "🔗", path: "/mcp" },
      { id: "mcp-project-sync", label: "Sincronização", icon: "🔄", path: "/mcp/sync" },
      { id: "mcp-project-services", label: "Serviços", icon: "🛠️", path: "/mcp/services" },
    ],
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
