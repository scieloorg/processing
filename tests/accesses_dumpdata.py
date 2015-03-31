# coding: utf-8
import unittest

from accesses import dumpdata
from xylose.scielodocument import Article

class DumpData(unittest.TestCase):

    def test_ckeck_given_issns(self):

        result = dumpdata.ckeck_given_issns(['1234-4321', '1244-333x'])

        self.assertEqual(sorted(result), sorted(['1234-4321', '1244-333x']))

    def test_ckeck_given_issns_with_invalid_issn(self):

        result = dumpdata.ckeck_given_issns(['1234-432a', '1244-333x'])

        self.assertEqual(result, ['1244-333x'])

    def test_ckeck_given_issns_empty(self):

        result = dumpdata.ckeck_given_issns([])

        self.assertEqual(result, [])


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
            sorted(['/PDF/ABCD/V22N3/EN_V22N3A01.PDF', '/PDF/ABCD/V22N3/V22N3A01.PDF'])
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

        result = dumpdata.join_accesses('S0102-67202009000300001', data)

        expected = [
            ['abstract', '2012-01-08', '3'],
            ['abstract', '2012-03-28', '1'],
            ['pdf', '2013-03-28', '1'],
            ['pdf', '2012-01-08', '3'],
            ['pdf', '2012-03-28', '2'],
            ['html', '2013-03-28', '1'],
            ['html', '2012-01-08', '3'],
            ['html', '2012-03-28', '1'],
            ['html', '2013-01-08', '1']
        ]

        self.assertEqual(sorted(result), sorted(expected))


    def test_join_metadata_with_accesses(self):

        from tests.fixtures import articlemeta

        article = Article(articlemeta.document)

        accesses = ['abstract', '2012-01-08', '3']
    
        result = dumpdata.join_metadata_with_accesses(article, accesses)

        expected = {
                'id': 'scl_S0102-67202009000300001',
                'languages': ['pt'],
                'issn': '0102-6720',
                'document_type': 'research-article',
                'aff_countries': ['undefined'],
                'access_total': '3',
                'access_date': '2012-01-08',
                'subject_areas': ['Health Sciences'],
                'access_type':'abstract',
                'pid': 'S0102-67202009000300001',
                'collection': 'scl',
                'publication_year': '2009',
                'journal_title': 'ABCD. Arquivos Brasileiros de Cirurgia Digestiva (São Paulo)',
                'publication_date': '2009-09',
                'issue': 'scl_S0102-672020090003'
            }

        self.assertEqual(sorted([k+str(v) for k, v in expected.items()]), sorted([k+str(v) for k, v in result.items()]))
