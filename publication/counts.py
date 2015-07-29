# coding: utf-8
"""
Este processamento gera uma tabulação com contagens, soma, mediana de alguns
elementos do artigo: total de autores, total de citações, total de páginas

Formato de saída:
"PID","issn","título","área temática","ano de publicação","tipo de documento","total autores","0 autores", "1 autor","2 autores","3 autores","4 autores","5 autores","+6 autores","total páginas","total citações"
"""

import argparse
import logging
import codecs

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


def pages(first, last):

    try:
        pages = int(last)-int(first)
    except:
        pages = 0

    if pages >= 0:
        return pages
    else:
        return 0

class Dumper(object):

    def __init__(self, collection, issns=None, output_file=None):

        self._ratchet = utils.ratchet_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        header = [u"PID",u"issn",u"título",u"área temática",u"ano de publicação",u"tipo de documento",u"total autores",u"0 autores",u"1 autor",u"2 autores",u"3 autores",u"4 autores",u"5 autores",u"+6 autores",u"total páginas",u"total referências"]
        self.write(','.join(header))

    def write(self, line):
        if not self.output_file:
            print('%s\r\n' % line)
        else:
            self.output_file.write('%s\r\n' % line)

    def run(self):
        for item in self.items():
            self.write(item)

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.documents(collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                yield self.fmt_csv(data)
        
    def fmt_csv(self, data):
        countries = set()

        if data.normalized_affiliations:
            countries = set([i['country'].lower() for i in data.normalized_affiliations if 'country' in i and i['country'] != 'undefined'])

        tot_authors = len(data.authors or [])

        line = [
            data.publisher_id,
            data.journal.scielo_issn,
            data.journal.title,
            ','.join(data.journal.subject_areas),
            data.publication_date[0:4],
            data.document_type,
            str(tot_authors), # total de autores
            '1' if tot_authors == 0 else '0', # total de autores
            '1' if tot_authors == 1 else '0', # total de autores
            '1' if tot_authors == 2 else '0', # total de autores
            '1' if tot_authors == 3 else '0', # total de autores
            '1' if tot_authors == 4 else '0', # total de autores
            '1' if tot_authors == 5 else '0', # total de autores
            '1' if tot_authors >= 6 else '0', # total de autores
            str(pages(data.start_page, data.end_page)), # total de páginas
            str(len(data.citations or [])) # total de citações
        ]

        joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])

        return joined_line

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
