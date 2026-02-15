import sqlite3
import os

# Use the actual database path (instance folder)
db_path = os.path.join('instance', 'nearby_care.db')

if not os.path.exists(db_path):
    print(f"❌ Database file not found at: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nDatabase: {db_path}")
print(f"Size: {os.path.getsize(db_path)} bytes")
print(f"Found {len(tables)} tables:")
for table in sorted(tables):
    print(f"  - {table[0]}")

conn.close()

print("\n✅ Database schema verified!")


