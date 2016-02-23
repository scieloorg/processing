# coding: utf-8
"""
Este processamento realiza a exportação/atualização de número de citações
recebidas no índice da ferramenta de busca search.scielo.org
"""
import argparse
import logging
import json

import requests

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

    def __init__(self, collection, issns=None):

        self._articlemeta = utils.articlemeta_server()
        self._accessstats = utils.accessstats_server()
        self._cited_by = utils.citedby_server()
        self._solr_search_scielo_org = utils.settings.get('app:main', {}).get(
            'solr_search_scielo_org', 'localhost:8080')
        self.collection = collection
        self.issns = issns or [None]

    def _commit(self):
        url_commit = 'http://%s/solr/scielo-articles/update?commit=true' % self._solr_search_scielo_org
        url_optimize = 'http://%s/solr/scielo-articles/update?optimize=true' % self._solr_search_scielo_org

        requests.get(url_commit)
        requests.get(url_optimize)

    def _update_document_citations(self, doc_id, citations, accesses):
        headers = {'content-type': 'application/json'}

        data = {
            "add": {
                "doc": {
                    "id": doc_id
                }
            }
        }

        if citations:
            data['add']['doc']['total_received'] = {'set': str(citations)}

        if accesses:
            data['add']['doc']['total_access'] = {'set': str(accesses)}

        url = 'http://%s/solr/scielo-articles/update?wt=json' % self._solr_search_scielo_org

        response = requests.get(url, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            return response.json()

    def _load_citations(self, item):

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
        import pdb; pdb.set_trace()
        for item in self.items():
            citations = self._load_citations(item)
            item_id = '-'.join([item.publisher_id, item.collection_acronym])

            accesses = self._load_accesses(item)

            self._update_document_citations(item_id, citations, accesses)

        self._commit()

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

    dumper = Dumper(args.collection, issns)

    dumper.run()
