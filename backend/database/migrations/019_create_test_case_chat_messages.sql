-- 019_create_test_case_chat_messages.sql
-- Histórico de refino pelo agente na etapa de Casos de Teste (CEG).
-- Cada refino via chat ajusta o grafo causa-efeito de um UC, regenera os casos e
-- sobe a versão da sessão (test_case_sessions.version). Segue o mesmo padrão de
-- data_model_chat_messages / ui_spec_chat_messages.

CREATE TABLE IF NOT EXISTS test_case_chat_messages (
    id                    VARCHAR(36) NOT NULL PRIMARY KEY,
    test_case_session_id  VARCHAR(36) NOT NULL,
    role                  VARCHAR(20) NOT NULL,   -- user | assistant
    content               TEXT,
    uc_id                 VARCHAR(20),            -- UC alvo do ajuste (ex.: UC-004)
    created_at            TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_tccm_session (test_case_session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
