# coding: utf-8
import unittest

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
