from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import os
import jwt
import bcrypt
import random
import string
from dotenv import load_dotenv
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nearby_care.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

db = SQLAlchemy(app)

# Google Places API Key
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', '')

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    searches = db.relationship('SearchHistory', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_address = db.Column(db.String(300))
    place_id = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
with app.app_context():
    db.create_all()

# Helper functions
def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP via email using plain SMTP"""
    try:
        sender_email = "nnearbycare@gmail.com"
        sender_password = "afstbmbkaizifiry"
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Nearby Care - Email Verification OTP"
        message["From"] = sender_email
        message["To"] = email
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #667eea; text-align: center;">🏥 Nearby Care</h2>
                    <h3 style="color: #333;">Email Verification</h3>
                    <p style="color: #666; font-size: 16px;">Thank you for registering with Nearby Care!</p>
                    <p style="color: #666; font-size: 16px;">Your OTP for email verification is:</p>
                    <div style="background-color: #667eea; color: white; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666; font-size: 14px;">This OTP will expire in 10 minutes.</p>
                    <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                    <hr style="border: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        © 2025 Nearby Care. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        
        print(f"Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def token_required(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user and send OTP"""
    try:
        data = request.json
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        print(f"Signup request: username={username}, email={email}")
        
        # Check if user already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': 'Email already registered'}), 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already taken'}), 400
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        print(f"Generated OTP: {otp_code}")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user (unverified)
        user = User(username=username, email=email, password_hash=password_hash, is_verified=False)
        db.session.add(user)
        db.session.flush()
        
        # Save OTP to database
        otp = OTP(email=email, otp_code=otp_code, expires_at=expires_at)
        db.session.add(otp)
        db.session.commit()
        
        print(f"User created and OTP saved to DB")
        
        # Send OTP email
        email_sent = send_otp_email(email, otp_code)
        
        return jsonify({
            'message': 'Registration successful! OTP sent to your email.',
            'email': email,
            'otp_debug': otp_code  # For testing - remove in production
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and activate user account"""
    try:
        data = request.json
        email = data.get('email')
        otp_code = data.get('otp')
        
        if not all([email, otp_code]):
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Find valid OTP
        otp = OTP.query.filter_by(
            email=email, 
            otp_code=otp_code, 
            is_used=False
        ).filter(OTP.expires_at > datetime.utcnow()).first()
        
        if not otp:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        
        # Mark OTP as used and verify user
        otp.is_used = True
        user.is_verified = True
        db.session.commit()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Email verified successfully!',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"OTP verification error: {str(e)}")
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP to user's email"""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        otp = OTP(email=email, otp_code=otp_code, expires_at=expires_at)
        db.session.add(otp)
        db.session.commit()
        
        if send_otp_email(email, otp_code):
            return jsonify({'message': 'OTP sent successfully!'}), 200
        else:
            return jsonify({'error': 'Failed to send OTP email'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login existing user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_verified:
            return jsonify({'error': 'Please verify your email first'}), 401
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Login error: {str(e)}'}), 500

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'is_verified': current_user.is_verified
    }), 200

# Hospital Search Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Nearby Care API is running'}), 200

@app.route('/api/search-hospitals-osm', methods=['POST'])
def search_hospitals_osm():
    """Search for hospitals using OpenStreetMap Overpass API (Free)"""
    try:
        data = request.json
        location = data.get('location')
        radius = data.get('radius', 5000)
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Use Nominatim to geocode the location
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        nominatim_params = {
            'q': location,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'NearbyCareApp/1.0'}
        
        nom_response = requests.get(nominatim_url, params=nominatim_params, headers=headers)
        nom_data = nom_response.json()
        
        if not nom_data:
            return jsonify({'error': 'Could not find location'}), 404
        
        lat = float(nom_data[0]['lat'])
        lon = float(nom_data[0]['lon'])
        
        # Query Overpass API for hospitals
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius},{lat},{lon});
          way["amenity"="hospital"](around:{radius},{lat},{lon});
          node["amenity"="clinic"](around:{radius},{lat},{lon});
          way["amenity"="clinic"](around:{radius},{lat},{lon});
        );
        out center;
        """
        
        overpass_response = requests.get(overpass_url, params={'data': overpass_query})
        overpass_data = overpass_response.json()
        
        # Format hospital data
        hospitals = []
        for element in overpass_data.get('elements', []):
            tags = element.get('tags', {})
            
            # Get coordinates
            if element['type'] == 'node':
                elem_lat = element['lat']
                elem_lon = element['lon']
            else:
                elem_lat = element.get('center', {}).get('lat')
                elem_lon = element.get('center', {}).get('lon')
            
            hospital = {
                'id': element['id'],
                'name': tags.get('name', 'Unnamed Hospital'),
                'address': tags.get('addr:full') or f"{tags.get('addr:street', '')}, {tags.get('addr:city', '')}".strip(', '),
                'latitude': elem_lat,
                'longitude': elem_lon,
                'phone': tags.get('phone'),
                'website': tags.get('website'),
                'emergency': tags.get('emergency'),
                'type': tags.get('amenity')
            }
            hospitals.append(hospital)
        
        # Save search history (if user is authenticated)
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.replace('Bearer ', '')
                decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = decoded['user_id']
                
                search_record = SearchHistory(
                    user_id=user_id,
                    location=location,
                    latitude=lat,
                    longitude=lon
                )
                db.session.add(search_record)
                db.session.commit()
            except:
                pass
        
        return jsonify({
            'location': location,
            'coordinates': {'lat': lat, 'lng': lon},
            'hospitals': hospitals,
            'count': len(hospitals)
        }), 200
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites', methods=['POST'])
@token_required
def add_favorite(current_user):
    """Add a hospital to favorites"""
    try:
        data = request.json
        
        favorite = Favorite(
            user_id=current_user.id,
            hospital_name=data['hospital_name'],
            hospital_address=data.get('hospital_address'),
            place_id=data.get('place_id'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Added to favorites', 'id': favorite.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites', methods=['GET'])
@token_required
def get_favorites(current_user):
    """Get all favorite hospitals"""
    try:
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        
        return jsonify([{
            'id': f.id,
            'hospital_name': f.hospital_name,
            'hospital_address': f.hospital_address,
            'place_id': f.place_id,
            'latitude': f.latitude,
            'longitude': f.longitude,
            'added_date': f.added_date.isoformat()
        } for f in favorites]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
@token_required
def delete_favorite(current_user, favorite_id):
    """Remove a hospital from favorites"""
    try:
        favorite = Favorite.query.filter_by(id=favorite_id, user_id=current_user.id).first_or_404()
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Removed from favorites'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-history', methods=['GET'])
@token_required
def get_search_history(current_user):
    """Get recent search history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        searches = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.search_date.desc()).limit(limit).all()
        
        return jsonify([{
            'id': s.id,
            'location': s.location,
            'latitude': s.latitude,
            'longitude': s.longitude,
            'search_date': s.search_date.isoformat()
        } for s in searches]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
