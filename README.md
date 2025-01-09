# Papers Scanner Project

## Introduction

This project is designed to automate the process of analyzing research papers. It extracts key insights, summarizes the content, and identifies relevant keywords and metadata. This tool aims to streamline literature review and accelerate research by providing quick access to essential information within academic papers.

## Initialize Environment

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management ([Installation instructions](https://python-poetry.org/docs/#installation))

#### Prerequisites To deploy

- Docker (for containerized deployment) ([Installation instructions](https://docs.docker.com/get-docker/))
- Google Cloud CLI (gcloud) (for cloud deployment) ([Installation instructions](https://cloud.google.com/sdk/docs/install))
- Set up your GCP account, project and follow below deployment section.

### Installation Steps

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

2. Install dependencies using Poetry:

```bash
poetry install
```

### Environment Setup

1. Create and populate an `.env` file in the root directory of the project.

```shell
# Development Mode
IS_DEV=True

# Google Credentials
GOOGLE_API_KEY=your_google_api_key
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json

# BigQuery Configuration
BIGQUERY_TABLE_ID=your_bigquery_table_id
BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS=credentials/bigquery-service-account.json

# Langchain Configuration
LANGCHAIN_TRACING_V2=true        # Enable Langchain tracing
LANGCHAIN_ENDPOINT=your_langchain_endpoint          # LangSmith endpoint
LANGCHAIN_API_KEY=your_langchain_api_key           # LangSmith API key
LANGCHAIN_PROJECT=your_langchain_project_name      # LangSmith project name

# DataLab
DATALAB_API_KEY=your_datalab_api_key
```

#### Environment Variables Description:

- `IS_DEV`: Boolean flag to indicate development mode
- `GOOGLE_API_KEY`: Your Google API key for accessing Google services (e.g., Gemini API)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud service account credentials JSON file
- `BIGQUERY_TABLE_ID`: Your BigQuery table identifier
- `BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS`: Path to BigQuery-specific service account credentials
- `LANGCHAIN_TRACING_V2`: Enable or disable tracing for Langchain debugging
- `LANGCHAIN_ENDPOINT`: The endpoint for your Langchain tracing server (LangSmith)
- `LANGCHAIN_API_KEY`: The API key for your Langchain tracing server
- `LANGCHAIN_PROJECT`: The name of your Langchain project
- `DATALAB_API_KEY`: API key for DataLab services

**Note:** I used different credentials for BigQuery and LLM usage, but should use the same.

### Debugging and Testing

#### Debugging with LangGraph

You can use the `langgraph dev` command to debug your LangChain applications. This integrates with LangSmith to provide visibility into your LangChain execution:

```bash
langgraph dev
```

This will give you access to the LangSmith interface where you can:

- Track and debug your LangChain executions
- View detailed traces of your chains and agents
- Monitor performance and usage

#### Running Tests

Tests are located in the `tests` directory and can be run using pytest through Poetry:

```bash
# Run specific test file
poetry run pytest -s tests/workflows/paper_scanner.py
```

For testing the scanner with local files:

1. Edit the file paths inside the test code to point to your test PDF or markdown file
2. Run the specific test file as shown above

#### Running Local app

```bash
# You had to set up a bigQuery table before and set the environments, otherwise run local test for testing
poetry run paper_scanner_app
```

### Deployment to Google Cloud Platform (GCP)

Follow these steps to deploy a production version to GCP:

1. Initial GCP Setup:

```bash
# Create and set a new GCP project
gcloud config set project [PROJECT_ID]

# Enable required services
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com
```

2. Enable billing for your project through GCP Console

3. Create bigQuery table and set relative environments

4. Build and Push Docker Container:

```bash
# Build container
# Need to debug as the container weight is very high when running for linux/amd64
docker build --platform linux/amd64 -t gcr.io/[PROJECT_ID]/streamlit-app:latest .

# Configure docker authentication
gcloud auth configure-docker

# Push to Google Container Registry
docker push gcr.io/[PROJECT_ID]/streamlit-app:latest

# optionally (Test Docker locally)
docker run -e PORT=8080 -p 8080:8080 --env-file .env gcr.io/[PROJECT_ID]/streamlit-app:latest
```

3. Deploy to Cloud Run:

```bash
# After loading envs inside .env create env.yaml file (for a productive env. you should use google secrets manager for envs and credentials)
awk -F= '!/^#/ && NF > 0 { print $1 ": " $2 }' .env > env.yaml

# Deploy to cloud run
gcloud run deploy streamlit-app \
    --image gcr.io/[PROJECT_ID]/streamlit-app:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --env-vars-file env.yaml
```

### Available Scripts

The application includes several utility scripts to manage different tasks:

- `paper_scanner_app`: Launches the Streamlit application locally for interactive analysis

```bash
poetry run paper_scanner_app
```
