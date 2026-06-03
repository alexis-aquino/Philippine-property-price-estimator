# Philippine Property Price Predictor

A machine learning project that predicts condo prices in Metro Manila
using data scraped from Lamudi.com.ph.

## Project Status
🔄 In Progress — Currently on Phase 2 (Data Cleaning)

## Dataset
- 1,380 cleaned condo listings from Metro Manila
- Scraped from Lamudi.com.ph using Playwright
- Features: price, floor area, bedrooms, bathrooms, 
  city, coordinates, price per sqm

## Tech Stack
- Scraping: Playwright, BeautifulSoup4
- Data: Pandas, NumPy
- Modeling: Scikit-learn, XGBoost (coming soon)
- Dashboard: Streamlit (coming soon)

## Project Structure
Philippine-property-price-predictor/
├── day1_fetch.py          # Initial requests test
├── day1_playwright.py     # Final Playwright scraper
├── scrape_listings.py     # 50-page listing scraper
├── scrape_prices.py       # Individual listing price scraper
├── clean_data.py          # Outlier removal
├── fill_missing.py        # Imputation + feature creation
├── audit.py               # Dataset auditing
└── README.md

## Results (so far)
- Scraped 1,500 listings across 50 pages
- 96.3% price extraction rate
- 1,380 clean rows after outlier removal
- 0 null values in final dataset