from dotenv import load_dotenv

load_dotenv(override=True)

from langchain.document_loaders import PDFPlumberLoader
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_and_save_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF and save it to a results directory next to the PDF.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Path to the saved results file
    """
    try:
        # Convert to Path object for easier path manipulation
        pdf_path = Path(pdf_path)

        # Create results directory next to the PDF file
        results_dir = pdf_path.parent / "results"
        results_dir.mkdir(exist_ok=True)

        # Create output filename
        output_file = results_dir / f"{pdf_path.stem}_extracted.txt"

        # Load and extract text
        logger.info(f"Loading PDF: {pdf_path}")
        loader = PDFPlumberLoader(str(pdf_path))
        pages = loader.load()

        # Combine text from all pages
        full_text = " ".join(page.page_content for page in pages)

        # Save to file
        output_file.write_text(full_text)
        logger.info(f"Saved extracted text to: {output_file}")

        return str(output_file)

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise


def test_pdf_extraction():
    """Basic test for PDF extraction and saving."""
    # Test file path
    pdf_path = "tests/mocks/academic_papers/alexnet.pdf"

    try:
        # Extract and save text
        result_path = extract_and_save_pdf(pdf_path)

        # Verify results
        assert os.path.exists(result_path), "Result file was not created"

        # Read saved content to verify it's not empty
        with open(result_path, "r") as f:
            content = f.read()
            assert len(content) > 0, "Extracted text is empty"

        print(f"Test passed! Results saved to: {result_path}")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise
