from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import jwt
import bcrypt
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from functools import wraps
import cohere
import google.generativeai as genai
import json
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import func
from config import config

# Get environment (default to development)
env = os.getenv('FLASK_ENV', 'development')

# Initialize Flask app with config
app = Flask(__name__)
app.config.from_object(config[env])

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler(
    app.config['LOG_FILE'],
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
app.logger.addHandler(file_handler)
app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))

# Initialize AI APIs from config
COHERE_API_KEY = app.config.get('COHERE_API_KEY') or 'QoZJbghtZ8xKrATjrDfhVckWcE7hIOv4Gt8p9STV'
GEMINI_API_KEY = app.config.get('GOOGLE_API_KEY') or 'AIzaSyChPE050NNk3jakECiS-MK4PxrBzZJXcHg'

co = cohere.Client(COHERE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

app.logger.info(f'Starting Flask server in {env} mode...')

# CORS Configuration from config
CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')  # 'user', 'admin'
    status = db.Column(db.String(20), default='active')  # 'active', 'suspended', 'banned'
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    hospital_name = db.Column(db.String(255), nullable=False)
    hospital_address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Use OSM element id returned as 'id' by Overpass; store as string to be safe
    hospital_id = db.Column(db.String(64), nullable=False)
    hospital_name = db.Column(db.String(255))
    hospital_address = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.Text)
    moderated_by = db.Column(db.Integer)  # Admin user ID
    moderated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    qualifications = db.Column(db.String(255))
    experience_years = db.Column(db.Integer)
    consultation_fee = db.Column(db.Float)
    hospital_id = db.Column(db.String(64), nullable=False)  # OSM hospital ID
    hospital_name = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    available_days = db.Column(db.String(100))  # JSON string: ["Mon", "Tue", "Wed"]
    available_hours = db.Column(db.String(50))  # "09:00-17:00"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    hospital_id = db.Column(db.String(64), nullable=False)
    hospital_name = db.Column(db.String(255))
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)  # "10:00"
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)
    deleted_by = db.Column(db.Integer)  # Admin user ID who deleted
    deleted_at = db.Column(db.DateTime)
    deletion_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    blood_type = db.Column(db.String(5))  # A+, B-, O+, etc.
    allergies = db.Column(db.Text)  # Comma-separated or paragraph
    chronic_conditions = db.Column(db.Text)  # Comma-separated or paragraph
    emergency_contact = db.Column(db.String(150))
    emergency_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date of the medical event/test
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Admin Models
class AdminLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'delete_appointment', 'send_announcement', etc.
    target_type = db.Column(db.String(50))  # 'user', 'appointment', 'doctor', etc.
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)  # JSON details
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    recipient_type = db.Column(db.String(50))  # 'all', 'active', 'new', 'specific'
    recipient_ids = db.Column(db.Text)  # JSON array for specific users
    scheduled_at = db.Column(db.DateTime)  # NULL for immediate send
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'scheduled', 'sent', 'failed'
    recipients_count = db.Column(db.Integer, default=0)
    delivery_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DoctorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    hospital_name = db.Column(db.String(255))
    hospital_address = db.Column(db.Text)
    qualification = db.Column(db.String(255))
    experience_years = db.Column(db.Integer)
    consultation_fee = db.Column(db.Float)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    bio = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.String(10), nullable=False)  # "09:00"
    end_time = db.Column(db.String(10), nullable=False)  # "17:00"
    slot_duration = db.Column(db.Integer, default=30)  # minutes
    is_available = db.Column(db.Boolean, default=True)

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_by = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Helper functions
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_email(to_email, otp):
    try:
        # Read SMTP credentials from config
        sender = app.config['SMTP_SENDER']
        password = app.config['SMTP_APP_PASSWORD']

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Nearby Care - Email Verification"
        msg["From"] = sender
        msg["To"] = to_email
        
        html = f"""
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #0ea5e9;">Nearby Care</h2>
                <h3>Email Verification</h3>
                <p>Your OTP code is:</p>
                <div style="background: #0ea5e9; color: white; font-size: 32px; padding: 20px; text-align: center; border-radius: 8px;">
                    {otp}
                </div>
                <p>This code expires in 10 minutes.</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_otp_email(to_email, otp, purpose='signup'):
    """Send OTP email for various purposes"""
    try:
        sender = app.config['SMTP_SENDER']
        password = app.config['SMTP_APP_PASSWORD']

        # Customize subject and title based on purpose
        if purpose == 'email_verification':
            subject = "Nearby Care - Email Change Verification"
            title = "Email Change Verification"
            message = "You requested to change your email address. Use this OTP to verify your new email:"
        else:
            subject = "Nearby Care - Email Verification"
            title = "Email Verification"
            message = "Your OTP code is:"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        
        html = f"""
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #0ea5e9;">Nearby Care</h2>
                <h3>{title}</h3>
                <p>{message}</p>
                <div style="background: #0ea5e9; color: white; font-size: 32px; padding: 20px; text-align: center; border-radius: 8px;">
                    {otp}
                </div>
                <p>This code expires in 10 minutes.</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_appointment_email(to_email, appointment_data):
    """Send appointment confirmation email"""
    try:
        sender = app.config['SMTP_SENDER']
        password = app.config['SMTP_APP_PASSWORD']

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Appointment Confirmation - Nearby Care"
        msg["From"] = sender
        msg["To"] = to_email
        
        html = f"""
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #0ea5e9;">Nearby Care</h2>
                <h3>Appointment Confirmed!</h3>
                <div style="background: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Doctor:</strong> {appointment_data.get('doctor_name')}</p>
                    <p><strong>Hospital:</strong> {appointment_data.get('hospital_name')}</p>
                    <p><strong>Date:</strong> {appointment_data.get('date')}</p>
                    <p><strong>Time:</strong> {appointment_data.get('time')}</p>
                    <p><strong>Specialty:</strong> {appointment_data.get('specialty')}</p>
                </div>
                <p>Please arrive 15 minutes early for registration.</p>
                <p style="color: #718096; font-size: 12px;">If you need to cancel or reschedule, please contact us at least 24 hours in advance.</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            if current_user.status != 'active':
                return jsonify({'error': 'Account suspended or banned'}), 403
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(level='admin'):
    """
    Admin authentication decorator with role-based access control.
    Levels: 'admin' (admin only)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Token missing'}), 401
            
            try:
                if token.startswith('Bearer '):
                    token = token[7:]
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = User.query.get(data['user_id'])
                if not current_user:
                    return jsonify({'error': 'User not found'}), 401
                if current_user.status != 'active':
                    return jsonify({'error': 'Account suspended or banned'}), 403
                
                # Check admin access
                if current_user.role != 'admin':
                    return jsonify({'error': 'Admin access required'}), 403
                    
            except Exception as e:
                app.logger.error(f"Admin auth error: {str(e)}")
                return jsonify({'error': 'Invalid token'}), 401
            
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# Helper function to log admin actions
def log_admin_action(admin_id, action, target_type=None, target_id=None, details=None):
    """Log admin actions for audit trail"""
    try:
        ip_address = request.remote_addr if request else None
        admin_log = AdminLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address
        )
        db.session.add(admin_log)
        db.session.commit()
        app.logger.info(f"Admin action logged: {action} by admin {admin_id}")
    except Exception as e:
        app.logger.error(f"Failed to log admin action: {str(e)}")
        db.session.rollback()

# Cohere AI-powered hospital matching
def intelligent_ai_analysis(symptoms, hospitals_data):
    """
    Intelligent AI System with Load Balancing & Cascading Fallback
    
    Priority Order (based on free tier capacity & reliability):
    1. Google Gemini (60 req/min, 1M tokens/day, most reliable)
    2. Cohere (100 req/min trial, good backup)
    3. Keyword Matching (always works, instant)
    
    Returns: (hospitals_with_scores, ai_metadata)
    """
    print("\n" + "="*60)
    print("INTELLIGENT AI SYSTEM - Starting Analysis")
    print(f"Symptoms: {symptoms}")
    print(f"Hospitals: {len(hospitals_data)}")
    print("="*60)
    
    # Try Gemini first (best free tier)
    print("\n[1/3] Trying Google Gemini AI...")
    result, metadata = analyze_hospitals_with_gemini(symptoms, hospitals_data)
    if result is not None:
        print("✓ SUCCESS: Gemini AI analyzed hospitals")
        return result, metadata
    
    # Try Cohere as backup
    print("\n[2/3] Gemini failed, trying Cohere AI...")
    result, metadata = analyze_hospitals_with_cohere(symptoms, hospitals_data)
    if result is not None:
        print("✓ SUCCESS: Cohere AI analyzed hospitals")
        return result, metadata
    
    # Use keyword matching as final fallback
    print("\n[3/3] All AI providers failed, using Keyword Matching...")
    result, metadata = keyword_based_matching(symptoms, hospitals_data)
    print("✓ SUCCESS: Keyword matching completed")
    return result, metadata


