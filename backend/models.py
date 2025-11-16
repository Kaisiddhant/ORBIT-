from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    salary = db.Column(db.Float)
    google_id = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policies = db.relationship('Policy', backref='user', lazy=True, cascade='all, delete-orphan')
    quotes = db.relationship('Quote', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'age': self.age,
            'salary': self.salary
        }

class InsurancePlan(db.Model):
    __tablename__ = 'insurance_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Health, Life, Vehicle, etc.
    coverage_amount = db.Column(db.Float, nullable=False)
    base_premium = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.JSON)  # JSON array of features
    age_min = db.Column(db.Integer, default=18)
    age_max = db.Column(db.Integer, default=100)
    salary_min = db.Column(db.Float, default=0)
    popularity_score = db.Column(db.Float, default=0)
    rating = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'type': self.type,
            'coverage_amount': self.coverage_amount,
            'base_premium': self.base_premium,
            'description': self.description,
            'features': self.features,
            'age_range': [self.age_min, self.age_max],
            'rating': self.rating
        }

class Policy(db.Model):
    __tablename__ = 'policies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('insurance_plans.id'), nullable=False)
    policy_number = db.Column(db.String(50), unique=True, nullable=False)
    premium = db.Column(db.Float, nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    pdf_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    plan = db.relationship('InsurancePlan', backref='policies')
    
    def to_dict(self):
        return {
            'id': self.id,
            'policy_number': self.policy_number,
            'plan': self.plan.to_dict(),
            'premium': self.premium,
            'coverage_amount': self.coverage_amount,
            'start_date': self.start_date.isoformat(),
            'status': self.status
        }

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('insurance_plans.id'), nullable=False)
    estimated_premium = db.Column(db.Float, nullable=False)
    user_age = db.Column(db.Integer)
    user_salary = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    plan = db.relationship('InsurancePlan', backref='quotes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan': self.plan.to_dict(),
            'estimated_premium': self.estimated_premium,
            'created_at': self.created_at.isoformat()
        }