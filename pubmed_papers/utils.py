"""
Utility functions for the pubmed_papers package.
"""

import logging
import sys
from typing import Optional

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers to the same logger
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(level)
    
    return logger

def validate_email(email: str) -> bool:
    """
    Validate that a string is a properly formatted email.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email, False otherwise
    """
    import re
    
    # Simple email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_company_keywords() -> list[str]:
    """
    Get a list of keywords indicating pharmaceutical or biotech companies.
    
    Returns:
        List of company keywords
    """
    return [
        "pharm", "therapeutics", "biotech", "biopharma", "drug", "medicines",
        "inc", "corp", "llc", "ltd", "gmbh", "co.", "company", "laboratories",
        "labs", "health", "medical", "life sciences", "diagnostics", "genomics",
        "biosciences", "technologies", "biologics", "pharmaceuticals"
    ]

def get_academic_keywords() -> list[str]:
    """
    Get a list of keywords indicating academic institutions.
    
    Returns:
        List of academic keywords
    """
    return [
        "university", "college", "institute", "school", "faculty", 
        "academy", "hospital", "clinic", "medical center", "laboratory",
        "national", "federal", "ministry", "department", "government",
        "research center", "foundation", "association"
    ] 
