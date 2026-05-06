from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import json
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"]) # This allows Angular (running on a different port) to call this API

# Load model, scaler, and features once at startup
model    = joblib.load('churn_model.pkl')
scaler   = joblib.load('scaler.pkl')
features = json.load(open('features.json'))

print("Model loaded successfully")
print("Expected features:", features)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data sent from Angular
        data = request.get_json()
        print("Received data:", data)

        # Build input row with all features set to 0 first
        row = {f: 0 for f in features}

        # English level mapping (ordinal)
        english_map = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}

        # Fill values from request
        direct_fields = [
            'age', 'course_completion_rate', 'attendance_rate',
            'avg_test_score', 'days_since_last_login',
            'upgrade_history', 'package_duration_months', 'total_payments'
        ]
        for field in direct_fields:
            if field in data and field in row:
                row[field] = float(data[field])

        # English level (encoded)
        if 'english_level' in data:
            row['english_level'] = english_map.get(data['english_level'], 0)

        # One-hot encoded fields
        if 'registration_channel' in data:
            key = f"registration_channel_{data['registration_channel']}"
            if key in row:
                row[key] = 1

        if 'profession' in data:
            key = f"profession_{data['profession']}"
            if key in row:
                row[key] = 1

        # Build DataFrame in the exact feature order
        input_df = pd.DataFrame([row])[features]
        print("Input vector:", input_df.to_dict(orient='records'))

        # Get prediction and probability
        proba      = model.predict_proba(input_df)[0][1]
        prediction = int(proba >= 0.5)

        result = {
            'prediction': prediction,
            'probability': round(float(proba), 4),
            'probability_percent': round(float(proba) * 100, 2),
            'risk_level': (
                'High'   if proba >= 0.7 else
                'Medium' if proba >= 0.5 else
                'Low'
            ),
            'message': (
                'This student is likely to churn.'
                if prediction == 1
                else 'This student is likely to stay.'
            )
        }

        print("Result:", result)
        return jsonify(result)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': 'churn_random_forest'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)