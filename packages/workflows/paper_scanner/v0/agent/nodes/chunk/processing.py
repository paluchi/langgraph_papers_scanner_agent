from packages.workflows.paper_scanner.v0.agent.schemas.format_instructions import (
    ChunkProcessorAnalysis,
)
from packages.workflows.paper_scanner.v0.agent.prompt_templates import (
    discovery_prompt,
)
from packages.workflows.paper_scanner.v0.agent.schemas.states import OverallState
from packages.workflows.paper_scanner.v0.utils.call_llm import call_llm
from langgraph.types import Send


# This node processes the chunk using the LLM and routes to the appropriate nodes to create and update findings and update metadata
def chunk_processor(state: OverallState):
    # Take the current_chunk
    current_chunk = state["current_chunk"]

    # Format existing findings with respetive id, title, summary into a text
    ### Id: <id>
    ### Title: <title>
    ### Summary: <summary>
    ### ...
    existing_findings = "".join(
        [
            f"Id: {finding['id']}\nTitle: {finding['title']}\nSummary: {finding['summary']}\n\n"
            for finding in state["findings"]
        ]
    )
    if len(state["findings"]) == 0:
        existing_findings = "No existing findings yet"

    # Process the chunk using the LLM
    analysis_result: ChunkProcessorAnalysis = call_llm(
        prompt_template=discovery_prompt,
        input_parameters={
            "text": current_chunk["content"],
            "existing_findings": existing_findings,
        },
        pydantic_object=ChunkProcessorAnalysis,
    )

    state["current_chunk"]["analysis"] = analysis_result

    return state


def search_finding_by_id(state: OverallState, finding_id: str):
    for finding in state["findings"]:
        if finding["id"] == finding_id:
            return finding
    return None


def post_processing_router(state: OverallState):
    # Take the current_chunk
    current_chunk_analysis = state["current_chunk"]["analysis"]

    # For each finding create a langgraph send query pointing to 'finding_router'
    branches = []
    for finding in current_chunk_analysis["findings"]["findings_updates"]:
        existing_finding = search_finding_by_id(state, finding["id"])
        if not finding:
            raise ValueError(f"Finding with id {finding['id']} not found")
        branches.append(
            Send(
                "finding_updater",
                {
                    "chunk": state["current_chunk"],
                    "finding": existing_finding,
                    "what_to_update": finding["what_to_update"],
                },
            )
        )

    for finding in current_chunk_analysis["findings"]["new_findings"]:
        branches.append(
            Send(
                "finding_creator",
                {
                    "chunk": state["current_chunk"],
                    "title": finding["title"],
                    "description": finding["description"],
                },
            )
        )

    # If any medata element is present send add a branch to 'metadata_updater'
    metadata = current_chunk_analysis["metadata"]
    if any(metadata.values()):
        branches.append(Send("metadata_updater", metadata))

    if len(branches) == 0:
        branches.append(Send("processing_sink", state))

    return branches
