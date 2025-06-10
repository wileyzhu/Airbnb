# %%
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import os

# %%
os.chdir("/Users/wiley/desktop/airbnb")
listings = pd.read_csv("listings.csv")
neighbourhoods = pd.read_csv("neighbourhoods.csv")
reviews = pd.read_csv("reviews-2.csv")
calendar = pd.read_csv("calendar.csv")
detailed_listings = pd.read_csv("listings-2.csv")


# %%
df = listings.copy()
host = df['host_name'].value_counts().head(10).reset_index()
hosts = host['host_name'].tolist()

# %%
import re
dfs = {}  # a dictionary of DataFrames
for host_name in hosts:
    safe_name = re.sub(r'\W+', '_', str(host_name))
    filename = f"host_{safe_name}.csv"
    dfs[host_name] = pd.read_csv(filename)

# %%
import plotly.express as px

# Combine all host DataFrames into one for plotting
plot_df = pd.concat([dfs[host_name] for host_name in hosts], ignore_index=True)
plot_df['date'] = pd.to_datetime(plot_df['date'])
plot_df = (
    plot_df
    .groupby(['host_name', plot_df['date'].dt.to_period('W')])['price_x']
    .mean()
    .reset_index()
)
plot_df['date'] = plot_df['date'].dt.to_timestamp()
fig = px.line(
	plot_df,
	x='date',
	y='price_x',
	color='host_name',
	line_shape='linear',
	title='Price Trends for All Hosts'
)
fig.update_traces(mode='lines')
fig.update_layout(xaxis_title='Date', yaxis_title='Price')
fig.write_html('first_figure.html', auto_open=True)

# %%
calendar.head()

# %%
calendar['price'] = calendar['price'].str.replace('$', '').str.replace(',', '').astype(float)
calendar['date'] = pd.to_datetime(calendar['date'], format='%Y-%m-%d')
calendar['adjusted_price'] = calendar['adjusted_price'].str.replace('$', '').str.replace(',', '').astype(float)
calendar['discount'] = calendar['price'] - calendar['adjusted_price']/calendar['price']

# %%
import geopandas as gpd
geo_json = gpd.read_file('neighbourhoods.geojson')

# %%
geo_json.head()

# %%
geo_json.drop(columns=['neighbourhood_group'], inplace=True, errors='ignore')

# %%
import json
geo_neiboor = json.loads(geo_json.to_json())

# %%
import folium
m = folium.Map(location=[51.51, -0.12], zoom_start=12)
price = listings.groupby('neighbourhood').agg({'price': 'mean'}).reset_index()
folium.Choropleth(
    geo_data=geo_neiboor,
    data=price,
    columns=['neighbourhood', 'price'],
    key_on='feature.properties.neighbourhood',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
).add_to(m)
m

# %%
geo_listings = pd.merge(geo_json, listings, left_on='neighbourhood', right_on='neighbourhood')
geo_listings = geo_listings.drop(columns=['neighbourhood_group'], errors='ignore')

# %%
detailed_listings1 = pd.merge(listings, detailed_listings, on='id', how='left')

# %%
m = folium.Map(location=[51.51, -0.12], zoom_start=12)
review_scores_location = detailed_listings1.groupby('neighbourhood_x').agg({'review_scores_location': 'mean'}).reset_index()
import branca
colormap = branca.colormap.LinearColormap(
    vmin=review_scores_location['review_scores_location'].min(),
    vmax=review_scores_location['review_scores_location'].max(),
    colors=["red", "orange", "lightblue", "green", "darkgreen"],
    caption="Review Scores Location",
)

# %%
geo_reviews = pd.merge(geo_json, review_scores_location, left_on='neighbourhood', right_on='neighbourhood_x')

