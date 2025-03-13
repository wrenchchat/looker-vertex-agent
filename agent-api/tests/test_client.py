#!/usr/bin/env python3
"""
Test client for the Vertex AI Agent API.
This script sends a question to the API and displays the response.
"""

import argparse
import json
import requests
import sys
import time
from datetime import datetime

def ask_question(question, session_id=None, api_url="http://localhost:8082/ask"):
    """
    Send a question to the Vertex AI Agent API.
    
    Args:
        question (str): The question to ask
        session_id (str, optional): Session ID for continuous conversation
        api_url (str, optional): URL of the API endpoint
        
    Returns:
        dict: The API response as a dictionary
    """
    if not session_id:
        session_id = f"test-session-{time.time()}"
        
    payload = {
        "question": question,
        "sessionId": session_id
    }
    
    print(f"\nSending question to {api_url}:")
    print(f'Question: "{question}"')
    print(f"Session ID: {session_id}")
    
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None

def main():
    """Main function to parse arguments and call the API."""
    parser = argparse.ArgumentParser(description="Test client for Vertex AI Agent API")
    parser.add_argument("--question", "-q", type=str, 
                        default="What are the best practices for data modeling in Looker?",
                        help="Question to ask the agent")
    parser.add_argument("--session", "-s", type=str, 
                        help="Session ID for continuous conversation")
    parser.add_argument("--url", "-u", type=str, 
                        default="http://localhost:8082/ask",
                        help="API endpoint URL")
    
    args = parser.parse_args()
    
    # Send the question to the API
    result = ask_question(args.question, args.session, args.url)
    
    # Display the result
    if result:
        print("\nResponse from API:")
        print("----------------------------------------")
        print(f"Question: {result.get('question', 'N/A')}")
        print(f"Answer: {result.get('answer', 'No answer provided')}")
        print(f"Session ID: {result.get('sessionId', 'N/A')}")
        print(f"Timestamp: {result.get('timestamp', 'N/A')}")
        print("----------------------------------------")
        
        # Return success
        return 0
    else:
        # Return error
        return 1

if __name__ == "__main__":
    sys.exit(main()) 