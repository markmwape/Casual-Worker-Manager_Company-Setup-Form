-- Create temporary table with new schema
CREATE TABLE worker_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    company_id INTEGER NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- Copy data from old table to new one
INSERT INTO worker_temp (id, first_name, last_name, created_at, company_id)
SELECT id, first_name, last_name, created_at, company_id
FROM worker;

-- Drop old table
DROP TABLE worker;

-- Rename new table to original name
ALTER TABLE worker_temp RENAME TO worker;