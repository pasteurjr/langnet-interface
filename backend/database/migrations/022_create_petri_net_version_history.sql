-- 022_create_petri_net_version_history.sql
-- Histórico de versões da etapa de Rede de Petri.
-- Camada ADITIVA e não-destrutiva: a rede "viva" continua sendo lida/gravada em
-- projects.project_data (get_project_data / update_project_data). Esta tabela apenas
-- registra snapshots de cada geração/edição/restauração/aprovação, por project_id
-- (a Rede de Petri é por projeto, não por sessão).

CREATE TABLE IF NOT EXISTS petri_net_version_history (
    project_id           VARCHAR(36)  NOT NULL,
    version              INT UNSIGNED NOT NULL,
    petri_net_json       LONGTEXT     NOT NULL,
    created_at           TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
    created_by           VARCHAR(36)  DEFAULT NULL,
    change_type          ENUM('initial_generation','ai_refinement','manual_edit','approval_revision')
                            DEFAULT 'manual_edit',
    change_description   VARCHAR(500) DEFAULT NULL,
    doc_size             INT UNSIGNED DEFAULT NULL,
    is_approved_version  TINYINT(1)   DEFAULT 0,
    PRIMARY KEY (project_id, version),
    KEY idx_pnvh_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
