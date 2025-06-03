// src/App.tsx (CORRIGIDO - Rotas AgentChatPage DESCOMENTADAS)
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { NavigationProvider } from "./contexts/NavigationContext";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import ProjectList from "./pages/ProjectList";
import ProjectDetail from "./pages/ProjectDetail";
import DocumentsPage from "./pages/DocumentsPage";
import SpecificationPage from "./pages/SpecificationPage";
import AgentsPage from "./pages/AgentsPage";
import TasksPage from "./pages/TasksPage";
import YamlPage from "./pages/YamlPage";
import PetriNetPage from "./pages/PetriNetPage";
import CodePage from "./pages/CodePage";
import MonitoringPage from "./pages/MonitoringPage";
import ChatPage from "./pages/ChatPage";
import SettingsPage from "./pages/SettingsPage";
import HelpPage from "./pages/HelpPage";
import NotFoundPage from "./pages/NotFoundPage";
import DeploymentPage from "./pages/DeploymentPage";

// ✅ Páginas MCP já implementadas (MANTÉM rotas originais)
import McpGlobalConfigPage from "./pages/McpGlobalConfigPage";
import McpServiceDiscoveryPage from "./pages/McpServiceDiscoveryPage";
import McpProjectIntegrationPage from "./pages/McpProjectIntegrationPage";

// ✅ Nova página implementada - DESCOMENTADO
import AgentChatPage from "./pages/AgentChatPage";

import "./App.css";

const App: React.FC = () => {
  return (
    <Router>
      <NavigationProvider>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="projects" element={<ProjectList />} />
            <Route path="projects/new" element={<ProjectDetail />} />
            <Route path="projects/:id" element={<ProjectDetail />} />
            <Route path="projects/:id/documents" element={<DocumentsPage />} />
            <Route path="projects/:id/spec" element={<SpecificationPage />} />
            <Route path="projects/:id/agents" element={<AgentsPage />} />
            <Route path="projects/:id/tasks" element={<TasksPage />} />
            <Route path="projects/:id/yaml" element={<YamlPage />} />
            <Route path="projects/:id/petri" element={<PetriNetPage />} />
            <Route path="projects/:id/code" element={<CodePage />} />
            <Route path="projects/:id/monitor" element={<MonitoringPage />} />
            <Route path="projects/:id/chat" element={<ChatPage />} />

            {/* ✅ ROTAS MCP GLOBAIS - MANTÉM compatibilidade */}
            <Route path="mcp/config" element={<McpGlobalConfigPage />} />
            <Route path="mcp/services" element={<McpServiceDiscoveryPage />} />
            {/* 🆕 Nova rota para sincronização global (a implementar) */}
            <Route
              path="mcp/state-sync"
              element={<div>McpStateSyncPage - A implementar</div>}
            />

            {/* ✅ ROTAS INTERFACE INTERATIVA GLOBAL - DESCOMENTADO */}
            <Route path="interactive/agent-chat" element={<AgentChatPage />} />
            {/* 🆕 Demais rotas (a implementar) */}
            <Route
              path="interactive/agent-designer"
              element={<div>AgentDesignerPage - A implementar</div>}
            />
            <Route
              path="interactive/artifacts"
              element={<div>ArtifactManagerPage - A implementar</div>}
            />
            <Route
              path="interactive/system-state"
              element={<div>SystemStatePage - A implementar</div>}
            />
            <Route
              path="interactive/forms"
              element={<div>DynamicFormsPage - A implementar</div>}
            />

            <Route path="settings" element={<SettingsPage />} />
            <Route path="help" element={<HelpPage />} />

            {/* Rotas standalone para acesso direto */}
            <Route path="/yaml" element={<YamlPage />} />
            <Route path="/specification" element={<SpecificationPage />} />
            <Route path="/code" element={<CodePage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/deployment" element={<DeploymentPage />} />

            {/* ✅ ROTAS ESPECÍFICAS DO CONTEXTO DE PROJETO */}
            <Route
              path="/project/:projectId/documents"
              element={<DocumentsPage />}
            />
            <Route
              path="/project/:projectId/spec"
              element={<SpecificationPage />}
            />
            <Route
              path="/project/:projectId/specification"
              element={<SpecificationPage />}
            />
            <Route path="/project/:projectId/agents" element={<AgentsPage />} />
            <Route path="/project/:projectId/tasks" element={<TasksPage />} />
            <Route path="/project/:projectId/yaml" element={<YamlPage />} />
            <Route
              path="/project/:projectId/petri-net"
              element={<PetriNetPage />}
            />
            <Route path="/project/:projectId/code" element={<CodePage />} />
            <Route
              path="/project/:projectId/code-generation"
              element={<CodePage />}
            />
            <Route
              path="/project/:projectId/deploy"
              element={<DeploymentPage />}
            />
            <Route
              path="/project/:projectId/monitoring"
              element={<MonitoringPage />}
            />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route
              path="/project/:projectId/langfuse"
              element={<MonitoringPage />}
            />

            {/* ✅ ROTAS MCP POR PROJETO - MANTÉM compatibilidade */}
            <Route
              path="/project/:projectId/mcp"
              element={<McpProjectIntegrationPage />}
            />
            <Route
              path="/project/:projectId/mcp/sync"
              element={<div>McpProjectSyncPage - A implementar</div>}
            />
            <Route
              path="/project/:projectId/mcp/services"
              element={<div>McpProjectServicesPage - A implementar</div>}
            />

            {/* ✅ ROTAS INTERFACE INTERATIVA POR PROJETO - DESCOMENTADO */}
            <Route
              path="/project/:projectId/interactive/agent-chat"
              element={<AgentChatPage />}
            />
            <Route
              path="/project/:projectId/interactive/agent-designer"
              element={<div>AgentDesignerPage - A implementar</div>}
            />
            <Route
              path="/project/:projectId/interactive/artifacts"
              element={<div>ArtifactManagerPage - A implementar</div>}
            />
            <Route
              path="/project/:projectId/interactive/system-state"
              element={<div>SystemStatePage - A implementar</div>}
            />
            <Route
              path="/project/:projectId/interactive/forms"
              element={<div>DynamicFormsPage - A implementar</div>}
            />

            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </NavigationProvider>
    </Router>
  );
};

export default App;
