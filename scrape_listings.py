from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import json
import pandas as pd

BASE_URL = "https://www.lamudi.com.ph/metro-manila/condominium/buy/?page={}"

def fetch_with_playwright(url, page):
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    return page.content()

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

# --- SCRAPE 50 PAGES ---
all_listings = []
PAGES_TO_SCRAPE = 50
seen_urls = set()  # Track URLs to avoid duplicates

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for page_num in range(1, PAGES_TO_SCRAPE + 1):
        url = BASE_URL.format(page_num)
        print(f"Scraping page {page_num}/{PAGES_TO_SCRAPE}...")

        try:
            html = fetch_with_playwright(url, page)
            listings = extract_listings(html)

            # Deduplicate — skip listings we've already seen
            new_listings = []
            for listing in listings:
                if listing["url"] not in seen_urls:
                    seen_urls.add(listing["url"])
                    new_listings.append(listing)

            all_listings.extend(new_listings)
            print(f"  Got {len(new_listings)} new listings — total: {len(all_listings)}")

            # Save progress every 10 pages
            if page_num % 10 == 0:
                df_temp = pd.DataFrame(all_listings)
                df_temp.to_csv("lamudi_listings_progress.csv", index=False)
                print(f"  --- Progress saved at page {page_num} ---")

        except Exception as e:
            print(f"  Page {page_num} failed — {e}")
            continue

        time.sleep(2)

    browser.close()

# Final save
df = pd.DataFrame(all_listings)
df.drop_duplicates(subset=["url"], inplace=True)
df.to_csv("lamudi_listings_large.csv", index=False)

print(f"\nDone!")
print(f"Total unique listings: {len(df)}")
print(f"Saved to lamudi_listings_large.csv")