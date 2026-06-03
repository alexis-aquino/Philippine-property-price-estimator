import pandas as pd
import numpy as np
from geopy.distance import geodesic

df = pd.read_csv("lamudi_modeling_ready.csv")

print(f"Starting shape: {df.shape}")

# ============================================================
# FEATURE 1: log_price
# Your model will predict this instead of raw price
# log1p(x) = log(x + 1) — handles zero values safely
# expm1(x) converts back: np.expm1(log_price) = original price
# ============================================================
df["log_price"] = np.log1p(df["price"])
print("✓ Created log_price")

# ============================================================
# FEATURE 2: Distance to key business districts
# Properties closer to BGC and Makati CBD command higher prices
# geodesic measures real curved-earth distance in kilometers
# ============================================================

# Coordinates of key Metro Manila landmarks
BGC_CENTER     = (14.5547, 121.0486)   # Bonifacio Global City
MAKATI_CBD     = (14.5547, 121.0244)   # Ayala Avenue, Makati
ORTIGAS_CENTER = (14.5875, 121.0603)   # Ortigas Center, Pasig
EDSA_CENTER    = (14.6091, 121.0223)   # EDSA-Quezon Ave intersection

def calc_distance(lat, lon, landmark):
    """
    Calculates distance in km between a listing and a landmark.
    geodesic accounts for the curvature of the earth —
    more accurate than straight-line Euclidean distance.
    Returns None if coordinates are missing.
    """
    try:
        return geodesic((lat, lon), landmark).km
    except Exception:
        return None

print("Calculating distances to landmarks...")

df["dist_to_bgc"] = df.apply(
    lambda row: calc_distance(row["latitude"], row["longitude"], BGC_CENTER),
    axis=1
)

df["dist_to_makati"] = df.apply(
    lambda row: calc_distance(row["latitude"], row["longitude"], MAKATI_CBD),
    axis=1
)

df["dist_to_ortigas"] = df.apply(
    lambda row: calc_distance(row["latitude"], row["longitude"], ORTIGAS_CENTER),
    axis=1
)

# Distance to nearest CBD — the minimum of all three distances
# This captures "how close is this unit to ANY major business hub"
df["dist_to_nearest_cbd"] = df[
    ["dist_to_bgc", "dist_to_makati", "dist_to_ortigas"]
].min(axis=1)

print("✓ Created distance features")

# ============================================================
# FEATURE 3: City-level aggregate features
# These tell the model the typical price level in each city
# transform('median') pastes the group median onto every row
# ============================================================

df["city_median_price"] = df.groupby("city")["price"].transform("median")
df["city_median_price_per_sqm"] = df.groupby("city")["price_per_sqm"].transform("median")
df["city_listing_count"] = df.groupby("city")["price"].transform("count")

print("✓ Created city aggregate features")

# ============================================================
# FEATURE 4: Size category
# Buckets floor area into meaningful groups
# pd.cut divides a continuous variable into labeled bins
# ============================================================
df["size_category"] = pd.cut(
    df["floor_area"],
    bins=[0, 30, 50, 80, 120, 500],
    labels=["micro", "small", "medium", "large", "luxury"]
)

print("✓ Created size_category")

# ============================================================
# FEATURE 5: Amenity flags from description text
# Simple keyword search — does the description mention these?
# ============================================================
amenities = {
    "has_pool":    ["pool", "swimming"],
    "has_gym":     ["gym", "fitness"],
    "has_parking": ["parking", "car park", "carpark"],
    "has_balcony": ["balcony", "terrace"],
}

for feature, keywords in amenities.items():
    df[feature] = df["description"].str.lower().apply(
        lambda text: int(any(kw in str(text) for kw in keywords))
    )

print("✓ Created amenity features")

# ============================================================
# FEATURE 6: One-hot encode city
# Converts "Makati", "Taguig" etc into binary columns
# so the model can understand location numerically
# ============================================================
df = pd.get_dummies(df, columns=["city"], prefix="city", drop_first=False)
print("✓ One-hot encoded city")

# ============================================================
# SUMMARYimport pandas as pd
import numpy as np
from geopy.distance import geodesic

df = pd.read_csv("lamudi_modeling_ready.csv")

print(f"Starting shape: {df.shape}")

# ============================================================
# FEATURE 1: log_price
# Your model will predict this instead of raw price
# log1p(x) = log(x + 1) — handles zero values safely
# expm1(x) converts back: np.expm1(log_price) = original price
# ============================================================
df["log_price"] = np.log1p(df["price"])
print("✓ Created log_price")

# ============================================================
# FEATURE 2: Distance to key business districts
# Properties closer to BGC and Makati CBD command higher prices
# geodesic measures real curved-earth distance in kilometers
# ============================================================

# Coordinates of key Metro Manila landmarks
BGC_CENTER     = (14.5547, 121.0486)   # Bonifacio Global City
MAKATI_CBD     = (14.5547, 121.0244)   # Ayala Avenue, Makati
ORTIGAS_CENTER = (14.5875, 121.0603)   # Ortigas Center, Pasig
EDSA_CENTER    = (14.6091, 121.0223)   # EDSA-Quezon Ave intersection

