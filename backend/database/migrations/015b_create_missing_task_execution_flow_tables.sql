-- ════════════════════════════════════════════════════════════════
-- Migration 015b: Missing Task Execution Flow Tables
-- ════════════════════════════════════════════════════════════════
-- Purpose: Create version_history and chat_messages tables (missing from 015)
-- Author: Claude Code
-- Date: 2026-01-10
-- ════════════════════════════════════════════════════════════════

SET FOREIGN_KEY_CHECKS = 0;

-- ════════════════════════════════════════════════════════════════
-- TABELA: task_execution_flow_version_history
-- ════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS `task_execution_flow_version_history`;

CREATE TABLE `task_execution_flow_version_history` (
  `session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` INT(10) UNSIGNED NOT NULL,
  `flow_document` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `change_type` ENUM('initial_generation','ai_refinement','manual_edit','approval_revision','feedback_incorporation') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'manual_edit',
  `change_description` VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `section_changes` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `doc_size` INT(10) UNSIGNED DEFAULT NULL,
  `review_notes` VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reviewed_by` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reviewed_at` TIMESTAMP NULL DEFAULT NULL,
  `is_approved_version` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`session_id`, `version`),
  KEY `idx_change_type` (`change_type`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_approved` (`is_approved_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Version history for task execution flow documents';

-- ════════════════════════════════════════════════════════════════
-- TABELA: task_execution_flow_chat_messages
-- ════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS `task_execution_flow_chat_messages`;

CREATE TABLE `task_execution_flow_chat_messages` (
  `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_type` ENUM('user','agent','system','assistant') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'system',
  `sender_name` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message_text` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_type` ENUM('chat','status','progress','result','error','warning','info','document') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'chat',
  `timestamp` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `parent_message_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `metadata` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Chat messages for task execution flow refinement sessions';

-- ════════════════════════════════════════════════════════════════
-- ADD FOREIGN KEYS
-- ════════════════════════════════════════════════════════════════

ALTER TABLE `task_execution_flow_version_history`
  ADD CONSTRAINT `fk_tefvh_session` FOREIGN KEY (`session_id`) REFERENCES `task_execution_flow_sessions` (`id`) ON DELETE CASCADE;

ALTER TABLE `task_execution_flow_chat_messages`
  ADD CONSTRAINT `fk_tefcm_session` FOREIGN KEY (`session_id`) REFERENCES `task_execution_flow_sessions` (`id`) ON DELETE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;
