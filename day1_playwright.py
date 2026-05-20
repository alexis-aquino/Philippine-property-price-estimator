from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import json
import pandas as pd

BASE_URL = "https://www.lamudi.com.ph/metro-manila/condominium/buy/?page={}"

def fetch_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        html = page.content()
        browser.close()
        return html

def extract_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    listings = []

    for script in scripts:
        try:
            data        = json.loads(script.string)
            graph       = data[0]["@graph"]
            main_entity = graph[0]["mainEntity"]
            item_list   = main_entity[0]
            items       = item_list["itemListElement"]

            for item in items:
                prop = item.get("item", {})
                listing = {
                    "name":        prop.get("name"),
                    "description": prop.get("description"),
                    "bedrooms":    prop.get("numberOfBedrooms"),
                    "bathrooms":   prop.get("numberOfBathroomsTotal"),
                    "floor_area":  prop.get("floorSize", {}).get("value"),
                    "region":      prop.get("address", {}).get("addressRegion"),
                    "city":        prop.get("address", {}).get("addressLocality"),
                    "street":      prop.get("address", {}).get("streetAddress"),
                    "latitude":    prop.get("geo", {}).get("latitude"),
                    "longitude":   prop.get("geo", {}).get("longitude"),
                    "url":         prop.get("url"),
                }
                listings.append(listing)

        except Exception as e:
            print(f"  Could not parse page — {e}")
            continue

    return listings

# --- PAGINATION LOOP ---
all_listings = []
PAGES_TO_SCRAPE = 10  # 10 pages x 30 listings = ~300 rows

for page_num in range(1, PAGES_TO_SCRAPE + 1):
    url = BASE_URL.format(page_num)
    print(f"Scraping page {page_num}/{PAGES_TO_SCRAPE}...")

    html = fetch_with_playwright(url)
    listings = extract_listings(html)

    print(f"  Got {len(listings)} listings — running total: {len(all_listings) + len(listings)}")
    all_listings.extend(listings)

    # Rate limiting — be polite, wait 2 seconds between pages
    # Without this Lamudi may detect you as a bot and block your IP
    time.sleep(2)

# Save everything
df = pd.DataFrame(all_listings)
df.to_csv("lamudi_raw.csv", index=False)

print(f"\nDone!")
print(f"Total listings collected: {len(all_listings)}")
print(f"Saved to lamudi_raw.csv")
print(f"\nShape: {df.shape}")
print(f"\nNull counts:\n{df.isnull().sum()}")
print(f"\nPreview:\n{df.head()}")