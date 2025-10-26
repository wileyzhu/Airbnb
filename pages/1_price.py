import streamlit as st
import pandas as pd
import re
import os
from pathlib import Path

# Handle plotly import with fallback
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly not available. Using basic charts instead.")

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="💰 Price Analysis",
    page_icon="💰",
    layout="wide"
)

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    """Load datasets with proper error handling"""
    data_dir = Path("Data")
    
    if not data_dir.exists():
        st.error("❌ Data directory not found!")
        return None, None, None, None, None
    
    try:
        listings = pd.read_csv(data_dir / "listings.csv")
        detailed_listings = pd.read_csv(data_dir / "listings-2.csv")
        reviews = pd.read_csv(data_dir / "reviews-2.csv").sample(min(2000, len(pd.read_csv(data_dir / "reviews-2.csv"))), random_state=42)
        calendar = pd.read_csv(data_dir / "calendar.csv")
        return listings, detailed_listings, reviews, calendar, None
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None, None, None, None, None

listings, detailed_listings, reviews, calendar, geo_json = load_data()

if listings is None:
    st.stop()

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF5A5F;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
st.sidebar.markdown("### 💰 Price Analysis Options")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis Type:",
    ["Price Distribution", "Neighborhood Comparison", "Host Price Trends", "Price vs Features"]
)

# ------------------ TITLE ------------------
st.title("💰 Price Analysis Dashboard")
st.markdown("Explore pricing patterns and trends in Airbnb listings")

# ------------------ PRICE DISTRIBUTION ------------------
if analysis_type == "Price Distribution":
    st.header("📊 Price Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price histogram
        if PLOTLY_AVAILABLE:
            fig_hist = px.histogram(
                listings, 
                x='price', 
                nbins=50,
                title="Distribution of Listing Prices",
                labels={'price': 'Price (£)', 'count': 'Number of Listings'}
            )
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            # Fallback to matplotlib
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.hist(listings['price'], bins=50, alpha=0.7)
            ax.set_xlabel('Price (£)')
            ax.set_ylabel('Number of Listings')
            ax.set_title('Distribution of Listing Prices')
            st.pyplot(fig)
    
    with col2:
        # Price statistics
        st.markdown("### 📈 Price Statistics")
        price_stats = listings['price'].describe()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Average Price", f"£{price_stats['mean']:.2f}")
            st.metric("Median Price", f"£{price_stats['50%']:.2f}")
        with col_b:
            st.metric("Min Price", f"£{price_stats['min']:.2f}")
            st.metric("Max Price", f"£{price_stats['max']:.2f}")

# ------------------ NEIGHBORHOOD COMPARISON ------------------
elif analysis_type == "Neighborhood Comparison":
    st.header("🏘️ Price by Neighborhood")
    
    # Top neighborhoods by average price
    neighborhood_prices = listings.groupby('neighbourhood')['price'].agg(['mean', 'count']).reset_index()
    neighborhood_prices = neighborhood_prices[neighborhood_prices['count'] >= 10]  # Filter neighborhoods with at least 10 listings
    neighborhood_prices = neighborhood_prices.sort_values('mean', ascending=False).head(15)
    
    if PLOTLY_AVAILABLE:
        fig_bar = px.bar(
            neighborhood_prices,
            x='neighbourhood',
            y='mean',
            title="Average Price by Neighborhood (Top 15)",
            labels={'mean': 'Average Price (£)', 'neighbourhood': 'Neighborhood'}
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        # Fallback to matplotlib
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(range(len(neighborhood_prices)), neighborhood_prices['mean'])
        ax.set_xticks(range(len(neighborhood_prices)))
        ax.set_xticklabels(neighborhood_prices['neighbourhood'], rotation=45, ha='right')
        ax.set_ylabel('Average Price (£)')
        ax.set_title('Average Price by Neighborhood (Top 15)')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Box plot for price distribution by neighborhood
    top_neighborhoods = neighborhood_prices.head(10)['neighbourhood'].tolist()
    filtered_listings = listings[listings['neighbourhood'].isin(top_neighborhoods)]
    
    fig_box = px.box(
        filtered_listings,
        x='neighbourhood',
        y='price',
        title="Price Distribution by Neighborhood (Top 10)"
    )
    fig_box.update_xaxes(tickangle=45)
    st.plotly_chart(fig_box, use_container_width=True)

# ------------------ HOST PRICE TRENDS ------------------
elif analysis_type == "Host Price Trends":
    st.header("👥 Host Price Analysis")
    
    # Top hosts by number of listings
    top_hosts = listings['host_name'].value_counts().head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hosts = px.bar(
            x=top_hosts.index,
            y=top_hosts.values,
            title="Top 10 Hosts by Number of Listings",
            labels={'x': 'Host Name', 'y': 'Number of Listings'}
        )
        fig_hosts.update_xaxes(tickangle=45)
        st.plotly_chart(fig_hosts, use_container_width=True)
    
    with col2:
        # Average price by top hosts
        host_prices = listings[listings['host_name'].isin(top_hosts.index)].groupby('host_name')['price'].mean().sort_values(ascending=False)
        
        fig_host_prices = px.bar(
            x=host_prices.index,
            y=host_prices.values,
            title="Average Price by Top Hosts",
            labels={'x': 'Host Name', 'y': 'Average Price (£)'}
        )
        fig_host_prices.update_xaxes(tickangle=45)
        st.plotly_chart(fig_host_prices, use_container_width=True)

# ------------------ PRICE VS FEATURES ------------------
elif analysis_type == "Price vs Features":
    st.header("🔍 Price vs Property Features")
    
    if 'room_type' in listings.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Price by room type
            fig_room = px.box(
                listings,
                x='room_type',
                y='price',
                title="Price Distribution by Room Type"
            )
            st.plotly_chart(fig_room, use_container_width=True)
        
        with col2:
            # Average price by room type
            room_prices = listings.groupby('room_type')['price'].mean().sort_values(ascending=False)
            fig_room_avg = px.bar(
                x=room_prices.index,
                y=room_prices.values,
                title="Average Price by Room Type",
                labels={'x': 'Room Type', 'y': 'Average Price (£)'}
            )
            st.plotly_chart(fig_room_avg, use_container_width=True)
    
    # Check if we have detailed listings data
    if detailed_listings is not None and not detailed_listings.empty:
        st.subheader("📋 Detailed Property Analysis")
        
        # Merge with detailed data
        merged_data = pd.merge(listings, detailed_listings, on='id', how='inner')
        
        if 'accommodates' in merged_data.columns:
            fig_scatter = px.scatter(
                merged_data.sample(1000) if len(merged_data) > 1000 else merged_data,
                x='accommodates',
                y='price_x',
                title="Price vs Number of Guests Accommodated",
                labels={'accommodates': 'Number of Guests', 'price_x': 'Price (£)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
