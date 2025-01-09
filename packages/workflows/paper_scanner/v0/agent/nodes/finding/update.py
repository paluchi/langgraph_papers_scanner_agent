from packages.workflows.paper_scanner.v0.utils.call_llm import call_llm

from packages.workflows.paper_scanner.v0.agent.schemas.format_instructions import (
    FindingUpdate,
)
from packages.workflows.paper_scanner.v0.agent.schemas.states import (
    Finding,
    OverallState,
    findingUpdaterState,
)

from packages.workflows.paper_scanner.v0.agent.prompt_templates import (
    finding_update_prompt,
)


def finding_updater(state: findingUpdaterState):
    chunk_text = state["chunk"]["content"]
    chunk_id = state["chunk"]["chunk_id"]
    finding = state["finding"]
    what_to_update = state["what_to_update"]

    finding_data_as_text = f"Title: {finding['title']}\nSummary: {finding['summary']}\nMethodology: {finding['methodology']}"

    finding_update_data: FindingUpdate = call_llm(
        prompt_template=finding_update_prompt,
        input_parameters={
            "finding": finding_data_as_text,
            "text": chunk_text,
            "what_to_update": what_to_update,
        },
        pydantic_object=FindingUpdate,
        
    )

    # Create a new finding object with the updated data
    new_finding: Finding = {
        **finding,
        "title": finding_update_data["title"],
        "summary": finding_update_data["summary"],
        "methodology": finding_update_data["methodology"],
        "source_chunks_ids": [chunk_id],
    }

    # Add the new finding to the state
    newState: OverallState = {"findings": [new_finding]}

    return newState
