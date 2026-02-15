from app import app, db, User
import bcrypt

with app.app_context():
    email = 'abijeethchari8080@gmail.com'
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    if user:
        print(f"✅ User found!")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"   Status: {user.status}")
        print(f"   Created: {user.created_at}")
        
        # Update password to match user's password
        new_password = '123456'
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = password_hash
        user.is_verified = True  # Make sure it's verified
        db.session.commit()
        
        print(f"\n✅ Password updated and account verified!")
        print(f"   You can now login with:")
        print(f"   Email: {email}")
        print(f"   Password: {new_password}")
    else:
        print(f"❌ User not found. Creating new account...")
        
        # Create new user
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(
            username='Abijeeth',
            email=email,
            password_hash=password_hash,
            is_verified=True,  # Pre-verify
            status='active'
        )
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✅ Account created and verified!")
        print(f"   Email: {email}")
        print(f"   Username: Abijeeth")
        print(f"   Password: 123456")
