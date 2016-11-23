import unittest

from bibliometric import citedby_journal


class TestBibliometric(unittest.TestCase):

    def test_compute_citations(self):

        query_result = {
            "took": 1857,
            "hits": {
                "max_score": 0.0,
                "hits": [],
                "total": 195
            },
            "aggregations": {
                "publication_year": {
                    "sum_other_doc_count": 0,
                    "buckets": [
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "2012"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2011"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2010"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2008"
                                    },
                                    {
                                        "doc_count": 3,
                                        "key": "2007"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2005"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2003"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2001"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1998"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1997"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1993"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1990"
                                    },
                                    {
                                        "doc_count": 3,
                                        "key": "1988"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1986"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1980"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1979"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1973"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 25,
                            "key": "2012"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "2013"
                                    },
                                    {
                                        "doc_count": 3,
                                        "key": "2012"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2006"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2005"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2004"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2002"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1998"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1996"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1995"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1993"
                                    },
                                    {
                                        "doc_count": 5,
                                        "key": "1992"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1988"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1981"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1979"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 23,
                            "key": "2015"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 2,
                                        "key": "2011"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2009"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2008"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2006"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2005"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2000"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1997"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1994"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1993"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1988"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1986"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1984"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1981"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1980"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1974"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 20,
                            "key": "2013"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 2,
                                        "key": "2012"
                                    },
                                    {
                                        "doc_count": 3,
                                        "key": "2010"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2009"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2008"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2006"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2002"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1988"
                                    },
                                    {
                                        "doc_count": 3,
                                        "key": "1984"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1980"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1972"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 19,
                            "key": "2014"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 2,
                                        "key": "2013"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2012"
                                    },
                                    {
                                        "doc_count": 3,
                                        "key": "2011"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2010"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2009"
                                    },
                                    {
                                        "doc_count": 3,
                                        "key": "2005"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2004"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2003"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1998"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1997"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1995"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1959"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 18,
                            "key": "2016"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1996"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1994"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1990"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1988"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1985"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1984"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1980"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1975"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1970"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1968"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 13,
                            "key": "2007"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "2008"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2006"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2005"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2002"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2001"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1994"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1988"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1985"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1984"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1982"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1974"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 13,
                            "key": "2011"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "2006"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2003"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2001"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2000"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1998"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1997"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1995"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1993"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1991"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1984"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1980"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 12,
                            "key": "2010"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "2008"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "2007"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2005"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2004"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2002"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1998"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1990"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1968"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 11,
                            "key": "2009"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1988"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1986"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1975"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1974"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 8,
                            "key": "1999"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1994"
                                    },
                                    {
                                        "doc_count": 2,
                                        "key": "1991"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1986"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1979"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 6,
                            "key": "1998"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "2003"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1996"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1995"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1994"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1991"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 6,
                            "key": "2006"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1999"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1990"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1986"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1974"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 5,
                            "key": "2000"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "2004"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "2003"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1994"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1981"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1964"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 5,
                            "key": "2008"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1995"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1992"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1983"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1971"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 4,
                            "key": "2004"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1979"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 2,
                            "key": "2001"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1996"
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "1989"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 2,
                            "key": "2005"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1994"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 1,
                            "key": "1997"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1972"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 1,
                            "key": "2002"
                        },
                        {
                            "reference_publication_year": {
                                "sum_other_doc_count": 0,
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "1992"
                                    }
                                ],
                                "doc_count_error_upper_bound": 0
                            },
                            "doc_count": 1,
                            "key": "2003"
                        }
                    ],
                    "doc_count_error_upper_bound": 0
                }
            },
            "timed_out": False,
            "_shards": {
                "failed": 0,
                "total": 5,
                "successful": 5
            }
        }

        result = citedby_journal.compute_citations(query_result)

        self.assertEqual('x', result)
