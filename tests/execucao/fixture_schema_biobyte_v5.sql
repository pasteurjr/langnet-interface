SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `usuarios` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `nome` VARCHAR(200) NOT NULL DEFAULT '',
    `email` VARCHAR(200) NOT NULL,
    `senha_hash` VARCHAR(255) NOT NULL DEFAULT '',
    `senha_sal` VARCHAR(64) NOT NULL DEFAULT '',
    `papel` ENUM('medico', 'enfermeiro', 'administrador') NOT NULL,
    `ativo` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_usuarios_email` (`email`),
    INDEX `idx_usuarios_papel` (`papel`),
    INDEX `idx_usuarios_ativo` (`ativo`)
) COMMENT='Pessoa que acessa o sistema; possui nome, e-mail, senha (hash+sal), papel e indicador de ativo.';

CREATE TABLE `pacientes` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `nome` VARCHAR(200) NOT NULL DEFAULT '',
    `data_nascimento` DATE NOT NULL,
    `sexo` ENUM('M', 'F', 'outro') NOT NULL,
    `numero_prontuario` VARCHAR(50) NOT NULL,
    `medico_responsavel_id` CHAR(36),
    `uuid_anonimo` CHAR(36) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_pacientes_numero_prontuario` (`numero_prontuario`),
    UNIQUE INDEX `idx_pacientes_uuid_anonimo` (`uuid_anonimo`),
    INDEX `idx_pacientes_medico_responsavel_id` (`medico_responsavel_id`),
    INDEX `idx_pacientes_nome` (`nome`),
    FOREIGN KEY (`medico_responsavel_id`) REFERENCES usuarios(id) ON DELETE RESTRICT
) COMMENT='Pessoa com cateter venoso central; possui nome, data de nascimento, sexo, número do prontuário e médico responsável.';

CREATE TABLE `casos_clinicos` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `paciente_id` CHAR(36) NOT NULL,
    `data_inicio` DATE NOT NULL,
    `data_encerramento` DATE,
    `estado` ENUM('ativo', 'encerrado') NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_casos_clinicos_paciente_id` (`paciente_id`),
    INDEX `idx_casos_clinicos_estado` (`estado`),
    INDEX `idx_casos_clinicos_data_inicio` (`data_inicio`),
    FOREIGN KEY (`paciente_id`) REFERENCES pacientes(id) ON DELETE CASCADE
) COMMENT='Episódio do paciente com cateter; possui data de início, data de encerramento opcional e estado (ativo/encerrado).';

CREATE TABLE `sitios_insercao` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `nome` ENUM('jugular_interna', 'subclavia', 'femoral') NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_sitios_insercao_nome` (`nome`)
) COMMENT='Enumeração dos sítios de inserção do cateter.';

CREATE TABLE `faixas_risco` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `nome` ENUM('baixo', 'moderado', 'alto') NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_faixas_risco_nome` (`nome`)
) COMMENT='Enumeração das faixas de risco.';

CREATE TABLE `dados_risco` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `idade_na_data` INTEGER NOT NULL DEFAULT 0,
    `dias_cateter` INTEGER NOT NULL DEFAULT 0,
    `apache_ii` INTEGER NOT NULL DEFAULT 0,
    `sitio_insercao_id` CHAR(36) NOT NULL,
    `comorbidades_relevantes` TEXT NOT NULL DEFAULT (''),
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_dados_risco_caso_id` (`caso_id`),
    INDEX `idx_dados_risco_sitio_insercao_id` (`sitio_insercao_id`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE,
    FOREIGN KEY (`sitio_insercao_id`) REFERENCES sitios_insercao(id) ON DELETE RESTRICT
) COMMENT='Conjunto dos cinco dados de risco associados a um caso clínico.';

