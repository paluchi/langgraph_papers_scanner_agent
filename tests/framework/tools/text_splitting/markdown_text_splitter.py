from dotenv import load_dotenv

load_dotenv(override=True)

from langchain.text_splitter import MarkdownTextSplitter
from pathlib import Path
import re


MARKDOWN_FILE_PATH = "tests/tools/pdf_pre_processing/results/alexnet.md"


def split_markdown_by_headers(content: str):
    """
    Splits markdown content by headers (#, ##, ###, etc.).

    Args:
        content (str): The markdown content to split.

    Returns:
        List of tuples: Each tuple contains the header and the associated content.
    """
    pattern = r"^(#{1,6} .+)$"
    matches = list(re.finditer(pattern, content, flags=re.MULTILINE))

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        header = match.group(0)
        body = content[start:end].strip()
        sections.append((header, body))
    return sections


def split_and_save_markdown_by_sections(
    input_file: str, chunk_size: int = 10000, chunk_overlap: int = 0
):
    """
    Split a markdown file into sections based on headers, and further subdivide
    sections that exceed the chunk size.

    Args:
        input_file (str): Path to input markdown file
        chunk_size (int): Maximum size of each chunk
        chunk_overlap (int): Number of characters to overlap between chunks

    Returns:
        int: Total number of chunks created
    """
    # Create output directory
    script_dir = Path(__file__).parent
    output_path = script_dir / "results"
    output_path.mkdir(parents=True, exist_ok=True)

    # Read input file
    content = Path(input_file).read_text()

    # Split by headers
    sections = split_markdown_by_headers(content)

    # Initialize splitter
    splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    total_chunks = 0

    # Process each section
    for i, (header, section_content) in enumerate(sections, 1):
        if len(section_content) <= chunk_size:
            # Save as a single chunk if it fits within the chunk_size
            chunk_file = output_path / f"section_{i}.md"
            chunk_file.write_text(section_content)
            total_chunks += 1
        else:
            # Subdivide the section if it exceeds the chunk size
            chunks = splitter.split_text(section_content)
            for j, chunk in enumerate(chunks, 1):
                chunk_file = output_path / f"section_{i}_chunk_{j}.md"
                chunk_file.write_text(chunk)
                total_chunks += 1

    return total_chunks


# Example usage:
def test_split_and_save_markdown():
    num_chunks = split_and_save_markdown_by_sections(
        input_file=MARKDOWN_FILE_PATH,
        chunk_size=10000,
        chunk_overlap=0,
    )
    print(f"Created {num_chunks} chunks")
