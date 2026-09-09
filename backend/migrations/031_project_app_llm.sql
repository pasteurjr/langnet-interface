-- Modelo de linguagem que a APLICAÇÃO GERADA vai usar — escolha do projeto, não do ambiente.
-- Antes: `projects.default_llm` guardava um rótulo solto ("OpenAI GPT-4") que ninguém lia, e o
-- aplicativo gerado saía sempre com o modelo local no arquivo de ambiente. Agora a escolha fica
-- aqui, é feita pela interface e vai para o pacote gerado.
ALTER TABLE projects
  ADD COLUMN app_llm_config LONGTEXT NULL
  COMMENT 'JSON: {provedor, modelo, endereco, max_tokens} do modelo usado pela aplicação gerada';
