#!/usr/bin/env python3
"""Simple launcher for Airbnb Dashboard"""

import subprocess
import sys
import os

def main():
    print("🏠 Starting Airbnb Dashboard...")
    
    # Check if Data directory exists
    if not os.path.exists("Data"):
        print("\n⚠️  Warning: Data directory not found")
        print("Create a 'Data' folder with your CSV files:")
        print("  - listings.csv")
        print("  - listings-2.csv")
        print("  - reviews-2.csv")
        print("  - calendar.csv\n")
    
    # Run the simple version (no dependency issues)
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_simple.py"])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
