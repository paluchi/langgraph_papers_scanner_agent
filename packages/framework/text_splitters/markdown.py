from langchain.text_splitter import MarkdownTextSplitter
import re


def split_markdown_by_headers(content: str):
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


def markdown_text_split(
    input_text: str, chunk_size: int = 10000, chunk_overlap: int = 0
):
    """
    Split markdown content into sections based on headers and chunk size.

    Args:
        input_text (str): Markdown content as string
        chunk_size (int): Maximum size of each chunk
        chunk_overlap (int): Number of characters to overlap between chunks

    Returns:
        List[str]: List of all chunks created
    """
    sections = split_markdown_by_headers(input_text)
    splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    all_chunks = []
    for _, section_content in sections:
        if len(section_content) <= chunk_size:
            all_chunks.append(section_content)
        else:
            chunks = splitter.split_text(section_content)
            all_chunks.extend(chunks)

    return all_chunks
