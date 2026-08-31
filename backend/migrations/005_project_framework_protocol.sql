-- 005: Configurações do projeto — framework (amplia opções) + protocolo agêntico
-- Amplia o ENUM de framework para incluir langgraph, openai (SDK) e anthropic (SDK),
-- mantendo crewai como padrão do sistema. Adiciona a coluna `protocol` (default okf — o nosso),
-- com os demais protocolos (mcp, a2a, acp, anp) como opções (mock por ora).

ALTER TABLE projects
  MODIFY framework ENUM('crewai','langchain','langgraph','autogen','openai','anthropic','custom')
  DEFAULT 'crewai';

ALTER TABLE projects
  ADD COLUMN protocol VARCHAR(20) NOT NULL DEFAULT 'okf' AFTER framework;