def keyword_based_matching(symptoms, hospitals_data):
    """
    Fallback: Use keyword matching when AI fails or for quick results
    """
    symptoms_lower = symptoms.lower()
    
    # Symptom to specialty mapping
    symptom_map = {
        'heart': ['cardiology', 'cardiac', 'heart', 'cardiovascular'],
        'chest': ['cardiology', 'cardiac', 'emergency', 'general'],
        'tooth': ['dental', 'dentist', 'orthodont'],
        'teeth': ['dental', 'dentist', 'orthodont'],
        'dental': ['dental', 'dentist', 'orthodont'],
        'eye': ['ophthalmology', 'eye', 'vision', 'optometry'],
        'vision': ['ophthalmology', 'eye', 'optometry'],
        'skin': ['dermatology', 'skin', 'dermatologist'],
        'bone': ['orthopedic', 'orthopaedic', 'bone', 'fracture'],
        'fracture': ['orthopedic', 'orthopaedic', 'trauma', 'emergency'],
        'pregnancy': ['maternity', 'obstetric', 'gynecology', 'women'],
        'baby': ['pediatric', 'children', 'pediatrics'],
        'child': ['pediatric', 'children', 'pediatrics'],
        'mental': ['psychiatry', 'mental', 'psychology'],
        'depression': ['psychiatry', 'mental', 'psychology'],
        'cancer': ['oncology', 'cancer', 'tumor'],
        'kidney': ['nephrology', 'kidney', 'renal', 'dialysis'],
        'diabetes': ['endocrinology', 'diabetes', 'metabolic'],
        'stomach': ['gastroenterology', 'digestive', 'gastro', 'general'],
        'fever': ['general', 'internal medicine', 'emergency', 'infectious'],
        'cold': ['general', 'internal medicine', 'ent'],
        'cough': ['pulmonology', 'respiratory', 'general', 'chest'],
        'breathing': ['pulmonology', 'respiratory', 'emergency'],
        'surgery': ['surgery', 'surgical', 'general surgery'],
        'accident': ['emergency', 'trauma', 'orthopedic'],
        'injury': ['emergency', 'trauma', 'orthopedic'],
    }
    
    # Find relevant specialties
    relevant_specialties = set()
    for keyword, specialties in symptom_map.items():
        if keyword in symptoms_lower:
            relevant_specialties.update(specialties)
    
    # Score hospitals
    for hospital in hospitals_data:
        score = 0
        reasons = []
        
        name_lower = hospital['name'].lower()
        tags = hospital.get('tags', {})
        
        # Check hospital name for specialty keywords
        for specialty in relevant_specialties:
            if specialty in name_lower:
                score += 40
                reasons.append(f"Specializes in {specialty}")
                break
        
        # Check tags for specialty
        if tags:
            speciality_tag = tags.get('healthcare:speciality', '').lower()
            healthcare_tag = tags.get('healthcare', '').lower()
            amenity_tag = tags.get('amenity', '').lower()
            
            for specialty in relevant_specialties:
                if specialty in speciality_tag or specialty in healthcare_tag or specialty in amenity_tag:
                    score += 35
                    reasons.append(f"Tagged as {specialty}")
                    break
        
        # Emergency keywords get high score for urgent symptoms
        urgent_keywords = ['emergency', 'trauma', 'accident', 'injury', 'severe', 'urgent']
        if any(kw in symptoms_lower for kw in urgent_keywords):
            if 'emergency' in name_lower or tags.get('emergency') == 'yes':
                score += 25
                reasons.append("Has emergency services")
        
        # Give base score to general hospitals
        if score == 0:
            if 'hospital' in name_lower or tags.get('amenity') == 'hospital':
                score = 30
                reasons.append("General hospital facility")
            elif 'clinic' in name_lower or tags.get('amenity') == 'clinic':
                score = 25
                reasons.append("General clinic facility")
        
        # Normalize to 0-1 range
        hospital['ai_score'] = min(score / 100.0, 1.0)
        hospital['ai_reason'] = reasons[0] if reasons else 'General healthcare facility'
        hospital['ai_reasons'] = [{'text': r, 'score': score} for r in reasons]
    
    return hospitals_data, {
        'enabled': True,
        'method': 'keyword_matching',
        'analyzed_count': len(hospitals_data)
    }


def analyze_hospitals_with_gemini(symptoms, hospitals_data):
    """
    Use Google Gemini AI (PRIORITY #1 - Best free tier, 60 req/min, 1M tokens/day)
    """
    try:
        print(f"\n=== GEMINI AI ANALYSIS (Primary) ===")
        print(f"Symptoms: {symptoms}")
        print(f"Hospitals to analyze: {len(hospitals_data)}")
        
        if not symptoms or not hospitals_data:
            return hospitals_data, None
        
        # Prepare concise hospital list
        hospital_list = []
        for idx, h in enumerate(hospitals_data):
            info = f"{idx}: {h['name']}"
            if h.get('tags'):
                tags = h['tags']
                specs = []
                if tags.get('healthcare:speciality'):
                    specs.append(f"Spec: {tags['healthcare:speciality']}")
                if tags.get('healthcare'):
                    specs.append(f"Type: {tags['healthcare']}")
                if specs:
                    info += f" ({', '.join(specs)})"
            hospital_list.append(info)
        
        prompt = f"""You are a medical AI assistant. Match patient symptoms to the best hospitals.

PATIENT SYMPTOMS: {symptoms}

HOSPITALS:
{chr(10).join(hospital_list)}

TASK: Score each hospital 0-100 based on suitability for these symptoms.

Rules:
- Specialized hospitals (e.g., "Dental Clinic" for tooth pain) = 80-100
- General hospitals that can treat it = 60-79  
- Basic facilities that might help = 40-59
- Not suitable = 0-39

RESPOND ONLY WITH JSON (no markdown, no extra text):
{{
  "scores": [
    {{"index": 0, "score": 85, "reason": "Perfect match - dental specialist"}},
    {{"index": 1, "score": 65, "reason": "General hospital with dental dept"}}
  ]
}}

Score all {len(hospitals_data)} hospitals."""

        # Use Gemini Pro (free tier)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise Exception("Empty response from Gemini")
        
        print(f"Gemini response: {response.text[:200]}")
        
        # Parse JSON from response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        scores = result.get('scores', [])
        
        print(f"Parsed {len(scores)} scores from Gemini")
        
        # Apply scores
        for item in scores:
            idx = item.get('index', -1)
            score = item.get('score', 0)
            reason = item.get('reason', '')
            
            if 0 <= idx < len(hospitals_data):
                hospitals_data[idx]['ai_score'] = score / 100.0
                hospitals_data[idx]['ai_reason'] = reason
                hospitals_data[idx]['ai_reasons'] = [{'text': reason, 'score': score}]
        
        # Sort by AI score
        hospitals_data.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        
        print(f"=== GEMINI SUCCESS ===\n")
        return hospitals_data, {
            'enabled': True,
            'method': 'gemini_ai',
            'model': 'gemini-pro',
            'analyzed_count': len(scores)
        }
        
    except Exception as e:
        print(f"GEMINI AI ERROR: {e}")
        return None, None  # Signal to try next provider


