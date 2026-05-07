"""
Script pour comparer Random Forest vs Gradient Boosting
et déterminer lequel est le meilleur
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

print("="*70)
print("COMPARAISON: Random Forest vs Gradient Boosting")
print("="*70)

# 1. Charger les données
print("\n1. Chargement des données...")
df = pd.read_excel('dataset_clean (1).xlsx')
df = df.drop_duplicates(subset='student_id')
print(f"   ✓ {df.shape[0]} étudiants chargés")

# 2. Préparer les features
target_col = 'lifetime_value'
if target_col not in df.columns:
    revenue_cols = [col for col in df.columns if 'payment' in col.lower() or 'revenue' in col.lower() or 'value' in col.lower()]
    if revenue_cols:
        target_col = revenue_cols[0]

y = df[target_col]

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
exclude_cols = ['student_id', target_col]
feature_cols = [col for col in numeric_cols if col not in exclude_cols]

categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
if categorical_cols:
    df_encoded = pd.get_dummies(df[categorical_cols], drop_first=True)
    X_numeric = df[feature_cols]
    X = pd.concat([X_numeric, df_encoded], axis=1)
else:
    X = df[feature_cols]

print(f"   ✓ {X.shape[1]} features préparées")

# 3. Split et normalisation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"   ✓ Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# 4. Tester Random Forest avec les meilleurs paramètres trouvés
print("\n2. Test Random Forest (paramètres optimaux)...")
rf_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
rf_pred = rf_model.predict(X_test_scaled)
rf_r2 = r2_score(y_test, rf_pred)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))

# Validation croisée
rf_cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=3, scoring='r2', n_jobs=-1)
rf_cv_mean = rf_cv_scores.mean()

print(f"   ✓ R² Test: {rf_r2:.4f}")
print(f"   ✓ RMSE Test: {rf_rmse:.2f}")
print(f"   ✓ R² CV (3-fold): {rf_cv_mean:.4f} (±{rf_cv_scores.std():.4f})")

# 5. Tester Gradient Boosting avec différents paramètres
print("\n3. Test Gradient Boosting (paramètres optimaux)...")
gb_model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)
gb_pred = gb_model.predict(X_test_scaled)
gb_r2 = r2_score(y_test, gb_pred)
gb_rmse = np.sqrt(mean_squared_error(y_test, gb_pred))

# Validation croisée
gb_cv_scores = cross_val_score(gb_model, X_train_scaled, y_train, cv=3, scoring='r2', n_jobs=-1)
gb_cv_mean = gb_cv_scores.mean()

print(f"   ✓ R² Test: {gb_r2:.4f}")
print(f"   ✓ RMSE Test: {gb_rmse:.2f}")
print(f"   ✓ R² CV (3-fold): {gb_cv_mean:.4f} (±{gb_cv_scores.std():.4f})")

# 6. Comparaison
print("\n" + "="*70)
print("COMPARAISON FINALE")
print("="*70)

print("\n📊 Scores de validation croisée (critère de sélection):")
print(f"   Random Forest:      {rf_cv_mean:.4f}")
print(f"   Gradient Boosting:  {gb_cv_mean:.4f}")

print("\n📊 Scores sur le test set:")
print(f"   Random Forest:      R²={rf_r2:.4f}, RMSE={rf_rmse:.2f}")
print(f"   Gradient Boosting:  R²={gb_r2:.4f}, RMSE={gb_rmse:.2f}")

# Déterminer le gagnant
if rf_cv_mean > gb_cv_mean:
    winner = "Random Forest"
    diff = rf_cv_mean - gb_cv_mean
    print(f"\n🏆 GAGNANT: Random Forest")
    print(f"   Différence: +{diff:.4f} en validation croisée")
else:
    winner = "Gradient Boosting"
    diff = gb_cv_mean - rf_cv_mean
    print(f"\n🏆 GAGNANT: Gradient Boosting")
    print(f"   Différence: +{diff:.4f} en validation croisée")

# Vérifier le modèle déployé
print("\n" + "="*70)
print("MODÈLE ACTUELLEMENT DÉPLOYÉ")
print("="*70)
deployed_model = joblib.load("best_model.pkl")
deployed_type = type(deployed_model).__name__
print(f"Type: {deployed_type}")

if deployed_type == "RandomForestRegressor" and winner == "Random Forest":
    print("✅ Le bon modèle est déployé!")
elif deployed_type == "GradientBoostingRegressor" and winner == "Gradient Boosting":
    print("✅ Le bon modèle est déployé!")
else:
    print(f"⚠️  ATTENTION: Le modèle déployé ({deployed_type}) ne correspond pas au gagnant ({winner})")
    print(f"   Recommandation: Réentraîner avec train_model.py pour déployer le meilleur modèle")

print("="*70)
