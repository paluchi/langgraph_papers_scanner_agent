import streamlit as st
import logging
from apps.paper_scanner_app.methods.process_run import process_selected_method
from apps.paper_scanner_app.methods.retrieve_runs import retrieve_runs
from packages.workflows import paper_scanner
from datetime import datetime

# This is the main app file for the streamlit Paper Scanner app.
# It's too long and in a real project, it would be split into multiple files.

VERSION_MAP = {
    version: {
        "description": f"{version}" + (" (Latest)" if version == "v0" else ""),
        "function": func,
    }
    for version, func in paper_scanner.items()
    if version != "available_versions" and version != "latest"
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if "runs" not in st.session_state:
    st.session_state["runs"] = []


# Function to format datetime
def format_datetime(date_str):
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str


# Function to display chunks
def display_chunks(chunk_ids: list, chunks: list, finding_id: str):
    for idx, chunk_id in enumerate(chunk_ids):
        chunk = next((c for c in chunks if c["chunk_id"] == chunk_id), None)
        if chunk and chunk.get("content"):
            st.text_area(
                "Source Text",
                chunk["content"],
                height=100,
                disabled=True,
                key=f"finding_{finding_id}_chunk_{chunk_id}_{idx}",
            )


# Title and description
st.title("Papers Scanner App")
st.write(
    "An AI system that automatically extracts and consolidates research findings from academic papers."
)

# Initialize active tab in session state if not present
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Upload & Process"

# Create tabs and set active tab based on session state
tab1, tab2, tab3 = st.tabs(["Upload & Process", "View Runs", "About"])

# Set the active tab
active_tab_index = 0 if st.session_state["active_tab"] == "Upload & Process" else 1
st.query_params["tab"] = active_tab_index

# Now use the tabs as before
with tab1:
    st.header("Upload & Process Files")
    user_name = st.text_input("Enter your name:")
    uploaded_file = st.file_uploader(
        "Upload a file (PDF or Markdown only)", type=["pdf"]
    )

    # Version selection dropdown
    selected_version = st.selectbox(
        "Select a version:",
        options=list(VERSION_MAP.keys()),
        format_func=lambda x: VERSION_MAP[x]["description"],
    )

    # Process file button
    if st.button("Process File"):
        if user_name and uploaded_file:
            process_func = VERSION_MAP[selected_version]["function"]
            process_selected_method(
                process_func, uploaded_file, selected_version, user_name
            )
        else:
            st.error("Please provide your name and upload a file.")

with tab2:
    st.header("View Previous Runs")

    # Add reload button
    if st.button("🔄 Reload Runs"):
        st.session_state["runs"] = retrieve_runs()
        st.success("Runs reloaded successfully!")

    if not st.session_state["runs"]:
        st.session_state["runs"] = retrieve_runs()

    if st.session_state["runs"]:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            sort_order = st.radio("Sort by:", ["Newest First", "Oldest First"])
        with col2:
            filter_user = st.text_input("Filter by user:", "")

        # Sort by start_execution time in run_metadata with proper None handling
        def get_sort_key(run):
            try:
                start_time = run.get("run_metadata", {}).get("start_execution", "")
                if start_time:
                    try:
                        return datetime.fromisoformat(start_time)
                    except:
                        return datetime.min
                return datetime.min
            except:
                return datetime.min

        runs_to_display = sorted(
            [
                run for run in st.session_state["runs"] if run is not None
            ],  # Filter out None values
            key=get_sort_key,
            reverse=(sort_order == "Newest First"),
        )

        # Filter by user if specified
        if filter_user:
            runs_to_display = [
                run
                for run in runs_to_display
                if filter_user.lower()
                in str(run.get("run_metadata", {}).get("user_name", "")).lower()
            ]

        if not runs_to_display:
            st.info("No matching runs found.")

        for run in runs_to_display:
            if run is None:  # Skip None values
                continue

            metadata = run.get("metadata", {})
            run_metadata = run.get("run_metadata", {})

            # Create expander title with fallbacks for all values
            title_parts = []
            if metadata.get("title"):
                title_parts.append(f"📄 {metadata.get('title', 'Untitled')}")
            if run_metadata.get("user_name"):
                title_parts.append(
                    f"👤 {run_metadata.get('user_name', 'Unknown User')}"
                )
            if run_metadata.get("start_execution"):
                title_parts.append(
                    f"🕒 {format_datetime(run_metadata.get('start_execution', ''))}"
                )

            expander_title = " - ".join(title_parts) if title_parts else "Untitled Run"

            with st.expander(expander_title):
                # Document Metadata Section
                st.subheader("📋 Document Metadata")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Title:**", metadata.get("title", "N/A"))
                    st.write(
                        "**Publication Date:**", metadata.get("publication_date", "N/A")
                    )
                with col2:
                    st.write(
                        "**Authors:**", ", ".join(metadata.get("authors", ["N/A"]))
                    )
                st.write("**Abstract:**", metadata.get("abstract", "N/A"))

                # Run Metadata Section
                st.subheader("⚙️ Run Information")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Version:**", run_metadata.get("version", "N/A"))
                    st.write("**Status:**", run_metadata.get("status", "N/A"))
                with col2:
                    st.write(
                        "**Start Time:**",
                        format_datetime(run_metadata.get("start_execution", "N/A")),
                    )
                with col3:
                    st.write(
                        "**End Time:**",
                        format_datetime(run_metadata.get("end_execution", "N/A")),
                    )

                # Findings Section
                st.subheader("🔍 Findings")
                tab_consolidated, tab_raw = st.tabs(
                    ["Consolidated Findings", "Raw Findings"]
                )

                with tab_consolidated:
                    st.write(
                        "**Number of Consolidated Findings:**",
                        len(run.get("consolidated_findings", [])),
                    )
                    for idx, finding in enumerate(
                        run.get("consolidated_findings", []), 1
                    ):
                        st.markdown(
                            f"### Finding {idx}: {finding.get('title', 'Untitled')}"
                        )
                        st.write("**Summary:**", finding.get("summary", "N/A"))
                        st.write("**Methodology:**", finding.get("methodology", "N/A"))
                        st.write(
                            "**Keywords:**", ", ".join(finding.get("keywords", ["N/A"]))
                        )
                        st.markdown("---")

                with tab_raw:
                    st.write(
                        "**Number of Raw Findings:**", len(run.get("raw_findings", []))
                    )
                    for idx, finding in enumerate(run.get("raw_findings", []), 1):
                        st.markdown(
                            f"### Finding {idx}: {finding.get('title', 'Untitled')}"
                        )
                        st.write("**Summary:**", finding.get("summary", "N/A"))
                        st.write("**Methodology:**", finding.get("methodology", "N/A"))
                        st.markdown("---")
                        st.markdown("**Source Chunks:**")
                        display_chunks(
                            finding.get("source_chunks_ids", []),
                            run.get("chunks", []),
                            finding.get("id", str(idx)),
                        )
                        st.markdown("---")

                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download Raw Findings",
                        data=str(run.get("raw_findings", [])),
                        file_name=f"raw_findings_{run_metadata.get('start_execution', 'download')}.json",
                        mime="application/json",
                        key=f"raw_findings_download_{run_metadata.get('start_execution', '')}_{run.get('metadata', {}).get('title', '')}_{id(run)}",  # Using multiple identifiers
                    )
                with col2:
                    st.download_button(
                        "📥 Download Consolidated Findings",
                        data=str(run.get("consolidated_findings", [])),
                        file_name=f"consolidated_findings_{run_metadata.get('start_execution', 'download')}.json",
                        mime="application/json",
                        key=f"consolidated_findings_download_{run_metadata.get('start_execution', '')}_{run.get('metadata', {}).get('title', '')}_{id(run)}",  # Using multiple identifiers
                    )
    else:
        st.info("No runs available yet. Upload and process a file in the first tab.")

