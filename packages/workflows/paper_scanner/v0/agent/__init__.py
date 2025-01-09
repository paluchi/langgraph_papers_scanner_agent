from langgraph.graph import StateGraph, START, END

from packages.workflows.paper_scanner.v0.agent.nodes.chunk.loading import (
    chunks_initializer,
    next_chunk_preparer,
    should_continue,
)
from packages.workflows.paper_scanner.v0.agent.nodes.chunk.processing import (
    chunk_processor,
    post_processing_router,
)
from packages.workflows.paper_scanner.v0.agent.nodes.finding.consolidation import (
    findings_consolidator,
)
from packages.workflows.paper_scanner.v0.agent.nodes.finding.creation import (
    finding_creator,
)
from packages.workflows.paper_scanner.v0.agent.nodes.finding.processing_sink import (
    processing_sink,
)
from packages.workflows.paper_scanner.v0.agent.nodes.finding.update import (
    finding_updater,
)
from packages.workflows.paper_scanner.v0.agent.nodes.metadata.update import (
    metadata_updater,
)
from packages.workflows.paper_scanner.v0.agent.schemas.states import (
    OverallState,
    InputState,
)


# AGENT GRAPH DEFINITION AND EXPORT
# ---------------------------------


# Define the graph
builder = StateGraph(OverallState, input=InputState)

# Add nodes
builder.add_node("chunks_initializer", chunks_initializer)
builder.add_node("next_chunk_preparer", next_chunk_preparer)
builder.add_node("chunk_processor", chunk_processor)
builder.add_node("finding_updater", finding_updater)
builder.add_node("finding_creator", finding_creator)
builder.add_node("metadata_updater", metadata_updater)
builder.add_node("processing_sink", processing_sink)
builder.add_node("findings_consolidator", findings_consolidator)

# Add edges
builder.add_edge(START, "chunks_initializer")
builder.add_edge("chunks_initializer", "next_chunk_preparer")
builder.add_conditional_edges(
    "next_chunk_preparer",
    should_continue,
    {True: "chunk_processor", False: "findings_consolidator"},
)
builder.add_conditional_edges(
    "chunk_processor",
    post_processing_router,
    ["finding_updater", "finding_creator", "metadata_updater"],
)
builder.add_edge("finding_updater", "processing_sink")
builder.add_edge("finding_creator", "processing_sink")
builder.add_edge("metadata_updater", "processing_sink")
builder.add_edge("processing_sink", "next_chunk_preparer")
builder.add_edge("findings_consolidator", END)

# Compile the graph
paper_summarization_agent = builder.compile()
