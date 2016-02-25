# coding: utf-8
"""
Este processamento utiliza a API do DOAJ para listar o status dos periódicos
nesta fonte de informação.
"""
import os
import argparse
import logging
import codecs
import json
import time
from io import BytesIO, StringIO
from datetime import datetime, timedelta

import requests
from lxml import etree

from doaj.journals import Journals

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


def request_api(url, timeout=3, attempts=10):

    attempt = 0
    while True:
        result = None
        if attempt == attempts:
            return None
        try:
            result = requests.get(url, timeout=3)
        except:
            logger.error("Fail to retrieve data from (%s) attempt %d/%d" % (url, attempt, attempts))
            time.sleep(1)

        if result and result.status_code == 200:
            return result

        attempt += 1


class Dumper(object):

    def __init__(self, collection, issns=None, output_file=None):

        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.doaj_journals = Journals()
        self.issns = issns
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        header = [u"coleção",u"issn scielo",u"issn impresso",u"issn eletrônico",u"título",u"ID no DOAJ",u"Provider no DOAJ",u"Status no DOAJ"]
        self.write(','.join(header))

    def get_doaj_journal(self, issns):
        data = {}
        journal = None

        for issn in issns:
            journal = request_api('https://doaj.org/api/v1/search/journals/issn:%s' % issn).json()
            if journal:
                break

        if not journal:
            logger.debug("No data available in DOAJ for %s" % str(issns))
            return data

        if not len(journal['results']) > 0:
            logger.debug("No data available in DOAJ for %s" % str(issns))
            return data

        active = journal['results'][0]['bibjson'].get('active', None)

        data['id'] = journal['results'][0]['id']
        data['provider'] = journal['results'][0]['bibjson'].get('provider', 'undefined')
        data['active'] = 'undefined' if active == None else str(active)
        data['active'] = 'reapplication' if data['active'] == 'False' else data['active']
        data['active'] = 'active' if data['active'] == 'True' else data['active']

        return data

    def write(self, line):
        if not self.output_file:
            print(line.encode('utf-8'))
        else:
            self.output_file.write('%s\r\n' % line)

    def run(self):
        for item in self.items():
            self.write(item)

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.journals(collection=self.collection, issn=issn):
                jissns = set()
                if data.print_issn:
                    jissns.add(data.print_issn)
                if data.electronic_issn:
                    jissns.add(data.print_issn)
                jissns.add(data.scielo_issn)
                in_doaj = self.get_doaj_journal(list(jissns))
                yield self.fmt_csv(data, in_doaj)
        
    def fmt_csv(self, data, in_doaj):

        line = [
            data.collection_acronym,
            data.scielo_issn,
            data.print_issn or "",
            data.electronic_issn or "",
            data.title,
            in_doaj.get('id', ""),
            in_doaj.get('provider', ""),
            in_doaj.get('active', "")
        ]

        joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])

        return joined_line

def main():

    parser = argparse.ArgumentParser(
        description='Retrieve the SciELO journals status in DOAJ'
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
        '--output_file',
        '-r',
        help='File to receive the dumped data'
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

    dumper = Dumper(args.collection, issns, args.output_file)

    dumper.run()
