-- ============================================================
-- MIGRATION: Create Specification Tables
-- Date: 2025-12-10
-- Description: Create tables for functional specification management
--              Replicates structure of execution_sessions + session_requirements_version
-- ============================================================

USE langnet;

-- ============================================================
-- Table: execution_specification_sessions
-- Description: Stores specification generation sessions
-- ============================================================

CREATE TABLE IF NOT EXISTS `execution_specification_sessions` (
  `id` char(36) NOT NULL DEFAULT (uuid()) COMMENT 'Unique session ID',
  `project_id` char(36) NOT NULL COMMENT 'Project ID',
  `user_id` char(36) NOT NULL COMMENT 'User who generated the specification',
  `requirements_session_id` char(36) NOT NULL COMMENT 'Source requirements session ID',
  `requirements_version` int(10) unsigned NOT NULL COMMENT 'Specific version of requirements used',
  `session_name` varchar(255) DEFAULT NULL COMMENT 'Optional session name',
  `started_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Generation start time',
  `finished_at` timestamp NULL DEFAULT NULL COMMENT 'Generation end time',
  `status` enum('generating','completed','failed','cancelled','paused','reviewing') NOT NULL DEFAULT 'generating' COMMENT 'Generation status',
  `specification_document` longtext DEFAULT NULL COMMENT 'Generated specification document in markdown format',
  `generation_log` longtext DEFAULT NULL COMMENT 'Generation process log',
  `execution_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Generation metadata (prompts, config, etc)',
  `generation_time_ms` bigint(20) unsigned DEFAULT NULL COMMENT 'Total generation time in milliseconds',
  `ai_model_used` varchar(100) DEFAULT NULL COMMENT 'AI model used (gpt-4, claude-3, etc)',
  `total_sections` int(10) unsigned DEFAULT 0 COMMENT 'Total sections generated',
  `approval_status` enum('pending','approved','needs_revision','rejected') NOT NULL DEFAULT 'pending' COMMENT 'Approval status',
  `approved_by` char(36) DEFAULT NULL COMMENT 'ID of approver user',
  `approved_at` timestamp NULL DEFAULT NULL COMMENT 'Approval timestamp',
  `approval_notes` varchar(500) DEFAULT NULL COMMENT 'Approval/rejection notes',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Record creation timestamp',
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Record update timestamp',

  -- Primary Key
  PRIMARY KEY (`id`),

  -- Indexes for common queries
  KEY `idx_spec_session_project_id` (`project_id`),
  KEY `idx_spec_session_user_id` (`user_id`),
  KEY `idx_spec_session_requirements_session` (`requirements_session_id`),
  KEY `idx_spec_session_status` (`status`),
  KEY `idx_spec_session_approval_status` (`approval_status`),
  KEY `idx_spec_session_started_at` (`started_at`),
  KEY `idx_spec_project_status` (`project_id`,`status`,`started_at` DESC),
  KEY `idx_spec_approval_pending` (`approval_status`,`project_id`),

  -- Foreign Keys
  CONSTRAINT `fk_spec_session_project_id`
    FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,

  CONSTRAINT `fk_spec_session_user_id`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,

  CONSTRAINT `fk_spec_session_requirements_session`
    FOREIGN KEY (`requirements_session_id`) REFERENCES `execution_sessions` (`id`)
    ON DELETE RESTRICT,

  CONSTRAINT `fk_spec_session_approved_by`
    FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`)
    ON DELETE SET NULL,

  -- Check Constraints
  CONSTRAINT `chk_spec_finish_time`
    CHECK (`finished_at` is null or `finished_at` >= `started_at`),

  CONSTRAINT `chk_spec_approval_timestamps`
    CHECK (`approved_at` is null or `approved_at` >= `started_at`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Specification generation sessions';

-- ============================================================
-- Table: specification_version_history
-- Description: Version history for specifications
-- ============================================================

CREATE TABLE IF NOT EXISTS `specification_version_history` (
  `specification_session_id` char(36) NOT NULL COMMENT 'Specification session ID',
  `version` int(10) unsigned NOT NULL COMMENT 'Version number (sequential)',
  `specification_document` longtext NOT NULL COMMENT 'Full specification document in markdown',
  `created_at` timestamp NULL DEFAULT current_timestamp() COMMENT 'Version creation timestamp',
  `created_by` char(36) DEFAULT NULL COMMENT 'User who created this version',
  `change_type` enum('initial_generation','ai_refinement','manual_edit','approval_revision','feedback_incorporation') DEFAULT 'manual_edit' COMMENT 'Type of change',
  `change_description` varchar(500) DEFAULT NULL COMMENT 'Description of changes made',
  `section_changes` longtext DEFAULT NULL COMMENT 'JSON detailing which sections were modified',
  `doc_size` int(10) unsigned DEFAULT NULL COMMENT 'Document size in bytes',
  `review_notes` varchar(500) DEFAULT NULL COMMENT 'Reviewer notes (if applicable)',
  `reviewed_by` char(36) DEFAULT NULL COMMENT 'User who reviewed this version',
  `reviewed_at` timestamp NULL DEFAULT NULL COMMENT 'Review timestamp',
  `is_approved_version` boolean DEFAULT false COMMENT 'Flag if this is the approved version',

  -- Composite Primary Key (session_id, version)
  PRIMARY KEY (`specification_session_id`,`version`),

  -- Indexes
  KEY `idx_spec_version_session_id` (`specification_session_id`),
  KEY `idx_spec_version_created_at` (`created_at`),
  KEY `idx_spec_version_change_type` (`change_type`),
  KEY `idx_spec_version_approved` (`is_approved_version`),

  -- Foreign Keys
  CONSTRAINT `fk_spec_version_session_id`
    FOREIGN KEY (`specification_session_id`) REFERENCES `execution_specification_sessions` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,

  CONSTRAINT `fk_spec_version_created_by`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
    ON DELETE SET NULL,

  CONSTRAINT `fk_spec_version_reviewed_by`
    FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`)
    ON DELETE SET NULL,

  -- Check Constraints
  CONSTRAINT `chk_spec_version_review_time`
    CHECK (`reviewed_at` is null or `reviewed_at` >= `created_at`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='Specification version history';

-- ============================================================
-- Verification Queries (Optional - for testing)
-- ============================================================

-- Verify tables were created
SELECT 'execution_specification_sessions table' as table_name,
       COUNT(*) as row_count
FROM information_schema.tables
WHERE table_schema = 'langnet'
  AND table_name = 'execution_specification_sessions';

SELECT 'specification_version_history table' as table_name,
       COUNT(*) as row_count
FROM information_schema.tables
WHERE table_schema = 'langnet'
  AND table_name = 'specification_version_history';

-- Show table structures
DESCRIBE execution_specification_sessions;
DESCRIBE specification_version_history;

-- ============================================================
-- End of Migration
-- ============================================================
