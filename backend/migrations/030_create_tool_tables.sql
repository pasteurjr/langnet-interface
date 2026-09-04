-- Etapa FERRAMENTAS: resolve cada ferramenta citada no ATS para uma implementação REAL.
CREATE TABLE IF NOT EXISTS tool_sessions (
  id varchar(36) NOT NULL,
  project_id varchar(36) NOT NULL,
  user_id varchar(36) DEFAULT NULL,
  agent_task_spec_session_id varchar(36) DEFAULT NULL,
  agent_task_spec_version int(10) unsigned DEFAULT NULL,
  version int(11) DEFAULT 1,
  status varchar(30) DEFAULT 'draft',
  tools_json longtext DEFAULT NULL,
  total_tools int(11) DEFAULT 0,
  total_resolvidas int(11) DEFAULT 0,
  total_pendentes int(11) DEFAULT 0,
  generation_log text DEFAULT NULL,
  approval_status varchar(20) DEFAULT 'pending',
  approved_by varchar(36) DEFAULT NULL,
  approved_at timestamp NULL DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (id),
  KEY idx_tool_project (project_id),
  KEY idx_tool_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS tool_chat_messages (
  id varchar(36) NOT NULL,
  tool_session_id varchar(36) NOT NULL,
  role varchar(20) NOT NULL,
  content longtext NOT NULL,
  tool_name varchar(120) DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  KEY idx_tcm_session (tool_session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS tool_version_history (
  id int(11) NOT NULL AUTO_INCREMENT,
  tool_session_id varchar(36) NOT NULL,
  version int(11) NOT NULL,
  tools_json longtext DEFAULT NULL,
  change_type varchar(30) DEFAULT NULL,
  change_description text DEFAULT NULL,
  created_by varchar(36) DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  KEY idx_tvh_session (tool_session_id, version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
