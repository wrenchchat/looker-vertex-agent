#!/usr/bin/env python3
"""
Test script for Vertex AI Conversation API
"""
import os
import sys
import json
import requests
from datetime import datetime
import google.auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request as AuthRequest

# Configuration
PROJECT_ID = os.environ.get('PROJECT_ID', 'heuristicsai')
LOCATION = os.environ.get('LOCATION', 'us-central1')  # Use a supported location
AGENT_ID = os.environ.get('AGENT_ID', '8285e0d0-24ae-43e9-8491-b0bd99befc87')
CREDENTIALS_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 
                                  '/Users/dionedge/dev/creds/heuristicsai-9ad7dd8375bf.json')

# Sample test question
TEST_QUESTION = "What are the best practices for data modeling in Looker?"

def test_vertex_conversation():
    """Test using Vertex AI Conversation API"""
    try:
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
        
        # API URL for Vertex AI Conversation
        api_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/chat-bison:predict"
        
        # Prepare the request payload
        payload = {
            "instances": [
                {
                    "context": "You are a Looker and data analytics expert. Answer questions about Looker and data modeling.",
                    "messages": [
                        {"author": "user", "content": TEST_QUESTION}
                    ]
                }
            ],
            "parameters": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Set headers with authentication
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\nSending request to Vertex AI Conversation API...")
        print(f"URL: {api_url}")
        print(f"Question: {TEST_QUESTION}\n")
        
        # Make the API call
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Check the response
        if response.status_code != 200:
            print(f"Error: API call failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Parse the response
        response_data = response.json()
        
        # Print the full response for debugging
        print("\nFull API Response:")
        print(json.dumps(response_data, indent=2))
        
        # Extract and print the response content
        if 'predictions' in response_data and len(response_data['predictions']) > 0:
            if 'candidates' in response_data['predictions'][0]:
                for candidate in response_data['predictions'][0]['candidates']:
                    if 'content' in candidate:
                        print("\n=== RESPONSE ===")
                        print("="*50)
                        print(candidate['content'])
                        print("="*50)
                        break
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Vertex AI Conversation API...")
    test_vertex_conversation() 