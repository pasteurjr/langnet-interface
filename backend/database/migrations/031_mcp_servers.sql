-- F2 Fase 1 — Servidores MCP (Model Context Protocol)
-- Registro GLOBAL de servidores MCP; descoberta de tools via cliente MCP.
-- Segredos (headers/credenciais) cifrados/mascarados — nunca retornados em claro.
CREATE TABLE IF NOT EXISTS mcp_servers (
  id                VARCHAR(36)  PRIMARY KEY,
  name              VARCHAR(255) NOT NULL,
  transport         VARCHAR(20)  NOT NULL DEFAULT 'sse',   -- sse | http | stdio
  url               VARCHAR(500),                          -- para sse/http
  command           VARCHAR(500),                          -- para stdio
  category          VARCHAR(100),
  credentials_json  TEXT,                                  -- headers/env (segredo) — mascarado na leitura
  status            VARCHAR(20)  NOT NULL DEFAULT 'registrado', -- registrado | ativo | erro
  capabilities_json LONGTEXT,                              -- tools descobertas
  last_error        TEXT,
  created_by        VARCHAR(36),
  created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_mcp_name (name)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
