from uuid import uuid4

from packages.workflows.paper_scanner.v0.agent.schemas.states import (
    ChunkInfo,
    ChunkStatus,
    PaperMetadata,
    OverallState,
    InputState,
)


# This node is the first one and initializes the state for the chunk processing agent
def chunks_initializer(state: InputState):
    chunks = state["chunks"]
    min_chunk_length = 500  # Minimum character length for a chunk

    # First pass: Merge short chunks
    merged_chunks = []
    if chunks:
        current_chunk = chunks[
            -1
        ]  # Start with the last chunk since we're processing in reverse

        for next_chunk in reversed(chunks[:-1]):  # Process remaining chunks in reverse
            if len(current_chunk) < min_chunk_length:
                # Merge with next chunk
                current_chunk = next_chunk + "\n\n" + current_chunk
            else:
                merged_chunks.insert(0, current_chunk)
                current_chunk = next_chunk

        # Don't forget to add the last processed chunk
        merged_chunks.insert(0, current_chunk)

    # Create ChunkInfo objects after merging
    chunks_queue = [
        ChunkInfo(chunk_id=str(uuid4()), content=chunk, status=ChunkStatus.PENDING)
        for chunk in merged_chunks
    ]

    agent_state = OverallState()
    agent_state["metadata"] = PaperMetadata()
    agent_state["findings"] = []
    agent_state["consolidated_findings"] = []
    agent_state["current_chunk"] = None
    agent_state["chunks_queue"] = chunks_queue
    agent_state["processed_chunks"] = []

    return agent_state


# This node prepares the next chunk to be processed by the agent (executes first on each iteration)
def next_chunk_preparer(state: OverallState):
    if state.get("current_chunk", None):
        # Add current chunk to the processed chunks, update its status to PROCESSED
        state["current_chunk"]["status"] = ChunkStatus.PROCESSED
        state["processed_chunks"].append(state["current_chunk"])
        # Set the current chunk to None
        state["current_chunk"] = None

    # Set the state["current_chunk"] to the first entry of the state["chunks_queue"]
    # Remove it from the queue
    state["current_chunk"] = (
        state["chunks_queue"].pop(0) if len(state["chunks_queue"]) else None
    )
    # return the new state
    return state


# Checks if process finished and routes accordingly
def should_continue(state: OverallState):
    # If the state["chunks_queue"] is not empty, return True
    # Otherwise, return False
    if state["chunks_queue"] or state["current_chunk"]:
        return True
    else:
        return False
