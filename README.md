# 🏡 Airbnb Data Dashboard

This is an interactive multi-page Streamlit web application for exploring Airbnb listings data in London. The app allows users to visualize host pricing trends, explore geospatial patterns of prices and reviews, and analyze customer review texts with topic modeling.

## 📁 Project Structure

airbnb-dashboard/
├── app.py                     # Shared loader for data and libraries
├── listings.csv               # Airbnb listing data
├── listings-2.csv             # Detailed listings
├── reviews-2.csv              # Review texts
├── calendar.csv               # Pricing calendar
├── neighbourhoods.geojson     # Geo-boundaries for London neighborhoods
└── pages/
├── 1_📈_Host_Price_Trends.py     # Host price trend analysis (Plotly)
├── 2_🌍_Map_Dashboard.py         # Folium maps for price, reviews, and clusters
└── 3_🧠_Text_Analysis.py         # LDA topic modeling and word cloud

## 🚀 How to Run

1. **Install dependencies:**

```bash
pip install streamlit pandas numpy plotly folium geopandas branca gensim spacy nltk pyLDAvis streamlit-folium
python -m nltk.downloader stopwords
python -m spacy download en_core_web_sm

	2.	Run the app:

streamlit run app.py

	3.	Use the sidebar to navigate between pages:
	•	📈 Host Price Trends
	•	🌍 Map Dashboard
	•	🧠 Text Analysis

📊 Features

1. Host Price Trends
	•	Visualize average weekly price trends for the top 10 hosts.
	•	Based on individual CSV exports per host.

2. Map Dashboard
	•	Choropleth Map: Average price by neighborhood.
	•	Review Score Map: Visualize location ratings across London.
	•	Marker Cluster: Interactive map showing all listings.

3. Text Analysis
	•	Preprocesses Airbnb review text with lemmatization and stopword removal.
	•	Generates a WordCloud of common terms.
	•	Builds an LDA topic model and plots coherence scores.
	•	Interactive LDA visualizations with pyLDAvis.

⚙️ Caching & Optimization
	•	Uses @st.cache_data and @st.cache_resource to prevent recomputation on page switches.
	•	Heavy model components are excluded from reruns via Streamlit’s underscore parameter convention.

🔐 Optional: Google Translate

If you want to translate review texts:
	1.	Enable Google Cloud Translate API.
	2.	Set your environment variable in your terminal:

export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/your/service_account.json"

📌 Notes
	•	Large datasets and LDA models may consume significant memory; sampling is used to keep the app responsive.
	•	This app is tested on macOS using Python 3.11 and Streamlit 1.32+.
