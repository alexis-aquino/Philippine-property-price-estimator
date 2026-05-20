import pandas as pd
import re

df = pd.read_csv("lamudi_raw.csv")

def extract_price(description):
    """
    Extracts the first price mentioned in a listing description.
    Returns a float in pesos or None if no price found.
    """
    if not isinstance(description, str):
        return None

    # Normalize: remove newlines and extra spaces first
    # This makes patterns easier to match
    description = " ".join(description.split())

    # Pattern 1: Shorthand millions with peso sign — ₱28M or ₱ 28.5M
    match = re.search(r'₱\s*(\d+(?:\.\d+)?)\s*[Mm]', description)
    if match:
        return float(match.group(1)) * 1_000_000

    # Pattern 2: Shorthand millions with Php — Php 28M or PHP 28.5M
    match = re.search(r'[Pp][Hh][Pp]\s*(\d+(?:\.\d+)?)\s*[Mm]', description)
    if match:
        return float(match.group(1)) * 1_000_000

    # Pattern 3: Full number with peso sign — ₱ 4,252,740.06 or ₱3500000
    match = re.search(r'₱\s*([\d,]+(?:\.\d+)?)', description)
    if match:
        price_str = match.group(1).replace(",", "")
        value = float(price_str)
        # Sanity check: condo prices should be between 500k and 500M
        if 500_000 <= value <= 500_000_000:
            return value

    # Pattern 4: Php prefix — Php 6,900,000 or PHP 3500000
    match = re.search(r'[Pp][Hh][Pp]\s*([\d,]+(?:\.\d+)?)', description)
    if match:
        price_str = match.group(1).replace(",", "")
        value = float(price_str)
        if 500_000 <= value <= 500_000_000:
            return value

    return None

# Apply extraction
df["price"] = df["description"].apply(extract_price)

# --- STATS ---
total     = len(df)
extracted = df["price"].notna().sum()
missing   = df["price"].isna().sum()

print(f"Total listings:    {total}")
print(f"Prices extracted:  {extracted} ({extracted/total*100:.1f}%)")
print(f"Prices missing:    {missing} ({missing/total*100:.1f}%)")

# --- SANITY CHECK: suspicious prices ---
print(f"\n--- Suspiciously low prices (under ₱500,000) ---")
low = df[df["price"] < 500_000][["name", "city", "price", "description"]]
for _, row in low.iterrows():
    print(f"  {row['name']} | {row['city']} | ₱{row['price']:,.0f}")
    print(f"  Description: {row['description'][:200]}\n")

print(f"\n--- Suspiciously high prices (over ₱200,000,000) ---")
high = df[df["price"] > 200_000_000][["name", "city", "price"]]
print(high.to_string())

# --- PRICE DISTRIBUTION ---
print(f"\n--- Price stats (extracted listings only) ---")
print(df["price"].describe().apply(lambda x: f"₱{x:,.0f}"))

# --- SAVE ---
df.to_csv("lamudi_with_price.csv", index=False)
print(f"\nSaved to lamudi_with_price.csv")
print(f"Columns: {df.columns.tolist()}")