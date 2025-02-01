from app import app, db
from models import Disease, Drug, HealthTip, PreventiveMeasure  # Import your models
import json

# Load the JSON file
with open('data/diseases_data.json', 'r') as file:
    diseases = json.load(file)

with open('data/drugs_data.json', 'r') as file:
    drugs = json.load(file)

with open('data/health_tips_data.json', 'r') as file:
    health_tips = json.load(file)

with open('data/preventive_measures_data.json', 'r') as file:
    preventive_measures = json.load(file)  # Load preventive measures data

# Use the application context to add data
with app.app_context():
    # Seeding diseases
    for disease in diseases:
        new_disease = Disease(
            name=disease['name'],
            category=disease.get('category', 'Unknown'),
            symptoms=", ".join(disease.get('symptoms', [])),
            causes=", ".join(disease.get('causes', [])),
            prevention=", ".join(disease.get('prevention', [])),  # Prevention linked only to disease itself
            treatment=", ".join(disease.get('treatments', []))
        )
        db.session.add(new_disease)

    db.session.commit()

print("Diseases populated successfully!")

with app.app_context():
    # Seeding drugs
    for drug in drugs:
        new_drug = Drug(
            name=drug['name'],
            category=drug.get('category', 'Unknown'),
            usage=drug.get('usage', 'No usage description available'),
            dosage=drug.get('dosage', 'No dosage information available'),
            side_effects=", ".join(drug.get('side_effects', [])),
            precautions=", ".join(drug.get('precautions', []))
        )
        db.session.add(new_drug)

    db.session.commit()

print("Drugs database populated successfully!")

with app.app_context():
    # Seeding health tips
    for health_tip in health_tips:
        new_health_tip = HealthTip(tip=health_tip['tip'])
        db.session.add(new_health_tip)

    db.session.commit()

print("Health tips data successfully seeded!")

with app.app_context():
    # Seeding preventive measures
    for preventive_measure in preventive_measures:
        new_preventive_measure = PreventiveMeasure(
            title=preventive_measure['title'],  # Use 'title' instead of 'measure'
            description=preventive_measure.get('description', 'No description available')  # Optional description
        )
        db.session.add(new_preventive_measure)

    db.session.commit()

print("Preventive measures data successfully seeded!")
