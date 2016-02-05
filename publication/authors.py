# coding: utf-8
"""
Este processamento gera uma tabulação de autores e afiliação de cada artigo da
coleção SciELO.
Formato de saída:
"PID","issn","título","área temática","ano de publicação","tipo de documento","author","instituição","paises de afiliação","estado de afiliação","cidade de afiliação"
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
        self.write(','.join([u"PID",u"ISSN",u"título",u"área temática",u"ano de publicação",u"tipo de documento",u"author",u"instituição",u"paises de afiliação",u"estado de afiliação",u"cidade de afiliação"]))

    def write(self, lines):

        if isinstance(lines, unicode):
            lines = [lines]

        for line in lines:
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
            for data in self._articlemeta.documents(collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                for item in self.fmt_csv(data):
                    yield item

    def join_line(self, line):

        return ','.join(['"%s"' % i.replace('"', '""') for i in line])

    def fmt_csv(self, data):
        countries = set()

        affs = {item['index'].upper():item for item in data.mixed_affiliations}

        line = [
            data.publisher_id,
            data.journal.scielo_issn,
            data.journal.title,
            ','.join(data.journal.subject_areas),
            data.publication_date[0:4],
            data.document_type
        ]
        if data.authors:
            for author in data.authors:
                author_line = [' '.join([author.get('given_names', ''), author.get('surname', '')])]
                if 'xref' in author:
                    for index in author['xref']:
                        index = index.upper()
                        aff_line = []
                        aff_line.append(affs.get(index, {}).get('institution', '')),
                        aff_line.append(affs.get(index, {}).get('country', '')),
                        aff_line.append(affs.get(index, {}).get('state', '')),
                        aff_line.append(affs.get(index, {}).get('city', ''))
                        yield self.join_line(line+author_line+aff_line)
                else:
                    yield self.join_line(line+author_line)
        else:
            yield self.join_line(line)

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
