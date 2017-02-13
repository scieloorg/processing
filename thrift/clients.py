# coding: utf-8
import os
import thriftpy
import json
import logging
from datetime import date

from articlemeta.client import ThriftClient as ArticleMetaThriftClient
from citedby.client import ThriftClient as CitedByThriftClient
from citedby.custom_query import journal_titles
from thriftpy.rpc import make_client
from xylose.scielodocument import Article, Journal

import utils

LIMIT = 1000

logger = logging.getLogger(__name__)

ratchet_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/ratchet.thrift')

accessstats_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/access_stats.thrift')

publication_stats_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/publication_stats.thrift')


class ServerError(Exception):
    def __init__(self, message=None):
        self.message = message or 'thirftclient: ServerError'

    def __str__(self):
        return repr(self.message)


class AccessStats(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Access Stats.
        """
        self._address = address
        self._port = port

    @property
    def client(self):

        client = make_client(
            accessstats_thrift.AccessStats,
            self._address,
            self._port
        )
        return client

    def _compute_access_lifetime(self, query_result):

        data = []

        for publication_year in query_result['aggregations']['publication_year']['buckets']:
            for access_year in publication_year['access_year']['buckets']:
                data.append([
                    publication_year['key'],
                    access_year['key'],
                    int(access_year['access_html']['value']),
                    int(access_year['access_abstract']['value']),
                    int(access_year['access_pdf']['value']),
                    int(access_year['access_epdf']['value']),
                    int(access_year['access_total']['value'])
                ])

        return sorted(data)

    def access_lifetime(self, issn, collection, raw=False):

        body = {
            "query": {
                "bool": {
                    "must": [{
                            "match": {
                                "collection": collection
                            }
                        },
                        {
                            "match": {
                                "issn": issn
                            }
                        }
                    ]
                }
            },
            "size": 0,
            "aggs": {
                "publication_year": {
                    "terms": {
                        "field": "publication_year",
                        "size": 0,
                        "order": {
                            "access_total": "desc"
                        }
                  },
                  "aggs": {
                        "access_total": {
                            "sum": {
                                "field": "access_total"
                            }
                        },
                        "access_year": {
                            "terms": {
                                "field": "access_year",
                                "size": 0,
                                "order": {
                                    "access_total": "desc"
                                }
                            },
                            "aggs": {
                                "access_total": {
                                    "sum": {
                                        "field": "access_total"
                                    }
                                },
                                "access_abstract": {
                                    "sum": {
                                        "field": "access_abstract"
                                    }
                                },
                                "access_epdf": {
                                    "sum": {
                                        "field": "access_epdf"
                                    }
                                },
                                "access_html": {
                                    "sum": {
                                        "field": "access_html"
                                    }
                                },
                                "access_pdf": {
                                    "sum": {
                                        "field": "access_pdf"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        query_parameters = [
            accessstats_thrift.kwargs('size', '0')
        ]

        query_result = json.loads(self.client.search(json.dumps(body), query_parameters))

        computed = self._compute_access_lifetime(query_result)

        return query_result if raw else computed

    def journal_access_monthnyear(self, issn):

        body = {
            "query": {
                "match": {
                    "issn": issn
                }
            },
            "aggs": {
                "access_year": {
                    "terms": {
                        "field": "access_year",
                        "size": 0
                    },
                    "aggs": {
                        "access_month": {
                            "terms": {
                                "field": "access_month",
                                "size": 0
                            },
                            "aggs": {
                                "access_total": {
                                    "sum": {
                                        "field": "access_total"
                                    }
                                },
                                "access_epdf": {
                                    "sum": {
                                        "field": "access_epdf"
                                    }
                                },
                                "access_pdf": {
                                    "sum": {
                                        "field": "access_pdf"
                                    }
                                },
                                "access_html": {
                                    "sum": {
                                        "field": "access_html"
                                    }
                                },
                                "access_abstract": {
                                    "sum": {
                                        "field": "access_abstract"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        query_parameters = [
            accessstats_thrift.kwargs('size', '1000')
        ]

        query_result = json.loads(self.client.search(json.dumps(body), query_parameters))

        return query_result

    def collection_access_monthnyear(self, collection):

        body = {
            "query": {
                "match": {
                    "collection": collection
                }
            },
            "aggs": {
                "access_year": {
                    "terms": {
                        "field": "access_year",
                        "size": 0
                    },
                    "aggs": {
                        "access_month": {
                            "terms": {
                                "field": "access_month",
                                "size": 0
                            },
                            "aggs": {
                                "access_total": {
                                    "sum": {
                                        "field": "access_total"
                                    }
                                },
                                "access_epdf": {
                                    "sum": {
                                        "field": "access_epdf"
                                    }
                                },
                                "access_pdf": {
                                    "sum": {
                                        "field": "access_pdf"
                                    }
                                },
                                "access_html": {
                                    "sum": {
                                        "field": "access_html"
                                    }
                                },
                                "access_abstract": {
                                    "sum": {
                                        "field": "access_abstract"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        query_parameters = [
            accessstats_thrift.kwargs('size', '1000')
        ]

        query_result = json.loads(self.client.search(json.dumps(body), query_parameters))

        return query_result

    def document_access_monthnyear(self, code):

        body = {
            "query": {
                "match": {
                    "id": code
                }
            },
            "aggs": {
                "access_year": {
                    "terms": {
                        "field": "access_year",
                        "size": 0
                    },
                    "aggs": {
                        "access_month": {
                            "terms": {
                                "field": "access_month",
                                "size": 0
                            },
                            "aggs": {
                                "access_total": {
                                    "sum": {
                                        "field": "access_total"
                                    }
                                },
                                "access_epdf": {
                                    "sum": {
                                        "field": "access_epdf"
                                    }
                                },
                                "access_pdf": {
                                    "sum": {
                                        "field": "access_pdf"
                                    }
                                },
                                "access_html": {
                                    "sum": {
                                        "field": "access_html"
                                    }
                                },
                                "access_abstract": {
                                    "sum": {
                                        "field": "access_abstract"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        query_parameters = [
            accessstats_thrift.kwargs('size', '0')
        ]

        query_result = json.loads(self.client.search(json.dumps(body), query_parameters))

        return query_result


class PublicationStats(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o PublicationStats.
        """
        self._address = address
        self._port = port

    @property
    def client(self):
        client = make_client(
            publication_stats_thrift.PublicationStats,
            self._address,
            self._port
        )

        return client

    def _compute_documents_languages_by_year(self, query_result, years=0):

        year = date.today().year

        years = {str(i): {'pt': 0, 'en': 0, 'es': 0, 'other': 0} for i in range(year, year-years, -1)}

        for item in query_result['aggregations']['publication_year']['buckets']:
            if not item['key'] in years:
                continue

            langs = {'pt': 0, 'en': 0, 'es': 0, 'other': 0}

            for language in item['languages']['buckets']:
                if language['key'] in langs:
                    langs[language['key']] += language['doc_count']
                else:
                    langs['other'] += language['doc_count']

            years[item['key']] = langs

        return years

    def documents_languages_by_year(self, issn, collection, years=0):

        body = {
            "query": {
                "filtered": {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "issn": issn
                                    }
                                },
                                {
                                    "match": {
                                        "collection": collection
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "publication_year": {
                    "terms": {
                        "field": "publication_year",
                        "size": years,
                        "order": {
                            "_term": "desc"
                        }
                    },
                    "aggs": {
                        "languages": {
                            "terms": {
                                "field": "languages",
                                "size": 0
                            }
                        }
                    }
                }
            }
        }

        query_parameters = [
            publication_stats_thrift.kwargs('size', '0')
        ]

        query_result = json.loads(self.client.search('article', json.dumps(body), query_parameters))

        return self._compute_documents_languages_by_year(query_result, years=years)

    def _compute_number_of_articles_by_year(self, query_result, years=0):


        if years == 0:
            return query_result['aggregations']['id']['value']

        year = date.today().year

        years = {str(i): 0 for i in range(year, year-years, -1)}

        for item in query_result['aggregations']['publication_year']['buckets']:
            if not item['key'] in years:
                continue

            years[item['key']] = item.get('doc_count', 0)

        return [(k, v) for k, v in sorted(years.items(), reverse=True)]

    def number_of_articles_by_year(self, issn, collection, document_types=None, years=0):

        body = {
            "query": {
                "filtered": {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "issn": issn
                                    }
                                },
                                {
                                    "match": {
                                        "collection": collection
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "id": {
                    "cardinality": {
                        "field": "id"
                    }
                }
            }
        }

        if document_types:

            body['query']['filtered']['filter'] = {
                "query": {
                    "bool": {
                        "should": []
                    }
                }
            }

            for item in document_types:

                body['query']['filtered']['filter']['query']['bool']['should'].append({
                    "match": {
                        "document_type": item
                    }
                })

        if years != 0:
            body['aggs'] = {
                "publication_year": {
                    "terms": {
                        "field": "publication_year",
                        "size": years,
                        "order": {
                            "_term": 'desc'
                        }
                    },
                    "aggs": {
                        "id": {
                            "cardinality": {
                                "field": "id"
                            }
                        }
                    }
                }
            }

        query_parameters = [
            publication_stats_thrift.kwargs('size', '0')
        ]

        query_result = json.loads(self.client.search('article', json.dumps(body), query_parameters))

        return self._compute_number_of_articles_by_year(query_result, years=years)

    def _compute_number_of_issues_by_year(self, query_result, years=0):

        if years == 0:
            return query_result['aggregations']['issue']['value']

        year = date.today().year

        years = {str(i): 0 for i in range(year, year-years, -1)}

        for item in query_result['aggregations']['publication_year']['buckets']:
            if not item['key'] in years:
                continue
            years[item['key']] = item.get('issue', {}).get('value', 0)

        return [(k, v) for k, v in sorted(years.items(), reverse=True)]

    def number_of_issues_by_year(self, issn, collection, years=0, type=None):
        """
        type: ['regular', 'supplement', 'pressrelease', 'ahead', 'special']
        """

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "issn": issn
                            }
                        },
                        {
                            "match": {
                                "collection": collection
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "issue": {
                    "cardinality": {
                        "field": "issue"
                    }
                }
            }

        }

        if type:
            body['query']['bool']['must'].append({"match": {"issue_type": type}})

        if years != 0:
            body['aggs'] = {
                "publication_year": {
                    "terms": {
                        "field": "publication_year",
                        "size": years,
                        "order": {
                            "_term": 'desc'
                        }
                    },
                    "aggs": {
                        "issue": {
                            "cardinality": {
                                "field": "issue"
                            }
                        }
                    }
                }
            }

        query_parameters = [
            publication_stats_thrift.kwargs('size', '0')
        ]

        query_result = json.loads(self.client.search(
            'article', json.dumps(body), query_parameters))

        return self._compute_number_of_issues_by_year(
            query_result, years=years)

    def _compute_first_included_document_by_journal(self, query_result):

        if len(query_result.get('hits', {'hits': []}).get('hits', [])) == 0:
            return None

        return query_result['hits']['hits'][0].get('_source', None)

    def first_included_document_by_journal(self, issn, collection):

        body = {
            "query": {
                "filtered": {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "collection": collection
                                    }
                                },
                                {
                                    "match": {
                                        "issn": issn
                                    }
                                },
                                {
                                    "match": {
                                        "issue_type": "regular"
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "sort": [
                {
                    "publication_date": {
                        "order": "asc"
                    }
                }
            ]
        }

        query_parameters = [
            publication_stats_thrift.kwargs('size', '1')
        ]

        query_result = json.loads(self.client.search('article', json.dumps(body), query_parameters))

        return self._compute_first_included_document_by_journal(query_result)

    def _compute_last_included_document_by_journal(self, query_result):

        if len(query_result.get('hits', {'hits': []}).get('hits', [])) == 0:
            return None

        return query_result['hits']['hits'][0].get('_source', None)

    def last_included_document_by_journal(self, issn, collection, metaonly=False):

        body = {
            "query": {
                "filtered": {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "collection": collection
                                    }
                                },
                                {
                                    "match": {
                                        "issn": issn
                                    }
                                },
                                {
                                    "match": {
                                        "issue_type": "regular"
                                    }
                                }
                            ]
                        }
                    },
                    "filter": {
                        "exists": {
                            "field": "publication_date"
                        }
                    }
                }
            },
            "sort": [
                {
                    "publication_date": {
                        "order": "desc"
                    }
                }
            ]
        }

        query_parameters = [
            publication_stats_thrift.kwargs('size', '1')
        ]

        query_result = json.loads(self.client.search('article', json.dumps(body), query_parameters))

        return self._compute_last_included_document_by_journal(query_result)


