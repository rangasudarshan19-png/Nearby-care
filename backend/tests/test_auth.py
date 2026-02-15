"""
Test suite for authentication endpoints
"""
import json

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json
    assert data['status'] in ['healthy', 'degraded']
    assert 'checks' in data
    assert 'database' in data['checks']

def test_signup(client):
    """Test user registration"""
    response = client.post('/api/auth/signup', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.json
    assert 'message' in data
    assert 'email' in data

def test_signup_duplicate_email(client):
    """Test signup with duplicate email"""
    user_data = {
        'username': 'user1',
        'email': 'duplicate@example.com',
        'password': 'password123'
    }
    # First signup
    client.post('/api/auth/signup', json=user_data)
    
    # Second signup with same email
    response = client.post('/api/auth/signup', json=user_data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_login_success(client):
    """Test successful login"""
    # First create user
    client.post('/api/auth/signup', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'password123'
    })
    
    # Verify user (bypass OTP for testing)
    from app import User, db
    user = User.query.filter_by(email='login@example.com').first()
    user.is_verified = True
    db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'login@example.com',
        'password': 'password123'
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
