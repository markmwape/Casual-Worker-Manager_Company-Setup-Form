-- Migration 039: Add created_at field to User table
-- First add the column without default
ALTER TABLE user ADD COLUMN created_at DATETIME;

-- Then update existing records with current timestamp
UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL; 