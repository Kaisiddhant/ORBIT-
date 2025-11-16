import os
from datetime import timedelta

class Config:
    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'orbit-insurance-secret-key-2024'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///orbit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Insurance Plan Configuration
    INSURANCE_TYPES = ['Health', 'Life', 'Vehicle', 'Home', 'Travel']
    
    # ML Model Settings
    MODEL_PATH = 'models/recommendation_model.pkl'
    SCALER_PATH = 'models/scaler.pkl'