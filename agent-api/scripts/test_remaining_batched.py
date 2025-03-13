#!/usr/bin/env python3
"""
Test remaining questions in batches

This script tests the Vertex AI Agent using service account credentials,
processing questions in small batches to avoid timeout issues.
"""

import os
import re
import json
import time
import csv
import pickle
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

# Set of already tested question indices to avoid duplicates
# Load from pickle file instead of hardcoding
try:
    with open('tested_indices.pkl', 'rb') as f:
        TESTED_INDICES = pickle.load(f)
    print(f"Loaded {len(TESTED_INDICES)} previously tested question indices from file.")
except FileNotFoundError:
    # Fallback to default set if file doesn't exist
    TESTED_INDICES = set(list(range(52)) + [74, 83, 110, 122, 127, 139])
    print(f"Using default list of {len(TESTED_INDICES)} tested indices.")

def extract_all_questions(file_path):
    """
    Extract all questions from the markdown file.
    Returns a list of tuples: (question, category, difficulty)
    """
    questions = []
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find categories and difficulties
    sections = re.split(r'\*\*([^*]+)\*\*\s*\n\s*\*\*([^*]+)\*\*', content)
    
    # Extract all questions
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

def filter_untested_questions(all_questions):
    """
    Filter out questions that have already been tested.
    """
    untested_questions = []
    
    for idx, q_tuple in enumerate(all_questions):
        if idx not in TESTED_INDICES:
            untested_questions.append((idx, q_tuple))
    
    return untested_questions

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

