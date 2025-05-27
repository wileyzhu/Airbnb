# 🏡 Airbnb London Data Analysis

This project explores Airbnb listings in London through data analysis, geospatial visualization, and basic text mining.

## Overview

The analysis focuses on:

- **Host Pricing Trends**: Identifying pricing patterns of top hosts
- **Geospatial Insights**: Mapping listing prices and review scores by neighbourhood
- **Customer Reviews**: Using topic modeling (LDA) to uncover common themes in reviews

Streamlit is included as an optional interface to interact with the results visually.

## Key Components

- **Data Cleaning & Aggregation**: Merging listings, calendar, and review data
- **Visualization**:
  - Line plots of host prices over time (Plotly)
  - Choropleth and cluster maps (Folium)
  - Word clouds and topic models (Gensim + pyLDAvis)
- **Optional App (Streamlit)**:
  - Pages include host trends, map dashboard, and review analysis
  - Use caching to speed up page switches

## How to Use

1. Install dependencies:

pip install -r requirements.txt

2. (Optional) Run the interactive app:

streamlit run app.py

Data

Files used:
	•	listings.csv
	•	listings-2.csv
	•	calendar.csv
	•	reviews-2.csv
	•	neighbourhoods.geojson

These are standard Airbnb datasets for London, preprocessed for use.

Author

Created by [Wiley Zhu] as part of a data analytics project on the London Airbnb market.

