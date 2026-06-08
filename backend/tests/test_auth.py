"""
Test suite for authentication endpoints
"""
import json
from datetime import date, datetime, timedelta


def login_test_user(client, username, email, password='Password123!', make_admin=False):
    client.post('/api/auth/signup', json={
        'username': username,
        'email': email,
        'password': password
    })

    from app import User, db
    user = User.query.filter_by(email=email).first()
    user.is_verified = True
    user.is_admin = make_admin
    user.role = 'admin' if make_admin else 'user'
    db.session.commit()

    login_response = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    return user, login_response.json['token']


def create_admin_headers(client, email='admincreate@example.com'):
    _, token = login_test_user(client, 'adminuser', email, make_admin=True)
    return {'Authorization': f'Bearer {token}'}


def create_user_headers(client, email='doctoruser@example.com'):
    user, token = login_test_user(client, 'normaluser', email, make_admin=False)
    return user, {'Authorization': f'Bearer {token}'}


def next_weekday(target_weekday):
    today = date.today()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json
    assert data['status'] in ['healthy', 'degraded']
    assert 'checks' in data
    assert 'database' in data['checks']


def test_safe_error_response_does_not_leak_exception(client):
    """Test internal errors return a safe client message"""
    from app import safe_error_response
    response, status = safe_error_response('test failure', Exception('secret database detail'))
    assert status == 500
    assert response.json['error'] == 'Something went wrong. Please try again.'
    assert 'secret database detail' not in response.json['error']


def test_admin_preflight_check(client):
    """Test admin-only preflight reports required runtime checks"""
    admin_headers = create_admin_headers(client, email='admin@nearbycare.com')
    response = client.get('/api/preflight', headers=admin_headers)
    assert response.status_code == 200
    assert response.json['status'] == 'ready'
    assert 'database' in response.json['checks']
    assert response.json['checks']['admin_account']['exists'] is True


def test_db_maintenance_reports_ready(client):
    """Test DB maintenance is idempotent and validates schema"""
    from app import run_db_maintenance
    result = run_db_maintenance()
    assert result['ok'] is True
    assert result['missing_tables'] == []
    assert result['missing_columns'] == {}
    assert result['scheduled_slot_index'] == 'ensured'


def test_nvidia_streaming_health_response(monkeypatch, client):
    """Test NVIDIA NIM streamed chunks are parsed into one assistant response"""
    import app as app_module

    class FakeResponse:
        def raise_for_status(self):
            return None

        def iter_lines(self):
            lines = [
                b'data: {"choices":[{"delta":{"content":"Drink water"}}]}',
                b'data: {"choices":[{"delta":{"content":" and rest."}}]}',
                b'data: [DONE]',
            ]
            return iter(lines)

    def fake_post(*args, **kwargs):
        assert kwargs['stream'] is True
        assert kwargs['timeout'][1] == app_module.NVIDIA_NIM_TIMEOUT_SECONDS
        assert kwargs['json']['model'] == app_module.NVIDIA_NIM_MODEL
        return FakeResponse()

    monkeypatch.setattr(app_module, 'NVIDIA_API_KEY', 'test-nvidia-key')
    monkeypatch.setattr(app_module.requests, 'post', fake_post)

    response = app_module.generate_health_response_with_nvidia('I have fever', [])
    assert response == 'Drink water and rest.'


def test_health_assistant_messages_start_with_user_after_system(client):
    """Test frontend assistant greeting is removed before sending to NVIDIA"""
    import app as app_module

    messages = app_module.build_health_assistant_messages('current symptom', [
        {'role': 'assistant', 'content': 'Hello, describe symptoms.'},
        {'role': 'user', 'content': 'I have fever'},
        {'role': 'assistant', 'content': 'How high is it?'},
    ])

    roles = [message['role'] for message in messages]
    assert roles == ['system', 'user', 'assistant', 'user']
    assert messages[-1]['content'] == 'current symptom'


def test_symptom_chat_reports_unavailable_when_nvidia_fails(monkeypatch, client, auth_headers):
    """Test symptom chat does not silently pretend local fallback is AI"""
    import requests
    import app as app_module

    def timeout_post(*args, **kwargs):
        raise requests.Timeout('provider timed out')

    monkeypatch.setattr(app_module, 'NVIDIA_API_KEY', 'test-nvidia-key')
    monkeypatch.setattr(app_module, 'GEMINI_API_KEY', '')
    monkeypatch.setattr(app_module.requests, 'post', timeout_post)
    client.application.config['AI_LOCAL_FALLBACK_ENABLED'] = False

    response = client.post('/api/symptom-chat', json={
        'message': 'I have fever and headache',
        'chat_history': []
    }, headers=auth_headers)

    assert response.status_code == 503
    assert response.json['provider'] == 'unavailable'
    assert 'temporarily unavailable' in response.json['error']


