# coding: utf-8
"""
Unit tests for KBART URL generation logic

Note: These tests verify the URL generation method in isolation using mocks.
Full integration tests require the complete SciELO infrastructure (ArticleMeta, etc.)
"""
import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class KbartUrlGenerationTest(unittest.TestCase):
    """
    Tests for the _generate_journal_url method that prefers electronic ISSN over print ISSN.
    This addresses the issue where journals transition to electronic-only publication.
    """

    def _create_dumper_instance(self):
        """Helper to create a Dumper instance without dependencies"""
        # Import here to avoid module-level import errors
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from export.kbart import Dumper
        dumper = Dumper.__new__(Dumper)
        return dumper

    def test_generate_journal_url_with_electronic_issn(self):
        """
        Test that _generate_journal_url prefers electronic ISSN when available.
        This is the fix for the Revista española de sanidad penitenciaria issue.
        """
        dumper = self._create_dumper_instance()
        
        # Create a mock journal object mimicking the problematic journal
        journal = Mock()
        journal.scielo_domain = 'scielo.isciii.es'
        journal.electronic_issn = '2013-6463'  # Current ISSN
        journal.print_issn = '1575-0620'  # Old ISSN (no longer used)
        journal.any_issn = Mock(return_value='2013-6463')  # Prefers electronic
        
        # Test the URL generation
        url = dumper._generate_journal_url(journal)
        
        # Verify the URL uses the electronic ISSN (2013-6463), not print ISSN (1575-0620)
        self.assertIn('2013-6463', url)
        self.assertNotIn('1575-0620', url)
        self.assertEqual(url, 'http://scielo.isciii.es/scielo.php?script=sci_issues&pid=2013-6463&lng=en')

    def test_generate_journal_url_with_only_print_issn(self):
        """
        Test that _generate_journal_url falls back to print ISSN when electronic is not available
        """
        dumper = self._create_dumper_instance()
        
        # Create a mock journal object
        journal = Mock()
        journal.scielo_domain = 'scielo.br'
        journal.electronic_issn = None
        journal.print_issn = '1234-5678'
        journal.any_issn = Mock(return_value='1234-5678')
        
        # Test the URL generation
        url = dumper._generate_journal_url(journal)
        
        # Verify the URL uses the print ISSN
        self.assertIn('1234-5678', url)
        self.assertEqual(url, 'http://scielo.br/scielo.php?script=sci_issues&pid=1234-5678&lng=en')

    def test_generate_journal_url_with_no_issn(self):
        """
        Test that _generate_journal_url returns empty string when no ISSN is available
        """
        dumper = self._create_dumper_instance()
        
        # Create a mock journal object
        journal = Mock()
        journal.scielo_domain = 'scielo.br'
        journal.electronic_issn = None
        journal.print_issn = None
        journal.any_issn = Mock(return_value=None)
        
        # Test the URL generation
        url = dumper._generate_journal_url(journal)
        
        # Verify the URL is empty
        self.assertEqual(url, '')

    def test_generate_journal_url_with_no_domain(self):
        """
        Test that _generate_journal_url returns empty string when no domain is available
        """
        dumper = self._create_dumper_instance()
        
        # Create a mock journal object
        journal = Mock()
        journal.scielo_domain = None
        journal.electronic_issn = '2013-6463'
        journal.print_issn = '1575-0620'
        journal.any_issn = Mock(return_value='2013-6463')
        
        # Test the URL generation
        url = dumper._generate_journal_url(journal)
        
        # Verify the URL is empty
        self.assertEqual(url, '')


if __name__ == '__main__':
    unittest.main()
