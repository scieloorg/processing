# coding: utf-8
"""
Este processamento gera uma tabulação de periódicos seguindo o formato Kbart.

Formato de saída:
"Título do Periódico","ISSN impresso","ISSN online","Data do primeiro número","volume","número","Data do último número publicado","volume","número","url issues","ID SciELO"
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
        self._publicationstats = utils.publicationstats_server()
        self.collection = collection
        self.issns = issns
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        header = [u"Título do Periódico",u"ISSN impresso",u"ISSN online",u"Data do primeiro número",u"volume",u"número",u"Data do último número publicado",u"volume",u"número",u"url issues",u"ID SciELO"]
        self.write(','.join(header))


    def _first_included_document_by_journal(self, issn, collection):

        fid = self._publicationstats.first_included_document_by_journal(issn, collection)

        if not fid:
            return None

        document = self._articlemeta.document(fid['pid'], fid['collection'])

        return document

    def _last_included_document_by_journal(self, issn, collection):

        lid = self._publicationstats.last_included_document_by_journal(issn, collection)

        if not lid:
            return None

        document = self._articlemeta.document(lid['pid'], lid['collection'])

        return document

    def write(self, line):
        if not self.output_file:
            print(line)
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
                logger.debug('Reading document: %s' % data.scielo_issn)
                yield self.fmt_csv(data)
        
    def fmt_csv(self, data):
        line = []

        first_document = self._first_included_document_by_journal(data.scielo_issn, data.collection_acronym)
        last_document = self._last_included_document_by_journal(data.scielo_issn, data.collection_acronym)
        line.append(data.title)
        line.append(data.print_issn or '')
        line.append(data.electronic_issn or '')
        line.append(first_document.publication_date or '' if first_document else '')
        line.append(first_document.volume or '' if first_document else '')
        line.append(first_document.issue or '' if first_document else '')
        line.append(last_document.publication_date or '' if last_document else '')
        line.append(last_document.volume or '' if last_document else '')
        line.append(last_document.issue or '' if last_document else '')
        line.append(data.url().replace('sci_serial', 'sci_issues'))
        line.append(data.scielo_issn or '')

        joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])

        return joined_line

def main():

    parser = argparse.ArgumentParser(
        description='Export journals list in Kabart format'
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
