"""
Command-line interface for the pubmed_papers package.
"""

import argparse
import logging
import sys
from typing import List, Optional

from pubmed_papers.fetcher import PubMedFetcher
from pubmed_papers.parser import PaperDataParser
from pubmed_papers.utils import setup_logger

# Configure logger
logger = setup_logger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments (default: sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with pharmaceutical/biotech company authors.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "query",
        help="PubMed search query (supports full PubMed query syntax)"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Output file path to save results as CSV (if not provided, results will be printed to console)"
    )
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Print debug information during execution"
    )
    
    parser.add_argument(
        "-m", "--max-results",
        type=int,
        default=500,
        help="Maximum number of papers to fetch"
    )
    
    parser.add_argument(
        "-e", "--email",
        default="your.email@example.com",
        help="Email address for NCBI Entrez API (required by NCBI)"
    )
    
    parser.add_argument(
        "-k", "--api-key",
        help="NCBI API key to increase rate limits"
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the command-line interface.
    
    Args:
        args: Command-line arguments (default: sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parsed_args = parse_args(args)
    
    # Set up debugging
    if parsed_args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
        logger.debug(f"Arguments: {parsed_args}")
    
    try:
        # Initialize the PubMed fetcher
        fetcher = PubMedFetcher(
            email=parsed_args.email,
            api_key=parsed_args.api_key
        )
        
        # Search for papers
        logger.info(f"Searching PubMed for: {parsed_args.query}")
        pubmed_ids = fetcher.search(
            query=parsed_args.query,
            max_results=parsed_args.max_results,
            debug=parsed_args.debug
        )
        
        if not pubmed_ids:
            logger.warning("No papers found matching the query")
            return 0
        
        logger.info(f"Found {len(pubmed_ids)} papers matching the query")
        
        # Fetch paper details
        logger.info("Fetching paper details...")
        papers = fetcher.fetch_details(pubmed_ids, debug=parsed_args.debug)
        
        # Filter for papers with company authors
        logger.info("Filtering papers with pharmaceutical/biotech company authors...")
        filtered_papers = PaperDataParser.filter_papers_with_company_authors(papers)
        
        logger.info(f"Found {len(filtered_papers)} papers with company authors")
        
        # Export results
        if parsed_args.file:
            PaperDataParser.export_to_csv(filtered_papers, parsed_args.file)
            logger.info(f"Results saved to {parsed_args.file}")
        else:
            # Print to console
            PaperDataParser.print_results(filtered_papers)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        if parsed_args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
