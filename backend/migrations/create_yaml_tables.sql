-- ============================================
-- YAML GENERATION TABLES
-- Migration: Create agents_yaml and tasks_yaml tables
-- Date: 2025-12-29
-- ============================================

-- ============================================
-- AGENTS YAML SESSIONS
-- ============================================
CREATE TABLE agents_yaml_sessions (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  agent_task_spec_session_id CHAR(36) NOT NULL,
  agent_task_spec_version INT UNSIGNED NOT NULL DEFAULT 1,
  session_name VARCHAR(255),

  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP NULL,
  status ENUM('generating', 'completed', 'failed', 'cancelled', 'reviewing') DEFAULT 'generating',

  agents_yaml_content LONGTEXT,
  generation_log LONGTEXT,
  execution_metadata JSON,
  generation_time_ms BIGINT UNSIGNED,
  ai_model_used VARCHAR(100),
  total_agents INT UNSIGNED DEFAULT 0,

  approval_status ENUM('pending', 'approved', 'needs_revision', 'rejected') DEFAULT 'pending',
  approved_by CHAR(36),
  approved_at TIMESTAMP NULL,
  approval_notes VARCHAR(500),

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_project (project_id),
  INDEX idx_spec_session (agent_task_spec_session_id),
  INDEX idx_status (status),
  INDEX idx_created (created_at),

  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_task_spec_session_id) REFERENCES agent_task_specification_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- AGENTS YAML VERSIONS
-- ============================================
CREATE TABLE agents_yaml_version_history (
  session_id CHAR(36) NOT NULL,
  version INT UNSIGNED NOT NULL,
  agents_yaml_content LONGTEXT NOT NULL,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by CHAR(36),
  change_type ENUM('initial_generation', 'ai_refinement', 'manual_edit', 'approval_revision') DEFAULT 'manual_edit',
  change_description VARCHAR(500),
  section_changes JSON,
  doc_size INT UNSIGNED,

  review_notes VARCHAR(500),
  reviewed_by CHAR(36),
  reviewed_at TIMESTAMP NULL,
  is_approved_version TINYINT(1) DEFAULT 0,

  PRIMARY KEY (session_id, version),
  INDEX idx_approved (is_approved_version),
  INDEX idx_change_type (change_type),
  INDEX idx_created (created_at),

  FOREIGN KEY (session_id) REFERENCES agents_yaml_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- AGENTS YAML CHAT
-- ============================================
CREATE TABLE agents_yaml_chat_messages (
  id CHAR(36) PRIMARY KEY,
  session_id CHAR(36) NOT NULL,
  sender_type ENUM('user', 'agent', 'system') NOT NULL,
  sender_name VARCHAR(100),
  message_text TEXT NOT NULL,
  message_type ENUM('chat', 'status', 'progress', 'result', 'error') DEFAULT 'chat',
  parent_message_id CHAR(36),
  metadata JSON,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_session (session_id),
  INDEX idx_timestamp (timestamp),
  FOREIGN KEY (session_id) REFERENCES agents_yaml_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TASKS YAML SESSIONS
-- ============================================
CREATE TABLE tasks_yaml_sessions (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  agent_task_spec_session_id CHAR(36) NOT NULL,
  agent_task_spec_version INT UNSIGNED NOT NULL DEFAULT 1,
  session_name VARCHAR(255),

  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP NULL,
  status ENUM('generating', 'completed', 'failed', 'cancelled', 'reviewing') DEFAULT 'generating',

  tasks_yaml_content LONGTEXT,
  generation_log LONGTEXT,
  execution_metadata JSON,
  generation_time_ms BIGINT UNSIGNED,
  ai_model_used VARCHAR(100),
  total_tasks INT UNSIGNED DEFAULT 0,

  approval_status ENUM('pending', 'approved', 'needs_revision', 'rejected') DEFAULT 'pending',
  approved_by CHAR(36),
  approved_at TIMESTAMP NULL,
  approval_notes VARCHAR(500),

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_project (project_id),
  INDEX idx_spec_session (agent_task_spec_session_id),
  INDEX idx_status (status),
  INDEX idx_created (created_at),

  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_task_spec_session_id) REFERENCES agent_task_specification_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TASKS YAML VERSIONS
-- ============================================
CREATE TABLE tasks_yaml_version_history (
  session_id CHAR(36) NOT NULL,
  version INT UNSIGNED NOT NULL,
  tasks_yaml_content LONGTEXT NOT NULL,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by CHAR(36),
  change_type ENUM('initial_generation', 'ai_refinement', 'manual_edit', 'approval_revision') DEFAULT 'manual_edit',
  change_description VARCHAR(500),
  section_changes JSON,
  doc_size INT UNSIGNED,

  review_notes VARCHAR(500),
  reviewed_by CHAR(36),
  reviewed_at TIMESTAMP NULL,
  is_approved_version TINYINT(1) DEFAULT 0,

  PRIMARY KEY (session_id, version),
  INDEX idx_approved (is_approved_version),
  INDEX idx_change_type (change_type),
  INDEX idx_created (created_at),

  FOREIGN KEY (session_id) REFERENCES tasks_yaml_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TASKS YAML CHAT
-- ============================================
CREATE TABLE tasks_yaml_chat_messages (
  id CHAR(36) PRIMARY KEY,
  session_id CHAR(36) NOT NULL,
  sender_type ENUM('user', 'agent', 'system') NOT NULL,
  sender_name VARCHAR(100),
  message_text TEXT NOT NULL,
  message_type ENUM('chat', 'status', 'progress', 'result', 'error') DEFAULT 'chat',
  parent_message_id CHAR(36),
  metadata JSON,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_session (session_id),
  INDEX idx_timestamp (timestamp),
  FOREIGN KEY (session_id) REFERENCES tasks_yaml_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
