-- 024_test_case_add_specification_version.sql
-- Rastreabilidade (ETAPA 1): a etapa de Casos de Teste (CEG) passa a persistir QUAL versão
-- da Especificação foi consumida na geração (não apenas o specification_session_id).
-- Aditivo e não-destrutivo: linhas existentes ficam com NULL.

ALTER TABLE test_case_sessions
    ADD COLUMN specification_version INT UNSIGNED NULL;
