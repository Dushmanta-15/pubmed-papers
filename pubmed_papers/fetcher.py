"""
Module for fetching papers from PubMed API.
"""

from typing import Dict, List, Optional, Any, Tuple, cast
import time
import logging
from urllib.parse import quote

import requests
from Bio import Entrez

from pubmed_papers.utils import setup_logger

# Configure logger
logger = setup_logger(__name__)

class PubMedFetcher:
    """
    Class to fetch papers from PubMed API using Entrez.
    """

    def __init__(self, email: str = "your.email@example.com", api_key: Optional[str] = None) -> None:
        """
        Initialize the PubMed fetcher.

        Args:
            email: Email to use for Entrez API (required by NCBI).
            api_key: Optional API key to increase rate limits.
        """
        self.email = email
        self.api_key = api_key
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        self.batch_size = 100  # Number of records to fetch in each batch

    def search(self, query: str, max_results: int = 1000, debug: bool = False) -> List[str]:
        """
        Search PubMed for papers matching the query.

        Args:
            query: PubMed search query.
            max_results: Maximum number of results to return.
            debug: Whether to print debug information.

        Returns:
            List of PubMed IDs matching the query.
        """
        if debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(f"Searching PubMed with query: {query}")

        try:
            # First get the count of results
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=0,
                usehistory="y"
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            count = int(search_results["Count"])
            webenv = search_results["WebEnv"]
            query_key = search_results["QueryKey"]

            if debug:
                logger.debug(f"Found {count} results")

            # Limit the results to max_results
            count = min(count, max_results)

            # Fetch results in batches
            pubmed_ids: List[str] = []
            for start in range(0, count, self.batch_size):
                end = min(count, start + self.batch_size)
                if debug:
                    logger.debug(f"Downloading record {start+1} to {end}")

                fetch_handle = Entrez.esearch(
                    db="pubmed",
                    term=query,
                    retstart=start,
                    retmax=self.batch_size,
                    retmode="xml"
                )
                results = Entrez.read(fetch_handle)
                fetch_handle.close()
                
                # Add IDs to our list
                batch_ids = results["IdList"]
                pubmed_ids.extend(batch_ids)
                
                # Be nice to the NCBI servers
                time.sleep(0.5)

            return pubmed_ids

        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []

    def fetch_details(self, pubmed_ids: List[str], debug: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch details for a list of PubMed IDs.

        Args:
            pubmed_ids: List of PubMed IDs to fetch details for.
            debug: Whether to print debug information.

        Returns:
            List of dictionaries containing paper details.
        """
        if not pubmed_ids:
            return []

        if debug:
            logger.debug(f"Fetching details for {len(pubmed_ids)} papers")

        paper_details: List[Dict[str, Any]] = []

        # Fetch papers in batches to avoid API limits
        for i in range(0, len(pubmed_ids), self.batch_size):
            batch_ids = pubmed_ids[i:i + self.batch_size]
            
            if debug:
                logger.debug(f"Fetching batch {i//self.batch_size + 1}, size: {len(batch_ids)}")
            
            try:
                fetch_handle = Entrez.efetch(
                    db="pubmed",
                    id=",".join(batch_ids),
                    retmode="xml"
                )
                records = Entrez.read(fetch_handle)
                fetch_handle.close()

                # Process each paper in the batch
                for paper in records["PubmedArticle"]:
                    paper_info = self._extract_paper_info(paper, debug)
                    if paper_info:
                        paper_details.append(paper_info)
                
                # Be nice to the NCBI servers
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching paper details: {e}")
        
        return paper_details

    def _extract_paper_info(self, paper: Dict[str, Any], debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        Extract relevant information from a PubMed paper record.

        Args:
            paper: PubMed paper record.
            debug: Whether to print debug information.

        Returns:
            Dictionary containing extracted paper information or None if there's an error.
        """
        try:
            article = paper["MedlineCitation"]["Article"]
            
            # Extract basic info
            pubmed_id = paper["MedlineCitation"]["PMID"]
            title = article["ArticleTitle"]
            
            # Extract publication date
            try:
                pub_date_info = article["Journal"]["JournalIssue"]["PubDate"]
                pub_date = self._format_pub_date(pub_date_info)
            except KeyError:
                pub_date = "Unknown"
            
            # Extract authors and their affiliations
            authors = self._extract_authors(article)
            
            # Find non-academic authors and their affiliations
            non_academic_authors, company_affiliations, corresponding_email = self._find_non_academic_authors(authors)
            
            return {
                "PubmedID": pubmed_id,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": "; ".join(non_academic_authors) if non_academic_authors else "",
                "Company Affiliation(s)": "; ".join(company_affiliations) if company_affiliations else "",
                "Corresponding Author Email": corresponding_email
            }
            
        except Exception as e:
            if debug:
                logger.error(f"Error extracting paper info: {e}")
            return None

    def _format_pub_date(self, pub_date_info: Dict[str, Any]) -> str:
        """
        Format publication date from PubMed record.

        Args:
            pub_date_info: Dictionary containing publication date information.

        Returns:
            Formatted publication date string.
        """
        # PubMed date format can vary - handle different possibilities
        if "Year" in pub_date_info:
            year = pub_date_info["Year"]
            month = pub_date_info.get("Month", "01")
            day = pub_date_info.get("Day", "01")
            
            # Convert month names to numbers if needed
            month_map = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }
            
            if month in month_map:
                month = month_map[month]
            
            # Ensure month and day are 2 digits
            month = month.zfill(2) if isinstance(month, str) else f"{month:02d}"
            day = day.zfill(2) if isinstance(day, str) else f"{day:02d}"
            
            return f"{year}-{month}-{day}"
        elif "MedlineDate" in pub_date_info:
            # Handle MedlineDate format (e.g., "2022 Jan-Feb")
            return pub_date_info["MedlineDate"]
        else:
            return "Unknown"

    def _extract_authors(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract authors and their affiliations from a PubMed article.

        Args:
            article: PubMed article record.

        Returns:
            List of dictionaries containing author information.
        """
        authors_list: List[Dict[str, Any]] = []
        
        # Check if article has author list
        if "AuthorList" not in article:
            return authors_list
        
        authors = article["AuthorList"]
        
        for author in authors:
            # Skip if not a complete author entry
            if "LastName" not in author and "CollectiveName" not in author:
                continue
            
            author_info: Dict[str, Any] = {}
            
            # Get author name
            if "LastName" in author:
                author_name = f"{author.get('LastName', '')}"
                if "ForeName" in author:
                    author_name = f"{author.get('ForeName', '')} {author_name}"
                elif "Initials" in author:
                    author_name = f"{author.get('Initials', '')} {author_name}"
            else:
                author_name = author.get("CollectiveName", "Unknown Author")
            
            author_info["name"] = author_name
            
            # Get author affiliations
            affiliations = []
            
            # Modern PubMed format
            if "AffiliationInfo" in author:
                for affiliation in author["AffiliationInfo"]:
                    if "Affiliation" in affiliation:
                        affiliations.append(affiliation["Affiliation"])
            
            # Extract email if present (might be part of affiliation)
            email = ""
            for affiliation in affiliations:
                if "@" in affiliation:
                    # Simple extraction, can be improved with regex
                    parts = affiliation.split()
                    for part in parts:
                        if "@" in part:
                            email = part.strip(".,;()")
            
            author_info["affiliations"] = affiliations
            author_info["email"] = email
            
            authors_list.append(author_info)
        
        return authors_list

    def _find_non_academic_authors(self, authors: List[Dict[str, Any]]) -> Tuple[List[str], List[str], str]:
        """
        Identify authors affiliated with pharmaceutical or biotech companies.

        Args:
            authors: List of author information dictionaries.

        Returns:
            Tuple of (non-academic author names, company affiliations, corresponding author email).
        """
        non_academic_authors: List[str] = []
        company_affiliations: List[str] = []
        corresponding_email = ""
        
        # Common academic keywords
        academic_keywords = [
            "university", "college", "institute", "school", "academy", 
            "hospital", "clinic", "medical center", "centre", "laboratory",
            "national", "federal", "ministry"
        ]
        
        # Pharma/biotech indicators
        company_keywords = [
            "pharm", "bio", "therapeutics", "medicines", "drugs", "health",
            "medical", "life sciences", "biotech", "inc", "corp", "llc", "ltd", "gmbh"
        ]
        
        for author in authors:
            is_non_academic = False
            company_name = ""
            
            for affiliation in author.get("affiliations", []):
                affiliation_lower = affiliation.lower()
                
                # Skip if clearly academic
                if any(keyword in affiliation_lower for keyword in academic_keywords):
                    continue
                
                # Check for company indicators
                if any(keyword in affiliation_lower for keyword in company_keywords):
                    is_non_academic = True
                    # Extract company name (simple approach)
                    words = affiliation.split(',')
                    if len(words) > 0:
                        company_name = words[0].strip()
                    break
            
            if is_non_academic:
                non_academic_authors.append(author["name"])
                if company_name and company_name not in company_affiliations:
                    company_affiliations.append(company_name)
            
            # Check for corresponding author email
            if author.get("email") and not corresponding_email:
                corresponding_email = author["email"]
        
        return non_academic_authors, company_affiliations, corresponding_email
