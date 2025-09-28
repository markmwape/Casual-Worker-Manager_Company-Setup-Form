-- Migration 037: Update expected_workers to string format
-- This migration safely handles the expected_workers_string column

-- Check if the column already exists and add it if it doesn't
SELECT CASE 
    WHEN NOT EXISTS (
        SELECT 1 FROM pragma_table_info('workspace') 
        WHERE name = 'expected_workers_string'
    ) 
    THEN 'ALTER TABLE workspace ADD COLUMN expected_workers_string VARCHAR(50) NOT NULL DEFAULT "below_100"'
    ELSE 'SELECT 1' -- Do nothing if column exists
END; 