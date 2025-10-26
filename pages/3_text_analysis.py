import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import plotly.express as px
import re

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="📝 Text Analysis",
    page_icon="📝",
    layout="wide"
)

# ----------------- LOAD DATA -----------------
@st.cache_data
def load_data():
    """Load datasets with proper error handling"""
    data_dir = Path("Data")
    
    if not data_dir.exists():
        st.error("❌ Data directory not found!")
        return None, None
    
    try:
        # Try to load translated reviews first, then fall back to regular reviews
        translated_path = data_dir / "translated_reviews.csv"
        reviews_path = data_dir / "reviews-2.csv"
        
        if translated_path.exists():
            reviews = pd.read_csv(translated_path)
            text_column = "translated_text"
        elif reviews_path.exists():
            reviews = pd.read_csv(reviews_path)
            text_column = "comments"
        else:
            st.error("❌ No review files found!")
            return None, None
        
        # Sample for performance
        if len(reviews) > 5000:
            reviews = reviews.sample(5000, random_state=42)
        
        return reviews, text_column
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None, None

reviews, text_column = load_data()

if reviews is None:
    st.stop()

# Filter out empty reviews
reviews = reviews.dropna(subset=[text_column])
reviews = reviews[reviews[text_column].str.len() > 10]  # Remove very short reviews

