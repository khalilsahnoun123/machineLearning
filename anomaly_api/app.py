from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import pandas as pd


app = Flask(__name__)
CORS(app, origins=["http://localhost:4200", "http://127.0.0.1:4200"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "anomaly_model.joblib")

artifact = joblib.load(MODEL_PATH)
model = artifact.get("pipeline") if isinstance(artifact, dict) else artifact

DEFAULT_FEATURES = [
    "age",
    "gender",
    "english_level",
    "attendance_rate",
    "avg_test_score",
    "engagement_score",
    "login_frequency_per_week",
    "time_spent_hours_per_week",
    "package_type",
    "package_price",
    "package_duration_months",
    "total_payments",
    "profession",
    "income_level",
    "city",
    "registration_channel",
    "days_since_last_login",
    "course_completion_rate",
    "assignment_submission_rate",
    "video_watch_percentage",
    "payment_delay_days",
    "discount_used",
    "upgrade_history",
    "churn",
    "lifetime_value",
    "churn_risk",
    "academic_success",
]

DEFAULT_VALUES = {
    "age": 25,
    "gender": "Male",
    "english_level": "Intermediate",
    "attendance_rate": 0.75,
    "avg_test_score": 70,
    "engagement_score": 0.6,
    "login_frequency_per_week": 3,
    "time_spent_hours_per_week": 6,
    "package_type": "Standard",
    "package_price": 300,
    "package_duration_months": 6,
    "total_payments": 1,
    "profession": "Student",
    "income_level": "Medium",
    "city": "Tunis",
    "registration_channel": "Online",
    "days_since_last_login": 7,
    "course_completion_rate": 0.65,
    "assignment_submission_rate": 0.7,
    "video_watch_percentage": 0.6,
    "payment_delay_days": 0,
    "discount_used": 0,
    "upgrade_history": 0,
    "churn": 0,
    "lifetime_value": 300,
    "churn_risk": 0.3,
    "academic_success": "Average",
}

ALIASES = {
    "assignment_completion": "assignment_submission_rate",
    "study_hours_weekly": "time_spent_hours_per_week",
}

ORDINAL_MAPS = {
    "academic_success": {"Low": 0, "Average": 1, "High": 2},
    "discount_used": {"No": 0, "Yes": 1},
    "churn": {"No": 0, "Yes": 1},
}

CATEGORICAL_FIELDS = {
    "gender",
    "english_level",
    "profession",
    "income_level",
    "city",
    "registration_channel",
    "package_type",
}

PERCENTAGE_FIELDS = {
    "attendance_rate",
    "engagement_score",
    "course_completion_rate",
    "assignment_submission_rate",
    "video_watch_percentage",
    "churn_risk",
}


def _unwrap_estimator(candidate):
    if hasattr(candidate, "steps") and candidate.steps:
        return candidate.steps[-1][1]
    return candidate


estimator = _unwrap_estimator(model)


def _expected_features():
    if isinstance(artifact, dict) and artifact.get("feature_columns"):
        return list(artifact["feature_columns"])
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    if hasattr(estimator, "feature_names_in_"):
        return list(estimator.feature_names_in_)

    n_features = getattr(model, "n_features_in_", None) or getattr(estimator, "n_features_in_", None)
    if n_features:
        return DEFAULT_FEATURES[: int(n_features)]

    return DEFAULT_FEATURES


FEATURES = _expected_features()


def _coerce_value(field, value):
    if value is None or value == "":
        return DEFAULT_VALUES.get(field, 0)

    if field in CATEGORICAL_FIELDS:
        return str(value)

    if isinstance(value, str):
        value = ORDINAL_MAPS.get(field, {}).get(value, value)

    try:
        number = float(value)
    except (TypeError, ValueError):
        return DEFAULT_VALUES.get(field, 0)

    if field in PERCENTAGE_FIELDS and number > 1:
        return number / 100

    return number


def _payload_with_aliases(data):
    payload = dict(data or {})
    for source, target in ALIASES.items():
        if source in payload and target not in payload:
            payload[target] = payload[source]
    return payload


def _build_input(data):
    payload = _payload_with_aliases(data)
    row = {
        feature: _coerce_value(feature, payload.get(feature, DEFAULT_VALUES.get(feature, 0)))
        for feature in FEATURES
    }
    return pd.DataFrame([row], columns=FEATURES)


def _normalize_prediction(raw_prediction):
    value = int(np.asarray(raw_prediction).ravel()[0])
    detector_names = {"IsolationForest", "OneClassSVM", "LocalOutlierFactor", "EllipticEnvelope"}
    model_name = type(estimator).__name__

    if value == -1:
        is_anomaly = True
    elif model_name in detector_names:
        is_anomaly = False
    else:
        is_anomaly = value == 1

    label = "Anomaly" if is_anomaly else "Normal"
    return value, is_anomaly, label


def _score_sample(input_df):
    if hasattr(model, "decision_function"):
        score = float(np.asarray(model.decision_function(input_df)).ravel()[0])
        confidence = round(min(abs(score) * 100, 100), 2)
        return score, confidence

    if hasattr(model, "score_samples"):
        score = float(np.asarray(model.score_samples(input_df)).ravel()[0])
        confidence = round(min(abs(score) * 10, 100), 2)
        return score, confidence

    if hasattr(model, "predict_proba"):
        proba = np.asarray(model.predict_proba(input_df))[0]
        confidence = round(float(proba.max()) * 100, 2)
        anomaly_probability = float(proba[1]) if len(proba) > 1 else float(proba.max())
        return anomaly_probability, confidence

    return None, None


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        input_df = _build_input(data)

        raw_prediction = model.predict(input_df)
        prediction, is_anomaly, label = _normalize_prediction(raw_prediction)
        anomaly_score, confidence = _score_sample(input_df)
        threshold = artifact.get("threshold") if isinstance(artifact, dict) else None
        label_names = artifact.get("label_names") if isinstance(artifact, dict) else None

        return jsonify({
            "prediction": prediction,
            "label": label,
            "is_anomaly": is_anomaly,
            "risk_level": "High" if is_anomaly else "Low",
            "anomaly_score": None if anomaly_score is None else round(anomaly_score, 6),
            "confidence": confidence,
            "threshold": threshold,
            "label_names": label_names,
            "features_used": FEATURES,
            "message": (
                "This student profile looks unusual and should be reviewed."
                if is_anomaly
                else "This student profile follows the expected behavioral pattern."
            ),
        })

    except Exception as exc:
        app.logger.exception("Anomaly prediction error")
        return jsonify({"error": str(exc)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": type(model).__name__,
        "artifact": type(artifact).__name__,
        "features": FEATURES,
    })


if __name__ == "__main__":
    print("Anomaly API running on http://127.0.0.1:5004")
    app.run(host="0.0.0.0", port=5004, debug=True)
