import os
import sqlite3
import logging
import re
from flask import send_from_directory

def apply_sqlite_migrations(engine, model_base, migrations_dir):
    """Apply SQLite migrations from .sql files in the migrations directory."""
    try:
        # Get database path from engine URL
        db_path = str(engine.url).replace('sqlite:///', '')
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create migrations table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        
        # Get list of applied migrations
        cursor.execute('SELECT filename FROM migrations')
        applied_migrations = {row[0] for row in cursor.fetchall()}
        
        # Get list of migration files
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        # Apply new migrations
        for filename in migration_files:
            if filename not in applied_migrations:
                try:
                    logging.info(f"Applying migration: {filename}")
                    
                    # Read migration file
                    with open(os.path.join(migrations_dir, filename), 'r') as f:
                        migration_sql = f.read()
                    
                    # Split into individual statements
                    statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
                    
                    # Execute each statement separately
                    for statement in statements:
                        try:
                            if statement.strip():
                                # Handle CREATE TABLE
                                if statement.upper().startswith('CREATE TABLE'):
                                    statement = statement.replace(
                                        'CREATE TABLE',
                                        'CREATE TABLE IF NOT EXISTS'
                                    )
                                    cursor.execute(statement)
                                    conn.commit()
                                
                                # Handle SELECT CASE statements that generate ALTER TABLE
                                elif statement.upper().startswith('SELECT CASE'):
                                    # Execute the CASE statement to get the ALTER TABLE command if needed
                                    cursor.execute(statement)
                                    result = cursor.fetchone()
                                    if result and result[0]:  # If we got an ALTER TABLE command
                                        try:
                                            cursor.execute(result[0])
                                            conn.commit()
                                            logging.info(f"Executed dynamic SQL: {result[0]}")
                                        except sqlite3.OperationalError as e:
                                            if "already exists" in str(e):
                                                logging.warning(f"Column already exists, skipping: {str(e)}")
                                            else:
                                                raise
                                
                                # Handle ALTER TABLE ADD COLUMN statements directly
                                elif statement.strip().upper().startswith('ALTER TABLE') and 'ADD COLUMN' in statement.upper():
                                    # Use regex to extract table and column name
                                    match = re.match(r"ALTER\s+TABLE\s+([`\w\"]+)\s+ADD\s+COLUMN\s+([`\w\"]+)", statement, re.IGNORECASE)
                                    if match:
                                        table_name = match.group(1).strip('`"')
                                        col_name = match.group(2).strip('`"')
                                        # Check if column already exists
                                        cursor.execute(f"PRAGMA table_info({table_name})")
                                        existing_cols = [row[1] for row in cursor.fetchall()]
                                        if col_name in existing_cols:
                                            logging.info(f"Column {col_name} already exists in {table_name}, skipping")
                                            continue
                                    try:
                                        cursor.execute(statement)
                                        conn.commit()
                                        logging.info(f"Successfully executed: {statement}")
                                    except sqlite3.OperationalError as e:
                                        if "duplicate column name" in str(e):
                                            logging.warning(f"Duplicate column skipped: {str(e)}")
                                            continue
                                        elif "no such table" in str(e):
                                            logging.warning(f"Table doesn't exist, skipping: {str(e)}")
                                            continue
                                        else:
                                            logging.error(f"Error executing statement: {statement}")
                                            logging.error(f"Error: {str(e)}")
                                            raise
                                
                                # Handle regular statements
                                else:
                                    cursor.execute(statement)
                                    conn.commit()
                                
                        except sqlite3.OperationalError as e:
                            if "already exists" in str(e):
                                logging.warning(f"Object already exists: {str(e)}")
                                continue
                            elif "no such column" in str(e):
                                logging.warning(f"Column doesn't exist (probably already dropped): {str(e)}")
                                continue
                            else:
                                raise
                    
                    # Record migration as applied
                    cursor.execute('INSERT OR IGNORE INTO migrations (filename) VALUES (?)', (filename,))
                    conn.commit()
                    logging.info(f"Successfully applied migration: {filename}")
                    
                except Exception as e:
                    logging.error(f"Error applying migration {filename}: {str(e)}")
                    # Don't record the migration as applied if it failed
                    raise
            else:
                logging.info(f"Skipping already applied migration: {filename}")
        
        conn.close()
        logging.info("Migration process completed")
        
    except Exception as e:
        logging.error(f"Error applying migrations: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

def upload_file_to_storage(file_storage, destination_dir='uploads'):
    """Save uploaded file to the uploads directory and return the file path."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    file_path = os.path.join(destination_dir, file_storage.filename)
    file_storage.save(file_path)
    logging.info(f"File uploaded to {file_path}")
    return file_path

def download_file_from_storage(filename, source_dir='uploads'):
    """Send a file from the uploads directory using Flask's send_from_directory."""
    logging.info(f"Sending file {filename} from {source_dir}")
    return send_from_directory(source_dir, filename)

def llm(prompt, **kwargs):
    """Mock LLM function: returns a canned response for any prompt."""
    logging.info(f"Mock LLM called with prompt: {prompt}")
    return {
        'prompt': prompt,
        'response': 'This is a mock response from the LLM.'
    } 