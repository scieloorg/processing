# coding: utf-8
"""
Este processamento gera uma tabulação de país de afiliação de cada artigo da
coleção SciELO.
Formato de saída:
"PID","issn","título","ano de publicação","tipo de documento","paises de afiliação","exclusivo nacional","exclusivo estrangeiro","nacional + estrangeiro"
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


class Dumper(object):

    def __init__(self, collection, issns=None, output_file=None):

        self._ratchet = utils.ratchet_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.output_file = output_file

    def run(self):

        header = u'PID,ISSN,título,ano de publicação,tipo de documento,paises de afiliação,exclusivo nacional,exclusivo estrangeiro,nacional + estrangeiro'

        if not self.issns:
            self.issns = [None]

        if not self.output_file:
            print(header)
            for issn in self.issns:
                for data in self.get_data(issn=issn):
                    print(self.fmt_csv(data))
            exit()

        with codecs.open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(u'%s\r\n' % header)
            for issn in self.issns:
                for data in self.get_data(issn=issn):
                    f.write(u'%s\r\n' % self.fmt_csv(data))
        
    def fmt_csv(self, data):
        countries = set()

        if data.normalized_affiliations:
            countries = set([i['country'].lower() for i in data.normalized_affiliations if 'country' in i and i['country'] != 'undefined'])

        line = [
            data.publisher_id,
            data.journal.scielo_issn,
            data.journal.title,
            data.publication_date[0:4],
            data.document_type,
            ', '.join(countries),
            'X' if 'brazil' in countries and len(countries) == 1 else '',
            'X' if not 'brazil' in countries and len(countries) > 0 else '',
            'X' if 'brazil' in countries and len(countries) > 1 else '',
        ]

        return ','.join(['"%s"' % i for i in line])

    def get_data(self, issn):
        for document in self._articlemeta.documents(collection=self.collection, issn=issn):

            yield document


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
