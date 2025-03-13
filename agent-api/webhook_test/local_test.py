"""
Local testing script for the Vertex AI agent webhook.
This allows you to test the Cloud Function locally before deployment.
"""
import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify, Request

# Import the function from main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import test_vertex_agent

# Create a simple Flask app for testing
app = Flask(__name__)

@app.route('/test', methods=['GET', 'POST'])
def test_function():
    """Route that simulates the Cloud Function."""
    # Run only one test question if testing locally
    if request.method == 'GET':
        # Mock the request to only run one test question
        class MockRequest:
            method = 'GET'
        
        response, status_code = test_vertex_agent(MockRequest())
        return response, status_code
    
    elif request.method == 'POST':
        # Pass through the POST request
        response, status_code = test_vertex_agent(request)
        return response, status_code

@app.route('/', methods=['GET'])
def home():
    """Home route with instructions."""
    return """
    <h1>Vertex AI Agent Tester</h1>
    <p>Use the following endpoints:</p>
    <ul>
        <li><a href="/test">/test</a> (GET) - Run predefined tests</li>
        <li>/test (POST) - Run custom tests with your own questions</li>
    </ul>
    <p>Example POST request:</p>
    <pre>
    curl -X POST http://localhost:8080/test \\
      -H "Content-Type: application/json" \\
      -d '{
        "questions": [
          "How do I create a calculated field in Looker?",
          "What is the difference between a view and an explore?"
        ]
      }'
    </pre>
    """

if __name__ == '__main__':
    # Make sure environment variables are set
    if 'PROJECT_ID' not in os.environ:
        os.environ['PROJECT_ID'] = 'heuristicsai'
    if 'LOCATION' not in os.environ:
        os.environ['LOCATION'] = 'global'
    if 'VERTEX_AI_APP_ID' not in os.environ:
        os.environ['VERTEX_AI_APP_ID'] = '8285e0d0-24ae-43e9-8491-b0bd99befc87'
    if 'BIGQUERY_DATASET' not in os.environ:
        os.environ['BIGQUERY_DATASET'] = 'conversations'
    if 'BIGQUERY_TABLE' not in os.environ:
        os.environ['BIGQUERY_TABLE'] = 'bia'
    
    # Set GOOGLE_APPLICATION_CREDENTIALS if not already set
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/dionedge/dev/creds/heuristicsai-9ad7dd8375bf.json'
    
    app.run(host='0.0.0.0', port=8080, debug=True) 