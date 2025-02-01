from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, Disease, Drug, HealthTip, PreventiveMeasure  # Import models from models.py
import json
import random
import traceback
import logging
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for missing environment variables
required_env_vars = ['DATABASE_URL', 'SECRET_KEY', 'JWT_SECRET_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"Environment variable {var} is missing.")
        exit(1)

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(
    app,
    resources={r"/api/*": {"origins": "https://iridescent-lolly-506319.netlify.app"}},  # Allow React frontend
    supports_credentials=True,  # Allow cookies
)

# Root endpoint
@app.route('/')
def index():
    return make_response('<h1>Welcome to the Health Awareness App!</h1>', 200)

# User Signup Route
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON or empty request"}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirmPassword = data.get('confirmPassword')

        if not all([username, email, password, confirmPassword]):
            return jsonify({"success": False, "message": "All fields are required"}), 400
        if password != confirmPassword:
            return jsonify({"success": False, "message": "Passwords do not match"}), 400

        # Check if user exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({"success": False, "message": "Username or email already exists"}), 409

        # Hash password and create user
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": True, "message": "Sign up successful"}), 201

    except Exception as e:
        logger.error(f"Error during signup: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": "An error occurred during signup"}), 500

# User Login Route
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
        if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity=str(user.email))  # Make sure identity is a string
            return jsonify({"success": True, "token": access_token}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401

    except Exception as e:
        logger.error(f"Error during login: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500



# Protected API Routes
@app.route('/api/diseases', methods=['GET'])
@jwt_required()
def get_diseases():
    try:
        diseases = Disease.query.all()
        if not diseases:
            return jsonify({'success': False, 'message': 'No diseases found.'}), 404

        disease_list = [{
            'id': disease.id,
            'name': disease.name,
            'category': disease.category,
            'causes': disease.causes,
            'symptoms': disease.symptoms,
            'prevention': disease.prevention,
            'treatment': disease.treatment,
            'pathogen': disease.pathogen,
            'mode_of_spread': disease.mode_of_spread,
            'incubation_period': disease.incubation_period
        } for disease in diseases]

        return jsonify({'success': True, 'data': disease_list}), 200

    except Exception as e:
        logger.error(f"Error fetching diseases: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/api/diseases', methods=['POST'])
@jwt_required()
def add_disease():
    try:
        data = request.get_json()
        new_disease = Disease(
            name=data['name'],
            category=data['category'],
            causes=json.dumps(data.get('causes', [])),
            symptoms=json.dumps(data.get('symptoms', [])),
            prevention=json.dumps(data.get('prevention', [])),
            treatment=json.dumps(data.get('treatment', [])),
            pathogen=data.get('pathogen'),
            mode_of_spread=data.get('mode_of_spread'),
            incubation_period=data.get('incubation_period')
        )
        db.session.add(new_disease)
        db.session.commit()
        return jsonify({"success": True, "message": "Disease added successfully!"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/drugs', methods=['GET'])
@jwt_required()
def get_drugs():
    try:
        drugs = Drug.query.all()
        drug_list = [{
            'id': drug.id,
            'name': drug.name,
            'category': drug.category,
            'usage': drug.usage,
            'dosage': drug.dosage,
            'side_effects': drug.side_effects,
            'precautions': drug.precautions
        } for drug in drugs]

        return jsonify({'success': True, 'data': drug_list}), 200
    except Exception as e:
        logger.error(f"Error fetching drugs: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/api/drugs', methods=['POST'])
@jwt_required()
def add_drug():
    try:
        data = request.get_json()

        # Ensure required fields are provided
        if not data or 'name' not in data or 'category' not in data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Create a new drug instance
        new_drug = Drug(
            name=data['name'],
            category=data.get('category', 'Unknown'),
            usage=data.get('usage', 'No usage description available'),
            dosage=data.get('dosage', 'No dosage information available'),
            side_effects=", ".join(data.get('side_effects', [])),
            precautions=", ".join(data.get('precautions', []))
        )

        # Add and commit the drug to the database
        db.session.add(new_drug)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Drug added successfully!', 'data': new_drug.id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    

@app.route('/api/health-tips/random', methods=['GET'])
def get_random_health_tip():
    try:
        health_tips = HealthTip.query.all()
        if not health_tips:
            return jsonify({'success': False, 'message': 'No health tips available.'}), 404

        random_tip = random.choice(health_tips)
        return jsonify({'success': True, 'data': {'id': random_tip.id, 'tip': random_tip.tip}}), 200

    except Exception as e:
        logger.error(f"Error fetching health tips: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching health tips.'}), 500
    
@app.route('/api/health-tips', methods=['POST'])
@jwt_required()
def add_health_tip():
    try:
        data = request.get_json()

        if not data or 'tip' not in data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        new_tip = HealthTip(
            tip=data['tip']
        )

        db.session.add(new_tip)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Health tip added successfully!', 'data': new_tip.id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/preventive-measures', methods=['GET'])
@jwt_required()
def get_preventive_measures():
    try:
        measures = PreventiveMeasure.query.all()
        return jsonify({
            'success': True,
            'data': [measure.to_dict() for measure in measures]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching preventive measures: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching data.'}), 500
    
@app.route('/api/preventive-measures', methods=['POST'])
@jwt_required()
def add_preventive_measure():
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'title' not in data or 'description' not in data:
            return jsonify({'success': False, 'message': 'Title and description are required'}), 400

        # Create a new preventive measure instance
        new_measure = PreventiveMeasure(
            title=data['title'],
            description=data['description']
        )

        # Save to the database
        db.session.add(new_measure)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Preventive measure added successfully!',
            'data': new_measure.to_dict()
        }), 201
    except Exception as e:
        print(f"Error adding preventive measure: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while adding data.'}), 500


# Main entry point
if __name__ == '__main__':
    app.run(port=5000, debug=True)
