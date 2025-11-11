-- Add language_preference column to user table
-- This migration adds support for multi-language user preferences

-- Check if column exists before adding (for idempotency)
ALTER TABLE "user"
ADD COLUMN IF NOT EXISTS language_preference VARCHAR(10) DEFAULT 'en' NOT NULL;
