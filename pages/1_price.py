from app import load_data
from app import st, pd, px
import re
import os

# ------------------ LOAD DATA ------------------
@st.cache_data
def get_data():
    return load_data()

listings, detailed_listings, reviews, calendar, geo_json = get_data()

# ------------------ SIDEBAR ------------------
st.sidebar.markdown("### Host Price Trends")

# ------------------ TITLE ------------------
st.title("📈 Host Price Trends")

# ------------------ LOAD HOST FILES ------------------
top_hosts = listings['host_name'].value_counts().head(10).index.tolist()
dfs = {}

for host in top_hosts:
    safe_name = re.sub(r'\W+', '_', str(host))
    file_path = f"host_{safe_name}.csv"
    if os.path.exists(file_path):
        dfs[host] = pd.read_csv(file_path)

# ------------------ PLOT ------------------
if dfs:
    plot_df = pd.concat(dfs.values(), ignore_index=True)
    plot_df['date'] = pd.to_datetime(plot_df['date'], errors='coerce')
    plot_df = plot_df.dropna(subset=['date'])

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
        title="Average Weekly Price by Host"
    )
    fig.update_layout(xaxis_title='Date', yaxis_title='Price (£)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No host-specific CSV files found. Please ensure files like `host_Alice.csv` exist.")
