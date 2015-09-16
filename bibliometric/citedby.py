# coding: utf-8
"""
Este processamento gera uma tabulação de idiomas de publicação de cada artigo
da coleção SciELO.
Formato de saída:
"PID","ISSN","título","área temática","ano de publicação","tipo de documento","título do documento","citado por PID","citado por ISSN","citado por título","citado por título do documento"
"""
import argparse
import logging
import codecs
import json

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

        self._citedby = utils.citedby_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        header = [u"PID", u"ISSN", u"título", u"área temática", u"ano de publicação", u"tipo de documento", u"título do documento", u"citado por PID", u"citado por ISSN", u"citado por título", u"citado por título do documento"]
        self.write(','.join(header))

    def write(self, line):
        if not self.output_file:
            print(line)
        else:
            self.output_file.write('%s\r\n' % line)

    def run(self):
        for item in self.items():
            self.write(item)


    def citedby(self, pid):
        data = self._citedby.citedby_pid(pid, False)
        dataj = json.loads(data)
        if isinstance(dataj, dict):
            for item in dataj.get('cited_by', []):
                yield item

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.documents(collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                for item in self.citedby(data.publisher_id):
                    yield self.fmt_csv(data, item)
        
    def fmt_csv(self, data, citedby):
        know_languages = set(['pt', 'es', 'en'])
        languages = set(data.languages())
        line = []
        line.append(data.publisher_id)
        line.append(data.journal.scielo_issn)
        line.append(data.journal.title)
        line.append(','.join(data.journal.subject_areas))
        line.append(data.publication_date[0:4])
        line.append(data.document_type)
        line.append(data.original_title())
        line.append(citedby.get('code', ''))
        line.append(citedby.get('issn', ''))
        line.append(citedby.get('source', ''))
        line.append(citedby.get('titles', [''])[0])

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
