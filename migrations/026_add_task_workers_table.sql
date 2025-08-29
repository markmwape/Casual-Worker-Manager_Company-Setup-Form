-- Create task_workers association table
CREATE TABLE task_workers (
    task_id INTEGER NOT NULL,
    worker_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, worker_id),
    FOREIGN KEY (task_id) REFERENCES task(id),
    FOREIGN KEY (worker_id) REFERENCES worker(id)
);