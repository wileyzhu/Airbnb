# 🏠 Airbnb Dashboard - Setup Guide

## ✅ Recommended: Fresh Environment Setup

The cleanest way to run this dashboard is with a fresh conda environment:

### Step 1: Create New Environment
```bash
conda create -n airbnb python=3.9 -y
conda activate airbnb
```

### Step 2: Install Core Packages
```bash
pip install streamlit pandas matplotlib
```

### Step 3: Create Data Directory
```bash
mkdir Data
# Copy your CSV files into the Data directory
```

### Step 4: Run the Dashboard
```bash
streamlit run app_simple.py
```

## 📁 Required Data Files

Place these files in the `Data/` directory:
- `listings.csv`
- `listings-2.csv`
- `reviews-2.csv`
- `calendar.csv`

## 🎯 What You Get

The simple dashboard (`app_simple.py`) includes:
- ✅ Dataset overview with metrics
- ✅ Price analysis and distributions
- ✅ Basic charts (room types, hosts)
- ✅ Data explorer with filtering
- ✅ No dependency conflicts!

## 🚀 Quick Commands

```bash
# Activate environment
conda activate airbnb

# Run dashboard
streamlit run app_simple.py

# Or use the launcher
python run.py
```

## 💡 Troubleshooting

If you get import errors:
```bash
# Deactivate current environment
conda deactivate

# Remove old environment
conda env remove -n airbnb_dashboard

# Start fresh with the steps above
```

## 📝 Notes

- The simple version uses only matplotlib (no plotly/xarray conflicts)
- Works with any recent pandas version
- Automatically handles large datasets
- Clean, fast, and reliable!