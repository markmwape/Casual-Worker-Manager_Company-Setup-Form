-- Create a new attendance table with the correct schema
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

-- If no tasks exist, create a default task to assign to existing records
INSERT INTO task (name, description, status, start_date, created_at, company_id)
SELECT 
    'Default Task', 
    'Migrated Attendance Records', 
    'Pending', 
    date, 
    datetime('now'), 
    company_id
FROM (
    SELECT DISTINCT date, company_id 
    FROM attendance 
    WHERE date IS NOT NULL
) AS unique_dates
WHERE NOT EXISTS (
    SELECT 1 FROM task 
    WHERE task.start_date = unique_dates.date
);

-- Migrate existing data to the new table, using the first matching task or the default task
INSERT INTO attendance_temp (
    id, worker_id, date, check_in_time, check_out_time, 
    status, company_id, task_id
)
SELECT 
    id, worker_id, date, check_in_time, check_out_time, 
    status, company_id,
    COALESCE(
        (SELECT id FROM task WHERE start_date = attendance.date LIMIT 1),
        (SELECT id FROM task WHERE name = 'Default Task' AND start_date = attendance.date LIMIT 1)
    ) as task_id
FROM attendance;

-- Drop the old table
DROP TABLE attendance;

-- Rename the new table
ALTER TABLE attendance_temp RENAME TO attendance;