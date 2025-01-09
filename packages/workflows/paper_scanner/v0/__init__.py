from io import BytesIO
import logging
from packages.workflows.paper_scanner.v0.agent import paper_summarization_agent
from packages.framework.document_loaders.marker_loader import marker_load
from packages.framework.text_splitters.markdown import markdown_text_split
from packages.workflows.paper_scanner.v0.utils.call_marker_api import call_marker_api

# WORKFLOW FUNCTION THAT INGESTS A PDF OR MARKDOWN PAPER, EXECUTES THE PAPER SCANNER AGENT, AND RETURNS THE RESULTS
# --------------------------------------------------------------------------------------------------------------


def run_paper_scanner_v0(
    pdf_paper: BytesIO = None,
    markdown_paper: str = None,
    use_local_marker: bool = False,
) -> dict:
    """
    Processes a research paper and extracts insights using a chat model and graph-based processing.

    Args:
        pdf_paper (BytesIO): PDF data of the paper as a BytesIO buffer.
        markdown_paper (str): Markdown content of the paper.
        use_local_marker (bool): Whether to use the local marker for PDF processing.
        **marker_options: Additional options to pass to the Marker API.

    Returns:
        dict: Processed results containing insights, metadata, and summaries.
    """
    if not pdf_paper and not markdown_paper:
        raise ValueError("Either a PDF or markdown paper must be provided")

    markdown_content = markdown_paper
    if not markdown_content:
        if use_local_marker:
            # Process the PDF buffer using local marker
            pdf_data = marker_load(pdf_buffer=pdf_paper)
            markdown_content = pdf_data.get("markdown", "")
        else:

            # Process the PDF buffer using the Marker API
            api_response = call_marker_api(pdf_file=pdf_paper)
            markdown_content = api_response.get("markdown", "")

    # Split the markdown into sections and chunks
    logging.info("Splitting the markdown content into sections and chunks...")
    chunks = markdown_text_split(
        input_text=markdown_content, chunk_size=10000, chunk_overlap=0
    )

    # Call the paper summarization agent
    logging.info("Calling the paper summarization agent...")
    result = paper_summarization_agent.invoke(
        {"chunks": chunks}, {"recursion_limit": 200}
    )

    logging.info("Processing complete.")
    return result
