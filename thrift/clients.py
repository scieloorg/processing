# coding: utf-8
import os
import thriftpy
import json
import logging

from thriftpy.rpc import make_client
from xylose.scielodocument import Article, Journal

LIMIT = 1000

logger = logging.getLogger(__name__)

ratchet_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/ratchet.thrift')

articlemeta_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/articlemeta.thrift')


citedby_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/citedby.thrift')

publication_stats_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/publication_stats.thrift')

class ServerError(Exception):
    def __init__(self, message=None):
        self.message = message or 'thirftclient: ServerError'
    
    def __str__(self):
        return repr(self.message)


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
                                }
                            ]
                        }
                    },
                    "filter": {
                        "exists": {
                            "field": "processing_date"
                        }
                    }
                }
            },
            "sort": [
                {
                    "processing_date": {
                        "order": "asc"
                    }
                }
            ]
        }

        query_parameters = [
            publication_stats_thrift.kwargs('size', '1')
        ]

        query_result = json.loads(self.client.search('article', json.dumps(body), query_parameters))

        return query_result


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
                                }
                            ]
                        }
                    },
                    "filter": {
                        "exists": {
                            "field": "processing_date"
                        }
                    }
                }
            },
            "sort": [
                {
                    "processing_date": {
                        "order": "desc"
                    }
                }
            ]
        }

        query_parameters = [
            publication_stats_thrift.kwargs('size', '1')
        ]

        query_result = json.loads(self.client.search('article', json.dumps(body), query_parameters))

        return query_result

class Citedby(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Citedby.
        """
        self._address = address
        self._port = port

    @property
    def client(self):
        client = make_client(
            citedby_thrift.Citedby,
            self._address,
            self._port
        )

        return client

    def citedby_pid(self, code, metaonly=False):

        data = self.client.citedby_pid(code, metaonly)

        return data


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


class ArticleMeta(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Articlemeta.
        """
        self._address = address
        self._port = port

    @property
    def client(self):

        client = make_client(
            articlemeta_thrift.ArticleMeta,
            self._address,
            self._port
        )
        return client


    def journals(self, collection=None, issn=None):
        offset = 0
        while True:
            identifiers = self.client.get_journal_identifiers(collection=collection, issn=issn, limit=LIMIT, offset=offset)
            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                journal = self.client.get_journal(
                    code=identifier.code[0], collection=identifier.collection)

                jjournal = json.loads(journal)

                xjournal = Journal(jjournal)

                logger.info('Journal loaded: %s_%s' % ( identifier.collection, identifier.code))

                yield xjournal

            offset += 1000

    def exists_article(self, code, collection):
        try:
            return self.client.exists_article(
                code,
                collection
            )
        except:
            msg = 'Error checking if document exists: %s_%s' % (collection, code)
            raise ServerError(msg)

    def set_doaj_id(self, code, collection, doaj_id):
        try:
            article = self.client.set_doaj_id(
                code,
                collection,
                doaj_id
            )
        except:
            msg = 'Error senting doaj id for document: %s_%s' % (collection, code)
            raise ServerError(msg)


    def document(self, code, collection, replace_journal_metadata=True, fmt='xylose'):
        try:
            article = self.client.get_article(
                code=code,
                collection=collection,
                replace_journal_metadata=True, 
                fmt=fmt
            )
        except:
            msg = 'Error retrieving document: %s_%s' % (collection, code)
            raise ServerError(msg)

        if fmt == 'xylose':
            jarticle = json.loads(article)
            xarticle = Article(jarticle)
            logger.info('Document loaded: %s_%s' % ( collection, code))
            return xarticle
        else:
            logger.info('Document loaded: %s_%s' % ( collection, code))
            return article


    def documents(self, collection=None, issn=None, from_date=None,
        until_date=None, fmt='xylose'):
        offset = 0
        while True:
            identifiers = self.client.get_article_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                document = self.document(
                    code=identifier.code,
                    collection=identifier.collection,
                    replace_journal_metadata=True, 
                    fmt=fmt
                )

                yield document

            offset += 1000

    def collections(self):
        
        return [i for i in self._client.get_collection_identifiers()]