# coding: utf-8
import unittest
import datetime
import logging

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
