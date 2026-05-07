"""
Script to create a trained model for the Flask app.
This creates a mock model since the dataset is not available locally.
For production use, you should run the full notebook with your actual dataset.
"""

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

print("Creating mock model for testing purposes...")
print("Note: For production, run the full notebook with your actual dataset.")

# Create a mock trained model
# Based on the notebook, it appears to use RandomForestRegressor
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42
)

# Create mock training data with the expected features
# You'll need to adjust these feature names based on your actual data
n_samples = 100
n_features = 20

X_mock = np.random.randn(n_samples, n_features)
y_mock = np.random.randn(n_samples) * 1000 + 1500  # Mock revenue values

# Train the mock model
model.fit(X_mock, y_mock)

# Save the model
joblib.dump(model, "best_model.pkl")
print("✓ Model saved as 'best_model.pkl'")

# Also verify the scaler exists
try:
    scaler = joblib.load("scaler.pkl")
    print("✓ Scaler file 'scaler.pkl' found")
except:
    print("⚠ Warning: scaler.pkl not found, creating a mock scaler")
    scaler = StandardScaler()
    scaler.fit(X_mock)
    joblib.dump(scaler, "scaler.pkl")
    print("✓ Scaler saved as 'scaler.pkl'")

print("\n" + "="*60)
print("IMPORTANT: This is a MOCK model for testing only!")
print("To create a real model:")
print("1. Upload your dataset 'dataset_clean (1).xlsx'")
print("2. Run the Jupyter notebook 'modele_3_Gridsearch.ipynb'")
print("3. The notebook will create the actual trained model")
print("="*60)
