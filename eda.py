import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load your clean dataset
df = pd.read_csv("lamudi_modeling_ready.csv")

print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Set a clean visual style for all charts
# This makes every chart look professional without extra formatting
sns.set_theme(style="whitegrid", palette="muted")

# ============================================================
# CHART 1: Raw price distribution
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left chart — raw prices
# A histogram shows how many listings fall in each price range
axes[0].hist(df["price"], bins=50, color="#4C72B0", edgecolor="white")
axes[0].set_title("Price distribution (raw)")
axes[0].set_xlabel("Price (₱)")
axes[0].set_ylabel("Number of listings")
# Format x-axis as millions for readability
axes[0].xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: f"₱{x/1e6:.0f}M")
)

# Right chart — log-transformed prices
# Log transformation converts a skewed distribution into a normal one
# This is what your model will actually predict
df["log_price"] = np.log1p(df["price"])
axes[1].hist(df["log_price"], bins=50, color="#DD8452", edgecolor="white")
axes[1].set_title("Price distribution (log-transformed)")
axes[1].set_xlabel("log(Price)")
axes[1].set_ylabel("Number of listings")

plt.tight_layout()
plt.savefig("chart_price_distribution.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: chart_price_distribution.png")

# ============================================================
# CHART 2: Median price by city
# ============================================================
city_median = (
    df.groupby("city")["price"]
    .median()
    .sort_values(ascending=True)
)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(city_median.index, city_median.values, color="#4C72B0")
ax.set_title("Median condo price by city")
ax.set_xlabel("Median price (₱)")
ax.xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: f"₱{x/1e6:.0f}M")
)

# Add value labels on each bar
for bar, val in zip(bars, city_median.values):
    ax.text(
        val + 500000, bar.get_y() + bar.get_height()/2,
        f"₱{val/1e6:.1f}M",
        va="center", fontsize=9
    )

plt.tight_layout()
plt.savefig("chart_price_by_city.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: chart_price_by_city.png")

# ============================================================
# CHART 3: Price vs floor area scatter plot
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))

# Color each dot by city so you can see location patterns
cities = df["city"].unique()
colors = sns.color_palette("tab10", len(cities))
city_color = dict(zip(cities, colors))

for city in cities:
    subset = df[df["city"] == city]
    ax.scatter(
        subset["floor_area"],
        subset["price"],
        label=city,
        alpha=0.5,
        s=20,
        color=city_color[city]
    )

ax.set_title("Price vs floor area by city")
ax.set_xlabel("Floor area (sqm)")
ax.set_ylabel("Price (₱)")
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: f"₱{x/1e6:.0f}M")
)
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

plt.tight_layout()
plt.savefig("chart_price_vs_area.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: chart_price_vs_area.png")

# ============================================================
# CHART 4: Correlation heatmap
# ============================================================
# A heatmap shows how strongly each pair of numeric features
# correlates with each other
# Values close to 1.0 = strong positive correlation
# Values close to -1.0 = strong negative correlation
# Values close to 0 = no relationship

numeric_cols = ["price", "floor_area", "bedrooms", "bathrooms",
                "price_per_sqm", "latitude", "longitude"]

corr = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(
    corr,
    annot=True,        # Show correlation values in each cell
    fmt=".2f",         # Round to 2 decimal places
    cmap="coolwarm",   # Blue = negative, red = positive
    center=0,
    square=True,
    ax=ax
)
ax.set_title("Feature correlation heatmap")

plt.tight_layout()
plt.savefig("chart_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: chart_correlation_heatmap.png")

# ============================================================
# CHART 5: Price distribution by number of bedrooms
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))

sns.boxplot(
    data=df,
    x="bedrooms",
    y="price",
    palette="muted",
    ax=ax
)
ax.set_title("Price distribution by number of bedrooms")
ax.set_xlabel("Number of bedrooms")
ax.set_ylabel("Price (₱)")
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: f"₱{x/1e6:.0f}M")
)

plt.tight_layout()
plt.savefig("chart_price_by_bedrooms.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: chart_price_by_bedrooms.png")

print("\nAll charts saved.")
print(f"\nKey stats:")
print(f"Strongest correlator with price: {corr['price'].drop('price').abs().idxmax()}")
print(f"Correlation value: {corr['price'].drop('price').abs().max():.3f}")