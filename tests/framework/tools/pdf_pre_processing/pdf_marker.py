from dotenv import load_dotenv
load_dotenv(override=True)

import logging
from pathlib import Path
from packages.framework.document_loaders.marker_loader import marker_load


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAPER_PATH = "tests/mocks/academic_papers/deep_residual_learning.pdf"
# PAPER_PATH = "tests/mocks/academic_papers/alexnet.pdf"


def test_marker_processing():
    script_dir = Path(__file__).parent  # Get the directory of the script
    results_path = (
        script_dir / "results"
    )  # Create a results directory in the same directory as the script
    results_path.mkdir(
        parents=True, exist_ok=True
    )  # Create the directory if it does not exist

    pdf_path = Path(PAPER_PATH)

    # Read the PDF file as bytes
    with open(pdf_path, "rb") as pdf_file:
        pdf_buffer = pdf_file.read()

    # Process the PDF to get the rendered output
    rendered = marker_load(pdf_buffer)

    # Save markdown
    output_md = results_path / f"{pdf_path.stem}.md"
    logger.info(f"Output Markdown file: {output_md}")

    with open(output_md, "w") as f:
        f.write(rendered["markdown"])

    logger.info(f"Saved markdown to {output_md}")
