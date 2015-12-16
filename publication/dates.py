# coding: utf-8
"""
Este processamento gera uma tabulação de datas do artigo (publicação, submissão,
    aceite, entrada no scieloe atualização no scielo)
Formato de saída:
"PID","ISSN","título","área temática","ano de publicação","tipo de documento","submissão","recebido","revisado","aceito","publicado","entrada no SciELO","Atualização no SciELO"
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
        header = [u"PID",u"ISSN",u"título",u"área temática",u"ano de publicação",u"tipo de documento",u"submissão","recebido","revisado","aceito","publicado",u"entrada no SciELO",u"atualização no SciELO"]
        self.write(','.join(header))

    def write(self, line):
        if not self.output_file:
            print(line)
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
            for data in self._articlemeta.documents(collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                yield self.fmt_csv(data)
        
    def fmt_csv(self, data):
        line = []
        line.append(data.publisher_id)
        line.append(data.journal.scielo_issn)
        line.append(data.journal.title)
        line.append(','.join(data.journal.subject_areas))
        line.append(data.publication_date[0:4])
        line.append(data.receive_date or '')
        line.append(data.review_date or '')
        line.append(data.review_date or '')
        line.append(data.acceptance_date or '')
        line.append(data.publication_date or '')
        line.append(data.creation_date or '')
        line.append(data.update_date or '')

        joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])

        return joined_line

def main():

    parser = argparse.ArgumentParser(
        description='Dump article dates'
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
