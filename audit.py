import pandas as pd

df = pd.read_csv("lamudi_with_price.csv")

print("=== DATASET OVERVIEW ===")
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nNull counts:")
print(df.isnull().sum())

print(f"\n=== PRICE DISTRIBUTION BY CITY ===")
city_stats = df.groupby("city")["price"].agg(
    count="count",
    median="median",
    min="min",
    max="max"
).sort_values("median", ascending=False)

# Format as pesos
city_stats["median"] = city_stats["median"].apply(lambda x: f"₱{x:,.0f}")
city_stats["min"]    = city_stats["min"].apply(lambda x: f"₱{x:,.0f}")
city_stats["max"]    = city_stats["max"].apply(lambda x: f"₱{x:,.0f}")
print(city_stats.to_string())

print(f"\n=== BEDROOM DISTRIBUTION ===")
print(df["bedrooms"].value_counts().sort_index())

print(f"\n=== FLOOR AREA STATS ===")
df["floor_area"] = pd.to_numeric(df["floor_area"], errors="coerce")
print(df["floor_area"].describe().apply(lambda x: f"{x:.1f} sqm"))

print(f"\n=== SAMPLE COMPLETE ROWS ===")
complete = df.dropna(subset=["price", "bedrooms", "floor_area", "city"])
print(f"Rows with all key fields filled: {len(complete)}")
print(complete[["name", "city", "bedrooms", "floor_area", "price"]].head(10).to_string())