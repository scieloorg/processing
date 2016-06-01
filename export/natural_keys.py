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

import packtools
from packtools.catalogs import XML_CATALOG

import utils

os.environ['XML_CATALOG_FILES'] = XML_CATALOG
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
        header = [u"coleção", u"pid", u"título", u"volume", u"número", u"ano de publicação", u"primeira página", u"primeria página seq" u"última página", u"e-location", u"ahead of print id", u"chave"]

        self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

    def write(self, line):
        if not self.output_file:
            print(line.encode('utf-8'))
        else:
            self.output_file.write('%s\r\n' % line)

    def fmt_json(self, data, xml_etree):

        parsed_xml = xml_etree.lxml

        def get_value(expression):
            try:
                first_occ = parsed_xml.xpath(expression)[0]
            except IndexError:
                return None

            try:
                value = first_occ.text
            except AttributeError:
                # valor de atributo
                value = first_occ

            try:
                return value.strip()
            except AttributeError:
                return value

        line = []

        journal_title = get_value('/article/front/journal-meta/journal-title-group/journal-title')
        volume = get_value('/article/front/article-meta/volume')
        issue = get_value('/article/front/article-meta/issue')
        year = get_value('/article/front/article-meta/pub-date/year')
        fpage = get_value('/article/front/article-meta/fpage')
        fpage_seq = get_value('/article/article/front/article-meta/fpage/@seq')
        lpage = get_value('/article/front/article-meta/lpage')
        elocation = get_value('/article/front/article-meta/elocation')
        aop_id = get_value('/article/front/article-meta/article-id[@pub-id-type="other"]')

        line = [
            data.collection_acronym,
            data.publisher_id,
            journal_title if journal_title else '',
            volume if volume else '',
            issue if issue else '',
            year if year else '',
            fpage if fpage else '',
            fpage_seq if fpage_seq else '',
            lpage if lpage else '',
            elocation if elocation else '',
            aop_id if aop_id else ''
        ]

        natural_key = self.build_key(line[2:])

        line.append(natural_key)

        joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])

        return joined_line

    def parse(self, xml):
        f = StringIO(xml)
        try:
            tree = packtools.XMLValidator(f)
        except Exception as e:
            logger.exception(e)
            logger.error('Fail to parse XML')
            tree = None

        return tree

    def build_key(self, data):

        values = (i for i in data)
        text_values = (value if value else 'none' for value in values)
        joined_values = '_'.join(text_values)

        return utils.call_django_slugify(joined_values)

    def run(self):
        for issn in self.issns:
            for document in self._articlemeta.documents(
                    collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % document.publisher_id)

                try:
                    xml = self._articlemeta.document(
                        document.publisher_id, document.collection_acronym,
                        fmt='xmlrsps')
                except Exception as e:
                    logger.exception(e)
                    logger.error('Fail to read document: %s_%s' % (
                        document.publisher_id, document.collection_acronym))
                    xml = u''

                et = self.parse(xml)

                if not et:
                    logger.error('Fail to parse xml document: %s_%s' % (
                        document.publisher_id, document.collection_acronym))
                    continue

                self.write(self.fmt_json(document, et))


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