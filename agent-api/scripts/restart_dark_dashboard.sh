#!/bin/bash

# Restart Dark Dashboard Script
# This script stops any running Streamlit processes, clears the cache, and starts the dark-themed dashboard

echo "Stopping any running Streamlit processes..."
pkill -f streamlit || true

echo "Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache

echo "Starting the dark-themed dashboard..."
python3 -m streamlit run dashboard_dark.py &

echo "Dashboard is running at http://localhost:8501" 