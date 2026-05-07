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
        
        # Ensure all expected features are present
        for feature in feature_names:
            if feature not in df.columns:
                df[feature] = 0  # Default value for missing features
        
        # Select only the features used during training, in the correct order
        df = df[feature_names]
        
        # Scale the features
        df_scaled = scaler.transform(df)
        
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