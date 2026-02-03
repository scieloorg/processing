# coding: utf-8
"""
Este processamento gera uma tabulação de periódicos seguindo o formato Kbart.

Formato de saída (headers em inglês, conforme diretrizes KBART):
publication_title, print_identifier, online_identifier, date_first_issue_online, 
num_first_vol_online, num_first_issue_online, date_last_issue_online, 
num_last_vol_online, num_last_issue_online, title_url, first_author, title_id, 
embargo_info, coverage_depth, coverage_notes, publisher_name, publication_type, 
date_monograph_published_print, date_monograph_published_online, monograph_volume, 
monograph_edition, first_editor, parent_publication_title_id, 
preceding_publication_title_id, access_type
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
            u"publication_title",
            u"print_identifier",
            u"online_identifier",
            u"date_first_issue_online",
            u"num_first_vol_online",
            u"num_first_issue_online",
            u"date_last_issue_online",
            u"num_last_vol_online",
            u"num_last_issue_online",
            u"title_url",
            u"first_author",
            u"title_id",
            u"embargo_info",
            u"coverage_depth",
            u"coverage_notes",
            u"publisher_name",
            u"publication_type",
            u"date_monograph_published_print",
            u"date_monograph_published_online",
            u"monograph_volume",
            u"monograph_edition",
            u"first_editor",
            u"parent_publication_title_id",
            u"preceding_publication_title_id",
            u"access_type"

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
                if data.current_status != 'current':
                    logger.debug('Skipping non-active journal: %s (status: %s)' % (data.scielo_issn, data.current_status))
                    continue
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
        line.append(' '.join(data.publisher_name) if data.publisher_name else '')  # publisher_name
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
