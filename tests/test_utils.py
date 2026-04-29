# coding: utf-8
import os
import unittest
from unittest import mock

import utils


class UtilsTest(unittest.TestCase):

    def test_ckeck_given_issns(self):

        result = utils.ckeck_given_issns(['1234-4321', '1244-333x'])

        self.assertEqual(sorted(result), sorted(['1234-4321', '1244-333x']))

    def test_ckeck_given_issns_with_invalid_issn(self):

        result = utils.ckeck_given_issns(['1234-432a', '1244-333x'])

        self.assertEqual(result, ['1244-333x'])

    def test_ckeck_given_issns_empty(self):

        result = utils.ckeck_given_issns([])

        self.assertEqual(result, [])

    def test_split_date_1(self):

        result = utils.split_date('2016-01-31')

        self.assertEqual(result, ('2016', '01', '31'))

    def test_split_date_2(self):

        result = utils.split_date('2016-01')

        self.assertEqual(result, ('2016', '01', ''))

    def test_split_date_3(self):

        result = utils.split_date('2016')

        self.assertEqual(result, ('2016', '', ''))

    def test_split_date_4(self):

        result = utils.split_date('20160131')

        self.assertEqual(result, ('', '', ''))

    def test_split_date_5(self):

        result = utils.split_date('')

        self.assertEqual(result, ('', '', ''))

    def test_get_settings_from_environment(self):

        env = {
            'ARTICLEMETA_THRIFTSERVER': 'articlemeta.scielo.org:11621',
            'RATCHET_THRIFTSERVER': 'ratchet.scielo.org:11649',
        }

        with mock.patch.dict(os.environ, env, clear=True):
            result = utils.get_settings()

        self.assertEqual(
            result['app:main']['articlemeta_thriftserver'],
            'articlemeta.scielo.org:11621'
        )
        self.assertEqual(
            result['app:main']['ratchet_thriftserver'],
            'ratchet.scielo.org:11649'
        )

    def test_get_metadata_value_returns_default_for_incomplete_metadata(self):

        class Metadata(object):
            @property
            def current_status(self):
                raise IndexError('list index out of range')

        result = utils.get_metadata_value(Metadata(), 'current_status')

        self.assertEqual(result, '')
