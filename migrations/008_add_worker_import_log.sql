-- Create table for tracking worker imports
CREATE TABLE worker_import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    total_records INTEGER NOT NULL,
    successful_imports INTEGER NOT NULL, 
    duplicate_records INTEGER NOT NULL,
    error_records INTEGER NOT NULL,
    error_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id)
);