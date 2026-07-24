-- F2 Fase 2 — Vínculo de servidores MCP por projeto + atribuição de tools aos agentes
CREATE TABLE IF NOT EXISTS mcp_project_servers (
  project_id     VARCHAR(36) NOT NULL,
  mcp_server_id  VARCHAR(36) NOT NULL,
  enabled        TINYINT(1)  NOT NULL DEFAULT 1,
  created_at     TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (project_id, mcp_server_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS mcp_agent_tools (
  id             VARCHAR(36) PRIMARY KEY,
  project_id     VARCHAR(36) NOT NULL,
  agent_id       VARCHAR(120) NOT NULL,   -- chave do agente no agents.yaml
  mcp_server_id  VARCHAR(36) NOT NULL,
  tool_name      VARCHAR(200) NOT NULL,
  source         VARCHAR(20) NOT NULL DEFAULT 'manual', -- manual | sugerido
  created_at     TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_agent_tool (project_id, agent_id, mcp_server_id, tool_name)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
