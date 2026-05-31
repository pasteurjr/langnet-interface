-- ════════════════════════════════════════════════════════════════
-- Migration 016: Code Generation Tables
-- ════════════════════════════════════════════════════════════════
-- Purpose: Sessions, version history e chat para a fase de
--          geração de código Python compatível com o framework
--          visualtasksexec (CrewAI + LangChain + WebSocket).
-- ════════════════════════════════════════════════════════════════

SET FOREIGN_KEY_CHECKS = 0;

-- ────────────────────────────────────────────────────────────────
-- TABELA: code_generation_sessions
-- ────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS `code_generation_chat_messages`;
DROP TABLE IF EXISTS `code_generation_version_history`;
DROP TABLE IF EXISTS `code_generation_sessions`;

CREATE TABLE `code_generation_sessions` (
  `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `agents_yaml_session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tasks_yaml_session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `task_execution_flow_session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `websocket_port` INT(10) UNSIGNED NOT NULL DEFAULT 5002,
  `session_name` VARCHAR(255) DEFAULT NULL,
  `status` ENUM('generating','completed','failed') NOT NULL DEFAULT 'generating',
  `generated_files` LONGTEXT DEFAULT NULL COMMENT 'JSON array [{path, content, language?}]',
  `generation_log` LONGTEXT DEFAULT NULL,
  `current_version` INT(10) UNSIGNED NOT NULL DEFAULT 1,
  `total_files` INT(10) UNSIGNED DEFAULT 0,
  `execution_metadata` LONGTEXT DEFAULT NULL,
  `generation_time_ms` BIGINT(20) UNSIGNED DEFAULT NULL,
  `ai_model_used` VARCHAR(100) DEFAULT NULL,
  `started_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_at` TIMESTAMP NULL DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cg_project` (`project_id`),
  KEY `idx_cg_user` (`user_id`),
  KEY `idx_cg_status` (`status`),
  KEY `idx_cg_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Sessions de geração de código Python multi-arquivo para o framework agêntico';

-- ────────────────────────────────────────────────────────────────
-- TABELA: code_generation_version_history
-- ────────────────────────────────────────────────────────────────

CREATE TABLE `code_generation_version_history` (
  `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` INT(10) UNSIGNED NOT NULL,
  `generated_files` LONGTEXT DEFAULT NULL COMMENT 'snapshot JSON dos files dessa versão',
  `created_by` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `change_type` ENUM('initial','refine','manual_edit','restore') DEFAULT 'initial',
  `change_description` TEXT DEFAULT NULL,
  `total_files` INT(10) UNSIGNED DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_session_version` (`session_id`, `version`),
  KEY `idx_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Versão history de cada sessão de code generation';

-- ────────────────────────────────────────────────────────────────
-- TABELA: code_generation_chat_messages
-- ────────────────────────────────────────────────────────────────

CREATE TABLE `code_generation_chat_messages` (
  `id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_id` CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_type` ENUM('user','assistant','system') NOT NULL,
  `message_text` LONGTEXT DEFAULT NULL,
  `message_data` LONGTEXT DEFAULT NULL COMMENT 'JSON: {has_diff, old_files, new_files, affected_paths}',
  `message_type` VARCHAR(50) NOT NULL DEFAULT 'chat',
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cgcm_session` (`session_id`),
  KEY `idx_cgcm_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Chat de refinamento da geração de código';

-- ────────────────────────────────────────────────────────────────
-- FOREIGN KEYS
-- ────────────────────────────────────────────────────────────────

ALTER TABLE `code_generation_sessions`
  ADD CONSTRAINT `fk_cg_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_cg_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `code_generation_version_history`
  ADD CONSTRAINT `fk_cgvh_session` FOREIGN KEY (`session_id`) REFERENCES `code_generation_sessions` (`id`) ON DELETE CASCADE;

ALTER TABLE `code_generation_chat_messages`
  ADD CONSTRAINT `fk_cgcm_session` FOREIGN KEY (`session_id`) REFERENCES `code_generation_sessions` (`id`) ON DELETE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;
