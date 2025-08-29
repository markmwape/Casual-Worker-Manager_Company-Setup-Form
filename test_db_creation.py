#!/usr/bin/env python3
"""
Test database creation
"""
import os
import sqlite3

print(f"Current directory: {os.getcwd()}")
print(f"Database file exists: {os.path.exists('database.sqlite')}")
print(f"Database file size: {os.path.getsize('database.sqlite') if os.path.exists('database.sqlite') else 'N/A'}")

# Try to create a simple database
conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Create a test table
cursor.execute('''
CREATE TABLE IF NOT EXISTS test_table (
    id INTEGER PRIMARY KEY,
    name TEXT
)
''')

# Insert test data
cursor.execute('INSERT INTO test_table (name) VALUES (?)', ('test',))

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables in database: {tables}")

conn.commit()
conn.close()

print(f"Database file size after creation: {os.path.getsize('database.sqlite')}") 