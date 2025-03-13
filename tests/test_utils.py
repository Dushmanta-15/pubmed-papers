"""
Tests for the utils module.
"""

import logging
import unittest
from unittest.mock import patch

from pubmed_papers.utils import setup_logger, validate_email, get_company_keywords, get_academic_keywords


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_setup_logger(self):
        """Test the setup_logger function."""
        # Create a logger
        logger = setup_logger("test_logger")
        
        # Check that the logger has the correct properties
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.INFO)
        self.assertTrue(logger.handlers)
        
        # Test with debug level
        debug_logger = setup_logger("debug_logger", level=logging.DEBUG)
        self.assertEqual(debug_logger.level, logging.DEBUG)

    def test_validate_email(self):
        """Test the validate_email function."""
        # Valid emails
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name+tag@domain.co.uk"))
        self.assertTrue(validate_email("x@y.z"))
        
        # Invalid emails
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("missing@tld"))
        self.assertFalse(validate_email("@domain.com"))
        self.assertFalse(validate_email("user@domain@extra.com"))
        self.assertFalse(validate_email(""))

    def test_get_company_keywords(self):
        """Test the get_company_keywords function."""
        keywords = get_company_keywords()
        
        # Check that the function returns a list of strings
        self.assertIsInstance(keywords, list)
        self.assertTrue(all(isinstance(kw, str) for kw in keywords))
        
        # Check that some expected keywords are present
        self.assertIn("pharm", keywords)
        self.assertIn("biotech", keywords)
        self.assertIn("inc", keywords)

    def test_get_academic_keywords(self):
        """Test the get_academic_keywords function."""
        keywords = get_academic_keywords()
        
        # Check that the function returns a list of strings
        self.assertIsInstance(keywords, list)
        self.assertTrue(all(isinstance(kw, str) for kw in keywords))
        
        # Check that some expected keywords are present
        self.assertIn("university", keywords)
        self.assertIn("hospital", keywords)
        self.assertIn("institute", keywords)


if __name__ == "__main__":
    unittest.main()
