from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from io import BytesIO
from typing import Dict, Any, Union
import tempfile
import os


# Runks the marker locally to process a PDF buffer and return the rendered version
def marker_load(pdf_buffer: Union[bytes, BytesIO]) -> Dict[str, Any]:
    """
    Processes a PDF from a buffer and returns the rendered version.
    Creates a temporary file for processing and deletes it afterward.

    Args:
        pdf_buffer (Union[bytes, BytesIO]): PDF data as either bytes or BytesIO buffer.

    Returns:
        Dict[str, Any]: A dictionary containing the rendered PDF's markdown,
                        images, and metadata.
    """
    # Create the artifact dictionary
    artifact_dict = create_model_dict()

    # Initialize PdfConverter with the artifact_dict
    converter = PdfConverter(artifact_dict=artifact_dict)

    # Create a temporary file and write the buffer contents to it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        # Handle both bytes and BytesIO inputs
        content = (
            pdf_buffer.getvalue() if isinstance(pdf_buffer, BytesIO) else pdf_buffer
        )
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Convert the PDF using the temporary file path
        rendered = converter(temp_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Return the full rendered version as a dictionary
    return {
        "markdown": rendered.markdown,
        "images": rendered.images,
        "metadata": rendered.metadata,
    }
