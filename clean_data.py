import pandas as pd
import numpy as np

df = pd.read_csv("lamudi_large_with_price.csv")

print("=== RAW DATASET ===")
print(f"Shape: {df.shape}")
print(f"Price nulls: {df['price'].isna().sum()}")

# --- STEP 1: Convert price to numeric ---
# It's currently stored as a string because of the ₱ formatting
# pd.to_numeric with errors='coerce' converts what it can,
# and turns anything it can't convert into NaN instead of crashing
df["price"] = pd.to_numeric(df["price"], errors="coerce")
print(f"\nAfter numeric conversion — nulls: {df['price'].isna().sum()}")

# --- STEP 2: Visualize the problem ---
print("\n=== PRICE DISTRIBUTION BEFORE CLEANING ===")
print(df["price"].describe().apply(lambda x: f"₱{x:,.0f}"))

# Show the most extreme values so we understand what we're dealing with
print("\n--- 10 cheapest listings ---")
cheap = df.nsmallest(10, "price")[["name", "city", "floor_area", "price"]]
print(cheap.to_string())

print("\n--- 10 most expensive listings ---")
expensive = df.nlargest(10, "price")[["name", "city", "floor_area", "price"]]
print(expensive.to_string())

# --- STEP 3: Apply realistic price bounds ---
# For Metro Manila condos:
# Minimum realistic price: ₱1,500,000 (very small studio in outer area)
# Maximum realistic price: ₱200,000,000 (ultra-luxury penthouse)
# Anything outside this range is a data error — wrong field scraped,
# entire building listed, or community fee accidentally captured

PRICE_MIN = 1_500_000    # ₱1.5M
PRICE_MAX = 200_000_000  # ₱200M

before = len(df)
df_clean = df[
    (df["price"] >= PRICE_MIN) &
    (df["price"] <= PRICE_MAX)
].copy()
after = len(df_clean)

print(f"\n=== AFTER PRICE BOUNDS FILTER ===")
print(f"Rows before: {before}")
print(f"Rows removed: {before - after}")
print(f"Rows remaining: {after}")
print(f"\nCleaned price stats:")
print(df_clean["price"].describe().apply(lambda x: f"₱{x:,.0f}"))

# --- STEP 4: Clean floor_area ---
# Convert to numeric first
df_clean["floor_area"] = pd.to_numeric(df_clean["floor_area"], errors="coerce")

print(f"\n=== FLOOR AREA BEFORE CLEANING ===")
print(df_clean["floor_area"].describe().apply(lambda x: f"{x:.1f} sqm"))

# Show suspicious floor areas
print("\n--- Listings with floor_area > 500 sqm ---")
big = df_clean[df_clean["floor_area"] > 500][["name", "city", "floor_area", "price"]]
print(big.to_string())

print("\n--- Listings with floor_area < 15 sqm ---")
small = df_clean[df_clean["floor_area"] < 15][["name", "city", "floor_area", "price"]]
print(small.to_string())

# Apply floor area bounds
# Minimum: 15 sqm (micro studio)
# Maximum: 500 sqm (large penthouse)
AREA_MIN = 15
AREA_MAX = 500

before = len(df_clean)
df_clean = df_clean[
    (df_clean["floor_area"] >= AREA_MIN) &
    (df_clean["floor_area"] <= AREA_MAX)
].copy()
after = len(df_clean)

print(f"\n=== AFTER FLOOR AREA BOUNDS FILTER ===")
print(f"Rows removed: {before - after}")
print(f"Rows remaining: {after}")
print(f"Floor area stats:")
print(df_clean["floor_area"].describe().apply(lambda x: f"{x:.1f} sqm"))

# --- STEP 5: Clean bedroom outliers ---
print(f"\n=== BEDROOM VALUES ===")
print(df_clean["bedrooms"].value_counts().sort_index())

# Remove impossible bedroom counts
# A condo unit realistically has 0 (studio) to 5 bedrooms
df_clean = df_clean[
    df_clean["bedrooms"].isna() |
    (df_clean["bedrooms"] <= 5)
].copy()

print(f"\nAfter bedroom cleaning: {len(df_clean)} rows")
print(df_clean["bedrooms"].value_counts().sort_index())

# --- STEP 6: Save clean dataset ---
df_clean.to_csv("lamudi_large_clean.csv", index=False)

print(f"\n=== FINAL CLEAN DATASET ===")
print(f"Shape: {df_clean.shape}")
print(f"Null counts:")
print(df_clean.isnull().sum())
print(f"\nSaved to lamudi_clean.csv")