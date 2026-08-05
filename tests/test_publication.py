import unittest
from unittest.mock import MagicMock, patch

from publication import documents_dates, journals, journals_status_changes


class PublicationTest(unittest.TestCase):

    def test_interruption_status(self):

        data = [
            ('2010', 'current', ''),
            ('2013-10', 'suspended', 'suspended-by-committee')
        ]

        expected = ('2013-10', 'suspended', 'suspended-by-committee')

        result = journals.interruption_status(data)

        self.assertEqual(expected, result)

    def test_interruption_status_0(self):

        data = []

        result = journals.interruption_status(data)

        self.assertEqual(None, result)

    def test_interruption_status_1(self):

        data = [
            ('2010', 'current', '')
        ]

        result = journals.interruption_status(data)

        self.assertEqual(None, result)

    def test_interruption_status_2(self):

        data = [
            ('2010', 'current', ''),
            ('2013-10', 'suspended', 'suspended-by-committee'),
            ('2014-10', 'current', ''),
            ('2015-10', 'deceased', '')

        ]

        expected = ('2015-10', 'deceased', '')

        result = journals.interruption_status(data)

        self.assertEqual(expected, result)

    def test_document_dates_missing_issue_when_reading_aop_date(self):

        class Metadata(object):
            document_publication_date = '2020'
            creation_date = ''
            update_date = ''
            issue_publication_date = '2020'
            collection_acronym = 'dom'
            publisher_id = 'S0000-00002020000100001'
            document_type = 'research-article'
            receive_date = ''
            acceptance_date = ''
            review_date = ''

            @property
            def ahead_publication_date(self):
                raise KeyError('issue')

        class Journal(object):
            print_issn = '0000-0000'
            electronic_issn = ''
            scielo_issn = '0000-0000'
            title = 'Journal'
            subject_areas = ['Health Sciences']
            current_status = 'current'

        data = Metadata()
        data.journal = Journal()

        dumper = documents_dates.Dumper.__new__(documents_dates.Dumper)

        result = dumper.fmt_csv(data)

        self.assertIn('"S0000-00002020000100001"', result)

    def test_journals_fmt_csv_handles_none_creation_date_and_title(self):
        with patch.object(journals.utils, "articlemeta_server"), \
             patch.object(journals.utils, "publicationstats_server"), \
             patch.object(journals, "Analytics"):
            dumper = journals.Dumper.__new__(journals.Dumper)
            dumper._years = 6
            dumper.years_range = [2026, 2025, 2024, 2023, 2022, 2021]
            dumper._first_included_document_by_journal = MagicMock(return_value=None)
            dumper._last_included_document_by_journal = MagicMock(return_value=None)
            dumper._number_of_issues_by_year = MagicMock(return_value=[(2026, 0)] * 6)
            dumper._number_of_articles_by_year = MagicMock(return_value=[(2026, 0)] * 6)
            dumper._documents_languages_by_year = MagicMock(return_value={2026: {'pt': 0, 'es': 0, 'en': 0, 'other': 0}})

            mock_journal = MagicMock()
            mock_journal.title = None
            mock_journal.subtitle = None
            mock_journal.creation_date = None
            mock_journal.print_issn = "0000-0000"
            mock_journal.electronic_issn = None
            mock_journal.scielo_issn = "0000-0000"
            mock_journal.collection_acronym = "rvt"
            mock_journal.subject_areas = None
            mock_journal.publisher_name = None
            mock_journal.permissions = None
            mock_journal.periodicity = (1, "Annual")
            mock_journal.periodicity_in_months = "12"
            mock_journal.status_history = [("2020-01", "suspended", None)]

            result = dumper.fmt_csv(mock_journal)
            self.assertIn('"0000-0000"', result)
            self.assertIn('""', result)

    def test_journals_status_changes_fmt_csv_handles_none_reason(self):
        dumper = journals_status_changes.Dumper.__new__(journals_status_changes.Dumper)
        mock_journal = MagicMock()
        mock_journal.title = "Journal"
        mock_journal.print_issn = "0000-0000"
        mock_journal.electronic_issn = None
        mock_journal.scielo_issn = "0000-0000"
        mock_journal.collection_acronym = "rvt"
        mock_journal.subject_areas = None
        mock_journal.current_status = "suspended"

        history = ("2020-01-01", "suspended", None)

        result = dumper.fmt_csv(mock_journal, history)
        self.assertIn('"suspended"', result)
        self.assertIn('""', result)
