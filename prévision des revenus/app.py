from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import numpy as np
import time

app = Flask(__name__)
CORS(app)

# Load model, scaler, and feature names
model_path = os.path.join(os.path.dirname(__file__), "best_model.pkl")
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
features_path = os.path.join(os.path.dirname(__file__), "feature_names.pkl")

print("⏳ Loading model files...")
start_time = time.time()

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
feature_names = joblib.load(features_path)

load_time = time.time() - start_time
print(f"✓ Model loaded successfully in {load_time:.2f}s")
print(f"✓ Expected features: {len(feature_names)}")
print(f"✓ Model type: {type(model).__name__}")
print(f"✓ Ready to accept predictions on port 5002")

@app.route('/predict', methods=['POST'])
def predict():
    """
    Optimized prediction endpoint with performance tracking
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        # Step 1: Create feature vector directly (faster than DataFrame operations)
        feature_vector = {}
        
        # Numeric columns
        numeric_cols = ['age', 'attendance_rate', 'avg_test_score', 'engagement_score', 
                       'login_frequency_per_week', 'time_spent_hours_per_week', 'package_price',
                       'package_duration_months', 'total_payments', 'churn_risk', 'academic_success',
                       'days_since_last_login', 'course_completion_rate', 'assignment_submission_rate',
                       'video_watch_percentage', 'discount_used', 'payment_delay_days', 
                       'upgrade_history', 'churn']
        
        # Add numeric features
        for col in numeric_cols:
            feature_vector[col] = float(data.get(col, 0))
        
        # Step 2: One-hot encode categorical variables manually (faster)
        categorical_mappings = {
            'gender': ['Female', 'Male'],
            'english_level': ['Beginner', 'Intermediate', 'Advanced'],
            'package_type': ['Basic', 'Standard', 'Premium'],
            'profession': ['Business Owner', 'Doctor', 'Engineer', 'Other', 'Student', 'Teacher', 'Unemployed'],
            'income_level': ['Low', 'Medium', 'High'],
            'city': ['Tunis', 'Ariana', 'Bizerte', 'Gabès', 'Gafsa', 'Kairouan', 'Monastir', 'Nabeul', 'Sfax', 'Sousse'],
            'registration_channel': ['Direct', 'Facebook', 'Google', 'Instagram', 'Referral']
        }
        
        # Encode categorical features (drop_first=True logic)
        for cat_col, values in categorical_mappings.items():
            user_value = data.get(cat_col, values[0])
            # Skip first value (drop_first=True)
            for value in values[1:]:
                feature_vector[f"{cat_col}_{value}"] = 1 if user_value == value else 0
        
        # Step 3: Create ordered array matching feature_names
        X = np.zeros((1, len(feature_names)))
        for i, feature in enumerate(feature_names):
            X[0, i] = feature_vector.get(feature, 0)
        
        # Step 4: Scale and predict
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)[0]
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Categorize the prediction
        if prediction < 1000:
            category = "Low"
            interpretation = "The student has low revenue potential. Consider targeted engagement strategies."
        elif prediction < 1500:
            category = "Average"
            interpretation = "The student has standard revenue potential. Improvement opportunities available."
        elif prediction < 2000:
            category = "Good"
            interpretation = "The student shows good revenue potential. Maintain engagement and offer upgrades."
        else:
            category = "Excellent"
            interpretation = "The student has excellent revenue potential. Priority for premium services."
        
        print(f"✓ Prediction completed in {execution_time:.2f}ms - Result: ${prediction:.2f} ({category})")
        
        return jsonify({
            "prediction": float(prediction),
            "category": category,
            "interpretation": interpretation,
            "execution_time_ms": round(execution_time, 2),
            "status": "success"
        })
    
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        print(f"✗ Error after {execution_time:.2f}ms: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "execution_time_ms": round(execution_time, 2)
        }), 400

@app.route('/features', methods=['GET'])
def get_features():
    """Endpoint to get the list of required features"""
    return jsonify({
        "features": feature_names,
        "count": len(feature_names)
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "features_count": len(feature_names)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002)