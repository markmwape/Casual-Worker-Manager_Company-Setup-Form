-- Create temporary table with start_date instead of deadline
CREATE TABLE task_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    start_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    company_id INTEGER NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- Copy data from old table to new one, using created_at as start_date
INSERT INTO task_temp (id, name, description, status, start_date, created_at, company_id)
SELECT id, name, description, status, created_at, created_at, company_id
FROM task;

-- Drop old table
DROP TABLE task;

-- Rename new table to original name
ALTER TABLE task_temp RENAME TO task;

-- Add payment_type and per_part_rate columns to task table
ALTER TABLE task ADD COLUMN payment_type VARCHAR(20) NOT NULL DEFAULT 'per_day';
ALTER TABLE task ADD COLUMN per_part_rate FLOAT NULL;