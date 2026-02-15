import requests
import json

print("Testing AI Chat...")

# Login
login_data = {
    "email": "admin@nearbycare.com",
    "password": "admin123"
}

try:
    print("\n1. Logging in...")
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    token = response.json()['token']
    print("   ✓ Login successful")
    
    print("\n2. Sending message to AI...")
    chat_data = {
        "message": "I have a mild headache",
        "location": None,
        "chat_history": []
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post('http://localhost:5000/api/symptom-chat', 
                            json=chat_data, 
                            headers=headers)
    
    print("\n" + "="*60)
    print("AI RESPONSE:")
    print("="*60)
    print(response.json()['response'])
    print("="*60)
    print("\n✓ AI Chat is working perfectly!")
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