def test_symptom_chat_local_fallback_can_be_enabled(monkeypatch, client, auth_headers):
    """Test local fallback remains available only when explicitly configured"""
    import requests
    import app as app_module

    def timeout_post(*args, **kwargs):
        raise requests.Timeout('provider timed out')

    monkeypatch.setattr(app_module, 'NVIDIA_API_KEY', 'test-nvidia-key')
    monkeypatch.setattr(app_module, 'GEMINI_API_KEY', '')
    monkeypatch.setattr(app_module.requests, 'post', timeout_post)
    client.application.config['AI_LOCAL_FALLBACK_ENABLED'] = True

    response = client.post('/api/symptom-chat', json={
        'message': 'I have fever and headache',
        'chat_history': []
    }, headers=auth_headers)

    assert response.status_code == 200
    assert response.json['provider'] == 'local_fallback'
    assert 'Fever' in response.json['response']

def test_signup(client):
    """Test user registration"""
    response = client.post('/api/auth/signup', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == 201
    data = response.json
    assert 'message' in data
    assert 'email' in data

def test_signup_allows_retry_for_unverified_email(client):
    """Test signup replaces stale unverified accounts for the same email"""
    user_data = {
        'username': 'user1',
        'email': 'retry@example.com',
        'password': 'Password123!'
    }
    # First signup
    client.post('/api/auth/signup', json=user_data)
    
    # Second signup with same unverified email should replace the stale account
    response = client.post('/api/auth/signup', json={
        'username': 'user2',
        'email': 'retry@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == 201
    assert response.json['email'] == 'retry@example.com'

def test_signup_duplicate_verified_email(client):
    """Test signup with duplicate verified email is blocked"""
    user_data = {
        'username': 'verifieduser',
        'email': 'duplicate@example.com',
        'password': 'Password123!'
    }
    client.post('/api/auth/signup', json=user_data)

    from app import User, db
    user = User.query.filter_by(email='duplicate@example.com').first()
    user.is_verified = True
    db.session.commit()

    response = client.post('/api/auth/signup', json={
        'username': 'anotheruser',
        'email': 'duplicate@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == 400
    assert 'error' in response.json

def test_login_success(client):
    """Test successful login"""
    # First create user
    client.post('/api/auth/signup', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'Password123!'
    })
    
    # Verify user (bypass OTP for testing)
    from app import User, db
    user = User.query.filter_by(email='login@example.com').first()
    user.is_verified = True
    db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'login@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == 200
    data = response.json
    assert 'token' in data
    assert 'user' in data

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert 'error' in response.json

def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'


def test_signup_rejects_weak_password(client):
    """Test signup enforces strong passwords"""
    response = client.post('/api/auth/signup', json={
        'username': 'weakuser',
        'email': 'weak@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    assert 'uppercase' in response.json['error']


def test_forgot_password_reset_flow(client):
    """Test forgot password OTP verification and password reset"""
    client.post('/api/auth/signup', json={
        'username': 'resetuser',
        'email': 'reset@example.com',
        'password': 'Password123!'
    })

    from app import User, OTP, db
    user = User.query.filter_by(email='reset@example.com').first()
    user.is_verified = True
    db.session.commit()

    request_response = client.post('/api/auth/forgot-password/request', json={
        'email': 'reset@example.com'
    })
    assert request_response.status_code == 200

    otp = OTP.query.filter_by(email='reset@example.com', is_used=False).order_by(OTP.id.desc()).first()
    assert otp is not None

    verify_response = client.post('/api/auth/forgot-password/verify', json={
        'email': 'reset@example.com',
        'otp': otp.otp_code
    })
    assert verify_response.status_code == 200

    reset_response = client.post('/api/auth/forgot-password/reset', json={
        'email': 'reset@example.com',
        'otp': otp.otp_code,
        'new_password': 'Newpass123!'
    })
    assert reset_response.status_code == 200

    login_response = client.post('/api/auth/login', json={
        'email': 'reset@example.com',
        'password': 'Newpass123!'
    })
    assert login_response.status_code == 200


def test_otp_cannot_be_reused_or_used_after_expiry(client):
    """Test OTP lifecycle rejects reuse and expired OTPs"""
    from app import OTP, User, db

    client.post('/api/auth/signup', json={
        'username': 'otptest',
        'email': 'otp-reuse@example.com',
        'password': 'Password123!'
    })
    otp = OTP.query.filter_by(email='otp-reuse@example.com', is_used=False).order_by(OTP.id.desc()).first()
    assert otp is not None

    first = client.post('/api/auth/verify-otp', json={
        'email': 'otp-reuse@example.com',
        'otp': otp.otp_code
    })
    assert first.status_code == 200

    second = client.post('/api/auth/verify-otp', json={
        'email': 'otp-reuse@example.com',
        'otp': otp.otp_code
    })
    assert second.status_code == 400

    user = User.query.filter_by(email='otp-reuse@example.com').first()
    user.is_verified = True
    expired = OTP(
        email='otp-reuse@example.com',
        otp_code='123456',
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(expired)
    db.session.commit()

    expired_response = client.post('/api/auth/forgot-password/verify', json={
        'email': 'otp-reuse@example.com',
        'otp': '123456'
    })
    assert expired_response.status_code == 400


def test_admin_can_create_doctor(client):
    """Test admin can add doctor details for a hospital"""
    from app import Doctor
    admin_headers = create_admin_headers(client)
    _, user_headers = create_user_headers(client)

    response = client.post('/api/admin/doctors', json={
        'name': 'Dr Admin Created',
        'specialty': 'Cardiology',
        'hospital_id': 1001,
        'hospital_name': 'Central Care Hospital',
        'qualifications': 'MBBS, MD',
        'experience_years': 8,
        'consultation_fee': 500,
        'available_days': ['Mon', 'Wed'],
        'available_hours': '09:00-17:00'
    }, headers=admin_headers)

    assert response.status_code == 201
    assert response.json['doctor']['hospital_id'] == '1001'
    doctor = Doctor.query.filter_by(hospital_id='1001').first()
    assert doctor is not None
    assert doctor.name == 'Dr Admin Created'

    user_response = client.get('/api/doctors', headers=user_headers)
    assert user_response.status_code == 200
    assert any(item['id'] == doctor.id for item in user_response.json['doctors'])

    hospital_response = client.get('/api/doctors?hospital_id=1001', headers=user_headers)
    assert hospital_response.status_code == 200
    assert [item['id'] for item in hospital_response.json['doctors']] == [doctor.id]


def test_non_admin_cannot_create_or_delete_doctor(client):
    """Test doctor admin routes reject normal users"""
    from app import Doctor, db
    _, user_headers = create_user_headers(client, email='notadmin@example.com')

    create_response = client.post('/api/admin/doctors', json={
        'name': 'Dr Blocked',
        'specialty': 'Cardiology',
        'hospital_id': 'blocked-hospital',
        'hospital_name': 'Blocked Hospital'
    }, headers=user_headers)
    assert create_response.status_code == 403

    doctor = Doctor(
        name='Dr Existing',
        specialty='Dental',
        hospital_id='delete-denied',
        hospital_name='Delete Denied Hospital'
    )
    db.session.add(doctor)
    db.session.commit()

    delete_response = client.delete(f'/api/admin/doctors/{doctor.id}', headers=user_headers)
    assert delete_response.status_code == 403
    assert Doctor.query.get(doctor.id) is not None


def test_admin_can_hard_delete_doctor_and_cancel_future_appointments(client):
    """Test hard delete removes doctor from lists and cancels future appointments"""
    from app import Appointment, Doctor, db
    admin_headers = create_admin_headers(client, email='admindelete@example.com')
    user, user_headers = create_user_headers(client, email='patientdelete@example.com')

    doctor = Doctor(
        name='Dr Delete Me',
        specialty='Neurology',
        hospital_id='delete-hospital',
        hospital_name='Delete Hospital',
        available_days=json.dumps(['Mon']),
        available_hours='09:00-17:00'
    )
    db.session.add(doctor)
    db.session.commit()

    appointment = Appointment(
        user_id=user.id,
        doctor_id=doctor.id,
        hospital_id=doctor.hospital_id,
        hospital_name=doctor.hospital_name,
        appointment_date=date.today() + timedelta(days=3),
        appointment_time='10:00',
        status='scheduled'
    )
    db.session.add(appointment)
    db.session.commit()

    delete_response = client.delete(f'/api/admin/doctors/{doctor.id}', headers=admin_headers)
    assert delete_response.status_code == 200
    assert delete_response.json['cancelled_appointments'] == 1
    assert Doctor.query.get(doctor.id) is None

    doctors_response = client.get('/api/doctors', headers=user_headers)
    assert doctors_response.status_code == 200
    assert all(item['id'] != doctor.id for item in doctors_response.json['doctors'])

    db.session.refresh(appointment)
    assert appointment.status == 'cancelled'
    assert appointment.deletion_reason == 'Doctor removed by admin'

    appointments_response = client.get('/api/appointments', headers=user_headers)
    assert appointments_response.status_code == 200
    deleted_row = next(item for item in appointments_response.json['appointments'] if item['id'] == appointment.id)
    assert deleted_row['doctor_name'] == 'Deleted doctor'


def test_doctor_slots_and_booking_respect_available_days(client):
    """Test unavailable weekdays return no slots and cannot be booked"""
    from app import Doctor, db
    user, user_headers = create_user_headers(client, email='weekdaypatient@example.com')
    doctor = Doctor(
        name='Dr Weekday',
        specialty='Cardiology',
        hospital_id='weekday-hospital',
        hospital_name='Weekday Hospital',
        available_days=json.dumps(['Mon']),
        available_hours='09:00-11:00'
    )
    db.session.add(doctor)
    db.session.commit()

    monday = next_weekday(0)
    tuesday = next_weekday(1)

    unavailable_slots = client.get(
        f'/api/doctors/{doctor.id}/available-slots?date={tuesday.isoformat()}',
        headers=user_headers
    )
    assert unavailable_slots.status_code == 200
    assert unavailable_slots.json['slots'] == []
    assert 'not available' in unavailable_slots.json['message']

    unavailable_booking = client.post('/api/appointments', json={
        'doctor_id': doctor.id,
        'appointment_date': tuesday.isoformat(),
        'appointment_time': '09:00'
    }, headers=user_headers)
    assert unavailable_booking.status_code == 400
    assert 'not available' in unavailable_booking.json['error']

    outside_hours_booking = client.post('/api/appointments', json={
        'doctor_id': doctor.id,
        'appointment_date': monday.isoformat(),
        'appointment_time': '12:00'
    }, headers=user_headers)
    assert outside_hours_booking.status_code == 400
    assert 'outside doctor available hours' in outside_hours_booking.json['error']

    valid_booking = client.post('/api/appointments', json={
        'doctor_id': doctor.id,
        'appointment_date': monday.isoformat(),
        'appointment_time': '09:00'
    }, headers=user_headers)
    assert valid_booking.status_code == 201


def test_admin_doctor_list_filters(client):
    """Test admin doctor list supports hospital, specialty, and search filters"""
    from app import Doctor, db
    admin_headers = create_admin_headers(client, email='adminfilter@example.com')
    doctors = [
        Doctor(name='Dr Alpha', specialty='Cardiology', hospital_id='filter-1', hospital_name='Alpha Hospital'),
        Doctor(name='Dr Beta', specialty='Dermatology', hospital_id='filter-2', hospital_name='Beta Hospital'),
    ]
    db.session.add_all(doctors)
    db.session.commit()

    hospital_response = client.get('/api/admin/doctors?hospital_id=filter-1', headers=admin_headers)
    assert hospital_response.status_code == 200
    assert [item['name'] for item in hospital_response.json['doctors']] == ['Dr Alpha']

    specialty_response = client.get('/api/admin/doctors?specialty=Derm', headers=admin_headers)
    assert specialty_response.status_code == 200
    assert [item['name'] for item in specialty_response.json['doctors']] == ['Dr Beta']

    search_response = client.get('/api/admin/doctors?search=Alpha Hospital', headers=admin_headers)
    assert search_response.status_code == 200
    assert [item['name'] for item in search_response.json['doctors']] == ['Dr Alpha']


def test_sample_doctor_seed_marker_prevents_reseed_after_delete(client):
    """Test marker prevents deleted samples from coming back after startup"""
    from app import Doctor, SystemSetting, db, should_seed_sample_doctors, SAMPLE_DOCTORS_SEED_MARKER

    doctor = Doctor(
        name='Dr Seed Present',
        specialty='General Medicine',
        hospital_id='seed-hospital',
        hospital_name='Seed Hospital'
    )
    db.session.add(doctor)
    db.session.commit()

    assert should_seed_sample_doctors() is False
    assert SystemSetting.query.filter_by(key=SAMPLE_DOCTORS_SEED_MARKER).first() is not None

    Doctor.query.delete()
    db.session.commit()

    assert should_seed_sample_doctors() is False
    assert Doctor.query.count() == 0
