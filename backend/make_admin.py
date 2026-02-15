from app import app, db, User

with app.app_context():
    # Check admin user
    admin = User.query.filter_by(email='abijeethchari8080@gmail.com').first()
    
    if admin:
        print(f"Current user details:")
        print(f"  Email: {admin.email}")
        print(f"  Username: {admin.username}")
        print(f"  Role: {admin.role}")
        print(f"  is_admin: {admin.is_admin}")
        print(f"  Status: {admin.status}")
        
        # Update to admin
        admin.is_admin = True
        admin.role = 'admin'
        db.session.commit()
        
        print(f"\n✅ Updated to admin!")
        print(f"  New role: {admin.role}")
        print(f"  New is_admin: {admin.is_admin}")
    else:
        print("User not found")
