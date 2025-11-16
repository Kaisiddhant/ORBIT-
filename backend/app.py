from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db, User, InsurancePlan, Policy, Quote
from recommendation_engine import InsuranceRecommendationEngine
from utils.pdf_generator import PolicyPDFGenerator
from utils.security import validate_email, validate_password, generate_policy_number
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Initialize engines
recommendation_engine = InsuranceRecommendationEngine()
pdf_generator = PolicyPDFGenerator()

# ============== SEED DATA FUNCTION (DEFINE FIRST) ==============
def seed_insurance_plans():
    """Seed database with sample insurance plans"""
    plans = [
        # Health Insurance
        InsurancePlan(
            name="Basic Health Shield",
            provider="HealthFirst Insurance",
            type="Health",
            coverage_amount=100000,
            base_premium=5000,
            description="Comprehensive health coverage for individuals and families",
            features=["Hospitalization", "Doctor Visits", "Prescription Drugs", "Preventive Care", "Emergency Services"],
            age_min=18, age_max=65, salary_min=20000,
            popularity_score=85, rating=4.2
        ),
        InsurancePlan(
            name="Premium Health Plus",
            provider="HealthFirst Insurance",
            type="Health",
            coverage_amount=500000,
            base_premium=12000,
            description="Premium health coverage with worldwide emergency assistance",
            features=["All Basic Features", "Dental & Vision", "Mental Health", "International Coverage", "No Waiting Period"],
            age_min=18, age_max=70, salary_min=50000,
            popularity_score=92, rating=4.7
        ),
        
        # Life Insurance
        InsurancePlan(
            name="Term Life 20",
            provider="LifeSecure Corp",
            type="Life",
            coverage_amount=1000000,
            base_premium=8000,
            description="20-year term life insurance for financial security",
            features=["Death Benefit", "Terminal Illness Rider", "Accidental Death Benefit", "Convertible to Whole Life"],
            age_min=18, age_max=60, salary_min=30000,
            popularity_score=88, rating=4.5
        ),
        InsurancePlan(
            name="Whole Life Guardian",
            provider="LifeSecure Corp",
            type="Life",
            coverage_amount=2000000,
            base_premium=18000,
            description="Permanent life insurance with cash value accumulation",
            features=["Lifetime Coverage", "Cash Value Growth", "Loan Options", "Dividend Payments", "Estate Planning"],
            age_min=18, age_max=75, salary_min=75000,
            popularity_score=78, rating=4.3
        ),
        
        # Vehicle Insurance
        InsurancePlan(
            name="Auto Essential",
            provider="DriveGuard Insurance",
            type="Vehicle",
            coverage_amount=50000,
            base_premium=3000,
            description="Essential auto insurance coverage",
            features=["Liability Coverage", "Collision", "Comprehensive", "Roadside Assistance", "Rental Reimbursement"],
            age_min=21, age_max=80, salary_min=15000,
            popularity_score=90, rating=4.4
        ),
        InsurancePlan(
            name="Auto Premium Elite",
            provider="DriveGuard Insurance",
            type="Vehicle",
            coverage_amount=150000,
            base_premium=6000,
            description="Premium auto coverage with full protection",
            features=["All Essential Features", "Gap Coverage", "Custom Parts", "Accident Forgiveness", "New Car Replacement"],
            age_min=25, age_max=75, salary_min=40000,
            popularity_score=82, rating=4.6
        ),
        
        # Home Insurance
        InsurancePlan(
            name="Home Protection Basic",
            provider="HomeShield Inc",
            type="Home",
            coverage_amount=300000,
            base_premium=4500,
            description="Basic home insurance for property protection",
            features=["Dwelling Coverage", "Personal Property", "Liability Protection", "Medical Payments", "Loss of Use"],
            age_min=21, age_max=100, salary_min=25000,
            popularity_score=86, rating=4.3
        ),
        InsurancePlan(
            name="Home Premium Fortress",
            provider="HomeShield Inc",
            type="Home",
            coverage_amount=750000,
            base_premium=9000,
            description="Comprehensive home protection with enhanced coverage",
            features=["All Basic Features", "Flood Coverage", "Earthquake Coverage", "Valuable Items", "Identity Theft Protection"],
            age_min=25, age_max=100, salary_min=60000,
            popularity_score=79, rating=4.5
        ),
        
        # Travel Insurance
        InsurancePlan(
            name="Travel Safe",
            provider="GlobalTravel Insurance",
            type="Travel",
            coverage_amount=50000,
            base_premium=500,
            description="Essential travel insurance for domestic and international trips",
            features=["Trip Cancellation", "Medical Emergency", "Baggage Loss", "Flight Delay", "24/7 Assistance"],
            age_min=1, age_max=85, salary_min=10000,
            popularity_score=91, rating=4.6
        ),
        InsurancePlan(
            name="Travel Elite Worldwide",
            provider="GlobalTravel Insurance",
            type="Travel",
            coverage_amount=200000,
            base_premium=1200,
            description="Premium travel insurance with comprehensive worldwide coverage",
            features=["All Basic Features", "Adventure Sports", "Cruise Coverage", "Rental Car", "Pre-existing Conditions"],
            age_min=1, age_max=80, salary_min=30000,
            popularity_score=84, rating=4.8
        ),
    ]
    
    for plan in plans:
        db.session.add(plan)
    
    db.session.commit()
    print("✅ Insurance plans seeded successfully!")

