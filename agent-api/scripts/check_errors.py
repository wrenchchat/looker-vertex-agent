#!/usr/bin/env python3
"""
Check for errors in the test results
"""

import csv
import os
import glob

def find_error_questions():
    error_questions = []
    
    # List of result files to check
    result_files = glob.glob("*_results_*.csv")
    
    for file_path in result_files:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                question = row.get('question', '')
                category = row.get('category', '')
                difficulty = row.get('difficulty', '')
                answer = row.get('answer', '')
                
                # Check if the answer indicates an error
                if "error" in answer.lower() or "failed" in answer.lower() or "status code" in answer.lower():
                    error_questions.append({
                        'question': question,
                        'category': category,
                        'difficulty': difficulty,
                        'file': file_path,
                        'error_message': answer[:200] + "..." if len(answer) > 200 else answer
                    })
    
    return error_questions

def main():
    error_questions = find_error_questions()
    
    print(f"Found {len(error_questions)} questions with errors:\n")
    
    for i, error in enumerate(error_questions, 1):
        print(f"{i}. Question: {error['question']}")
        print(f"   Category: {error['category']}")
        print(f"   Difficulty: {error['difficulty']}")
        print(f"   Error message: {error['error_message']}")
        print(f"   File: {error['file']}")
        print()

if __name__ == "__main__":
    main()