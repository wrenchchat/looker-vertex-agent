#!/bin/bash

# Test the Vertex AI Agent API with curl

API_URL="http://localhost:8082/ask"
QUESTION="What are the best practices for data modeling in Looker?"
SESSION_ID="test-session-$(date +%s)"

echo "Testing Vertex AI Agent API"
echo "URL: $API_URL"
echo "Question: $QUESTION"
echo "Session ID: $SESSION_ID"
echo

# Send the request using curl
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"$QUESTION\",
    \"sessionId\": \"$SESSION_ID\"
  }")

# Check if curl was successful
if [ $? -ne 0 ]; then
  echo "Error: Failed to connect to the API server"
  echo "Make sure the server is running on http://localhost:8082"
  exit 1
fi

# Display the response
echo "Response from API:"
echo "----------------------------------------"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo "----------------------------------------"

# Extract the answer if possible
if command -v python3 &>/dev/null; then
  ANSWER=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('answer', 'No answer found'))" 2>/dev/null)
  if [ -n "$ANSWER" ] && [ "$ANSWER" != "No answer found" ]; then
    echo
    echo "Answer:"
    echo "----------------------------------------"
    echo "$ANSWER"
    echo "----------------------------------------"
  fi
fi 