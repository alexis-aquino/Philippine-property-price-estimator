import pandas as pd
import numpy as np

df = pd.read_csv("lamudi_large_clean.csv")

print("=== BEFORE IMPUTATION ===")
print(f"Shape: {df.shape}")
print(f"Nulls:\n{df.isnull().sum()}\n")

# --- STEP 1: Fill missing bedrooms ---
# Strategy: fill with the median bedrooms for that city
# Concept: "Group imputation" — use the group's typical value
# instead of the overall median, which is more accurate

df["bedrooms"] = df.groupby("city")["bedrooms"].transform(
    lambda x: x.fillna(x.median())
)

# If still null (city had no bedroom data at all), fill with overall median
df["bedrooms"] = df["bedrooms"].fillna(df["bedrooms"].median())
df["bedrooms"] = df["bedrooms"].round().astype(int)

print(f"Bedrooms nulls after fill: {df['bedrooms'].isna().sum()}")

# --- STEP 2: Fill missing bathrooms ---
# Same strategy — group by city, fill with median
df["bathrooms"] = df.groupby("city")["bathrooms"].transform(
    lambda x: x.fillna(x.median())
)
df["bathrooms"] = df["bathrooms"].fillna(df["bathrooms"].median())
df["bathrooms"] = df["bathrooms"].round().astype(int)

print(f"Bathrooms nulls after fill: {df['bathrooms'].isna().sum()}")

# --- STEP 3: Fill missing coordinates ---
# Strategy: fill with the average lat/lon for that city
# A listing in Makati with no GPS gets Makati's center coordinates
# Not perfect but close enough for distance-based features later

df["latitude"] = df.groupby("city")["latitude"].transform(
    lambda x: x.fillna(x.mean())
)
df["longitude"] = df.groupby("city")["longitude"].transform(
    lambda x: x.fillna(x.mean())
)

# Convert to float
df["latitude"]  = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

print(f"Latitude nulls after fill: {df['latitude'].isna().sum()}")
print(f"Longitude nulls after fill: {df['longitude'].isna().sum()}")

# --- STEP 4: Standardize city names ---
# Some cities have inconsistent naming
# Strip whitespace and title case everything
df["city"] = df["city"].str.strip().str.title()
df["region"] = df["region"].str.strip().str.title()

print(f"\nUnique cities: {sorted(df['city'].unique())}")

# --- STEP 5: Add price_per_sqm ---
# This is one of the most important features for property valuation
# It normalizes price by size so you can compare fairly across listings
df["price_per_sqm"] = df["price"] / df["floor_area"]

print(f"\nPrice per sqm stats:")
print(df["price_per_sqm"].describe().apply(lambda x: f"₱{x:,.0f}"))

# --- FINAL SAVE ---
df.to_csv("lamudi_modeling_ready.csv", index=False)

print(f"\n=== AFTER IMPUTATION ===")
print(f"Shape: {df.shape}")
print(f"Nulls:\n{df.isnull().sum()}")
print(f"\nSaved to lamudi_modeling_ready.csv")
print(f"\nSample rows:")
print(df[["name", "city", "bedrooms", "floor_area", "price", "price_per_sqm"]].head(10).to_string())