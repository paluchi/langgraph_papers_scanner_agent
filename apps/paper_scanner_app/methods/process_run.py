import logging
import streamlit as st
from io import BytesIO

from apps.paper_scanner_app.methods.retrieve_runs import retrieve_runs
from apps.paper_scanner_app.methods.store_run import store_to_bigquery
from apps.paper_scanner_app.utils import IS_DEV


import logging
import streamlit as st
from io import BytesIO
from datetime import datetime
import pytz


# Runs agent and stores the result in BigQuery
def process_selected_method(selected_method, uploaded_file, version, user_name):
    """
    Processes the file using the selected method.

    Args:
        selected_method (Callable): The processing method to be used.
        uploaded_file (UploadedFile): The uploaded file object from Streamlit.
        version (str): The selected version string.
        user_name (str): The user's name.
    """
    # Validate user input
    if not user_name:
        st.error("Please provide your name.")
        return

    if not uploaded_file:
        st.error("Please upload a valid PDF or Markdown file.")
        return

    try:
        # Get start time
        start_execution = datetime.now(pytz.UTC).isoformat()

        # Read file content as bytes
        file_content = uploaded_file.read()

        if not file_content:
            st.error("The uploaded file appears to be empty.")
            return

        # Convert to bytes if required
        raw_content = (
            file_content
            if isinstance(file_content, (str, bytes))
            else BytesIO(file_content).getvalue()
        )

        with st.spinner(
            f"Processing file with version {version}. It may take up to 5m depending on the paper's length and model availability delay..."
        ):
            # Call the selected processing function
            result = selected_method(
                pdf_paper=raw_content,  # Pass content as raw bytes
                use_local_marker=IS_DEV,
            )

            # Get end time
            end_execution = datetime.now(pytz.UTC).isoformat()

            # Add result to session state
            st.session_state["runs"].append(
                {
                    "file_name": uploaded_file.name,
                    "user": user_name,
                    "version": version,
                    "status": "success",
                    "details": result,
                }
            )

            # Prepare metadata for BigQuery storage with our calculated times
            run_metadata = {
                "start_execution": start_execution,
                "end_execution": end_execution,
                "status": "success",
                "user_name": user_name,
                "version": version,
            }

            logging.info("Storing the result in BigQuery...")
            store_to_bigquery(
                state=result,
                run_metadata=run_metadata,
            )

            # Display success message
            st.success("File processed successfully! Please go to runs view...")

            # Force a reload of the runs data
            st.session_state["runs"] = retrieve_runs()

            # BELOW LINE NOT WORKING
            # Switch to the "View Runs" tab
            st.session_state["active_tab"] = "View Runs"

            # Trigger a rerun to show the updated view
            st.rerun()

    except Exception as e:
        logging.error(f"An error occurred while processing: {str(e)}")
        st.error(f"An error occurred while processing: {str(e)}")