# ----------------- CUSTOM CSS -----------------
st.markdown("""
<style>
    .analysis-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF5A5F;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
st.sidebar.markdown("### 📝 Text Analysis Options")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis Type:",
    ["Basic Statistics", "Word Cloud", "Sentiment Analysis", "Common Phrases"]
)

# ----------------- TITLE -----------------
st.title("📝 Text Analysis Dashboard")
st.markdown("Analyze guest reviews and listing descriptions for insights")

# Display basic info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📝 Total Reviews", f"{len(reviews):,}")
with col2:
    avg_length = reviews[text_column].str.len().mean()
    st.metric("📏 Avg Review Length", f"{avg_length:.0f} chars")
with col3:
    st.metric("📊 Text Column", text_column.replace('_', ' ').title())

st.markdown("---")

# ----------------- BASIC STATISTICS -----------------
if analysis_type == "Basic Statistics":
    st.header("📊 Review Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Review length distribution
        try:
            import plotly.express as px
            PLOTLY_AVAILABLE = True
        except ImportError:
            PLOTLY_AVAILABLE = False
        
        review_lengths = reviews[text_column].str.len()
        
        if PLOTLY_AVAILABLE:
            fig_hist = px.histogram(
                x=review_lengths,
                nbins=50,
                title="Distribution of Review Lengths",
                labels={'x': 'Review Length (characters)', 'y': 'Count'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            # Fallback to matplotlib
            fig, ax = plt.subplots()
            ax.hist(review_lengths, bins=50, alpha=0.7)
            ax.set_xlabel('Review Length (characters)')
            ax.set_ylabel('Count')
            ax.set_title('Distribution of Review Lengths')
            st.pyplot(fig)
    
    with col2:
        # Word count distribution
        word_counts = reviews[text_column].str.split().str.len()
        fig_words = px.histogram(
            x=word_counts,
            nbins=50,
            title="Distribution of Word Counts",
            labels={'x': 'Word Count', 'y': 'Count'}
        )
        st.plotly_chart(fig_words, use_container_width=True)
    
    # Sample reviews
    st.subheader("📝 Sample Reviews")
    sample_reviews = reviews.sample(5)[text_column].tolist()
    for i, review in enumerate(sample_reviews, 1):
        with st.expander(f"Sample Review {i}"):
            st.write(review[:500] + "..." if len(review) > 500 else review)

# ----------------- WORD CLOUD -----------------
elif analysis_type == "Word Cloud":
    st.header("☁️ Word Cloud Analysis")
    
    try:
        from wordcloud import WordCloud, STOPWORDS
        
        # Combine all text
        all_text = ' '.join(reviews[text_column].astype(str))
        
        # Custom stopwords
        custom_stopwords = set(STOPWORDS)
        custom_stopwords.update(['stay', 'great', 'good', 'get', 'would', 'london', 'little', 'really', 'well', 'one', 'place', 'time', 'nice'])
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            stopwords=custom_stopwords,
            max_words=100,
            colormap='viridis'
        ).generate(all_text)
        
        # Display
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        
        # Most common words
        st.subheader("🔤 Most Common Words")
        word_freq = wordcloud.words_
        top_words = list(word_freq.items())[:20]
        
        words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
        fig_bar = px.bar(
            words_df,
            x='Word',
            y='Frequency',
            title="Top 20 Most Frequent Words"
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    except ImportError:
        st.error("❌ WordCloud library not available. Please install it with: pip install wordcloud")

# ----------------- SENTIMENT ANALYSIS -----------------
elif analysis_type == "Sentiment Analysis":
    st.header("😊 Sentiment Analysis")
    
    try:
        from textblob import TextBlob
        
        # Calculate sentiment for a sample of reviews
        sample_size = min(1000, len(reviews))
        sample_reviews = reviews.sample(sample_size)[text_column]
        
        with st.spinner("Analyzing sentiment..."):
            sentiments = []
            for review in sample_reviews:
                blob = TextBlob(str(review))
                sentiments.append({
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                })
        
        sentiment_df = pd.DataFrame(sentiments)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment distribution
            fig_sentiment = px.histogram(
                sentiment_df,
                x='polarity',
                nbins=30,
                title="Sentiment Polarity Distribution",
                labels={'polarity': 'Polarity (-1: Negative, 1: Positive)'}
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            # Subjectivity distribution
            fig_subj = px.histogram(
                sentiment_df,
                x='subjectivity',
                nbins=30,
                title="Subjectivity Distribution",
                labels={'subjectivity': 'Subjectivity (0: Objective, 1: Subjective)'}
            )
            st.plotly_chart(fig_subj, use_container_width=True)
        
        # Sentiment categories
        positive = len(sentiment_df[sentiment_df['polarity'] > 0.1])
        negative = len(sentiment_df[sentiment_df['polarity'] < -0.1])
        neutral = len(sentiment_df) - positive - negative
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Positive Reviews", f"{positive} ({positive/len(sentiment_df)*100:.1f}%)")
        with col2:
            st.metric("😐 Neutral Reviews", f"{neutral} ({neutral/len(sentiment_df)*100:.1f}%)")
        with col3:
            st.metric("😞 Negative Reviews", f"{negative} ({negative/len(sentiment_df)*100:.1f}%)")
        
    except ImportError:
        st.error("❌ TextBlob library not available. Please install it with: pip install textblob")

# ----------------- COMMON PHRASES -----------------
elif analysis_type == "Common Phrases":
    st.header("🔍 Common Phrases Analysis")
    
    # Simple n-gram analysis
    from collections import Counter
    import re
    
    # Clean and tokenize text
    all_text = ' '.join(reviews[text_column].astype(str).str.lower())
    # Remove special characters and extra spaces
    clean_text = re.sub(r'[^a-zA-Z\s]', '', all_text)
    words = clean_text.split()
    
    # Remove common stop words
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'were', 'are', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Most common single words
        st.subheader("🔤 Most Common Words")
        word_counts = Counter(filtered_words)
        top_words = word_counts.most_common(20)
        
        words_df = pd.DataFrame(top_words, columns=['Word', 'Count'])
        fig_words = px.bar(
            words_df,
            x='Word',
            y='Count',
            title="Top 20 Single Words"
        )
        fig_words.update_xaxes(tickangle=45)
        st.plotly_chart(fig_words, use_container_width=True)
    
    with col2:
        # Most common bigrams
        st.subheader("👥 Most Common Word Pairs")
        bigrams = [f"{filtered_words[i]} {filtered_words[i+1]}" 
                  for i in range(len(filtered_words)-1)]
        bigram_counts = Counter(bigrams)
        top_bigrams = bigram_counts.most_common(20)
        
        bigrams_df = pd.DataFrame(top_bigrams, columns=['Bigram', 'Count'])
        fig_bigrams = px.bar(
            bigrams_df,
            x='Bigram',
            y='Count',
            title="Top 20 Word Pairs"
        )
        fig_bigrams.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bigrams, use_container_width=True)
    
    # Show some example phrases
    st.subheader("📝 Example Phrases")
    example_phrases = [bigram for bigram, count in top_bigrams[:10]]
    st.write("Most common phrases found in reviews:")
    for phrase in example_phrases:
        st.write(f"• {phrase}")

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown("*Text analysis completed. Use the sidebar to explore different analysis types.*")
