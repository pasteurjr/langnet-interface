CREATE TABLE pacientes (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL,
    contato VARCHAR(20),
    convenio VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pacientes_cpf (cpf)
) COMMENT='Pacientes atendidos no sistema';

CREATE TABLE especialidades (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    nome VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_especialidades_nome (nome)
) COMMENT='Especialidades médicas oferecidas no sistema';

CREATE TABLE medicos (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    nome VARCHAR(255) NOT NULL,
    crm VARCHAR(10) NOT NULL UNIQUE,
    especialidade_id CHAR(36) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (especialidade_id) REFERENCES especialidades(id) ON DELETE CASCADE,
    INDEX idx_medicos_crm (crm),
    INDEX idx_medicos_especialidade_id (especialidade_id)
) COMMENT='Médicos que atendem os pacientes no sistema';

CREATE TABLE agentes_ia (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    nome VARCHAR(255) NOT NULL UNIQUE,
    status ENUM('ativo', 'inativo') NOT NULL DEFAULT 'ativo',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agentes_ia_nome (nome)
) COMMENT='Agentes de IA utilizados no sistema para triagem e atendimento';

CREATE TABLE atendimentos (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    paciente_id CHAR(36) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
    INDEX idx_atendimentos_paciente_id (paciente_id)
) COMMENT='Atendimentos realizados no sistema';

CREATE TABLE pre_diagnosticos (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    atendimento_id CHAR(36) NOT NULL,
    hipoteses TEXT NOT NULL,
    nivel_confianca FLOAT NOT NULL,
    exames_sugeridos TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (atendimento_id) REFERENCES atendimentos(id) ON DELETE CASCADE,
    INDEX idx_pre_diagnosticos_atendimento_id (atendimento_id)
) COMMENT='Pré-diagnósticos gerados pelo sistema para os pacientes';

CREATE TABLE encaminhamentos (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    atendimento_id CHAR(36) NOT NULL,
    especialidade_id CHAR(36) NOT NULL,
    medico_id CHAR(36) NOT NULL,
    prioridade ENUM('normal', 'urgente') NOT NULL DEFAULT 'normal',
    status ENUM('gerado', 'pendente', 'concluido') NOT NULL DEFAULT 'gerado',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (atendimento_id) REFERENCES atendimentos(id) ON DELETE CASCADE,
    FOREIGN KEY (especialidade_id) REFERENCES especialidades(id) ON DELETE CASCADE,
    FOREIGN KEY (medico_id) REFERENCES medicos(id) ON DELETE CASCADE,
    INDEX idx_encaminhamentos_atendimento_id (atendimento_id),
    INDEX idx_encaminhamentos_especialidade_id (especialidade_id),
    INDEX idx_encaminhamentos_medico_id (medico_id)
) COMMENT='Encaminhamentos gerados para os pacientes após pré-diagnóstico';

CREATE TABLE prontuarios (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    paciente_id CHAR(36) NOT NULL,
    atendimento_id CHAR(36) NOT NULL,
    triagem TEXT NOT NULL,
    pre_diagnostico_id CHAR(36) NOT NULL,
    encaminhamento_id CHAR(36) NOT NULL,
    resumo_medico TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
    FOREIGN KEY (atendimento_id) REFERENCES atendimentos(id) ON DELETE CASCADE,
    FOREIGN KEY (pre_diagnostico_id) REFERENCES pre_diagnosticos(id) ON DELETE CASCADE,
    FOREIGN KEY (encaminhamento_id) REFERENCES encaminhamentos(id) ON DELETE CASCADE,
    INDEX idx_prontuarios_paciente_id (paciente_id),
    INDEX idx_prontuarios_atendimento_id (atendimento_id),
    INDEX idx_prontuarios_pre_diagnostico_id (pre_diagnostico_id),
    INDEX idx_prontuarios_encaminhamento_id (encaminhamento_id)
) COMMENT='Prontuários eletrônicos dos pacientes';

CREATE TABLE consentimentos (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    paciente_id CHAR(36) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    versao_termo VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
    INDEX idx_consentimentos_paciente_id (paciente_id)
) COMMENT='Consentimentos dos pacientes para coleta e uso de dados';