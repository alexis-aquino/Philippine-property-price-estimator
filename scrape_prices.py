from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

df = pd.read_csv("lamudi_listings_large.csv")

def get_listing_price(url, page):
    """
    Visits one listing page and extracts the price from
    the prices-and-fees__price div.
    Returns a float in pesos or None if no price found.
    
    Note: we pass the Playwright 'page' object in instead of
    creating a new browser for every listing — much faster.
    """
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the price div we identified
        price_div = soup.find("div", class_="prices-and-fees__price")
        
        if price_div:
            raw_text = price_div.get_text(strip=True)
            # raw_text looks like "₱ 66,349,585" — clean it
            # Remove ₱, spaces, commas then convert to float
            cleaned = re.sub(r'[₱,\s]', '', raw_text)
            if cleaned:
                return float(cleaned)
        
        return None
        
    except Exception as e:
        print(f"  Error on {url}: {e}")
        return None

def scrape_all_prices(df):
    prices = []
    
    # Open ONE browser for all listings — reuse it across requests
    # This is much faster than opening/closing a browser per listing
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        total = len(df)
        
        for i, row in df.iterrows():
            url = row["url"]
            print(f"  [{i+1}/{total}] Scraping: {row['name']} — {row['city']}")
            
            price = get_listing_price(url, page)
            prices.append(price)
            
            if price:
                print(f"    ✓ Price: ₱{price:,.0f}")
            else:
                print(f"    ✗ No price found")
            
            # Save progress every 50 listings
            # If script crashes, you won't lose everything
            if (i + 1) % 50 == 0:
                df_temp = df.copy()
                df_temp["price"] = prices + [None] * (total - len(prices))
                df_temp.to_csv("lamudi_with_price_progress.csv", index=False)
                print(f"\n  --- Progress saved at listing {i+1} ---\n")
            
            # Rate limiting — 2 seconds between requests
            time.sleep(2)
        
        browser.close()
    
    return prices

print("Starting price scraper...")
print(f"Total listings to scrape: {len(df)}\n")

prices = scrape_all_prices(df)
df["price"] = prices

# Final save
df.to_csv("lamudi_large_with_price.csv", index=False)

# Summary
extracted = df["price"].notna().sum()
missing   = df["price"].isna().sum()
total     = len(df)

print(f"\n=== DONE ===")
print(f"Total listings:   {total}")
print(f"Prices found:     {extracted} ({extracted/total*100:.1f}%)")
print(f"Prices missing:   {missing} ({missing/total*100:.1f}%)")
print(f"\nPrice stats:")
print(df["price"].describe().apply(lambda x: f"₱{x:,.2f}"))
print(f"\nSaved to lamudi_with_price.csv")