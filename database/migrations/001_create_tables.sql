-- ===================================================================
-- LangNet Database Schema - Migration 001
-- Created: 2025-11-07
-- Description: Create all missing tables for LangNet system
-- ===================================================================

USE langnet;

-- ===================================================================
-- TABLE: documents
-- Purpose: Store project documentation for analysis
-- Requisito: 2.1 - Módulo de Leitura e Análise de Documentação
-- ===================================================================
CREATE TABLE IF NOT EXISTS documents (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  file_type VARCHAR(50),
  file_size BIGINT UNSIGNED,
  file_path VARCHAR(1000),
  storage_type ENUM('local','s3','gcs','azure') DEFAULT 'local',
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status ENUM('uploaded','analyzing','analyzed','error') NOT NULL DEFAULT 'uploaded',
  analysis_results LONGTEXT,
  extracted_entities LONGTEXT,
  requirements LONGTEXT,
  metadata LONGTEXT,
  INDEX idx_project_id (project_id),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_uploaded_at (uploaded_at),
  FULLTEXT INDEX ft_filename (filename, original_filename),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- TABLE: specifications
-- Purpose: Store functional specifications for projects
-- Requisito: 2.2 - Módulo de Geração de Especificação Funcional
-- ===================================================================
CREATE TABLE IF NOT EXISTS specifications (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL UNIQUE,
  user_id CHAR(36) NOT NULL,
  content LONGTEXT NOT NULL,
  version VARCHAR(50) DEFAULT '1.0',
  status ENUM('draft','generated','reviewing','approved','needs_revision') NOT NULL DEFAULT 'draft',
  requirements_functional LONGTEXT,
  requirements_nonfunctional LONGTEXT,
  data_model LONGTEXT,
  workflows LONGTEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  approved_at TIMESTAMP NULL,
  approved_by CHAR(36),
  INDEX idx_project_id (project_id),
  INDEX idx_status (status),
  INDEX idx_updated_at (updated_at),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
  FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- TABLE: agents
-- Purpose: Store agent definitions for projects
-- Requisito: 2.3.1 - Identificação e Design de Agentes
-- ===================================================================
CREATE TABLE IF NOT EXISTS agents (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  agent_id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(500),
  goal TEXT,
  backstory TEXT,
  tools LONGTEXT,
  verbose TINYINT(1) DEFAULT 0,
  allow_delegation TINYINT(1) DEFAULT 0,
  max_iter INT DEFAULT 25,
  max_rpm INT,
  status ENUM('active','inactive','draft') NOT NULL DEFAULT 'draft',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  metadata LONGTEXT,
  UNIQUE KEY unique_agent_project (project_id, agent_id),
  INDEX idx_project_id (project_id),
  INDEX idx_agent_id (agent_id),
  INDEX idx_status (status),
  INDEX idx_name (name),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- TABLE: tasks
-- Purpose: Store task definitions for projects
-- Requisito: 2.3.2 - Design de Tarefas
-- ===================================================================
CREATE TABLE IF NOT EXISTS tasks (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  task_id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  agent_id CHAR(36),
  expected_output TEXT,
  tools LONGTEXT,
  async_execution TINYINT(1) DEFAULT 0,
  context LONGTEXT,
  input_schema LONGTEXT,
  output_schema LONGTEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  metadata LONGTEXT,
  UNIQUE KEY unique_task_project (project_id, task_id),
  INDEX idx_project_id (project_id),
  INDEX idx_task_id (task_id),
  INDEX idx_agent_id (agent_id),
  INDEX idx_name (name),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- TABLE: yaml_files
-- Purpose: Store generated YAML configuration files
-- Requisito: 2.4 - Módulo de Geração de Arquivos YAML
-- ===================================================================
CREATE TABLE IF NOT EXISTS yaml_files (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  file_type ENUM('agents','tasks','tools','config') NOT NULL,
  filename VARCHAR(255) NOT NULL,
  content LONGTEXT NOT NULL,
  version VARCHAR(50),
  is_valid TINYINT(1) DEFAULT 1,
  validation_errors LONGTEXT,
  generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_project_id (project_id),
  INDEX idx_file_type (file_type),
  INDEX idx_filename (filename),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- TABLE: code_generations
-- Purpose: Store generated Python code
-- Requisito: 2.6 - Módulo de Geração de Código Python
-- ===================================================================
CREATE TABLE IF NOT EXISTS code_generations (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36) NOT NULL,
  framework ENUM('crewai','langchain','autogen','custom') NOT NULL,
  llm_provider VARCHAR(50),
  status ENUM('pending','generating','ready','error','building','deploying','deployed') NOT NULL DEFAULT 'pending',
  code_structure LONGTEXT,
  files LONGTEXT,
  generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  built_at TIMESTAMP NULL,
  deployed_at TIMESTAMP NULL,
  deployment_url VARCHAR(500),
  build_logs LONGTEXT,
  test_results LONGTEXT,
  quality_metrics LONGTEXT,
  metadata LONGTEXT,
  INDEX idx_project_id (project_id),
  INDEX idx_status (status),
  INDEX idx_framework (framework),
  INDEX idx_generated_at (generated_at),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- TABLE: mcp_connections
-- Purpose: Store MCP (Model Context Protocol) connections
-- Requisito: 2.7 - Módulo de Integração com MCP
-- ===================================================================
CREATE TABLE IF NOT EXISTS mcp_connections (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36),
  server_name VARCHAR(255) NOT NULL,
  server_url VARCHAR(500) NOT NULL,
  auth_type ENUM('none','basic','bearer','apikey') DEFAULT 'none',
  auth_credentials LONGTEXT,
  services LONGTEXT,
  status ENUM('active','inactive','error') NOT NULL DEFAULT 'inactive',
  last_sync TIMESTAMP NULL,
  health_check_url VARCHAR(500),
  metadata LONGTEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_project_id (project_id),
  INDEX idx_status (status),
  INDEX idx_server_name (server_name),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- TABLE: monitoring_metrics
-- Purpose: Store monitoring metrics (Langfuse integration)
-- Requisito: 2.8 - Módulo de Monitoramento via Langfuse
-- ===================================================================
CREATE TABLE IF NOT EXISTS monitoring_metrics (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  project_id CHAR(36),
  session_id CHAR(36),
  task_execution_id CHAR(36),
  metric_type ENUM('llm_call','token_usage','latency','error','cost') NOT NULL,
  metric_name VARCHAR(255) NOT NULL,
  metric_value DECIMAL(20,6),
  metric_unit VARCHAR(50),
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  trace_id VARCHAR(255),
  span_id VARCHAR(255),
  metadata LONGTEXT,
  INDEX idx_project_id (project_id),
  INDEX idx_session_id (session_id),
  INDEX idx_task_execution_id (task_execution_id),
  INDEX idx_metric_type (metric_type),
  INDEX idx_timestamp (timestamp),
  INDEX idx_trace_id (trace_id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (session_id) REFERENCES execution_sessions(id) ON DELETE CASCADE,
  FOREIGN KEY (task_execution_id) REFERENCES task_executions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- Additional Indexes for Performance Optimization
-- ===================================================================

-- Composite indexes for common queries
CREATE INDEX idx_project_user ON projects(user_id, created_at DESC);
CREATE INDEX idx_session_project_status ON execution_sessions(project_id, status, started_at DESC);
CREATE INDEX idx_task_exec_session_status ON task_executions(session_id, status, started_at);
CREATE INDEX idx_logs_task_timestamp ON verbose_logs(task_execution_id, timestamp DESC);
CREATE INDEX idx_metrics_project_time ON monitoring_metrics(project_id, timestamp DESC);

-- Full-text search for projects
ALTER TABLE projects ADD FULLTEXT INDEX ft_name_description (name, description);

-- ===================================================================
-- Verification Queries
-- ===================================================================

-- Show all tables
SHOW TABLES;

-- Verify new tables structure
DESCRIBE documents;
DESCRIBE specifications;
DESCRIBE agents;
DESCRIBE tasks;
DESCRIBE yaml_files;
DESCRIBE code_generations;
DESCRIBE mcp_connections;
DESCRIBE monitoring_metrics;

-- Count records in each table
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'documents', COUNT(*) FROM documents
UNION ALL SELECT 'specifications', COUNT(*) FROM specifications
UNION ALL SELECT 'agents', COUNT(*) FROM agents
UNION ALL SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL SELECT 'yaml_files', COUNT(*) FROM yaml_files
UNION ALL SELECT 'code_generations', COUNT(*) FROM code_generations
UNION ALL SELECT 'execution_sessions', COUNT(*) FROM execution_sessions
UNION ALL SELECT 'task_executions', COUNT(*) FROM task_executions
UNION ALL SELECT 'execution_outputs', COUNT(*) FROM execution_outputs
UNION ALL SELECT 'verbose_logs', COUNT(*) FROM verbose_logs
UNION ALL SELECT 'mcp_connections', COUNT(*) FROM mcp_connections
UNION ALL SELECT 'monitoring_metrics', COUNT(*) FROM monitoring_metrics;

-- ===================================================================
-- END OF MIGRATION 001
-- ===================================================================
