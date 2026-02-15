import requests
import json

print("="*60)
print("Testing AI Chat with Severe Symptom + Location")
print("="*60)

try:
    # Login
    login_resp = requests.post('http://localhost:5000/api/auth/login', 
                               json={'email':'admin@nearbycare.com','password':'admin123'})
    token = login_resp.json()['token']
    print("\n✓ Logged in")
    
    # Test with severe chest pain and Delhi location
    chat_resp = requests.post('http://localhost:5000/api/symptom-chat',
                             json={
                                 'message': 'I have severe chest pain and difficulty breathing',
                                 'location': {'lat': 28.6139, 'lng': 77.2090},
                                 'chat_history': []
                             },
                             headers={'Authorization': f'Bearer {token}'})
    
    data = chat_resp.json()
    
    print("\n" + "="*60)
    print("AI RESPONSE (without asterisks):")
    print("="*60)
    print(data['response'][:300] + "...")
    
    print("\n" + "="*60)
    if 'suggested_hospitals' in data:
        print(f"✓ HOSPITALS FOUND: {len(data['suggested_hospitals'])} hospitals")
        print("="*60)
        for i, h in enumerate(data['suggested_hospitals'], 1):
            print(f"\n{i}. {h['name']}")
            print(f"   Distance: {h['distance']}")
            print(f"   Address: {h['address']}")
    else:
        print("✗ NO HOSPITALS IN RESPONSE")
        print("="*60)
        
except Exception as e:
    print(f"\n✗ Error: {e}")
