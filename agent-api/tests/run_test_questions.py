#!/usr/bin/env python3
"""
Test Question Runner for Vertex AI Agent API

This script reads questions from a markdown file and sends them to the Vertex AI Agent API.
It saves the results to a CSV file for further analysis.
"""

import os
import re
import csv
import json
import time
import sys
import requests
import argparse
from datetime import datetime
from tqdm import tqdm  # Progress bar

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Set default paths relative to project structure
DEFAULT_QUESTIONS_PATH = os.path.join(project_root, 'tests', 'test_questions.md')
DEFAULT_RESULTS_PATH = os.path.join(project_root, 'data', 'results', f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

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

def ask_question(question, session_id, api_url="http://localhost:8082/ask"):
    """
    Send a question to the Vertex AI Agent API.
    
    Args:
        question (str): The question to ask
        session_id (str): Session ID for continuous conversation
        api_url (str): URL of the API endpoint
        
    Returns:
        dict: The API response as a dictionary
    """
    payload = {
        "question": question,
        "sessionId": session_id
    }
    
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60  # Longer timeout for complex questions
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending request for question '{question}': {e}")
        return None

def main():
    """Main function to run the test questions."""
    parser = argparse.ArgumentParser(description="Test Vertex AI Agent with test questions")
    parser.add_argument("--file", "-f", type=str, 
                        default=DEFAULT_QUESTIONS_PATH,
                        help="Path to the markdown file with test questions")
    parser.add_argument("--url", "-u", type=str, 
                        default="http://localhost:8082/ask",
                        help="API endpoint URL")
    parser.add_argument("--output", "-o", type=str, 
                        default=DEFAULT_RESULTS_PATH,
                        help="Output CSV file for results")
    parser.add_argument("--start", "-s", type=int, default=1,
                        help="Start from this question number (1-indexed)")
    parser.add_argument("--limit", "-l", type=int, default=0,
                        help="Limit the number of questions to process (0 = all)")
    
    args = parser.parse_args()
    
    # Extract questions
    print(f"Extracting questions from {args.file}...")
    questions = extract_questions(args.file)
    
    if not questions:
        print("No questions found in the file.")
        return 1
    
    print(f"Found {len(questions)} questions.")
    
    # Prepare CSV file
    fieldnames = ['question_number', 'question', 'category', 'difficulty', 
                 'answer', 'session_id', 'timestamp', 'response_time_ms']
    
    with open(args.output, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process questions
        start_idx = max(0, args.start - 1)
        end_idx = len(questions) if args.limit <= 0 else min(start_idx + args.limit, len(questions))
        
        for i in tqdm(range(start_idx, end_idx), desc="Processing questions"):
            question, category, difficulty = questions[i]
            question_number = i + 1
            
            print(f"\nQuestion {question_number}: {question}")
            print(f"Category: {category}, Difficulty: {difficulty}")
            
            # Ask the question
            session_id = f"test-{question_number}-{int(time.time())}"
            start_time = time.time()
            result = ask_question(question, session_id, args.url)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            if result:
                answer = result.get('answer', 'No answer provided')
                timestamp = result.get('timestamp', datetime.now().isoformat())
                
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
                    'timestamp': timestamp,
                    'response_time_ms': response_time_ms
                })
                csvfile.flush()  # Ensure data is written immediately
            else:
                print("Failed to get response")
                
                # Write error to CSV
                writer.writerow({
                    'question_number': question_number,
                    'question': question,
                    'category': category,
                    'difficulty': difficulty,
                    'answer': "ERROR: Failed to get response",
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'response_time_ms': response_time_ms
                })
                csvfile.flush()
            
            # Add a small delay between questions to avoid overwhelming the API
            time.sleep(1)
    
    print(f"\nResults saved to {args.output}")
    return 0

if __name__ == "__main__":
    main() 