import os
from app import app, db

# Delete old database if it exists
db_path = 'nearby_care.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("Deleted old database")

# Create all tables using SQLAlchemy
with app.app_context():
    db.create_all()
    print("Database created successfully!")
    
    # Show created tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\nCreated {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")

