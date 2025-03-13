#!/bin/bash

# Script to check permissions for the service account

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Loaded environment variables from .env"
else
  echo "Warning: .env file not found"
fi

# Check if jq is installed
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed."
  echo "Install with: brew install jq"
  exit 1
fi

# Function to extract the service account email from credentials file
get_service_account_email() {
  local creds_file="$1"
  if [ -f "$creds_file" ]; then
    jq -r '.client_email' "$creds_file" 2>/dev/null
  else
    echo ""
  fi
}

# Function to check permissions
check_permissions() {
  local project_id="$1"
  local service_account_email="$2"
  
  echo "Checking IAM permissions for $service_account_email in project $project_id..."
  
  # This requires gcloud to be authenticated
  gcloud projects get-iam-policy "$project_id" --format=json 2>/dev/null | \
    jq --arg email "serviceAccount:$service_account_email" '.bindings[] | select(.members[] | contains($email)) | {role: .role, members: .members}' 2>/dev/null
}

# Get credentials file path from env var or use default
CREDS_FILE="${GOOGLE_APPLICATION_CREDENTIALS:-""}"

if [ -z "$CREDS_FILE" ]; then
  echo "Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set."
  echo "Please set it in the .env file or export it in your shell."
  exit 1
fi

echo "Using credentials file: $CREDS_FILE"

# Extract service account email
SERVICE_ACCOUNT_EMAIL=$(get_service_account_email "$CREDS_FILE")

if [ -z "$SERVICE_ACCOUNT_EMAIL" ]; then
  echo "Error: Could not extract service account email from credentials file."
  echo "Check that the file exists and is a valid service account key file."
  exit 1
fi

echo "Service account email: $SERVICE_ACCOUNT_EMAIL"

# Extract project ID from env var or use default
PROJECT_ID="${PROJECT_ID:-"heuristicsai"}"

echo "Project ID: $PROJECT_ID"
echo

# Check current permissions
echo "Current IAM permissions:"
echo "----------------------------------------"
PERMISSIONS=$(check_permissions "$PROJECT_ID" "$SERVICE_ACCOUNT_EMAIL")

if [ -z "$PERMISSIONS" ]; then
  echo "No permissions found for this service account in the project."
  echo "This might be because:"
  echo "1. The service account doesn't have any roles assigned"
  echo "2. You don't have permission to view IAM policies"
  echo "3. gcloud is not authenticated or configured correctly"
else
  echo "$PERMISSIONS" | jq '.'
fi
echo "----------------------------------------"

# Check for specific required permissions
echo
echo "Required roles for Dialogflow CX API:"
echo "----------------------------------------"
echo "1. roles/dialogflow.client (Dialogflow API Client)"
echo "2. roles/dialogflow.admin (Dialogflow API Admin) - more comprehensive"
echo "3. roles/aiplatform.user (Vertex AI User)"
echo "----------------------------------------"

echo
echo "To add these roles, run the following commands:"
echo "----------------------------------------"
echo "gcloud projects add-iam-policy-binding $PROJECT_ID \\"
echo "  --member=\"serviceAccount:$SERVICE_ACCOUNT_EMAIL\" \\"
echo "  --role=\"roles/dialogflow.client\""
echo
echo "gcloud projects add-iam-policy-binding $PROJECT_ID \\"
echo "  --member=\"serviceAccount:$SERVICE_ACCOUNT_EMAIL\" \\"
echo "  --role=\"roles/aiplatform.user\""
echo "----------------------------------------"

echo
echo "After adding permissions, it may take a few minutes for them to propagate."
echo "Then run the test script again to check if the issue is resolved:"
echo "----------------------------------------"
echo "./test.sh"
echo "----------------------------------------" 