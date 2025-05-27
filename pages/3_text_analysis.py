import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from gensim import corpora, models
from gensim.models import CoherenceModel
import spacy
from nltk.corpus import stopwords as nltk_stopwords
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis
import os
import re

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Text Analysis",
    page_icon="📊",
    layout="wide"
)
st.sidebar.header('Text Analysis')

# ----------------- LOAD DATA -----------------
@st.cache_data
def load_reviews():
    return pd.read_csv("translated_reviews.csv")

reviews = load_reviews().dropna(subset=["translated_text"])

# ----------------- TEXT PREPROCESSING -----------------
@st.cache_data
def preprocess_text(texts):
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    stop_words = set(nltk_stopwords.words("english"))
    stop_words.update(['stay', 'great', 'good', 'get', 'would', 'london', 'little', 'really', 'well', 'one'])

    processed_texts = []
    for doc in nlp.pipe(texts, batch_size=1000):
        tokens = [token.lemma_.lower() for token in doc
                  if token.is_alpha and
                     token.lemma_.lower() not in stop_words and
                     len(token) > 2]
        processed_texts.append(tokens)
    return processed_texts

with st.spinner("Preprocessing text..."):
    texts = preprocess_text(reviews['translated_text'].tolist())

# ----------------- DICTIONARY & CORPUS -----------------
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(doc) for doc in texts]

# ----------------- WORD CLOUD -----------------
st.subheader("☁️ Word Cloud")
wordcloud = WordCloud(
    width=1000,
    height=400,
    background_color='white',
    stopwords=STOPWORDS
).generate(' '.join([' '.join(doc) for doc in texts]))

fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis("off")
st.pyplot(fig_wc)

# ----------------- COHERENCE SCORE PLOT -----------------
st.subheader("📈 Coherence Score vs Number of Topics")
@st.cache_data
def compute_coherence(_dictionary, _corpus, _texts, k_range):
    scores = []
    for k in k_range:
        lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=k, random_state=42)
        cm = CoherenceModel(model=lda, texts=_texts, dictionary=_dictionary, coherence='c_v')
        scores.append(cm.get_coherence())
    return scores

k_range = range(2, 11)
coherence_scores = compute_coherence(dictionary, corpus, texts, k_range)
fig_coh, ax_coh = plt.subplots()
ax_coh.plot(k_range, coherence_scores, marker='o')
ax_coh.set_xlabel("Number of Topics")
ax_coh.set_ylabel("Coherence Score (c_v)")
ax_coh.set_title("Optimal Number of Topics")
st.pyplot(fig_coh)

# ----------------- LDA VISUALIZATION -----------------
st.subheader("🔍 LDA Interactive Visualization")

@st.cache_resource
def prepare_lda_html(dictionary, corpus, texts, num_topics):
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, random_state=42)
    vis_data = gensimvis.prepare(lda, corpus, dictionary)
    output_path = "lda_visualization.html"
    pyLDAvis.save_html(vis_data, output_path)
    return output_path

html_path = prepare_lda_html(dictionary, corpus, texts, num_topics=3)
st.markdown(f"[Click here to view LDA interactive visualization]({html_path})", unsafe_allow_html=True)