CREATE TABLE `escores_cox` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `escore` NUMERIC NOT NULL DEFAULT 0,
    `faixa_risco_id` CHAR(36) NOT NULL,
    `preditor_linear` NUMERIC NOT NULL DEFAULT 0,
    `fatores_peso` JSON,
    `versao_modelo` VARCHAR(200) NOT NULL DEFAULT '',
    `data_calculo` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_escores_cox_caso_id` (`caso_id`),
    INDEX `idx_escores_cox_faixa_risco_id` (`faixa_risco_id`),
    INDEX `idx_escores_cox_data_calculo` (`data_calculo`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE,
    FOREIGN KEY (`faixa_risco_id`) REFERENCES faixas_risco(id) ON DELETE RESTRICT
) COMMENT='Resultado do serviço externo — escore, faixa de risco, preditor linear, fatores que pesaram, versão do modelo e data do cálculo.';

CREATE TABLE `resultados_hemocultura` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `situacao` ENUM('pendente', 'disponivel', 'erro') NOT NULL,
    `identificador_amostra` VARCHAR(100) NOT NULL DEFAULT '',
    `origem` ENUM('hemocultura', 'ponta_cateter', 'outra') NOT NULL,
    `microrganismo` VARCHAR(200),
    `multirresistente` TINYINT(1),
    `mensagem_erro` TEXT,
    `importado_em` TIMESTAMP NOT NULL,
    `hash_resultado` VARCHAR(64) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_resultados_hemocultura_caso_id` (`caso_id`),
    INDEX `idx_resultados_hemocultura_situacao` (`situacao`),
    INDEX `idx_resultados_hemocultura_origem` (`origem`),
    INDEX `idx_resultados_hemocultura_importado_em` (`importado_em`),
    UNIQUE INDEX `idx_resultados_hemocultura_hash_resultado` (`hash_resultado`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE
) COMMENT='Retorno do laboratório — situação, identificador da amostra, origem, microrganismo, indicação de multirresistência e antibiograma.';

CREATE TABLE `antimicrobianos` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `nome` VARCHAR(200) NOT NULL,
    `classe` VARCHAR(100) NOT NULL DEFAULT '',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_antimicrobianos_nome` (`nome`),
    INDEX `idx_antimicrobianos_classe` (`classe`)
) COMMENT='Catálogo de antimicrobianos e suas classes.';

CREATE TABLE `antibiogramas` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `resultado_hemocultura_id` CHAR(36) NOT NULL,
    `antimicrobiano_id` CHAR(36) NOT NULL,
    `resultado` ENUM('sensivel', 'intermediario', 'resistente') NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_antibiogramas_resultado_hemocultura_id` (`resultado_hemocultura_id`),
    INDEX `idx_antibiogramas_antimicrobiano_id` (`antimicrobiano_id`),
    UNIQUE INDEX `idx_antibiogramas_resultado_hemocultura_antimicrobiano` (`resultado_hemocultura_id`, `antimicrobiano_id`),
    FOREIGN KEY (`resultado_hemocultura_id`) REFERENCES resultados_hemocultura(id) ON DELETE CASCADE,
    FOREIGN KEY (`antimicrobiano_id`) REFERENCES antimicrobianos(id) ON DELETE RESTRICT
) COMMENT='Resultado de sensibilidade para cada antimicrobiano testado em um resultado de hemocultura.';

CREATE TABLE `criterios_nhsn` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `versao` VARCHAR(120) NOT NULL,
    `nome` VARCHAR(200) NOT NULL DEFAULT '',
    `limiares` JSON NOT NULL,
    `vigencia_inicio` DATE NOT NULL,
    `vigencia_fim` DATE,
    `criado_por` CHAR(36) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_criterios_nhsn_versao` (`versao`),
    INDEX `idx_criterios_nhsn_criado_por` (`criado_por`),
    INDEX `idx_criterios_nhsn_vigencia_inicio` (`vigencia_inicio`),
    INDEX `idx_criterios_nhsn_vigencia_fim` (`vigencia_fim`),
    FOREIGN KEY (`criado_por`) REFERENCES usuarios(id) ON DELETE RESTRICT
) COMMENT='Versão, nome, limiares e período de vigência do critério NHSN.';

CREATE TABLE `classificacoes` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `resultado` ENUM('confirmada', 'descartada', 'pendente') NOT NULL,
    `criterio_id` CHAR(36) NOT NULL,
    `assinado_por` CHAR(36) NOT NULL,
    `sobrescrita` TINYINT(1) NOT NULL DEFAULT 0,
    `justificativa` TEXT,
    `decidido_por_agente` TINYINT(1) NOT NULL DEFAULT 0,
    `data_decisao` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_classificacoes_caso_id` (`caso_id`),
    INDEX `idx_classificacoes_criterio_id` (`criterio_id`),
    INDEX `idx_classificacoes_assinado_por` (`assinado_por`),
    INDEX `idx_classificacoes_resultado` (`resultado`),
    INDEX `idx_classificacoes_data_decisao` (`data_decisao`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE,
    FOREIGN KEY (`criterio_id`) REFERENCES criterios_nhsn(id) ON DELETE RESTRICT,
    FOREIGN KEY (`assinado_por`) REFERENCES usuarios(id) ON DELETE RESTRICT
) COMMENT='Resultado (confirmada, descartada, pendente), critério aplicado, ator que assinou e justificativa (quando sobrescrita).';

