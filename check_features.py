import pandas as pd
import numpy as np

df = pd.read_csv("lamudi_features.csv")

print(f"Shape: {df.shape}")
print(f"\nAll columns:")
for col in df.columns:
    print(f"  {col}: {df[col].dtype}")

print(f"\nNull counts (should all be 0):")
print(df.isnull().sum()[df.isnull().sum() > 0])

print(f"\nCorrelation with log_price (top 10):")
numeric_df = df.select_dtypes(include=[np.number])
corr = numeric_df.corr()["log_price"].drop("log_price")
print(corr.abs().sort_values(ascending=False).head(10))