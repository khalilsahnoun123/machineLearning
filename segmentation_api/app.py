"""
╔══════════════════════════════════════════════════════════════╗
║  app.py — Student Segmentation API                          ║
║  EnglishForU · KMeans Clustering · Flask 5000               ║
╚══════════════════════════════════════════════════════════════╝

Expected model artefacts (same folder as this file):
  • kmeans_model.pkl  (or my_model.pkl)
  • scaler.pkl        (or my_scaler.pkl)

Features the model was trained on (notebook order):
  attendance_rate, login_frequency_per_week, time_spent_hours_per_week,
  days_since_last_login, avg_test_score, engagement_score,
  course_completion_rate, assignment_submission_rate, video_watch_percentage,
  performance_index, activity_ratio, risk_score, content_engagement,
  learning_efficiency
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
import json
import os

app = Flask(__name__)
CORS(app)  # allow Angular dev-server (localhost:4200)

# ── 1.  Load artefacts ──────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _try_load(names: list[str]):
    """Try a list of candidate filenames; return first that exists."""
    for name in names:
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
    return None


kmeans = _try_load(["kmeans_model.pkl", "my_model.pkl", "model.pkl"])
scaler = _try_load(["scaler.pkl", "my_scaler.pkl"])

if kmeans is None:
    print("⚠️  WARNING — no KMeans model file found. "
          "A rule-based fallback will be used instead.")
if scaler is None:
    print("⚠️  WARNING — no scaler file found. Raw values will be used.")

# Ordered list matching the scaler / KMeans training columns
FEATURE_ORDER = [
    "attendance_rate",
    "login_frequency_per_week",
    "time_spent_hours_per_week",
    "days_since_last_login",
    "avg_test_score",
    "engagement_score",
    "course_completion_rate",
    "assignment_submission_rate",
    "video_watch_percentage",
    "performance_index",
    "activity_ratio",
    "risk_score",
    "content_engagement",
    "learning_efficiency",
]

# Optional: override with saved feature list if present
features_path = os.path.join(BASE_DIR, "my_features.json")
if os.path.exists(features_path):
    with open(features_path) as f:
        FEATURE_ORDER = json.load(f)

# ── 2.  Segment catalogue ───────────────────────────────────────────────────

SEGMENTS = {
    # key = cluster id (int), determined at runtime
    # Filled dynamically after prediction; template below used for lookup.
    "excellent": {
        "segment": "⭐ Excellent Student",
        "description": (
            "High performer with strong engagement. Consistently attends class, "
            "completes assignments on time and scores well on tests."
        ),
        "recommendation": (
            "Offer advanced challenges, leadership roles or mentoring opportunities "
            "to maintain motivation and channel energy productively."
        ),
        "risk": "🟢 Low Risk",
        "color": "#27AE60",
    },
    "discreet": {
        "segment": "📚 Discreet Studious",
        "description": (
            "Good academic scores but lower social interaction. Prefers self-paced "
            "learning; may be under-using collaborative features."
        ),
        "recommendation": (
            "Encourage participation in group activities and discussion forums. "
            "Introduce peer-study sessions to boost engagement."
        ),
        "risk": "🟡 Medium Risk",
        "color": "#F39C12",
    },
    "struggling": {
        "segment": "💬 Engaged but Struggling",
        "description": (
            "High platform engagement and participation but academic scores remain "
            "below average. Active presence that needs academic support."
        ),
        "recommendation": (
            "Provide targeted tutoring, remedial content and structured study plans. "
            "Pair with high-performing peers for collaborative learning."
        ),
        "risk": "🟠 Medium-High Risk",
        "color": "#E67E22",
    },
    "at_risk": {
        "segment": "⚠️ At-Risk Student",
        "description": (
            "Low performance combined with low engagement. Minimal platform activity, "
            "poor test results and high dropout probability."
        ),
        "recommendation": (
            "Trigger immediate academic intervention: personal tutor contact, "
            "motivational coaching and a recovery action plan."
        ),
        "risk": "🔴 High Risk",
        "color": "#C0392B",
    },
}

# ── 3.  Feature engineering (mirrors the notebook) ──────────────────────────

def build_feature_vector(data: dict) -> np.ndarray:
    """
    Accept the 5 Angular form fields and reconstruct all 14 training features.
    Missing fields get sensible median defaults so the scaler stays happy.
    """
    # --- Direct inputs (normalise to [0,1] where the model expects fractions) ---
    attendance_rate    = float(data.get("attendance_rate", 75)) / 100      # % → fraction
    avg_test_score     = float(data.get("avg_test_score", 70))             # kept as 0-100
    engagement_score   = float(data.get("engagement_score", 60)) / 100    # % → fraction
    assignment_sub     = float(data.get("assignment_completion", 80)) / 100
    study_hours        = float(data.get("study_hours_weekly", 10))

    # --- Defaults for features not in the Angular form ---
    login_freq          = 3.0          # sessions / week  (platform median)
    days_since_login    = 7.0          # days             (platform median)
    course_completion   = assignment_sub * 0.9   # correlated proxy
    video_watch_pct     = engagement_score * 0.85

    # --- Engineered features (exact formulae from notebook) ---
    performance_index = (
        (avg_test_score / 100) + attendance_rate + course_completion
    ) / 3

    activity_ratio = login_freq / (study_hours + 0.001)

    risk_score = days_since_login * (1 - engagement_score)

    content_engagement = (
        video_watch_pct + assignment_sub + course_completion
    ) / 3

    learning_efficiency = avg_test_score / (study_hours + 0.001)

    # Build the vector in training column order
    vector = {
        "attendance_rate":           attendance_rate,
        "login_frequency_per_week":  login_freq,
        "time_spent_hours_per_week": study_hours,
        "days_since_last_login":     days_since_login,
        "avg_test_score":            avg_test_score,
        "engagement_score":          engagement_score,
        "course_completion_rate":    course_completion,
        "assignment_submission_rate":assignment_sub,
        "video_watch_percentage":    video_watch_pct,
        "performance_index":         performance_index,
        "activity_ratio":            activity_ratio,
        "risk_score":                risk_score,
        "content_engagement":        content_engagement,
        "learning_efficiency":       learning_efficiency,
    }

    return np.array([vector[f] for f in FEATURE_ORDER]).reshape(1, -1)


# ── 4.  Rule-based fallback (used when no pkl is available) ─────────────────

def rule_based_cluster(data: dict) -> int:
    """
    Reproduces the notebook's SEGMENT_NAMES logic without a trained model.
    Returns a cluster id 0-3.
    """
    perf  = (float(data.get("avg_test_score", 70)) / 100
             + float(data.get("attendance_rate", 75)) / 100
             + float(data.get("assignment_completion", 80)) / 100) / 3
    eng   = float(data.get("engagement_score", 60)) / 100

    if perf >= 0.70 and eng >= 0.50:
        return 0   # Excellent
    elif perf >= 0.60 and eng < 0.50:
        return 1   # Discreet studious
    elif perf < 0.60 and eng >= 0.50:
        return 2   # Engaged but struggling
    else:
        return 3   # At-risk


def cluster_to_profile(cluster_id: int, perf: float, eng: float) -> dict:
    """
    Map a raw cluster number to a human-readable profile.
    The mapping is data-driven from the notebook's logic.
    """
    if perf >= 0.70 and eng >= 0.50:
        key = "excellent"
    elif perf >= 0.60 and eng < 0.50:
        key = "discreet"
    elif perf < 0.60 and eng >= 0.50:
        key = "struggling"
    else:
        key = "at_risk"

    profile = SEGMENTS[key].copy()
    profile["cluster"] = cluster_id
    return profile


# ── 5.  Route ────────────────────────────────────────────────────────────────

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)

        # Convenience values for profile resolution
        perf = (
            float(data.get("avg_test_score", 70)) / 100
            + float(data.get("attendance_rate", 75)) / 100
            + float(data.get("assignment_completion", 80)) / 100
        ) / 3
        eng = float(data.get("engagement_score", 60)) / 100

        # ── Predict cluster ──────────────────────────────────────────────────
        if kmeans is not None:
            X = build_feature_vector(data)
            X_scaled = scaler.transform(X) if scaler is not None else X
            cluster_id = int(kmeans.predict(X_scaled)[0])
        else:
            cluster_id = rule_based_cluster(data)

        # ── Build response ───────────────────────────────────────────────────
        profile = cluster_to_profile(cluster_id, perf, eng)

        # Radar chart data — 5 normalised scores (0-100) for the frontend
        radar = {
            "Attendance":   round(float(data.get("attendance_rate", 75)), 1),
            "Test Score":   round(float(data.get("avg_test_score", 70)), 1),
            "Engagement":   round(float(data.get("engagement_score", 60)), 1),
            "Assignments":  round(float(data.get("assignment_completion", 80)), 1),
            "Study Hours":  min(round(float(data.get("study_hours_weekly", 10)) * 5, 1), 100),
        }

        return jsonify({
            "cluster":        profile["cluster"],
            "segment":        profile["segment"],
            "description":    profile["description"],
            "recommendation": profile["recommendation"],
            "risk":           profile["risk"],
            "color":          profile["color"],
            "action":         _build_action(profile["risk"]),
            "radar":          radar,
        })

    except Exception as exc:
        app.logger.exception("Prediction error")
        return jsonify({"error": str(exc)}), 500


def _build_action(risk_level: str) -> str:
    actions = {
        "🟢 Low Risk":         "Keep up the excellent work! Explore advanced modules.",
        "🟡 Medium Risk":      "Join group study sessions and engage more in forums.",
        "🟠 Medium-High Risk": "Schedule a tutoring session and follow the recovery plan.",
        "🔴 High Risk":        "Immediate intervention required — contact your academic advisor.",
    }
    return actions.get(risk_level, "Review your study habits and seek support.")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": kmeans is not None,
        "scaler_loaded": scaler is not None,
        "features": FEATURE_ORDER,
    })


# ── 6.  Entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Segmentation API running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
