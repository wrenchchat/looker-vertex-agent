#!/usr/bin/env python3
"""
Test a diverse sample of questions from different categories

This script tests the Vertex AI Agent using service account credentials,
taking a sample of questions from different categories and difficulty levels.
"""

import os
import re
import json
import time
import csv
import random
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

def sample_diverse_questions(questions, samples_per_category=2, samples_per_difficulty=2):
    """
    Sample questions to get a diverse set across categories and difficulties.
    """
    # Group questions by category
    category_questions = {}
    difficulty_questions = {}
    
    for q, category, difficulty in questions:
        if category not in category_questions:
            category_questions[category] = []
        category_questions[category].append((q, category, difficulty))
        
        if difficulty not in difficulty_questions:
            difficulty_questions[difficulty] = []
        difficulty_questions[difficulty].append((q, category, difficulty))
    
    # Sample from each category
    sampled_questions = []
    
    # First by category
    for category, questions_list in category_questions.items():
        # Take random samples from this category
        if len(questions_list) <= samples_per_category:
            samples = questions_list  # Take all if we have fewer than requested
        else:
            samples = random.sample(questions_list, samples_per_category)
        
        for sample in samples:
            if sample not in sampled_questions:
                sampled_questions.append(sample)
    
    # Then by difficulty
    for difficulty, questions_list in difficulty_questions.items():
        # Take random samples from this difficulty
        if len(questions_list) <= samples_per_difficulty:
            samples = questions_list  # Take all if we have fewer than requested
        else:
            samples = random.sample(questions_list, samples_per_difficulty)
        
        for sample in samples:
            if sample not in sampled_questions:
                sampled_questions.append(sample)
    
    return sampled_questions

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

def run_tests(questions, output_file="diverse_sample_results.csv"):
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
            session_id = f"diverse-sample-{question_number}-{int(time.time())}"
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
    print(f"TEST SUMMARY FOR {total_questions} DIVERSE QUESTIONS")
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
    print(f"Testing Vertex AI Agent with service account credentials - Diverse Sample")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Credentials file: {CREDENTIALS_FILE}")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Credentials file not found: {CREDENTIALS_FILE}")
        return 1
        
    print("Credentials file exists")
    
    # Extract all questions
    questions_file = "/Users/dionedge/dev/looker-vertex-agent/agent-api/tests/test_questions.md"
    print(f"Extracting all questions from {questions_file}...")
    all_questions = extract_all_questions(questions_file)
    
    # Sample diverse questions
    print(f"Sampling diverse questions...")
    sampled_questions = sample_diverse_questions(all_questions, samples_per_category=4, samples_per_difficulty=4)
    
    if not sampled_questions:
        print("No questions sampled.")
        return 1
    
    print(f"Sampled {len(sampled_questions)} diverse questions.")
    
    # Run tests with the sampled questions
    output_file = f"diverse_sample_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    run_tests(sampled_questions, output_file)
    
    return 0

if __name__ == "__main__":
    main()