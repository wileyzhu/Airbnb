import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="🏠 Airbnb Dashboard (Simple)",
    page_icon="🏠",
    layout="wide"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF5A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF5A5F;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<h1 class="main-header">🏠 London Airbnb Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Analyzing Airbnb listings data from London, UK**")
st.caption("Data source: [Inside Airbnb](https://insideairbnb.com/get-the-data.html)")

# ------------------ DATA LOADING ------------------
@st.cache_data
def load_data():
    """Load datasets with simple error handling"""
    data_dir = Path("Data")
    
    if not data_dir.exists():
        st.error("❌ Data directory not found!")
        st.info("Please create a 'Data' directory with your CSV files")
        return None
    
    try:
        datasets = {}
        
        # Try to load each file
        files = {
            'listings': 'listings.csv',
            'detailed_listings': 'listings-2.csv',
            'reviews': 'reviews-2.csv',
            'calendar': 'calendar.csv'
        }
        
        for key, filename in files.items():
            file_path = data_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    if key == 'reviews' and len(df) > 2000:
                        df = df.sample(2000, random_state=42)
                    datasets[key] = df
                    st.success(f"✅ Loaded {filename} ({len(df):,} rows)")
                except Exception as e:
                    st.warning(f"⚠️ Could not load {filename}: {e}")
            else:
                st.warning(f"⚠️ File not found: {filename}")
        
        return datasets if datasets else None
        
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None

# Load data
data = load_data()

if data is None:
    st.stop()

# ------------------ SIDEBAR ------------------
st.sidebar.markdown("### 📊 Analysis Options")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis:",
    ["Dataset Overview", "Price Analysis", "Basic Charts", "Data Explorer"]
)

# ------------------ MAIN CONTENT ------------------
if analysis_type == "Dataset Overview":
    st.header("📊 Dataset Overview")
    
    # Show metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'listings' in data:
            st.metric("🏠 Listings", f"{len(data['listings']):,}")
    
    with col2:
        if 'reviews' in data:
            st.metric("💬 Reviews", f"{len(data['reviews']):,}")
    
    with col3:
        if 'detailed_listings' in data:
            st.metric("📋 Detailed", f"{len(data['detailed_listings']):,}")
    
    with col4:
        if 'calendar' in data:
            st.metric("📅 Calendar", f"{len(data['calendar']):,}")
    
    # Show data info
    st.subheader("📋 Data Information")
    
    for name, df in data.items():
        with st.expander(f"📊 {name.replace('_', ' ').title()} ({len(df):,} rows)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Columns:**")
                st.write(list(df.columns))
            
            with col2:
                st.write("**Data Types:**")
                st.write(df.dtypes.value_counts())
            
            st.write("**Sample Data:**")
            st.dataframe(df.head(), use_container_width=True)

elif analysis_type == "Price Analysis":
    st.header("💰 Price Analysis")
    
    if 'listings' in data:
        listings = data['listings']
        
        if 'price' in listings.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Price Distribution")
                
                # Simple histogram with matplotlib
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(listings['price'], bins=50, alpha=0.7, color='#FF5A5F')
                ax.set_xlabel('Price (£)')
                ax.set_ylabel('Number of Listings')
                ax.set_title('Distribution of Listing Prices')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
            
            with col2:
                st.subheader("📈 Price Statistics")
                
                price_stats = listings['price'].describe()
                
                # Display metrics
                st.metric("Average Price", f"£{price_stats['mean']:.2f}")
                st.metric("Median Price", f"£{price_stats['50%']:.2f}")
                st.metric("Min Price", f"£{price_stats['min']:.2f}")
                st.metric("Max Price", f"£{price_stats['max']:.2f}")
                st.metric("Standard Deviation", f"£{price_stats['std']:.2f}")
            
            # Price by neighborhood (if available)
            if 'neighbourhood' in listings.columns:
                st.subheader("🏘️ Price by Neighborhood")
                
                neighborhood_prices = listings.groupby('neighbourhood')['price'].agg(['mean', 'count']).reset_index()
                neighborhood_prices = neighborhood_prices[neighborhood_prices['count'] >= 5]
                neighborhood_prices = neighborhood_prices.sort_values('mean', ascending=False).head(15)
                
                fig, ax = plt.subplots(figsize=(12, 8))
                bars = ax.bar(range(len(neighborhood_prices)), neighborhood_prices['mean'], color='#FF5A5F', alpha=0.7)
                ax.set_xticks(range(len(neighborhood_prices)))
                ax.set_xticklabels(neighborhood_prices['neighbourhood'], rotation=45, ha='right')
                ax.set_ylabel('Average Price (£)')
                ax.set_title('Average Price by Neighborhood (Top 15)')
                ax.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'£{height:.0f}', ha='center', va='bottom', fontsize=8)
                
                plt.tight_layout()
                st.pyplot(fig)
        else:
            st.warning("⚠️ Price column not found in listings data")
    else:
        st.warning("⚠️ Listings data not available")

