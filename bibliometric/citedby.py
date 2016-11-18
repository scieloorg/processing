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
            header.append(u"document publishing ID (PID SciELO)")
            header.append(u"document publishing year")
            header.append(u"document type")
            header.append(u"document is citable")
            header.append(u"document title")
            header.append(u"cited by pid")
            header.append(u"cited by issn")
            header.append(u"cited by journal")
            header.append(u"cited by document title")

            self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

    def write(self, line):
        if not self.output_file:
            print(line.encode('utf-8'))
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

                citedby = self._citedby.citedby_pid(data.publisher_id, metaonly=False)
                dataj = json.loads(citedby)
                if self.output_format == 'json' and isinstance(dataj, dict):
                    yield self.fmt_json(dataj)
                    continue

                for item in dataj.get('cited_by', []):
                    yield self.fmt_csv((data, item))

    def fmt_json(self, content):

        return json.dumps(content)

    def fmt_csv(self, content):

        data, citedby = content

        know_languages = set(['pt', 'es', 'en'])
        languages = set(data.languages())

        issns = []
        if data.journal.print_issn:
            issns.append(data.journal.print_issn)
        if data.journal.electronic_issn:
            issns.append(data.journal.electronic_issn)

        line = []
        line.append(datetime.datetime.now().isoformat()[0:10])
        line.append(u'document')
        line.append(data.collection_acronym)
        line.append(data.journal.scielo_issn)
        line.append(u';'.join(issns))
        line.append(data.journal.title)
        line.append(u';'.join(data.journal.subject_areas or []))
        for area in choices.THEMATIC_AREAS:
            if area.lower() in [i.lower() for i in data.journal.subject_areas or []]:
                line.append(u'1')
            else:
                line.append(u'0')
        line.append('1' if len(data.journal.subject_areas or []) > 2 else '0')
        line.append(data.journal.current_status)
        line.append(data.publisher_id)
        line.append(data.publication_date[0:4])
        line.append(data.document_type)
        line.append(u'1' if data.document_type.lower() in choices.CITABLE_DOCUMENT_TYPES else '0')
        line.append(data.original_title() or '')
        line.append(citedby.get('code', ''))
        line.append(citedby.get('issn', ''))
        line.append(citedby.get('source', ''))

        if 'titles' in citedby and len(citedby['titles']) > 0:
            line.append(citedby['titles'][0])
        else:
            line.append('')

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
