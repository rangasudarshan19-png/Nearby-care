import requests
import json

email = 'abijeethchari8080@gmail.com'
password = '123456'

print("="*60)
print("TESTING LOGIN WITH DIFFERENT EMAIL FORMATS")
print("="*60)

tests = [
    ('abijeethchari8080@gmail.com', '123456', 'Exact match'),
    ('ABIJEETHCHARI8080@GMAIL.COM', '123456', 'Uppercase'),
    ('  abijeethchari8080@gmail.com  ', '123456', 'With spaces'),
    ('AbijeethChari8080@Gmail.Com', '123456', 'Mixed case'),
]

for email_test, pwd, description in tests:
    r = requests.post('http://localhost:5000/api/auth/login', 
                     json={'email': email_test, 'password': pwd})
    status = "✅ SUCCESS" if r.status_code == 200 else f"❌ FAILED ({r.status_code})"
    print(f"{status} - {description}")
    if r.status_code != 200:
        print(f"  Error: {r.json().get('error', 'Unknown')}")

print("\n" + "="*60)
print("FINAL VERIFICATION")
print("="*60)
r = requests.post('http://localhost:5000/api/auth/login',
                 json={'email': 'abijeethchari8080@gmail.com', 'password': '123456'})
if r.status_code == 200:
    data = r.json()
    print("✅ LOGIN SUCCESSFUL!")
    print(f"   Username: {data['user']['username']}")
    print(f"   Email: {data['user']['email']}")
    print(f"   Token: {data['token'][:50]}...")
else:
    print(f"❌ Login failed: {r.json()}")
