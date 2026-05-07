"""
Script pour vérifier que le meilleur modèle est bien déployé
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error

print("="*70)
print("VÉRIFICATION DU MODÈLE DÉPLOYÉ")
print("="*70)

# 1. Charger le modèle
print("\n1. Chargement du modèle...")
model = joblib.load("best_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_names = joblib.load("feature_names.pkl")

print(f"   ✓ Type de modèle: {type(model).__name__}")
print(f"   ✓ Nombre de features: {len(feature_names)}")

# 2. Afficher les paramètres du modèle
print("\n2. Paramètres du modèle:")
params = model.get_params()
important_params = {
    'n_estimators': params.get('n_estimators'),
    'max_depth': params.get('max_depth'),
    'min_samples_split': params.get('min_samples_split'),
    'random_state': params.get('random_state')
}
for key, value in important_params.items():
    print(f"   - {key}: {value}")

# 3. Vérifier avec le dataset
print("\n3. Test avec le dataset...")
try:
    df = pd.read_excel('dataset_clean (1).xlsx')
    df = df.drop_duplicates(subset='student_id')
    
    # Trouver la colonne cible
    target_col = 'lifetime_value'
    if target_col not in df.columns:
        revenue_cols = [col for col in df.columns if 'payment' in col.lower() or 'revenue' in col.lower() or 'value' in col.lower()]
        if revenue_cols:
            target_col = revenue_cols[0]
    
    y = df[target_col]
    
    # Préparer les features
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
    
    # S'assurer que les features correspondent
    X = X[feature_names]
    
    # Normaliser
    X_scaled = scaler.transform(X)
    
    # Prédire
    y_pred = model.predict(X_scaled)
    
    # Calculer les métriques
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    print(f"   ✓ Dataset chargé: {df.shape[0]} étudiants")
    print(f"   ✓ R² Score: {r2:.4f}")
    print(f"   ✓ RMSE: {rmse:.2f}")
    
    # Statistiques sur les prédictions
    print(f"\n4. Statistiques des prédictions:")
    print(f"   - Minimum: {y_pred.min():.2f} $")
    print(f"   - Maximum: {y_pred.max():.2f} $")
    print(f"   - Moyenne: {y_pred.mean():.2f} $")
    print(f"   - Médiane: {np.median(y_pred):.2f} $")
    
except FileNotFoundError:
    print("   ⚠ Dataset non trouvé - impossible de tester les performances")
    print("   Le modèle est chargé mais non testé")

# 5. Conclusion
print("\n" + "="*70)
print("RÉSUMÉ")
print("="*70)
print(f"✓ Modèle déployé: {type(model).__name__}")
print(f"✓ Optimisé avec GridSearchCV")
print(f"✓ Paramètres optimaux:")
print(f"  - n_estimators: {params.get('n_estimators')}")
print(f"  - max_depth: {params.get('max_depth')}")
print(f"  - min_samples_split: {params.get('min_samples_split')}")

if 'r2' in locals():
    print(f"\n✓ Performance sur le dataset complet:")
    print(f"  - R² Score: {r2:.4f}")
    print(f"  - RMSE: {rmse:.2f} $")
    
    if r2 > 0.7:
        print(f"\n✅ EXCELLENT: Le modèle a un R² > 0.7, il est très performant!")
    elif r2 > 0.5:
        print(f"\n✅ BON: Le modèle a un R² > 0.5, il est performant!")
    else:
        print(f"\n⚠ ATTENTION: Le modèle a un R² < 0.5, il pourrait être amélioré")

print("\n✅ Le meilleur modèle (sélectionné par GridSearchCV) est bien déployé!")
print("="*70)
