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
        header = [
            u"Título do Periódico (publication_title)",
            u"ISSN impresso (print_identifier)",
            u"ISSN online (online_identifier)",
            u"Data do primeiro fascículo (date_first_issue_online)",
            u"volume do primeiro fascículo (num_first_vol_online)",
            u"número do primeiro fascículo (num_first_issue_online)",
            u"Data do último fascículo publicado (date_last_issue_online)",
            u"volume do último fascículo publicado (num_last_vol_online)",
            u"número do último fascículo publicado (num_last_issue_online)",
            u"url de fascículos (title_url)",
            u"primeiro autor (first_author)",
            u"ID do periódico no SciELO (title_id)",
            u"informação de embargo (embargo_info)",
            u"cobertura (coverage_depth)",
            u"informação sobre cobertura (coverage_notes)",
            u"nome do publicador (publisher_name)",
            u"tipo de publicação (publication_type)",
            u"data de publicação monográfica impressa (date_monograph_published_print)",
            u"data de publicação monográfica online (date_monograph_published_online)",
            u"volume de monografia (monograph_volume)",
            u"edição de monografia (monograph_edition)",
            u"primeiro editor (first_editor)",
            u"ID de publicação pai (parent_publication_title_id)",
            u"ID de publicação prévia (preceding_publication_title_id)",
            u"tipo de acesso (access_type)"

        ]

        self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

    def _first_included_document_by_journal(self, issn, collection):

        fid = self._publicationstats.first_included_document_by_journal(
            issn, collection)

        if not fid:
            return None

        document = self._articlemeta.document(fid['pid'], fid['collection'])

        if not document.data:
            return None

        return document

    def _last_included_document_by_journal(self, issn, collection):

        lid = self._publicationstats.last_included_document_by_journal(
            issn, collection)

        if not lid:
            return None

        document = self._articlemeta.document(lid['pid'], lid['collection'])

        if not document.data:
            return None

        return document

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
        line.append(
            first_document.publication_date or '' if first_document else '')
        line.append(
            first_document.issue.volume or '' if first_document and first_document.issue else '')
        line.append(
            first_document.issue.number or '' if first_document and first_document.issue else '')
        if data.current_status != 'current':
            line.append(
                last_document.publication_date or '' if last_document else '')
            line.append(
                last_document.issue.volume or '' if last_document and last_document.issue else '')
            line.append(
                last_document.issue.number or '' if last_document and last_document.issue else '')
        else:
            line += ['', '', '']
        line.append(data.url().replace('sci_serial', 'sci_issues'))
        line.append('')  # first_author
        line.append(data.scielo_issn or '')
        line.append('')  # embargo_info
        line.append('fulltext')  # coverage_depth
        line.append('')  # coverage_notes
        line.append(' '.join(data.publisher_name) if data.publisher_name else [])  # publisher_name
        line.append('Serial')  # publication_type
        line.append('')  # date_monograph_published_print
        line.append('')  # date_monograph_published_online
        line.append('')  # monograph_volume
        line.append('')  # monograph_edition
        line.append('')  # first_editor
        line.append('')  # parent_publication_title_id
        line.append('')  # preceding_publication_title_id
        line.append('F')  # access_type

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
