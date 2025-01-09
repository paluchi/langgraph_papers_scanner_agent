from packages.workflows.paper_scanner.v0.agent.schemas.format_instructions import (
    ChunkProcessorMetadata,
)
from packages.workflows.paper_scanner.v0.agent.schemas.states import (
    OverallState,
)


def metadata_updater(state: ChunkProcessorMetadata):
    updated_state: OverallState = {
        "metadata": {
            "title": state["title"],
            "authors": state["authors"],
            "publication_date": state["publication_date"],
            "abstract": state["abstract"],
        }
    }
    return updated_state
