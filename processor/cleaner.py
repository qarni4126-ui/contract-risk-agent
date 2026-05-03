# cleaner.py
"""
Text Cleaning
Removes noise, normalizes whitespace, keeps structure.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean raw extracted text.
    
    Removes:
    - Multiple spaces/newlines
    - Special Unicode characters
    - Leading/trailing whitespace
    
    Args:
        text: Raw text from PDF/DOCX
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special Unicode
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Clean up newlines (keep some structure but remove excessive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def normalize_clause(clause: str) -> str:
    """
    Normalize a single clause (remove leading numbers, bullets).
    
    Example:
        "2.1. Obligations of Buyer" → "Obligations of Buyer"
    
    Args:
        clause: Raw clause text
        
    Returns:
        Normalized clause
    """
    # Remove leading numbers/bullets
    clause = re.sub(r'^[\d\.]+\s*', '', clause)
    clause = re.sub(r'^[-•*]\s*', '', clause)
    
    return clause.strip()


def is_valid_clause(clause: str, min_length: int = 20) -> bool:
    """
    Check if a chunk is a valid clause (not too short, not junk).
    
    Args:
        clause: Clause text
        min_length: Minimum character count
        
    Returns:
        True if valid
    """
    return len(clause) >= min_length and len(clause.split()) > 5