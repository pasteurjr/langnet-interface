-- Rastreabilidade Etapa 3: proveniência da Rede de Petri
-- Registra, por versão da rede, QUAL sessão e QUAL versão de cada fonte a produziu:
--   agents.yaml, tasks.yaml e Sequência de Tarefas (task_execution_flow).
-- Aditivo e backward-compatible: colunas NULL (versões antigas ficam sem proveniência).

ALTER TABLE petri_net_version_history
  ADD COLUMN agents_yaml_session_id          VARCHAR(36)  NULL,
  ADD COLUMN agents_yaml_version             INT UNSIGNED NULL,
  ADD COLUMN tasks_yaml_session_id           VARCHAR(36)  NULL,
  ADD COLUMN tasks_yaml_version              INT UNSIGNED NULL,
  ADD COLUMN task_execution_flow_session_id  VARCHAR(36)  NULL,
  ADD COLUMN task_execution_flow_version     INT UNSIGNED NULL;
