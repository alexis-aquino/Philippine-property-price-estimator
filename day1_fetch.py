import requests
import time

# This is the User-Agent header — it tells the website what "browser" is visiting.
# Without this, some sites block you immediately because they see "python-requests"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# The URL we want to fetch — Metro Manila condo listings, page 1
URL = "https://www.lamudi.com.ph/metro-manila/condominium/buy/?page=1"

def fetch_page(url):
    """
    Sends an HTTP GET request to the URL and returns the HTML.
    Returns None if the request fails.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        # status_code 200 means "OK" — the request succeeded
        # status_code 403 means "Forbidden" — site is blocking you
        # status_code 404 means "Not Found" — page doesn't exist
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            return response.text  # .text gives you the HTML as a string
        else:
            print(f"Failed to fetch page. Status: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("Request timed out — site took too long to respond")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error — check your internet")
        return None

# Run it
html = fetch_page(URL)

if html:
    # Print just the first 2000 characters so we can see the structure
    print("\n--- First 2000 characters of HTML ---\n")
    print(html[:2000])
    print(f"\n--- Total HTML length: {len(html):,} characters ---")

    # Search for the word "price" in the HTML and show surrounding context
index = html.find("price")
print(html[index-100 : index+200])

# Check if actual price values (₱) appear in the HTML at all
if "₱" in html:
    index = html.find("₱")
    print("Found ₱ symbol at index:", index)
    print(html[index-100 : index+300])
else:
    print("No ₱ symbol found in the HTML")
    
# Also check for a price pattern like digits followed by commas
import re
prices = re.findall(r'[\d,]{7,}', html)
print("\nPossible price numbers found:", prices[:10])