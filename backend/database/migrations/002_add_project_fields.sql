-- ===================================================================
-- LangNet Database Schema - Migration 002
-- Created: 2025-11-08
-- Description: Add missing project fields and create master test user
-- ===================================================================

USE langnet;

-- ===================================================================
-- PART 1: Add missing columns to projects table (idempotent)
-- ===================================================================

-- Add domain column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='projects' AND COLUMN_NAME='domain') > 0,
  'SELECT 1',
  'ALTER TABLE projects ADD COLUMN domain VARCHAR(100) AFTER description'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add framework column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='projects' AND COLUMN_NAME='framework') > 0,
  'SELECT 1',
  'ALTER TABLE projects ADD COLUMN framework ENUM(''crewai'',''langchain'',''autogen'',''custom'') DEFAULT NULL AFTER domain'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add default_llm column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='projects' AND COLUMN_NAME='default_llm') > 0,
  'SELECT 1',
  'ALTER TABLE projects ADD COLUMN default_llm VARCHAR(100) AFTER framework'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add memory_system column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='projects' AND COLUMN_NAME='memory_system') > 0,
  'SELECT 1',
  'ALTER TABLE projects ADD COLUMN memory_system VARCHAR(100) AFTER default_llm'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add start_from column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='projects' AND COLUMN_NAME='start_from') > 0,
  'SELECT 1',
  'ALTER TABLE projects ADD COLUMN start_from ENUM(''blank'',''template'') DEFAULT ''blank'' AFTER memory_system'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add template column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='projects' AND COLUMN_NAME='template') > 0,
  'SELECT 1',
  'ALTER TABLE projects ADD COLUMN template VARCHAR(100) AFTER start_from'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add status column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='projects' AND COLUMN_NAME='status') > 0,
  'SELECT 1',
  'ALTER TABLE projects ADD COLUMN status ENUM(''draft'',''active'',''completed'',''archived'',''error'') DEFAULT ''draft'' AFTER template'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add indexes for performance (IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_domain ON projects(domain);
CREATE INDEX IF NOT EXISTS idx_framework ON projects(framework);
CREATE INDEX IF NOT EXISTS idx_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_start_from ON projects(start_from);

-- ===================================================================
-- PART 2: Add missing columns to users table (idempotent)
-- ===================================================================

-- Add role column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='users' AND COLUMN_NAME='role') > 0,
  'SELECT 1',
  'ALTER TABLE users ADD COLUMN role VARCHAR(50) AFTER password_hash'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add is_active column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='users' AND COLUMN_NAME='is_active') > 0,
  'SELECT 1',
  'ALTER TABLE users ADD COLUMN is_active TINYINT(1) DEFAULT 1 AFTER role'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add last_login column if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA='langnet' AND TABLE_NAME='users' AND COLUMN_NAME='last_login') > 0,
  'SELECT 1',
  'ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL AFTER is_active'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add indexes for users (IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_is_active ON users(is_active);

-- ===================================================================
-- PART 3: Create master test user
-- Password: 'teste' hashed with bcrypt
-- ===================================================================

INSERT INTO users (id, name, email, password_hash, role, is_active)
VALUES (
  UUID(),
  'Admin Master',
  'teste@teste.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztpvVjUFrT8u',
  'admin',
  1
)
ON DUPLICATE KEY UPDATE id=id;  -- Evitar erro se usuário já existir

-- ===================================================================
-- Verification Queries
-- ===================================================================

-- Show updated projects structure
DESCRIBE projects;

-- Show created user
SELECT id, name, email, role, is_active, created_at
FROM users
WHERE email = 'teste@teste.com';

-- ===================================================================
-- END OF MIGRATION 002
-- ===================================================================
