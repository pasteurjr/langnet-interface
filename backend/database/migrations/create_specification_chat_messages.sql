-- ============================================================
-- Table: specification_chat_messages
-- Mensagens de chat para sessões de especificação
-- ============================================================

CREATE TABLE IF NOT EXISTS `specification_chat_messages` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  `session_id` CHAR(36) NOT NULL COMMENT 'ID da sessão de especificação',
  `sender_type` ENUM('user', 'agent', 'system', 'assistant') NOT NULL DEFAULT 'system',
  `sender_name` VARCHAR(255) NULL,
  `message_text` LONGTEXT NOT NULL,
  `message_type` ENUM('chat', 'status', 'progress', 'result', 'error', 'warning', 'info', 'document') NOT NULL DEFAULT 'chat',
  `timestamp` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `parent_message_id` CHAR(36) NULL,
  `metadata` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,

  PRIMARY KEY (`id`),

  CONSTRAINT `fk_spec_chat_session_id`
    FOREIGN KEY (`session_id`) REFERENCES `execution_specification_sessions` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,

  KEY `idx_spec_chat_session_id` (`session_id`),
  KEY `idx_spec_chat_timestamp` (`timestamp`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
