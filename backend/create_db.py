from app import app, db, run_db_maintenance

# Create any missing tables using SQLAlchemy. This must not delete existing app data.
with app.app_context():
    result = run_db_maintenance()
    print("Database tables are ready.")
    if not result['ok']:
        print(f"Missing tables: {result['missing_tables']}")
        print(f"Missing columns: {result['missing_columns']}")
        raise SystemExit(1)
    
    # Show created tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\nCreated {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")

