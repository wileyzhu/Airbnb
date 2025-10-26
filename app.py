import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# Handle optional imports with fallbacks
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly not available. Some visualizations will be limited.")

try:
    import folium
    from folium.plugins import MarkerCluster
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    st.warning("⚠️ Folium not available. Map features will be limited.")

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="🏠 Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .sub-header {
        font-size: 1.2rem;
        color: #484848;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF5A5F;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<h1 class="main-header">🏠 Airbnb Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Explore comprehensive insights from Airbnb listings data</p>', unsafe_allow_html=True)

# ------------------ DATA LOADING WITH ERROR HANDLING ------------------
@st.cache_data
def load_data():
    """Load all required datasets with proper error handling"""
    
    # Define data directory path
    data_dir = Path("airbnb/data")
    
    # Alternative paths to check
    alternative_paths = [
        Path("data"),
        Path("Data"),
        Path("."),
        Path("../data"),
        Path("../airbnb/data")
    ]
    
    # Find the correct data directory
    data_path = None
    for path in [data_dir] + alternative_paths:
        if path.exists():
            data_path = path
            break
    
    if data_path is None:
        st.error("❌ Data directory not found. Please ensure your data files are in one of these locations:")
        for path in [data_dir] + alternative_paths:
            st.write(f"- `{path}`")
        st.stop()
    
    try:
        # Load datasets with progress indication
        with st.spinner("🔄 Loading datasets..."):
            datasets = {}
            
            # Define required files
            required_files = {
                'listings': 'listings.csv',
                'detailed_listings': 'listings-2.csv', 
                'reviews': 'reviews-2.csv',
                'calendar': 'calendar.csv',
                'neighbourhoods': 'neighbourhoods.geojson'
            }
            
            # Load each file
            for key, filename in required_files.items():
                file_path = data_path / filename
                
                if not file_path.exists():
                    st.warning(f"⚠️ File not found: {filename}")
                    continue
                
                try:
                    if filename.endswith('.csv'):
                        if key == 'reviews':
                            # Sample reviews for performance
                            df = pd.read_csv(file_path)
                            datasets[key] = df.sample(min(2000, len(df)), random_state=42)
                        else:
                            datasets[key] = pd.read_csv(file_path)
                    elif filename.endswith('.geojson'):
                        if GEOPANDAS_AVAILABLE:
                            datasets[key] = gpd.read_file(file_path)
                        else:
                            st.warning(f"⚠️ GeoPandas not available. Skipping {filename}")
                    
                    st.success(f"✅ Loaded {filename}")
                    
                except Exception as e:
                    st.error(f"❌ Error loading {filename}: {str(e)}")
            
            return datasets
            
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

# Load data
data = load_data()

# ------------------ DATA OVERVIEW ------------------
if data:
    st.markdown("---")
    st.markdown("### 📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'listings' in data:
            st.metric("🏠 Total Listings", f"{len(data['listings']):,}")
    
    with col2:
        if 'reviews' in data:
            st.metric("💬 Reviews Loaded", f"{len(data['reviews']):,}")
    
    with col3:
        if 'detailed_listings' in data:
            st.metric("📋 Detailed Records", f"{len(data['detailed_listings']):,}")
    
    with col4:
        if 'calendar' in data:
            st.metric("📅 Calendar Entries", f"{len(data['calendar']):,}")
    
    # Navigation instructions
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.info("👈 Use the sidebar to navigate between different analysis pages:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**💰 Price Analysis**\n- Price distributions\n- Neighborhood comparisons\n- Seasonal trends")
    with col2:
        st.markdown("**🗺️ Interactive Maps**\n- Listing locations\n- Price heatmaps\n- Neighborhood boundaries")
    with col3:
        st.markdown("**📝 Text Analysis**\n- Review sentiment\n- Description insights\n- Word clouds")

else:
    st.error("❌ No data could be loaded. Please check your data files and try again.")

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit*")