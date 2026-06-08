-- ════════════════════════════════════════════════════════════════
-- Migration 017: Persistir agent_task_spec_session_id nas runs de
-- geração de código (usado pelo parser deterministic de tools).
-- ════════════════════════════════════════════════════════════════

ALTER TABLE `code_generation_sessions`
  ADD COLUMN `agent_task_spec_session_id` CHAR(36) CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci DEFAULT NULL
    AFTER `task_execution_flow_session_id`;

CREATE INDEX `idx_cg_ats_session` ON `code_generation_sessions` (`agent_task_spec_session_id`);
