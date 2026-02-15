from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from functools import wraps
import requests

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        verified INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS otps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        code TEXT NOT NULL,
        expires TEXT NOT NULL,
        used INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        hospital_name TEXT NOT NULL,
        hospital_address TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        search_term TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

init_db()

# Helper functions
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    try:
        sender = "nnearbycare@gmail.com"
        password = "afst bmbk aizi fjry"
        
        msg = MIMEMultipart()
        msg["Subject"] = "Nearby Care - Verification Code"
        msg["From"] = sender
        msg["To"] = email
        
        html = f"""
        <div style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea;">🏥 Nearby Care</h2>
            <p>Your verification code is:</p>
            <h1 style="background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 8px; letter-spacing: 8px;">{otp}</h1>
            <p style="color: #666;">This code expires in 10 minutes.</p>
        </div>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            request.current_user_id = current_user_id
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'All fields required'}), 400
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400
        
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Username already taken'}), 400
        
        # Hash password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Create user
        c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                 (username, email, hashed))
        conn.commit()
        
        # Generate and save OTP
        otp = generate_otp()
        expires = (datetime.now() + timedelta(minutes=10)).isoformat()
        c.execute('INSERT INTO otps (email, code, expires) VALUES (?, ?, ?)',
                 (email, otp, expires))
        conn.commit()
        conn.close()
        
        # Send email
        send_otp_email(email, otp)
        
        return jsonify({
            'message': 'Signup successful! Check your email for OTP.',
            'otp_debug': otp  # Remove in production
        }), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.json
        email = data.get('email')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new OTP
        otp = generate_otp()
        expires = (datetime.now() + timedelta(minutes=10)).isoformat()
        c.execute('INSERT INTO otps (email, code, expires) VALUES (?, ?, ?)',
                 (email, otp, expires))
        conn.commit()
        conn.close()
        
        # Send email
        send_otp_email(email, otp)
        
        return jsonify({
            'message': 'OTP sent successfully!',
            'otp_debug': otp  # Remove in production
        }), 200
        
    except Exception as e:
        print(f"Resend OTP error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Find valid OTP
        c.execute('SELECT * FROM otps WHERE email = ? AND code = ? AND used = 0', (email, otp))
        otp_record = c.fetchone()
        
        if not otp_record:
            conn.close()
            return jsonify({'error': 'Invalid OTP'}), 400
        
        # Check if expired
        expires = datetime.fromisoformat(otp_record[3])
        if datetime.now() > expires:
            conn.close()
            return jsonify({'error': 'OTP expired'}), 400
        
        # Mark OTP as used and verify user
        c.execute('UPDATE otps SET used = 1 WHERE id = ?', (otp_record[0],))
        c.execute('UPDATE users SET verified = 1 WHERE email = ?', (email,))
        conn.commit()
        
        # Get user
        c.execute('SELECT id, username, email FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        # Generate token
        token = jwt.encode({
            'user_id': user[0],
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'Verification successful!',
            'token': token,
            'user': {'id': user[0], 'username': user[1], 'email': user[2]}
        }), 200
        
    except Exception as e:
        print(f"Verify error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if not user or not bcrypt.checkpw(password.encode(), user[3].encode()):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user[4]:  # verified column
            return jsonify({'error': 'Email not verified'}), 403
        
        # Generate token
        token = jwt.encode({
            'user_id': user[0],
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {'id': user[0], 'username': user[1], 'email': user[2]}
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-hospitals-osm', methods=['POST'])
@token_required
def search_hospitals():
    try:
        data = request.json
        area_name = data.get('area')
        radius_km = float(data.get('radius_km', 5))

        if not area_name:
            return jsonify({'error': 'Area name is required'}), 400

        # 1) Geocode area using Nominatim (OSM) to get lat/lon
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        geo_resp = requests.get(
            nominatim_url,
            params={
                'q': area_name,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': 'in'  # prefer India
            },
            headers={'User-Agent': 'nearby-care-app'}
        )

        if geo_resp.status_code != 200 or not geo_resp.json():
            return jsonify({'error': f'Area "{area_name}" not found'}), 404

        geo_data = geo_resp.json()[0]
        lat = float(geo_data['lat'])
        lon = float(geo_data['lon'])

        # 2) Query Overpass API for hospitals/clinics within radius
        overpass_url = "https://overpass-api.de/api/interpreter"
        radius_m = int(radius_km * 1000)
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          way["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="clinic"](around:{radius_m},{lat},{lon});
          way["amenity"="clinic"](around:{radius_m},{lat},{lon});
          node["healthcare"="hospital"](around:{radius_m},{lat},{lon});
          way["healthcare"="hospital"](around:{radius_m},{lat},{lon});
        );
        out center;
        """

        osm_resp = requests.post(overpass_url, data={'data': overpass_query}, headers={'User-Agent': 'nearby-care-app'}, timeout=30)

        hospitals = []
        if osm_resp.status_code == 200:
            osm_data = osm_resp.json()
            for element in osm_data.get('elements', []):
                tags = element.get('tags', {})

                if 'center' in element:
                    h_lat = element['center']['lat']
                    h_lon = element['center']['lon']
                elif 'lat' in element and 'lon' in element:
                    h_lat = element['lat']
                    h_lon = element['lon']
                else:
                    continue

                hospital = {
                    'id': element.get('id'),
                    'name': tags.get('name', 'Unnamed Hospital'),
                    'address': tags.get('addr:full') or tags.get('addr:street') or area_name,
                    'latitude': h_lat,
                    'longitude': h_lon,
                    'beds': tags.get('beds'),
                    'rating': tags.get('rating', 4.0),
                    'phone': tags.get('phone') or tags.get('contact:phone'),
                    'website': tags.get('website'),
                    'opening_hours': tags.get('opening_hours')
                }
                hospitals.append(hospital)

        # 3) Fallback dummy data if Overpass fails or returns empty
        if not hospitals:
            hospitals = [
                {
                    'id': 1,
                    'name': 'City General Hospital',
                    'address': f'{area_name}, Central Medical District',
                    'latitude': lat + 0.001,
                    'longitude': lon + 0.001,
                    'beds': 250,
                    'rating': 4.5,
                    'phone': '+91-9876543210',
                    'website': 'https://example-hospital.com'
                },
                {
                    'id': 2,
                    'name': 'Medical Care Center',
                    'address': f'{area_name}, Healthcare Plaza',
                    'latitude': lat - 0.001,
                    'longitude': lon - 0.001,
                    'beds': 150,
                    'rating': 4.2,
                    'phone': '+91-9876543211',
                    'website': 'https://example-medical.com'
                }
            ]

        return jsonify({
            'hospitals': hospitals,
            'coordinates': {'lat': lat, 'lon': lon},
            'area': area_name
        }), 200

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites', methods=['POST'])
@token_required
def add_favorite():
    try:
        data = request.json
        user_id = request.current_user_id
        
        hospital_name = data.get('hospital_name')
        hospital_address = data.get('hospital_address')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not all([hospital_name, hospital_address, latitude, longitude]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO favorites (user_id, hospital_name, hospital_address, latitude, longitude, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (user_id, hospital_name, hospital_address, latitude, longitude, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Added to favorites successfully'}), 201
    except Exception as e:
        print(f"Favorite error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites', methods=['GET'])
@token_required
def get_favorites():
    try:
        user_id = request.current_user_id
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM favorites WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        favorites = c.fetchall()
        conn.close()
        
        result = [
            {
                'id': f[0],
                'hospital_name': f[2],
                'hospital_address': f[3],
                'latitude': f[4],
                'longitude': f[5]
            } for f in favorites
        ]
        
        return jsonify({'favorites': result}), 200
    except Exception as e:
        print(f"Get favorites error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-history', methods=['POST'])
@token_required
def save_search_history():
    try:
        data = request.json
        user_id = request.current_user_id
        search_term = data.get('search_term')
        
        if not search_term:
            return jsonify({'error': 'Search term required'}), 400
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO search_history (user_id, search_term, created_at)
                    VALUES (?, ?, ?)''',
                 (user_id, search_term, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Search saved'}), 201
    except Exception as e:
        print(f"Search history error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-history', methods=['GET'])
@token_required
def get_search_history():
    try:
        user_id = request.current_user_id
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM search_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10', (user_id,))
        searches = c.fetchall()
        conn.close()
        
        result = [{'id': s[0], 'search_term': s[2], 'date': s[3]} for s in searches]
        
        return jsonify({'history': result}), 200
    except Exception as e:
        print(f"Get search history error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n✅ Server starting on http://localhost:5000")
    print("📍 Available Endpoints:")
    print("   - POST /api/signup")
    print("   - POST /api/verify-otp")
    print("   - POST /api/login")
    print("   - POST /api/search-hospitals-osm (protected)")
    print("   - POST /api/favorites (protected)")
    print("   - GET /api/favorites (protected)")
    print("   - POST /api/search-history (protected)")
    print("   - GET /api/search-history (protected)\n")
    app.run(debug=True, port=5000)
