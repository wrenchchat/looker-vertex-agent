# Looker Vertex AI Agent

A conversational AI agent built on Google's Vertex AI platform, specializing in Looker, BigQuery, and data analytics assistance.

## Project Overview

This project provides a conversational interface to help users with Looker, BigQuery, dbt, Looker Studio, and related data technologies. The system consists of a Flask-based API that connects to Google's Vertex AI Conversational Agents (Dialogflow CX), an analytics dashboard for monitoring performance, and comprehensive testing tools.

## Directory Structure

- **src/**: Source code
  - **api/**: Flask API for the Vertex AI Agent
  - **dashboard/**: Streamlit dashboard for agent analytics
  - **webhook/**: Webhook service for agent integrations

- **tests/**: Testing components
  - **unit/**: Unit tests
  - **integration/**: Integration tests
  - **performance/**: Performance testing scripts
  - Test utilities and question datasets

- **data/**: Test results and visualization assets
  - **results/**: CSV files containing test results
  - **viz/**: Generated visualization images

- **config/**: Configuration files
  - **playbooks/**: Agent knowledge base playbooks
  - **openapi/**: API specifications
  - Main configuration files

- **docs/**: Project documentation
  - **integration/**: Integration guides
  - **deployment/**: Deployment documentation
  - **reports/**: Project reports and summaries

- **tools/**: Data store and utility tools
  - Tools for preparing and uploading data to agent knowledge bases

- **reference/**: Reference materials
  - Documentation for Vertex AI, Dialogflow, and related technologies

## Getting Started

### Prerequisites

- Python 3.8+
- Google Cloud Platform account with enabled APIs:
  - Vertex AI API
  - Dialogflow CX API
  - Cloud Storage

### Installation

1. Clone the repository
2. Set up the environment:
   ```bash
   # Install API dependencies
   cd src/api
   pip install -r requirements.txt
   ```

3. Configure your Google Cloud credentials
4. Start the API server:
   ```bash
   python agent_api.py
   ```

### Running the Dashboard

```bash
cd src/dashboard
./run_dashboard.sh
```

### Running Tests

```bash
cd tests
python run_test_questions.py
```

## License

[Specify your license here]

## Acknowledgments

- Google Cloud Vertex AI team
- Looker documentation contributors