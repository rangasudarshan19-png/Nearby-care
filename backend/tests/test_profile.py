"""
Test suite for user profile and medical records
"""

def test_get_user_profile(client, auth_headers):
    """Test getting user profile"""
    response = client.get('/api/user/profile', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert 'user' in data or 'profile' in data

def test_update_user_profile(client, auth_headers):
    """Test updating user profile"""
    response = client.post('/api/user/profile',
                          headers=auth_headers,
                          json={
                              'blood_type': 'O+',
                              'allergies': 'Penicillin',
                              'chronic_conditions': 'Hypertension',
                              'emergency_contact': 'John Doe',
                              'emergency_phone': '+1-555-0100'
                          })
    assert response.status_code == 200
    data = response.json
    assert 'profile' in data
    assert data['profile']['blood_type'] == 'O+'

def test_add_medical_record(client, auth_headers):
    """Test adding a medical record"""
    from datetime import datetime
    
    response = client.post('/api/user/medical-records',
                          headers=auth_headers,
                          json={
                              'title': 'Annual Checkup',
                              'description': 'All vitals normal',
                              'date': datetime.now().strftime('%Y-%m-%d')
                          })
    assert response.status_code == 201
    data = response.json
    assert 'record' in data

def test_get_medical_records(client, auth_headers):
    """Test getting medical records"""
    # First add a record
    from datetime import datetime
    client.post('/api/user/medical-records',
               headers=auth_headers,
               json={
                   'title': 'Test Record',
                   'description': 'Test description',
                   'date': datetime.now().strftime('%Y-%m-%d')
               })
    
    # Get records
    response = client.get('/api/user/medical-records', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert 'records' in data
    assert len(data['records']) > 0

def test_delete_medical_record(client, auth_headers):
    """Test deleting a medical record"""
    from datetime import datetime
    
    # First add a record
    add_response = client.post('/api/user/medical-records',
                              headers=auth_headers,
                              json={
                                  'title': 'To Delete',
                                  'description': 'Will be deleted',
                                  'date': datetime.now().strftime('%Y-%m-%d')
                              })
    
    if add_response.status_code == 201:
        record_id = add_response.json['record']['id']
        
        # Delete it
        response = client.delete(f'/api/user/medical-records/{record_id}',
                               headers=auth_headers)
        assert response.status_code == 200