elif analysis_type == "Basic Charts":
    st.header("📊 Basic Charts")
    
    if 'listings' in data:
        listings = data['listings']
        
        # Room type analysis
        if 'room_type' in listings.columns:
            st.subheader("🏠 Room Type Distribution")
            
            room_counts = listings['room_type'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(room_counts.index, room_counts.values, color='#FF5A5F', alpha=0.7)
                ax.set_ylabel('Number of Listings')
                ax.set_title('Listings by Room Type')
                ax.grid(True, alpha=0.3)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                           f'{int(height)}', ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                # Pie chart
                fig, ax = plt.subplots(figsize=(8, 8))
                colors = ['#FF5A5F', '#00A699', '#FC642D', '#484848', '#767676']
                wedges, texts, autotexts = ax.pie(room_counts.values, labels=room_counts.index, 
                                                 autopct='%1.1f%%', colors=colors[:len(room_counts)])
                ax.set_title('Room Type Distribution')
                st.pyplot(fig)
        
        # Host analysis
        if 'host_name' in listings.columns:
            st.subheader("👥 Top Hosts")
            
            top_hosts = listings['host_name'].value_counts().head(10)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(range(len(top_hosts)), top_hosts.values, color='#00A699', alpha=0.7)
            ax.set_xticks(range(len(top_hosts)))
            ax.set_xticklabels(top_hosts.index, rotation=45, ha='right')
            ax.set_ylabel('Number of Listings')
            ax.set_title('Top 10 Hosts by Number of Listings')
            ax.grid(True, alpha=0.3)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height)}', ha='center', va='bottom')
            
            plt.tight_layout()
            st.pyplot(fig)

elif analysis_type == "Data Explorer":
    st.header("🔍 Data Explorer")
    
    # Dataset selector
    dataset_name = st.selectbox("Choose Dataset:", list(data.keys()))
    
    if dataset_name in data:
        df = data[dataset_name]
        
        st.subheader(f"📊 {dataset_name.replace('_', ' ').title()}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", f"{len(df.columns)}")
        with col3:
            st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
        # Column selector for analysis
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_columns:
            st.subheader("📈 Column Analysis")
            
            selected_column = st.selectbox("Choose Column to Analyze:", numeric_columns)
            
            if selected_column:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogram
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(df[selected_column].dropna(), bins=30, alpha=0.7, color='#FF5A5F')
                    ax.set_xlabel(selected_column)
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'Distribution of {selected_column}')
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                
                with col2:
                    # Statistics
                    st.write("**Statistics:**")
                    stats = df[selected_column].describe()
                    for stat, value in stats.items():
                        st.write(f"**{stat.title()}:** {value:.2f}")
        
        # Show raw data
        st.subheader("📋 Raw Data")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            show_rows = st.slider("Number of rows to show:", 5, min(100, len(df)), 10)
        with col2:
            if st.checkbox("Show all columns"):
                st.dataframe(df.head(show_rows), use_container_width=True)
            else:
                # Show first 10 columns
                cols_to_show = df.columns[:10]
                st.dataframe(df[cols_to_show].head(show_rows), use_container_width=True)
                if len(df.columns) > 10:
                    st.info(f"Showing first 10 of {len(df.columns)} columns")

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("*London Airbnb Data Dashboard*")
st.caption("Data from [Inside Airbnb](https://insideairbnb.com/) | Built with Streamlit")