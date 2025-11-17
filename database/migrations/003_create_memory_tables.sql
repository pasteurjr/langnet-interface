-- Migration 003: Create Memory System Tables
-- System for standardized agent memory across the application
-- Supports: conversations, messages, agent memory, and project context

-- ============================================================================
-- CONVERSATIONS TABLE
-- Tracks all conversations with agents (chat, document analysis, refinement)
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversations (
    id CHAR(36) PRIMARY KEY,
    project_id CHAR(36) NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    user_id CHAR(36) NULL,
    conversation_type ENUM('chat', 'document_analysis', 'task_execution', 'refinement', 'agent_design') NOT NULL DEFAULT 'chat',
    context_data LONGTEXT NULL COMMENT 'JSON with context (document_id, task_id, execution_id, etc)',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    message_count INT DEFAULT 0,
    status ENUM('active', 'paused', 'completed', 'failed') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

    INDEX idx_project (project_id),
    INDEX idx_agent (agent_id),
    INDEX idx_status (status),
    INDEX idx_type (conversation_type),
    INDEX idx_started (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- MESSAGES TABLE
-- Stores all messages exchanged in conversations
-- ============================================================================

CREATE TABLE IF NOT EXISTS messages (
    id CHAR(36) PRIMARY KEY,
    conversation_id CHAR(36) NOT NULL,
    agent_id VARCHAR(100) NULL COMMENT 'Agent who sent the message (NULL if from user)',
    sender ENUM('user', 'agent', 'system') NOT NULL,
    content LONGTEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL DEFAULT 'text' COMMENT 'text, command, error, result, tool_use, thinking',
    metadata LONGTEXT NULL COMMENT 'JSON with extra data (tokens, cost, tool_calls, etc)',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,

    INDEX idx_conversation (conversation_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_sender (sender),
    INDEX idx_type (message_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- AGENT_MEMORY TABLE
-- Stores agent memory items (short-term, long-term, context, entities)
-- Replaces pickle files with database persistence
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_memory (
    id CHAR(36) PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    project_id CHAR(36) NOT NULL,
    conversation_id CHAR(36) NULL COMMENT 'Optional link to conversation',
    memory_type ENUM('short_term', 'long_term', 'context', 'entity') NOT NULL DEFAULT 'short_term',
    key_name VARCHAR(255) NOT NULL,
    value LONGTEXT NOT NULL COMMENT 'JSON or text value',
    importance_score DECIMAL(5,2) DEFAULT 1.0 COMMENT 'Used for pruning (0.0-100.0)',
    access_count INT DEFAULT 0 COMMENT 'Number of times accessed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL COMMENT 'Expiration time for short-term memory',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,

    INDEX idx_agent_project (agent_id, project_id),
    INDEX idx_memory_type (memory_type),
    INDEX idx_importance (importance_score DESC),
    INDEX idx_key (key_name),
    INDEX idx_expires (expires_at),
    UNIQUE KEY unique_memory_key (agent_id, project_id, memory_type, key_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- PROJECT_CONTEXT TABLE
-- Stores accumulated knowledge about projects (requirements, architecture, decisions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS project_context (
    id CHAR(36) PRIMARY KEY,
    project_id CHAR(36) NOT NULL,
    context_type VARCHAR(100) NOT NULL COMMENT 'requirements, architecture, decisions, glossary, entities, workflows',
    context_key VARCHAR(255) NOT NULL COMMENT 'Specific key within type (e.g., FR-001, entity:User)',
    context_value LONGTEXT NOT NULL COMMENT 'JSON or text value',
    source VARCHAR(255) NULL COMMENT 'Where this context came from (document_analysis, chat, manual, agent_suggestion)',
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

    UNIQUE KEY unique_context (project_id, context_type, context_key),
    INDEX idx_project (project_id),
    INDEX idx_context_type (context_type),
    INDEX idx_source (source),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- CONVERSATION_SUMMARIES TABLE
-- Stores LLM-generated summaries of long conversations to reduce token usage
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversation_summaries (
    id CHAR(36) PRIMARY KEY,
    conversation_id CHAR(36) NOT NULL,
    summary_text LONGTEXT NOT NULL,
    message_range_start CHAR(36) NULL COMMENT 'First message ID included in summary',
    message_range_end CHAR(36) NULL COMMENT 'Last message ID included in summary',
    messages_summarized INT DEFAULT 0,
    tokens_saved INT DEFAULT 0 COMMENT 'Estimated tokens saved by summarization',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,

    INDEX idx_conversation (conversation_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- MEMORY_STATS TABLE
-- Tracks memory usage statistics per agent/project for monitoring
-- ============================================================================

CREATE TABLE IF NOT EXISTS memory_stats (
    id CHAR(36) PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    project_id CHAR(36) NOT NULL,
    stat_date DATE NOT NULL,
    short_term_count INT DEFAULT 0,
    long_term_count INT DEFAULT 0,
    context_count INT DEFAULT 0,
    entity_count INT DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    avg_importance DECIMAL(5,2) DEFAULT 0.0,
    total_accesses INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

    UNIQUE KEY unique_agent_date (agent_id, project_id, stat_date),
    INDEX idx_agent_project (agent_id, project_id),
    INDEX idx_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TRIGGERS
-- Automatic maintenance triggers
-- ============================================================================

-- Trigger: Update message count when new message is inserted
DELIMITER $$

CREATE TRIGGER update_message_count_after_insert
AFTER INSERT ON messages
FOR EACH ROW
BEGIN
    UPDATE conversations
    SET message_count = message_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
END$$

DELIMITER ;

-- Trigger: Update access stats when memory is recalled
DELIMITER $$

CREATE TRIGGER update_memory_access_after_read
BEFORE UPDATE ON agent_memory
FOR EACH ROW
BEGIN
    IF NEW.last_accessed > OLD.last_accessed THEN
        SET NEW.access_count = OLD.access_count + 1;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- No initial data needed for memory tables
-- Tables will be populated as agents interact with users

-- ============================================================================
-- COMMENTS & DOCUMENTATION
-- ============================================================================

-- Table purposes:
-- - conversations: Track all agent interactions with context
-- - messages: Store conversation history for recall and refinement
-- - agent_memory: Persistent memory for agents (replaces pickle files)
-- - project_context: Accumulated project knowledge (requirements, architecture)
-- - conversation_summaries: Reduce token usage for long conversations
-- - memory_stats: Monitor memory usage and performance

-- Memory types explained:
-- - short_term: Recent conversation, expires after session or time limit
-- - long_term: Important information, persists across sessions
-- - context: Project/document context, structured knowledge
-- - entity: Extracted entities (people, systems, concepts)

-- Importance score (0.0-100.0):
-- - Used for pruning when memory limits are reached
-- - Higher score = more important, less likely to be pruned
-- - Based on: access_count, recency, manual importance, relevance

-- Retention policies:
-- - short_term: Prune by time (expires_at) or capacity (keep last N)
-- - long_term: Prune by importance score when capacity reached
-- - context: Never auto-prune, manual cleanup only
-- - entity: Merge duplicates, prune low-importance entities
