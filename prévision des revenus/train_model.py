"""
Train the revenue prediction model using the actual dataset.
This script extracts the model training logic from the notebook.
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

print("="*60)
print("Training Revenue Prediction Model")
print("="*60)

# 1. Load the dataset
print("\n1. Loading dataset...")
df = pd.read_excel('dataset_clean (1).xlsx')
df = df.drop_duplicates(subset='student_id')
print(f"   ✓ Loaded {df.shape[0]} students with {df.shape[1]} columns")

# 2. Prepare features and target
print("\n2. Preparing features and target variable...")

# Target variable (what we want to predict)
target_col = 'lifetime_value'  # Based on the notebook, this seems to be the revenue target

# Check if the target column exists
if target_col not in df.columns:
    print(f"   Available columns: {df.columns.tolist()}")
    # Try to find a revenue-related column
    revenue_cols = [col for col in df.columns if 'payment' in col.lower() or 'revenue' in col.lower() or 'value' in col.lower()]
    if revenue_cols:
        target_col = revenue_cols[0]
        print(f"   Using '{target_col}' as target variable")
    else:
        raise ValueError("Could not find revenue/payment column")

y = df[target_col]

# Select numeric features (excluding ID and target)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
exclude_cols = ['student_id', target_col]
feature_cols = [col for col in numeric_cols if col not in exclude_cols]

# Handle categorical variables if needed
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
if categorical_cols:
    print(f"   Found categorical columns: {categorical_cols}")
    # One-hot encode categorical variables
    df_encoded = pd.get_dummies(df[categorical_cols], drop_first=True)
    X_numeric = df[feature_cols]
    X = pd.concat([X_numeric, df_encoded], axis=1)
else:
    X = df[feature_cols]

print(f"   ✓ Features: {X.shape[1]} columns")
print(f"   ✓ Target: {target_col}")

# 3. Split the data
print("\n3. Splitting data into train/test sets...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   ✓ Training set: {X_train.shape[0]} samples")
print(f"   ✓ Test set: {X_test.shape[0]} samples")

# 4. Scale the features
print("\n4. Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("   ✓ Features scaled")

# 5. Train models with GridSearch
print("\n5. Training models (this may take a few minutes)...")

models = {
    'RandomForest': {
        'model': RandomForestRegressor(random_state=42),
        'params': {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5]
        }
    },
    'GradientBoosting': {
        'model': GradientBoostingRegressor(random_state=42),
        'params': {
            'n_estimators': [50, 100],
            'learning_rate': [0.01, 0.1],
            'max_depth': [3, 5]
        }
    }
}

best_score = -np.inf
best_model = None
best_model_name = None

for name, config in models.items():
    print(f"\n   Training {name}...")
    grid_search = GridSearchCV(
        config['model'],
        config['params'],
        cv=3,
        scoring='r2',
        n_jobs=-1,
        verbose=0
    )
    grid_search.fit(X_train_scaled, y_train)
    
    score = grid_search.best_score_
    print(f"   ✓ {name} - Best CV R² Score: {score:.4f}")
    print(f"     Best params: {grid_search.best_params_}")
    
    if score > best_score:
        best_score = score
        best_model = grid_search.best_estimator_
        best_model_name = name

# 6. Evaluate the best model
print(f"\n6. Best model: {best_model_name}")
y_pred = best_model.predict(X_test_scaled)
test_r2 = r2_score(y_test, y_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"   ✓ Test R² Score: {test_r2:.4f}")
print(f"   ✓ Test RMSE: {test_rmse:.2f}")

# 7. Save the model and scaler
print("\n7. Saving model and scaler...")
joblib.dump(best_model, "best_model.pkl")
joblib.dump(scaler, "scaler.pkl")
print("   ✓ Model saved as 'best_model.pkl'")
print("   ✓ Scaler saved as 'scaler.pkl'")

# 8. Save feature names for reference
feature_names = X.columns.tolist()
joblib.dump(feature_names, "feature_names.pkl")
print(f"   ✓ Feature names saved ({len(feature_names)} features)")

print("\n" + "="*60)
print("✓ Model training completed successfully!")
print("="*60)
print(f"\nModel Performance Summary:")
print(f"  - Model Type: {best_model_name}")
print(f"  - R² Score: {test_r2:.4f}")
print(f"  - RMSE: {test_rmse:.2f}")
print(f"  - Number of features: {len(feature_names)}")
print("\nYour Flask app is now ready to make real predictions!")
