"""
Tests for the parser module.
"""

import io
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile

import pandas as pd

from pubmed_papers.parser import PaperDataParser


class TestPaperDataParser(unittest.TestCase):
    """Test cases for the PaperDataParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_papers = [
            {
                "PubmedID": "12345",
                "Title": "Test Paper 1",
                "Publication Date": "2022-01-15",
                "Non-academic Author(s)": "John Doe",
                "Company Affiliation(s)": "Pharma Inc",
                "Corresponding Author Email": "john@pharma.com"
            },
            {
                "PubmedID": "67890",
                "Title": "Test Paper 2",
                "Publication Date": "2022-02-20",
                "Non-academic Author(s)": "",
                "Company Affiliation(s)": "",
                "Corresponding Author Email": "jane@university.edu"
            },
            {
                "PubmedID": "54321",
                "Title": "Test Paper 3",
                "Publication Date": "2022-03-10",
                "Non-academic Author(s)": "Bob Smith",
                "Company Affiliation(s)": "Biotech Corp",
                "Corresponding Author Email": "bob@biotech.com"
            }
        ]

    def test_filter_papers_with_company_authors(self):
        """Test the filter_papers_with_company_authors method."""
        # Filter papers
        filtered_papers = PaperDataParser.filter_papers_with_company_authors(self.sample_papers)
        
        # Check that papers with company affiliations are kept
        self.assertEqual(len(filtered_papers), 2)
        self.assertEqual(filtered_papers[0]["PubmedID"], "12345")
        self.assertEqual(filtered_papers[1]["PubmedID"], "54321")
        
        # Check with empty list
        filtered_papers = PaperDataParser.filter_papers_with_company_authors([])
        self.assertEqual(len(filtered_papers), 0)

    def test_export_to_csv_file(self):
        """Test exporting papers to a CSV file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp_path = tmp.name
        
        try:
            # Export to file
            PaperDataParser.export_to_csv(self.sample_papers, tmp_path)
            
            # Check that the file exists and has the correct content
            self.assertTrue(os.path.exists(tmp_path))
            
            # Read the file and check its content
            df = pd.read_csv(tmp_path)
            self.assertEqual(len(df), 3)
            self.assertEqual(list(df.columns), [
                "PubmedID", "Title", "Publication Date",
                "Non-academic Author(s)", "Company Affiliation(s)",
                "Corresponding Author Email"
            ])
            self.assertEqual(df.iloc[0]["PubmedID"], "12345")
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_export_to_csv_string(self):
        """Test exporting papers to a CSV string."""
        # Export to string
        csv_string = PaperDataParser.export_to_csv(self.sample_papers)
        
        # Check that the string is not empty
        self.assertTrue(csv_string)
        
        # Check with empty list
        csv_string = PaperDataParser.export_to_csv([])
        self.assertEqual(csv_string, "")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_print_results(self, mock_stdout):
        """Test the print_results method."""
        # Print results
        PaperDataParser.print_results(self.sample_papers)
        
        # Check that output contains expected text
        output = mock_stdout.getvalue()
        self.assertIn("Found 3 papers", output)
        self.assertIn("Test Paper 1", output)
        self.assertIn("Pharma Inc", output)
        
        # Test with empty list
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        PaperDataParser.print_results([])
        
        output = mock_stdout.getvalue()
        self.assertIn("No papers found", output)


if __name__ == "__main__":
    unittest.main() 
