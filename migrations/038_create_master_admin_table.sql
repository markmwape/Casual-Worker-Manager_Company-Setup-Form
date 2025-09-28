-- Migration 038: Create MasterAdmin table
CREATE TABLE IF NOT EXISTS master_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(150) NOT NULL UNIQUE,
    name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (created_by) REFERENCES master_admin(id)
); 