CREATE TABLE `alertas` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `tipo` VARCHAR(100) NOT NULL DEFAULT '',
    `gravidade` ENUM('baixa', 'media', 'alta') NOT NULL,
    `situacao` ENUM('aberto', 'reconhecido', 'encerrado') NOT NULL,
    `texto_gerado` TEXT NOT NULL DEFAULT (''),
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_alertas_caso_id` (`caso_id`),
    INDEX `idx_alertas_gravidade` (`gravidade`),
    INDEX `idx_alertas_situacao` (`situacao`),
    INDEX `idx_alertas_created_at` (`created_at`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE
) COMMENT='Tipo, gravidade, situação (aberto, reconhecido, encerrado) e texto gerado (agêntico).';

CREATE TABLE `notificacoes` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `alerta_id` CHAR(36) NOT NULL,
    `destinatario` VARCHAR(200) NOT NULL DEFAULT '',
    `canal` ENUM('email') NOT NULL,
    `status` ENUM('pendente', 'enviada', 'falha') NOT NULL,
    `tempo_decorrido_ms` INTEGER,
    `mensagem_falha` TEXT,
    `tentativas` INTEGER NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_notificacoes_alerta_id` (`alerta_id`),
    INDEX `idx_notificacoes_status` (`status`),
    INDEX `idx_notificacoes_destinatario` (`destinatario`),
    FOREIGN KEY (`alerta_id`) REFERENCES alertas(id) ON DELETE CASCADE
) COMMENT='Destinatário, canal, status, tempo decorrido e mensagem de falha (quando houver).';

CREATE TABLE `bundles` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `nome` VARCHAR(200) NOT NULL,
    `indicacao` TEXT NOT NULL DEFAULT (''),
    `reducao_media_risco` DECIMAL(5,2) NOT NULL DEFAULT 0,
    `intervalo_confianca` VARCHAR(50),
    `ativo` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_bundles_nome` (`nome`),
    INDEX `idx_bundles_ativo` (`ativo`)
) COMMENT='Nome, indicação, redução média de risco e intervalo de confiança.';

CREATE TABLE `recomendacoes` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `bundle_recomendado_id` CHAR(36),
    `justificativa` TEXT NOT NULL DEFAULT (''),
    `decisao_agente` ENUM('recomendar', 'insuficiente') NOT NULL,
    `escolha_medica_bundle_id` CHAR(36),
    `data` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_recomendacoes_caso_id` (`caso_id`),
    INDEX `idx_recomendacoes_bundle_recomendado_id` (`bundle_recomendado_id`),
    INDEX `idx_recomendacoes_escolha_medica_bundle_id` (`escolha_medica_bundle_id`),
    INDEX `idx_recomendacoes_decisao_agente` (`decisao_agente`),
    INDEX `idx_recomendacoes_data` (`data`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE,
    FOREIGN KEY (`bundle_recomendado_id`) REFERENCES bundles(id) ON DELETE RESTRICT,
    FOREIGN KEY (`escolha_medica_bundle_id`) REFERENCES bundles(id) ON DELETE RESTRICT
) COMMENT='Bundle sugerido pelo sistema, justificativa textual, decisão do agente (recomendar/insuficiente) e escolha médica (quando divergente).';

CREATE TABLE `estimativas_reducao_risco` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `horizonte_dias` ENUM('30', '90', '180') NOT NULL,
    `reducao_absoluta` NUMERIC NOT NULL DEFAULT 0,
    `reducao_relativa` NUMERIC NOT NULL DEFAULT 0,
    `intervalo_confianca` VARCHAR(50),
    `data_calculo` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_estimativas_reducao_risco_caso_id` (`caso_id`),
    INDEX `idx_estimativas_reducao_risco_horizonte_dias` (`horizonte_dias`),
    INDEX `idx_estimativas_reducao_risco_data_calculo` (`data_calculo`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE
) COMMENT='Redução absoluta, redução relativa, intervalo de confiança e horizonte (30/90/180 dias).';

CREATE TABLE `ciclos_integrados` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `etapas_status` JSON NOT NULL,
    `resultado_por_etapa` JSON NOT NULL,
    `iniciado_em` TIMESTAMP NOT NULL,
    `concluido_em` TIMESTAMP,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_ciclos_integrados_caso_id` (`caso_id`),
    INDEX `idx_ciclos_integrados_iniciado_em` (`iniciado_em`),
    INDEX `idx_ciclos_integrados_concluido_em` (`concluido_em`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE
) COMMENT='Execução da sequência de seis etapas com status e resultado por etapa.';

