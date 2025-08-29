-- Add payout_type column to report_field
-- defaults to 'both' for existing rows
ALTER TABLE report_field ADD COLUMN payout_type VARCHAR(20) NOT NULL DEFAULT 'both'; 