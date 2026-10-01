"""
Train XGBoost model for Philippine property price prediction.
Saves the model and preprocessing info for Streamlit app to use.
"""

import pandas as pd
import numpy as np
import pickle
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

print("=" * 60)
print("Training XGBoost Model for Philippine Property Prices")
print("=" * 60)

# Load featured data
df = pd.read_csv("lamudi_features.csv")
print(f"\nDataset shape: {df.shape}")

# Select features for modeling
feature_cols = [
    'bedrooms', 'bathrooms', 'floor_area', 'price_per_sqm',
    'dist_to_bgc', 'dist_to_makati', 'dist_to_ortigas', 'dist_to_nearest_cbd',
    'city_median_price', 'city_median_price_per_sqm', 'city_listing_count',
    'has_pool', 'has_gym', 'has_parking', 'has_balcony'
]

# Add one-hot encoded city columns
city_cols = [col for col in df.columns if col.startswith('city_')]
feature_cols.extend(city_cols)

X = df[feature_cols].copy()
y = df['log_price'].copy()  # Target is log-transformed price

print(f"\nFeatures: {len(feature_cols)}")
print(f"Target variable: log_price")
print(f"Missing values in X: {X.isnull().sum().sum()}")

# Handle any remaining missing values
X = X.fillna(X.median(numeric_only=True))

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTrain set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# Train Gradient Boosting model
print("\nTraining Gradient Boosting model...")
model = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    random_state=42,
    verbose=0
)

model.fit(X_train, y_train)

# Evaluate
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)
print(f"\nTraining Set:")
print(f"  MAE:  ₱{np.expm1(train_mae):,.0f}")
print(f"  RMSE: {train_rmse:.4f} (log scale)")
print(f"  R²:   {train_r2:.4f}")

print(f"\nTest Set:")
print(f"  MAE:  ₱{np.expm1(test_mae):,.0f}")
print(f"  RMSE: {test_rmse:.4f} (log scale)")
print(f"  R²:   {test_r2:.4f}")

# Feature importance
print("\n" + "=" * 60)
print("TOP 10 MOST IMPORTANT FEATURES")
print("=" * 60)
importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in importance_df.head(10).iterrows():
    print(f"{row['feature']:30s} {row['importance']:.4f}")

# Save model and metadata
metadata = {
    'feature_cols': feature_cols,
    'city_cols': city_cols,
    'model_name': 'Gradient Boosting',
    'train_r2': train_r2,
    'test_r2': test_r2,
    'test_mae': test_mae,
    'test_rmse': test_rmse
}

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)

print("\n✅ Model saved to model.pkl")
print("✅ Metadata saved to metadata.pkl")
print("\nReady for Streamlit app!")
