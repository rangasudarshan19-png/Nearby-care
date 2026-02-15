"""Add is_admin column to users table"""
import sqlite3
import os

db_path = 'instance/nearby_care.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        print("Adding is_admin column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        conn.commit()
        print("✓ Column added successfully!")
    else:
        print("Column is_admin already exists")
    
    conn.close()
else:
    print(f"Database not found at {db_path}")
    print("Run app.py to create the database first")
