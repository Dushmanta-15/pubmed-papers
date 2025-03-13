"""
Module for parsing and exporting paper data.
"""

import csv
import io
import sys
from typing import Dict, List, Any, TextIO, Optional

import pandas as pd

from pubmed_papers.utils import setup_logger

# Configure logger
logger = setup_logger(__name__)

class PaperDataParser:
    """
    Class to parse and export paper data.
    """
    
    @staticmethod
    def filter_papers_with_company_authors(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter papers to only include those with at least one author from a pharma/biotech company.
        
        Args:
            papers: List of paper dictionaries.
            
        Returns:
            Filtered list of papers.
        """
        return [
            paper for paper in papers 
            if paper.get("Non-academic Author(s)") and paper.get("Company Affiliation(s)")
        ]
    
    @staticmethod
    def export_to_csv(papers: List[Dict[str, Any]], output_file: Optional[str] = None) -> Optional[str]:
        """
        Export papers to CSV format.
        
        Args:
            papers: List of paper dictionaries.
            output_file: Optional path to save the CSV file. If None, will return the CSV as a string.
            
        Returns:
            CSV string if output_file is None, else None.
        """
        if not papers:
            logger.warning("No papers to export")
            return ""
        
        # Define the CSV columns
        columns = [
            "PubmedID", 
            "Title", 
            "Publication Date", 
            "Non-academic Author(s)", 
            "Company Affiliation(s)",
            "Corresponding Author Email"
        ]
        
        try:
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(papers)
            
            if output_file:
                # Save to file
                df.to_csv(output_file, index=False, columns=columns, quoting=csv.QUOTE_NONNUMERIC)
                logger.info(f"Exported {len(papers)} papers to {output_file}")
                return None
            else:
                # Return as string
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, columns=columns, quoting=csv.QUOTE_NONNUMERIC)
                return csv_buffer.getvalue()
                
        except Exception as e:
            logger.error(f"Error exporting papers to CSV: {e}")
            return None
    
    @staticmethod
    def print_results(papers: List[Dict[str, Any]], output: TextIO = sys.stdout) -> None:
        """
        Print paper results to the specified output stream.
        
        Args:
            papers: List of paper dictionaries.
            output: Output stream to print to (default: sys.stdout).
        """
        if not papers:
            print("No papers found matching the criteria.", file=output)
            return
        
        print(f"Found {len(papers)} papers with pharmaceutical/biotech company authors:", file=output)
        print("-" * 80, file=output)
        
        for i, paper in enumerate(papers, 1):
            print(f"Paper {i}:", file=output)
            print(f"  PubMed ID: {paper.get('PubmedID', 'N/A')}", file=output)
            print(f"  Title: {paper.get('Title', 'N/A')}", file=output)
            print(f"  Publication Date: {paper.get('Publication Date', 'N/A')}", file=output)
            print(f"  Non-academic Author(s): {paper.get('Non-academic Author(s)', 'N/A')}", file=output)
            print(f"  Company Affiliation(s): {paper.get('Company Affiliation(s)', 'N/A')}", file=output)
            print(f"  Corresponding Author Email: {paper.get('Corresponding Author Email', 'N/A')}", file=output)
            print("-" * 80, file=output)
