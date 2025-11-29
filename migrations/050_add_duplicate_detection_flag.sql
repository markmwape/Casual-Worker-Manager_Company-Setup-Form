-- Add duplicate detection flag to import_field table
-- This feature allows marking custom fields for duplicate value checking

ALTER TABLE import_field ADD COLUMN enable_duplicate_detection BOOLEAN DEFAULT 0;

-- Create an index on the flag for efficient filtering
CREATE INDEX idx_import_field_duplicate_detection ON import_field(company_id, enable_duplicate_detection);
