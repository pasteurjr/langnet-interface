"""
PDF Processing Utilities
Handles PDF text extraction and chunking for agent processing.

Based on content-automation-system implementation.
"""

import re
from pathlib import Path
from typing import List, Optional


def extract_pdf_text(pdf_path: str, max_pages: int = 50) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to process (default: 50)

    Returns:
        Extracted text as a string

    Raises:
        Exception: If PDF cannot be read
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not path.suffix.lower() == '.pdf':
        raise ValueError(f"File is not a PDF: {pdf_path}")

    text = ''

    # Try pypdf first (modern library)
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        parts = []

        # Limit to max_pages
        pages_to_process = min(len(reader.pages), max_pages)

        for i in range(pages_to_process):
            try:
                page_text = reader.pages[i].extract_text() or ''
                if page_text.strip():
                    parts.append(page_text)
            except Exception as e:
                print(f"Warning: Failed to extract page {i+1}: {e}")
                continue

        text = "\n\n".join(parts)

    except ImportError:
        # Fallback to PyPDF2 if pypdf not available
        try:
            from PyPDF2 import PdfReader as PyPDF2Reader
            reader = PyPDF2Reader(str(path))
            parts = []

            pages_to_process = min(len(reader.pages), max_pages)

            for i in range(pages_to_process):
                try:
                    page_text = reader.pages[i].extract_text() or ''
                    if page_text.strip():
                        parts.append(page_text)
                except Exception as e:
                    print(f"Warning: Failed to extract page {i+1}: {e}")
                    continue

            text = "\n\n".join(parts)

        except ImportError:
            raise ImportError("Neither pypdf nor PyPDF2 is installed. Install with: pip install pypdf")

    # Clean up the text
    text = clean_text(text)

    return text


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing excessive whitespace.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    # Remove multiple blank lines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Remove excessive spaces
    text = re.sub(r' +', ' ', text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def chunk_text(text: str, max_chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.

    Uses a sliding window approach with character-based chunking.

    Args:
        text: Text to chunk
        max_chunk_size: Maximum size of each chunk in characters (default: 1000)
        overlap: Number of characters to overlap between chunks (default: 200)

    Returns:
        List of text chunks

    Example:
        >>> text = "A" * 2500
        >>> chunks = chunk_text(text, max_chunk_size=1000, overlap=200)
        >>> len(chunks)
        4
        >>> len(chunks[0])
        1000
        >>> len(chunks[1])
        1000
    """
    if not text or not text.strip():
        return []

    chunks = []
    text_len = len(text)

    # Calculate step size (how far to move forward each iteration)
    # step = chunk_size - overlap ensures proper overlap
    step = max(1, max_chunk_size - max(0, overlap))

    i = 0
    while i < text_len:
        # Get chunk from current position
        j = min(i + max_chunk_size, text_len)
        chunk = text[i:j]

        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk)

        # Move forward by step size
        i += step

        # Break if we've reached the end
        if j >= text_len:
            break

    return chunks


def format_document_chunks(
    document_name: str,
    chunks: List[str],
    max_chunks: Optional[int] = None
) -> List[str]:
    """
    Format chunks with document header for agent processing.

    Args:
        document_name: Name of the source document
        chunks: List of text chunks
        max_chunks: Maximum number of chunks to include (default: all)

    Returns:
        List of formatted chunks with [DOCUMENTO: name] prefix

    Example:
        >>> chunks = ["chunk1", "chunk2"]
        >>> formatted = format_document_chunks("test.pdf", chunks)
        >>> formatted[0]
        '[DOCUMENTO: test.pdf]\\nchunk1'
    """
    if max_chunks:
        chunks = chunks[:max_chunks]

    formatted = []
    for chunk in chunks:
        if chunk.strip():
            formatted.append(f"[DOCUMENTO: {document_name}]\n{chunk}")

    return formatted


def process_pdf_for_agent(
    pdf_path: str,
    max_pages: int = 50,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    max_chunks: Optional[int] = 60
) -> dict:
    """
    Complete PDF processing pipeline: extract, chunk, and format.

    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum pages to extract (default: 50)
        chunk_size: Size of each chunk in characters (default: 1000)
        chunk_overlap: Overlap between chunks (default: 200)
        max_chunks: Maximum chunks to return (default: 60)

    Returns:
        Dictionary with:
            - 'document_name': Name of the PDF file
            - 'raw_text': Full extracted text
            - 'chunks': List of text chunks (unformatted)
            - 'formatted_chunks': List of formatted chunks with document header
            - 'stats': Statistics about processing

    Example:
        >>> result = process_pdf_for_agent("document.pdf")
        >>> result['stats']['num_pages']
        50
        >>> len(result['formatted_chunks'])
        60
    """
    path = Path(pdf_path)
    document_name = path.name

    # Extract text
    print(f"📄 Extracting text from {document_name}...")
    raw_text = extract_pdf_text(pdf_path, max_pages=max_pages)

    if not raw_text or not raw_text.strip():
        raise ValueError(f"No text could be extracted from {document_name}")

    # Chunk text
    print(f"✂️  Chunking text (size={chunk_size}, overlap={chunk_overlap})...")
    chunks = chunk_text(raw_text, max_chunk_size=chunk_size, overlap=chunk_overlap)

    # Format chunks
    print(f"📝 Formatting {len(chunks)} chunks...")
    formatted_chunks = format_document_chunks(document_name, chunks, max_chunks=max_chunks)

    # Calculate statistics
    stats = {
        'document_name': document_name,
        'document_path': str(path),
        'raw_text_length': len(raw_text),
        'raw_text_words': len(raw_text.split()),
        'num_chunks': len(chunks),
        'num_formatted_chunks': len(formatted_chunks),
        'avg_chunk_size': sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
        'chunk_size_config': chunk_size,
        'overlap_config': chunk_overlap,
        'max_chunks_config': max_chunks
    }

    print(f"✅ Processed {document_name}: {stats['num_formatted_chunks']} chunks, "
          f"{stats['raw_text_words']} words")

    return {
        'document_name': document_name,
        'raw_text': raw_text,
        'chunks': chunks,
        'formatted_chunks': formatted_chunks,
        'stats': stats
    }


if __name__ == "__main__":
    # Simple test
    import sys

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = process_pdf_for_agent(pdf_path)

        print("\n" + "="*80)
        print("PROCESSING RESULTS")
        print("="*80)
        print(f"Document: {result['document_name']}")
        print(f"Text length: {result['stats']['raw_text_length']:,} chars")
        print(f"Words: {result['stats']['raw_text_words']:,}")
        print(f"Chunks: {result['stats']['num_chunks']}")
        print(f"Avg chunk size: {result['stats']['avg_chunk_size']:.0f} chars")
        print("\n" + "="*80)
        print("FIRST CHUNK PREVIEW")
        print("="*80)
        print(result['formatted_chunks'][0][:500] + "...")
    else:
        print("Usage: python pdf_processor.py <path_to_pdf>")
