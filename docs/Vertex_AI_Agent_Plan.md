# Vertex AI Agent

## Objective

We are building an agent in Vertex AI Agent Builder to help Looker customers, including Admins, Developers, and Power Users. The Conversational Agent (Dialogflow CX) framework utilizes a Generative AI model and consists of Playbooks and Tools. Playbooks are YAML files that describe how agents collaborate to solve customer problems using Tools and/or other agents. Available tools include:

- **Data Stores**: Domain-specific knowledge accessible to agents via RAG
- **OpenAPI**: Provides access to Gemini 2, Google's most advanced AI model
- **Code-Interpreter**: Enables agents to write code to solve customer problems

The agent will be accessible to customers via Slack.

## Structure

We will implement six Playbooks, each containing an Agent with specific Tools:

```
- Generalist-Playbook (Routine)
    - Generalist-Agent
        - OpenAPI
        - Code-Interpreter
- Looker-Playbook (Task)
    - Looker-Agent
        - looker-ds
        - OpenAPI
        - Code-Interpreter
- BigQuery-Playbook (Task)
    - BigQuery-Agent
        - bigquery-ds
        - OpenAPI
        - Code-Interpreter
- Looker-Studio-Playbook (Task)
    - Looker-Studio-Agent
        - looker-studio-ds
        - OpenAPI
        - Code-Interpreter
- dbt-Playbook (Task)
    - dbt-Agent
        - dbt-ds
        - OpenAPI
        - Code-Interpreter
- Omni-Playbook (Task)
    - Omni-Agent
        - omni-ds
        - OpenAPI
        - Code-Interpreter
```

## Implementation Plan

### 1. Data Store Creation

First, we need to build five Data Stores (Looker, Looker-Studio, BigQuery, dbt, and Omni) and populate them with data from three sources:
- API documentation
- Help documentation
- GitHub repositories

We'll use Puppeteer to scrape data from appropriate URLs and flatten designated repositories for code file access.

#### Current Status:

| Product      | GitHub Repos | Scrape APIs | Scrape Docs |
|--------------|--------------|-------------|-------------|
| Looker       | See Note-1   | Completed   | Completed   |
| Looker-Studio| See Note-2   | Pending     | Pending     |
| BigQuery     | See Note-3   | Pending     | Pending     |
| dbt          | See Note-4   | Pending     | Pending     |
| Omni         | See Note-5   | Pending     | Pending     |

**Notes:**
1. Repositories downloaded to `/Users/dionedge/dev/looker-vertex-agent/tools/data-stores/looker/repos`; need to be flattened into `/looker/repo`
2. Repositories downloaded to `/Users/dionedge/dev/looker-vertex-agent/tools/data-stores/looker-studio/repos`; need to be flattened into `/looker-studio/repo`
3. Repositories downloaded to `/Users/dionedge/dev/looker-vertex-agent/tools/data-stores/bigquery/repos`; need to be flattened into `/bigquery/repo`
4. Repositories downloaded to `/Users/dionedge/dev/looker-vertex-agent/tools/data-stores/dbt/repos`; need to be flattened into `/dbt/repos`
5. Repositories downloaded to `/Users/dionedge/dev/looker-vertex-agent/tools/data-stores/omni/repos`; need to be flattened into `/omni/repos`

### 2. Documentation Scraping Rules

#### General Rules
- **Docs**: Depth=2, convert baseline URL to markdown, click every URL on the baseline page and convert those pages to markdown
- **API**: Depth=2, convert baseline URL to markdown, click every URL on the baseline page and convert those pages to text
- **Repos**: Flatten repository, exclude common files, append all remaining files with .txt extension

#### Product-Specific URLs

**Looker-Studio**
- Docs:
  - https://developers.google.com/looker-studio/connector
  - https://developers.google.com/looker-studio/visualization
  - https://developers.google.com/looker-studio/integrate
- API:
  - https://developers.google.com/looker-studio/integrate/api

**BigQuery**
- Docs:
  - https://cloud.google.com/bigquery/docs/introduction
  - https://cloud.google.com/bigquery/docs/developer-overview
- API:
  - https://cloud.google.com/bigquery/docs/reference/libraries
  - https://cloud.google.com/bigquery/docs/reference/bigquerydatapolicy/rest
  - https://cloud.google.com/bigquery/docs/reference/bigqueryconnection
  - https://cloud.google.com/bigquery/docs/reference/storage/libraries
  - https://cloud.google.com/bigquery/docs/reference/reservations
  - https://cloud.google.com/bigquery/docs/reference/analytics-hub/rest
  - https://cloud.google.com/bigquery/docs/reference/datatransfer/libraries

**Omni**
- Docs:
  - https://omni.co/blog
- API:
  - https://docs.omni.co/docs

**dbt**
- Docs:
  - https://docs.getdbt.com/reference/references-overview
  - https://docs.getdbt.com/guides
  - https://docs.getdbt.com/best-practices
- API:
  - https://docs.getdbt.com/dbt-cloud/api-v2#/

## Project Infrastructure: heuristicsai

### Cloud Storage Buckets
- gs://bia-bigquery
- gs://bia-conversations
- gs://bia-dbt
- gs://bia-looker
- gs://bia-looker-studio
- gs://bia-omni

### Data Stores
- bigquery-ds
- dbt-ds
- looker-ds
- looker-studio-ds
- omni-ds

### BigQuery
- heuristicsai.conversations.bia

### Parser Configuration
We will use the Digital parser for all Data Stores. The Digital parser:
- Is enabled by default for all file types
- Processes ingested documents when no other default parser is specified
- Supports markdown files

Note: A GCP service account with appropriate permissions is available in Keychain for uploading data to our buckets.
A GitHub repo was created for this project: https://github.com/wrenchchatrepo/looker-vertex-agent.