# %%
m = folium.Map(location=[51.51, -0.12], zoom_start=12)
popup = folium.GeoJsonPopup(
    fields=['neighbourhood_x', 'review_scores_location'],
    aliases=['Neighbourhood', 'Review Scores Location'],
    localize=True,
    labels=True,
    style="background-color: white; color: black; font-size: 12px;",
)
folium.GeoJson(
    geo_reviews,
    style_function=lambda x: {
        'fillColor': colormap(x['properties']['review_scores_location'])
        if x['properties']['review_scores_location'] > 0 else 'transparent',
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.7,
    },
    popup=popup,
).add_to(m)
colormap.add_to(m)
m

# %%
m = folium.Map(location=[51.51, -0.12], zoom_start=12)
from folium.plugins import MarkerCluster

marker_cluster = MarkerCluster().add_to(m)

for _, row in listings.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['host_name']}<br>£{row['price']:.0f}"
    ).add_to(marker_cluster)

m

# %%
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/wiley/Documents/Downloads/crypto-analyzer-458015-q2-a063b8b803a6.json"

# %%
from google.cloud import translate_v2 as translate

def batched_translate(text_list, project_id, target_language="en", max_chars=10000, batch_size=120):
    client = translate.Client()
    current_batch = []
    char_count = 0
    results = []

    for text in text_list:
        text_len = len(text)
        
        # If adding this text exceeds char limit or batch size, translate the current batch
        if (char_count + text_len > max_chars) or (len(current_batch) >= batch_size):
            translated = client.translate(current_batch, target_language=target_language)
            results.extend([r['translatedText'] for r in translated])
            current_batch = []
            char_count = 0

        current_batch.append(text)
        char_count += text_len

    # Translate any leftover batch
    if current_batch:
        translated = client.translate(current_batch, target_language=target_language)
        results.extend([r['translatedText'] for r in translated])

    return results
reviews = reviews.sample(2000, random_state=42)
# Run translation ONCE for the entire column
translated_texts = batched_translate(
    reviews['comments'].tolist(),
    project_id="crypto-analyzer-458015-q2",
    target_language="en",
    max_chars=10000,
    batch_size=120
)

# Assign result back to DataFrame
reviews['translated_text'] = translated_texts

# %%
reviews.head()

# %%
from wordcloud import WordCloud, STOPWORDS
stopwords = set(STOPWORDS)
stopwords.update(['br'])

# %%
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    stopwords=stopwords,
    min_font_size=10
).generate(' '.join(reviews['translated_text'].dropna()))
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# %%
import spacy
import nltk
from nltk.corpus import stopwords as nltk_stopwords

# Download the spaCy model if not already present
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

stop_words = set(nltk_stopwords.words('english'))
def preprocess(texts):
    processed_texts = []

    for doc in nlp.pipe(texts, batch_size=1000):
        tokens = [token.lemma_.lower() for token in doc
                  if token.is_alpha and
                     token.lemma_.lower() not in stop_words and
                     len(token) > 2]
        processed_texts.append(tokens)

    return processed_texts

# %%

from gensim import corpora, models
text = preprocess(reviews['translated_text'].dropna().tolist())
dictionary = corpora.Dictionary(text)
corpus = [dictionary.doc2bow(doc) for doc in text]
lda_model = models.LdaModel(
    corpus,
    num_topics=5,
    id2word=dictionary,
    passes=10,
    random_state=42
)
lda_model.print_topics()

# %%
from gensim.models import CoherenceModel
import matplotlib.pyplot as plt

def find_optimal_k(dictionary, corpus, texts, k_range):
    from gensim.models import LdaModel

    coherence_scores = []
    for k in k_range:
        lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=k, random_state=42)
        coherence_model = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
        score = coherence_model.get_coherence()
        coherence_scores.append(score)
        print(f"Topics: {k}, Coherence: {score:.4f}")
    
    # Plot
    plt.plot(k_range, coherence_scores)
    plt.xlabel("Number of Topics")
    plt.ylabel("Coherence Score (c_v)")
    plt.title("Optimal Topic Count")
    plt.show()
    
    return coherence_scores

# Example:
# k_scores = find_optimal_k(dictionary, corpus, texts, range(5, 21))

# %%
find_optimal_k(dictionary, corpus, text, range(2, 11))

# %%
import numpy
print(numpy.__version__)


