-- Add task_id column to attendance table
CREATE TABLE attendance_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    date DATE NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Absent',
    company_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    FOREIGN KEY (worker_id) REFERENCES worker(id),
    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (task_id) REFERENCES task(id)
);

-- Copy data from old table to new one
INSERT INTO attendance_temp (
    id, worker_id, date, check_in_time, check_out_time, 
    status, company_id, task_id
)
SELECT 
    id, worker_id, date, check_in_time, check_out_time, 
    status, company_id, 
    (SELECT id FROM task WHERE start_date = date LIMIT 1) as task_id
FROM attendance;

-- Drop old table
DROP TABLE attendance;

-- Rename new table to original name
ALTER TABLE attendance_temp RENAME TO attendance;