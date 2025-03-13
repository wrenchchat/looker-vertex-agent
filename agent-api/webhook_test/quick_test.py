#!/usr/bin/env python3
"""
Simple test script for Vertex AI Agent that tests a single question
"""
import os
import json
import requests
from datetime import datetime
import google.auth
import google.auth.transport.requests

# Set environment variables if not already set
os.environ['PROJECT_ID'] = os.environ.get('PROJECT_ID', 'heuristicsai')
os.environ['LOCATION'] = os.environ.get('LOCATION', 'global')
os.environ['VERTEX_AI_APP_ID'] = os.environ.get('VERTEX_AI_APP_ID', '8285e0d0-24ae-43e9-8491-b0bd99befc87')

# Sample question to test
TEST_QUESTION = "What are the best practices for data modeling in Looker?"

def get_access_token():
    """Get an OAuth 2.0 access token using the default credentials."""
    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

def test_question(question):
    """Test a single question with the Vertex AI Agent"""
    project_id = os.environ.get('PROJECT_ID')
    location = os.environ.get('LOCATION')
    agent_id = os.environ.get('VERTEX_AI_APP_ID')
    
    # Get access token for authentication
    access_token = get_access_token()
    
    # Prepare the API URL
    api_url = f"https://dialogflow.googleapis.com/v3/projects/{project_id}/locations/{location}/agents/{agent_id}/sessions/test-session-{datetime.now().timestamp()}:detectIntent"
    
    # Prepare the request payload
    payload = {
        "queryInput": {
            "text": {
                "text": question
            },
            "languageCode": "en"
        }
    }
    
    # Set headers with authentication
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting question: \"{question}\"\n")
    
    # Make the API call
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: API call failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    # Parse the response
    response_data = response.json()
    
    # Extract the response text
    response_text = "No response text found"
    if "queryResult" in response_data and "responseMessages" in response_data["queryResult"]:
        for msg in response_data["queryResult"]["responseMessages"]:
            if "text" in msg and "text" in msg["text"]:
                response_text = "\n".join(msg["text"]["text"])
                break
    
    return {
        "question": question,
        "response": response_text,
        "status_code": response.status_code
    }

if __name__ == "__main__":
    print("Testing Vertex AI Agent with a quick test...")
    
    # Make sure GOOGLE_APPLICATION_CREDENTIALS is set
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        print("Setting GOOGLE_APPLICATION_CREDENTIALS to default location...")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/dionedge/dev/creds/heuristicsai-9ad7dd8375bf.json'
    
    # Test the question
    result = test_question(TEST_QUESTION)
    
    if result:
        print("\n=== TEST RESULT ===")
        print(f"Question: {result['question']}")
        print(f"Status: {result['status_code']}")
        print("\nResponse:")
        print("="*50)
        print(result['response'])
        print("="*50) 