# coding: utf-8
import unittest

from accesses import dumpdata
from xylose.scielodocument import Article


class DumpDataTest(unittest.TestCase):

    def test_website_2018_urls(self):
        result = dumpdata.website_2018_urls(
                    acron='abcd', year_pub='2018',
                    volume='22', number='3', fpage='10', fpage_sequence=None,
                    lpage='11', article_id='e707', suppl_number='0',
                    doi='doi1510.bla1', order='12345')
        self.assertEqual(
            result,
            [u'/article/abcd/2018.v22n3suppl0/e707/',
                u'/pdf/abcd/2018.v22n3suppl0/e707/']
        )

    def test_pdf_keys(self):
        data = {
            'html': {
                'pt': 'http://www.scielo.br?script=sci_arttext&pid=S0102-67202009000300001&tlng=pt'
            },
            'pdf': {
                'pt': 'http://www.scielo.br/pdf/abcd/v22n3/v22n3a01.pdf',
                'en': 'http://www.scielo.br/pdf/abcd/v22n3/en_v22n3a01.pdf'
            }
        }

        result = dumpdata.pdf_keys(data)

        self.assertEqual(
            sorted(result),
            sorted(['/pdf/abcd/v22n3/v22n3a01.pdf', '/pdf/abcd/v22n3/en_v22n3a01.pdf'])
        )

    def test_pdf_keys_without_pdf(self):
        data = {
            'html': {
                'pt': 'http://www.scielo.br?script=sci_arttext&pid=S0102-67202009000300001&tlng=pt'
            }
        }

        result = dumpdata.pdf_keys(data)

        self.assertEqual(result, [])

    def test_fbpe_key(self):

        result = dumpdata.fbpe_key('S0102-67202009000300001')

        self.assertEqual(result, 'S0102-6720(09)000300001')

    def test_join_accesses(self):
        record_1 = {
            "abstract": {
                "total": 4,
                "y2012": {
                    "m01": {
                        "d08": 3,
                        "total": 3
                    },
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 4
                }
            },
            "html": {
                "total": 4,
                "y2012": {
                    "m01": {
                        "d08": 3,
                        "total": 3
                    },
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 4
                },
                "y2013": {
                    "m01": {
                        "d08": 1,
                        "total": 1
                    },
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 2
                }
            },
            "y2012": {
                "m01": {
                    "d08": 6,
                    "total": 6
                },
                "m03": {
                    "d28": 2,
                    "total": 2
                },
                "total": 8
            },
            "y2013": {
                "m01": {
                    "d08": 1,
                    "total": 1
                },
                "m03": {
                    "d28": 1,
                    "total": 1
                },
                "total": 2
            },
            "code": "S0102-67202009000300001",
            "issue": "0102-672020090003",
            "journal": "0102-6720",
            "total": 10,
            "type": "article"
        }

        record_2 = {
            "code": "/PDF/ABCD/V22N3/V22N3A01.PDF",
            "total": 6,
            "pdf": {
                "total": 6,
                "y2012": {
                    "m01": {
                        "d08": 3,
                        "total": 3
                    },
                    "m03": {
                        "d28": 2,
                        "total": 2
                    },
                    "total": 5
                },
                "y2013": {
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 1
                }
            },
            "y2012": {
                "m01": {
                    "d08": 3,
                    "total": 3
                },
                "m03": {
                    "d28": 2,
                    "total": 2
                },
                "total": 5
            },
            "y2013": {
                "m03": {
                    "d28": 1,
                    "total": 1
                },
                "total": 1
            }
        }

        data = [record_1, record_2]

        result = dumpdata.join_accesses('S0102-67202009000300001', data, '1500-01-01', '2014-01-01', False)

        expected = {
            '2012-01': {
                'abstract': 3,
                'pdf': 3,
                'html': 3
            },
            '2012-03': {
                'abstract': 1,
                'pdf': 2,
                'html': 1
            },
            '2013-01': {
                'html': 1
            },
            '2013-03': {
                'pdf': 1,
                'html': 1
            }
        }

        self.assertEqual(sorted(result), sorted(expected))


    def test_join_accesses_dayly(self):
        record_1 = {
            "abstract": {
                "total": 4,
                "y2012": {
                    "m01": {
                        "d08": 3,
                        "total": 3
                    },
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 4
                }
            },
            "html": {
                "total": 4,
                "y2012": {
                    "m01": {
                        "d08": 3,
                        "total": 3
                    },
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 4
                },
                "y2013": {
                    "m01": {
                        "d08": 1,
                        "total": 1
                    },
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 2
                }
            },
            "y2012": {
                "m01": {
                    "d08": 6,
                    "total": 6
                },
                "m03": {
                    "d28": 2,
                    "total": 2
                },
                "total": 8
            },
            "y2013": {
                "m01": {
                    "d08": 1,
                    "total": 1
                },
                "m03": {
                    "d28": 1,
                    "total": 1
                },
                "total": 2
            },
            "code": "S0102-67202009000300001",
            "issue": "0102-672020090003",
            "journal": "0102-6720",
            "total": 10,
            "type": "article"
        }

        record_2 = {
            "code": "/PDF/ABCD/V22N3/V22N3A01.PDF",
            "total": 6,
            "pdf": {
                "total": 6,
                "y2012": {
                    "m01": {
                        "d08": 3,
                        "total": 3
                    },
                    "m03": {
                        "d28": 2,
                        "total": 2
                    },
                    "total": 5
                },
                "y2013": {
                    "m03": {
                        "d28": 1,
                        "total": 1
                    },
                    "total": 1
                }
            },
            "y2012": {
                "m01": {
                    "d08": 3,
                    "total": 3
                },
                "m03": {
                    "d28": 2,
                    "total": 2
                },
                "total": 5
            },
            "y2013": {
                "m03": {
                    "d28": 1,
                    "total": 1
                },
                "total": 1
            }
        }

        data = [record_1, record_2]

        result = dumpdata.join_accesses('S0102-67202009000300001', data, '1500-01-01', '2014-01-01', True)

        expected = {
            '2012-01-08': {
                'abstract': 3,
                'pdf': 3,
                'html': 3
            },
            '2012-03-28': {
                'html': 1
            },
            '2013-01-08': {
                'pdf': 1,
                'html': 1
            },
            '2013-03-28': {
                'pdf': 1,
                'html': 1
            }
        }

        self.assertEqual(sorted(result), sorted(expected))

    def test_join_metadata_with_accesses(self):

        from tests.fixtures import articlemeta

        article = Article(articlemeta.document)

        accesses = {
            'abstract': 3,
            'html': 1,
            'pdf': 10
        }

        result = dumpdata.join_metadata_with_accesses(article, '2012-01-08', accesses)

        expected = {
                'id': 'scl_S0102-67202009000300001',
                'languages': ['pt'],
                'issn': '0102-6720',
                'issns': {'0102-6720'},
                'document_type': 'research-article',
                'aff_countries': ['undefined'],
                'document_title': 'An\u00e1lise de custos entre a raquianestesia e a anestesia venosa com propofol associada ao bloqueio perianal local em opera\u00e7\u00f5es anorretais',
                'issue_title': 'ABCD, arq. bras. cir. dig., 2009, v22n3',
                'access_total': 14,
                'access_abstract': 3,
                'access_html': 1,
                'access_pdf': 10,
                'access_epdf': 0,
                'access_date': '2012-01-08T00:00:00',
                'access_year': '2012',
                'access_month': '01',
                'access_day': '08',
                'subject_areas': ['Health Sciences'],
                'pid': 'S0102-67202009000300001',
                'collection': 'scl',
                'publication_year': '2009',
                'publication_date_at_scielo': '2010-05-14',
                'journal_current_status': 'current',
                'journal_title': 'ABCD. Arquivos Brasileiros de Cirurgia Digestiva (S\u00e3o Paulo)',
                'processing_date': '2010-05-14',
                'publication_date': '2009-09',
                'issue': '0102-672020090003'
            }

        self.assertEqual(sorted([k+str(v) for k, v in expected.items()]), sorted([k+str(v) for k, v in result.items()]))
