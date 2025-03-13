#!/usr/bin/env python3
"""
Direct Test Script for Vertex AI Agent

This script tests the Vertex AI Agent directly using the Dialogflow CX API,
without requiring the Flask API server to be running.
"""

import os
import re
import json
import time
import csv
from datetime import datetime
from tqdm import tqdm
from google.oauth2 import service_account
from google.auth.transport.requests import Request as AuthRequest
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - hardcoded for direct testing
PROJECT_ID = 'heuristicsai'
LOCATION = 'global'  # Changed to global based on documentation
AGENT_ID = '8285e0d0-24ae-43e9-8491-b0bd99befc87'  # Updated agent ID
CREDENTIALS_FILE = '/Users/dionedge/dev/creds/heuristicsai-9ad7dd8375bf.json'

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

def ask_question_direct(question, session_id):
    """
    Ask a question directly to the Vertex AI Agent using Dialogflow CX API
    
    Args:
        question (str): The question to ask
        session_id (str): Session ID for continuous conversation
        
    Returns:
        str: The response text from the agent
    """
    try:
        # Check if credentials file exists
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")
            
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Refresh credentials
        auth_req = AuthRequest()
        credentials.refresh(auth_req)
        token = credentials.token
        
        # API URL for Dialogflow CX
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

def run_tests(questions, limit=5, output_file="direct_test_results.csv"):
    """
    Run tests using the direct API approach
    
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
            
            # Ask the question
            session_id = f"direct-test-{question_number}-{int(time.time())}"
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
    print(f"Testing Vertex AI Agent directly")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Credentials file: {CREDENTIALS_FILE}")
    
    # Extract questions from test file
    questions_file = "/Users/dionedge/dev/looker-vertex-agent/agent-api/tests/test_questions.md"
    print(f"Extracting questions from {questions_file}...")
    questions = extract_questions(questions_file)
    
    if not questions:
        print("No questions found in the file.")
        return 1
    
    print(f"Found {len(questions)} questions.")
    
    # Run tests with a small sample
    output_file = f"direct_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    limit = 5  # Test only 5 questions
    run_tests(questions, limit, output_file)
    
    return 0

if __name__ == "__main__":
    main()