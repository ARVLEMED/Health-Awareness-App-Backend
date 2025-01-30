from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, Disease, Drug ,HealthTip,PreventiveMeasure# Import models from models.py
import json
import random
import traceback
import logging
import os
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv()


# Initialize Flask app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
    resources={r"/api/*": {"origins": "http://localhost:5173"}},  # Allow React frontend
    supports_credentials=True,  # Allow cookies
)

# Root endpoint
@app.route('/')
def index():
    return make_response('<h1>Welcome to the Health Awareness App!</h1>', 200)


@app.route('/api/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 204  # Handle preflight requests

    try:
        # Get data from the request
        data = request.get_json()
        logger.debug(f"Signup request received. Raw data: {data}")

        if data is None:
            return jsonify({"success": False, "message": "Invalid JSON or empty request"}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirmPassword = data.get('confirmPassword')

        # Input validation
        if not all([username, email, password, confirmPassword]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        if password != confirmPassword:
            return jsonify({"success": False, "message": "Passwords do not match"}), 400

        # Check if user exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
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


@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204  # Respond to preflight request

    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate input
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        # Debug: Log input data
        print(f"Login attempt with email: {data['email']}")

        # Query user from the database by email
        user = User.query.filter_by(email=data['email']).first()  # Use email here
        
        if not user:
            # Debug: User not found
            print("User not found.")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
        # Check if the password is correct
        if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
            # Debug: Password correct, generating token
            print("Password correct, generating token.")

            # Create a JWT token
            access_token = create_access_token(identity={"email": user.email})  # Use email in the token payload
            return jsonify({"success": True, "token": access_token}), 200
        else:
            # Debug: Password incorrect
            print("Incorrect password.")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401

    except Exception as e:
        # Catch any errors
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    try:
        # Query all diseases from the database
        diseases = Disease.query.all()
        
        # Debug: Log diseases count
        print(f"Diseases found: {len(diseases)}")

        # Check if any diseases were found
        if not diseases:
            return jsonify({'success': False, 'message': 'No diseases found.'}), 404

        # Format the response
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
        
        # Return the list as a JSON response
        return jsonify({'success': True, 'data': disease_list}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# API Route to Add a New Disease
@app.route('/api/diseases', methods=['POST'])
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
    

@app.route('/api/drugs', methods=['POST'])

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
    
@app.route('/api/drugs', methods=['GET'])
#@jwt_required()
def get_drugs():
    try:
        # Fetch all drugs from the database
        drugs = Drug.query.all()

        # Format the response as a list of dictionaries
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
        return jsonify({'success': False, 'message': str(e)}), 500
    
# API Route for Health Tips (GET and POST)
import random

@app.route('/api/health-tips/random', methods=['GET'])
def get_random_health_tip():
    try:
        health_tips = HealthTip.query.all()

        if not health_tips:
            return jsonify({'success': False, 'message': 'No health tips available.'}), 404

        random_tip = random.choice(health_tips)  # Select a random health tip
        return jsonify({'success': True, 'data': {'id': random_tip.id, 'tip': random_tip.tip}}), 200
    
    except Exception as e:
        # Log the error
        print(f"Error fetching random health tip: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching health tips.'}), 500

@app.route('/api/health-tips', methods=['POST'])
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
        print(f"Error fetching preventive measures: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching data.'}), 500
@app.route('/api/preventive-measures', methods=['POST'])
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
