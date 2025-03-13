#!/usr/bin/env python3
"""
Advanced Question Runner for Vertex AI Agent API

This script tests the Vertex AI Agent with more challenging questions that may not 
be in the original test set. It includes complex technical questions, multi-part 
questions, and edge cases.
"""

import os
import re
import csv
import json
import time
import argparse
import requests
from datetime import datetime
from tqdm import tqdm

# Advanced questions covering different complexity levels
ADVANCED_QUESTIONS = [
    {
        "category": "Looker", 
        "difficulty": "Difficult",
        "question": "How can I implement row-level security in Looker that restricts users to seeing only data from their assigned geographic region?"
    },
    {
        "category": "Looker", 
        "difficulty": "Difficult",
        "question": "What's the best way to optimize a slow-running LookML dashboard that includes multiple derived tables?"
    },
    {
        "category": "Looker", 
        "difficulty": "Extremely Difficult",
        "question": "I'm trying to create a complex calculation that involves window functions across multiple join paths. How can I implement this in LookML?"
    },
    {
        "category": "BigQuery", 
        "difficulty": "Difficult",
        "question": "How do I implement efficient incremental processing in BigQuery for tables that receive updates to existing records?"
    },
    {
        "category": "BigQuery", 
        "difficulty": "Extremely Difficult",
        "question": "I need to implement a complex analytical workflow that involves geographic data processing, ML prediction, and time-series forecasting in BigQuery. What's the optimal approach?"
    },
    {
        "category": "BQML", 
        "difficulty": "Difficult",
        "question": "How can I implement a recommendation system using BQML that takes into account both user behavior and product metadata?"
    },
    {
        "category": "dbt", 
        "difficulty": "Difficult",
        "question": "What's the best approach for implementing a slowly changing dimension type 2 (SCD2) in dbt when the source data doesn't have reliable updated timestamps?"
    },
    {
        "category": "Omni", 
        "difficulty": "Difficult",
        "question": "How can I optimize a cross-cloud query in Looker that joins data from BigQuery and Snowflake using Omni?"
    },
    {
        "category": "Looker", 
        "difficulty": "Extremely Difficult",
        "question": "I have a complex data model with multiple fanouts and need to create a merged result. How can I avoid duplicate counting while maintaining all the necessary join paths?"
    },
    {
        "category": "Technical", 
        "difficulty": "Difficult",
        "question": "Our Looker instance is showing degraded performance during peak hours. What monitoring metrics should I check and what steps can I take to diagnose the bottleneck?"
    }
]

# Multi-part questions to test conversational capabilities
MULTI_PART_QUESTIONS = [
    {
        "category": "Looker", 
        "difficulty": "Difficult",
        "question": "I want to create a dashboard for our executive team. It needs to show sales by region, product category, and over time. What's the best way to structure this?"
    },
    {
        "category": "BigQuery", 
        "difficulty": "Difficult",
        "question": "I need to migrate our data warehouse from Redshift to BigQuery. What are the key considerations and steps in this process?"
    },
    {
        "category": "BQML", 
        "difficulty": "Difficult",
        "question": "Can you explain how to build and deploy a customer churn prediction model using BQML? I'm interested in understanding both the technical implementation and how to operationalize the predictions."
    },
    {
        "category": "Looker", 
        "difficulty": "Difficult",
        "question": "How do custom fields work in Looker? I want to allow my business users to create their own metrics without needing to modify LookML."
    },
    {
        "category": "Technical", 
        "difficulty": "Extremely Difficult",
        "question": "We're experiencing some data discrepancies between our Looker dashboards and our source database. What could be causing this and how should we investigate?"
    }
]

# Edge cases and ambiguous questions
EDGE_CASE_QUESTIONS = [
    {
        "category": "Ambiguous", 
        "difficulty": "Difficult",
        "question": "How do I join tables?"
    },
    {
        "category": "Ambiguous", 
        "difficulty": "Difficult",
        "question": "What's the best visualization?"
    },
    {
        "category": "Technical", 
        "difficulty": "Difficult",
        "question": "Can you write me a complex SQL query?"
    },
    {
        "category": "Technical", 
        "difficulty": "Difficult",
        "question": "Why isn't my Looker model working?"
    },
    {
        "category": "Edge Case", 
        "difficulty": "Extremely Difficult",
        "question": "Can you help me design a multi-cloud data architecture that includes BigQuery, Snowflake, and Redshift with Looker as the semantic layer?"
    }
]

