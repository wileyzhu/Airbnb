# ------------------ PAGE CONFIG ------------------
import streamlit as st
st.set_page_config(
    page_title="🗺️ Interactive Maps",
    page_icon="🗺️",
    layout="wide"
)

# ------------------ IMPORTS ------------------
import pandas as pd
import json
from pathlib import Path

# Handle optional imports
try:
    import folium
    from folium.plugins import MarkerCluster, HeatMap
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    st.error("❌ Folium not available. Please install it with: pip install folium streamlit-folium")
    st.stop()

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
        
        # Try to load GeoJSON
        geo_json = None
        geo_path = data_dir / "neighbourhoods.geojson"
        if geo_path.exists():
            try:
                import geopandas as gpd
                geo_json = gpd.read_file(geo_path)
            except ImportError:
                st.warning("⚠️ GeoPandas not available. Some map features will be limited.")
        
        return listings, detailed_listings, reviews, calendar, geo_json
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None, None, None, None, None

listings, detailed_listings, reviews, calendar, geo_json = load_data()

if listings is None:
    st.stop()

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
st.sidebar.markdown("### 🗺️ Map Options")
map_type = st.sidebar.selectbox(
    "Choose Map Type:",
    ["Listings Overview", "Price Heatmap", "Neighborhood Analysis", "Review Scores"]
)

# Filter options
st.sidebar.markdown("### 🔍 Filters")
price_range = st.sidebar.slider(
    "Price Range (£)",
    min_value=int(listings['price'].min()),
    max_value=int(listings['price'].max()),
    value=(int(listings['price'].min()), int(listings['price'].max()))
)

# Filter data based on price range
filtered_listings = listings[
    (listings['price'] >= price_range[0]) & 
    (listings['price'] <= price_range[1])
]

# ------------------ TITLE ------------------
st.title("🗺️ Interactive Maps Dashboard")
st.markdown("Explore Airbnb listings geographically with interactive maps")

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📍 Total Listings", f"{len(filtered_listings):,}")
with col2:
    st.metric("💰 Avg Price", f"£{filtered_listings['price'].mean():.2f}")
with col3:
    st.metric("🏘️ Neighborhoods", f"{filtered_listings['neighbourhood'].nunique()}")

st.markdown("---")

