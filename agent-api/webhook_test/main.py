import functions_framework
import json
import os
import google.auth
import google.auth.transport.requests
from google.cloud import bigquery
import requests
from datetime import datetime

# Test questions for the Vertex AI agent
TEST_QUESTIONS = [
    "What are the best practices for data modeling in Looker?",
    "How do I optimize a BigQuery query with many joins?",
    "What's the difference between explores and views in Looker?",
    "How can I create a dashboard in Looker Studio?",
    "What are the benefits of using dbt with BigQuery?",
    "How can I connect to BigQuery Omni from GCP?",
    "What's the difference between LookML and SQL?",
    "How do I create a derived table in Looker?",
    "What are the best practices for BigQuery partitioning?",
    "How can I implement row-level security in Looker?"
]

def get_access_token():
    """Get an OAuth 2.0 access token using the default credentials."""
    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

def log_to_bigquery(project_id, dataset_id, table_id, data):
    """Log the question and response to BigQuery."""
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    # Ensure the table exists (create if it doesn't)
    try:
        client.get_table(table_ref)
    except Exception:
        # Create table
        schema = [
            bigquery.SchemaField("question", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("response_text", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("full_response", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table, exists_ok=True)
    
    # Insert row
    rows_to_insert = [data]
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    
    if errors:
        print(f"Error inserting rows: {errors}")
        return False
    return True

@functions_framework.http
def test_vertex_agent(request):
    """HTTP Cloud Function that tests the Vertex AI agent with predefined questions."""
    # Get configuration from environment variables
    project_id = os.environ.get('PROJECT_ID', 'heuristicsai')
    location = os.environ.get('LOCATION', 'global')
    agent_id = os.environ.get('VERTEX_AI_APP_ID', '8285e0d0-24ae-43e9-8491-b0bd99befc87')
    bq_dataset = os.environ.get('BIGQUERY_DATASET', 'conversations')
    bq_table = os.environ.get('BIGQUERY_TABLE', 'bia')
    
    # Get access token for authentication
    access_token = get_access_token()
    
    # Process request
    if request.method == 'GET':
        # Handle scheduled invocation or testing
        results = []
        
        for question in TEST_QUESTIONS:
            # Prepare the API URL
            api_url = f"https://dialogflow.googleapis.com/v3/projects/{project_id}/locations/{location}/agents/{agent_id}/sessions/test-session-{datetime.now().timestamp()}:detectIntent"
            
            # Prepare the request payload
            payload = {
                "queryInput": {
                    "text": {
                        "text": question
                    },
                    "languageCode": "en"
                }
            }
            
            # Set headers with authentication
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            try:
                # Make the API call
                response = requests.post(api_url, headers=headers, json=payload)
                response_data = response.json()
                
                # Extract the response text from the agent
                response_text = "No response text found"
                if "queryResult" in response_data and "responseMessages" in response_data["queryResult"]:
                    for msg in response_data["queryResult"]["responseMessages"]:
                        if "text" in msg and "text" in msg["text"]:
                            response_text = "\n".join(msg["text"]["text"])
                            break
                
                # Log to BigQuery
                log_data = {
                    "question": question,
                    "response_text": response_text,
                    "full_response": json.dumps(response_data),
                    "timestamp": datetime.now().isoformat()
                }
                
                log_to_bigquery(project_id, bq_dataset, bq_table, log_data)
                
                # Add to results
                results.append({
                    "question": question,
                    "response": response_text,
                    "status": response.status_code
                })
                
            except Exception as e:
                results.append({
                    "question": question,
                    "error": str(e),
                    "status": "Error"
                })
        
        return json.dumps({
            "status": "success",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    elif request.method == 'POST':
        # Handle custom questions via POST
        try:
            request_json = request.get_json(silent=True)
            
            if not request_json or 'questions' not in request_json:
                return json.dumps({
                    "status": "error",
                    "message": "Please provide a 'questions' array in the request body"
                }), 400
            
            custom_questions = request_json['questions']
            results = []
            
            for question in custom_questions:
                # Prepare the API URL
                api_url = f"https://dialogflow.googleapis.com/v3/projects/{project_id}/locations/{location}/agents/{agent_id}/sessions/test-session-{datetime.now().timestamp()}:detectIntent"
                
                # Prepare the request payload
                payload = {
                    "queryInput": {
                        "text": {
                            "text": question
                        },
                        "languageCode": "en"
                    }
                }
                
                # Set headers with authentication
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Make the API call
                response = requests.post(api_url, headers=headers, json=payload)
                response_data = response.json()
                
                # Extract the response text from the agent
                response_text = "No response text found"
                if "queryResult" in response_data and "responseMessages" in response_data["queryResult"]:
                    for msg in response_data["queryResult"]["responseMessages"]:
                        if "text" in msg and "text" in msg["text"]:
                            response_text = "\n".join(msg["text"]["text"])
                            break
                
                # Log to BigQuery
                log_data = {
                    "question": question,
                    "response_text": response_text,
                    "full_response": json.dumps(response_data),
                    "timestamp": datetime.now().isoformat()
                }
                
                log_to_bigquery(project_id, bq_dataset, bq_table, log_data)
                
                # Add to results
                results.append({
                    "question": question,
                    "response": response_text,
                    "status": response.status_code
                })
            
            return json.dumps({
                "status": "success",
                "results": results,
                "timestamp": datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            }), 500
    
    else:
        return json.dumps({
            "status": "error",
            "message": "Method not allowed"
        }), 405 