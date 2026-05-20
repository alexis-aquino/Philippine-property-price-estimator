from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import json
import pandas as pd

df = pd.read_csv("lamudi_raw.csv")

# Listing index 3 — Fort Bonifacio, we know this one has a price
test_url = df["url"].iloc[3]
print(f"Testing URL: {test_url}")

def fetch_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # domcontentloaded is faster than networkidle
        # It fires as soon as the HTML is parsed, without waiting
        # for every image and ad to finish loading
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Give JavaScript extra time to inject the listing data
        time.sleep(5)

        html = page.content()
        browser.close()
        return html

def inspect_listing_page(html):
    soup = BeautifulSoup(html, "html.parser")

    # Check JSON-LD blocks
    scripts = soup.find_all("script", type="application/ld+json")
    print(f"\nFound {len(scripts)} JSON-LD blocks on listing page")

    for i, script in enumerate(scripts):
        try:
            data = json.loads(script.string)

            if isinstance(data, list):
                data = data[0]

            # Dig into @graph if present
            if "@graph" in data:
                graph = data["@graph"]
                print(f"@graph has {len(graph)} items")
                for j, item in enumerate(graph):
                    if isinstance(item, dict):
                        print(f"\n  @graph[{j}] @type: {item.get('@type')}")
                        print(f"  keys: {list(item.keys())}")
                        # Print full item if it looks like a property
                        if item.get("@type") in [
                            "Accommodation", "RealEstateListing",
                            "Product", "Offer", "House"
                        ]:
                            print(json.dumps(item, indent=2)[:2000])

        except Exception as e:
            print(f"Script {i+1}: could not parse — {e}")

    # Search HTML elements for ₱
    print("\n--- Elements containing ₱ ---")
    price_elements = soup.find_all(
        lambda tag: tag.string and "₱" in tag.string
    )
    print(f"Total elements with ₱: {len(price_elements)}")
    for el in price_elements[:10]:
        print(f"  Tag: {el.name} | Class: {el.get('class')} | Text: {el.string.strip()[:100]}")

    # Search raw page text for ₱
    full_text = soup.get_text()
    if "₱" in full_text:
        idx = full_text.find("₱")
        print(f"\nFirst ₱ in full page text:")
        print(full_text[idx-100:idx+300])

html = fetch_with_playwright(test_url)
inspect_listing_page(html)