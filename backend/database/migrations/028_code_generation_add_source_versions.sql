-- Rastreabilidade Etapa 4: proveniência da Geração de Código
-- code_generation_sessions já guarda os IDs das 4 fontes de sessão, mas não a
-- VERSÃO de cada uma, nem qual Rede de Petri e quais telas (ui_spec) foram usadas.
-- Estas colunas fecham a cadeia de rastreabilidade até o código gerado.
-- Aditivo/backward-compatible: colunas NULL.

ALTER TABLE code_generation_sessions
  ADD COLUMN agents_yaml_version            INT UNSIGNED NULL,
  ADD COLUMN tasks_yaml_version             INT UNSIGNED NULL,
  ADD COLUMN task_execution_flow_version    INT UNSIGNED NULL,
  ADD COLUMN agent_task_spec_version        INT UNSIGNED NULL,
  ADD COLUMN petri_net_version              INT UNSIGNED NULL,
  ADD COLUMN ui_spec_session_id            VARCHAR(36)  NULL,
  ADD COLUMN ui_spec_version                INT UNSIGNED NULL;
