# coding: utf-8
import os
import thriftpy
import json
import logging

from thriftpy.rpc import make_client
from xylose.scielodocument import Article

LIMIT = 1000

logger = logging.getLogger(__name__)

ratchet_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/ratchet.thrift')

articlemeta_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/articlemeta.thrift')

class Ratchet(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Ratchet.
        """
        self._client = make_client(
            ratchet_thrift.RatchetStats,
            address,
            port
        )

    def client(self):
        return self._client

    def document(self, code):

        data = self._client.general(code=code)

        return data


class ArticleMeta(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Articlemeta.
        """
        self._client = make_client(
            articlemeta_thrift.ArticleMeta,
            address,
            port
        )

    def client(self):
        return self._client

    def documents(self, collection, issns=None):

        offset = 0
        while True:
            identifiers = self._client.get_article_identifiers(collection=collection, limit=LIMIT, offset=offset)
            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:
                if issns and not identifier.code[1:10] in issns:
                    continue
                article = self._client.get_article(
                    code=identifier.code, collection=identifier.collection)

                jarticle = json.loads(article)

                xarticle = Article(jarticle)

                logger.info('Document loaded: %s_%s' % ( identifier.collection, identifier.code))

                yield xarticle

            offset += 1000

    def collections(self):
        
        return [i for i in self._client.get_collection_identifiers()]