def run_batch(questions_batch, batch_num, output_file="remaining_batched_results.csv", append=False):
    """
    Run tests for a batch of questions
    
    Args:
        questions_batch: List of (idx, (question, category, difficulty)) tuples
        batch_num: Batch number for logging
        output_file: CSV file to save results
        append: Whether to append to the output file
    """
    # Prepare CSV file
    fieldnames = ['question_number', 'question', 'category', 'difficulty', 
                 'answer', 'session_id', 'timestamp', 'response_time_ms']
    
    total_questions = len(questions_batch)
    success_count = 0
    error_count = 0
    
    # Summary statistics for this batch
    stats_by_category = {}
    stats_by_difficulty = {}
    
    # Create or append to CSV file
    mode = 'a' if append else 'w'
    with open(output_file, mode, newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not append:
            writer.writeheader()
        
        # Process questions with tqdm progress bar
        for batch_idx, (orig_idx, (question, category, difficulty)) in enumerate(tqdm(questions_batch, desc=f"Batch {batch_num}")):
            question_number = orig_idx + 1  # 1-indexed for display
            
            # Progress indicator
            batch_progress = (batch_idx / total_questions) * 100
            print(f"\n[Batch {batch_num}, {batch_progress:.1f}%] Question {question_number}/140")
            print(f"Category: {category}, Difficulty: {difficulty}")
            print(f"Q: {question}")
            
            # Ask the question
            session_id = f"batch{batch_num}-q{question_number}-{int(time.time())}"
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
                
                # Save tested index to a pickle file for resumability
                with open('tested_indices.pkl', 'wb') as f:
                    pickle.dump(TESTED_INDICES.union({orig_idx}), f)
                
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
                error_count += 1
            
            # Add a delay between questions to avoid rate limiting
            time.sleep(1)
    
    # Print batch summary
    print("\n" + "="*50)
    print(f"BATCH {batch_num} SUMMARY ({total_questions} QUESTIONS)")
    print("="*50)
    print(f"Successful responses: {success_count} ({success_count/total_questions*100:.1f}%)")
    print(f"Errors: {error_count} ({error_count/total_questions*100:.1f}%)")
    
    return success_count, error_count, stats_by_category, stats_by_difficulty

def main():
    """Main function to run the test questions in batches."""
    print(f"Testing Vertex AI Agent with service account credentials - Batched Remaining Questions")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Credentials file: {CREDENTIALS_FILE}")
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Credentials file not found: {CREDENTIALS_FILE}")
        return 1
        
    print("Credentials file exists")
    
    # Try to load previously tested indices
    if os.path.exists('tested_indices.pkl'):
        with open('tested_indices.pkl', 'rb') as f:
            global TESTED_INDICES
            TESTED_INDICES = pickle.load(f)
        print(f"Loaded {len(TESTED_INDICES)} previously tested question indices.")
    
    # Extract all questions
    questions_file = "/Users/dionedge/dev/looker-vertex-agent/agent-api/tests/test_questions.md"
    print(f"Extracting all questions from {questions_file}...")
    all_questions = extract_all_questions(questions_file)
    
    # Filter out already tested questions
    untested_questions = filter_untested_questions(all_questions)
    
    if not untested_questions:
        print("No untested questions remaining.")
        return 0
    
    print(f"Found {len(untested_questions)} untested questions out of {len(all_questions)} total.")
    
    # Process in small batches to avoid timeouts
    batch_size = 10
    num_batches = (len(untested_questions) + batch_size - 1) // batch_size
    
    print(f"Will process in {num_batches} batches of up to {batch_size} questions each.")
    
    # Output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"remaining_batched_results_{timestamp}.csv"
    
    # Process each batch
    overall_success = 0
    overall_error = 0
    all_categories = {}
    all_difficulties = {}
    
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(untested_questions))
        batch = untested_questions[start_idx:end_idx]
        
        print(f"\nProcessing batch {batch_num+1}/{num_batches} ({len(batch)} questions)")
        
        success, error, categories, difficulties = run_batch(
            batch, 
            batch_num + 1, 
            output_file, 
            append=(batch_num > 0)
        )
        
        overall_success += success
        overall_error += error
        
        # Merge statistics
        for category, stats in categories.items():
            if category not in all_categories:
                all_categories[category] = {'count': 0, 'success': 0, 'total_time': 0}
            all_categories[category]['count'] += stats['count']
            all_categories[category]['success'] += stats['success']
            all_categories[category]['total_time'] += stats['total_time']
            
        for difficulty, stats in difficulties.items():
            if difficulty not in all_difficulties:
                all_difficulties[difficulty] = {'count': 0, 'success': 0, 'total_time': 0}
            all_difficulties[difficulty]['count'] += stats['count']
            all_difficulties[difficulty]['success'] += stats['success']
            all_difficulties[difficulty]['total_time'] += stats['total_time']
    
    # Print overall summary
    total_tested = overall_success + overall_error
    print("\n" + "="*50)
    print(f"OVERALL SUMMARY FOR REMAINING {total_tested} QUESTIONS")
    print("="*50)
    print(f"Total questions: {total_tested}")
    print(f"Successful responses: {overall_success} ({overall_success/total_tested*100:.1f}%)")
    print(f"Errors: {overall_error} ({overall_error/total_tested*100:.1f}%)")
    
    print("\nPerformance by Category:")
    for category, stats in all_categories.items():
        success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
        avg_time = stats['total_time'] / stats['success'] if stats['success'] > 0 else 0
        print(f"  {category}: {stats['success']}/{stats['count']} successful ({success_rate:.1f}%), Avg response: {avg_time:.0f}ms")
    
    print("\nPerformance by Difficulty:")
    for difficulty in ['Easy', 'Medium', 'Difficult', 'Extremely Difficult']:
        if difficulty in all_difficulties:
            stats = all_difficulties[difficulty]
            success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
            avg_time = stats['total_time'] / stats['success'] if stats['success'] > 0 else 0
            print(f"  {difficulty}: {stats['success']}/{stats['count']} successful ({success_rate:.1f}%), Avg response: {avg_time:.0f}ms")
    
    print("\nResults saved to: " + output_file)
    return 0

if __name__ == "__main__":
    main()