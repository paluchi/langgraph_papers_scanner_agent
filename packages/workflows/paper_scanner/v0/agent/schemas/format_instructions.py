from typing_extensions import Annotated, TypedDict, Optional, List, Dict
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import operator

# HERE LIES THE FORMAT INSTRUCTIONS FOR ALL AGENT NODES
# Subdivide file into different files when it gets too long
# ----------------------------


# Chunk processor
class ChunkProcessorMetadata(BaseModel):
    reasoning: str = Field(
        description="A very brief reasoning evaluating if the text contains metadata"
    )
    title: Optional[str] = Field(
        default=None, description="Title of the academic paper, if provided"
    )
    authors: Optional[List[str]] = Field(
        default=None, description="Authors of the academic paper, if provided"
    )
    publication_date: Optional[str] = Field(
        default=None, description="Publication date of the academic paper, if provided"
    )
    abstract: Optional[str] = Field(
        default=None, description="Abstract of the academic paper, if provided"
    )


class ChunkProcessorNewFinding(BaseModel):
    title: str = Field(description="Finding title")
    description: str = Field(
        description="Finding brief but exact description, be specific to avoid encompassing many findings"
    )


class ChunkProcessorExistingFinding(BaseModel):
    id: str = Field(description="Unique identifier of the finding to update")
    what_to_update: str = Field(description="What's the update needed for this finding")


class FindingsDetails(BaseModel):
    reasoning: str = Field(
        description="A reasoning of the possible matched or new findings"
    )
    findings_updates: List[ChunkProcessorExistingFinding] = Field(
        description="List of existing findings updates. Leave empty if no funding updates"
    )
    new_findings: List[ChunkProcessorNewFinding] = Field(
        description="List of new findings. Leave empty if no new findings"
    )


class ChunkProcessorAnalysis(BaseModel):
    findings: FindingsDetails = Field(description="Finding search analysis")
    metadata: ChunkProcessorMetadata = Field(
        description=("Metadata of the academic paper")
    )


# Finding creator
class NewFinding(BaseModel):
    title: str = Field(description="Title of the finding")
    summary: str = Field(
        description="Brief summary of the research finding (what it discusses? why it is important?)"
    )
    methodology: str = Field(
        description="Brief description of the methodology (how the research was conducted?)"
    )


# Finding updater
class FindingUpdate(BaseModel):
    title: Optional[str] = Field(
        description="Title of the finding. Leave empty if enough representative of the summary"
    )
    summary: Optional[str] = Field(
        description="Summary of the research finding. Leave empty if already representative"
    )
    methodology: Optional[str] = Field(
        description="Brief description of the methodology. Leave empty if already representative"
    )


# Findings consolidator
class ConsilidatedFinding(BaseModel):
    title: str = Field(description="Title of the finding")
    summary: str = Field(
        description="Brief summary of the research finding (what it discusses? why it is important?)"
    )
    methodology: str = Field(
        description="Brief description of the methodology (how the research was conducted?)"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Main keywords related to the finding"
    )


class FindingsConsolidator(BaseModel):
    findings: List[ConsilidatedFinding] = Field(
        description="List of consolidated findings"
    )
