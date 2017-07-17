# coding: utf-8
"""
Este processamento realiza a geração de chaves naturais dos artigos para fins de
de teste de exportação dos XML para o SciELO Manager.

Formato de saída:
"pid","issn scielo","volume","número","first page","last page","e-location"
"""

import os
import argparse
import logging
import codecs
import json

from io import StringIO

from legendarium.urlegendarium import URLegendarium
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

    def __init__(self, collection, issns=None, output_file=None):

        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns or [None]
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file

    def write(self, line):
        if not self.output_file:
            print(line.encode('utf-8'))
        else:
            self.output_file.write('%s\r\n' % line)

    def fmt_json(self, data):

        item = {
            'collection_acronym': data.collection_acronym,
            'publisher_id': data.publisher_id,
            'journal_title': data.journal.title,
            'journal_acronym': data.journal.acronym,
            'volume': data.issue.volume,
            'number': data.issue.number,
            'supplement': (data.issue.supplement_volume or '') + (data.issue.supplement_number or ''),
            'publication_year': data.publication_date[:4],
            'first_page': data.start_page or '',
            'first_page_seq': data.start_page_sequence or '',
            'last_page': data.end_page or '',
            'elocation': data.elocation or ''
        }

        # legendarium natural_url
        natural_url = str(URLegendarium(
            item['journal_acronym'],
            item['publication_year'],
            item['volume'],
            item['number'],
            item['first_page'],
            item['last_page'],
            item['elocation'],
            item['supplement']
        ))

        natural_key = self.build_key([
            item['journal_acronym'],
            item['volume'],
            item['number'],
            item['supplement'],
            item['publication_year'],
            item['first_page'],
            item['last_page'],
            item['elocation'],
            ])

        item['natural_key'] = natural_key
        item['natural_url'] = natural_url

        return json.dumps(item)

    def fmt_csv(self, data):

        line = [
            data.collection_acronym,
            data.publisher_id,
            data.journal.title,
            data.journal.acronym,
            data.issue.volume,
            data.issue.number,
            (data.issue.supplement_volume or '') + (data.issue.supplement_number or ''),
            data.publication_date[:4],
            data.start_page or '',
            data.start_page_sequence or '',
            data.end_page or '',
            data.elocation or ''
        ]

        # legendarium natural_url
        natural_url = str(URLegendarium(
            data.journal.acronym,
            data.publication_date[:4],
            data.issue.volume,
            data.issue.number,
            data.start_page or '',
            data.end_page or '',
            data.elocation or '',
            (data.issue.supplement_volume or '') + (data.issue.supplement_number or ''),
        ))

        natural_key = self.build_key(line[3:])

        line.append(natural_key)
        line.append(natural_url)

        joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])

        return joined_line

    def build_key(self, data):

        values = (i for i in data)
        text_values = (value if value else 'none' for value in values)
        joined_values = '_'.join(text_values)

        return utils.slugify(joined_values)

    def run(self, output_fmt='json'):

        if output_fmt == 'csv':
            header = [
                u"coleção",
                u"pid",
                u"título",
                "acrônimo do título",
                u"volume",
                u"número",
                u"suplemento",
                u"ano de publicação",
                u"primeira página",
                u"primeria página seq"
                u"última página",
                u"e-location",
                u"chave natural",
                u"url natural"
            ]
            self.write(
                u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header])
            )

        for issn in self.issns:
            for document in self._articlemeta.documents(
                collection=self.collection, issn=issn
            ):

                logger.debug('Reading document: %s' % document.publisher_id)

                if output_fmt == 'csv':
                    output_fmt = self.fmt_csv
                else:
                    output_fmt = self.fmt_json

                self.write(output_fmt(document))


def main():

    parser = argparse.ArgumentParser(
        description='Dump languages distribution by article'
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
        '--format',
        '-f',
        choices=['json', 'csv'],
        default='json',
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

    dumper.run(args.format)