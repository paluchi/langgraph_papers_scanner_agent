from dotenv import load_dotenv

load_dotenv(override=True)

from io import BytesIO
import json
import os
import time
from packages.workflows.paper_scanner.v0 import run_paper_scanner_v0
import logging

# HERE LIES A TEST SCRIPT TO RUN THE PAPER SCANNER WORKFLOW AND STORE THE RESULTS LOCALY
# Set global variables to configure the test
# Run with: poetry run pytest -s tests/workflows/paper_scanner.py

VERSION = "v0"
PDF_PAPER_PATH = "tests/mocks/academic_papers/alexnet.pdf"

# If MARKDOWN_PAPER_PATH is set, the paper will be loaded as markdown, otherwise as PDF (markdown is faster for testing)
MARKDOWN_PAPER_PATH = (
    "tests/framework/tools/pdf_pre_processing/results/deep_residual_learning.md"
)
# MARKDOWN_PAPER_PATH = None

RESULTS_STORE_PATH = "tests/workflows/results/papers_scanner"

PAPER_PATH = MARKDOWN_PAPER_PATH if MARKDOWN_PAPER_PATH else PDF_PAPER_PATH

# Local marker executes document loading and pre-processing locally
USE_LOCAL_MARKER = True


versions_dict = {
    "v0": run_paper_scanner_v0,
}


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",  # Add timestamps and levels
    handlers=[logging.StreamHandler()],  # Log to the console
)


def test_paper_scanner():
    try:
        logging.info("Starting paper scanner test")

        # Load paper as BytesIO
        logging.info("Loading paper from %s", PAPER_PATH)
        if MARKDOWN_PAPER_PATH:
            with open(MARKDOWN_PAPER_PATH, "r") as f:
                paper = f.read()
        else:
            with open(PAPER_PATH, "rb") as f:
                paper = BytesIO(f.read())

        # Process paper
        logging.info("Processing paper with version %s", VERSION)
        if MARKDOWN_PAPER_PATH:
            results = versions_dict[VERSION](
                markdown_paper=paper, use_local_marker=USE_LOCAL_MARKER
            )
        else:  # PDF paper
            results = versions_dict[VERSION](
                pdf_paper=paper, use_local_marker=USE_LOCAL_MARKER
            )
        logging.info("Results have been processed")

        # Create results store directory
        logging.info("Creating results store directory at %s", RESULTS_STORE_PATH)
        os.makedirs(RESULTS_STORE_PATH, exist_ok=True)

        # Save results
        results_path = os.path.join(
            RESULTS_STORE_PATH, f"paper_scan_{int(time.time())}.json"
        )

        with open(results_path, "w") as f:
            json.dump(results, f)

        # Log status
        logging.info("Results saved to: %s", results_path)
    except Exception as e:
        logging.error("An error occurred: %s", e)