def ask_question(question_text, api_url="http://localhost:8082/ask"):
    """Send a question to the Vertex AI Agent API."""
    try:
        # Prepare the payload
        payload = {
            "question": question_text
        }
        
        # Make the API request
        start_time = time.time()
        response = requests.post(api_url, json=payload)
        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return {
                "answer": result.get("answer", "No answer returned"),
                "response_time_ms": response_time_ms,
                "session_id": result.get("session_id", "No session ID"),
                "success": True
            }
        else:
            return {
                "answer": f"ERROR: API returned status code {response.status_code}",
                "response_time_ms": response_time_ms,
                "session_id": None,
                "success": False
            }
    
    except Exception as e:
        return {
            "answer": f"ERROR: {str(e)}",
            "response_time_ms": -1,
            "session_id": None,
            "success": False
        }

def run_questions(questions, api_url, output_file):
    """Run a list of questions and save the results to a CSV file."""
    results = []
    
    # Setup the progress bar
    with tqdm(total=len(questions), desc="Processing questions") as pbar:
        for i, question_obj in enumerate(questions):
            question_num = i + 1
            category = question_obj.get("category", "Uncategorized")
            difficulty = question_obj.get("difficulty", "Unknown")
            question_text = question_obj.get("question", "")
            
            # Print the question information
            print(f"\nQuestion {question_num}: [{category}] [{difficulty}]")
            print(f"Q: {question_text}")
            
            # Send the question to the API
            result = ask_question(question_text, api_url)
            answer = result.get("answer", "No answer returned")
            response_time_ms = result.get("response_time_ms", -1)
            session_id = result.get("session_id", "No session ID")
            success = result.get("success", False)
            
            # Print the answer
            print(f"A: {answer[:200]}..." if len(answer) > 200 else f"A: {answer}")
            print(f"Response Time: {response_time_ms} ms | Success: {success}")
            
            # Save the result
            results.append({
                "question_number": question_num,
                "category": category,
                "difficulty": difficulty,
                "question": question_text,
                "answer": answer,
                "response_time_ms": response_time_ms,
                "session_id": session_id,
                "success": success
            })
            
            # Update the progress bar
            pbar.update(1)
    
    # Save the results to a CSV file
    fieldnames = [
        "question_number", "category", "difficulty", "question",
        "answer", "response_time_ms", "session_id", "success"
    ]
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults saved to {output_file}")
    
    return results

def main():
    """Main function to run the advanced questions."""
    parser = argparse.ArgumentParser(description="Run advanced questions against the Vertex AI Agent API")
    parser.add_argument("--url", type=str, default="http://localhost:8082/ask",
                        help="URL of the Vertex AI Agent API (default: http://localhost:8082/ask)")
    parser.add_argument("--output", "-o", type=str, 
                        default=f"advanced_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        help="Path to the output CSV file")
    parser.add_argument("--type", "-t", type=str, choices=["advanced", "multi-part", "edge", "all"],
                        default="all", help="Type of questions to run (default: all)")
    
    args = parser.parse_args()
    
    # Determine which questions to run based on the type
    if args.type == "advanced":
        questions = ADVANCED_QUESTIONS
        print(f"Running {len(questions)} advanced questions...")
    elif args.type == "multi-part":
        questions = MULTI_PART_QUESTIONS
        print(f"Running {len(questions)} multi-part questions...")
    elif args.type == "edge":
        questions = EDGE_CASE_QUESTIONS
        print(f"Running {len(questions)} edge case questions...")
    else:  # "all"
        questions = ADVANCED_QUESTIONS + MULTI_PART_QUESTIONS + EDGE_CASE_QUESTIONS
        print(f"Running all {len(questions)} questions...")
    
    # Run the questions
    run_questions(questions, args.url, args.output)

if __name__ == "__main__":
    main() 