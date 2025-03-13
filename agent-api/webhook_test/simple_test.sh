#!/bin/bash

# Simple script to test the Vertex AI Agent using direct web request

# Output a summary of what we're about to do
echo "===== Testing Vertex AI Agent with a direct web request ====="
echo

# Define question 
QUESTION="What are the best practices for data modeling in Looker?"

# Create a timestamp session ID to make sure each request is unique
SESSION_ID="test-session-$(date +%s)"

# Set the endpoint URL - use http://localhost:8080 for local testing with ngrok
SERVER_URL="https://wrench.chat/ask"

echo "Sending test question to: $SERVER_URL"
echo "Question: $QUESTION"
echo

# Make the request to the endpoint
RESPONSE=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"$QUESTION\",
    \"sessionId\": \"$SESSION_ID\"
  }")

# Display the response
echo "Response from server:"
echo "----------------------------------------"
echo "$RESPONSE" | jq 2>/dev/null || echo "$RESPONSE"
echo "----------------------------------------"

# Extract just the answer text if possible
if command -v jq &>/dev/null; then
  ANSWER=$(echo "$RESPONSE" | jq -r '.answer // .response // .' 2>/dev/null)
  if [[ "$ANSWER" != "null" && "$ANSWER" != "$RESPONSE" ]]; then
    echo
    echo "Extracted answer:"
    echo "----------------------------------------"
    echo "$ANSWER"
    echo "----------------------------------------"
  fi
fi

echo
echo "===== Test complete =====" 