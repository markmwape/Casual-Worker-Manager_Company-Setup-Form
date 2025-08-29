-- Create worker custom field values table
CREATE TABLE IF NOT EXISTS worker_custom_field_value (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    custom_field_id INTEGER NOT NULL,
    value VARCHAR(255),
    FOREIGN KEY (worker_id) REFERENCES worker(id),
    FOREIGN KEY (custom_field_id) REFERENCES import_field(id)
);