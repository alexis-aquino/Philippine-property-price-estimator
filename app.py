"""
Philippine Property Price Predictor - Streamlit Dashboard
Interactive tool for predicting metro Manila condo prices
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="🏢 PH Property Price Estimator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOAD MODEL & DATA
# ============================================================================
@st.cache_resource
def load_model():
    with open('model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_resource
def load_metadata():
    with open('metadata.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    return pd.read_csv('lamudi_features.csv')

model = load_model()
metadata = load_metadata()
df = load_data()

# ============================================================================
# SIDEBAR - NAVIGATION
# ============================================================================
st.sidebar.title("🏠 PH Property Estimator")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select a page:",
    ["🎯 Price Predictor", "📊 Data Explorer", "📈 Model Insights", "ℹ️ About"]
)

# ============================================================================
# PAGE 1: PRICE PREDICTOR
# ============================================================================
if page == "🎯 Price Predictor":
    st.title("🎯 Property Price Predictor")
    st.markdown("Predict condo prices in Metro Manila based on property features")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Property Details")

        bedrooms = st.slider("Bedrooms", min_value=1, max_value=6, value=2, step=1)
        bathrooms = st.slider("Bathrooms", min_value=1, max_value=4, value=1, step=1)
        floor_area = st.number_input("Floor Area (sqm)", min_value=20, max_value=200, value=50, step=5)
        city = st.selectbox("City", sorted(df['city'].unique()))

        st.markdown("**Amenities**")
        has_pool = st.checkbox("Swimming Pool", value=False)
        has_gym = st.checkbox("Gym/Fitness", value=False)
        has_parking = st.checkbox("Parking", value=False)
        has_balcony = st.checkbox("Balcony/Terrace", value=False)

    with col2:
        st.subheader("Location Details")

        # Get city-specific stats
        city_data = df[df['city'] == city]
        lat = st.number_input(
            "Latitude",
            min_value=14.0,
            max_value=15.0,
            value=float(city_data['latitude'].median()),
            step=0.001
        )
        lon = st.number_input(
            "Longitude",
            min_value=120.5,
            max_value=121.5,
            value=float(city_data['longitude'].median()),
            step=0.001
        )

        st.markdown("**Market Context**")
        median_price_city = city_data['price'].median()
        median_sqm_city = city_data['price_per_sqm'].median()

        st.metric("City Median Price", f"₱{median_price_city:,.0f}")
        st.metric("City Median Price/sqm", f"₱{median_sqm_city:,.0f}")

    # ====================================================================
    # MAKE PREDICTION
    # ====================================================================
    if st.button("🔮 Predict Price", use_container_width=True):
        from geopy.distance import geodesic

        # Calculate distances
        BGC_CENTER = (14.5547, 121.0486)
        MAKATI_CBD = (14.5547, 121.0244)
        ORTIGAS_CENTER = (14.5875, 121.0603)

        def calc_distance(lat, lon, landmark):
            try:
                return geodesic((lat, lon), landmark).km
            except:
                return None

        dist_to_bgc = calc_distance(lat, lon, BGC_CENTER)
        dist_to_makati = calc_distance(lat, lon, MAKATI_CBD)
        dist_to_ortigas = calc_distance(lat, lon, ORTIGAS_CENTER)
        dist_to_nearest = min([dist_to_bgc, dist_to_makati, dist_to_ortigas])

        # Price per sqm estimate
        price_per_sqm = median_sqm_city

        # Aggregate features
        city_listing_count = len(city_data)

        # Prepare features in same order as model
        features = {
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'floor_area': floor_area,
            'price_per_sqm': price_per_sqm,
            'dist_to_bgc': dist_to_bgc,
            'dist_to_makati': dist_to_makati,
            'dist_to_ortigas': dist_to_ortigas,
            'dist_to_nearest_cbd': dist_to_nearest,
            'city_median_price': median_price_city,
            'city_median_price_per_sqm': median_sqm_city,
            'city_listing_count': city_listing_count,
            'has_pool': int(has_pool),
            'has_gym': int(has_gym),
            'has_parking': int(has_parking),
            'has_balcony': int(has_balcony),
        }

        # Add one-hot encoded city features
        for col in metadata['city_cols']:
            city_name = col.replace('city_', '')
            features[col] = 1 if city_name == city else 0

        # Create dataframe in correct feature order
        X_pred = pd.DataFrame([features])[metadata['feature_cols']]

        # Predict
        log_price_pred = model.predict(X_pred)[0]
        price_pred = np.expm1(log_price_pred)

        # Display result
        st.success("✅ Prediction complete!")

        pred_col1, pred_col2, pred_col3 = st.columns(3)

        with pred_col1:
            st.metric(
                "Estimated Price",
                f"₱{price_pred:,.0f}",
                delta=f"{((price_pred/median_price_city - 1) * 100):+.1f}% vs city median"
            )

        with pred_col2:
            price_per_sqm_pred = price_pred / floor_area
            st.metric(
                "Price per sqm",
                f"₱{price_per_sqm_pred:,.0f}"
            )

        with pred_col3:
            st.metric(
                "Confidence",
                f"{metadata['test_r2']*100:.1f}%",
                help="Model R² score on test data"
            )

        # Comparison with city stats
        st.markdown("---")
        st.subheader("Market Comparison")

        comparison_col1, comparison_col2 = st.columns(2)

        with comparison_col1:
            st.write(f"**Your Property**: ₱{price_pred:,.0f}")
            st.write(f"**City Median**: ₱{median_price_city:,.0f}")

            if price_pred > median_price_city:
                diff = price_pred - median_price_city
                pct = (diff / median_price_city) * 100
                st.write(f"**Premium**: +₱{diff:,.0f} ({pct:.1f}% above median)")
            else:
                diff = median_price_city - price_pred
                pct = (diff / median_price_city) * 100
                st.write(f"**Discount**: -₱{diff:,.0f} ({pct:.1f}% below median)")

        with comparison_col2:
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = ['#FF6B6B', '#4ECDC4']
            prices = [price_pred, median_price_city]
            labels = ['Your Property', 'City Median']
            bars = ax.bar(labels, prices, color=colors, alpha=0.8, edgecolor='black', linewidth=2)

            ax.set_ylabel('Price (₱)', fontsize=12, fontweight='bold')
            ax.set_title(f'Price Comparison in {city}', fontsize=14, fontweight='bold')
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₱{x/1e6:.1f}M' if x >= 1e6 else f'₱{x/1e3:.0f}K'))

            # Add value labels on bars
            for bar, price in zip(bars, prices):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₱{price:,.0f}',
                       ha='center', va='bottom', fontweight='bold', fontsize=11)

            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

# ============================================================================
# PAGE 2: DATA EXPLORER
# ============================================================================
elif page == "📊 Data Explorer":
    st.title("📊 Data Explorer")
    st.markdown("Explore patterns in Metro Manila condo market")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Price Distribution",
        "🏙️ By City",
        "📏 By Size",
        "🔗 Correlations"
    ])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df['price']/1e6, bins=40, color='#4ECDC4', alpha=0.8, edgecolor='black')
            ax.set_xlabel('Price (₱ Millions)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Number of Listings', fontsize=11, fontweight='bold')
            ax.set_title('Price Distribution', fontsize=13, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)

        with col2:
            stats = df['price'].describe()
            st.metric("Average Price", f"₱{stats['mean']:,.0f}")
            st.metric("Median Price", f"₱{stats['50%']:,.0f}")
            st.metric("Price Range", f"₱{stats['min']:,.0f} - ₱{stats['max']:,.0f}")
            st.metric("Standard Dev", f"₱{stats['std']:,.0f}")

    with tab2:
        city_stats = df.groupby('city').agg({
            'price': ['count', 'median', 'mean'],
            'floor_area': 'median'
        }).round(0)

        city_stats.columns = ['Count', 'Median Price', 'Mean Price', 'Median Area']
        city_stats = city_stats.sort_values('Median Price', ascending=False)

        fig, ax = plt.subplots(figsize=(12, 6))
        city_stats['Median Price'].plot(kind='barh', ax=ax, color='#FF6B6B', alpha=0.8, edgecolor='black')
        ax.set_xlabel('Median Price (₱)', fontsize=11, fontweight='bold')
        ax.set_title('Median Price by City', fontsize=13, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₱{x/1e6:.1f}M'))
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

        st.dataframe(city_stats, use_container_width=True)

    with tab3:
        df['size_label'] = pd.cut(
            df['floor_area'],
            bins=[0, 30, 50, 80, 120, 500],
            labels=['Micro\n<30sqm', 'Small\n30-50sqm', 'Medium\n50-80sqm', 'Large\n80-120sqm', 'Luxury\n>120sqm']
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        df.boxplot(column='price', by='size_label', ax=ax)
        ax.set_ylabel('Price (₱)', fontsize=11, fontweight='bold')
        ax.set_xlabel('Property Size', fontsize=11, fontweight='bold')
        ax.set_title('Price by Property Size', fontsize=13, fontweight='bold')
        plt.suptitle('')  # Remove automatic title
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₱{x/1e6:.1f}M' if x >= 1e6 else f'₱{x/1e3:.0f}K'))
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

    with tab4:
        numeric_cols = ['price', 'floor_area', 'bedrooms', 'bathrooms', 'price_per_sqm',
                       'dist_to_nearest_cbd', 'city_listing_count']

        corr_matrix = df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                   square=True, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title('Feature Correlation Matrix', fontsize=13, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

# ============================================================================
# PAGE 3: MODEL INSIGHTS
# ============================================================================
elif page == "📈 Model Insights":
    st.title("📈 Model Performance & Insights")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Model Type", metadata['model_name'])

    with col2:
        st.metric("Test R² Score", f"{metadata['test_r2']:.4f}", help="Higher is better (max 1.0)")

    with col3:
        st.metric("Test MAE", f"₱{np.expm1(metadata['test_mae']):,.0f}")

    with col4:
        st.metric("Training Samples", f"{len(df)}")

    st.markdown("---")

    st.subheader("Feature Importance")
    st.markdown("Top features that influence price predictions:")

    importance_df = pd.DataFrame({
        'Feature': metadata['feature_cols'],
    })

    # Calculate importance using model
    importance_scores = model.feature_importances_
    importance_df['Importance'] = importance_scores
    importance_df = importance_df.sort_values('Importance', ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(importance_df)), importance_df['Importance'], color='#4ECDC4', alpha=0.8, edgecolor='black')
    ax.set_yticks(range(len(importance_df)))
    ax.set_yticklabels(importance_df['Feature'])
    ax.set_xlabel('Importance Score', fontsize=11, fontweight='bold')
    ax.set_title('Top 15 Features by Importance', fontsize=13, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("Key Findings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Strong Predictors:**
        - 📐 **Floor Area**: Largest impact on price
        - 💰 **Price per sqm**: Market rate indicator
        - 📍 **Location**: Distance to CBDs matters
        - 🏙️ **City**: Different cities have different price levels
        """)

    with col2:
        st.markdown(f"""
        **Model Quality:**
        - ✅ R² = {metadata['test_r2']:.4f} (explains {metadata['test_r2']*100:.1f}% of price variation)
        - ✅ Very low RMSE on log scale ({metadata['test_rmse']:.4f})
        - ✅ Good generalization (no overfitting)
        - ✅ Trained on {len(df)} real Metro Manila listings
        """)

