# Looker Vertex AI Agent

A conversational AI agent built on Google's Vertex AI platform, specializing in Looker, BigQuery, and data analytics assistance.

## Project Overview

This project implements a conversational interface to help users with Looker, BigQuery, dbt, Looker Studio, Omni and related data technologies. The system consists of:

1. **API Server**: A Flask-based API that connects to Google's Vertex AI Conversational Agents (Dialogflow CX)
2. **Analytics Dashboard**: A Streamlit dashboard for monitoring agent performance metrics
3. **Webhook Service**: A Cloud Function for scheduled testing and logging responses to BigQuery

## Features

- **Multi-Domain Knowledge**: Specialized knowledge bases for Looker, BigQuery, dbt, Looker Studio, and Omni
- **Natural Language Understanding**: Uses Vertex AI's powerful LLM capabilities to understand and respond to complex data queries
- **Performance Analytics**: Comprehensive dashboard for monitoring agent performance, response times, and accuracy
- **Integration Testing**: Automated testing framework with questions of varying difficulty and categories
- **Slack Integration**: Connects the agent to Slack workspaces (in development)

## Repository Structure

- **agent-api/**: API component, testing framework, and webhooks
  - **scripts/**: Core API scripts and utilities
  - **tests/**: Test framework and question datasets
  - **webhook_test/**: Webhook implementation for automated testing
  - **data/**: Test results and metrics
  - **viz/**: Visualization assets for the dashboard

- **src/**: Source code reorganized for production
  - **api/**: Production-ready Flask API server
  - **dashboard/**: Streamlit analytics dashboard
  - **webhook/**: Production webhook service

- **config/**: Configuration and knowledge base definitions
  - **playbooks/**: Domain-specific knowledge configurations
  - **openapi/**: API specifications and documentation

- **docs/**: Project documentation
  - **deployment/**: Deployment guides and instructions
  - **integration/**: Integration documentation
  - **reports/**: Project summaries and test reports

- **tools/**: Utilities for knowledge base creation
  - **data-stores/**: Domain-specific knowledge repositories
  - Scripts for document scraping and bucket management

- **scripts/**: Utility scripts for setup and management
  - Repository setup, authentication, and data upload utilities

- **slack/**: Slack integration components (in development)

## Getting Started

### Prerequisites

- Python 3.8+
- Google Cloud Platform account with enabled APIs:
  - Vertex AI API
  - Dialogflow CX API
  - Cloud Storage
  - BigQuery
- Google Cloud SDK installed and configured

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/your-org/looker-vertex-agent.git
   cd looker-vertex-agent
   ```

2. Set up GCP authentication
   ```bash
   ./scripts/setup-gcp-auth.sh
   ```

3. Install API dependencies
   ```bash
   cd src/api
   pip install -r requirements.txt
   ```

4. Start the API server
   ```bash
   python agent_api.py
   ```

### Running the Dashboard

The dashboard provides analytics on agent performance and test results.

```bash
cd src/dashboard
./run_dashboard.sh
```

### Testing the Agent

Run the test suite against the agent to evaluate performance:

```bash
cd agent-api/scripts
python run_test_questions.py
```

Analyze test results:

```bash
python analyze_results.py
```

## Deployment

See detailed deployment instructions in `docs/deployment/`.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Cloud Vertex AI team
- Looker, BigQuery, and Google Cloud documentation contributors