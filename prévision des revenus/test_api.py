"""
Test script for the Flask API
"""
import requests
import json

# API endpoint
BASE_URL = "http://127.0.0.1:5000"

print("="*60)
print("Testing Flask API")
print("="*60)

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Make sure the Flask app is running (python app.py)")
    exit(1)

# Test 2: Get features
print("\n2. Getting required features...")
try:
    response = requests.get(f"{BASE_URL}/features")
    features_data = response.json()
    print(f"   ✓ Number of features: {features_data['count']}")
    print(f"   Features: {features_data['features'][:5]}... (showing first 5)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Make a prediction with sample data
print("\n3. Testing prediction endpoint...")
sample_data = {
    "age": 30,
    "attendance_rate": 0.85,
    "avg_test_score": 75.5,
    "engagement_score": 0.8,
    "login_frequency_per_week": 5,
    "time_spent_hours_per_week": 15.5,
    "total_payments": 500,
    "months_subscribed": 6,
    "days_since_last_login": 2,
    "course_completion_rate": 0.7,
    "assignment_submission_rate": 0.75,
    "video_watch_percentage": 0.8,
    "discount_used": 0,
    "payment_delay_days": 0,
    "upgrade_history": 1,
    "churn": 0,
    # Categorical features (will be one-hot encoded)
    "gender_Male": 1,
    "english_level_Intermediate": 1,
    "package_type_Standard": 1,
    "profession_Student": 1,
    "income_level_Medium": 1,
    "city_Paris": 1,
    "registration_channel_Website": 1
}

try:
    response = requests.post(
        f"{BASE_URL}/predict",
        json=sample_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    if result.get("status") == "success":
        print(f"   ✓ Predicted lifetime value: ${result['prediction']:.2f}")
    else:
        print(f"   Response: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("✓ API testing completed!")
print("="*60)
