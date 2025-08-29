-- Create temporary table with updated schema
CREATE TABLE task_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    company_id INTEGER NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- Copy data from old table to new one
INSERT INTO task_temp (id, name, description, status, created_at, company_id)
SELECT id, name, description, status, created_at, company_id
FROM task;

-- Drop old table
DROP TABLE task;

-- Rename new table to original name
ALTER TABLE task_temp RENAME TO task;