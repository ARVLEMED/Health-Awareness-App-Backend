from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import bcrypt

# contains definitions of tables and associated schema constructs
metadata = MetaData()

# create the Flask SQLAlchemy extension
db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self,password):
        salt = bcrypt.gensalt()
        self.password =bcrypt.hashpw(
            password.encode('utf-8'), salt).decode('utf8')
        
    def check_password(self,password):
            return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        
    def __repr__(self):
        return f'<User {self.username}>'
    
class Disease(db.Model):
    __tablename__ = 'diseases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)  # Communicable or Non-communicable
    causes = db.Column(db.JSON, nullable=True, default=[])  # Default to empty list
    symptoms = db.Column(db.JSON, nullable=True, default=[])
    prevention = db.Column(db.JSON, nullable=True, default=[])
    treatment = db.Column(db.JSON, nullable=True, default=[])
    pathogen = db.Column(db.String(255), nullable=True)
    mode_of_spread = db.Column(db.String(255), nullable=True)
    incubation_period = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Disease {self.name}>"


class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    usage = db.Column(db.Text, nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    side_effects = db.Column(db.Text, nullable=True)
    precautions = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return f"<Drug {self.name}>"
    
class HealthTip(db.Model):
    __tablename__ = 'health_tips'
    id = db.Column(db.Integer, primary_key=True)
    tip = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<HealthTip {self.tip}>"

class PreventiveMeasure(db.Model):
    __tablename__ = 'preventive_measures'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }