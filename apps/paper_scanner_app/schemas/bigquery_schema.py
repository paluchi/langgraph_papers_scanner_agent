from google.cloud import bigquery
from typing import TypedDict, List, Optional

PAPER_SCANNER_SCHEMA = [
    bigquery.SchemaField(
        "metadata",
        "RECORD",
        mode="NULLABLE",
        fields=[
            bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("authors", "STRING", mode="REPEATED"),
            bigquery.SchemaField("publication_date", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("abstract", "STRING", mode="NULLABLE"),
        ],
    ),
    bigquery.SchemaField(
        "raw_findings",
        "RECORD",
        mode="REPEATED",
        fields=[
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("methodology", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("source_chunks_ids", "STRING", mode="REPEATED"),
        ],
    ),
    bigquery.SchemaField(
        "consolidated_findings",
        "RECORD",
        mode="REPEATED",
        fields=[
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("methodology", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("keywords", "STRING", mode="REPEATED"),
        ],
    ),
    bigquery.SchemaField(
        "chunks",
        "RECORD",
        mode="REPEATED",
        fields=[
            bigquery.SchemaField("chunk_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
        ],
    ),
    bigquery.SchemaField(
        "run_metadata",
        "RECORD",
        mode="NULLABLE",
        fields=[
            bigquery.SchemaField("start_execution", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("end_execution", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField(
                "status", "STRING", mode="NULLABLE"
            ),  # e.g., "SUCCESS", "FAILURE"
            bigquery.SchemaField("user_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("version", "STRING", mode="NULLABLE"),
        ],
    ),
]


class MetadataTypedDict(TypedDict, total=False):
    title: Optional[str]
    authors: List[str]
    publication_date: Optional[str]
    abstract: Optional[str]


class RawFindingTypedDict(TypedDict, total=False):
    id: str
    title: Optional[str]
    summary: Optional[str]
    methodology: Optional[str]
    source_chunks_ids: List[str]


class ConsolidatedFindingTypedDict(TypedDict, total=False):
    id: str
    title: Optional[str]
    summary: Optional[str]
    methodology: Optional[str]
    keywords: List[str]


class ChunkTypedDict(TypedDict, total=False):
    chunk_id: str
    content: Optional[str]


class RunMetadataTypedDict(TypedDict, total=False):
    start_execution: Optional[str]  # Replace with datetime if desired
    end_execution: Optional[str]  # Replace with datetime if desired
    status: Optional[str]
    user_name: Optional[str]
    version: Optional[str]


class PaperScannerSchema(TypedDict, total=False):
    metadata: Optional[MetadataTypedDict]
    raw_findings: List[RawFindingTypedDict]
    consolidated_findings: List[ConsolidatedFindingTypedDict]
    chunks: List[ChunkTypedDict]
    run_metadata: Optional[RunMetadataTypedDict]
