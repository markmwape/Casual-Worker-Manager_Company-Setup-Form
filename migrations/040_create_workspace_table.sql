-- Migration 040: Create workspace table
-- This migration creates the workspace table that's required for the application

CREATE TABLE IF NOT EXISTS workspace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    workspace_code VARCHAR(16) UNIQUE NOT NULL,
    address TEXT,
    country VARCHAR(100) NOT NULL,
    industry_type VARCHAR(100) NOT NULL,
    company_phone VARCHAR(20) NOT NULL,
    company_email VARCHAR(150) NOT NULL,
    expected_workers INTEGER,
    expected_workers_string VARCHAR(50) NOT NULL DEFAULT 'below_100',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    subscription_status VARCHAR(50) DEFAULT 'trial',
    trial_end_date TIMESTAMP,
    subscription_end_date TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user(id)
);

-- Create index on workspace_code for faster lookups
CREATE INDEX IF NOT EXISTS idx_workspace_code ON workspace(workspace_code);

-- Create index on created_by for faster user workspace queries
CREATE INDEX IF NOT EXISTS idx_workspace_created_by ON workspace(created_by); 