CREATE TABLE `paineis_vigilancia` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `periodo_dias` ENUM('7', '30', '90', '365') NOT NULL,
    `casos_ativos` INTEGER NOT NULL DEFAULT 0,
    `escore_medio` DECIMAL(5,2),
    `classificacoes_nhsn` JSON,
    `alertas_abertos` INTEGER NOT NULL DEFAULT 0,
    `conformidade_mensal` DECIMAL(5,2),
    `distribuicao_faixa` JSON,
    `data_consulta` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_paineis_vigilancia_periodo_dias` (`periodo_dias`),
    INDEX `idx_paineis_vigilancia_data_consulta` (`data_consulta`)
) COMMENT='Agregação por período — casos ativos, escore médio, classificações NHSN, alertas abertos, conformidade mensal e distribuição por faixa.';

CREATE TABLE `relatorios_vigilancia` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `periodo_dias` ENUM('7', '30', '90', '365') NOT NULL,
    `formato` ENUM('PDF', 'CSV') NOT NULL,
    `filtro_paciente_id` CHAR(36),
    `quantidade_registros` INTEGER NOT NULL DEFAULT 0,
    `conteudo` TEXT,
    `data_geracao` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_relatorios_vigilancia_filtro_paciente_id` (`filtro_paciente_id`),
    INDEX `idx_relatorios_vigilancia_periodo_dias` (`periodo_dias`),
    INDEX `idx_relatorios_vigilancia_formato` (`formato`),
    INDEX `idx_relatorios_vigilancia_data_geracao` (`data_geracao`),
    FOREIGN KEY (`filtro_paciente_id`) REFERENCES pacientes(id) ON DELETE RESTRICT
) COMMENT='Exportação em PDF/CSV por período, filtrável por paciente.';

CREATE TABLE `logs_auditoria` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `usuario_id` CHAR(36) NOT NULL,
    `acao` VARCHAR(100) NOT NULL DEFAULT '',
    `registro_afetado` VARCHAR(200) NOT NULL DEFAULT '',
    `data_hora` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `hash_anterior` VARCHAR(64),
    `hash_atual` VARCHAR(64) NOT NULL DEFAULT '',
    `correlation_id` CHAR(36),
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_logs_auditoria_usuario_id` (`usuario_id`),
    INDEX `idx_logs_auditoria_data_hora` (`data_hora`),
    INDEX `idx_logs_auditoria_correlation_id` (`correlation_id`),
    FOREIGN KEY (`usuario_id`) REFERENCES usuarios(id) ON DELETE RESTRICT
) COMMENT='Visão consultável da trilha, com filtros.';

CREATE TABLE `trilhas_auditoria` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `usuario_id` CHAR(36) NOT NULL,
    `acao` VARCHAR(100) NOT NULL DEFAULT '',
    `registro_afetado` VARCHAR(200) NOT NULL DEFAULT '',
    `data_hora` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `hash_anterior` VARCHAR(64),
    `hash_atual` VARCHAR(64) NOT NULL DEFAULT '',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_trilhas_auditoria_usuario_id` (`usuario_id`),
    INDEX `idx_trilhas_auditoria_data_hora` (`data_hora`),
    FOREIGN KEY (`usuario_id`) REFERENCES usuarios(id) ON DELETE RESTRICT
) COMMENT='Registro convencional do sistema, sem uso de agente de IA.';