def calc_distance(lat, lon, landmark):
    """
    Calculates distance in km between a listing and a landmark.
    geodesic accounts for the curvature of the earth —
    more accurate than straight-line Euclidean distance.
    Returns None if coordinates are missing.
    """
    try:
        return geodesic((lat, lon), landmark).km
    except Exception:
        return None

print("Calculating distances to landmarks...")

df["dist_to_bgc"] = df.apply(
    lambda row: calc_distance(row["latitude"], row["longitude"], BGC_CENTER),
    axis=1
)

df["dist_to_makati"] = df.apply(
    lambda row: calc_distance(row["latitude"], row["longitude"], MAKATI_CBD),
    axis=1
)

df["dist_to_ortigas"] = df.apply(
    lambda row: calc_distance(row["latitude"], row["longitude"], ORTIGAS_CENTER),
    axis=1
)

# Distance to nearest CBD — the minimum of all three distances
# This captures "how close is this unit to ANY major business hub"
df["dist_to_nearest_cbd"] = df[
    ["dist_to_bgc", "dist_to_makati", "dist_to_ortigas"]
].min(axis=1)

print("✓ Created distance features")

# ============================================================
# FEATURE 3: City-level aggregate features
# These tell the model the typical price level in each city
# transform('median') pastes the group median onto every row
# ============================================================

df["city_median_price"] = df.groupby("city")["price"].transform("median")
df["city_median_price_per_sqm"] = df.groupby("city")["price_per_sqm"].transform("median")
df["city_listing_count"] = df.groupby("city")["price"].transform("count")

print("✓ Created city aggregate features")

# ============================================================
# FEATURE 4: Size category
# Buckets floor area into meaningful groups
# pd.cut divides a continuous variable into labeled bins
# ============================================================
df["size_category"] = pd.cut(
    df["floor_area"],
    bins=[0, 30, 50, 80, 120, 500],
    labels=["micro", "small", "medium", "large", "luxury"]
)

print("✓ Created size_category")

# ============================================================
# FEATURE 5: Amenity flags from description text
# Simple keyword search — does the description mention these?
# ============================================================
amenities = {
    "has_pool":    ["pool", "swimming"],
    "has_gym":     ["gym", "fitness"],
    "has_parking": ["parking", "car park", "carpark"],
    "has_balcony": ["balcony", "terrace"],
}

for feature, keywords in amenities.items():
    df[feature] = df["description"].str.lower().apply(
        lambda text: int(any(kw in str(text) for kw in keywords))
    )

print("✓ Created amenity features")

# ============================================================
# FEATURE 6: One-hot encode city
# Converts "Makati", "Taguig" etc into binary columns
# so the model can understand location numerically
# ============================================================
df = pd.get_dummies(df, columns=["city"], prefix="city", drop_first=False)
print("✓ One-hot encoded city")

# ============================================================
# SUMMARY
# ============================================================
print(f"\nFinal shape: {df.shape}")
print(f"\nNew features created:")
new_features = [
    "log_price", "dist_to_bgc", "dist_to_makati",
    "dist_to_ortigas", "dist_to_nearest_cbd",
    "city_median_price", "city_median_price_per_sqm",
    "city_listing_count", "size_category",
    "has_pool", "has_gym", "has_parking", "has_balcony"
]
for f in new_features:
    print(f"  {f}: {df[f].dtype} — sample: {df[f].iloc[0]}")

print(f"\nDistance stats:")
print(df[["dist_to_bgc", "dist_to_makati", "dist_to_nearest_cbd"]].describe().round(2))

print(f"\nAmenity counts:")
for f in ["has_pool", "has_gym", "has_parking", "has_balcony"]:
    count = df[f].sum()
    pct = count / len(df) * 100
    print(f"  {f}: {count} listings ({pct:.1f}%)")

# Save
df.to_csv("lamudi_features.csv", index=False)
print(f"\nSaved to lamudi_features.csv")
# ============================================================
print(f"\nFinal shape: {df.shape}")
print(f"\nNew features created:")
new_features = [
    "log_price", "dist_to_bgc", "dist_to_makati",
    "dist_to_ortigas", "dist_to_nearest_cbd",
    "city_median_price", "city_median_price_per_sqm",
    "city_listing_count", "size_category",
    "has_pool", "has_gym", "has_parking", "has_balcony"
]
for f in new_features:
    print(f"  {f}: {df[f].dtype} — sample: {df[f].iloc[0]}")

print(f"\nDistance stats:")
print(df[["dist_to_bgc", "dist_to_makati", "dist_to_nearest_cbd"]].describe().round(2))

print(f"\nAmenity counts:")
for f in ["has_pool", "has_gym", "has_parking", "has_balcony"]:
    count = df[f].sum()
    pct = count / len(df) * 100
    print(f"  {f}: {count} listings ({pct:.1f}%)")

# Save
df.to_csv("lamudi_features.csv", index=False)
print(f"\nSaved to lamudi_features.csv")