# 🏠 Airbnb Data Dashboard

Simple Streamlit dashboard for analyzing Airbnb listings data from London.

## � Datak Source

Data downloaded from: [Inside Airbnb](https://insideairbnb.com/get-the-data.html)
- **City**: London, United Kingdom
- **Dataset**: Listings, Reviews, and Calendar data

## 🚀 Quick Start

### 1. Create Data Directory
```bash
mkdir Data
# Add your CSV files to the Data directory
```

Required files:
- `Data/listings.csv`
- `Data/listings-2.csv`
- `Data/reviews-2.csv`
- `Data/calendar.csv`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
python run.py
```

Or directly:
```bash
streamlit run app_simple.py
```

## � Feratures

- **Dataset Overview**: View metrics and data information
- **Price Analysis**: Distribution, statistics, and neighborhood comparisons
- **Basic Charts**: Room types, top hosts, visualizations
- **Data Explorer**: Interactive column analysis and filtering

## � Prgoject Structure
```
Airbnb-1/
├── app_simple.py         # Main dashboard (simple version)
├── Data/                 # Your CSV files go here
├── requirements.txt      # Dependencies
├── run.py               # Simple launcher
└── README.md            # This file
```

## 💡 Notes

- Uses matplotlib for charts (no dependency conflicts)
- Works with any pandas version
- Automatically samples large datasets for performance
- Clean, user-friendly interface

## 📖 About the Data

This dashboard analyzes Airbnb data from London, sourced from [Inside Airbnb](https://insideairbnb.com/), an independent, non-commercial project that provides data about Airbnb's impact on residential communities.

**Dataset includes:**
- Detailed listings information (property types, prices, locations)
- Guest reviews and ratings
- Calendar availability and pricing
- Host information and statistics

---
*Built with Streamlit | Data from Inside Airbnb*