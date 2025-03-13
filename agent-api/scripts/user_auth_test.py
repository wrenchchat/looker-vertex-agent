#!/usr/bin/env python3
"""
Direct Test Script for Vertex AI Agent using User Authentication

This script tests the Vertex AI Agent directly using the user's gcloud authentication,
without requiring the Flask API server to be running.
"""

import os
import re
import json
import time
import csv
import subprocess
from datetime import datetime
from tqdm import tqdm
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - hardcoded for direct testing
PROJECT_ID = 'heuristicsai'
LOCATION = 'us-central1'  # Changed to us-central1 as requested
AGENT_ID = 'fa0bd62b-3fc7-46c8-9d55-3a18d9812a70'

def extract_questions(file_path):
    """
    Extract questions from the markdown file.
    Returns a list of tuples: (question, category, difficulty)
    """
    questions = []
    current_category = ""
    current_difficulty = ""
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find categories and difficulties
    sections = re.split(r'\*\*([^*]+)\*\*\s*\n\s*\*\*([^*]+)\*\*', content)
    
    # Process sections
    for i in range(1, len(sections), 3):
        if i+2 <= len(sections):
            category = sections[i].strip()
            difficulty = sections[i+1].strip()
            section_content = sections[i+2]
            
            # Extract numbered questions
            numbered_questions = re.findall(r'\d+\.\s+(.*?)\n', section_content)
            
            for question in numbered_questions:
                questions.append((question.strip(), category, difficulty))
    
    return questions

def get_access_token():
    """
    Get an access token using the user's gcloud authentication
    """
    try:
        # Run gcloud command to get access token
        result = subprocess.run(
            ['gcloud', 'auth', 'print-access-token'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        # Return the token (strip whitespace)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting access token: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None

def ask_question_direct(question, session_id, location=None):
    """
    Ask a question directly to the Vertex AI Agent using Dialogflow CX API
    
    Args:
        question (str): The question to ask
        session_id (str): Session ID for continuous conversation
        location (str): Optional location override
        
    Returns:
        str: The response text from the agent
    """
    try:
        # Get access token using gcloud CLI
        token = get_access_token()
        if not token:
            return "Failed to get access token"
        
        # Use provided location or default
        loc = location or LOCATION
        
        # API URL for Dialogflow CX
        api_url = f"https://{loc}-dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{loc}/agents/{AGENT_ID}/sessions/{session_id}:detectIntent"
        
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
        
        print(f"Trying with location: {loc}")
        print(f"API URL: {api_url}")
        
        # Make the API call
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        # Check response
        if response.status_code != 200:
            error_msg = f"Agent API call failed with status code {response.status_code}: {response.text}"
            print(error_msg)
            return error_msg
            
        # Parse response
        response_data = response.json()
        
        # Extract response text
        response_text = "No response from agent"
        if "queryResult" in response_data and "responseMessages" in response_data["queryResult"]:
            for msg in response_data["queryResult"]["responseMessages"]:
                if "text" in msg and "text" in msg["text"]:
                    response_text = "\n".join(msg["text"]["text"])
                    break
        
        return response_text
    
    except Exception as e:
        error_msg = f"Error sending request: {str(e)}"
        print(error_msg)
        return error_msg

def run_tests(questions, limit=5, output_file="user_auth_test_results.csv"):
    """
    Run tests using the direct API approach with user authentication
    
    Args:
        questions: List of (question, category, difficulty) tuples
        limit: Maximum number of questions to test
        output_file: CSV file to save results
    """
    # Prepare CSV file
    fieldnames = ['question_number', 'question', 'category', 'difficulty', 
                 'answer', 'session_id', 'timestamp', 'response_time_ms']
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process questions
        num_questions = min(limit, len(questions)) if limit > 0 else len(questions)
        
        for i in tqdm(range(num_questions), desc="Testing questions"):
            question, category, difficulty = questions[i]
            question_number = i + 1
            
            print(f"\nQuestion {question_number}: {question}")
            print(f"Category: {category}, Difficulty: {difficulty}")
            
            # Use the specified location (now defaulted to us-central1)
            session_id = f"user-auth-test-{question_number}-{int(time.time())}"
            start_time = time.time()
            answer = ask_question_direct(question, session_id)
                
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            print(f"Answer: {answer[:100]}..." if len(answer) > 100 else f"Answer: {answer}")
            print(f"Response time: {response_time_ms} ms")
            
            # Write to CSV
            writer.writerow({
                'question_number': question_number,
                'question': question,
                'category': category,
                'difficulty': difficulty,
                'answer': answer,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'response_time_ms': response_time_ms
            })
            csvfile.flush()  # Ensure data is written immediately
            
            # Add a delay between questions
            time.sleep(1)
    
    print(f"\nResults saved to {output_file}")

def main():
    """Main function to run the test questions."""
    print(f"Testing Vertex AI Agent directly (using user authentication)")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Agent ID: {AGENT_ID}")
    
    # Test access token
    token = get_access_token()
    if not token:
        print("Failed to get access token. Make sure you're logged in with 'gcloud auth login'")
        return 1
    print("Successfully got access token")
    
    # Extract questions from test file
    questions_file = "/Users/dionedge/dev/looker-vertex-agent/agent-api/tests/test_questions.md"
    print(f"Extracting questions from {questions_file}...")
    questions = extract_questions(questions_file)
    
    if not questions:
        print("No questions found in the file.")
        return 1
    
    print(f"Found {len(questions)} questions.")
    
    # Run tests with a small sample
    output_file = f"user_auth_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    limit = 5  # Test only 5 questions
    run_tests(questions, limit, output_file)
    
    return 0

if __name__ == "__main__":
    main()