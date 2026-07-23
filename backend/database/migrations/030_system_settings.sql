-- F1 — Configurações do Sistema reais (UC-P01)
-- Persiste config editável pela UI (banco de dados, provedor LLM, integrações).
-- Segredos (senha de banco, API keys) NUNCA são retornados em claro pela API;
-- a flag is_secret marca quais valores devem ser mascarados na leitura.

CREATE TABLE IF NOT EXISTS system_settings (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  section       VARCHAR(50)  NOT NULL,        -- 'database' | 'llm' | 'integrations' | ...
  setting_key   VARCHAR(100) NOT NULL,        -- ex.: 'db_host', 'lmstudio_model_name'
  setting_value TEXT,
  is_secret     TINYINT(1)   NOT NULL DEFAULT 0,
  updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by    VARCHAR(36),
  UNIQUE KEY uq_section_key (section, setting_key)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
