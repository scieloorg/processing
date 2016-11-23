# coding: utf-8
"""
Este processamento gera uma tabulação de citações concedidas no SciELO por
artigos da coleção SciELO.
Formato de saída:
"PID","ISSN","título","área temática","ano de publicação","tipo de documento","título do documento","citado por PID","citado por ISSN","citado por título","citado por título do documento"
"""
import argparse
import logging
import codecs
import json
import datetime

import utils
import choices

logger = logging.getLogger(__name__)

OUTPUT_FORMAT = 'csv'


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


def compute_citations(raw_data):

    data = []
    for publication_year in raw_data['aggregations']['publication_year']['buckets']:
        for reference_publication_year in publication_year['reference_publication_year']['buckets']:
            result = (publication_year['key'], (reference_publication_year['key'], reference_publication_year['doc_count']))
            data.append(result)

    return data


class Dumper(object):

    def __init__(self, collection, issns=None, output_file=None, output_format=OUTPUT_FORMAT):

        self._citedby = utils.citedby_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.output_format = output_format
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file

        if output_format != 'json':
            header = []
            header.append(u"extraction date")
            header.append(u"study unit")
            header.append(u"collection")
            header.append(u"ISSN SciELO")
            header.append(u"ISSN\'s")
            header.append(u"title at SciELO")
            header.append(u"title thematic areas")
            for area in choices.THEMATIC_AREAS:
                header.append(u"title is %s" % area.lower())
            header.append(u"title is multidisciplinary")
            header.append(u"title current status")
            header.append(u"has optimized queries")
            header.append(u"publications from (year)")
            header.append(u"cited publications from (year)")
            header.append(u"total of citations")

            self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

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
            for data in self._articlemeta.journals(
                    collection=self.collection, issn=issn):
                logger.debug('Reading journal: %s' % data.scielo_issn)

                titles = []
                titles.append(data.title)
                titles.append(data.title_nlm)
                titles.append(data.fulltitle)
                titles.append(data.abbreviated_title)
                titles.append(data.abbreviated_iso_title)
                titles += data.other_titles or []
                titles = [i for i in set(titles) if i]

                citedby = self._citedby.publication_and_citing_years(data.scielo_issn, titles)

                for item in compute_citations(citedby) or []:
                    yield self.fmt_csv((data, item))

    def fmt_csv(self, content):

        data, citedby = content

        issns = []
        if data.print_issn:
            issns.append(data.print_issn)
        if data.electronic_issn:
            issns.append(data.electronic_issn)

        line = []
        line.append(datetime.datetime.now().isoformat()[0:10])
        line.append(u'journal')
        line.append(data.collection_acronym)
        line.append(data.scielo_issn)
        line.append(u';'.join(issns))
        line.append(data.title)
        line.append(u';'.join(data.subject_areas or []))
        for area in choices.THEMATIC_AREAS:
            if area.lower() in [i.lower() for i in data.subject_areas or []]:
                line.append(u'1')
            else:
                line.append(u'0')
        line.append('1' if len(data.subject_areas or []) > 2 else '0')
        line.append(data.current_status)
        line.append('1' if self._citedby.has_optmized_journal_queries(data.scielo_issn) else '0')
        line.append(str(citedby[0]))
        line.append(str(citedby[1][0]))
        line.append(str(citedby[1][1]))

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
        '--output_format',
        '-f',
        choices=['json', 'csv'],
        default=OUTPUT_FORMAT,
        help='Output format'
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

    dumper = Dumper(args.collection, issns, args.output_file, args.output_format)

    dumper.run()
