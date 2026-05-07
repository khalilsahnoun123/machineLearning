"""
Script de test rapide pour vérifier l'API Revenue
"""

import requests
import json

print("="*60)
print("TEST DE L'API REVENUE")
print("="*60)

# Test 1: Health check
print("\n1. Test Health Check...")
try:
    response = requests.get("http://127.0.0.1:5002/health", timeout=5)
    if response.status_code == 200:
        print("✅ API accessible!")
        print(f"   Réponse: {response.json()}")
    else:
        print(f"❌ Erreur: Status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ ERREUR: L'API n'est pas démarrée!")
    print("   Solution: Lancez 'python app.py' dans le dossier 'prévision des revenus'")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: Get features
print("\n2. Test Get Features...")
try:
    response = requests.get("http://127.0.0.1:5002/features", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['count']} features disponibles")
    else:
        print(f"❌ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3: Prediction
print("\n3. Test Prediction...")
test_data = {
    "age": 20,
    "gender": "M",
    "enrollment_year": 2023,
    "program": "Computer Science",
    "gpa": 3.5,
    "attendance_rate": 85,
    "study_hours_per_week": 15,
    "extracurricular_activities": 2,
    "previous_education_level": "High School",
    "family_income": 50000,
    "distance_from_home": 10,
    "part_time_job": 0,
    "scholarship": 1,
    "health_status": "Good",
    "relationship_status": "Single",
    "stress_level": 3,
    "social_support": 4,
    "career_goals_clarity": 4,
    "financial_stress": 2,
    "academic_pressure": 3
}

try:
    response = requests.post(
        "http://127.0.0.1:5002/predict",
        json=test_data,
        timeout=5
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Prédiction réussie!")
        print(f"   Revenu prédit: {result['prediction']:.2f} $")
    else:
        print(f"❌ Erreur: Status {response.status_code}")
        print(f"   Message: {response.text}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "="*60)
print("FIN DES TESTS")
print("="*60)
