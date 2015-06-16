# coding: utf-8
"""
Este processamento gera uma tabulação com contagens, soma, mediana de alguns
elementos do artigo: total de autores, total de citações, total de páginas

Formato de saída:
"issn scielo","issn impresso","issn eletrônico","título","área temática","bases WOS","áreas WOS","status","ano de inclusão","licença de uso padrão"
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

        header = u'"issn scielo","issn impresso","issn eletrônico","nome do publicador","título","título abreviado","título nlm","área temática","bases WOS","áreas temáticas WOS","situação atual","ano de inclusão","licença de uso padrão"'

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

        line = [
            data.scielo_issn,
            data.print_issn or "",
            data.electronic_issn or "",
            data.publisher_name or "",
            data.title,
            data.abbreviated_title or "",
            data.title_nlm or "",
            ','.join(data.subject_areas or []),
            ','.join(data.wos_citation_indexes or []),
            ','.join(data.wos_subject_areas or []),
            data.current_status,
            data.creation_date[:4],
        ]

        if data.permissions:
            line.append(data.permissions.get('id', "") or "")
        else:
            line.append("")

        return ','.join(['"%s"' % i for i in line])

    def get_data(self, issn):
        for document in self._articlemeta.journals(collection=self.collection, issn=issn):

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
