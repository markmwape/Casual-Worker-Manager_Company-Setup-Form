#!/usr/bin/env python3
"""
Simple migration test
"""
import os
import sqlite3

# Create a fresh database
if os.path.exists('test_database.sqlite'):
    os.remove('test_database.sqlite')

conn = sqlite3.connect('test_database.sqlite')
cursor = conn.cursor()

# Create migrations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL UNIQUE,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Test a simple migration
try:
    cursor.execute('CREATE TABLE company (id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()
    print("✅ Company table created successfully")
    
    # Record migration
    cursor.execute('INSERT INTO migrations (filename) VALUES (?)', ('test_migration.sql',))
    conn.commit()
    print("✅ Migration recorded successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {tables}")

# Check migrations
cursor.execute("SELECT * FROM migrations")
migrations = cursor.fetchall()
print(f"Migrations: {migrations}")

conn.close() 