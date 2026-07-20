-- Rastreabilidade — Backfill de versões de proveniência em artefatos pré-fix
-- Artefatos gerados antes das correções de rastreabilidade têm o VÍNCULO de sessão
-- da fonte, mas o número da VERSÃO em NULL. Aqui preenchemos a versão da fonte que
-- estava VIGENTE na data de criação do artefato (MAX(version) da history da fonte
-- com created_at <= created_at do artefato). Idempotente: só toca em NULLs deriváveis.
--
-- Não deriváveis (deixados NULL de propósito, sem history de onde derivar à época):
--   ui_spec_sessions.data_model_version, code_generation_sessions.task_execution_flow_version
--
-- Nota de collation: os id de sessão diferem entre tabelas (general_ci vs unicode_ci);
-- forçamos COLLATE utf8mb4_general_ci na comparação.

UPDATE data_model_sessions t
SET t.specification_version = (
  SELECT MAX(h.version) FROM specification_version_history h
  WHERE h.specification_session_id COLLATE utf8mb4_general_ci = t.specification_session_id COLLATE utf8mb4_general_ci
    AND h.created_at <= t.created_at)
WHERE t.specification_version IS NULL AND t.specification_session_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM specification_version_history h
    WHERE h.specification_session_id COLLATE utf8mb4_general_ci = t.specification_session_id COLLATE utf8mb4_general_ci
      AND h.created_at <= t.created_at);

UPDATE ui_spec_sessions t
SET t.specification_version = (
  SELECT MAX(h.version) FROM specification_version_history h
  WHERE h.specification_session_id COLLATE utf8mb4_general_ci = t.specification_session_id COLLATE utf8mb4_general_ci
    AND h.created_at <= t.created_at)
WHERE t.specification_version IS NULL AND t.specification_session_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM specification_version_history h
    WHERE h.specification_session_id COLLATE utf8mb4_general_ci = t.specification_session_id COLLATE utf8mb4_general_ci
      AND h.created_at <= t.created_at);

UPDATE code_generation_sessions t
SET t.agents_yaml_version = (
  SELECT MAX(h.version) FROM agents_yaml_version_history h
  WHERE h.session_id COLLATE utf8mb4_general_ci = t.agents_yaml_session_id COLLATE utf8mb4_general_ci
    AND h.created_at <= t.created_at)
WHERE t.agents_yaml_version IS NULL AND t.agents_yaml_session_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM agents_yaml_version_history h
    WHERE h.session_id COLLATE utf8mb4_general_ci = t.agents_yaml_session_id COLLATE utf8mb4_general_ci
      AND h.created_at <= t.created_at);

UPDATE code_generation_sessions t
SET t.tasks_yaml_version = (
  SELECT MAX(h.version) FROM tasks_yaml_version_history h
  WHERE h.session_id COLLATE utf8mb4_general_ci = t.tasks_yaml_session_id COLLATE utf8mb4_general_ci
    AND h.created_at <= t.created_at)
WHERE t.tasks_yaml_version IS NULL AND t.tasks_yaml_session_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM tasks_yaml_version_history h
    WHERE h.session_id COLLATE utf8mb4_general_ci = t.tasks_yaml_session_id COLLATE utf8mb4_general_ci
      AND h.created_at <= t.created_at);

UPDATE code_generation_sessions t
SET t.agent_task_spec_version = (
  SELECT MAX(h.version) FROM agent_task_spec_version_history h
  WHERE h.session_id COLLATE utf8mb4_general_ci = t.agent_task_spec_session_id COLLATE utf8mb4_general_ci
    AND h.created_at <= t.created_at)
WHERE t.agent_task_spec_version IS NULL AND t.agent_task_spec_session_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM agent_task_spec_version_history h
    WHERE h.session_id COLLATE utf8mb4_general_ci = t.agent_task_spec_session_id COLLATE utf8mb4_general_ci
      AND h.created_at <= t.created_at);
