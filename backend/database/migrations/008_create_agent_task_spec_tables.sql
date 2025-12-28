-- ════════════════════════════════════════════════════════════════
-- Migration 008: Agent Task Specification Tables
-- ════════════════════════════════════════════════════════════════
-- Purpose: Create tables for agent/task specification document generation
-- Author: Claude Code
-- Date: 2025-12-24
-- ════════════════════════════════════════════════════════════════

SET FOREIGN_KEY_CHECKS = 0;

-- ════════════════════════════════════════════════════════════════
-- TABELA 1: agent_task_specification_sessions
-- ════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS `agent_task_specification_sessions`;

CREATE TABLE `agent_task_specification_sessions` (
  `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `specification_session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `specification_version` INT(10) UNSIGNED NOT NULL DEFAULT 1,
  `session_name` VARCHAR(255) DEFAULT NULL,
  `started_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_at` TIMESTAMP NULL DEFAULT NULL,
  `status` ENUM('generating','completed','failed','cancelled','paused','reviewing') DEFAULT 'generating',
  `agent_task_spec_document` LONGTEXT DEFAULT NULL,
  `generation_log` LONGTEXT DEFAULT NULL,
  `execution_metadata` LONGTEXT DEFAULT NULL,
  `generation_time_ms` BIGINT(20) UNSIGNED DEFAULT NULL,
  `ai_model_used` VARCHAR(100) DEFAULT NULL,
  `total_agents` INT(10) UNSIGNED DEFAULT 0,
  `total_tasks` INT(10) UNSIGNED DEFAULT 0,
  `approval_status` ENUM('pending','approved','needs_revision','rejected') DEFAULT 'pending',
  `approved_by` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `approved_at` TIMESTAMP NULL DEFAULT NULL,
  `approval_notes` VARCHAR(500) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_spec_session` (`specification_session_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_approved_by` (`approved_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ════════════════════════════════════════════════════════════════
-- TABELA 2: agent_task_spec_version_history
-- ════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS `agent_task_spec_version_history`;

CREATE TABLE `agent_task_spec_version_history` (
  `session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` INT(10) UNSIGNED NOT NULL,
  `agent_task_spec_document` LONGTEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `created_by` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `change_type` ENUM('initial_generation','ai_refinement','manual_edit','approval_revision','feedback_incorporation') DEFAULT 'manual_edit',
  `change_description` VARCHAR(500) DEFAULT NULL,
  `section_changes` LONGTEXT DEFAULT NULL,
  `doc_size` INT(10) UNSIGNED DEFAULT NULL,
  `review_notes` VARCHAR(500) DEFAULT NULL,
  `reviewed_by` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reviewed_at` TIMESTAMP NULL DEFAULT NULL,
  `is_approved_version` BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (`session_id`, `version`),
  KEY `idx_approved_version` (`is_approved_version`),
  KEY `idx_change_type` (`change_type`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_reviewed_by` (`reviewed_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ════════════════════════════════════════════════════════════════
-- TABELA 3: agent_task_spec_chat_messages
-- ════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS `agent_task_spec_chat_messages`;

CREATE TABLE `agent_task_spec_chat_messages` (
  `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_type` ENUM('user','agent','system','assistant') NOT NULL,
  `sender_name` VARCHAR(255) DEFAULT NULL,
  `message_text` LONGTEXT NOT NULL,
  `message_type` ENUM('chat','status','progress','result','error','warning','info','document') DEFAULT 'chat',
  `timestamp` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `parent_message_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `metadata` LONGTEXT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_sender_type` (`sender_type`),
  KEY `idx_message_type` (`message_type`),
  KEY `idx_parent_message` (`parent_message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ════════════════════════════════════════════════════════════════
-- ADD FOREIGN KEYS
-- ════════════════════════════════════════════════════════════════

ALTER TABLE `agent_task_specification_sessions`
  ADD CONSTRAINT `fk_ats_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_ats_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_ats_spec` FOREIGN KEY (`specification_session_id`) REFERENCES `execution_specification_sessions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_ats_approved_by` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

ALTER TABLE `agent_task_spec_version_history`
  ADD CONSTRAINT `fk_atsv_session` FOREIGN KEY (`session_id`) REFERENCES `agent_task_specification_sessions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_atsv_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_atsv_reviewed_by` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

ALTER TABLE `agent_task_spec_chat_messages`
  ADD CONSTRAINT `fk_atscm_session` FOREIGN KEY (`session_id`) REFERENCES `agent_task_specification_sessions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_atscm_parent` FOREIGN KEY (`parent_message_id`) REFERENCES `agent_task_spec_chat_messages` (`id`) ON DELETE SET NULL;

SET FOREIGN_KEY_CHECKS = 1;