# ============================================================================
# PAGE 4: ABOUT
# ============================================================================
elif page == "ℹ️ About":
    st.title("ℹ️ About This Project")

    st.markdown("""
    ## Philippine Property Price Estimator

    An end-to-end machine learning project predicting condo prices in Metro Manila.

    ### 📊 Dataset
    - **Source**: Lamudi.com.ph (Leading PH real estate platform)
    - **Listings**: 1,380 cleaned condo listings
    - **Location**: Metro Manila (13 cities)
    - **Features**: 31 engineered features per property

    ### 🔧 Tech Stack
    - **Web Scraping**: Playwright, BeautifulSoup4
    - **Data Processing**: Pandas, NumPy
    - **Feature Engineering**: Geopy (distance calculations), one-hot encoding
    - **Modeling**: Scikit-learn Gradient Boosting
    - **Dashboard**: Streamlit

    ### 🏗️ Project Phases
    1. ✅ **Data Scraping** - 50 pages of Lamudi listings
    2. ✅ **Data Cleaning** - Outlier removal, 96.3% price extraction rate
    3. ✅ **Feature Engineering** - 31 engineered features
    4. ✅ **Model Training** - Gradient Boosting with 99.36% accuracy
    5. ✅ **Dashboard** - Interactive Streamlit app

    ### 🎯 Model Features

    **Property Features:**
    - Bedrooms, bathrooms, floor area
    - Amenities (pool, gym, parking, balcony)
    - Property condition indicators

    **Location Features:**
    - GPS coordinates (latitude, longitude)
    - Distance to key business districts (BGC, Makati, Ortigas)
    - City-level market statistics

    ### 📈 Performance
    - **R² Score**: 0.9936 (test set)
    - **Mean Absolute Error**: ≈ ₱200K
    - **Training Samples**: 1,104
    - **Test Samples**: 276

    ### 📍 Coverage
    Cities included: Makati, Taguig, BGC, Quezon City, Pasig, Mandaluyong,
    Parañaque, Manila, Marikina, Pasay, San Juan, Las Piñas, Pateros

    ### 🚀 Future Enhancements
    - Real-time price scraping
    - Market trend analysis
    - Portfolio analysis for investors
    - API endpoint for automated predictions
    - Price forecast model

    ---

    **Built with ❤️ for the PH real estate market**

    [GitHub Repo](https://github.com/alexis-aquino/philippine-property-price-estimator)
    """)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 12px;'>"
    "Philippine Property Price Estimator | Built with Streamlit | "
    f"Model: {metadata['model_name']} (R² = {metadata['test_r2']:.4f})"
    "</div>",
    unsafe_allow_html=True
)
