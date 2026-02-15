"""
Create a default admin user for the system
Run this script after creating the database
"""
from app import app, db, User
import bcrypt

def create_admin():
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@nearbycare.com').first()
        
        if existing_admin:
            # Update existing admin to admin
            existing_admin.role = 'admin'
            existing_admin.is_admin = True
            existing_admin.status = 'active'
            existing_admin.is_verified = True
            db.session.commit()
            print(f"[OK] Updated existing admin: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Status: {existing_admin.status}")
            return
        
        # Create new admin
        password = 'admin123'  # Change this in production!
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin = User(
            username='admin',
            email='admin@nearbycare.com',
            password_hash=password_hash,
            is_verified=True,
            is_admin=True,
            role='admin',
            status='active'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("[OK] Admin created successfully!")
        print(f"   Email: {admin.email}")
        print(f"   Password: {password}")
        print(f"   Role: {admin.role}")
        print("\n[WARNING] IMPORTANT: Change the password after first login!")

if __name__ == '__main__':
    create_admin()
