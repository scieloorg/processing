# coding: utf-8
import unittest

from utils import accessstats_server


class ThirftClientsTest(unittest.TestCase):

    def test_compute_access_lifetime(self):

        accessstats = accessstats_server()

        query_result = {
            "hits": {
                "hits": [],
                "total": 10187,
                "max_score": 0.0
            },
            "timed_out": False,
            "took": 26,
            "aggregations": {
                "publication_year": {
                    "buckets": [
                        {
                            "access_total": {
                                "value": 122651.0
                            },
                            "access_year": {
                                "buckets": [
                                    {
                                        "access_html": {
                                            "value": 28622.0
                                        },
                                        "doc_count": 276,
                                        "access_abstract": {
                                            "value": 820.0
                                        },
                                        "key": "2014",
                                        "access_total": {
                                            "value": 34370.0
                                        },
                                        "access_epdf": {
                                            "value": 0.0
                                        },
                                        "access_pdf": {
                                            "value": 4928.0
                                        }
                                    },
                                    {
                                        "access_html": {
                                            "value": 27590.0
                                        },
                                        "doc_count": 275,
                                        "access_abstract": {
                                            "value": 465.0
                                        },
                                        "key": "2015",
                                        "access_total": {
                                            "value": 33234.0
                                        },
                                        "access_epdf": {
                                            "value": 70.0
                                        },
                                        "access_pdf": {
                                            "value": 5109.0
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 562
                            },
                            "key": "2010",
                            "doc_count": 1113
                        },
                        {
                            "access_total": {
                                "value": 66330.0
                            },
                            "access_year": {
                                "buckets": [
                                    {
                                        "access_html": {
                                            "value": 10195.0
                                        },
                                        "doc_count": 273,
                                        "access_abstract": {
                                            "value": 970.0
                                        },
                                        "key": "2014",
                                        "access_total": {
                                            "value": 23490.0
                                        },
                                        "access_epdf": {
                                            "value": 0.0
                                        },
                                        "access_pdf": {
                                            "value": 12325.0
                                        }
                                    },
                                    {
                                        "access_html": {
                                            "value": 12989.0
                                        },
                                        "doc_count": 276,
                                        "access_abstract": {
                                            "value": 438.0
                                        },
                                        "key": "2015",
                                        "access_total": {
                                            "value": 15545.0
                                        },
                                        "access_epdf": {
                                            "value": 52.0
                                        },
                                        "access_pdf": {
                                            "value": 2066.0
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 552
                            },
                            "key": "2009",
                            "doc_count": 1101
                        }
                    ],
                    "doc_count_error_upper_bound": -1,
                    "sum_other_doc_count": 7973
                }
            },
            "_shards": {
                "successful": 5,
                "failed": 0,
                "total": 5
            }
        }

        expected = [
            ["2010", "2014", 28622, 820, 4928, 0, 34370],
            ["2010", "2015", 27590, 465, 5109, 70, 33234],
            ["2009", "2014", 10195, 970, 12325, 0, 23490],
            ["2009", "2015", 12989, 438, 2066, 52, 15545]
        ]

        result = accessstats._compute_access_lifetime(query_result)

        self.assertEqual(sorted(expected), result)