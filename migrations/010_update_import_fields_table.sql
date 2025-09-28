-- Create temporary table with updated schema
CREATE TABLE import_field_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- Copy data from old table to new one
INSERT INTO import_field_temp (id, company_id, name, field_type, created_at)
SELECT id, company_id, name, field_type, created_at FROM import_field;

-- Drop old table
DROP TABLE import_field;

-- Rename new table to original name
ALTER TABLE import_field_temp RENAME TO import_field;