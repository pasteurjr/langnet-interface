-- 026_task_execution_flow_add_source_versions.sql
-- Rastreabilidade (ETAPA 2): a etapa de Sequência de Tarefas (task execution flow) passa a
-- persistir QUAIS versões das fontes foram consumidas na geração:
--   - a versão da Especificação Funcional (specification_version_history)
--   - a versão da Especificação de Agentes/Tarefas (agent_task_spec_version_history)
--   - a versão do tasks.yaml (tasks_yaml_version_history)
-- Aditivo e não-destrutivo: linhas existentes ficam com NULL.

ALTER TABLE task_execution_flow_sessions
    ADD COLUMN specification_version   INT UNSIGNED NULL,
    ADD COLUMN agent_task_spec_version INT UNSIGNED NULL,
    ADD COLUMN tasks_yaml_version      INT UNSIGNED NULL;
