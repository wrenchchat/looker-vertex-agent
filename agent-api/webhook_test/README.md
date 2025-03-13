# Vertex AI Agent Testing

## Summary of Findings

After attempting several methods to test the Vertex AI Agent programmatically, we've identified the following:

1. **Permission Issues**: The service account credentials don't have the necessary permissions for direct API access to the Dialogflow CX API (`dialogflow.sessions.detectIntent`) or the Vertex AI API (`aiplatform.endpoints.predict`).

2. **API Configuration**: The correct API endpoints require proper configuration with valid project ID, location, and agent ID parameters.

3. **Authentication Method**: Using service account keys requires specific permissions that need to be granted in the Google Cloud IAM settings.

## Recommended Testing Approaches

### 1. Web Interface Testing (Recommended)

The most reliable way to test your agent is through the Google Cloud Console web interfaces:

- **Dialogflow CX Console**: Test using the built-in "Test Agent" feature
- **Vertex AI Agent Builder**: Test using the testing interface in the Agent Builder 

See detailed instructions in the [test_instructions.md](./test_instructions.md) file.

### 2. API Testing (After Permission Setup)

To enable API testing, the following steps need to be completed:

1. Open the [Google Cloud IAM Admin](https://console.cloud.google.com/iam-admin) page
2. Find the service account being used for testing
3. Grant the following roles:
   - `Dialogflow API Client`
   - `Dialogflow API Admin` (if you need write access)
   - `Vertex AI User`

After configuring permissions, our test scripts can be used:
- `quick_test.py`: Simple Python script for testing via Dialogflow API
- `direct_test.py`: More detailed script with fallback options
- `conversation_test.py`: Tests via Vertex AI Conversation API
- `simple_test.sh`: Simple curl-based test for web endpoints

## Next Steps

1. Complete the permissions setup in Google Cloud IAM
2. Verify the agent works using the web interface methods 
3. Re-run the test scripts to confirm API access is working
4. Continue with the implementation of the webhook infrastructure

## Project Structure

```
webhook_test/
├── README.md                 # This overview document
├── test_instructions.md      # Step-by-step guide for web-based testing
├── requirements-quick.txt    # Dependencies for quick_test.py
├── requirements-direct.txt   # Dependencies for comprehensive testing
├── quick_test.py             # Basic Python test script
├── direct_test.py            # Comprehensive Python test script
├── conversation_test.py      # Vertex AI Conversation test
├── simple_test.sh            # Curl-based web endpoint test
├── test_curl.sh              # Curl-based API test
└── main.py                   # Cloud Function webhook (to be implemented)
```

## Features

- Sends predefined test questions to your Vertex AI agent
- Handles custom questions via POST requests
- Stores all questions and responses in BigQuery
- Compatible with Cloud Scheduler for regular testing
- Detailed response logging and error handling
- Visualization and analysis of test results

## Quick Start

```bash
# Navigate to this directory
cd /Users/dionedge/dev/looker-vertex-agent/webhook_test

# Make shell scripts executable
chmod +x *.sh

# Deploy the Cloud Function
./deploy.sh

# Set up scheduled testing (optional)
./setup_scheduler.sh

# Monitor the health of the webhook
./monitor_health.sh

# Analyze test results (after collecting some data)
python analyze_results.py
```

## File Overview

- `main.py` - Core Cloud Function code that tests the Vertex AI agent
- `local_test.py` - Script for testing locally before deployment
- `deploy.sh` - Script to deploy the Cloud Function to GCP
- `setup_scheduler.sh` - Script to set up Cloud Scheduler for regular testing
- `monitor_health.sh` - Script to check the health of the webhook
- `analyze_results.py` - Script to analyze and visualize test results
- `requirements.txt` - Required Python dependencies

## Detailed Instructions

### 1. Local Testing

Before deploying to GCP, you can test the webhook locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the local Flask server
python local_test.py
```

This starts a local server at http://localhost:8080 where you can test the webhook.

### 2. Deployment to Cloud Functions

You can deploy the webhook using the provided script:

```bash
./deploy.sh
```

Or manually with gcloud:

```bash
gcloud functions deploy vertex-agent-tester \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=test_vertex_agent \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=PROJECT_ID=heuristicsai,LOCATION=global,VERTEX_AI_APP_ID=8285e0d0-24ae-43e9-8491-b0bd99befc87,BIGQUERY_DATASET=conversations,BIGQUERY_TABLE=bia
```

### 3. Set Up Scheduled Testing

To run tests on a regular schedule, use the provided script:

```bash
./setup_scheduler.sh
```

You can customize the schedule by setting environment variables:

```bash
SCHEDULE="0 */3 * * *" TIMEZONE="America/New_York" ./setup_scheduler.sh
```

This example would run tests every 3 hours.

### 4. Monitor Webhook Health

You can check the health of your webhook using:

```bash
./monitor_health.sh
```

This script verifies:
- If the Cloud Function exists and is active
- If the function responds to test requests
- If Cloud Scheduler jobs are set up
- If BigQuery is receiving data

### 5. Analyze Test Results

After collecting test data, you can analyze and visualize the results:

```bash
python analyze_results.py
```

This generates visualizations in the `./results` directory, including:
- Response length distribution
- Response length over time
- Tests per day
- Top questions
- Summary statistics

You can customize the analysis with options:

```bash
python analyze_results.py --days 30 --output-dir ./my_results
```

## Usage Examples

### Running Predefined Tests

To run the predefined test questions, send a GET request to your Cloud Function URL:

```bash
curl https://your-function-url.cloudfunctions.net/vertex-agent-tester
```

### Running Custom Tests

To test with custom questions, send a POST request with JSON:

```bash
curl -X POST \
  https://your-function-url.cloudfunctions.net/vertex-agent-tester \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "How do I create a calculated field in Looker?",
      "What is the difference between a view and an explore?"
    ]
  }'
```

### Viewing Results in BigQuery

The results are stored in your BigQuery table:

```sql
SELECT 
  question, 
  response_text, 
  timestamp 
FROM 
  `heuristicsai.conversations.bia`
ORDER BY 
  timestamp DESC
LIMIT 
  100
```

## Customizing Test Questions

To modify the predefined test questions, edit the `TEST_QUESTIONS` array in the `main.py` file.

## Troubleshooting

If you encounter errors:

1. Check the Cloud Function logs in the GCP Console
2. Run `./monitor_health.sh` to diagnose issues
3. Verify that your Vertex AI agent ID is correct
4. Ensure the service account has appropriate permissions
5. Confirm that BigQuery dataset and table exist

## Next Steps

After setting up the webhook, consider:

1. Creating a Looker Studio dashboard to visualize the test results
2. Setting up alerts for failed tests or unexpected responses
3. Expanding the test question set to cover more scenarios
4. Adding sentiment analysis of responses to evaluate tone
5. Implementing A/B testing for different agent configurations 