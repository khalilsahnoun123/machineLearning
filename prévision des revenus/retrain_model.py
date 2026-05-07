"""
Réentraînement du modèle de prévision des revenus
avec UNIQUEMENT les colonnes qui existent dans le dataset
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

print("="*70)
print("RÉENTRAÎNEMENT DU MODÈLE DE PRÉVISION DES REVENUS")
print("="*70)

# 1. Charger le dataset
print("\n1. Chargement du dataset...")
df = pd.read_excel('dataset_clean (1).xlsx')
df = df.drop_duplicates(subset='student_id')
print(f"   ✓ {df.shape[0]} étudiants chargés")
print(f"   ✓ {df.shape[1]} colonnes disponibles")

# 2. Afficher les colonnes disponibles
print("\n2. Colonnes disponibles dans le dataset:")
print(f"   {list(df.columns)}")

# 3. Préparer les features et la target
print("\n3. Préparation des features...")

# Target: lifetime_value
target_col = 'lifetime_value'
y = df[target_col]

# Features numériques (exclure student_id et lifetime_value)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_features = [col for col in numeric_cols if col not in ['student_id', target_col]]

print(f"   ✓ Features numériques: {numeric_features}")

# Features catégorielles
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
print(f"   ✓ Features catégorielles: {categorical_cols}")

# Créer X avec features numériques
X_numeric = df[numeric_features]

# One-hot encode des features catégorielles
if categorical_cols:
    df_categorical = df[categorical_cols]
    df_encoded = pd.get_dummies(df_categorical, drop_first=True)
    X = pd.concat([X_numeric, df_encoded], axis=1)
else:
    X = X_numeric

print(f"   ✓ Total features après encodage: {X.shape[1]}")
print(f"   ✓ Liste des features: {list(X.columns)}")

# 4. Split train/test
print("\n4. Split train/test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   ✓ Train: {X_train.shape[0]} samples")
print(f"   ✓ Test: {X_test.shape[0]} samples")

# 5. Normalisation
print("\n5. Normalisation des features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("   ✓ Normalisation terminée")

# 6. Entraînement avec GridSearchCV
print("\n6. Entraînement des modèles (cela peut prendre quelques minutes)...")

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
    print(f"\n   Entraînement de {name}...")
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
    print(f"   ✓ {name} - Meilleur score CV R²: {score:.4f}")
    print(f"     Meilleurs paramètres: {grid_search.best_params_}")
    
    if score > best_score:
        best_score = score
        best_model = grid_search.best_estimator_
        best_model_name = name

# 7. Évaluation du meilleur modèle
print(f"\n7. Meilleur modèle: {best_model_name}")
y_pred = best_model.predict(X_test_scaled)
test_r2 = r2_score(y_test, y_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"   ✓ R² Score (test): {test_r2:.4f}")
print(f"   ✓ RMSE (test): {test_rmse:.2f} $")

# 8. Sauvegarder le modèle, scaler et feature names
print("\n8. Sauvegarde du modèle...")
joblib.dump(best_model, "best_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(list(X.columns), "feature_names.pkl")

print("   ✓ Modèle sauvegardé: best_model.pkl")
print("   ✓ Scaler sauvegardé: scaler.pkl")
print("   ✓ Features sauvegardées: feature_names.pkl")

# 9. Résumé
print("\n" + "="*70)
print("✅ RÉENTRAÎNEMENT TERMINÉ AVEC SUCCÈS!")
print("="*70)
print(f"\nRésumé:")
print(f"  - Modèle: {best_model_name}")
print(f"  - R² Score: {test_r2:.4f}")
print(f"  - RMSE: {test_rmse:.2f} $")
print(f"  - Nombre de features: {X.shape[1]}")
print(f"\nFeatures utilisées:")
for i, feat in enumerate(X.columns, 1):
    print(f"  {i}. {feat}")

print("\n✅ Le modèle est prêt à être utilisé par l'API Flask!")
print("="*70)
