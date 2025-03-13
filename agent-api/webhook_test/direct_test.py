#!/usr/bin/env python3
"""
Direct test script that uses the service account key file for Vertex AI Agent testing
"""
import os
import sys
import json
import requests
from datetime import datetime

# Configuration (uses environment variables or defaults)
PROJECT_ID = os.environ.get('PROJECT_ID', 'heuristicsai')
LOCATION = os.environ.get('LOCATION', 'global')
AGENT_ID = os.environ.get('AGENT_ID', '8285e0d0-24ae-43e9-8491-b0bd99befc87')
CREDENTIALS_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 
                                  '/Users/dionedge/dev/creds/heuristicsai-9ad7dd8375bf.json')

# Test question
TEST_QUESTION = "What are the best practices for data modeling in Looker?"

def test_with_vertexai_api():
    """Test using the Vertex AI API directly"""
    try:
        from google.cloud import aiplatform
        
        # Initialize the SDK
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        
        # Create a publisher client
        client = aiplatform.Publisher.create()
        
        # Create a session
        session_id = f"test-session-{datetime.now().timestamp()}"
        
        print(f"Project: {PROJECT_ID}")
        print(f"Location: {LOCATION}")
        print(f"Agent ID: {AGENT_ID}")
        print(f"Session: {session_id}")
        print(f"Question: {TEST_QUESTION}")
        
        # Send the request
        response = client.detect_intent(
            agent=AGENT_ID,
            session=session_id,
            text=TEST_QUESTION
        )
        
        print("\nResponse from Vertex AI:")
        print(response)
        
    except Exception as e:
        print(f"Error using Vertex AI API: {e}")
        print("Falling back to REST API...")
        test_with_rest_api()

def test_with_rest_api():
    """Test using direct REST API calls"""
    try:
        # Try to import the Google Auth libraries
        import google.auth
        from google.auth.transport.requests import Request as AuthRequest
        from google.oauth2 import service_account
        
        print(f"Using credentials file: {CREDENTIALS_FILE}")
        
        # Check if credentials file exists
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"Error: Credentials file {CREDENTIALS_FILE} not found!")
            sys.exit(1)
        
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Refresh credentials
        auth_req = AuthRequest()
        credentials.refresh(auth_req)
        token = credentials.token
        
        # Create a unique session ID
        session_id = f"test-session-{datetime.now().timestamp()}"
        
        # Build the API URL
        api_url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/sessions/{session_id}:detectIntent"
        
        # Prepare the request payload
        payload = {
            "queryInput": {
                "text": {
                    "text": TEST_QUESTION
                },
                "languageCode": "en"
            }
        }
        
        # Set headers with authentication
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\nSending request to: {api_url}")
        
        # Make the API call
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Check the response
        if response.status_code != 200:
            print(f"Error: API call failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Parse the response
        response_data = response.json()
        
        # Extract the response text
        response_text = "No response text found"
        if "queryResult" in response_data and "responseMessages" in response_data["queryResult"]:
            for msg in response_data["queryResult"]["responseMessages"]:
                if "text" in msg and "text" in msg["text"]:
                    response_text = "\n".join(msg["text"]["text"])
                    break
        
        # Print the results
        print("\n=== TEST RESULT ===")
        print(f"Status: {response.status_code}")
        print("\nResponse:")
        print("="*50)
        print(response_text)
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Vertex AI Agent...")
    
    # First try with Vertex AI API
    try:
        import google.cloud.aiplatform
        test_with_vertexai_api()
    except ImportError:
        print("Vertex AI API not available, using REST API...")
        test_with_rest_api() 