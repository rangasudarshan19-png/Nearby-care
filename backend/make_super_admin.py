import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, User

with app.app_context():
    # Find the user
    admin = User.query.filter_by(email='abijeethchari8080@gmail.com').first()
    
    if not admin:
        print("❌ User not found!")
        sys.exit(1)
    
    print(f"Current user details:")
    print(f"  Email: {admin.email}")
    print(f"  Role: {admin.role}")
    print(f"  is_admin: {admin.is_admin}")
    
    # Update to admin
    admin.role = 'admin'
    admin.is_admin = True
    db.session.commit()
    
    print(f"\n✅ Updated to admin!")
    print(f"  New role: {admin.role}")
    print(f"  New is_admin: {admin.is_admin}")
    print("\n⚠️ Please logout and login again to refresh your session!")
