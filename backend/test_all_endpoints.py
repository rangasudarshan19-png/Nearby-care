"""
Comprehensive API endpoint test - tests ALL routes
Run: python test_all_endpoints.py
"""
import requests
import json
import sys
import time

BASE = "http://localhost:5000"
PASS = 0
FAIL = 0
RESULTS = []

def test(name, method, url, expected_status, token=None, json_data=None, retries=2):
    global PASS, FAIL
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    for attempt in range(retries + 1):
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=15)
            elif method == "POST":
                r = requests.post(url, headers=headers, json=json_data, timeout=15)
            elif method == "PUT":
                r = requests.put(url, headers=headers, json=json_data, timeout=15)
            elif method == "DELETE":
                r = requests.delete(url, headers=headers, json=json_data, timeout=15)
            
            status = "PASS" if r.status_code == expected_status else "FAIL"
            if status == "PASS":
                PASS += 1
            else:
                FAIL += 1
            
            RESULTS.append((name, status, r.status_code, expected_status))
            data = None
            try:
                data = r.json()
            except:
                pass
            
            icon = "OK" if status == "PASS" else "XX"
            print(f"  [{icon}] {name}: {r.status_code} (expected {expected_status})")
            return r.status_code, data
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            FAIL += 1
            RESULTS.append((name, "FAIL", str(e)[:60], expected_status))
            print(f"  [XX] {name}: ERROR - {str(e)[:80]}")
            return None, None

print("=" * 60)
print("NEARBY CARE - COMPREHENSIVE API TEST")
print("=" * 60)

# 1. Health Check
print("\n--- Health Check ---")
test("Health /api/health", "GET", f"{BASE}/api/health", 200)
test("Health /health", "GET", f"{BASE}/health", 200)

# 2. Signup
print("\n--- Auth: Signup ---")
status, data = test("Signup new user", "POST", f"{BASE}/api/auth/signup", 201, 
    json_data={"username": "apitest", "email": "apitest@test.com", "password": "password123"})

otp_code = data.get("otp_debug") if data else None
print(f"     OTP: {otp_code}")

test("Signup duplicate email", "POST", f"{BASE}/api/auth/signup", 400,
    json_data={"username": "apitest2", "email": "apitest@test.com", "password": "password123"})

test("Signup missing fields", "POST", f"{BASE}/api/auth/signup", 400,
    json_data={"username": "", "email": "", "password": ""})

# 3. Verify OTP
print("\n--- Auth: Verify OTP ---")
if otp_code:
    test("Verify OTP invalid", "POST", f"{BASE}/api/auth/verify-otp", 400,
        json_data={"email": "apitest@test.com", "otp": "000000"})
    
    status, data = test("Verify OTP valid", "POST", f"{BASE}/api/auth/verify-otp", 200,
        json_data={"email": "apitest@test.com", "otp": otp_code})

# 4. Login
print("\n--- Auth: Login ---")
test("Login wrong password", "POST", f"{BASE}/api/auth/login", 401,
    json_data={"email": "apitest@test.com", "password": "wrongpassword"})

test("Login non-existent", "POST", f"{BASE}/api/auth/login", 401,
    json_data={"email": "noexist@test.com", "password": "password123"})

status, data = test("Login valid", "POST", f"{BASE}/api/auth/login", 200,
    json_data={"email": "apitest@test.com", "password": "password123"})

TOKEN = data.get("token") if data else None
print(f"     Token obtained: {'Yes' if TOKEN else 'No'}")

# 5. Auth: Me
print("\n--- Auth: Me ---")
test("Get current user", "GET", f"{BASE}/api/auth/me", 200, token=TOKEN)
test("Get current user no token", "GET", f"{BASE}/api/auth/me", 401)

# 6. Profile
print("\n--- User Profile ---")
test("Get user profile", "GET", f"{BASE}/api/user/profile", 200, token=TOKEN)
test("Update name", "PUT", f"{BASE}/api/user/update-name", 200, token=TOKEN,
    json_data={"name": "API Test User"})
test("Change password", "POST", f"{BASE}/api/user/change-password", 200, token=TOKEN,
    json_data={"current_password": "password123", "new_password": "newpass123"})
# Change back
test("Change password back", "POST", f"{BASE}/api/user/change-password", 200, token=TOKEN,
    json_data={"current_password": "newpass123", "new_password": "password123"})

# 7. Medical Records
print("\n--- Medical Records ---")
test("Get medical records", "GET", f"{BASE}/api/user/medical-records", 200, token=TOKEN)
status, data = test("Add medical record", "POST", f"{BASE}/api/user/medical-records", 201, token=TOKEN,
    json_data={"title": "Blood Test", "description": "Routine CBC test", "date": "2026-01-15"})
