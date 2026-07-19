-- 020_create_test_case_version_history.sql
-- Histórico de versões da etapa de Casos de Teste (CEG).
-- Cada versão guarda um snapshot completo dos resultados (results_json) + o Documento
-- de Validação (validation_document) daquele momento. Espelha
-- specification_version_history / task_execution_flow_version_history, mas para esta
-- etapa. A coluna test_case_sessions.version fica em sincronia com o MAX(version) aqui.

CREATE TABLE IF NOT EXISTS test_case_version_history (
    session_id           VARCHAR(36)  NOT NULL,
    version              INT UNSIGNED NOT NULL,
    results_json         LONGTEXT,                 -- snapshot completo dos resultados {"results":[...]}
    validation_document  LONGTEXT,                 -- Documento de Validação (HTML) daquela versão
    created_at           TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
    created_by           VARCHAR(36)  DEFAULT NULL,
    change_type          ENUM('initial_generation','ai_refinement','manual_edit','approval_revision')
                            DEFAULT 'manual_edit',
    change_description   VARCHAR(500) DEFAULT NULL,
    doc_size             INT UNSIGNED DEFAULT NULL, -- tamanho do results_json snapshot
    PRIMARY KEY (session_id, version),
    KEY idx_tcvh_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
