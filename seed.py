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


# Use the application context to add data
with app.app_context():
    # Seeding diseases
    for disease in diseases:
        new_disease = Disease(
            name=disease['name'],
            category=disease.get('category', 'Unknown'),
            symptoms=", ".join(disease.get('symptoms', [])),
            causes=", ".join(disease.get('causes', [])),
            prevention=", ".join(disease.get('prevention', [])),
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