class Citedby(CitedByThriftClient):

    def publication_and_citing_years(self, issn, titles, py_range=None):

        body = {"query": {"filtered": {}}}

        fltr = {
            "filter": {
                "bool": {
                    "must": []

                }
            }
        }

        if py_range:
            fltr["filter"]["bool"]['must'].append(
                {
                    "range": {
                        "publication_year": {
                            "gte": py_range[0],
                            "lte": py_range[1]
                        }
                    }
                }
            )

        query = {
            "query": {
                "bool": {
                    "should": [],
                    "must_not": []
                }
            }
        }

        aggs = {
            "aggs": {
                "publication_year": {
                    "terms": {
                        "field": "publication_year",
                        "size": 0
                    },
                    "aggs": {
                        "reference_publication_year": {
                            "terms": {
                                "field": "reference_publication_year",
                                "size": 0,
                                "order": {
                                    "_term": "desc"
                                }
                            }
                        }
                    }
                }
            }
        }

        for item in self._fuzzy_custom_query(issn, titles):
            query['query']['bool']['should'].append(item)

        for item in self._must_not_custom_query(issn):
            query['query']['bool']['must_not'].append(item)

        body['query']['filtered'].update(fltr)
        body['query']['filtered'].update(query)
        body.update(aggs)

        query_parameters = [
            self.CITEDBY_THRIFT.kwargs('size', '0'),
            self.CITEDBY_THRIFT.kwargs('search_type', 'count')
        ]

        query_result = json.loads(self.client.search(json.dumps(body), query_parameters))

        return query_result

    def has_optmized_journal_queries(self, issn):

        if journal_titles.load(issn):
            return True

        return False

    @staticmethod
    def _must_not_custom_query(issn):
        """
            Este metodo constroi a lista de filtros por título de periódico que
            será aplicada na pesquisa boleana como restrição "must_not".
            A lista de filtros é coletada do template de pesquisa customizada
            do periódico, quanto este template existir.
        """

        custom_queries = set([utils.cleanup_string(i) for i in journal_titles.load(issn).get('must_not', [])])

        for item in custom_queries:

            query = {
                "match": {
                    "reference_source_cleaned": item
                }
            }

            yield query

    @staticmethod
    def _fuzzy_custom_query(issn, titles):
        """
            Este metodo constroi a lista de filtros por título de periódico que
            será aplicada na pesquisa boleana como match por similaridade "should".
            A lista de filtros é coletada do template de pesquisa customizada
            do periódico, quanto este template existir.
        """
        custom_queries = journal_titles.load(issn).get('should', [])
        titles = [{'title': i} for i in titles if i not in [x['title'] for x in custom_queries]]
        titles.extend(custom_queries)

        for item in titles:

            if len(item['title'].strip()) == 0:
                continue

            query = {
                "fuzzy": {
                    "reference_source_cleaned": {
                        "value": utils.cleanup_string(item['title']),
                        "fuzziness": item.get('fuzziness', 3),
                        "max_expansions": 50
                    }
                }
            }

            yield query


class Ratchet(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Ratchet.
        """
        self._address = address
        self._port = port

    @property
    def client(self):
        client = make_client(
            ratchet_thrift.RatchetStats,
            self._address,
            self._port
        )

        return client

    def document(self, code):

        data = self.client.general(code=code)

        return data


class ArticleMeta(ArticleMetaThriftClient):
    pass
