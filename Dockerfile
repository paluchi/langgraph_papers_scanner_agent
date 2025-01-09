# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Define build arguments
ARG IS_DEV
ARG GOOGLE_API_KEY
ARG GOOGLE_APPLICATION_CREDENTIALS
ARG BIGQUERY_TABLE_ID
ARG BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS
ARG LANGCHAIN_TRACING_V2
ARG LANGCHAIN_ENDPOINT
ARG LANGCHAIN_API_KEY
ARG LANGCHAIN_PROJECT
ARG DATALAB_API_KEY

# Set environment variables from build arguments
ENV IS_DEV=${IS_DEV} \
    GOOGLE_API_KEY=${GOOGLE_API_KEY} \
    GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} \
    BIGQUERY_TABLE_ID=${BIGQUERY_TABLE_ID} \
    BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS=${BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS} \
    LANGCHAIN_TRACING_V2=${LANGCHAIN_TRACING_V2} \
    LANGCHAIN_ENDPOINT=${LANGCHAIN_ENDPOINT} \
    LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY} \
    LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT} \
    DATALAB_API_KEY=${DATALAB_API_KEY}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set environment variables for Poetry and Streamlit
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false

# Set the working directory
WORKDIR /app

# Copy Poetry files first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install dependencies without the project (dependency-only mode first)
RUN poetry install --no-root

# Copy the entire application code
COPY . /app

# Re-install the project to include the app itself
RUN poetry install

# Add the current directory to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Run the Streamlit app
CMD ["poetry", "run", "streamlit", "run", "apps/paper_scanner_app/app.py", "--server.port=8080"]