record_id = data.get("record", {}).get("id") if data else None
if record_id:
    test("Delete medical record", "DELETE", f"{BASE}/api/user/medical-records/{record_id}", 200, token=TOKEN)

# 8. Doctors
print("\n--- Doctors ---")
test("Get all doctors", "GET", f"{BASE}/api/doctors", 200, token=TOKEN)
test("Get doctors by specialty", "GET", f"{BASE}/api/doctors?specialty=Cardiology", 200, token=TOKEN)
test("Get specialties", "GET", f"{BASE}/api/specialties", 200, token=TOKEN)
test("Get doctor details", "GET", f"{BASE}/api/doctors/1", 200, token=TOKEN)
test("Get available slots", "GET", f"{BASE}/api/doctors/1/available-slots?date=2026-02-20", 200, token=TOKEN)

# 9. Appointments
print("\n--- Appointments ---")
status, data = test("Book appointment", "POST", f"{BASE}/api/appointments", 201, token=TOKEN,
    json_data={"doctor_id": 1, "appointment_date": "2026-02-20", "appointment_time": "10:00",
               "symptoms": "Headache", "notes": "First visit"})
appt_id = data.get("appointment", {}).get("id") if data else None
test("Get appointments", "GET", f"{BASE}/api/appointments", 200, token=TOKEN)
if appt_id:
    test("Cancel appointment", "DELETE", f"{BASE}/api/appointments/{appt_id}", 200, token=TOKEN)

# 10. Hospital Search (depends on external Overpass API - may fail if API is down)
print("\n--- Hospital Search ---")
status, data = test("Search hospitals", "POST", f"{BASE}/api/search-hospitals-osm", 200, token=TOKEN,
    json_data={"lat": 17.385, "lon": 78.4867, "location": "Hyderabad", "radius": 5})
if status == 502:
    print("     (502 = External Overpass API error - not a backend bug)")

# 11. Search History
print("\n--- Search History ---")
test("Get search history", "GET", f"{BASE}/api/search-history?limit=10", 200, token=TOKEN)

# 12. Favorites
print("\n--- Favorites ---")
status, data = test("Add favorite", "POST", f"{BASE}/api/favorites", 201, token=TOKEN,
    json_data={"hospital_name": "Test Hospital", "hospital_address": "123 Test St",
               "place_id": "test_1", "latitude": 17.385, "longitude": 78.4867})
test("List favorites", "GET", f"{BASE}/api/favorites", 200, token=TOKEN)

# 13. Reviews
print("\n--- Reviews ---")
test("Create review", "POST", f"{BASE}/api/reviews", 201, token=TOKEN,
    json_data={"hospital_id": "test_hospital_1", "hospital_name": "Test Hospital",
               "hospital_address": "123 Test St", "latitude": 17.385, "longitude": 78.4867,
               "rating": 5, "comment": "Excellent service"})
test("Get reviews", "GET", f"{BASE}/api/reviews?hospital_id=test_hospital_1", 200)
test("Review summary", "GET", f"{BASE}/api/reviews/summary?hospital_id=test_hospital_1", 200)

# 14. Suggest Specialty
print("\n--- AI: Suggest Specialty ---")
test("Suggest specialty", "POST", f"{BASE}/api/suggest-specialty", 200, token=TOKEN,
    json_data={"symptoms": "chest pain and shortness of breath"})

# 15. Admin - Login as admin
print("\n--- Admin Auth ---")
status, data = test("Admin login", "POST", f"{BASE}/api/auth/login", 200,
    json_data={"email": "admin@nearbycare.com", "password": "admin123"})
ADMIN_TOKEN = data.get("token") if data else None
print(f"     Admin token: {'Yes' if ADMIN_TOKEN else 'No'}")

# 16. Admin Endpoints
if ADMIN_TOKEN:
    print("\n--- Admin Endpoints ---")
    test("Admin stats", "GET", f"{BASE}/api/admin/stats", 200, token=ADMIN_TOKEN)
    test("Admin users", "GET", f"{BASE}/api/admin/users", 200, token=ADMIN_TOKEN)
    test("Admin appointments", "GET", f"{BASE}/api/admin/appointments", 200, token=ADMIN_TOKEN)
    test("Admin reviews", "GET", f"{BASE}/api/admin/reviews", 200, token=ADMIN_TOKEN)
    test("Admin logs", "GET", f"{BASE}/api/admin/logs", 200, token=ADMIN_TOKEN)
    test("Admin announcements", "GET", f"{BASE}/api/admin/announcements", 200, token=ADMIN_TOKEN)

# Summary
print("\n" + "=" * 60)
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL} tests")
print("=" * 60)

if FAIL > 0:
    print("\nFailed tests:")
    for name, status, got, expected in RESULTS:
        if status == "FAIL":
            print(f"  - {name}: got {got}, expected {expected}")

sys.exit(0 if FAIL == 0 else 1)
