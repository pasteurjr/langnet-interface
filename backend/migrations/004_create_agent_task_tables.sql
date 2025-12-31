-- Migration 004: Create Agent & Task Generation Tables
-- Data: 2025-12-23
-- Descrição: Tabelas para armazenar sessões de geração automática de agentes e tarefas

-- ═══════════════════════════════════════════════════════════
-- TABLE: agent_task_sessions
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS agent_task_sessions (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    session_name VARCHAR(255) NOT NULL,

    -- Referência à especificação base
    specification_session_id VARCHAR(36) NOT NULL,
    specification_version INT NOT NULL DEFAULT 1,

    -- Configuração da geração
    detail_level ENUM('concise', 'balanced', 'detailed') NOT NULL DEFAULT 'balanced',
    frameworks JSON NOT NULL,  -- ["CrewAI", "AutoGen", etc.]
    custom_instructions TEXT,

    -- Contadores
    agents_count INT NOT NULL DEFAULT 0,
    tasks_count INT NOT NULL DEFAULT 0,

    -- Dados gerados (YAML)
    agents_yaml LONGTEXT,
    tasks_yaml LONGTEXT,

    -- Dados gerados (JSON estruturado)
    agents_json JSON,
    tasks_json JSON,

    -- Grafo de dependências
    dependency_graph JSON,

    -- Status e metadados
    status ENUM('generating', 'completed', 'failed') NOT NULL DEFAULT 'generating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign keys
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- Indexes para performance
    INDEX idx_project_user (project_id, user_id),
    INDEX idx_spec_session (specification_session_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ═══════════════════════════════════════════════════════════
-- TABLE: agent_task_chat_messages
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS agent_task_chat_messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,

    -- Mensagem
    sender ENUM('user', 'system', 'assistant') NOT NULL,
    message TEXT NOT NULL,
    message_type ENUM('status', 'progress', 'result', 'error', 'document') DEFAULT 'status',

    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key
    FOREIGN KEY (session_id) REFERENCES agent_task_sessions(id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_session_created (session_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ═══════════════════════════════════════════════════════════
-- COMMENTS
-- ═══════════════════════════════════════════════════════════

ALTER TABLE agent_task_sessions COMMENT = 'Sessões de geração automática de agentes e tarefas a partir de especificações funcionais';
ALTER TABLE agent_task_chat_messages COMMENT = 'Mensagens de chat para refinamento de agentes e tarefas';
