# Philippine Property Price Predictor

A machine learning project that predicts condo prices in Metro Manila using data scraped from Lamudi.com.ph.

## Project Status
✅ **Complete** — All phases finished including interactive Streamlit dashboard

## Dataset
- 1,380 cleaned condo listings from Metro Manila
- Scraped from Lamudi.com.ph using Playwright
- Features: price, floor area, bedrooms, bathrooms, city, coordinates, price per sqm
- Coverage: 13 cities (Makati, Taguig, BGC, Quezon City, Pasig, Mandaluyong, Parañaque, Manila, Marikina, Pasay, San Juan, Las Piñas, Pateros)

## Tech Stack
- Scraping: Playwright, BeautifulSoup4
- Data: Pandas, NumPy
- Modeling: Scikit-learn Gradient Boosting (R² = 0.9936)
- Dashboard: Streamlit
- Visualization: Matplotlib, Seaborn

## Project Structure
```
philippine-property-price-estimator/
├── app.py                      # Streamlit interactive dashboard
├── train_model.py              # Model training script
├── feature_engineering.py      # Feature generation
├── clean_data.py               # Outlier removal
├── fill_missing.py             # Imputation + feature creation
├── day1_fetch.py               # Initial requests test
├── day1_playwright.py          # Final Playwright scraper
├── scrape_listings.py          # 50-page listing scraper
├── scrape_prices.py            # Individual listing price scraper
├── audit.py                    # Dataset auditing
├── model.pkl                   # Trained model
├── metadata.pkl                # Model metadata
├── lamudi_modeling_ready.csv   # Cleaned dataset
├── lamudi_features.csv         # Featured dataset
├── requirements.txt            # Python dependencies
└── README.md
```

## Results
- ✅ Scraped 1,500 listings across 50 pages
- ✅ 96.3% price extraction rate
- ✅ 1,380 clean rows after outlier removal
- ✅ 0 null values in final dataset
- ✅ 31 engineered features
- ✅ Model R² = 0.9936 (explains 99.36% of price variation)
- ✅ Mean Absolute Error ≈ ₱200K
- ✅ Interactive Streamlit dashboard for predictions

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the Dashboard
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Train the Model
```bash
python train_model.py
```

## Dashboard Features

### 🎯 Price Predictor
- Input property details (bedrooms, bathrooms, floor area)
- Select location and amenities
- Get instant price prediction with market comparison

### 📊 Data Explorer
- Price distribution analysis
- City-wise price comparison
- Property size analysis
- Feature correlation heatmap

### 📈 Model Insights
- Model performance metrics
- Feature importance ranking
- Key findings and statistics

### ℹ️ About
- Project overview
- Dataset information
- Technical details

## Model Performance
| Metric | Value |
|--------|-------|
| Model | Gradient Boosting Regressor |
| R² Score (Test) | 0.9936 |
| Mean Absolute Error | ₱200,000 |
| RMSE (log scale) | 0.0835 |
| Training Samples | 1,104 |
| Test Samples | 276 |

## Top Features by Importance
1. Floor Area (74.6%)
2. Price per sqm (25.1%)
3. Distance to Ortigas CBD (0.04%)
4. Bedrooms (0.03%)
5. Distance to BGC (0.03%)

## Key Insights
- **Floor area** is the strongest price predictor
- **Market rate (price/sqm)** provides strong baseline
- **Location matters** - distance to CBD affects prices
- **Amenities** have moderate impact (pool, gym, parking, balcony)
- **City selection** influences price ranges significantly

## Future Enhancements
- Real-time price scraping updates
- Market trend analysis & forecasting
- Investment portfolio analysis tools
- REST API endpoint
- Price prediction alerts
- Neighborhood-level analysis

## Requirements
- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- matplotlib >= 3.5.0
- seaborn >= 0.12.0
- streamlit >= 1.20.0
- geopy >= 2.2.0

## Development
Built using:
- Playwright for modern web scraping
- BeautifulSoup4 for HTML parsing
- Scikit-learn for machine learning
- Streamlit for rapid dashboard development

## Notes
- Price predictions are estimates based on historical data
- Model was trained on June 2026 market data
- For investment decisions, consult with real estate professionals
- Prices fluctuate based on market conditions

---

**Built with ❤️ for the Philippine real estate market**

This project demonstrates a complete ML pipeline: data collection → cleaning → feature engineering → modeling → deployment.
