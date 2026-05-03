# chunker.py

"""
Clause Splitting (Chunking)
Splits contract into logical sections, not random chunks.

Strategy:
1. Split by common clause headers
2. If no headers, split by sentence count
3. Keep context (clause number + text)
"""

import re
from typing import List, Tuple
from .cleaner import clean_text, normalize_clause, is_valid_clause


# Common clause patterns
CLAUSE_PATTERNS = [
    r'(?:^|\n)\s*(?:\d+\.)+\s*(?:[A-Z][A-Za-z\s]+)',  # Numbered: 1. Section Title
    r'(?:^|\n)\s*(?:SECTION|CLAUSE|ARTICLE)\s+[\d\w]+',  # SECTION 1
    r'(?:^|\n)\s*(?:[A-Z][A-Za-z\s]{5,})[:\n]',  # Title with colon
]


def chunk_by_headers(text: str) -> List[Tuple[str, str]]:
    """
    Split text by detected headers/numbered sections.
    
    Returns:
        List of (header, content) tuples
    """
    chunks = []
    
    # Try numbered sections (1.1, 1.2, etc.)
    sections = re.split(r'(?:^|\n)(\d+(?:\.\d+)*\s+[A-Z][^\n]*)', text)
    
    # Pair headers with content
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            header = sections[i].strip()
            content = sections[i + 1].strip()
            if is_valid_clause(content):
                chunks.append((header, content))
    
    return chunks if chunks else chunk_by_sentences(text)


def chunk_by_sentences(text: str, sentences_per_chunk: int = 10) -> List[Tuple[str, str]]:
    """
    Fallback: Split by sentence count if no headers found.
    
    Args:
        text: Full contract text
        sentences_per_chunk: Number of sentences per chunk
        
    Returns:
        List of (chunk_number, content) tuples
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        chunk_text = ' '.join(chunk_sentences)
        
        if is_valid_clause(chunk_text):
            chunk_num = (i // sentences_per_chunk) + 1
            chunks.append((f"Clause {chunk_num}", chunk_text))
    
    return chunks


def split_contract(text: str) -> List[dict]:
    """
    Main function: Split contract into chunks.
    
    Returns structured format:
    [
        {"id": 1, "header": "1. Definitions", "content": "..."},
        {"id": 2, "header": "2. Obligations", "content": "..."},
        ...
    ]
    
    Args:
        text: Raw contract text
        
    Returns:
        List of chunk dicts
    """
    # Clean first
    text = clean_text(text)
    
    # Try header-based chunking
    chunk_tuples = chunk_by_headers(text)
    
    # Convert to structured format
    chunks = []
    for idx, (header, content) in enumerate(chunk_tuples, 1):
        chunks.append({
            "id": idx,
            "header": normalize_clause(header),
            "content": content.strip(),
            "length": len(content.split())
        })
    
    return chunks