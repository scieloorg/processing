# coding: utf-8
"""
Este processamento gera uma tabulação de histórico de mudanças do status do 
periódico na coleção SciELO

Formato de saída:
"issn scielo","issn impresso","issn eletrônico","título","área temática","bases WOS","áreas WOS","status","ano de inclusão","licença de uso padrão","Histórico Ano","Histórico Status"
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
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        header = [u"issn scielo", u"issn impresso", u"issn eletrônico", u"nome do publicador", u"título", u"título abreviado", u"título nlm", u"área temática", u"bases WOS", u"áreas temáticas WOS", u"situação atual", u"ano de inclusão", u"licença de uso padrão", u"histórico data", u"histórico ano", u"histórico status", u"histório motivo"]
        self.write(','.join(header))

    def write(self, line):
        if not self.output_file:
            print(line.encode('utf-8'))
        else:
            self.output_file.write('%s\r\n' % line)

    def run(self):
        for item in self.items():
            self.write(item)
        logger.info('Export finished')

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.journals(collection=self.collection, issn=issn):
                for history in data.status_history:
                    yield self.fmt_csv(data, history)

    def fmt_csv(self, data, history):

        hist, status, reason = history

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
            data.creation_date[:4]
        ]

        if data.permissions:
            line.append(data.permissions.get('id', "") or "")
        else:
            line.append("")

        line += [
            hist,
            hist[0:4],
            status,
            reason
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
