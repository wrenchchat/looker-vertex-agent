#!/bin/bash

# Setup script for GCP authentication

echo "==== Google Cloud Storage Authentication Setup ===="
echo ""
echo "This script will help you set up authentication for Google Cloud Storage."
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: Google Cloud SDK (gcloud) is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in
echo "Checking if you're logged in to Google Cloud..."
ACCOUNT=$(gcloud config get-value account 2>/dev/null)

if [ -z "$ACCOUNT" ] || [ "$ACCOUNT" = "(unset)" ]; then
    echo "You're not logged in. Let's log in now."
    gcloud auth login
else
    echo "You're currently logged in as: $ACCOUNT"
    read -p "Would you like to continue with this account? (y/n): " CONTINUE
    
    if [[ $CONTINUE != "y" && $CONTINUE != "Y" ]]; then
        echo "Let's log in with a different account."
        gcloud auth login
    fi
fi

# Set the default project
echo ""
echo "Now, let's set the default project."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -n "$CURRENT_PROJECT" ] && [ "$CURRENT_PROJECT" != "(unset)" ]; then
    echo "Current project is set to: $CURRENT_PROJECT"
    read -p "Would you like to use this project? (y/n): " USE_CURRENT
    
    if [[ $USE_CURRENT != "y" && $USE_CURRENT != "Y" ]]; then
        read -p "Enter your Google Cloud project ID: " PROJECT_ID
        gcloud config set project $PROJECT_ID
    fi
else
    read -p "Enter your Google Cloud project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

# Create application credentials for local development
echo ""
echo "Setting up application default credentials for local development..."
gcloud auth application-default login

echo ""
echo "Authentication setup complete!"
echo "You can now run the upload script with: npm run upload"
echo ""

# Make the script executable
chmod +x "$0" 