from app import app, db, Doctor

with app.app_context():
    docs = Doctor.query.limit(5).all()
    print('\n✅ Doctors in database with Telugu names and Rupee fees:')
    print('='*60)
    for d in docs:
        print(f'  👨‍⚕️ {d.name} ({d.specialty})')
        print(f'     Fee: ₹{d.consultation_fee}')
        print(f'     Experience: {d.experience_years} years')
        print()
