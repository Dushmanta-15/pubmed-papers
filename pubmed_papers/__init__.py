"""
PubMed Papers - A tool to fetch research papers from PubMed with pharmaceutical/biotech company authors.

This package provides both a library and a command-line interface to fetch and filter PubMed papers.
"""

__version__ = "0.1.0"

# Export public API
from pubmed_papers.fetcher import PubMedFetcher
from pubmed_papers.parser import PaperDataParser

__all__ = ["PubMedFetcher", "PaperDataParser"]