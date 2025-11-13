-- Add trial extension tracking field to workspace table
ALTER TABLE workspace ADD COLUMN extension_used BOOLEAN DEFAULT FALSE;
