#!/usr/bin/env python3
"""
Analyze Vertex AI Agent test results from BigQuery.

This script retrieves test results from BigQuery, analyzes them, and
generates visualizations to help evaluate the agent's performance.
"""
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
from datetime import datetime, timedelta

# Set default styling for plots
plt.style.use('ggplot')
sns.set(style="whitegrid")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze Vertex AI Agent test results from BigQuery'
    )
    parser.add_argument(
        '--project-id',
        default=os.environ.get('PROJECT_ID', 'heuristicsai'),
        help='Google Cloud project ID'
    )
    parser.add_argument(
        '--dataset',
        default=os.environ.get('BIGQUERY_DATASET', 'conversations'),
        help='BigQuery dataset name'
    )
    parser.add_argument(
        '--table',
        default=os.environ.get('BIGQUERY_TABLE', 'bia'),
        help='BigQuery table name'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of data to analyze'
    )
    parser.add_argument(
        '--output-dir',
        default='./results',
        help='Directory to save visualizations'
    )
    return parser.parse_args()


def get_results_from_bigquery(project_id, dataset, table, days):
    """Retrieve test results from BigQuery."""
    client = bigquery.Client(project=project_id)
    
    # Calculate the date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Prepare and execute the query
    query = f"""
    SELECT
      question,
      response_text,
      timestamp,
      CHAR_LENGTH(response_text) AS response_length
    FROM
      `{project_id}.{dataset}.{table}`
    WHERE
      timestamp BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'
    ORDER BY
      timestamp DESC
    """
    
    print(f"Retrieving data from {project_id}.{dataset}.{table}...")
    return client.query(query).to_dataframe()


def analyze_results(df):
    """Analyze the test results."""
    if df.empty:
        print("No data found for the specified time period.")
        return None
    
    print(f"Retrieved {len(df)} test results.")
    
    # Basic statistics
    stats = {
        'total_tests': len(df),
        'unique_questions': df['question'].nunique(),
        'avg_response_length': df['response_length'].mean(),
        'min_response_length': df['response_length'].min(),
        'max_response_length': df['response_length'].max(),
        'tests_per_day': df.groupby(df['timestamp'].dt.date).size().mean()
    }
    
    # Add more advanced analysis here if needed
    
    return stats


def create_visualizations(df, stats, output_dir):
    """Create visualizations of the test results."""
    if df.empty:
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Response length distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['response_length'], bins=20, kde=True)
    plt.title('Distribution of Response Lengths')
    plt.xlabel('Response Length (characters)')
    plt.ylabel('Frequency')
    plt.savefig(f"{output_dir}/response_length_distribution.png")
    
    # 2. Response length over time
    plt.figure(figsize=(12, 6))
    plt.scatter(df['timestamp'], df['response_length'], alpha=0.6)
    plt.title('Response Length Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Response Length (characters)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/response_length_over_time.png")
    
    # 3. Tests per day
    tests_per_day = df.groupby(df['timestamp'].dt.date).size()
    plt.figure(figsize=(10, 6))
    tests_per_day.plot(kind='bar')
    plt.title('Number of Tests per Day')
    plt.xlabel('Date')
    plt.ylabel('Number of Tests')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/tests_per_day.png")
    
    # 4. Top 10 most frequent questions
    top_questions = df['question'].value_counts().head(10)
    plt.figure(figsize=(12, 8))
    top_questions.plot(kind='barh')
    plt.title('Top 10 Most Frequent Test Questions')
    plt.xlabel('Frequency')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/top_questions.png")
    
    # 5. Summary statistics
    plt.figure(figsize=(10, 6))
    plt.axis('off')
    plt.text(0.1, 0.9, f"Total Tests: {stats['total_tests']}", fontsize=14)
    plt.text(0.1, 0.8, f"Unique Questions: {stats['unique_questions']}", fontsize=14)
    plt.text(0.1, 0.7, f"Avg Response Length: {stats['avg_response_length']:.2f} chars", fontsize=14)
    plt.text(0.1, 0.6, f"Min Response Length: {stats['min_response_length']} chars", fontsize=14)
    plt.text(0.1, 0.5, f"Max Response Length: {stats['max_response_length']} chars", fontsize=14)
    plt.text(0.1, 0.4, f"Avg Tests per Day: {stats['tests_per_day']:.2f}", fontsize=14)
    plt.title('Summary Statistics', fontsize=16)
    plt.savefig(f"{output_dir}/summary_stats.png")
    
    print(f"Visualizations saved to {output_dir}/ directory.")


def main():
    # Parse command line arguments
    args = parse_args()
    
    # Retrieve results from BigQuery
    df = get_results_from_bigquery(args.project_id, args.dataset, args.table, args.days)
    
    # Convert timestamp to datetime
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Analyze results
    stats = analyze_results(df)
    
    if stats:
        # Print statistics
        print("\nSummary Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Create visualizations
        create_visualizations(df, stats, args.output_dir)
        
        print("\nAnalysis complete!")


if __name__ == "__main__":
    main() 