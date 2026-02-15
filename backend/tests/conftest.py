import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from config import config

@pytest.fixture
def client():
    """Create test client"""
    app.config.from_object(config['testing'])
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Get authorization headers for authenticated requests"""
    # Register and login to get token
    register_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    client.post('/api/auth/signup', json=register_data)
    
    # Verify OTP (in testing, we'd need to mock this or get from DB)
    # For now, manually verify the user
    from app import User
    user = User.query.filter_by(email='test@example.com').first()
    user.is_verified = True
    db.session.commit()
    
    # Login
    login_data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    response = client.post('/api/auth/login', json=login_data)
    token = response.json['token']
    
    return {'Authorization': f'Bearer {token}'}
