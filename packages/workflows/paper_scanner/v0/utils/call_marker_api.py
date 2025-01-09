from io import BytesIO
import logging
import requests
import time
from typing import Optional, Dict, Any
import os

# HERE LIES A PREPROCESSING HELPER FOR PDF
# It calls marker algorithm hosted on Datalab
# ----------------------------


def call_marker_api(
    pdf_file: BytesIO,
    max_pages: Optional[int] = None,
    langs: Optional[str] = None,
    force_ocr: bool = False,
    paginate: bool = False,
    strip_existing_ocr: bool = False,
    disable_image_extraction: bool = True,
    use_llm: bool = False,
    output_format: str = "markdown",
    skip_cache: bool = False,
    max_retries: int = 100,
    retry_delay: int = 10,
) -> Dict[str, Any]:
    """
    Makes a call to the Marker API to process a PDF file and polls for results.

    Args:
        pdf_file (BytesIO): The PDF file as a BytesIO buffer
        max_pages (Optional[int]): Maximum number of pages to process
        langs (Optional[str]): Languages for OCR, comma separated
        force_ocr (bool): Whether to force OCR on all pages
        paginate (bool): Whether to paginate the output
        strip_existing_ocr (bool): Whether to strip existing OCR
        disable_image_extraction (bool): Whether to disable image extraction
        use_llm (bool): Whether to use LLM for enhanced processing
        output_format (str): Output format ('json' or 'markdown')
        skip_cache (bool): Whether to skip cache and rerun inference
        max_retries (int): Maximum number of times to check for results
        retry_delay (int): Delay in seconds between retry attempts

    Returns:
        Dict[str, Any]: The API response containing markdown and images

    Raises:
        ValueError: If API key or endpoint is not set
        requests.exceptions.RequestException: For API communication errors
        TimeoutError: If maximum retries reached before getting results
    """
    api_key = os.getenv("DATALAB_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Please set the DATALAB_API_KEY environment variable."
        )

    url = "https://www.datalab.to/api/v1/marker"

    # Prepare the files and data for the multipart form
    files = {"file": ("document.pdf", pdf_file, "application/pdf")}

    data = {
        "max_pages": max_pages,
        "langs": langs,
        "force_ocr": force_ocr,
        "paginate": paginate,
        "strip_existing_ocr": strip_existing_ocr,
        "disable_image_extraction": disable_image_extraction,
        "use_llm": use_llm,
        "output_format": output_format,
        "skip_cache": skip_cache,
    }

    # Remove None values from data
    data = {k: v for k, v in data.items() if v is not None}

    headers = {"X-API-Key": api_key}

    # Initial submission
    logging.info("Submitting PDF to Marker API")
    response = requests.post(url, files=files, data=data, headers=headers)
    response.raise_for_status()
    initial_response = response.json()

    if not initial_response.get("success"):
        raise ValueError(f"API request failed: {initial_response.get('error')}")

    check_url = initial_response.get("request_check_url")
    if not check_url:
        raise ValueError("No request ID received from API")

    logging.info("Polling for results at %s", check_url)
    for attempt in range(max_retries):
        result_response = requests.get(check_url, headers=headers)
        result_response.raise_for_status()
        result = result_response.json()

        # Check if processing is complete
        if result.get("status") == "complete":
            if result.get("success") == True:
                logging.info("marker api call completed")
                return result
            else:
                raise ValueError(f"Processing failed: {result.get('error')}")

        time.sleep(retry_delay)

    raise TimeoutError(
        f"Maximum retries ({max_retries}) reached without getting results"
    )
