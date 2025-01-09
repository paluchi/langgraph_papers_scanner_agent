import logging
from typing import TypedDict
from google.cloud import bigquery

from apps.paper_scanner_app.utils import (
    bigquery_credentials,
    BIGQUERY_TABLE_ID,
)
from packages.workflows.paper_scanner.v0.agent.schemas.states import OverallState


class RunMetadata(TypedDict):
    start_execution: str
    end_execution: str
    status: str  # "SUCCESS" or "ERROR"
    user_name: str
    version: str


def store_to_bigquery(
    state: OverallState,
    run_metadata: RunMetadata,
) -> None:
    """
    Formats the input state and run metadata, and stores them in BigQuery.

    Args:
        state (OverallState): The overall state containing metadata, findings, and chunks.
        run_metadata (RunMetadata): Metadata about the run execution.
    """

    client = bigquery.Client(credentials=bigquery_credentials)

    # Format the data to match the BigQuery schema
    row = {
        "metadata": {
            "title": state["metadata"].get("title"),
            "authors": state["metadata"].get("authors", []),
            "publication_date": state["metadata"].get("publication_date"),
            "abstract": state["metadata"].get("abstract"),
        },
        "raw_findings": [
            {
                "id": finding["id"],
                "title": finding.get("title"),
                "summary": finding.get("summary"),
                "methodology": finding.get("methodology"),
                "source_chunks_ids": finding.get("source_chunks_ids", []),
            }
            for finding in state.get("findings", [])
        ],
        "consolidated_findings": [
            {
                "id": finding["id"],
                "title": finding.get("title"),
                "summary": finding.get("summary"),
                "methodology": finding.get("methodology"),
                "keywords": finding.get("keywords", []),
            }
            for finding in state.get("consolidated_findings", [])
        ],
        "chunks": [
            {
                "chunk_id": chunk["chunk_id"],
                "content": chunk.get("content"),
            }
            for chunk in state.get("processed_chunks", [])
        ],
        "run_metadata": {
            "start_execution": run_metadata["start_execution"],
            "end_execution": run_metadata["end_execution"],
            "status": run_metadata["status"],
            "user_name": run_metadata["user_name"],
            "version": run_metadata["version"],
        },
    }

    # Insert the row into BigQuery
    logging.info(f"Inserting row into BigQuery table: {BIGQUERY_TABLE_ID}")
    errors = client.insert_rows_json(BIGQUERY_TABLE_ID, [row])
    if errors:
        raise Exception(f"Failed to insert row into BigQuery: {errors}")
    else:
        logging.info(f"Inserted row into BigQuery")
