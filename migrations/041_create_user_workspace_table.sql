-- Migration 041: Create user_workspace table
-- This migration creates the user_workspace table for managing user-workspace relationships

CREATE TABLE IF NOT EXISTS user_workspace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    workspace_id INTEGER NOT NULL,
    role VARCHAR(20) DEFAULT 'Supervisor',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (workspace_id) REFERENCES workspace(id),
    UNIQUE(user_id, workspace_id)
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_workspace_user_id ON user_workspace(user_id);
CREATE INDEX IF NOT EXISTS idx_user_workspace_workspace_id ON user_workspace(workspace_id); 