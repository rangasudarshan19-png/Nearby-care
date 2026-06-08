import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Always load backend/.env, even when app.py is imported from another working directory.
load_dotenv(os.path.join(basedir, '.env'))


def normalize_database_url(value):
    """Resolve relative SQLite paths to the backend folder instead of Flask's instance folder."""
    def sqlite_uri(path):
        return f'sqlite:///{os.path.abspath(path).replace(os.sep, "/")}'

    if not value:
        return sqlite_uri(os.path.join(basedir, "nearby_care.db"))

    prefix = 'sqlite:///'
    if value.startswith(prefix):
        db_path = value[len(prefix):]
        if db_path and not os.path.isabs(db_path):
            return sqlite_uri(os.path.join(basedir, db_path))

    return value

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    SMTP_SENDER = os.getenv('SMTP_SENDER', '')
    SMTP_APP_PASSWORD = os.getenv('SMTP_APP_PASSWORD', '')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    
    # AI Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY', '')
    NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '')
    NVIDIA_NIM_MODEL = os.getenv('NVIDIA_NIM_MODEL', 'mistralai/mixtral-8x7b-instruct-v0.1')
    NVIDIA_NIM_URL = os.getenv('NVIDIA_NIM_URL', 'https://integrate.api.nvidia.com/v1/chat/completions')
    NVIDIA_NIM_TIMEOUT_SECONDS = float(os.getenv('NVIDIA_NIM_TIMEOUT_SECONDS', 45))
    NVIDIA_NIM_MAX_TOKENS = int(os.getenv('NVIDIA_NIM_MAX_TOKENS', 320))
    NVIDIA_NIM_TARGET_CHARS = int(os.getenv('NVIDIA_NIM_TARGET_CHARS', 900))
    AI_USE_GEMINI_FALLBACK = os.getenv('AI_USE_GEMINI_FALLBACK', 'False').lower() == 'true'
    AI_LOCAL_FALLBACK_ENABLED = os.getenv('AI_LOCAL_FALLBACK_ENABLED', 'False').lower() == 'true'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # OpenStreetMap Configuration
    NOMINATIM_USER_AGENT = os.getenv('NOMINATIM_USER_AGENT', 'NearbyCareApp/1.0')
    OVERPASS_API_URL = os.getenv('OVERPASS_API_URL', 'https://overpass-api.de/api/interpreter')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002').split(',')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'False').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    # Use backend/nearby_care.db even if DATABASE_URL is a relative SQLite URL.
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.getenv('DATABASE_URL'))
    SQLALCHEMY_ECHO = False  # Set to True to log SQL queries

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    @classmethod
    def validate(cls):
        """Validate production configuration - called only when actually in production"""
        if not os.getenv('SECRET_KEY'):
            raise ValueError("SECRET_KEY must be set in production")
        if not os.getenv('JWT_SECRET_KEY'):
            raise ValueError("JWT_SECRET_KEY must be set in production")
        if not os.getenv('DATABASE_URL'):
            raise ValueError("DATABASE_URL must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

