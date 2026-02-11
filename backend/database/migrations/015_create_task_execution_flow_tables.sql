-- ════════════════════════════════════════════════════════════════
-- Migration 015: Task Execution Flow Tables
-- ════════════════════════════════════════════════════════════════
-- Purpose: Create table for task execution flow document generation
-- Author: Claude Code
-- Date: 2026-01-10
-- ════════════════════════════════════════════════════════════════

SET FOREIGN_KEY_CHECKS = 0;

-- ════════════════════════════════════════════════════════════════
-- TABELA: task_execution_flow_sessions
-- ════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS `task_execution_flow_sessions`;

CREATE TABLE `task_execution_flow_sessions` (
  `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `agent_task_spec_session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `agents_yaml_session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tasks_yaml_session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_name` VARCHAR(255) DEFAULT NULL,
  `started_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_at` TIMESTAMP NULL DEFAULT NULL,
  `status` ENUM('generating','completed','failed') DEFAULT 'generating',
  `flow_document` LONGTEXT DEFAULT NULL,
  `total_tasks` INT(10) UNSIGNED DEFAULT 0,
  `has_parallelism` BOOLEAN DEFAULT FALSE,
  `generation_log` LONGTEXT DEFAULT NULL,
  `execution_metadata` LONGTEXT DEFAULT NULL,
  `generation_time_ms` BIGINT(20) UNSIGNED DEFAULT NULL,
  `ai_model_used` VARCHAR(100) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_agent_task_spec_session` (`agent_task_spec_session_id`),
  KEY `idx_agents_yaml_session` (`agents_yaml_session_id`),
  KEY `idx_tasks_yaml_session` (`tasks_yaml_session_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores task execution flow documents with State definitions, input/output functions, and dependency graphs';

-- ════════════════════════════════════════════════════════════════
-- ADD FOREIGN KEYS
-- ════════════════════════════════════════════════════════════════

ALTER TABLE `task_execution_flow_sessions`
  ADD CONSTRAINT `fk_tef_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_tef_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_tef_agent_task_spec` FOREIGN KEY (`agent_task_spec_session_id`) REFERENCES `agent_task_specification_sessions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_tef_agents_yaml` FOREIGN KEY (`agents_yaml_session_id`) REFERENCES `agents_yaml_sessions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_tef_tasks_yaml` FOREIGN KEY (`tasks_yaml_session_id`) REFERENCES `tasks_yaml_sessions` (`id`) ON DELETE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;
