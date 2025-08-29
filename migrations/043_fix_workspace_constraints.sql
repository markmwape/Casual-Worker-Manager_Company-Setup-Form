-- Fix workspace constraints by providing default values
-- This migration ensures all required fields have default values

-- Update existing workspaces to have default values for required fields
UPDATE workspace SET address = '' WHERE address IS NULL;
UPDATE workspace SET expected_workers = 0 WHERE expected_workers IS NULL; 