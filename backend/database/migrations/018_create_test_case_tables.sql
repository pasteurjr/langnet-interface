-- 018_create_test_case_tables.sql
-- Casos de Teste por Grafo de Causa-Efeito (CEG) — método do artigo do Pasteur Ottoni.
-- Uma sessão guarda os grafos causa-efeito + tabelas de decisão + casos de teste de
-- todos os casos de uso de uma especificação. execution_json é preenchido pelo executor
-- (fase seguinte) com o resultado esperado×obtido de cada caso rodado contra a app.

CREATE TABLE IF NOT EXISTS test_case_sessions (
    id                        VARCHAR(36) NOT NULL PRIMARY KEY,
    project_id                VARCHAR(36) NOT NULL,
    user_id                   VARCHAR(36),
    specification_session_id  VARCHAR(36),
    version                   INT(11)     DEFAULT 1,
    status                    VARCHAR(30) DEFAULT 'draft',   -- draft | generating | executed | approved
    results_json              LONGTEXT,                      -- {"results":[{uc,name,ceg,decision_table,test_cases,...}]}
    execution_json            LONGTEXT,                      -- resultado da execução (esperado×obtido) — fase executor
    validation_document       LONGTEXT,                      -- Documento de Validação (HTML) persistido na geração/refino
    total_ucs                 INT(11)     DEFAULT 0,
    total_cases               INT(11)     DEFAULT 0,
    generation_log            TEXT,
    created_at                TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    executed_at               TIMESTAMP   NULL,
    KEY idx_tcs_project (project_id),
    KEY idx_tcs_status (status),
    KEY idx_tcs_spec (specification_session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
