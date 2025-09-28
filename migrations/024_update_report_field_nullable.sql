-- Create temporary table with updated schema
CREATE TABLE report_field_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    formula TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- Copy data from old table to new one
INSERT INTO report_field_temp (id, company_id, name, field_type, formula, created_at)
SELECT id, company_id, name, field_type, formula, created_at FROM report_field;

-- Drop old table
DROP TABLE report_field;

-- Rename new table to original name
ALTER TABLE report_field_temp RENAME TO report_field;