# ------------------ LISTINGS OVERVIEW MAP ------------------
if map_type == "Listings Overview":
    st.header("📍 Airbnb Listings Overview")
    
    # Create base map
    center_lat = filtered_listings['latitude'].mean()
    center_lon = filtered_listings['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Add marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Sample data for performance if too many listings
    sample_size = min(1000, len(filtered_listings))
    sample_listings = filtered_listings.sample(sample_size) if len(filtered_listings) > sample_size else filtered_listings
    
    for _, row in sample_listings.iterrows():
        popup_text = f"""
        <b>{row['name'][:50]}...</b><br>
        Host: {row['host_name']}<br>
        Price: £{row['price']:.0f}<br>
        Room Type: {row.get('room_type', 'N/A')}<br>
        Neighborhood: {row['neighbourhood']}
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='red', icon='home')
        ).add_to(marker_cluster)
    
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st_folium(m, width=700, height=500)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if sample_size < len(filtered_listings):
        st.info(f"📊 Showing {sample_size:,} out of {len(filtered_listings):,} listings for performance")

# ------------------ PRICE HEATMAP ------------------
elif map_type == "Price Heatmap":
    st.header("💰 Price Distribution Heatmap")
    
    # HeatMap already imported above
    
    # Create base map
    center_lat = filtered_listings['latitude'].mean()
    center_lon = filtered_listings['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Prepare heat map data
    heat_data = [[row['latitude'], row['longitude'], row['price']] 
                 for idx, row in filtered_listings.iterrows()]
    
    # Add heat map
    HeatMap(heat_data, radius=15, blur=10, gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}).add_to(m)
    
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st_folium(m, width=700, height=500)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.info("🔥 Red areas indicate higher prices, blue areas indicate lower prices")

# ------------------ NEIGHBORHOOD ANALYSIS ------------------
elif map_type == "Neighborhood Analysis":
    st.header("🏘️ Neighborhood Analysis")
    
    if geo_json is not None:
        # Calculate neighborhood statistics
        neighborhood_stats = filtered_listings.groupby('neighbourhood').agg({
            'price': ['mean', 'count'],
            'latitude': 'mean',
            'longitude': 'mean'
        }).round(2)
        
        neighborhood_stats.columns = ['avg_price', 'listing_count', 'lat', 'lon']
        neighborhood_stats = neighborhood_stats.reset_index()
        
        # Create choropleth map
        center_lat = filtered_listings['latitude'].mean()
        center_lon = filtered_listings['longitude'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        
        try:
            folium.Choropleth(
                geo_data=geo_json,
                data=neighborhood_stats,
                columns=['neighbourhood', 'avg_price'],
                key_on='feature.properties.neighbourhood',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='Average Price (£)'
            ).add_to(m)
        except Exception as e:
            st.warning(f"⚠️ Could not create choropleth map: {e}")
        
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st_folium(m, width=700, height=500)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show top neighborhoods
        st.subheader("🏆 Top Neighborhoods by Average Price")
        top_neighborhoods = neighborhood_stats.nlargest(10, 'avg_price')[['neighbourhood', 'avg_price', 'listing_count']]
        st.dataframe(top_neighborhoods, use_container_width=True)
    else:
        st.warning("⚠️ Neighborhood boundaries data not available. Showing point map instead.")
        
        # Fallback to point map
        center_lat = filtered_listings['latitude'].mean()
        center_lon = filtered_listings['longitude'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        
        # Color code by neighborhood
        neighborhoods = filtered_listings['neighbourhood'].unique()
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        
        for i, neighborhood in enumerate(neighborhoods[:10]):  # Limit to 10 for visibility
            neighborhood_data = filtered_listings[filtered_listings['neighbourhood'] == neighborhood]
            color = colors[i % len(colors)]
            
            for _, row in neighborhood_data.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    popup=f"{neighborhood}<br>£{row['price']:.0f}",
                    color=color,
                    fill=True,
                    fillColor=color
                ).add_to(m)
        
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st_folium(m, width=700, height=500)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------ REVIEW SCORES ------------------
elif map_type == "Review Scores":
    st.header("⭐ Review Scores Analysis")
    
    if detailed_listings is not None and not detailed_listings.empty:
        # Merge with detailed data
        merged_data = pd.merge(filtered_listings, detailed_listings, on='id', how='inner')
        
        if 'review_scores_rating' in merged_data.columns:
            # Filter out listings without review scores
            review_data = merged_data.dropna(subset=['review_scores_rating'])
            
            if not review_data.empty:
                center_lat = review_data['latitude'].mean()
                center_lon = review_data['longitude'].mean()
                
                m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
                
                # Color code by review score
                for _, row in review_data.iterrows():
                    score = row['review_scores_rating']
                    
                    # Determine color based on score
                    if score >= 4.5:
                        color = 'green'
                    elif score >= 4.0:
                        color = 'orange'
                    else:
                        color = 'red'
                    
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=6,
                        popup=f"Rating: {score:.1f}/5<br>Price: £{row['price_x']:.0f}",
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7
                    ).add_to(m)
                
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                st_folium(m, width=700, height=500)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Legend
                st.markdown("""
                **Legend:**
                - 🟢 Green: Excellent (4.5+ stars)
                - 🟠 Orange: Good (4.0-4.4 stars)  
                - 🔴 Red: Below 4.0 stars
                """)
            else:
                st.warning("⚠️ No review score data available for the selected listings.")
        else:
            st.warning("⚠️ Review scores not available in the dataset.")
    else:
        st.warning("⚠️ Detailed listings data not available for review analysis.")