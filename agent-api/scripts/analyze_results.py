#!/usr/bin/env python3
"""
Test Results Analyzer for Vertex AI Agent API

This script analyzes the results of the test questions run against the agent.
It provides statistics and insights on response quality, response time, and error rates.
"""

import os
import csv
import glob
import argparse
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

def load_results(file_path):
    """Load results from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def analyze_results(df):
    """Analyze the test results."""
    if df is None or df.empty:
        print("No data to analyze.")
        return
    
    # Basic statistics
    total_questions = len(df)
    error_count = df['answer'].str.startswith('ERROR').sum()
    success_rate = ((total_questions - error_count) / total_questions) * 100
    
    # Response time statistics
    avg_response_time = df['response_time_ms'].mean()
    median_response_time = df['response_time_ms'].median()
    min_response_time = df['response_time_ms'].min()
    max_response_time = df['response_time_ms'].max()
    
    # Group by category and difficulty
    category_stats = df.groupby('category').agg({
        'question_number': 'count',
        'response_time_ms': 'mean'
    }).rename(columns={'question_number': 'count', 'response_time_ms': 'avg_response_time_ms'})
    
    difficulty_stats = df.groupby('difficulty').agg({
        'question_number': 'count',
        'response_time_ms': 'mean'
    }).rename(columns={'question_number': 'count', 'response_time_ms': 'avg_response_time_ms'})
    
    # Print statistics
    print("\n===== TEST RESULTS ANALYSIS =====")
    print(f"Total questions: {total_questions}")
    print(f"Successful responses: {total_questions - error_count} ({success_rate:.2f}%)")
    print(f"Error responses: {error_count} ({100 - success_rate:.2f}%)")
    print("\n----- Response Time Statistics -----")
    print(f"Average response time: {avg_response_time:.2f} ms")
    print(f"Median response time: {median_response_time:.2f} ms")
    print(f"Min response time: {min_response_time:.2f} ms")
    print(f"Max response time: {max_response_time:.2f} ms")
    
    print("\n----- Category Statistics -----")
    print(category_stats)
    
    print("\n----- Difficulty Statistics -----")
    print(difficulty_stats)
    
    return {
        'total_questions': total_questions,
        'error_count': error_count,
        'success_rate': success_rate,
        'avg_response_time': avg_response_time,
        'median_response_time': median_response_time,
        'min_response_time': min_response_time,
        'max_response_time': max_response_time,
        'category_stats': category_stats,
        'difficulty_stats': difficulty_stats,
        'df': df
    }

def generate_visualizations(analysis_results, output_dir):
    """Generate visualizations from the analysis results."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    df = analysis_results['df']
    
    # 1. Response time distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df['response_time_ms'], bins=20, alpha=0.7)
    plt.title('Response Time Distribution')
    plt.xlabel('Response Time (ms)')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'response_time_distribution.png'))
    plt.close()
    
    # 2. Response time by category
    plt.figure(figsize=(12, 6))
    category_times = df.groupby('category')['response_time_ms'].mean().sort_values(ascending=False)
    category_times.plot(kind='bar')
    plt.title('Average Response Time by Category')
    plt.xlabel('Category')
    plt.ylabel('Average Response Time (ms)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'response_time_by_category.png'))
    plt.close()
    
    # 3. Response time by difficulty
    plt.figure(figsize=(10, 6))
    difficulty_times = df.groupby('difficulty')['response_time_ms'].mean()
    difficulty_times.plot(kind='bar')
    plt.title('Average Response Time by Difficulty')
    plt.xlabel('Difficulty')
    plt.ylabel('Average Response Time (ms)')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'response_time_by_difficulty.png'))
    plt.close()
    
    # 4. Question count by category
    plt.figure(figsize=(12, 6))
    category_counts = df['category'].value_counts()
    category_counts.plot(kind='bar')
    plt.title('Question Count by Category')
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'question_count_by_category.png'))
    plt.close()
    
    print(f"Visualizations saved to {output_dir}")

def main():
    """Main function to analyze the test results."""
    parser = argparse.ArgumentParser(description="Analyze test results from the Vertex AI Agent API")
    parser.add_argument("--file", "-f", type=str, 
                        help="Path to the CSV file with test results")
    parser.add_argument("--dir", "-d", type=str, default="./viz", 
                        help="Directory to save visualizations")
    parser.add_argument("--combine", "-c", action="store_true",
                        help="Combine all test result files and analyze them together")
    
    args = parser.parse_args()
    
    if args.combine:
        # Combine all CSV files
        csv_files = glob.glob("test_results_*.csv")
        if not csv_files:
            print("No test result files found.")
            return 1
        
        print(f"Combining {len(csv_files)} result files:")
        for file in csv_files:
            print(f"  - {file}")
        
        dfs = []
        for file in csv_files:
            df = load_results(file)
            if df is not None:
                dfs.append(df)
        
        if not dfs:
            print("No valid data found in any files.")
            return 1
        
        combined_df = pd.concat(dfs, ignore_index=True)
        results = analyze_results(combined_df)
        generate_visualizations(results, args.dir)
    elif args.file:
        # Analyze a single file
        df = load_results(args.file)
        results = analyze_results(df)
        generate_visualizations(results, args.dir)
    else:
        print("Please specify a file to analyze or use --combine to analyze all result files.")
        return 1
    
    return 0

if __name__ == "__main__":
    main() 