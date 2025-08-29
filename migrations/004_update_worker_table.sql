-- Check and update columns only if they don't exist
SELECT CASE 
    WHEN NOT EXISTS(SELECT 1 FROM pragma_table_info('worker') WHERE name='first_name')
    THEN 'ALTER TABLE worker ADD COLUMN first_name VARCHAR(100) NOT NULL DEFAULT ""'
END WHERE 'ALTER TABLE worker ADD COLUMN first_name VARCHAR(100) NOT NULL DEFAULT ""' IS NOT NULL;

SELECT CASE 
    WHEN NOT EXISTS(SELECT 1 FROM pragma_table_info('worker') WHERE name='last_name')
    THEN 'ALTER TABLE worker ADD COLUMN last_name VARCHAR(100) NOT NULL DEFAULT ""'
END WHERE 'ALTER TABLE worker ADD COLUMN last_name VARCHAR(100) NOT NULL DEFAULT ""' IS NOT NULL;



-- Check if name column exists before trying to copy data and drop it
SELECT CASE 
    WHEN EXISTS(SELECT 1 FROM pragma_table_info('worker') WHERE name='name')
    THEN 'UPDATE worker SET first_name = name WHERE first_name = ""'
END WHERE 'UPDATE worker SET first_name = name WHERE first_name = ""' IS NOT NULL;

SELECT CASE 
    WHEN EXISTS(SELECT 1 FROM pragma_table_info('worker') WHERE name='name')
    THEN 'ALTER TABLE worker DROP COLUMN name'
END WHERE 'ALTER TABLE worker DROP COLUMN name' IS NOT NULL;