def analyze_hospitals_with_cohere(symptoms, hospitals_data):
    """
    Use Cohere AI (BACKUP #2 - 100 req/min trial, good for backup)
    """
    try:
        print(f"\n=== COHERE AI ANALYSIS (Backup) ===")
        print(f"Symptoms: {symptoms}")
        print(f"Number of hospitals: {len(hospitals_data)}")
        
        if not symptoms or not hospitals_data:
            print("No symptoms or no hospitals - skipping AI")
            return hospitals_data, None
        
        # Prepare hospital information for Cohere (simpler format for better AI matching)
        hospital_descriptions = []
        for idx, h in enumerate(hospitals_data):
            desc = f"Hospital {idx+1}: {h['name']}"
            
            # Add any available tags/specialties
            if h.get('tags'):
                tags = h['tags']
                details = []
                if 'healthcare:speciality' in tags:
                    details.append(f"Speciality: {tags['healthcare:speciality']}")
                if 'healthcare' in tags:
                    details.append(f"Type: {tags['healthcare']}")
                if 'amenity' in tags:
                    details.append(f"Amenity: {tags['amenity']}")
                if 'emergency' in tags:
                    details.append(f"Emergency: {tags['emergency']}")
                if details:
                    desc += f" | {' | '.join(details)}"
            
            hospital_descriptions.append(desc)
        
        print(f"Hospital descriptions prepared: {len(hospital_descriptions)}")
        
        # Create prompt for Cohere
        prompt = f"""You are a medical assistant helping patients find the right hospital based on their symptoms.

Patient's Symptoms: {symptoms}

Available Hospitals in the area:
{chr(10).join(hospital_descriptions)}

TASK: Analyze each hospital and score how suitable it is for treating the patient's symptoms.

IMPORTANT:
- If a hospital name mentions a specialty (e.g., "Cardiac Center"), give it high score for related symptoms
- If hospital has speciality tags, match them to symptoms
- If no specialty info, give moderate score for general hospitals
- Emergency-capable hospitals good for urgent symptoms

Respond in strict JSON format:
{{
  "recommendations": [
    {{"hospital_index": 0, "score": 85, "reason": "Cardiac center perfect for chest pain"}},
    {{"hospital_index": 1, "score": 60, "reason": "General hospital, can handle basic cases"}}
  ],
  "general_advice": "Suggest alternatives only if NO hospital scores above 60",
  "no_match_found": false
}}

Score ALL {len(hospitals_data)} hospitals. Use 0-100 where:
- 80-100: Highly specialized for these symptoms
- 60-79: Good match, can treat this
- 40-59: General facility, may help
- 0-39: Not suitable for these symptoms"""

        print("Calling Cohere API with command model...")
        
        # Try different models in order of preference
        models_to_try = ['command', 'command-light', 'command-nightly']
        response = None
        
        for model in models_to_try:
            try:
                print(f"Trying model: {model}")
                response = co.chat(
                    message=prompt,
                    model=model,
                    temperature=0.3,
                    max_tokens=1500
                )
                print(f"Success with model: {model}")
                break
            except Exception as model_error:
                print(f"Model {model} failed: {model_error}")
                continue
        
        if not response:
            print("All Cohere models failed, falling back to keyword matching")
            return keyword_based_matching(symptoms, hospitals_data)
        
        ai_text = response.text
        print(f"Cohere response received: {len(ai_text)} characters")
        print(f"First 200 chars: {ai_text[:200]}")
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            start = ai_text.find('{')
            end = ai_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = ai_text[start:end]
                ai_result = json.loads(json_str)
                print(f"Successfully parsed JSON")
            else:
                print("ERROR: No JSON found in response")
                ai_result = json.loads(ai_text)
        except Exception as parse_err:
            print(f"JSON parse error: {parse_err}")
            # Fallback if JSON parsing fails
            return hospitals_data, {
                'error': 'Could not parse AI response',
                'raw_response': ai_text[:500],
                'enabled': False
            }
        
        # Apply AI scores to hospitals
        recommendations = ai_result.get('recommendations', [])
        print(f"Got {len(recommendations)} recommendations")
        
        for rec in recommendations:
            idx = rec.get('hospital_index', -1)
            score = rec.get('score', 0)
            reason = rec.get('reason', '')
            
            if 0 <= idx < len(hospitals_data):
                hospitals_data[idx]['ai_score'] = score / 100.0  # Normalize to 0-1
                hospitals_data[idx]['ai_reason'] = reason
                hospitals_data[idx]['ai_reasons'] = [{'text': reason, 'score': score}]
                print(f"  Hospital {idx}: {hospitals_data[idx]['name']} = {score}% - {reason[:50]}")
        
        # Sort by AI score (highest first)
        hospitals_data.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        print(f"Hospitals sorted by AI score")
        
        # Prepare AI metadata
        ai_meta = {
            'enabled': True,
            'method': 'cohere_ai',
            'model': 'command',
            'no_match_found': ai_result.get('no_match_found', False),
            'general_advice': ai_result.get('general_advice', ''),
            'analyzed_count': len(recommendations)
        }
        
        print(f"=== COHERE SUCCESS ===\n")
        return hospitals_data, ai_meta
        
    except Exception as e:
        print(f"COHERE AI ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None  # Signal to try next provider

# Routes

@app.route('/api/search-hospitals-osm', methods=['POST'])
@token_required
def search_hospitals_osm(current_user):
    try:
        data = request.json or {}
        query = data.get('query') or data.get('location')
        lat = data.get('lat')
        lon = data.get('lon')
        symptoms_text = data.get('symptoms')
        radius_km = float(data.get('radius', 5))
        
        # Advanced filters
        hospital_type = data.get('hospitalType', '')
        emergency_only = data.get('emergencyOnly', False)
        min_rating = float(data.get('minRating', 0)) if data.get('minRating') else 0
        specialty = data.get('specialty', '')
        amenities = data.get('amenities', [])
        ownership = data.get('ownership', '')
        
        print(f"\n=== HOSPITAL SEARCH REQUEST ===")
        print(f"Location: {query}")
        print(f"Symptoms received: '{symptoms_text}'")
        print(f"Symptoms type: {type(symptoms_text)}")
        print(f"Symptoms is empty: {not symptoms_text}")
        print(f"Symptoms after strip: '{symptoms_text.strip() if symptoms_text else None}'")
        print(f"Radius: {radius_km} km")
        print(f"Advanced Filters: type={hospital_type}, emergency={emergency_only}, rating={min_rating}, specialty={specialty}, amenities={amenities}, ownership={ownership}")
        
        if not (query or (lat is not None and lon is not None)):
            return jsonify({'error': 'Location query or lat/lon required'}), 400

        # 1) Geocode location via Nominatim
        if lat is None or lon is None:
            nominatim_url = 'https://nominatim.openstreetmap.org/search'
            geo_res = requests.get(
                nominatim_url,
                params={'q': query, 'format': 'json', 'limit': 1},
                headers={'User-Agent': 'nearby-care-app'}
            )
            geo_res.raise_for_status()
            geo_data = geo_res.json()
            if not geo_data:
                return jsonify({'error': 'Location not found'}), 404
            lat = float(geo_data[0]['lat'])
            lon = float(geo_data[0]['lon'])
        else:
            lat = float(lat)
            lon = float(lon)

        # 2) Overpass query for hospitals within radius
        radius_m = int(radius_km * 1000)
        
        # Check if searching for dental/tooth related symptoms
        dental_keywords = ['tooth', 'teeth', 'dental', 'gum', 'cavity', 'toothache', 'dentist']
        is_dental = any(keyword in symptoms_text.lower() for keyword in dental_keywords) if symptoms_text else False
        
        if is_dental:
            # Search specifically for dental clinics/dentists
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="dentist"](around:{radius_m},{lat},{lon});
              way["amenity"="dentist"](around:{radius_m},{lat},{lon});
              node["healthcare"="dentist"](around:{radius_m},{lat},{lon});
              way["healthcare"="dentist"](around:{radius_m},{lat},{lon});
              node["amenity"="clinic"]["healthcare:speciality"~"dental",i](around:{radius_m},{lat},{lon});
              way["amenity"="clinic"]["healthcare:speciality"~"dental",i](around:{radius_m},{lat},{lon});
            );
            out center tags;
            """
        else:
            # General hospital search
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="hospital"](around:{radius_m},{lat},{lon});
              way["amenity"="hospital"](around:{radius_m},{lat},{lon});
              node["healthcare"="hospital"](around:{radius_m},{lat},{lon});
              way["healthcare"="hospital"](around:{radius_m},{lat},{lon});
              node["amenity"="clinic"](around:{radius_m},{lat},{lon});
              way["amenity"="clinic"](around:{radius_m},{lat},{lon});
            );
            out center tags;
            """
        ov_res = requests.post(
            'https://overpass-api.de/api/interpreter',
            data=overpass_query,
            headers={'User-Agent': 'nearby-care-app'}
        )
        ov_res.raise_for_status()
        ov_data = ov_res.json()
        
        # 3) Build hospital list with tags
        hospitals = []
        for el in ov_data.get('elements', []):
            tags = el.get('tags', {})
            name = tags.get('name') or 'Unnamed Hospital'
            address_parts = [
                tags.get('addr:housenumber'),
                tags.get('addr:street'),
                tags.get('addr:city'),
                tags.get('addr:state'),
                tags.get('addr:postcode')
            ]
            address = ' '.join([p for p in address_parts if p]) or tags.get('addr:full') or 'Address not available'
            if 'center' in el:
                hlat = el['center']['lat']
                hlon = el['center']['lon']
            else:
                hlat = el.get('lat')
                hlon = el.get('lon')
            
            hospitals.append({
                'id': el.get('id'),
                'name': name,
                'address': address,
                'latitude': hlat,
                'longitude': hlon,
                'tags': tags,  # Keep tags for Cohere AI and filtering
                'rating': float(tags.get('rating', tags.get('stars', 0))) or 0.0,  # OSM rating if available
                'ai_score': 0.0,
                'ai_reasons': [],
                'ai_reason': ''
            })

        # 4) Save to search history
        hist = SearchHistory(
            user_id=current_user.id,
            location=query or 'GPS',
            latitude=lat,
            longitude=lon
        )
        db.session.add(hist)
        db.session.commit()

        # 5) Calculate distance for all hospitals
        from math import radians, sin, cos, sqrt, atan2
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        for h in hospitals:
            h['distance'] = haversine(lat, lon, h['latitude'], h['longitude'])
        
        # 6) Apply advanced filters
        filtered_hospitals = []
        for h in hospitals:
            tags = h.get('tags', {})
            
            # Filter by hospital type
            if hospital_type:
                amenity = tags.get('amenity', '').lower()
                healthcare = tags.get('healthcare', '').lower()
                if hospital_type == 'hospital' and not (amenity == 'hospital' or healthcare == 'hospital'):
                    continue
                elif hospital_type == 'clinic' and not (amenity == 'clinic'):
                    continue
                elif hospital_type == 'doctors' and not (amenity == 'doctors' or 'medical' in amenity or 'medical' in healthcare):
                    continue
            
            # Filter by emergency services
            if emergency_only:
                emergency = tags.get('emergency', '').lower()
                if emergency != 'yes' and emergency != 'true':
                    continue
            
            # Filter by specialty
            if specialty:
                speciality_tags = tags.get('healthcare:speciality', '').lower()
                name_lower = h['name'].lower()
                if specialty == 'cardiac' and not ('cardiac' in speciality_tags or 'cardio' in name_lower or 'heart' in name_lower):
                    continue
                elif specialty == 'orthopedic' and not ('orthopedic' in speciality_tags or 'ortho' in name_lower or 'bone' in name_lower):
                    continue
                elif specialty == 'dental' and not ('dental' in speciality_tags or 'dentist' in name_lower or 'tooth' in name_lower):
                    continue
                elif specialty == 'pediatric' and not ('pediatric' in speciality_tags or 'paediatric' in speciality_tags or 'child' in name_lower or 'kids' in name_lower):
                    continue
                elif specialty == 'maternity' and not ('maternity' in speciality_tags or 'obstetric' in speciality_tags or 'maternity' in name_lower or 'women' in name_lower):
                    continue
                elif specialty == 'neurology' and not ('neurology' in speciality_tags or 'neuro' in name_lower or 'brain' in name_lower):
                    continue
                elif specialty == 'oncology' and not ('oncology' in speciality_tags or 'cancer' in name_lower):
                    continue
                elif specialty == 'ophthalmology' and not ('ophthalmology' in speciality_tags or 'eye' in name_lower or 'vision' in name_lower):
                    continue
                elif specialty == 'ent' and not ('ent' in speciality_tags or 'ear' in name_lower or 'nose' in name_lower or 'throat' in name_lower):
                    continue
                elif specialty == 'dermatology' and not ('dermatology' in speciality_tags or 'skin' in name_lower or 'derma' in name_lower):
                    continue
            
            # Filter by amenities
            if amenities:
                has_all_amenities = True
                for amenity in amenities:
                    if amenity == 'icu':
                        if not (tags.get('icu', '').lower() == 'yes' or 'icu' in h['name'].lower()):
                            has_all_amenities = False
                            break
                    elif amenity == 'parking':
                        if not (tags.get('parking', '').lower() == 'yes' or tags.get('parking:fee', '')):
                            has_all_amenities = False
                            break
                    elif amenity == 'pharmacy':
                        if not (tags.get('pharmacy', '').lower() == 'yes' or 'pharmacy' in h['name'].lower()):
                            has_all_amenities = False
                            break
                    elif amenity == 'lab':
                        if not (tags.get('lab', '').lower() == 'yes' or 'lab' in h['name'].lower() or 'diagnostic' in h['name'].lower()):
                            has_all_amenities = False
                            break
                if not has_all_amenities:
                    continue
            
            # Filter by ownership
            if ownership:
                operator = tags.get('operator', '').lower()
                operator_type = tags.get('operator:type', '').lower()
                name_lower = h['name'].lower()
                if ownership == 'government' and not ('government' in operator or 'govt' in name_lower or 'public' in operator_type):
                    continue
                elif ownership == 'private' and not ('private' in operator or 'private' in name_lower or 'pvt' in name_lower):
                    continue
                elif ownership == 'multispecialty' and not ('multi' in name_lower or 'super' in name_lower):
                    continue
            
            # Filter by minimum rating
            if min_rating > 0:
                # Get rating from reviews in database
                reviews = Review.query.filter_by(hospital_id=str(h['id'])).all()
                if reviews:
                    avg_rating = sum(r.rating for r in reviews) / len(reviews)
                    h['rating'] = avg_rating
                else:
                    # Use OSM rating if no reviews
                    h['rating'] = h.get('rating', 0)
                
                if h['rating'] < min_rating:
                    continue
            
            filtered_hospitals.append(h)
        
        hospitals = filtered_hospitals
        print(f"After filtering: {len(hospitals)} hospitals remaining")
        
        # 7) Use Intelligent AI System if symptoms provided
        ai = None
        if symptoms_text and symptoms_text.strip():
            # Limit to top 50 hospitals by distance to avoid timeout and API limits
            hospitals_for_ai = sorted(hospitals, key=lambda x: x.get('distance', 999))[:50]
            print(f"\nSending {len(hospitals_for_ai)} closest hospitals to AI (out of {len(hospitals)} total)")
            hospitals_for_ai, ai = intelligent_ai_analysis(symptoms_text, hospitals_for_ai)
            
            # Merge AI scores back into full hospital list
            ai_scores = {h['id']: {'ai_score': h.get('ai_score', 0), 'ai_reason': h.get('ai_reason', ''), 'ai_reasons': h.get('ai_reasons', [])} 
                        for h in hospitals_for_ai}
            for h in hospitals:
                if h['id'] in ai_scores:
                    h.update(ai_scores[h['id']])
            
            print(f"AI Method Used: {ai.get('method', 'unknown')}")
        
        # 8) Handle sorting
        sort_by = data.get('sortBy', 'nearby')
        if sort_by == 'ai_score' and symptoms_text:
            hospitals.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        elif sort_by == 'rating':
            # Calculate ratings for sorting if not already done
            for h in hospitals:
                if 'rating' not in h or h.get('rating', 0) == 0:
                    reviews = Review.query.filter_by(hospital_id=str(h['id'])).all()
                    if reviews:
                        h['rating'] = sum(r.rating for r in reviews) / len(reviews)
            hospitals.sort(key=lambda x: x.get('rating', 0), reverse=True)
        elif sort_by == 'name':
            hospitals.sort(key=lambda x: x.get('name', '').lower())
        else:  # Default: nearby (distance)
            hospitals.sort(key=lambda x: x.get('distance', 999))
        
        # Remove tags from final response (not needed in frontend)
        for h in hospitals:
            h.pop('tags', None)

        return jsonify({
            'hospitals': hospitals,
            'coordinates': {'lat': lat, 'lon': lon},
            'ai': ai
        })
    except requests.HTTPError as e:
        return jsonify({'error': f'API error: {e}'}), 502
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to search hospitals'}), 500

