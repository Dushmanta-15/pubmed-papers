"""
Tests for the fetcher module.
"""

import unittest
from unittest.mock import patch, MagicMock

from pubmed_papers.fetcher import PubMedFetcher


class TestPubMedFetcher(unittest.TestCase):
    """Test cases for the PubMedFetcher class."""

    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PubMedFetcher(email="test@example.com")

    @patch("pubmed_papers.fetcher.Entrez")
    def test_search(self, mock_entrez):
        """Test the search method."""
        # Mock the Entrez.esearch and Entrez.read methods
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        
        mock_search_results = {
            "Count": "100",
            "WebEnv": "web_env",
            "QueryKey": "query_key",
            "IdList": ["12345", "67890"]
        }
        mock_entrez.read.return_value = mock_search_results

        # Call the method
        result = self.fetcher.search("test query", max_results=10)

        # Check that Entrez.esearch was called with the correct parameters
        mock_entrez.esearch.assert_called_with(
            db="pubmed",
            term="test query",
            retmax=0,
            usehistory="y"
        )
        
        # Check that the result is the mock IdList
        self.assertEqual(result, ["12345", "67890"])

    @patch("pubmed_papers.fetcher.Entrez")
    def test_fetch_details(self, mock_entrez):
        """Test the fetch_details method."""
        # Mock the Entrez.efetch method
        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle
        
        # Mock the Entrez.read method
        mock_records = {
            "PubmedArticle": [
                {
                    "MedlineCitation": {
                        "PMID": "12345",
                        "Article": {
                            "ArticleTitle": "Test Article",
                            "Journal": {
                                "JournalIssue": {
                                    "PubDate": {
                                        "Year": "2022",
                                        "Month": "Jan"
                                    }
                                }
                            },
                            "AuthorList": [
                                {
                                    "LastName": "Doe",
                                    "ForeName": "John",
                                    "AffiliationInfo": [
                                        {"Affiliation": "Pharma Inc, USA"}
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]
        }
        mock_entrez.read.return_value = mock_records
        
        # Patch the _extract_paper_info method
        with patch.object(
            self.fetcher, '_extract_paper_info',
            return_value={
                "PubmedID": "12345",
                "Title": "Test Article",
                "Publication Date": "2022-01-01",
                "Non-academic Author(s)": "John Doe",
                "Company Affiliation(s)": "Pharma Inc",
                "Corresponding Author Email": ""
            }
        ):
            # Call the method
            result = self.fetcher.fetch_details(["12345"])
            
            # Check that Entrez.efetch was called with the correct parameters
            mock_entrez.efetch.assert_called_with(
                db="pubmed",
                id="12345",
                retmode="xml"
            )
            
            # Check the result
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["Title"], "Test Article")
            self.assertEqual(result[0]["PubmedID"], "12345")

    def test_format_pub_date(self):
        """Test the _format_pub_date method."""
        # Test with Year, Month, Day
        pub_date_info = {"Year": "2022", "Month": "01", "Day": "15"}
        result = self.fetcher._format_pub_date(pub_date_info)
        self.assertEqual(result, "2022-01-15")
        
        # Test with Month as text
        pub_date_info = {"Year": "2022", "Month": "Jan", "Day": "15"}
        result = self.fetcher._format_pub_date(pub_date_info)
        self.assertEqual(result, "2022-01-15")
        
        # Test with MedlineDate
        pub_date_info = {"MedlineDate": "2022 Jan-Feb"}
        result = self.fetcher._format_pub_date(pub_date_info)
        self.assertEqual(result, "2022 Jan-Feb")
        
        # Test with missing info
        pub_date_info = {}
        result = self.fetcher._format_pub_date(pub_date_info)
        self.assertEqual(result, "Unknown")

    def test_find_non_academic_authors(self):
        """Test the _find_non_academic_authors method."""
        # Test with non-academic author
        authors = [
            {
                "name": "John Doe",
                "affiliations": ["Pharma Inc, USA"],
                "email": "john@pharma.com"
            },
            {
                "name": "Jane Smith",
                "affiliations": ["University of Science, USA"],
                "email": "jane@university.edu"
            }
        ]
        
        non_academic, companies, email = self.fetcher._find_non_academic_authors(authors)
        
        self.assertEqual(non_academic, ["John Doe"])
        self.assertEqual(companies, ["Pharma Inc"])
        self.assertEqual(email, "john@pharma.com")
        
        # Test with no non-academic authors
        authors = [
            {
                "name": "Jane Smith",
                "affiliations": ["University of Science, USA"],
                "email": "jane@university.edu"
            }
        ]
        
        non_academic, companies, email = self.fetcher._find_non_academic_authors(authors)
        
        self.assertEqual(non_academic, [])
        self.assertEqual(companies, [])
        self.assertEqual(email, "jane@university.edu")


if __name__ == "__main__":
    unittest.main()
