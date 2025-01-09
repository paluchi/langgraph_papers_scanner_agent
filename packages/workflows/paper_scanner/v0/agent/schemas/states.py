from typing_extensions import Annotated, TypedDict, Optional, List, Dict
from enum import Enum
from pydantic import Field
import operator

from packages.workflows.paper_scanner.v0.agent.schemas.format_instructions import (
    ChunkProcessorAnalysis,
)

# HERE LIES THE STATES SCHEMAS
# Subdivide file into different files when it gets too long
# ----------------------------


class ChunkStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class ChunkInfo(TypedDict):
    chunk_id: str
    content: str
    status: ChunkStatus
    analysis: Optional[ChunkProcessorAnalysis] = None


class PaperMetadata(TypedDict):
    title: str = Field(default=None, description="Title of the academic paper")
    authors: str = Field(default=None, description="Authors of the academic paper")
    publication_date: str = Field(
        default=None, description="Publication date of the academic paper"
    )
    abstract: str = Field(default=None, description="Abstract of the academic paper")
    source_chunks_ids: List[str] = Field(default_factory=list)


class Finding(TypedDict):
    id: str = Field(description="Unique identifier of the finding")
    title: str = Field(description="Title of the finding")
    summary: str = Field(description="Summary of the research finding")
    methodology: str = Field(description="Brief description of the methodology")
    keywords: List[str] = Field(
        default_factory=list, description="Main keywords related to the finding"
    )
    source_chunks_ids: Annotated[List[str], operator.add] = Field(
        default_factory=list, description="List of source chunk IDs"
    )


# Below method is used to append new findings to the existing findings list and update the existing findings if the finding already exists.
def merge_findings(
    existing_findings: List[Finding], new_findings: List[Finding]
) -> List[Finding]:
    # Create a dictionary for efficient lookup of existing findings by ID
    findings_dict: Dict[str, Finding] = {f["id"]: f for f in existing_findings}

    for finding in new_findings:
        if finding["id"] in findings_dict:
            # Update the existing finding only for non-null values
            existing = findings_dict[finding["id"]]
            update_dict = {}

            if finding.get("title"):
                update_dict["title"] = finding["title"]
            if finding.get("summary"):
                update_dict["summary"] = finding["summary"]
            if finding.get("methodology"):
                update_dict["methodology"] = finding["methodology"]

            existing.update(update_dict)

            # Merge keywords if they exist in both findings
            if "keywords" in finding and "keywords" in existing:
                existing["keywords"] = list(
                    set(existing["keywords"] + finding["keywords"])
                )
            # If keywords only exist in the new finding, add them
            elif "keywords" in finding:
                existing["keywords"] = finding["keywords"]

            # Merge source_chunks_ids
            existing["source_chunks_ids"] = list(
                set(existing["source_chunks_ids"] + finding["source_chunks_ids"])
            )
        else:
            # Add new finding
            # Ensure the finding has a keywords field even if empty
            if "keywords" not in finding:
                finding["keywords"] = []
            findings_dict[finding["id"]] = finding

    # Return the updated list of findings
    return list(findings_dict.values())


class InputState(TypedDict):
    chunks: List[str] = Field(description="List of chunks to process")


class findingCreatorState(TypedDict):
    chunk: ChunkInfo = Field(description="Current chunk being processed")
    description: str = Field(description="Description of the new finding")


class findingUpdaterState(TypedDict):
    chunk: ChunkInfo = Field(description="Current chunk being processed")
    finding: Finding = Field(description="Finding to update")
    what_to_update: str = Field(description="What to update in the finding")


def merge_metadata(
    existing_metadata: PaperMetadata, new_metadata: PaperMetadata
) -> PaperMetadata:

    # Only merge if new metadata is provided for each field and existing metadata is not already present
    new_metadata = {
        "title": (
            existing_metadata.get("title")
            if existing_metadata.get("title")
            else new_metadata.get("title")
        ),
        "authors": (
            existing_metadata.get("authors")
            if existing_metadata.get("authors")
            else new_metadata.get("authors")
        ),
        "publication_date": (
            existing_metadata.get("publication_date")
            if existing_metadata.get("publication_date")
            else new_metadata.get("publication_date")
        ),
        "abstract": (
            existing_metadata.get("abstract")
            if existing_metadata.get("abstract")
            else new_metadata.get("abstract")
        ),
        "source_chunks_ids": list(
            existing_metadata.get("source_chunks_ids", [])
            + new_metadata.get("source_chunks_ids", [])
        ),
    }

    return new_metadata


class OverallState(TypedDict):
    metadata: Annotated[PaperMetadata, merge_metadata] = Field(
        description="Metadata of the academic paper"
    )
    findings: Annotated[List[Finding], merge_findings] = Field(
        description="List of findings with merge functionality"
    )
    consolidated_findings: List[Finding] = Field(
        description="List of consolidated findings"
    )
    chunks_queue: List[ChunkInfo] = Field(description="Queue of chunks to be processed")
    current_chunk: Optional[ChunkInfo] = Field(
        default=None, description="Current chunk being processed"
    )
    processed_chunks: List[ChunkInfo] = Field(description="List of processed chunks")
