-- 023_data_model_add_specification_version.sql
-- Rastreabilidade (ETAPA 1): a etapa de Modelo de Dados passa a persistir QUAL versão
-- da Especificação foi consumida na geração (não apenas o specification_session_id).
-- Aditivo e não-destrutivo: linhas existentes ficam com NULL.

ALTER TABLE data_model_sessions
    ADD COLUMN specification_version INT UNSIGNED NULL;
