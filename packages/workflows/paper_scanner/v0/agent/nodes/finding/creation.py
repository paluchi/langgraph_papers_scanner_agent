from uuid import uuid4
from packages.workflows.paper_scanner.v0.utils.call_llm import call_llm

from packages.workflows.paper_scanner.v0.agent.schemas.states import (
    Finding,
    OverallState,
    findingCreatorState,
)
from packages.workflows.paper_scanner.v0.agent.schemas.format_instructions import (
    NewFinding,
)

from packages.workflows.paper_scanner.v0.agent.prompt_templates import (
    finding_creation_prompt,
)


def finding_creator(state: findingCreatorState):
    chunk_text = state["chunk"]["content"]
    chunk_id = state["chunk"]["chunk_id"]
    funding_description = state["description"]
    funding_title = state["title"]

    # Create a new finding calling the LLM
    new_finding_data: NewFinding = call_llm(
        prompt_template=finding_creation_prompt,
        input_parameters={
            "text": chunk_text,
            "description": funding_description,
            "title": funding_title,
        },
        pydantic_object=NewFinding,
        
    )

    # Create a new finding object
    new_finding: Finding = {
        "id": str(uuid4()),
        "title": new_finding_data["title"],
        "summary": new_finding_data["summary"],
        "methodology": new_finding_data["methodology"],
        "source_chunks_ids": [chunk_id],
    }

    # Add the new finding to the state
    newState: OverallState = {"findings": [new_finding]}

    return newState
