#!/bin/bash

# Add the Python path where streamlit is installed
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# Run the dashboard
echo "Starting Vertex AI Agent Dashboard..."
streamlit run dashboard.py 