# ============== CREATE TABLES & SEED DATA ==============
with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if plans already exist
        if InsurancePlan.query.count() == 0:
            print("📊 Seeding initial data...")
            seed_insurance_plans()
        else:
            print("✅ Database already contains data. Skipping seed.")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

# ============== Authentication Routes ==============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            full_name=data.get('full_name', ''),
            phone=data.get('phone', ''),
            age=data.get('age'),
            salary=data.get('salary')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Google OAuth authentication"""
    try:
        data = request.get_json()
        google_id = data.get('google_id')
        email = data.get('email')
        full_name = data.get('full_name')
        
        if not google_id or not email:
            return jsonify({'error': 'Invalid Google authentication data'}), 400
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check by email
            user = User.query.filter_by(email=email).first()
            if user:
                user.google_id = google_id
            else:
                # Create new user
                user = User(
                    email=email,
                    full_name=full_name,
                    google_id=google_id
                )
                db.session.add(user)
        
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Google authentication successful',
            'token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== User Profile Routes ==============

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        user.full_name = data.get('full_name', user.full_name)
        user.phone = data.get('phone', user.phone)
        user.age = data.get('age', user.age)
        user.salary = data.get('salary', user.salary)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== Insurance Plan Routes ==============

@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Get all insurance plans"""
    try:
        plan_type = request.args.get('type')
        
        query = InsurancePlan.query
        if plan_type:
            query = query.filter_by(type=plan_type)
        
        plans = query.all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Get specific insurance plan"""
    try:
        plan = InsurancePlan.query.get(plan_id)
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        return jsonify({'plan': plan.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Recommendation Routes ==============

@app.route('/api/recommendations', methods=['POST'])
@jwt_required()
def get_recommendations():
    """Get personalized insurance recommendations"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        user_data = {
            'age': data.get('age', user.age or 30),
            'salary': data.get('salary', user.salary or 50000),
            'budget': data.get('budget'),
            'insurance_type': data.get('insurance_type')
        }
        
        # Get all available plans
        plans = InsurancePlan.query.all()
        plans_data = [plan.to_dict() for plan in plans]
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            user_data, 
            plans_data, 
            top_n=data.get('top_n', 5)
        )
        
        return jsonify({
            'recommendations': recommendations,
            'user_profile': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/premium-estimate', methods=['POST'])
def estimate_premium():
    """Estimate premium for a specific plan"""
    try:
        data = request.get_json()
        
        plan_id = data.get('plan_id')
        age = data.get('age')
        salary = data.get('salary')
        
        if not all([plan_id, age, salary]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        plan = InsurancePlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        premium = recommendation_engine.calculate_premium(
            plan.base_premium,
            age,
            salary,
            plan.coverage_amount,
            plan.type
        )
        
        return jsonify({
            'plan': plan.to_dict(),
            'estimated_premium': premium,
            'monthly_premium': round(premium / 12, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
@jwt_required()
def compare_plans():
    """Compare multiple insurance plans"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        data = request.get_json()
        plan_ids = data.get('plan_ids', [])
        
        if not plan_ids or len(plan_ids) < 2:
            return jsonify({'error': 'At least 2 plans required for comparison'}), 400
        
        plans = InsurancePlan.query.all()
        plans_data = [plan.to_dict() for plan in plans]
        
        user_data = {
            'age': user.age or 30,
            'salary': user.salary or 50000
        }
        
        comparison = recommendation_engine.compare_plans(plan_ids, plans_data, user_data)
        
        return jsonify({'comparison': comparison}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Policy Routes ==============

@app.route('/api/policies', methods=['GET'])
@jwt_required()
def get_user_policies():
    """Get all policies for logged-in user"""
    try:
        user_id = get_jwt_identity()
        policies = Policy.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'policies': [policy.to_dict() for policy in policies]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/policies', methods=['POST'])
@jwt_required()
def create_policy():
    """Create a new policy"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        plan = InsurancePlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        # Calculate premium
        premium = recommendation_engine.calculate_premium(
            plan.base_premium,
            user.age or 30,
            user.salary or 50000,
            plan.coverage_amount,
            plan.type
        )
        
        # Create policy
        policy = Policy(
            user_id=user_id,
            plan_id=plan_id,
            policy_number=generate_policy_number(),
            premium=premium,
            coverage_amount=plan.coverage_amount,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365),
            status='active'
        )
        
        db.session.add(policy)
        db.session.commit()
        
        # Generate PDF
        try:
            policy_data = policy.to_dict()
            user_data = user.to_dict()
            pdf_path = pdf_generator.generate_policy_document(policy_data, user_data)
            policy.pdf_path = pdf_path
            db.session.commit()
        except Exception as e:
            print(f"PDF generation error: {e}")
        
        return jsonify({
            'message': 'Policy created successfully',
            'policy': policy.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/policies/<int:policy_id>/download', methods=['GET'])
@jwt_required()
def download_policy(policy_id):
    """Download policy PDF"""
    try:
        user_id = get_jwt_identity()
        policy = Policy.query.filter_by(id=policy_id, user_id=user_id).first()
        
        if not policy:
            return jsonify({'error': 'Policy not found'}), 404
        
        if not policy.pdf_path or not os.path.exists(policy.pdf_path):
            return jsonify({'error': 'PDF not available'}), 404
        
        return send_file(policy.pdf_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Quote Routes ==============

@app.route('/api/quotes', methods=['POST'])
@jwt_required()
def save_quote():
    """Save a quote for later"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        plan = InsurancePlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        premium = recommendation_engine.calculate_premium(
            plan.base_premium,
            user.age or 30,
            user.salary or 50000,
            plan.coverage_amount,
            plan.type
        )
        
        quote = Quote(
            user_id=user_id,
            plan_id=plan_id,
            estimated_premium=premium,
            user_age=user.age,
            user_salary=user.salary
        )
        
        db.session.add(quote)
        db.session.commit()
        
        return jsonify({
            'message': 'Quote saved successfully',
            'quote': quote.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/quotes', methods=['GET'])
@jwt_required()
def get_quotes():
    """Get all saved quotes for user"""
    try:
        user_id = get_jwt_identity()
        quotes = Quote.query.filter_by(user_id=user_id).order_by(Quote.created_at.desc()).all()
        
        return jsonify({
            'quotes': [quote.to_dict() for quote in quotes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Analytics Routes ==============

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for user"""
    try:
        user_id = get_jwt_identity()
        
        active_policies = Policy.query.filter_by(user_id=user_id, status='active').count()
        total_coverage = db.session.query(db.func.sum(Policy.coverage_amount))\
            .filter_by(user_id=user_id, status='active').scalar() or 0
        total_premium = db.session.query(db.func.sum(Policy.premium))\
            .filter_by(user_id=user_id, status='active').scalar() or 0
        saved_quotes = Quote.query.filter_by(user_id=user_id).count()
        
        return jsonify({
            'active_policies': active_policies,
            'total_coverage': total_coverage,
            'total_annual_premium': total_premium,
            'saved_quotes': saved_quotes
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Health Check ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'ORBIT Insurance API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'plans': '/api/plans',
            'auth': '/api/auth/login'
        }
    }), 200

# ============== Run Application ==============

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 ORBIT Insurance Platform")
    print("="*50)
    print("📡 Server running on: http://localhost:5000")
    print("📊 API Documentation: http://localhost:5000/")
    print("🔧 Health Check: http://localhost:5000/api/health")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)