with tab3:
    st.header("About Paper Scanner")

    st.markdown(
        """
    Paper Scanner is an intelligent document analysis system that processes academic papers to automatically extract and consolidate key research findings. 
    It uses LangGraph orchestration and Gemini LLM to break down papers into meaningful chunks, identify significant findings, and generate both detailed 
    and consolidated insights while maintaining traceability to source text.
    """
    )

    # Display architecture image
    st.image(
        "apps/paper_scanner_app/assets/v0_architecture.png",
        caption="Paper Scanner v0 Architecture",
        use_container_width=True,
    )

    # Key Features
    st.subheader("🎯 Key Features")
    st.markdown(
        """
    - PDF document processing and analysis
    - LangGraph-based orchestration pipeline
    - Metadata extraction (title, authors, date, abstract)
    - Raw and consolidated findings generation
    - Source tracking to original text
    - 
    """
    )

    # Technical Details
    st.subheader("⚙️ Technical Implementation")
    st.markdown(
        """
    - **LLM Engine**: Gemini 1.5 Flash
    - **Workflow Engine**: LangGraph
    - **Chunk Processing**: Sequential with 500 char minimum
    - **Finding Types**: Raw findings with source tracking + Consolidated with keywords
    """
    )

    # Architectural Limitations
    st.subheader("⚠️ Core Architectural Limitations")
    st.markdown(
        """
    - **Sequential Processing**: Chunks must be processed in order, no parallel processing support
    - **Processing Time**: As chunks are processed sequentially, it takes its time
    - **Error Recovery**: No retry mechanism or partial results saving on failure besides LLM retries
    - **Memory Constraints**: All chunks and findings must be held in memory
    - **Processing Flow**: No ability to pause/resume or reprocess specific sections
    """
    )
