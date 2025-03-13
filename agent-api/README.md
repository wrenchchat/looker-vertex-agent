# Vertex AI Agent API

A Flask-based API server for interacting with Vertex AI Conversational Agents (Dialogflow CX).

## Features

- Simple REST API endpoints for interacting with your Vertex AI Agent
- Session management for continuous conversations
- Authentication with Google Cloud service accounts
- Dockerized deployment option
- Comprehensive error handling and logging

## Prerequisites

- Python 3.8+
- Google Cloud Project with a configured Vertex AI Conversational Agent (Dialogflow CX)
- Service account with appropriate permissions
- Google Cloud SDK (for permissions setup)

## Quick Start

### Local Installation

1. Clone the repository (if not already done)
2. Navigate to the agent-api directory:
   ```bash
   cd /Users/dionedge/dev/looker-vertex-agent/agent-api
   ```
3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
4. Set up your environment variables:
   ```bash
   # Copy the sample .env file and edit it with your settings
   cp .env.sample .env
   # Edit the .env file with your project details
   nano .env
   ```
5. Start the Flask server:
   ```bash
   python3 agent_api.py
   ```

### API Endpoints

#### GET /

Check if the API server is running.

**Response**:
```json
{
  "status": "active",
  "message": "Vertex AI Agent API is running"
}
```

#### POST /ask

Send a question to the Vertex AI Agent.

**Request**:
```json
{
  "question": "What are the best practices for data modeling in Looker?",
  "sessionId": "optional-session-id-for-continuous-conversation"
}
```

**Response**:
```json
{
  "question": "What are the best practices for data modeling in Looker?",
  "answer": "Here's a summary of best practices for data modeling in Looker: ...",
  "sessionId": "session-id-used-or-generated",
  "timestamp": "2023-09-09T12:34:56.789Z"
}
```

### Testing the API

You can test the API using the provided test script:

```bash
./test.sh
```

Or programmatically with the Python client:

```bash
python3 test_client.py --question "What are the best practices for data modeling in Looker?"
```

## Setting Up Permissions

If you encounter permission errors when accessing the Dialogflow CX API, you'll need to grant the appropriate roles to your service account. Use the provided script to check and fix permissions:

```bash
./check_permissions.sh
```

Follow the instructions provided by the script to add the necessary roles.

See [PERMISSION_SETUP.md](PERMISSION_SETUP.md) for detailed instructions on resolving permission issues.

## Deployment Options

### Docker Deployment

Build and run the Docker container:

```bash
# Build the Docker image
docker build -t vertex-ai-agent-api .

# Run the container
docker run -p 8080:8080 --env-file .env vertex-ai-agent-api
```

### Cloud Run Deployment

Deploy to Google Cloud Run:

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/vertex-ai-agent-api
gcloud run deploy vertex-ai-agent-api --image gcr.io/YOUR_PROJECT_ID/vertex-ai-agent-api --platform managed
```

### App Engine Deployment

1. Create an `app.yaml` file:
   ```yaml
   runtime: python39
   entrypoint: gunicorn -b :$PORT agent_api:app
   ```

2. Deploy to App Engine:
   ```bash
   gcloud app deploy
   ```

## Troubleshooting

See [PERMISSION_SETUP.md](PERMISSION_SETUP.md) for resolving permission issues.

Common issues:

1. **Connection refused**: The API server is not running. Start it with `python3 agent_api.py`.
2. **Permission denied**: The service account doesn't have the necessary permissions. Run `./check_permissions.sh`.
3. **Invalid credentials**: The credentials file is missing or invalid. Check your `.env` file.

## Project Status

See [SUMMARY.md](SUMMARY.md) for the current project status and next steps.

## Interactive Dashboard

The project includes an interactive dashboard to visualize the test results and analyze the performance of the Vertex AI Agent.

### Prerequisites

- Python 3.9 or later
- The following Python packages: `streamlit`, `plotly`, `pandas`

You can install these packages using:

```bash
pip3 install streamlit plotly pandas
```

### Running the Dashboard

You can launch the dashboard using the provided shell script:

```bash
./run_dashboard.sh
```

Or manually:

```bash
# Add streamlit to your PATH if needed
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
streamlit run dashboard.py
```

The dashboard will open in your default browser, typically at http://localhost:8501.

### Dashboard Features

- **Interactive Filtering**: Filter by category, difficulty, response time, etc.
- **Visual Analytics**: View charts and graphs showing response times, success rates, and more
- **Question Explorer**: Explore individual questions and answers
- **Raw Data**: Access and download the raw data for further analysis 