CREATE TABLE `tokens_acesso` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `usuario_id` CHAR(36) NOT NULL,
    `token` VARCHAR(500) NOT NULL,
    `emitido_em` TIMESTAMP NOT NULL,
    `expira_em` TIMESTAMP NOT NULL,
    `assinatura` VARCHAR(255) NOT NULL DEFAULT '',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_tokens_acesso_usuario_id` (`usuario_id`),
    UNIQUE INDEX `idx_tokens_acesso_token` (`token`),
    INDEX `idx_tokens_acesso_expira_em` (`expira_em`),
    FOREIGN KEY (`usuario_id`) REFERENCES usuarios(id) ON DELETE CASCADE
) COMMENT='Credencial emitida no login, com validade e assinatura.';

CREATE TABLE `credenciais_servicos_externos` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `servico` VARCHAR(100) NOT NULL,
    `credencial` VARCHAR(255) NOT NULL DEFAULT '',
    `rotacionado_em` TIMESTAMP,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `idx_credenciais_servicos_externos_servico` (`servico`)
) COMMENT='Armazenadas em cofre de segredos, com rotação.';

CREATE TABLE `decisoes_sistema` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `tipo` ENUM('risco', 'classificacao', 'conduta') NOT NULL,
    `caso_id` CHAR(36) NOT NULL,
    `origem_dado` VARCHAR(200) NOT NULL DEFAULT '',
    `valor` JSON NOT NULL,
    `data` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_decisoes_sistema_caso_id` (`caso_id`),
    INDEX `idx_decisoes_sistema_tipo` (`tipo`),
    INDEX `idx_decisoes_sistema_data` (`data`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE
) COMMENT='Registro de risco, classificação ou conduta, rastreável até a origem do dado.';

CREATE TABLE `resultados_laboratorio_brutos` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `caso_id` CHAR(36) NOT NULL,
    `payload_bruto` JSON NOT NULL,
    `situacao` ENUM('pendente', 'disponivel', 'erro') NOT NULL,
    `importado_em` TIMESTAMP NOT NULL,
    `hash_resultado` VARCHAR(64) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_resultados_laboratorio_brutos_caso_id` (`caso_id`),
    INDEX `idx_resultados_laboratorio_brutos_situacao` (`situacao`),
    INDEX `idx_resultados_laboratorio_brutos_importado_em` (`importado_em`),
    UNIQUE INDEX `idx_resultados_laboratorio_brutos_hash_resultado` (`hash_resultado`),
    FOREIGN KEY (`caso_id`) REFERENCES casos_clinicos(id) ON DELETE CASCADE
) COMMENT='Formato próprio do laboratório, podendo vir pendente ou com erro.';

CREATE TABLE `pacotes_bundle_aplicado` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `recomendacao_id` CHAR(36) NOT NULL,
    `bundle_id` CHAR(36) NOT NULL,
    `aplicado_em` TIMESTAMP NOT NULL,
    `justificativa` TEXT,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_pacotes_bundle_aplicado_recomendacao_id` (`recomendacao_id`),
    INDEX `idx_pacotes_bundle_aplicado_bundle_id` (`bundle_id`),
    INDEX `idx_pacotes_bundle_aplicado_aplicado_em` (`aplicado_em`),
    UNIQUE INDEX `idx_pacotes_bundle_aplicado_recomendacao_bundle` (`recomendacao_id`, `bundle_id`),
    FOREIGN KEY (`recomendacao_id`) REFERENCES recomendacoes(id) ON DELETE CASCADE,
    FOREIGN KEY (`bundle_id`) REFERENCES bundles(id) ON DELETE RESTRICT
) COMMENT='Conjunto recomendado pelo agente, com justificativa.';

CREATE TABLE `registros_auditoria` (
    `id` CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `usuario_id` CHAR(36) NOT NULL,
    `acao` VARCHAR(100) NOT NULL DEFAULT '',
    `registro_afetado` VARCHAR(200) NOT NULL DEFAULT '',
    `dados_antes` JSON,
    `dados_depois` JSON,
    `data_hora` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `hash_anterior` VARCHAR(64),
    `hash_atual` VARCHAR(64) NOT NULL DEFAULT '',
    `correlation_id` CHAR(36),
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_registros_auditoria_usuario_id` (`usuario_id`),
    INDEX `idx_registros_auditoria_data_hora` (`data_hora`),
    INDEX `idx_registros_auditoria_correlation_id` (`correlation_id`),
    FOREIGN KEY (`usuario_id`) REFERENCES usuarios(id) ON DELETE RESTRICT
) COMMENT='Entrada encadeada da trilha de auditoria; possui usuário, ação, registro afetado, data/hora e hash da entrada anterior.';

SET FOREIGN_KEY_CHECKS=1;
