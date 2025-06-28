import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import geopandas as gpd
import branca
import json
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from google.cloud import translate_v2 as translate
import os
import re
os.chdir("/Users/Wiley/desktop/airbnb")
# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="Airbnb Data Dashboard",
    page_icon=":house_with_garden:",
    layout="wide"
)
st.title("Welcome to the Airbnb Data Dashboard")
st.markdown("Navigate using the sidebar to explore data insights and maps.")
# ------------------ DATA LOAD ------------------
@st.cache_data
def load_data():
    listings = pd.read_csv("listings.csv")
    detailed_listings = pd.read_csv("listings-2.csv")
    reviews = pd.read_csv("reviews-2.csv").sample(2000, random_state=42)
    calendar = pd.read_csv("calendar.csv")
    geo_json = gpd.read_file('neighbourhoods.geojson')
    return listings, detailed_listings, reviews, calendar, geo_json

listings, detailed_listings, reviews, calendar, geo_json = load_data()

# ------------------ END ------------------