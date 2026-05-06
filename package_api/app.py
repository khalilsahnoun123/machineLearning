from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app, origins="*")

model        = joblib.load('model_package.pkl')
preprocessor = joblib.load('preprocessor.pkl')
encoder      = joblib.load('label_encoder.pkl')

print("Model loaded successfully")
print("Package classes:", encoder.classes_)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("Received data:", data)

        row = {
            "age":                        float(data.get("age", 0)),
            "attendance_rate":            float(data.get("attendance_rate", 0)),
            "avg_test_score":             float(data.get("avg_test_score", 0)),
            "engagement_score":           float(data.get("engagement_score", 0)),
            "login_frequency_per_week":   float(data.get("login_frequency_per_week", 0)),
            "time_spent_hours_per_week":  float(data.get("time_spent_hours_per_week", 0)),
            "churn_risk":                 float(data.get("churn_risk", 0)),
            "academic_success":           float(data.get("academic_success", 0)) if str(data.get("academic_success", "0")).replace('.','').isnumeric() else float({"Low": 0, "Average": 1, "High": 2}.get(data.get("academic_success", "Average"), 1)),
            "days_since_last_login":      float(data.get("days_since_last_login", 0)),
            "course_completion_rate":     float(data.get("course_completion_rate", 0)),
            "assignment_submission_rate": float(data.get("assignment_submission_rate", 0)),
            "video_watch_percentage":     float(data.get("video_watch_percentage", 0)),
            "discount_used":              float(data.get("discount_used", 0)),
            "payment_delay_days":         float(data.get("payment_delay_days", 0)),
            "upgrade_history":            float(data.get("upgrade_history", 0)),
            "churn":                      float(data.get("churn", 0)),
            "gender":                     str(data.get("gender", "Male")),
            "english_level":              str(data.get("english_level", "Beginner")),
            "profession":                 str(data.get("profession", "Student")),
            "income_level":               str(data.get("income_level", "Medium")),
            "city":                       str(data.get("city", "Tunis")),
            "registration_channel":       str(data.get("registration_channel", "Online")),
        }

        input_df = pd.DataFrame([row])

        numeric_cols = [
            "age", "attendance_rate", "avg_test_score", "engagement_score",
            "login_frequency_per_week", "time_spent_hours_per_week", "churn_risk",
            "academic_success", "days_since_last_login", "course_completion_rate",
            "assignment_submission_rate", "video_watch_percentage", "discount_used",
            "payment_delay_days", "upgrade_history", "churn"
        ]
        for col in numeric_cols:
            input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0).astype(np.float64)

        cat_cols = ["gender", "english_level", "profession", "income_level", "city", "registration_channel"]
        for col in cat_cols:
            input_df[col] = input_df[col].astype(str)

        X_pre   = preprocessor.transform(input_df)
        X_dense = X_pre.toarray() if hasattr(X_pre, "toarray") else X_pre

        y_encoded  = model.predict(X_dense).astype(int)
        prediction = encoder.inverse_transform(y_encoded)[0]

        proba      = model.predict_proba(X_dense)[0]
        confidence = round(float(proba.max()) * 100, 2)

        class_probas = {
            cls: round(float(p) * 100, 2)
            for cls, p in zip(encoder.classes_, proba)
        }

        result = {
            "prediction":   prediction,
            "confidence":   confidence,
            "all_packages": class_probas,
            "message":      f"Cet étudiant correspond au package : {prediction}"
        }

        print("Result:", result)
        return jsonify(result)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status":  "ok",
        "model":   "XGBoost",
        "classes": list(encoder.classes_)
    })


if __name__ == '__main__':
    app.run(debug=True, port=5003)