@app.route('/api/favorites', methods=['POST'])
@token_required
def add_favorite(current_user):
    try:
        data = request.json or {}
        fav = Favorite(
            user_id=current_user.id,
            hospital_name=data.get('hospital_name'),
            hospital_address=data.get('hospital_address'),
            latitude=float(data.get('latitude')),
            longitude=float(data.get('longitude'))
        )
        db.session.add(fav)
        db.session.commit()
        return jsonify({'message': 'Added to favorites'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add favorite'}), 500

@app.route('/api/favorites', methods=['GET'])
@token_required
def list_favorites(current_user):
    items = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    return jsonify([
        {
            'id': i.id,
            'hospital_name': i.hospital_name,
            'hospital_address': i.hospital_address,
            'latitude': i.latitude,
            'longitude': i.longitude,
            'created_at': i.created_at.isoformat()
        } for i in items
    ])

@app.route('/api/search-history', methods=['GET'])
@token_required
def get_history(current_user):
    limit = int(request.args.get('limit', 20))
    items = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.search_date.desc()).limit(limit).all()
    return jsonify([
        {
            'id': h.id,
            'location': h.location,
            'latitude': h.latitude,
            'longitude': h.longitude,
            'search_date': h.search_date.isoformat()
        } for h in items
    ])

# Reviews API
@app.route('/api/reviews', methods=['GET'])
def list_reviews():
    hospital_id = request.args.get('hospital_id')
    if not hospital_id:
        return jsonify({'error': 'hospital_id is required'}), 400
    items = Review.query.filter_by(hospital_id=str(hospital_id)).order_by(Review.created_at.desc()).all()
    return jsonify([
        {
            'id': r.id,
            'hospital_id': r.hospital_id,
            'user_id': r.user_id,
            'username': User.query.get(r.user_id).username if User.query.get(r.user_id) else 'Unknown',
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat()
        } for r in items
    ])

@app.route('/api/reviews', methods=['POST'])
@token_required
def create_review(current_user):
    try:
        data = request.json or {}
        hospital_id = data.get('hospital_id')
        rating = int(data.get('rating', 0))
        comment = (data.get('comment') or '').strip()
        if not hospital_id:
            return jsonify({'error': 'hospital_id is required'}), 400
        if rating < 1 or rating > 5:
            return jsonify({'error': 'rating must be between 1 and 5'}), 400

        r = Review(
            hospital_id=str(hospital_id),
            hospital_name=data.get('hospital_name'),
            hospital_address=data.get('hospital_address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            user_id=current_user.id,
            rating=rating,
            comment=comment
        )
        db.session.add(r)
        db.session.commit()
        return jsonify({'message': 'Review added', 'id': r.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add review'}), 500

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@token_required
def delete_review(current_user, review_id):
    r = Review.query.get(review_id)
    if not r:
        return jsonify({'error': 'Review not found'}), 404
    if not (current_user.is_admin or r.user_id == current_user.id):
        return jsonify({'error': 'Not authorized'}), 403
    db.session.delete(r)
    db.session.commit()
    return jsonify({'message': 'Review deleted'}), 200

@app.route('/api/reviews/summary', methods=['GET'])
def review_summary():
    hospital_id = request.args.get('hospital_id')
    if not hospital_id:
        return jsonify({'error': 'hospital_id is required'}), 400
    q = Review.query.filter_by(hospital_id=str(hospital_id))
    count = q.count()
    avg = 0.0
    if count:
        total = sum([r.rating for r in q.all()])
        avg = round(total / count, 2)
    return jsonify({'count': count, 'average': avg})

# Symptom-based specialty suggestions (rule-based MVP)
@app.route('/api/suggest-specialty', methods=['POST'])
def suggest_specialty():
    data = request.json or {}
    text = (data.get('symptoms') or '').lower()
    if not text:
        return jsonify({'error': 'symptoms text is required'}), 400

    rules = [
        {
            'keywords': ['chest pain', 'palpitations', 'shortness of breath', 'hypertension', 'heart'],
            'specialty': 'Cardiology',
            'hospital_types': ['Cardiac hospital', 'Multispecialty with cardiology'],
        },
        {
            'keywords': ['fever', 'cough', 'cold', 'flu', 'infection'],
            'specialty': 'Internal Medicine',
            'hospital_types': ['General hospital', 'Clinic'],
        },
        {
            'keywords': ['fracture', 'joint pain', 'back pain', 'sports injury'],
            'specialty': 'Orthopedics',
            'hospital_types': ['Orthopedic hospital', 'Multispecialty with orthopedics'],
        },
        {
            'keywords': ['skin rash', 'acne', 'itching', 'eczema'],
            'specialty': 'Dermatology',
            'hospital_types': ['Skin clinic', 'Multispecialty with dermatology'],
        },
        {
            'keywords': ['abdominal pain', 'diarrhea', 'vomiting', 'constipation', 'ulcer'],
            'specialty': 'Gastroenterology',
            'hospital_types': ['Gastro clinic', 'Multispecialty with gastroenterology'],
        },
        {
            'keywords': ['headache', 'migraine', 'seizure', 'numbness', 'stroke'],
            'specialty': 'Neurology',
            'hospital_types': ['Neuro hospital', 'Multispecialty with neurology'],
        },
        {
            'keywords': ['pregnancy', 'gyne', 'period', 'pcos', 'infertility'],
            'specialty': 'Obstetrics & Gynecology',
            'hospital_types': ['Women’s hospital', 'Multispecialty with OBGYN'],
        },
        {
            'keywords': ['child', 'pediatric', 'baby', 'newborn', 'vaccination'],
            'specialty': 'Pediatrics',
            'hospital_types': ['Children’s hospital', 'Multispecialty with pediatrics'],
        },
        {
            'keywords': ['diabetes', 'thyroid', 'hormone'],
            'specialty': 'Endocrinology',
            'hospital_types': ['Endocrine clinic', 'Multispecialty with endocrinology'],
        },
    ]

    matches = []
    for r in rules:
        score = sum([1 for k in r['keywords'] if k in text])
        if score:
            matches.append({
                'specialty': r['specialty'],
                'hospital_types': r['hospital_types'],
                'confidence': min(0.9, 0.2 * score)
            })

    if not matches:
        matches.append({
            'specialty': 'General Practice',
            'hospital_types': ['General hospital', 'Clinic'],
            'confidence': 0.3
        })

    return jsonify({
        'suggestions': matches,
        'disclaimer': 'Suggestions are informational only and not medical advice. Please consult a qualified healthcare professional for diagnosis and treatment.'
    })
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.json or {}
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        
        if not all([username, email, password]):
            return jsonify({'error': 'All fields required'}), 400
        
        # Check existing
        if User.query.filter(func.lower(User.email) == email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user = User(username=username, email=email, password_hash=password_hash, is_verified=False)
        db.session.add(user)
        db.session.flush()
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        otp = OTP(email=email, otp_code=otp_code, expires_at=expires_at)
        db.session.add(otp)
        db.session.commit()
        
        # Send email
        email_sent = send_email(email, otp_code)
        
        # Log OTP for debugging when email fails
        if not email_sent:
            print(f"\n{'='*50}")
            print(f"⚠️  EMAIL FAILED - OTP for {email}: {otp_code}")
            print(f"{'='*50}\n")
        
        return jsonify({
            'message': 'Registration successful! Check your email for OTP.' if email_sent else 'Registration successful! Check console for OTP (email failed).',
            'email': email,
            'otp_debug': otp_code,
            'email_sent': email_sent
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Signup error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json or {}
        email = (data.get('email') or '').strip().lower()
        otp_code = data.get('otp')
        
        if not all([email, otp_code]):
            return jsonify({'error': 'Email and OTP required'}), 400
        
        user = User.query.filter(func.lower(User.email) == email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        otp = OTP.query.filter_by(
            email=email,
            otp_code=otp_code,
            is_used=False
        ).filter(OTP.expires_at > datetime.utcnow()).first()
        
        if not otp:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        
        # Mark OTP as used
        otp.is_used = True
        user.is_verified = True
        db.session.commit()
        
        # Generate token
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
        print(f"Verify error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        otp = OTP(email=email, otp_code=otp_code, expires_at=expires_at)
        db.session.add(otp)
        db.session.commit()
        
        # Send email
        send_email(email, otp_code)
        
        return jsonify({
            'message': 'OTP resent successfully!',
            'otp_debug': otp_code
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Resend error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter(func.lower(User.email) == email).first()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_verified:
            return jsonify({'error': 'Email not verified'}), 403
        
        # Check account status
        if user.status != 'active':
            return jsonify({'error': f'Account is {user.status}'}), 403
        
        # Update login tracking
        user.last_login = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        db.session.commit()
        
        # Generate token
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
                'email': user.email,
                'is_admin': user.is_admin,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin
        }
    }), 200

# Admin routes
# ============================================
# DOCTOR ENDPOINTS
# ============================================

@app.route('/api/doctors', methods=['GET'])
@token_required
def get_doctors(current_user):
    """Get doctors with optional filters"""
    hospital_id = request.args.get('hospital_id')
    specialty = request.args.get('specialty')
    
    query = Doctor.query
    
    if hospital_id:
        query = query.filter_by(hospital_id=hospital_id)
    if specialty:
        query = query.filter(Doctor.specialty.ilike(f'%{specialty}%'))
    
    doctors = query.all()
    
    return jsonify({
        'doctors': [{
            'id': d.id,
            'name': d.name,
            'specialty': d.specialty,
            'qualifications': d.qualifications,
            'experience_years': d.experience_years,
            'consultation_fee': d.consultation_fee,
            'hospital_id': d.hospital_id,
            'hospital_name': d.hospital_name,
            'email': d.email,
            'phone': d.phone,
            'bio': d.bio,
            'rating': d.rating,
            'available_days': json.loads(d.available_days) if d.available_days else [],
            'available_hours': d.available_hours
        } for d in doctors]
    })

@app.route('/api/doctors/<int:doctor_id>', methods=['GET'])
@token_required
def get_doctor_details(current_user, doctor_id):
    """Get detailed information about a specific doctor"""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    return jsonify({
        'id': doctor.id,
        'name': doctor.name,
        'specialty': doctor.specialty,
        'qualifications': doctor.qualifications,
        'experience_years': doctor.experience_years,
        'consultation_fee': doctor.consultation_fee,
        'hospital_id': doctor.hospital_id,
        'hospital_name': doctor.hospital_name,
        'email': doctor.email,
        'phone': doctor.phone,
        'bio': doctor.bio,
        'rating': doctor.rating,
        'available_days': json.loads(doctor.available_days) if doctor.available_days else [],
        'available_hours': doctor.available_hours
    })

@app.route('/api/specialties', methods=['GET'])
@token_required
def get_specialties(current_user):
    """Get list of unique specialties"""
    specialties = db.session.query(Doctor.specialty).distinct().all()
    return jsonify({
        'specialties': [s[0] for s in specialties if s[0]]
    })

# ============================================
# APPOINTMENT ENDPOINTS
# ============================================

@app.route('/api/appointments', methods=['GET'])
@token_required
def get_appointments(current_user):
    """Get user's appointments"""
    status = request.args.get('status')
    
    query = Appointment.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    result = []
    for apt in appointments:
        doctor = Doctor.query.get(apt.doctor_id)
        result.append({
            'id': apt.id,
            'doctor_id': apt.doctor_id,
            'doctor_name': doctor.name if doctor else 'Unknown',
            'doctor_specialty': doctor.specialty if doctor else '',
            'hospital_id': apt.hospital_id,
            'hospital_name': apt.hospital_name,
            'appointment_date': apt.appointment_date.isoformat(),
            'appointment_time': apt.appointment_time,
            'status': apt.status,
            'symptoms': apt.symptoms,
            'notes': apt.notes,
            'created_at': apt.created_at.isoformat()
        })
    
    return jsonify({'appointments': result})

@app.route('/api/appointments', methods=['POST'])
@token_required
def book_appointment(current_user):
    """Book a new appointment"""
    data = request.json
    
    required_fields = ['doctor_id', 'appointment_date', 'appointment_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    # Get doctor details
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Parse date
    try:
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Check if slot is already booked
    existing = Appointment.query.filter_by(
        doctor_id=data['doctor_id'],
        appointment_date=appointment_date,
        appointment_time=data['appointment_time'],
        status='scheduled'
    ).first()
    
    if existing:
        return jsonify({'error': 'This time slot is already booked'}), 400
    
    # Create appointment
    appointment = Appointment(
        user_id=current_user.id,
        doctor_id=data['doctor_id'],
        hospital_id=doctor.hospital_id,
        hospital_name=doctor.hospital_name,
        appointment_date=appointment_date,
        appointment_time=data['appointment_time'],
        symptoms=data.get('symptoms', ''),
        notes=data.get('notes', '')
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    # Send confirmation email
    appointment_data = {
        'doctor_name': doctor.name,
        'hospital_name': doctor.hospital_name,
        'date': appointment_date.strftime('%B %d, %Y'),
        'time': data['appointment_time'],
        'specialty': doctor.specialty
    }
    # Send email in background thread to avoid blocking
    import threading
    threading.Thread(
        target=send_appointment_email,
        args=(current_user.email, appointment_data),
        daemon=True
    ).start()
    
    return jsonify({
        'message': 'Appointment booked successfully',
        'appointment_id': appointment.id,
        'appointment': {
            'id': appointment.id,
            'doctor_name': doctor.name,
            'hospital_name': doctor.hospital_name,
            'date': appointment_date.isoformat(),
            'time': appointment.appointment_time
        }
    }), 201

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
@token_required
def update_appointment(current_user, appointment_id):
    """Update appointment status (cancel/reschedule)"""
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    if appointment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    if 'status' in data:
        if data['status'] not in ['scheduled', 'cancelled', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
        appointment.status = data['status']
    
    if 'appointment_date' in data:
        try:
            appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    
    if 'appointment_time' in data:
        appointment.appointment_time = data['appointment_time']
    
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment updated successfully',
        'appointment': {
            'id': appointment.id,
            'status': appointment.status,
            'date': appointment.appointment_date.isoformat(),
            'time': appointment.appointment_time
        }
    })

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
@token_required
def delete_appointment(current_user, appointment_id):
    """Cancel an appointment"""
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    if appointment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointment.status = 'cancelled'
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Appointment cancelled successfully'})

@app.route('/api/doctors/<int:doctor_id>/available-slots', methods=['GET'])
@token_required
def get_available_slots(current_user, doctor_id):
    """Get available time slots for a doctor on a specific date"""
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'error': 'Date parameter required'}), 400
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Parse available hours (e.g., "09:00-17:00")
    if not doctor.available_hours:
        return jsonify({'slots': []})
    
    try:
        start_time, end_time = doctor.available_hours.split('-')
        start_hour = int(start_time.split(':')[0])
        end_hour = int(end_time.split(':')[0])
    except:
        return jsonify({'slots': []})
    
    # Generate hourly slots
    all_slots = []
    for hour in range(start_hour, end_hour):
        all_slots.append(f"{hour:02d}:00")
        all_slots.append(f"{hour:02d}:30")
    
    # Get booked slots
    booked_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        status='scheduled'
    ).all()
    
    booked_slots = [apt.appointment_time for apt in booked_appointments]
    
    # Return available slots
    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    
    return jsonify({
        'date': date_str,
        'doctor_id': doctor_id,
        'slots': available_slots,
        'booked_slots': booked_slots
    })

# ============================================
# USER PROFILE & MEDICAL RECORDS ENDPOINTS
# ============================================

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    """Get user's basic profile information"""
    app.logger.info(f'GET /api/user/profile called for user: {current_user.username} ({current_user.email})')
    response_data = {
        'user': {
            'name': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        }
    }
    app.logger.info(f'Returning user data: {response_data}')
    return jsonify(response_data)

@app.route('/api/user/profile', methods=['POST'])
@token_required
def update_user_profile(current_user):
    """Create or update user's medical profile"""
    data = request.json
    
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        # Create new profile
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
    
    # Update fields
    if 'blood_type' in data:
        profile.blood_type = data['blood_type']
    if 'allergies' in data:
        profile.allergies = data['allergies']
    if 'chronic_conditions' in data:
        profile.chronic_conditions = data['chronic_conditions']
    if 'emergency_contact' in data:
        profile.emergency_contact = data['emergency_contact']
    if 'emergency_phone' in data:
        profile.emergency_phone = data['emergency_phone']
    
    profile.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'profile': {
            'blood_type': profile.blood_type,
            'allergies': profile.allergies,
            'chronic_conditions': profile.chronic_conditions,
            'emergency_contact': profile.emergency_contact,
            'emergency_phone': profile.emergency_phone
        }
    })

@app.route('/api/user/medical-records', methods=['GET'])
@token_required
def get_medical_records(current_user):
    """Get all medical records for current user"""
    records = MedicalRecord.query.filter_by(user_id=current_user.id).order_by(MedicalRecord.date.desc()).all()
    
    return jsonify({
        'records': [{
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'date': r.date.isoformat(),
            'created_at': r.created_at.isoformat()
        } for r in records]
    })

@app.route('/api/user/medical-records', methods=['POST'])
@token_required
def add_medical_record(current_user):
    """Add a new medical record"""
    data = request.json
    
    if not data.get('title') or not data.get('description') or not data.get('date'):
        return jsonify({'error': 'Title, description, and date are required'}), 400
    
    try:
        record_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    record = MedicalRecord(
        user_id=current_user.id,
        title=data['title'],
        description=data['description'],
        date=record_date
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'message': 'Medical record added successfully',
        'record': {
            'id': record.id,
            'title': record.title,
            'description': record.description,
            'date': record.date.isoformat(),
            'created_at': record.created_at.isoformat()
        }
    }), 201

@app.route('/api/user/medical-records/<int:record_id>', methods=['DELETE'])
@token_required
def delete_medical_record(current_user, record_id):
    """Delete a medical record"""
    record = MedicalRecord.query.get(record_id)
    
    if not record:
        return jsonify({'error': 'Medical record not found'}), 404
    
    if record.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({'message': 'Medical record deleted successfully'})

# ============================================
# ACCOUNT MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/user/update-name', methods=['PUT'])
@token_required
def update_user_name(current_user):
    """Update user's display name"""
    data = request.json
    
    if not data.get('name') or not data['name'].strip():
        return jsonify({'error': 'Name is required'}), 400
    
    current_user.username = data['name'].strip()
    db.session.commit()
    
    return jsonify({
        'message': 'Name updated successfully',
        'name': current_user.username
    })

@app.route('/api/user/send-email-otp', methods=['POST'])
@token_required
def send_email_update_otp(current_user):
    """Send OTP to new email for verification"""
    data = request.json
    new_email = data.get('new_email', '').strip().lower()
    
    if not new_email:
        return jsonify({'error': 'New email is required'}), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        return jsonify({'error': 'Email already in use'}), 400
    
    # Generate OTP
    otp_code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Invalidate previous OTPs for this email
    OTP.query.filter_by(email=new_email).delete()
    
    # Create new OTP
    new_otp = OTP(
        email=new_email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.session.add(new_otp)
    db.session.commit()
    
    # Send email
    try:
        send_otp_email(new_email, otp_code, purpose='email_verification')
        return jsonify({'message': 'OTP sent to new email address'})
    except Exception as e:
        app.logger.error(f'Failed to send OTP email: {str(e)}')
        return jsonify({'error': 'Failed to send OTP. Please try again.'}), 500

@app.route('/api/user/verify-email-otp', methods=['POST'])
@token_required
def verify_email_update_otp(current_user):
    """Verify OTP and update email"""
    data = request.json
    new_email = data.get('new_email', '').strip().lower()
    otp_code = data.get('otp', '').strip()
    
    if not new_email or not otp_code:
        return jsonify({'error': 'Email and OTP are required'}), 400
    
    # Find valid OTP
    otp = OTP.query.filter_by(
        email=new_email,
        otp_code=otp_code,
        is_used=False
    ).first()
    
    if not otp:
        return jsonify({'error': 'Invalid OTP'}), 400
    
    if datetime.utcnow() > otp.expires_at:
        return jsonify({'error': 'OTP has expired'}), 400
    
    # Check if email is already taken
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        return jsonify({'error': 'Email already in use'}), 400
    
    # Update email and mark OTP as used
    current_user.email = new_email
    otp.is_used = True
    db.session.commit()
    
    return jsonify({
        'message': 'Email updated successfully',
        'email': current_user.email
    })

@app.route('/api/user/change-password', methods=['POST'])
@token_required
def change_user_password(current_user):
    """Change user password"""
    data = request.json
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new passwords are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    
    # Verify current password
    if not bcrypt.checkpw(current_password.encode('utf-8'), current_user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Hash and update new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    current_user.password_hash = hashed_password
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'})

@app.route('/api/user/delete-account', methods=['DELETE'])
@token_required
def delete_user_account(current_user):
    """Delete user account and all associated data"""
    try:
        # Delete all user-related data
        Favorite.query.filter_by(user_id=current_user.id).delete()
        SearchHistory.query.filter_by(user_id=current_user.id).delete()
        UserProfile.query.filter_by(user_id=current_user.id).delete()
        MedicalRecord.query.filter_by(user_id=current_user.id).delete()
        Appointment.query.filter_by(user_id=current_user.id).delete()
        Review.query.filter_by(user_id=current_user.id).delete()
        
        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        return jsonify({'message': 'Account deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting account: {str(e)}')
        return jsonify({'error': 'Failed to delete account'}), 500

# ============================================
# HEALTH CHECK ENDPOINTS
# ============================================

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connectivity
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        app.logger.error(f'Database health check failed: {str(e)}')
        db_status = 'unhealthy'
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'checks': {
            'database': db_status,
            'ai_services': {
                'gemini': 'configured' if GEMINI_API_KEY else 'not_configured',
                'cohere': 'configured' if COHERE_API_KEY else 'not_configured'
            }
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code


# ===================================
# ADMIN ENDPOINTS
# ===================================

# Admin Dashboard - Overview Stats
@app.route('/api/admin/stats', methods=['GET'])
@admin_required()
def get_admin_stats(current_user):
    """Get overview statistics for admin dashboard"""
    try:
        # User stats
        total_users = User.query.count()
        active_users = User.query.filter_by(status='active').count()
        new_users_week = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        suspended_users = User.query.filter_by(status='suspended').count()
        
        # Appointment stats
        total_appointments = Appointment.query.filter(
            Appointment.deleted_at.is_(None)
        ).count()
        scheduled_appointments = Appointment.query.filter_by(status='scheduled').filter(
            Appointment.deleted_at.is_(None)
        ).count()
        cancelled_appointments = Appointment.query.filter_by(status='cancelled').count()
        deleted_appointments = Appointment.query.filter(
            Appointment.deleted_at.isnot(None)
        ).count()
        
        # Recent appointments (last 30 days)
        recent_appointments = Appointment.query.filter(
            Appointment.created_at >= datetime.utcnow() - timedelta(days=30),
            Appointment.deleted_at.is_(None)
        ).count()
        
        # Review stats
        total_reviews = Review.query.count()
        flagged_reviews = Review.query.filter_by(is_flagged=True).count()
        
        # Doctor stats
        total_doctors = Doctor.query.count()
        active_doctors = Doctor.query.filter(Doctor.rating >= 4.0).count()
        
        # Search history
        total_searches = SearchHistory.query.count()
        searches_this_week = SearchHistory.query.filter(
            SearchHistory.search_date >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        log_admin_action(current_user.id, 'view_dashboard_stats')
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'new_this_week': new_users_week,
                'suspended': suspended_users
            },
            'appointments': {
                'total': total_appointments,
                'scheduled': scheduled_appointments,
                'cancelled': cancelled_appointments,
                'deleted': deleted_appointments,
                'recent_30_days': recent_appointments
            },
            'reviews': {
                'total': total_reviews,
                'flagged': flagged_reviews
            },
            'doctors': {
                'total': total_doctors,
                'high_rated': active_doctors
            },
            'searches': {
                'total': total_searches,
                'this_week': searches_this_week
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Admin stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# User Management
@app.route('/api/admin/users', methods=['GET'])
@admin_required()
def get_all_users(current_user):
    """Get all users with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        role_filter = request.args.get('role', '')
        
        query = User.query
        
        # Apply filters
        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%'))
            )
        if status_filter:
            query = query.filter_by(status=status_filter)
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        # Paginate
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        log_admin_action(current_user.id, 'list_users', details={'page': page, 'search': search})
        
        return jsonify({
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role,
                'status': u.status,
                'is_verified': u.is_verified,
                'last_login': u.last_login.isoformat() if u.last_login else None,
                'login_count': u.login_count or 0,
                'created_at': u.created_at.isoformat()
            } for u in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['GET'], endpoint='get_user_details')
@admin_required()
def get_user_details(current_user, user_id):
    """Get detailed information about a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get user's appointments
        appointments = Appointment.query.filter_by(user_id=user_id).all()
        
        # Get user's reviews
        reviews = Review.query.filter_by(user_id=user_id).all()
        
        # Get user's search history
        searches = SearchHistory.query.filter_by(user_id=user_id).order_by(
            SearchHistory.search_date.desc()
        ).limit(10).all()
        
        log_admin_action(current_user.id, 'view_user_details', 'user', user_id)
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'is_verified': user.is_verified,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'login_count': user.login_count or 0,
                'created_at': user.created_at.isoformat()
            },
            'stats': {
                'total_appointments': len(appointments),
                'total_reviews': len(reviews),
                'total_searches': len(searches)
            },
            'recent_activity': {
                'appointments': [{
                    'id': a.id,
                    'doctor_id': a.doctor_id,
                    'hospital_name': a.hospital_name,
                    'date': a.appointment_date.isoformat(),
                    'time': a.appointment_time,
                    'status': a.status
                } for a in appointments[:5]],
                'recent_searches': [{
                    'location': s.location,
                    'date': s.search_date.isoformat()
                } for s in searches]
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get user details error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
@admin_required()
def update_user_role(current_user, user_id):
    """Update user role (admin or super admin)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        new_role = data.get('role')
        
        if new_role not in ['user', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Don't allow changing own role
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot change your own role'}), 403
        
        old_role = user.role
        user.role = new_role
        user.is_admin = (new_role == 'admin')
        db.session.commit()
        
        log_admin_action(
            current_user.id, 
            'update_user_role', 
            'user', 
            user_id,
            {'old_role': old_role, 'new_role': new_role}
        )
        
        return jsonify({
            'message': f'User role updated to {new_role}',
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Update role error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
@admin_required()
def update_user_status(current_user, user_id):
    """Suspend, activate, or ban a user"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        new_status = data.get('status')
        reason = data.get('reason', '')
        
        if new_status not in ['active', 'suspended', 'banned']:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Don't allow changing own status
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot change your own status'}), 403
        
        old_status = user.status
        user.status = new_status
        db.session.commit()
        
        log_admin_action(
            current_user.id,
            'update_user_status',
            'user',
            user_id,
            {'old_status': old_status, 'new_status': new_status, 'reason': reason}
        )
        
        return jsonify({
            'message': f'User status updated to {new_status}',
            'user': {
                'id': user.id,
                'email': user.email,
                'status': user.status
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Update status error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'], endpoint='delete_user')
@admin_required()
def delete_user(current_user, user_id):
    """Delete a user account (admin only)"""  
    try:
        user = User.query.get_or_404(user_id)
        
        # Don't allow deleting own account
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 403
        
        # Store user info before deletion
        user_email = user.email
        user_username = user.username
        
        # Delete related records
        Appointment.query.filter_by(user_id=user_id).delete()
        Review.query.filter_by(user_id=user_id).delete()
        Favorite.query.filter_by(user_id=user_id).delete()
        SearchHistory.query.filter_by(user_id=user_id).delete()
        OTP.query.filter_by(email=user_email).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        log_admin_action(
            current_user.id,
            'delete_user',
            'user',
            user_id,
            {'email': user_email, 'username': user_username}
        )
        
        return jsonify({
            'message': f'User {user_email} deleted successfully'
        }), 200
        
    except Exception as e:
        app.logger.error(f"Delete user error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Appointment Management
@app.route('/api/admin/appointments', methods=['GET'])
@admin_required()
def get_all_appointments(current_user):
    """Get all appointments with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', '')
        include_deleted = request.args.get('include_deleted', 'false') == 'true'
        
        query = Appointment.query
        
        if not include_deleted:
            query = query.filter(Appointment.deleted_at.is_(None))
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        appointments = query.order_by(Appointment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        log_admin_action(current_user.id, 'list_appointments', details={'page': page})
        
        return jsonify({
            'appointments': [{
                'id': a.id,
                'user_id': a.user_id,
                'doctor_id': a.doctor_id,
                'hospital_name': a.hospital_name,
                'appointment_date': a.appointment_date.isoformat(),
                'appointment_time': a.appointment_time,
                'status': a.status,
                'deleted_at': a.deleted_at.isoformat() if a.deleted_at else None,
                'deletion_reason': a.deletion_reason,
                'created_at': a.created_at.isoformat()
            } for a in appointments.items],
            'total': appointments.total,
            'pages': appointments.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get appointments error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/appointments/<int:appointment_id>', methods=['DELETE'])
@admin_required()
def admin_delete_appointment(current_user, appointment_id):
    """Delete an appointment with reason tracking (Admin)"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.json
        reason = data.get('reason', 'Deleted by admin')
        
        # Soft delete
        appointment.deleted_by = current_user.id
        appointment.deleted_at = datetime.utcnow()
        appointment.deletion_reason = reason
        appointment.status = 'cancelled'
        db.session.commit()
        
        log_admin_action(
            current_user.id,
            'delete_appointment',
            'appointment',
            appointment_id,
            {'reason': reason, 'user_id': appointment.user_id}
        )
        
        return jsonify({
            'message': 'Appointment deleted successfully',
            'appointment_id': appointment_id
        }), 200
        
    except Exception as e:
        app.logger.error(f"Delete appointment error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Review Moderation
@app.route('/api/admin/reviews', methods=['GET'])
@admin_required()
def get_all_reviews(current_user):
    """Get all reviews with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        flagged_only = request.args.get('flagged', 'false') == 'true'
        
        query = Review.query
        
        if flagged_only:
            query = query.filter_by(is_flagged=True)
        
        reviews = query.order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        log_admin_action(current_user.id, 'list_reviews', details={'flagged_only': flagged_only})
        
        return jsonify({
            'reviews': [{
                'id': r.id,
                'hospital_name': r.hospital_name,
                'user_id': r.user_id,
                'rating': r.rating,
                'comment': r.comment,
                'is_flagged': r.is_flagged,
                'flag_reason': r.flag_reason,
                'created_at': r.created_at.isoformat()
            } for r in reviews.items],
            'total': reviews.total,
            'pages': reviews.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get reviews error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/reviews/<int:review_id>/flag', methods=['PUT'])
@admin_required()
def admin_flag_review(current_user, review_id):
    """Flag or unflag a review (Admin)"""
    try:
        review = Review.query.get_or_404(review_id)
        data = request.json
        is_flagged = data.get('is_flagged', True)
        reason = data.get('reason', '')
        
        review.is_flagged = is_flagged
        review.flag_reason = reason if is_flagged else None
        review.moderated_by = current_user.id
        review.moderated_at = datetime.utcnow()
        db.session.commit()
        
        log_admin_action(
            current_user.id,
            'flag_review' if is_flagged else 'unflag_review',
            'review',
            review_id,
            {'reason': reason}
        )
        
        return jsonify({
            'message': 'Review updated successfully',
            'review': {
                'id': review.id,
                'is_flagged': review.is_flagged
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Flag review error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/reviews/<int:review_id>', methods=['DELETE'])
@admin_required()
def admin_delete_review(current_user, review_id):
    """Delete a review permanently (Admin)"""
    try:
        review = Review.query.get_or_404(review_id)
        data = request.json
        reason = data.get('reason', 'Violated community guidelines')
        
        log_admin_action(
            current_user.id,
            'delete_review',
            'review',
            review_id,
            {'reason': reason, 'user_id': review.user_id, 'hospital': review.hospital_name}
        )
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review deleted successfully',
            'review_id': review_id
        }), 200
        
    except Exception as e:
        app.logger.error(f"Delete review error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Admin Activity Logs
@app.route('/api/admin/logs', methods=['GET'])
@admin_required()
def get_admin_logs(current_user):
    """Get admin activity logs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_filter = request.args.get('action', '')
        admin_id = request.args.get('admin_id', type=int)
        
        query = AdminLog.query
        
        if action_filter:
            query = query.filter(AdminLog.action.ilike(f'%{action_filter}%'))
        if admin_id:
            query = query.filter_by(admin_id=admin_id)
        
        logs = query.order_by(AdminLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get admin usernames for all logs
        result_logs = []
        for l in logs.items:
            admin_user = User.query.get(l.admin_id)
            admin_username = admin_user.username if admin_user else f'User #{l.admin_id}'
            
            result_logs.append({
                'id': l.id,
                'admin_id': l.admin_id,
                'admin_username': admin_username,
                'action': l.action,
                'target_type': l.target_type,
                'target_id': l.target_id,
                'details': l.details if l.details else '',
                'ip_address': l.ip_address,
                'timestamp': l.created_at.isoformat()
            })
        
        return jsonify({
            'logs': result_logs,
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get logs error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# System Logs
@app.route('/api/admin/system/logs', methods=['GET'])
@admin_required()
def get_system_logs(current_user):
    """Get application logs from file"""
    try:
        lines = request.args.get('lines', 100, type=int)
        level = request.args.get('level', '').upper()  # ERROR, WARNING, INFO
        
        log_file = app.config['LOG_FILE']
        
        if not os.path.exists(log_file):
            return jsonify({'error': 'Log file not found'}), 404
        
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
        
        # Filter by level if specified
        if level:
            filtered_lines = [line for line in all_lines if level in line]
        else:
            filtered_lines = all_lines
        
        # Get last N lines
        recent_logs = filtered_lines[-lines:]
        
        log_admin_action(current_user.id, 'view_system_logs', details={'lines': lines, 'level': level})
        
        return jsonify({
            'logs': recent_logs,
            'total_lines': len(all_lines),
            'filtered_lines': len(filtered_lines)
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get system logs error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Email Announcements
@app.route('/api/admin/announcements', methods=['POST'])
@admin_required()
def create_announcement(current_user):
    """Create and optionally send email announcement"""
    try:
        data = request.json
        subject = data.get('subject')
        message = data.get('message')
        recipient_type = data.get('recipient_type', 'all')  # 'all', 'active', 'new', 'specific'
        recipient_ids = data.get('recipient_ids', [])
        send_now = data.get('send_now', False)
        
        if not all([subject, message]):
            return jsonify({'error': 'Subject and message required'}), 400
        
        announcement = Announcement(
            admin_id=current_user.id,
            subject=subject,
            message=message,
            recipient_type=recipient_type,
            recipient_ids=json.dumps(recipient_ids) if recipient_ids else None,
            status='draft'
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        if send_now:
            # Get recipients based on type
            if recipient_type == 'all':
                recipients = User.query.filter_by(is_verified=True, status='active').all()
            elif recipient_type == 'active':
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                recipients = User.query.filter(
                    User.is_verified == True,
                    User.status == 'active',
                    User.last_login >= cutoff_date
                ).all()
            elif recipient_type == 'new':
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                recipients = User.query.filter(
                    User.is_verified == True,
                    User.status == 'active',
                    User.created_at >= cutoff_date
                ).all()
            elif recipient_type == 'specific' and recipient_ids:
                recipients = User.query.filter(
                    User.id.in_(recipient_ids),
                    User.is_verified == True
                ).all()
            else:
                recipients = []
            
            # Send emails (in production, use Celery for async)
            sent_count = 0
            for user in recipients:
                try:
                    # Simple email sending (you can enhance this)
                    send_email(user.email, f"{subject}\n\n{message}")
                    sent_count += 1
                except:
                    pass
            
            announcement.status = 'sent'
            announcement.sent_at = datetime.utcnow()
            announcement.recipients_count = len(recipients)
            announcement.delivery_count = sent_count
            db.session.commit()
            
            log_admin_action(
                current_user.id,
                'send_announcement',
                'announcement',
                announcement.id,
                {'recipient_type': recipient_type, 'sent_count': sent_count}
            )
            
            return jsonify({
                'message': 'Announcement sent successfully',
                'announcement_id': announcement.id,
                'sent_count': sent_count,
                'total_recipients': len(recipients)
            }), 200
        else:
            log_admin_action(
                current_user.id,
                'create_announcement',
                'announcement',
                announcement.id
            )
            
            return jsonify({
                'message': 'Announcement saved as draft',
                'announcement_id': announcement.id
            }), 201
        
    except Exception as e:
        app.logger.error(f"Create announcement error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/announcements', methods=['GET'])
@admin_required()
def get_announcements(current_user):
    """Get all announcements"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        announcements = Announcement.query.order_by(
            Announcement.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'announcements': [{
                'id': a.id,
                'subject': a.subject,
                'message': a.message,
                'recipient_type': a.recipient_type,
                'status': a.status,
                'recipients_count': a.recipients_count or 0,
                'delivery_count': a.delivery_count or 0,
                'created_at': a.created_at.isoformat(),
                'sent_at': a.sent_at.isoformat() if a.sent_at else None
            } for a in announcements.items],
            'total': announcements.total,
            'pages': announcements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get announcements error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/symptom-chat', methods=['POST'])
@token_required
def symptom_chat(current_user_id):
    """
    AI-powered symptom chat endpoint
    Uses Cohere AI for intelligent conversation
    Can suggest nearby hospitals if symptoms are severe
    """
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        user_location = data.get('location')  # {latitude, longitude} or {lat, lng}
        chat_history = data.get('chat_history', [])
        
        # Debug logging
        app.logger.info(f"Symptom chat - Message: {user_message[:50]}...")
        app.logger.info(f"Symptom chat - Location received: {user_location}")
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Call Google Gemini AI (Cohere models were all deprecated)
        try:
            # Build conversation history for Gemini
            conversation_text = ""
            for msg in chat_history[-6:]:  # Last 6 messages for context
                if msg.get('role') == 'user':
                    conversation_text += f"User: {msg.get('content')}\n"
                elif msg.get('role') == 'assistant':
                    conversation_text += f"Assistant: {msg.get('content')}\n"
            
            # System instruction + conversation context
            full_prompt = """You are an AI Health Assistant. Your role is to:
1. Listen to the user's symptoms carefully
2. Ask clarifying questions if needed
3. Provide general health advice (NOT a diagnosis)
4. If symptoms are severe/emergency, recommend seeking immediate medical attention
5. Be empathetic and supportive
6. Always remind users this is not a substitute for professional medical advice

Important: Only mention emergency services or hospitals if the symptoms described are genuinely severe or life-threatening.

IMPORTANT: Use plain text only. Do NOT use markdown formatting, asterisks, or special characters for emphasis. Write in simple, clear sentences.

"""
            if conversation_text:
                full_prompt += f"Previous conversation:\n{conversation_text}\n"
            
            full_prompt += f"User: {user_message}\nAssistant:"
            
            # Use Gemini AI (using latest flash model)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(full_prompt)
            ai_response = response.text.strip()
            
            # Remove markdown asterisks for better readability
            ai_response = ai_response.replace('**', '').replace('*', '')
            
        except Exception as e:
            app.logger.error(f"Gemini API error: {str(e)}")
            # Fallback response
            ai_response = "I'm having trouble connecting to my AI service right now. However, if you're experiencing severe symptoms like chest pain, difficulty breathing, severe bleeding, or loss of consciousness, please call emergency services (108 in India, 911 in US) immediately or visit the nearest emergency room."
        
        # Analyze if symptoms are severe and user has location
        # Only check user's message for severity, not AI response
        suggest_hospitals = False
        severity_keywords = [
            'chest pain', 'heart pain', 'heart attack', 'cardiac arrest', 'stroke', 
            'can\'t breathe', 'difficulty breathing', 'shortness of breath',
            'severe pain', 'bleeding heavily', 'unconscious', 'seizure', 'severe headache',
            'high fever', 'vomiting blood', 'severe injury', 'broken bone', 'emergency',
            'can\'t move', 'paralyzed', 'intense pain', 'collapsed', 'very weak',
            'sharp pain', 'crushing pain', 'tight chest', 'pressure in chest'
        ]
        
        user_message_lower = user_message.lower()
        for keyword in severity_keywords:
            if keyword in user_message_lower:
                suggest_hospitals = True
                app.logger.info(f"Severe symptom detected: '{keyword}' in message")
                break
        
        result = {'response': ai_response}
        
        # If severe symptoms detected but NO location, prompt user to share location
        if suggest_hospitals and not user_location:
            app.logger.warning("Severe symptom but NO location provided")
            ai_response += "\n\n🏥 To find nearby hospitals for you, please click the 'Share Location' button at the top of the chat."
            result['response'] = ai_response
        
        # If severe and location available, find nearby hospitals
        if suggest_hospitals and user_location:
            app.logger.info(f"Searching hospitals for location: {user_location}")
            try:
                # Handle both latitude/longitude and lat/lng formats
                lat = user_location.get('latitude') or user_location.get('lat')
                lon = user_location.get('longitude') or user_location.get('lng')
                
                if lat and lon:
                    # Search for nearby hospitals using Overpass API
                    overpass_url = "https://overpass-api.de/api/interpreter"
                    query = f"""
                    [out:json][timeout:25];
                    (
                      node["amenity"="hospital"](around:10000,{lat},{lon});
                      way["amenity"="hospital"](around:10000,{lat},{lon});
                      relation["amenity"="hospital"](around:10000,{lat},{lon});
                    );
                    out center;
                    """
                    
                    hospitals_response = requests.post(overpass_url, data={'data': query}, timeout=10)
                    
                    if hospitals_response.status_code == 200:
                        hospitals_data = hospitals_response.json()
                        hospitals = []
                        
                        for element in hospitals_data.get('elements', [])[:5]:  # Top 5
                            if element.get('tags'):
                                tags = element['tags']
                                h_lat = element.get('lat') or element.get('center', {}).get('lat')
                                h_lon = element.get('lon') or element.get('center', {}).get('lon')
                                
                                if h_lat and h_lon:
                                    # Calculate distance
                                    import math
                                    R = 6371  # Earth radius in km
                                    dlat = math.radians(h_lat - lat)
                                    dlon = math.radians(h_lon - lon)
                                    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(h_lat)) * math.sin(dlon/2)**2
                                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                                    distance = R * c
                                    
                                    hospitals.append({
                                        'name': tags.get('name', 'Hospital'),
                                        'address': tags.get('addr:full') or tags.get('addr:street', 'Address not available'),
                                        'latitude': h_lat,
                                        'longitude': h_lon,
                                        'distance': f"{distance:.2f} km"
                                    })
                        
                        if hospitals:
                            result['suggested_hospitals'] = hospitals
                            ai_response += "\n\n⚠️ Based on your symptoms, I've found some nearby hospitals. Please consider seeking immediate medical attention."
                            result['response'] = ai_response
                            
            except Exception as e:
                app.logger.error(f"Error fetching nearby hospitals: {str(e)}")
        
        # Log the interaction
        try:
            search = SearchHistory(
                user_id=current_user_id,
                query=user_message[:200],
                location='AI Chat Session',
                timestamp=datetime.utcnow()
            )
            db.session.add(search)
            db.session.commit()
        except:
            pass  # Don't fail if logging fails
        
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"Error in symptom chat: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500


if __name__ == '__main__':
    print("Starting Flask server...")
    print("Routes registered:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    # Ensure tables exist
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        admin = User.query.filter_by(email='admin@nearbycare.com').first()
        if not admin:
            print("\n🔑 Creating default admin account...")
            admin_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                username='admin',
                email='admin@nearbycare.com',
                password_hash=admin_hash,
                is_verified=True,
                is_admin=True,
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin account created!")
            print("   Email: admin@nearbycare.com")
            print("   Password: admin123")
            print("   ⚠️  Change this password immediately!\n")
        
        # Seed sample doctors if table is empty
        if Doctor.query.count() == 0:
            print("\n👨‍⚕️ Seeding sample doctors...")
            sample_doctors = [
                # Cardiology
                Doctor(name="Dr. Lakshmi Prasanna", specialty="Cardiology", qualifications="MD, FACC", 
                       experience_years=15, consultation_fee=1200.0, 
                       hospital_id="sample_hospital_1", hospital_name="Sample General Hospital",
                       email="lakshmi.p@hospital.com", phone="+91-9876543210",
                       bio="Experienced cardiologist specializing in preventive cardiology and heart disease.",
                       rating=4.8, available_days=json.dumps(["Mon", "Wed", "Fri"]), available_hours="09:00-17:00"),
                
                Doctor(name="Dr. Venkata Ramana", specialty="Cardiology", qualifications="MD, FACC, FSCAI", 
                       experience_years=20, consultation_fee=1600.0,
                       hospital_id="sample_hospital_2", hospital_name="City Cardiac Center",
                       email="v.ramana@cardiac.com", phone="+91-9876543211",
                       bio="Interventional cardiologist with expertise in complex cardiac procedures.",
                       rating=4.9, available_days=json.dumps(["Tue", "Thu", "Sat"]), available_hours="10:00-18:00"),
                
                # Orthopedics
                Doctor(name="Dr. Sravani Reddy", specialty="Orthopedics", qualifications="MD, FAAOS", 
                       experience_years=12, consultation_fee=1000.0,
                       hospital_id="sample_hospital_1", hospital_name="Sample General Hospital",
                       email="sravani.r@hospital.com", phone="+91-9876543212",
                       bio="Orthopedic surgeon specializing in sports medicine and joint replacement.",
                       rating=4.7, available_days=json.dumps(["Mon", "Tue", "Thu"]), available_hours="08:00-16:00"),
                
                # Pediatrics
                Doctor(name="Dr. Krishna Murthy", specialty="Pediatrics", qualifications="MD, FAAP", 
                       experience_years=18, consultation_fee=800.0,
                       hospital_id="sample_hospital_3", hospital_name="Children's Medical Center",
                       email="krishna.m@childmed.com", phone="+91-9876543213",
                       bio="Dedicated pediatrician with experience in newborn care and childhood diseases.",
                       rating=4.9, available_days=json.dumps(["Mon", "Wed", "Fri"]), available_hours="09:00-17:00"),
                
                # Dentistry
                Doctor(name="Dr. Anjali Devi", specialty="Dentistry", qualifications="DDS", 
                       experience_years=10, consultation_fee=700.0,
                       hospital_id="sample_hospital_4", hospital_name="Smile Dental Clinic",
                       email="anjali.d@smile.com", phone="+91-9876543214",
                       bio="General dentist offering comprehensive dental care and cosmetic dentistry.",
                       rating=4.8, available_days=json.dumps(["Mon", "Tue", "Wed", "Thu", "Fri"]), available_hours="08:00-18:00"),
                
                # Dermatology
                Doctor(name="Dr. Priyanka Rao", specialty="Dermatology", qualifications="MD, FAAD", 
                       experience_years=14, consultation_fee=1100.0,
                       hospital_id="sample_hospital_1", hospital_name="Sample General Hospital",
                       email="priyanka.r@hospital.com", phone="+91-9876543215",
                       bio="Dermatologist specializing in medical and cosmetic dermatology.",
                       rating=4.6, available_days=json.dumps(["Tue", "Wed", "Thu"]), available_hours="10:00-18:00"),
                
                # Neurology
                Doctor(name="Dr. Srinivas Goud", specialty="Neurology", qualifications="MD, FAAN", 
                       experience_years=22, consultation_fee=1500.0,
                       hospital_id="sample_hospital_2", hospital_name="City Cardiac Center",
                       email="srinivas.g@neuro.com", phone="+91-9876543216",
                       bio="Neurologist with expertise in stroke, epilepsy, and movement disorders.",
                       rating=4.9, available_days=json.dumps(["Mon", "Wed", "Fri"]), available_hours="09:00-17:00"),
                
                # General Medicine
                Doctor(name="Dr. Madhavi Nair", specialty="General Medicine", qualifications="MD", 
                       experience_years=8, consultation_fee=600.0,
                       hospital_id="sample_hospital_1", hospital_name="Sample General Hospital",
                       email="madhavi.n@hospital.com", phone="+91-9876543217",
                       bio="Family physician providing comprehensive primary care for all ages.",
                       rating=4.7, available_days=json.dumps(["Mon", "Tue", "Wed", "Thu", "Fri"]), available_hours="08:00-20:00"),
                
                # Ophthalmology
                Doctor(name="Dr. Ravi Shankar", specialty="Ophthalmology", qualifications="MD, FACS", 
                       experience_years=16, consultation_fee=1200.0,
                       hospital_id="sample_hospital_5", hospital_name="Vision Eye Center",
                       email="ravi.s@vision.com", phone="+91-9876543218",
                       bio="Eye surgeon specializing in cataract and LASIK surgery.",
                       rating=4.8, available_days=json.dumps(["Mon", "Thu", "Fri"]), available_hours="09:00-16:00"),
                
                # Psychiatry
                Doctor(name="Dr. Keerthi Chowdary", specialty="Psychiatry", qualifications="MD, Board Certified", 
                       experience_years=13, consultation_fee=1300.0,
                       hospital_id="sample_hospital_2", hospital_name="City Cardiac Center",
                       email="keerthi.c@mental.com", phone="+91-9876543219",
                       bio="Psychiatrist specializing in anxiety, depression, and mood disorders.",
                       rating=4.7, available_days=json.dumps(["Tue", "Wed", "Thu", "Fri"]), available_hours="10:00-18:00"),
            ]
            
            db.session.add_all(sample_doctors)
            db.session.commit()
            print(f"✅ Added {len(sample_doctors)} sample doctors!\n")
        
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False, threaded=True)
