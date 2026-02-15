from app import app
import json

with app.test_client() as client:
    payload = {
        'username': 'Abhi',
        'email': 'vabjeeth@gmail.com',
        'password': 'test123'
    }
    
    response = client.post(
        '/api/auth/signup',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    print('Status:', response.status_code)
    print('Response:', json.dumps(response.get_json(), indent=2))
