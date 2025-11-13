-- Add per_hour payment fields to Task table
ALTER TABLE task ADD COLUMN IF NOT EXISTS per_hour_payout FLOAT;
ALTER TABLE task ADD COLUMN IF NOT EXISTS per_hour_currency VARCHAR(10);

-- Add hours_worked field to Attendance table
ALTER TABLE attendance ADD COLUMN IF NOT EXISTS hours_worked FLOAT;

-- Add comment for documentation
COMMENT ON COLUMN task.per_hour_payout IS 'Hourly rate for per_hour payment type tasks';
COMMENT ON COLUMN task.per_hour_currency IS 'Currency for hourly payment';
COMMENT ON COLUMN attendance.hours_worked IS 'Number of hours worked for per_hour tasks';
