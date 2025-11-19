-- ============================================================
-- Tabela: chat_messages
-- Descrição: Armazena mensagens de chat das sessões de execução
-- Criado em: 2025-01-19
-- ============================================================

CREATE TABLE IF NOT EXISTS `chat_messages` (
  -- Identificação
  `id` CHAR(36) NOT NULL DEFAULT (UUID())
    COMMENT 'ID único da mensagem',

  -- Relacionamentos
  `session_id` CHAR(36) NOT NULL
    COMMENT 'ID da sessão de execução',

  `task_execution_id` CHAR(36) NULL
    COMMENT 'ID da execução da task (opcional - para mensagens específicas de tasks)',

  `agent_id` VARCHAR(255) NULL
    COMMENT 'ID do agente que enviou a mensagem (se aplicável)',

  -- Conteúdo da mensagem
  `sender_type` ENUM('user', 'agent', 'system', 'assistant') NOT NULL DEFAULT 'system'
    COMMENT 'Tipo de remetente da mensagem',

  `sender_name` VARCHAR(255) NULL
    COMMENT 'Nome do remetente (nome do agente ou usuário)',

  `message_text` TEXT NOT NULL
    COMMENT 'Conteúdo da mensagem',

  `message_type` ENUM('chat', 'status', 'progress', 'result', 'error', 'warning', 'info', 'document') NOT NULL DEFAULT 'chat'
    COMMENT 'Tipo/categoria da mensagem',

  -- Metadados
  `timestamp` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
    COMMENT 'Timestamp da mensagem com milissegundos',

  `sequence_number` INT UNSIGNED NULL
    COMMENT 'Número de sequência na sessão (para ordenação)',

  `parent_message_id` CHAR(36) NULL
    COMMENT 'ID da mensagem pai (para threads/respostas)',

  `metadata` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL
    COMMENT 'Metadados adicionais em JSON (attachments, formatting, etc)',

  -- Flags de controle
  `is_read` TINYINT(1) DEFAULT 0
    COMMENT 'Se a mensagem foi lida',

  `is_pinned` TINYINT(1) DEFAULT 0
    COMMENT 'Se a mensagem está fixada',

  `is_deleted` TINYINT(1) DEFAULT 0
    COMMENT 'Se a mensagem foi deletada (soft delete)',

  `deleted_at` TIMESTAMP NULL DEFAULT NULL
    COMMENT 'Timestamp da deleção',

  -- Chave primária
  PRIMARY KEY (`id`),

  -- Foreign Keys
  CONSTRAINT `fk_chat_messages_session_id`
    FOREIGN KEY (`session_id`) REFERENCES `execution_sessions` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,

  CONSTRAINT `fk_chat_messages_task_execution_id`
    FOREIGN KEY (`task_execution_id`) REFERENCES `task_executions` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,

  CONSTRAINT `fk_chat_messages_parent_message_id`
    FOREIGN KEY (`parent_message_id`) REFERENCES `chat_messages` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,

  -- Indexes para performance
  KEY `idx_chat_messages_session_id` (`session_id`),
  KEY `idx_chat_messages_task_execution_id` (`task_execution_id`),
  KEY `idx_chat_messages_timestamp` (`timestamp`),
  KEY `idx_chat_messages_sender_type` (`sender_type`),
  KEY `idx_chat_messages_message_type` (`message_type`),
  KEY `idx_chat_messages_agent_id` (`agent_id`),

  -- Indexes compostos para queries comuns
  KEY `idx_chat_session_timestamp` (`session_id`, `timestamp` DESC),
  KEY `idx_chat_session_type` (`session_id`, `message_type`),
  KEY `idx_chat_session_sender` (`session_id`, `sender_type`, `timestamp` DESC),
  KEY `idx_chat_task_timestamp` (`task_execution_id`, `timestamp` DESC),
  KEY `idx_chat_agent_timestamp` (`agent_id`, `timestamp` DESC),
  KEY `idx_chat_parent_messages` (`parent_message_id`, `timestamp` ASC),

  -- Índice para soft-delete
  KEY `idx_chat_is_deleted` (`is_deleted`, `timestamp` DESC),

  -- Check constraints
  CONSTRAINT `chk_chat_messages_sequence`
    CHECK (`sequence_number` IS NULL OR `sequence_number` >= 0),

  CONSTRAINT `chk_chat_messages_deleted`
    CHECK ((`is_deleted` = 0 AND `deleted_at` IS NULL) OR (`is_deleted` = 1 AND `deleted_at` IS NOT NULL))

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Mensagens de chat das sessões de execução';

-- ============================================================
-- Índices adicionais e otimizações
-- ============================================================

-- Trigger para auto-incrementar sequence_number (opcional)
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS `trg_chat_messages_sequence`
BEFORE INSERT ON `chat_messages`
FOR EACH ROW
BEGIN
  IF NEW.sequence_number IS NULL THEN
    SET NEW.sequence_number = (
      SELECT COALESCE(MAX(sequence_number), 0) + 1
      FROM chat_messages
      WHERE session_id = NEW.session_id
    );
  END IF;
END$$
DELIMITER ;

-- ============================================================
-- Queries de exemplo para testes
-- ============================================================

-- SELECT * FROM chat_messages WHERE session_id = 'xxx' AND is_deleted = 0 ORDER BY timestamp ASC;
-- SELECT * FROM chat_messages WHERE session_id = 'xxx' AND agent_id = 'yyy' ORDER BY timestamp DESC;
-- SELECT * FROM chat_messages WHERE parent_message_id = 'zzz' ORDER BY timestamp ASC;
-- SELECT * FROM chat_messages WHERE session_id = 'xxx' AND message_type = 'error' ORDER BY timestamp DESC;
