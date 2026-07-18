// src/App.tsx (ATUALIZADO - AgentDesignerPage ADICIONADO + Auth)
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { NavigationProvider } from "./contexts/NavigationContext";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import ProjectList from "./pages/ProjectList";
import ProjectDetail from "./pages/ProjectDetail";
import DocumentsPage from "./pages/DocumentsPage";
import SpecificationPage from "./pages/SpecificationPage";
import DataModelPage from "./pages/DataModelPage";
import UISpecPage from "./pages/UISpecPage";
import TestCasesPage from "./pages/TestCasesPage";
import SequenciaTarefasPage from "./pages/SequenciaTarefasPage";
import AgentsPage from "./pages/AgentsPage";
import TasksPage from "./pages/TasksPage";
import AgentTaskPage from "./pages/AgentTaskPage";
import YamlGenerationPage from "./pages/YamlGenerationPage";
import GenerateYamlPage from "./pages/GenerateYamlPage";
import YamlPage from "./pages/YamlPage";
import PetriNetPage from "./pages/PetriNetPage";
import CodePage from "./pages/CodePage";
import CodeGenerationPage from "./pages/CodeGenerationPage";
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

// ✅ Páginas Interface Interativa implementadas
import AgentChatPage from "./pages/AgentChatPage";
import AgentDesignerPage from "./pages/AgentDesignerPage";

// ✅ Novas páginas implementadas
import ArtifactManagerPage from "./pages/ArtifactManagerPage";
import SystemStatePage from "./pages/SystemStatePage";
import DynamicFormsPage from "./pages/DynamicFormsPage";
import McpStateSyncPage from "./pages/McpStateSyncPage";

// 🔐 Páginas de Autenticação
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ProtectedRoute from "./components/auth/ProtectedRoute";

// 📄 Páginas de Documentos
import RequirementsDocumentPage from "./pages/RequirementsDocumentPage";

import "./App.css";

const App: React.FC = () => {
  return (
    <Router>
      <NavigationProvider>
        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
        <Routes>
          {/* 🔓 Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* 🔐 Protected Routes */}
          <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="projects" element={<ProjectList />} />
            <Route path="projects/new" element={<ProjectDetail />} />
            <Route path="projects/:id" element={<ProjectDetail />} />
            <Route path="projects/:id/documents" element={<DocumentsPage />} />
            <Route path="projects/:id/spec" element={<SpecificationPage />} />
            <Route path="projects/:id/data-model" element={<DataModelPage />} />
            <Route path="projects/:id/ui-spec" element={<UISpecPage />} />
            <Route path="projects/:id/test-cases" element={<TestCasesPage />} />
            <Route path="projects/:id/agent-task" element={<AgentTaskPage />} />
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
            {/* ✅ Nova rota para sincronização global */}
            <Route
              path="mcp/state-sync"
              element={<McpStateSyncPage />}
            />
            {/* ✅ ROTAS INTERFACE INTERATIVA GLOBAL - ATUALIZADAS */}
            <Route path="interactive/agent-chat" element={<AgentChatPage />} />
            <Route
              path="interactive/agent-designer"
              element={<AgentDesignerPage />}
            />{" "}
            {/* 🆕 ROTA ATUALIZADA */}
            {/* ✅ Demais rotas implementadas */}
            <Route
              path="interactive/artifacts"
              element={<ArtifactManagerPage />}
            />
            <Route
              path="interactive/system-state"
              element={<SystemStatePage />}
            />
            <Route
              path="interactive/forms"
              element={<DynamicFormsPage />}
            />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="help" element={<HelpPage />} />
            {/* Rotas standalone para acesso direto */}
            <Route path="/generate-yaml" element={<GenerateYamlPage />} />
            <Route path="/yaml" element={<YamlPage />} />
            <Route path="/spec" element={<SpecificationPage />} />
            <Route path="/specification" element={<SpecificationPage />} />
            <Route path="/data-model" element={<DataModelPage />} />
            <Route path="/project/:projectId/data-model" element={<DataModelPage />} />
            <Route path="/ui-spec" element={<UISpecPage />} />
            <Route path="/project/:projectId/ui-spec" element={<UISpecPage />} />
            <Route path="/test-cases" element={<TestCasesPage />} />
            <Route path="/project/:projectId/test-cases" element={<TestCasesPage />} />
            <Route path="/task-execution-flow" element={<SequenciaTarefasPage />} />
            <Route path="/code" element={<CodePage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/deployment" element={<DeploymentPage />} />
            {/* ✅ ROTAS ESPECÍFICAS DO CONTEXTO DE PROJETO */}
            <Route
              path="/project/:projectId/documents"
              element={<DocumentsPage />}
            />
            <Route
              path="/project/:projectId/requirements/:executionId"
              element={<RequirementsDocumentPage />}
            />
            <Route
              path="/project/:projectId/spec"
              element={<SpecificationPage />}
            />
            <Route
              path="/project/:projectId/specification"
              element={<SpecificationPage />}
            />
            <Route
              path="/project/:projectId/task-execution-flow"
              element={<SequenciaTarefasPage />}
            />
            <Route
              path="/project/:projectId/agent-task"
              element={<AgentTaskPage />}
            />
            <Route
              path="/project/:projectId/yaml-generation"
              element={<YamlGenerationPage />}
            />
            <Route
              path="/project/:projectId/generate-yaml"
              element={<GenerateYamlPage />}
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
              element={<CodeGenerationPage />}
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
              element={<McpStateSyncPage />}
            />
            <Route
              path="/project/:projectId/mcp/services"
              element={<div>McpProjectServicesPage - A implementar</div>}
            />
            {/* ✅ ROTAS INTERFACE INTERATIVA POR PROJETO - ATUALIZADAS */}
            <Route
              path="/project/:projectId/interactive/agent-chat"
              element={<AgentChatPage />}
            />
            <Route
              path="/project/:projectId/interactive/agent-designer"
              element={<AgentDesignerPage />}
            />
            <Route
              path="/project/:projectId/interactive/artifacts"
              element={<ArtifactManagerPage />}
            />
            <Route
              path="/project/:projectId/interactive/system-state"
              element={<SystemStatePage />}
            />
            <Route
              path="/project/:projectId/interactive/forms"
              element={<DynamicFormsPage />}
            />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </NavigationProvider>
    </Router>
  );
};

export default App;
