#!/usr/bin/env python3
"""
Vertex AI Agent API - Direct approach implementation

This Flask application provides an endpoint to send questions to a Vertex AI Agent 
and receive responses. It handles authentication, session management, and response parsing.
"""
import os
import json
import sys
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from google.auth.transport.requests import Request as AuthRequest
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

# Load environment variables from .env file if it exists
load_dotenv(os.path.join(project_root, '.env'))

app = Flask(__name__)

# Configuration - from environment variables
PROJECT_ID = os.environ.get('PROJECT_ID', 'heuristicsai')
LOCATION = os.environ.get('LOCATION', 'us-central1')
AGENT_ID = os.environ.get('AGENT_ID', 'fa0bd62b-3fc7-46c8-9d55-3a18d9812a70')
CREDENTIALS_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 
                                 '/Users/dionedge/dev/creds/heuristicsai-9ad7dd8375bf.json')

@app.route('/', methods=['GET'])
def index():
    """Simple index endpoint to check if the service is running."""
    return jsonify({
        'status': 'online',
        'service': 'Vertex AI Agent API',
        'version': '1.0.0',
        'usage': 'Send POST requests to /ask with a JSON body containing "question" field'
    })

@app.route('/ask', methods=['POST'])
def ask_agent():
    """
    Endpoint to ask a question to your Vertex AI Agent
    
    Expected POST body:
    {
        "question": "Your question here",
        "sessionId": "optional-session-id"  # Will be generated if not provided
    }
    """
    try:
        # Get request data
        data = request.json
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required parameter: question'
            }), 400
            
        question = data['question']
        session_id = data.get('sessionId', f"session-{datetime.now().timestamp()}")
        
        # Log the request
        print(f"Received question: {question}")
        print(f"Session ID: {session_id}")
        
        # Check if credentials file exists
        if not os.path.exists(CREDENTIALS_FILE):
            return jsonify({
                'error': f"Credentials file not found: {CREDENTIALS_FILE}"
            }), 500
            
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Refresh credentials
        auth_req = AuthRequest()
        credentials.refresh(auth_req)
        token = credentials.token
        
        # API URL for Dialogflow CX - using regional endpoint
        # For regional agents, use the region-specific endpoint
        api_url = f"https://{LOCATION}-dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/sessions/{session_id}:detectIntent"
        
        # Request payload
        payload = {
            "queryInput": {
                "text": {
                    "text": question
                },
                "languageCode": "en"
            }
        }
        
        # Headers with authentication
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"Sending request to: {api_url}")
        
        # Make the API call
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Check response
        if response.status_code != 200:
            return jsonify({
                'error': f"Agent API call failed with status code {response.status_code}",
                'details': response.text
            }), response.status_code
            
        # Parse response
        response_data = response.json()
        
        # Extract response text
        response_text = "No response from agent"
        if "queryResult" in response_data and "responseMessages" in response_data["queryResult"]:
            for msg in response_data["queryResult"]["responseMessages"]:
                if "text" in msg and "text" in msg["text"]:
                    response_text = "\n".join(msg["text"]["text"])
                    break
        
        # Return the response
        return jsonify({
            'question': question,
            'answer': response_text,
            'sessionId': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'error': f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8082))
    print(f"Starting Vertex AI Agent API on port {port}...")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Credentials file: {CREDENTIALS_FILE}")
    app.run(host='0.0.0.0', port=port, debug=True) 