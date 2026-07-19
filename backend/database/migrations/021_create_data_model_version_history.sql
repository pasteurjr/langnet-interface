-- 021_create_data_model_version_history.sql
-- Histórico de versões da etapa de Modelo de Dados.
-- Cada versão guarda um snapshot completo dos artefatos (data_model_yaml, schema_sql,
-- models_py, alembic_migration, entities_json, validation_report) daquele momento.
-- Espelha test_case_version_history / specification_version_history, mas para esta
-- etapa. A coluna data_model_sessions.version fica em sincronia com o MAX(version) aqui.

CREATE TABLE IF NOT EXISTS data_model_version_history (
    session_id           VARCHAR(36)  NOT NULL,
    version              INT UNSIGNED NOT NULL,
    data_model_yaml      LONGTEXT,
    schema_sql           LONGTEXT,
    models_py            LONGTEXT,
    alembic_migration    LONGTEXT,
    entities_json        LONGTEXT,
    validation_report    LONGTEXT,
    created_at           TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
    created_by           VARCHAR(36)  DEFAULT NULL,
    change_type          ENUM('initial_generation','ai_refinement','manual_edit','approval_revision')
                            DEFAULT 'manual_edit',
    change_description   VARCHAR(500) DEFAULT NULL,
    doc_size             INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (session_id, version),
    KEY idx_dmvh_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
