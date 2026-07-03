# coding: utf-8
"""
Este processamento gera uma tabulação de fator de impacto dos periódicos SciELO. 
"""

import argparse
import logging
import codecs
import datetime

import utils
from clients.analytics import Analytics
import choices

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
        self._analytics = Analytics()
        self.collection = collection
        self.issns = issns
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        header = []
        header.append("extraction date")
        header.append("study unit")
        header.append("collection")
        header.append("ISSN SciELO")
        header.append("ISSN\'s")
        header.append("title at SciELO")
        header.append("title thematic areas")
        for area in choices.THEMATIC_AREAS:
            header.append("title is %s" % area.lower())
        header.append("title is multidisciplinary")
        header.append("title current status")
        header.append("base year")
        header.append("imediacity")
        header.append("SciELO impact 1 year")
        header.append("SciELO impact 2 years")
        header.append("SciELO impact 3 years")
        header.append("SciELO impact 4 years")
        header.append("SciELO impact 5 years")

        self.write(','.join(['"%s"' % i.replace('"', '""') for i in header]))

    def write(self, line):
        if not self.output_file:
            print(line)
        else:
            self.output_file.write('%s\r\n' % line)

    def run(self):
        for item in list(self.items()):
            self.write(item)
        logger.info('Export finished')

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.journals(collection=self.collection, issn=issn):
                for item in self.fmt_csv(data):
                    yield item

    def fmt_csv(self, data):

        issns = []
        if data.print_issn:
            issns.append(data.print_issn)
        if data.electronic_issn:
            issns.append(data.electronic_issn)

        line = []
        line.append(datetime.datetime.now().isoformat()[0:10])
        line.append('journal')
        line.append(data.collection_acronym)
        line.append(data.scielo_issn)
        line.append(';'.join(issns))
        line.append(data.title)
        line.append(';'.join(data.subject_areas))
        for area in choices.THEMATIC_AREAS:
            if area.lower() in [i.lower() for i in data.subject_areas]:
                line.append('1')
            else:
                line.append('0')
        line.append('1' if len(data.subject_areas or []) > 2 else '0')
        line.append(data.current_status)

        impact_factor = self._analytics.impact_factor(data.scielo_issn, self.collection)

        for item in impact_factor or []:
            l = None
            l = line + [str(i) for i in item]
            joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in l])
            yield joined_line


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
