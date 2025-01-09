from google.cloud import bigquery
from typing import List

from apps.paper_scanner_app.schemas.bigquery_schema import PaperScannerSchema
from apps.paper_scanner_app.utils import (
    bigquery_credentials,
    BIGQUERY_TABLE_ID,
)


# Retrieves all runs from the BigQuery table
def retrieve_runs(
    user_name: str = None, status: str = None
) -> List[PaperScannerSchema]:
    """
    Retrieves runs from the BigQuery table based on optional filters.

    Args:
        user_name (str, optional): Filter by user name. Defaults to None.
        status (str, optional): Filter by run status (e.g., "SUCCESS", "FAILURE"). Defaults to None.

    Returns:
        List[Dict]: A list of dictionaries representing the retrieved runs.
    """
    client = bigquery.Client(credentials=bigquery_credentials)

    # Base query
    query = f"SELECT * FROM `{BIGQUERY_TABLE_ID}`"

    # Add optional filters
    conditions = []
    if user_name:
        conditions.append(f"user_name = '{user_name}'")
    if status:
        conditions.append(f"run_metadata.status = '{status}'")

    if conditions:
        query += f" WHERE {' AND '.join(conditions)}"

    # Execute query
    query_job = client.query(query)
    results = query_job.result()

    # Convert results to a list of dictionaries
    runs = [dict(row) for row in results]

    return runs
