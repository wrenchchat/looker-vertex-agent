# Looker Vertex AI Agent File Structure

This document provides an overview of the repository structure after reorganization.

```
/looker-vertex-agent/
├── README.md                       # Main project documentation
│
├── src/                            # Source code
│   ├── api/                        # API Service components
│   │   ├── agent_api.py            # Main Flask application
│   │   ├── requirements.txt        # API dependencies
│   │   ├── Dockerfile              # Container definition for API
│   │   └── check_permissions.sh    # Authorization checks
│   │
│   ├── dashboard/                  # Dashboard components
│   │   ├── dashboard.py            # Streamlit dashboard
│   │   ├── requirements.txt        # Dashboard dependencies
│   │   └── run_dashboard.sh        # Dashboard start script
│   │
│   └── webhook/                    # Webhook service components
│       ├── main.py                 # Webhook handler
│       ├── requirements.txt        # Webhook dependencies
│       └── deploy.sh               # Deployment script
│
├── tests/                          # Testing components
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   ├── performance/                # Performance tests
│   ├── test_client.py              # Test client for API
│   ├── run_test_questions.py       # Test runner
│   ├── run_advanced_questions.py   # Advanced test runner
│   ├── analyze_results.py          # Results analyzer
│   └── test_questions.md           # Test question data
│
├── data/                           # Test results and visualization data
│   ├── results/                    # Test result CSV files
│   │   ├── test_results_mixed_questions.csv
│   │   ├── test_results_difficult_questions.csv
│   │   └── test_results_20_questions.csv
│   └── viz/                        # Visualization assets
│       ├── question_count_by_category.png
│       ├── response_time_by_category.png
│       ├── response_time_by_difficulty.png
│       └── response_time_distribution.png
│
├── config/                         # Configuration files
│   ├── playbooks/                  # Agent playbooks
│   │   ├── General Playbook.md
│   │   ├── Looker Playbook.md
│   │   ├── BigQuery Playbook.md
│   │   ├── Looker Studio Playbook.md
│   │   ├── dbt Playbook.md
│   │   └── Omni Playbook.md
│   ├── openapi/                    # OpenAPI specifications
│   │   ├── openapi.yaml
│   │   └── OpenAPI_Specification.md
│   ├── config.yaml                 # Main configuration
│   └── env.template                # Environment variable template
│
├── docs/                           # Project documentation
│   ├── development_plan.md         # Development plan document
│   ├── file_structure.md           # This file structure document
│   ├── integration/                # Integration documentation
│   │   └── slack_integration.md    # Slack integration docs
│   ├── deployment/                 # Deployment documentation
│   │   └── permission_setup.md     # Permission configuration
│   └── reports/                    # Project reports
│       ├── summary.md              # Project summary
│       ├── test_report.md          # Test results report
│       └── future_development.md   # Future development plans
│
├── tools/                          # Data store and utility tools
│   ├── data-stores/                # Data store creation tools
│   │   ├── bigquery/               # BigQuery data store
│   │   ├── dbt/                    # dbt data store
│   │   ├── looker/                 # Looker data store
│   │   ├── looker-studio/          # Looker Studio data store
│   │   └── omni/                   # Omni data store
│   ├── README.md                   # Tools documentation
│   └── openapi/                    # OpenAPI tools
│
└── reference/                      # Reference materials
    ├── vertex_ai/                  # Vertex AI documentation
    ├── dialogflow/                 # Dialogflow documentation
    ├── integrations/               # Integration documentation
    └── playbooks/                  # Playbooks reference
```

## Navigating the Repository

- **For Development**: Start with the `src/` directory that contains all the source code.
- **For Configuration**: Check the `config/` directory for configuration files.
- **For Documentation**: Refer to the `docs/` directory for project documentation.
- **For Testing**: Use the `tests/` directory for testing components.

## Key Files

- `src/api/agent_api.py`: The main Flask API for interacting with Vertex AI Agents
- `src/dashboard/dashboard.py`: The Streamlit dashboard for visualizing test results
- `tests/run_test_questions.py`: Script for running test questions against the API
- `config/config.yaml`: Main configuration file for the project