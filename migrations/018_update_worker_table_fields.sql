-- Create temporary table with updated schema
CREATE TABLE worker_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(100),
    last_name VARCHAR(100), 
    date_of_birth VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    company_id INTEGER NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Copy data from old table to new one
INSERT INTO worker_temp (id, created_at, company_id)
SELECT id, created_at, company_id
FROM worker;

-- Drop old table
DROP TABLE worker;

-- Rename new table to original name
ALTER TABLE worker_temp RENAME TO worker;