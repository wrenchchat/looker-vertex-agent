#!/bin/bash

# Default values - modify these if needed
PROJECT_ID=${PROJECT_ID:-"heuristicsai"}
LOCATION=${LOCATION:-"global"}
AGENT_ID=${AGENT_ID:-"8285e0d0-24ae-43e9-8491-b0bd99befc87"}
TEST_QUESTION="What are the best practices for data modeling in Looker?"

echo "Testing Vertex AI Agent with curl..."
echo "PROJECT_ID: $PROJECT_ID"
echo "LOCATION: $LOCATION"
echo "AGENT_ID: $AGENT_ID"
echo "QUESTION: $TEST_QUESTION"

# Get authentication token
echo "Getting authentication token..."
TOKEN=$(gcloud auth print-access-token)

if [ -z "$TOKEN" ]; then
  echo "Error: Failed to get authentication token. Are you logged in with gcloud?"
  exit 1
fi

# Create session ID (using timestamp for uniqueness)
SESSION_ID="test-session-$(date +%s)"

# API URL
API_URL="https://dialogflow.googleapis.com/v3/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/sessions/${SESSION_ID}:detectIntent"

echo "Sending request to: $API_URL"

# Send the request
RESPONSE=$(curl -s -X POST $API_URL \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"queryInput\": {
      \"text\": {
        \"text\": \"$TEST_QUESTION\"
      },
      \"languageCode\": \"en\"
    }
  }")

# Pretty print the response
echo "Response:"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"

# Extract just the text response if jq is available
if command -v jq &> /dev/null && [[ $RESPONSE == *"responseMessages"* ]]; then
  echo -e "\nExtracted response text:"
  echo "$RESPONSE" | jq -r '.queryResult.responseMessages[] | select(.text != null) | .text.text[]' 2>/dev/null
fi 