#!/usr/bin/env python3
"""
Test using service account credentials 

This script tests the Vertex AI Agent using service account credentials.
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
LOCATION = 'us-central1'
AGENT_ID = 'fa0bd62b-3fc7-46c8-9d55-3a18d9812a70'
CREDENTIALS_FILE = '/Users/dionedge/dev/creds/heuristicsai-9ad7dd8375bf.json'

def extract_questions(file_path, limit=None, diverse=False):
    """
    Extract questions from the markdown file.
    Returns a list of tuples: (question, category, difficulty)
    
    Args:
        file_path: Path to the markdown file
        limit: Maximum number of questions to extract (None for all)
        diverse: If True, extract questions from different categories
    """
    questions = []
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find categories and difficulties
    sections = re.split(r'\*\*([^*]+)\*\*\s*\n\s*\*\*([^*]+)\*\*', content)
    
    if not diverse:
        # Extract all questions or up to limit
        count = 0
        for i in range(1, len(sections), 3):
            if i+2 <= len(sections):
                category = sections[i].strip()
                difficulty = sections[i+1].strip()
                section_content = sections[i+2]
                
                # Extract numbered questions
                numbered_questions = re.findall(r'\d+\.\s+(.*?)\n', section_content)
                
                for question in numbered_questions:
                    questions.append((question.strip(), category, difficulty))
                    count += 1
                    if limit is not None and count >= limit:
                        return questions
    else:
        # Extract questions from different categories
        categories_seen = set()
        for i in range(1, len(sections), 3):
            if i+2 <= len(sections):
                category = sections[i].strip()
                difficulty = sections[i+1].strip()
                
                # Only take one question per category
                if category not in categories_seen and (limit is None or len(categories_seen) < limit):
                    section_content = sections[i+2]
                    
                    # Extract the first question from this category
                    numbered_questions = re.findall(r'\d+\.\s+(.*?)\n', section_content)
                    if numbered_questions:
                        questions.append((numbered_questions[0].strip(), category, difficulty))
                        categories_seen.add(category)
    
    return questions

def ask_question_service_acct(question, session_id):
    """
    Ask a question using service account credentials
    
    Args:
        question (str): The question to ask
        session_id (str): Session ID for continuous conversation
        
    Returns:
        str: The response text from the agent
    """
    try:
        # Check if credentials file exists
        if not os.path.exists(CREDENTIALS_FILE):
            return f"Credentials file not found: {CREDENTIALS_FILE}"
            
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

def run_tests(questions, output_file="service_acct_test_results.csv"):
    """
    Run tests using service account credentials
    
    Args:
        questions: List of (question, category, difficulty) tuples
        output_file: CSV file to save results
    """
    # Prepare CSV file
    fieldnames = ['question_number', 'question', 'category', 'difficulty', 
                 'answer', 'session_id', 'timestamp', 'response_time_ms']
    
    total_questions = len(questions)
    success_count = 0
    error_count = 0
    
    # Summary statistics by category and difficulty
    stats_by_category = {}
    stats_by_difficulty = {}
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process questions with tqdm progress bar
        for i, (question, category, difficulty) in enumerate(tqdm(questions, desc="Processing questions")):
            question_number = i + 1
            
            # Progress indicator
            percent_complete = (i / total_questions) * 100
            print(f"\n[{percent_complete:.1f}%] Question {question_number}/{total_questions}")
            print(f"Category: {category}, Difficulty: {difficulty}")
            print(f"Q: {question}")
            
            # Ask the question
            session_id = f"service-acct-test-{question_number}-{int(time.time())}"
            start_time = time.time()
            
            try:
                answer = ask_question_service_acct(question, session_id)
                end_time = time.time()
                response_time_ms = int((end_time - start_time) * 1000)
                
                # Determine if answer was successful or an error
                is_error = "error" in answer.lower() or "failed" in answer.lower() or "status code" in answer.lower()
                
                if is_error:
                    error_count += 1
                    print(f"ERROR: {answer[:150]}..." if len(answer) > 150 else f"ERROR: {answer}")
                else:
                    success_count += 1
                    print(f"A: {answer[:150]}..." if len(answer) > 150 else f"A: {answer}")
                    print(f"Response time: {response_time_ms} ms")
                
                # Update statistics
                if category not in stats_by_category:
                    stats_by_category[category] = {'count': 0, 'success': 0, 'total_time': 0}
                stats_by_category[category]['count'] += 1
                if not is_error:
                    stats_by_category[category]['success'] += 1
                    stats_by_category[category]['total_time'] += response_time_ms
                
                if difficulty not in stats_by_difficulty:
                    stats_by_difficulty[difficulty] = {'count': 0, 'success': 0, 'total_time': 0}
                stats_by_difficulty[difficulty]['count'] += 1
                if not is_error:
                    stats_by_difficulty[difficulty]['success'] += 1 
                    stats_by_difficulty[difficulty]['total_time'] += response_time_ms
                
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
            
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
                error_count += 1
            
            # Add a delay between questions to avoid rate limiting
            time.sleep(1)
    
    # Print summary statistics
    print("\n" + "="*50)
    print(f"TEST SUMMARY FOR {total_questions} QUESTIONS")
    print("="*50)
    print(f"Total questions: {total_questions}")
    print(f"Successful responses: {success_count} ({success_count/total_questions*100:.1f}%)")
    print(f"Errors: {error_count} ({error_count/total_questions*100:.1f}%)")
    
    print("\nPerformance by Category:")
    for category, stats in stats_by_category.items():
        success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
        avg_time = stats['total_time'] / stats['success'] if stats['success'] > 0 else 0
        print(f"  {category}: {stats['success']}/{stats['count']} successful ({success_rate:.1f}%), Avg response: {avg_time:.0f}ms")
    
    print("\nPerformance by Difficulty:")
    for difficulty in ['Easy', 'Medium', 'Difficult', 'Extremely Difficult']:
        if difficulty in stats_by_difficulty:
            stats = stats_by_difficulty[difficulty]
            success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
            avg_time = stats['total_time'] / stats['success'] if stats['success'] > 0 else 0
            print(f"  {difficulty}: {stats['success']}/{stats['count']} successful ({success_rate:.1f}%), Avg response: {avg_time:.0f}ms")
    
    print("\nResults saved to: " + output_file)
    return success_count, error_count

def main():
    """Main function to run the test questions."""
    print(f"Testing Vertex AI Agent with service account credentials")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Credentials file: {CREDENTIALS_FILE}")
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Credentials file not found: {CREDENTIALS_FILE}")
        return 1
        
    print("Credentials file exists")
    
    # Extract a subset of questions for testing
    questions_file = "/Users/dionedge/dev/looker-vertex-agent/agent-api/tests/test_questions.md"
    print(f"Extracting 20 test questions...")
    questions = extract_questions(questions_file, limit=20)
    
    if not questions:
        print("No questions found in the file.")
        return 1
    
    print(f"Extracted {len(questions)} questions.")
    
    # Run tests
    output_file = f"service_acct_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    run_tests(questions, output_file)
    
    return 0

if __name__ == "__main__":
    main()