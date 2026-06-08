import os
import shutil
from datetime import datetime

from app import app, db, run_db_maintenance


def get_sqlite_path():
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    prefix = 'sqlite:///'
    if not uri.startswith(prefix):
        return None
    return uri[len(prefix):]


def backup_sqlite_database():
    db_path = get_sqlite_path()
    if not db_path or not os.path.exists(db_path):
        return None

    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'nearby_care_{timestamp}.db')
    shutil.copy2(db_path, backup_path)
    return backup_path


def main():
    with app.app_context():
        backup_path = backup_sqlite_database()
        result = run_db_maintenance()
        result['backup_created'] = backup_path

        print('Database maintenance complete.')
        print(f"Backup: {backup_path or 'not needed'}")
        print(f"Scheduled slot index: {result['scheduled_slot_index']}")
        print(f"Cancelled duplicate scheduled slots: {result['cancelled_duplicate_scheduled_slots']}")
        print(f"Seed marker present: {result['sample_doctors_seed_marker']}")

        if not result['ok']:
            print(f"Missing tables: {result['missing_tables']}")
            print(f"Missing columns: {result['missing_columns']}")
            raise SystemExit(1)


if __name__ == '__main__':
    main()
