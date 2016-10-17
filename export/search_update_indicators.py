# coding: utf-8
"""
Este processamento realiza a exportação/atualização de número de citações e
acessos no índice da ferramenta de busca search.scielo.org
"""
import argparse
import logging
import json

import requests

from clients.search import Search
import utils

logger = logging.getLogger(__name__)


def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.setLevel(allowed_levels.get(logging_level, 'INFO'))

    if logging_file:
        hl = logging.FileHandler(logging_file, mode='a')
    else:
        hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    logger.addHandler(hl)

    return logger


class Dumper(object):

    def __init__(self, collection, issns=None, citations_mode='pid'):

        self._articlemeta = utils.articlemeta_server()
        self._accessstats = utils.accessstats_server()
        self._cited_by = utils.citedby_server()
        self._search = Search()
        self._load_citations = self._load_citations_by_meta if citations_mode == 'meta' else self._load_citations_by_pid
        self.collection = collection
        self.issns = issns or [None]

    def _load_citations_by_pid(self, item):

        attempt = 0
        response = self._cited_by.citedby_pid(item.publisher_id)

        try:
            total = json.loads(response)['article']['total_received']
        except:
            total = None

        return total

    def _load_citations_by_meta(self, item):

        title = item.original_title() if item.original_title() else None
        year = item.publication_date[0:4] if item.publication_date else None
        surname = item.authors[0].get('surname', None) if item.authors else None

        if title and surname and year:
            response = self._cited_by.citedby_meta(title, surname, int(year))

        try:
            total = json.loads(response)['article']['total_received']
        except:
            total = None

        return total

    def _load_accesses(self, item):

        response = self._accessstats.client.document(
            item.publisher_id, item.collection_acronym)

        try:
            total = int(json.loads(response)['access_total']['value'])
        except:
            total = 0

        return total

    def run(self):
        logger.info('Export started')

        for item in self.items():
            citations = self._load_citations(item)
            accesses = self._load_accesses(item)

            item_id = '-'.join([item.publisher_id, item.collection_acronym])
            self._search.update_document_indicators(
                item_id, citations, accesses)

        self._search.deploy()

        logger.info('Export finished')

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.documents(
                    collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                yield data


def main():

    parser = argparse.ArgumentParser(
        description='Update the citing numbers of each documents in search.scielo.org'
    )

    parser.add_argument(
        'issns',
        nargs='*',
        help='ISSN\'s separated by spaces'
    )

    parser.add_argument(
        '--collection',
        '-c',
        help='Collection Acronym'
    )

    parser.add_argument(
        '--citations_mode',
        '-m',
        default='pid',
        choices=['meta', 'pid'],
        help='Mode to retrieve received citations.'
    )

    parser.add_argument(
        '--logging_file',
        '-o',
        help='Full path to the log file'
    )

    parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()
    _config_logging(args.logging_level, args.logging_file)
    logger.info('Dumping data for: %s' % args.collection)

    issns = None
    if len(args.issns) > 0:
        issns = utils.ckeck_given_issns(args.issns)

    dumper = Dumper(args.collection, issns, args.citations_mode)

    dumper.run()
