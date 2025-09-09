-- Add subscription tier column to workspace table
-- This allows tracking different subscription levels (basic, premium, etc.)

ALTER TABLE workspace ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'basic';

-- Update existing records to have a default subscription tier
UPDATE workspace SET subscription_tier = 'basic' WHERE subscription_tier IS NULL;
