# coding: utf-8
import unittest

from publication import documents_dates
from publication import journals


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
