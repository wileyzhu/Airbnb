# ------------------ PAGE CONFIG ------------------
import streamlit as st
st.set_page_config(
    page_title="Airbnb Map Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ------------------ IMPORTS ------------------
import pandas as pd
import json
import folium
import branca
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from app import load_data  # Assumes app.py defines and exports load_data()

# ------------------ LOAD DATA ------------------
@st.cache_data
def get_data():
    return load_data()
listings, detailed_listings, reviews, calendar, geo_json = get_data()

# ------------------ SIDEBAR ------------------
st.sidebar.markdown("### Explore Airbnb Data Maps")

# ------------------ TITLE ------------------
st.markdown("# Welcome to the Airbnb Map Dashboard")

# ------------------ NEIGHBOURHOOD MAP ------------------
st.header("🗺️ Average Price by Neighbourhood")
geo_neigh = json.loads(geo_json.to_json())
avg_price = listings.groupby('neighbourhood').agg({'price': 'mean'}).reset_index()

m = folium.Map(location=[51.51, -0.12], zoom_start=12)
folium.Choropleth(
    geo_data=geo_neigh,
    data=avg_price,
    columns=['neighbourhood', 'price'],
    key_on='feature.properties.neighbourhood',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
).add_to(m)
st_data = st_folium(m, width=700)
st.sidebar.markdown("### Neighbourhoods with Highest Average Price")

# ------------------ REVIEW SCORES MAP ------------------
st.header("🌍 Review Scores by Location")
combined = pd.merge(listings, detailed_listings, on='id')
review_scores = combined.groupby('neighbourhood_x')['review_scores_location'].mean().reset_index()
geo_reviews = pd.merge(geo_json, review_scores, left_on='neighbourhood', right_on='neighbourhood_x')

m2 = folium.Map(location=[51.51, -0.12], zoom_start=12)
colormap = branca.colormap.LinearColormap(
    colors=["red", "orange", "lightblue", "green", "darkgreen"],
    vmin=review_scores['review_scores_location'].min(),
    vmax=review_scores['review_scores_location'].max(),
    caption="Review Scores Location"
)

popup = folium.GeoJsonPopup(
    fields=['neighbourhood_x', 'review_scores_location'],
    aliases=['Neighbourhood', 'Score'],
    localize=True,
    labels=True
)

folium.GeoJson(
    geo_reviews,
    style_function=lambda x: {
        'fillColor': colormap(x['properties']['review_scores_location']),
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.7,
    },
    popup=popup,
).add_to(m2)
colormap.add_to(m2)
st_data2 = st_folium(m2, width=700)
st.sidebar.markdown("### Neighbourhoods with Highest Review Scores")

# ------------------ MARKER CLUSTER MAP ------------------
st.header("📍 Airbnb Listings Map (Marker Cluster)")
m3 = folium.Map(location=[51.51, -0.12], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m3)

for _, row in listings.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['host_name']}<br>£{row['price']:.0f}"
    ).add_to(marker_cluster)

st_data3 = st_folium(m3, width=700, height=500)
st.sidebar.markdown("### Airbnb Listings Map with Marker Clusters")