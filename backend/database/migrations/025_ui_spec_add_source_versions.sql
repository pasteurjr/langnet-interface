-- 025_ui_spec_add_source_versions.sql
-- Rastreabilidade (ETAPA 1): a etapa de UI Spec passa a persistir QUAIS versões das fontes
-- foram consumidas na geração: a versão da Especificação e a versão do Modelo de Dados
-- efetivamente usado (incluindo o auto-descoberto mais recente do projeto).
-- Aditivo e não-destrutivo: linhas existentes ficam com NULL.

ALTER TABLE ui_spec_sessions
    ADD COLUMN specification_version INT UNSIGNED NULL,
    ADD COLUMN data_model_version   INT UNSIGNED NULL;
