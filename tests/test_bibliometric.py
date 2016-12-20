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

        self.assertEqual([('2012', ('2012', 1)), ('2012', ('2011', 2)), ('2012', ('2010', 1)), ('2012', ('2008', 2)), ('2012', ('2007', 3)), ('2012', ('2005', 2)), ('2012', ('2003', 1)), ('2012', ('2001', 1)), ('2012', ('1998', 1)), ('2012', ('1997', 1)), ('2012', ('1993', 1)), ('2012', ('1990', 1)), ('2012', ('1988', 3)), ('2012', ('1986', 1)), ('2012', ('1980', 2)), ('2012', ('1979', 1)), ('2012', ('1973', 1)), ('2015', ('2013', 1)), ('2015', ('2012', 3)), ('2015', ('2006', 1)), ('2015', ('2005', 1)), ('2015', ('2004', 1)), ('2015', ('2002', 1)), ('2015', ('1998', 1)), ('2015', ('1996', 2)), ('2015', ('1995', 1)), ('2015', ('1993', 2)), ('2015', ('1992', 5)), ('2015', ('1989', 1)), ('2015', ('1988', 1)), ('2015', ('1981', 1)), ('2015', ('1979', 1)), ('2013', ('2011', 2)), ('2013', ('2009', 2)), ('2013', ('2008', 1)), ('2013', ('2006', 1)), ('2013', ('2005', 1)), ('2013', ('2000', 2)), ('2013', ('1997', 2)), ('2013', ('1994', 1)), ('2013', ('1993', 1)), ('2013', ('1988', 1)), ('2013', ('1986', 1)), ('2013', ('1984', 1)), ('2013', ('1981', 1)), ('2013', ('1980', 1)), ('2013', ('1974', 2)), ('2014', ('2012', 2)), ('2014', ('2010', 3)), ('2014', ('2009', 1)), ('2014', ('2008', 1)), ('2014', ('2006', 1)), ('2014', ('2002', 2)), ('2014', ('1989', 1)), ('2014', ('1988', 2)), ('2014', ('1984', 3)), ('2014', ('1980', 2)), ('2014', ('1972', 1)), ('2016', ('2013', 2)), ('2016', ('2012', 1)), ('2016', ('2011', 3)), ('2016', ('2010', 1)), ('2016', ('2009', 2)), ('2016', ('2005', 3)), ('2016', ('2004', 1)), ('2016', ('2003', 1)), ('2016', ('1998', 1)), ('2016', ('1997', 1)), ('2016', ('1995', 1)), ('2016', ('1959', 1)), ('2007', ('1996', 1)), ('2007', ('1994', 1)), ('2007', ('1990', 2)), ('2007', ('1989', 2)), ('2007', ('1988', 1)), ('2007', ('1985', 1)), ('2007', ('1984', 1)), ('2007', ('1980', 1)), ('2007', ('1975', 1)), ('2007', ('1970', 1)), ('2007', ('1968', 1)), ('2011', ('2008', 1)), ('2011', ('2006', 1)), ('2011', ('2005', 1)), ('2011', ('2002', 1)), ('2011', ('2001', 2)), ('2011', ('1994', 1)), ('2011', ('1988', 1)), ('2011', ('1985', 1)), ('2011', ('1984', 1)), ('2011', ('1982', 1)), ('2011', ('1974', 2)), ('2010', ('2006', 1)), ('2010', ('2003', 1)), ('2010', ('2001', 1)), ('2010', ('2000', 1)), ('2010', ('1998', 1)), ('2010', ('1997', 1)), ('2010', ('1995', 1)), ('2010', ('1993', 1)), ('2010', ('1991', 1)), ('2010', ('1989', 1)), ('2010', ('1984', 1)), ('2010', ('1980', 1)), ('2009', ('2008', 1)), ('2009', ('2007', 2)), ('2009', ('2005', 1)), ('2009', ('2004', 1)), ('2009', ('2002', 1)), ('2009', ('1998', 1)), ('2009', ('1990', 2)), ('2009', ('1989', 1)), ('2009', ('1968', 1)), ('1999', ('1989', 1)), ('1999', ('1988', 1)), ('1999', ('1986', 2)), ('1999', ('1975', 2)), ('1999', ('1974', 2)), ('1998', ('1994', 1)), ('1998', ('1991', 2)), ('1998', ('1989', 1)), ('1998', ('1986', 1)), ('1998', ('1979', 1)), ('2006', ('2003', 1)), ('2006', ('1996', 1)), ('2006', ('1995', 1)), ('2006', ('1994', 1)), ('2006', ('1991', 1)), ('2000', ('1999', 1)), ('2000', ('1990', 1)), ('2000', ('1986', 1)), ('2000', ('1974', 1)), ('2008', ('2004', 1)), ('2008', ('2003', 1)), ('2008', ('1994', 1)), ('2008', ('1981', 1)), ('2008', ('1964', 1)), ('2004', ('1995', 1)), ('2004', ('1992', 1)), ('2004', ('1983', 1)), ('2004', ('1971', 1)), ('2001', ('1989', 1)), ('2001', ('1979', 1)), ('2005', ('1996', 1)), ('2005', ('1989', 1)), ('1997', ('1994', 1)), ('2002', ('1972', 1)), ('2003', ('1992', 1))], result)
