from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import numpy as np

app = Flask(__name__)
CORS(app)

# Load model, scaler, and feature names
model_path = os.path.join(os.path.dirname(__file__), "best_model.pkl")
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
features_path = os.path.join(os.path.dirname(__file__), "feature_names.pkl")

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
feature_names = joblib.load(features_path)

print(f"✓ Model loaded successfully")
print(f"✓ Expected features: {len(feature_names)}")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Create DataFrame from input data
        df = pd.DataFrame([data])
        
        # One-hot encode categorical variables to match training features
        categorical_cols = ['gender', 'english_level', 'package_type', 'profession', 'income_level', 'city', 'registration_channel']
        
        # Get numeric columns
        numeric_cols = ['age', 'attendance_rate', 'avg_test_score', 'engagement_score', 
                       'login_frequency_per_week', 'time_spent_hours_per_week', 'package_price',
                       'package_duration_months', 'total_payments', 'churn_risk', 'academic_success',
                       'days_since_last_login', 'course_completion_rate', 'assignment_submission_rate',
                       'video_watch_percentage', 'discount_used', 'payment_delay_days', 
                       'upgrade_history', 'churn']
        
        # Extract numeric features
        df_numeric = df[numeric_cols]
        
        # One-hot encode categorical features
        df_categorical = df[categorical_cols]
        df_encoded = pd.get_dummies(df_categorical, drop_first=True)
        
        # Combine numeric and encoded categorical
        df_combined = pd.concat([df_numeric, df_encoded], axis=1)
        
        # Ensure all expected features are present (add missing columns with 0)
        for feature in feature_names:
            if feature not in df_combined.columns:
                df_combined[feature] = 0
        
        # Select only the features used during training, in the correct order
        df_final = df_combined[feature_names]
        
        # Scale the features
        df_scaled = scaler.transform(df_final)
        
        # Make prediction
        prediction = model.predict(df_scaled)
        
        return jsonify({
            "prediction": float(prediction[0]),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
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