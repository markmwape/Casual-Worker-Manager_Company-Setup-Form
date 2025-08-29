-- Add workspace_id column to company table
-- This migration adds the missing workspace_id column that the Company model expects

-- Check if column already exists before adding
SELECT CASE 
    WHEN EXISTS (
        SELECT 1 FROM pragma_table_info('company') 
        WHERE name = 'workspace_id'
    ) 
    THEN 'SELECT 1'  -- Column exists, do nothing
    ELSE 'ALTER TABLE company ADD COLUMN workspace_id INTEGER REFERENCES workspace(id)'
END; 