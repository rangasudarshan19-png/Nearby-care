"""
Test suite for doctors and appointments
"""

def test_get_doctors(client, auth_headers):
    """Test getting list of doctors"""
    response = client.get('/api/doctors', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert 'doctors' in data

def test_get_doctors_by_specialty(client, auth_headers):
    """Test filtering doctors by specialty"""
    response = client.get('/api/doctors?specialty=Cardiology', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert 'doctors' in data
    for doctor in data['doctors']:
        assert doctor['specialty'] == 'Cardiology'

def test_get_doctor_details(client, auth_headers):
    """Test getting doctor details"""
    # First get list of doctors
    doctors_response = client.get('/api/doctors', headers=auth_headers)
    doctors = doctors_response.json['doctors']
    
    if doctors:
        doctor_id = doctors[0]['id']
        response = client.get(f'/api/doctors/{doctor_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.json
        assert 'doctor' in data

def test_book_appointment(client, auth_headers):
    """Test booking an appointment"""
    from datetime import datetime, timedelta
    
    # Get a doctor
    doctors_response = client.get('/api/doctors', headers=auth_headers)
    doctors = doctors_response.json['doctors']
    
    if doctors:
        doctor_id = doctors[0]['id']
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = client.post('/api/appointments',
                              headers=auth_headers,
                              json={
                                  'doctor_id': doctor_id,
                                  'appointment_date': tomorrow,
                                  'appointment_time': '10:00',
                                  'symptoms': 'Test symptoms'
                              })
        assert response.status_code == 201
        data = response.json
        assert 'appointment_id' in data

def test_get_appointments(client, auth_headers):
    """Test getting user's appointments"""
    response = client.get('/api/appointments', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert 'appointments' in data

def test_cancel_appointment(client, auth_headers):
    """Test canceling an appointment"""
    from datetime import datetime, timedelta
    
    # First book an appointment
    doctors_response = client.get('/api/doctors', headers=auth_headers)
    doctors = doctors_response.json['doctors']
    
    if doctors:
        doctor_id = doctors[0]['id']
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        booking_response = client.post('/api/appointments',
                                      headers=auth_headers,
                                      json={
                                          'doctor_id': doctor_id,
                                          'appointment_date': tomorrow,
                                          'appointment_time': '14:00',
                                          'symptoms': 'Test'
                                      })
        
        if booking_response.status_code == 201:
            appointment_id = booking_response.json['appointment_id']
            
            # Cancel it
            response = client.delete(f'/api/appointments/{appointment_id}',
                                    headers=auth_headers)
            assert response.status_code == 200

def test_get_available_slots(client, auth_headers):
    """Test getting available time slots"""
    from datetime import datetime, timedelta
    
    doctors_response = client.get('/api/doctors', headers=auth_headers)
    doctors = doctors_response.json['doctors']
    
    if doctors:
        doctor_id = doctors[0]['id']
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = client.get(f'/api/doctors/{doctor_id}/available-slots?date={tomorrow}',
                            headers=auth_headers)
        assert response.status_code == 200
        data = response.json
        assert 'slots' in data


def test_duplicate_scheduled_slot_is_rejected(client, auth_headers):
    """Test database-backed scheduled slot uniqueness"""
    from datetime import date, timedelta
    from app import Doctor, db

    doctor = Doctor(
        name='Dr Duplicate Guard',
        specialty='General Medicine',
        hospital_id='duplicate-guard',
        hospital_name='Duplicate Guard Hospital',
        available_days='[]',
        available_hours='09:00-11:00'
    )
    db.session.add(doctor)
    db.session.commit()

    appointment_date = (date.today() + timedelta(days=1)).isoformat()
    payload = {
        'doctor_id': doctor.id,
        'appointment_date': appointment_date,
        'appointment_time': '09:00',
        'symptoms': 'Test'
    }

    first = client.post('/api/appointments', headers=auth_headers, json=payload)
    second = client.post('/api/appointments', headers=auth_headers, json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json['error'] == 'This time slot is already booked'


def test_deleted_doctor_cannot_be_booked(client, auth_headers):
    """Test a hard-deleted doctor cannot receive new bookings"""
    from datetime import date, timedelta

    response = client.post('/api/appointments', headers=auth_headers, json={
        'doctor_id': 999999,
        'appointment_date': (date.today() + timedelta(days=1)).isoformat(),
        'appointment_time': '09:00'
    })

    assert response.status_code == 404
    assert response.json['error'] == 'Doctor not found'
