# coding: utf-8
import unittest

from publication import journals


class PublicationTest(unittest.TestCase):

    def test_interruption_status(self):

        data = [
            (u'2010', 'current', ''),
            (u'2013-10', 'suspended', 'suspended-by-committee')
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
            (u'2010', 'current', '')
        ]

        result = journals.interruption_status(data)

        self.assertEqual(None, result)

    def test_interruption_status_2(self):

        data = [
            (u'2010', 'current', ''),
            (u'2013-10', 'suspended', 'suspended-by-committee'),
            (u'2014-10', 'current', ''),
            (u'2015-10', 'deceased', '')

        ]

        expected = ('2015-10', 'deceased', '')

        result = journals.interruption_status(data)

        self.assertEqual(expected, result)
