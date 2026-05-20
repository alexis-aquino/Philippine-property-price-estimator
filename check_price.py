import pandas as pd

df = pd.read_csv("lamudi_raw.csv")

# Print the first 10 descriptions so we can see
# how prices are written across different listings
print("=== DESCRIPTION SAMPLES ===\n")
for i, desc in enumerate(df["description"].head(10)):
    # Print just the first 200 characters of each description
    print(f"Listing {i+1}:")
    print(desc[:200])
    print()