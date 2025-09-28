-- Add custom worker fields table
CREATE TABLE custom_worker_field (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    label VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT 0,
    is_default BOOLEAN DEFAULT 0,
    "order" INTEGER NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- Add worker custom field values table
CREATE TABLE worker_custom_field_value (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    custom_field_id INTEGER NOT NULL,
    value VARCHAR(255),
    FOREIGN KEY (worker_id) REFERENCES worker(id),
    FOREIGN KEY (custom_field_id) REFERENCES custom_worker_field(id)
);