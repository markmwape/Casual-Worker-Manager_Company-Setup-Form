-- Fix all missing columns that the models expect
-- This migration ensures all required columns exist in the database

-- Add missing columns to company table (if they don't exist)
SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('company') WHERE name = 'daily_payout_rate')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE company ADD COLUMN daily_payout_rate FLOAT DEFAULT 56.0'
END;

SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('company') WHERE name = 'currency')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE company ADD COLUMN currency VARCHAR(3) DEFAULT ''ZMW'''
END;

SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('company') WHERE name = 'currency_symbol')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE company ADD COLUMN currency_symbol VARCHAR(5) DEFAULT ''K'''
END;

SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('company') WHERE name = 'phone')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE company ADD COLUMN phone VARCHAR(20) DEFAULT '''''
END;

-- Add missing columns to worker table (if they don't exist)
SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('worker') WHERE name = 'date_of_birth')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE worker ADD COLUMN date_of_birth DATE'
END;

-- Add missing columns to task table (if they don't exist)
SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('task') WHERE name = 'payment_type')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE task ADD COLUMN payment_type VARCHAR(20) DEFAULT ''per_day'''
END;

SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('task') WHERE name = 'per_part_rate')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE task ADD COLUMN per_part_rate FLOAT'
END;

SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('task') WHERE name = 'per_part_payout')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE task ADD COLUMN per_part_payout FLOAT'
END;

SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('task') WHERE name = 'per_part_currency')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE task ADD COLUMN per_part_currency VARCHAR(10)'
END;

-- Add missing columns to attendance table (if they don't exist)
SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM pragma_table_info('attendance') WHERE name = 'units_completed')
    THEN 'SELECT 1'
    ELSE 'ALTER TABLE attendance ADD COLUMN units_completed INTEGER'
END; 