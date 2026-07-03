# coding: utf-8
"""
Este processamento gera uma tabulação de datas do artigo (publicação, submissão,
    aceite, entrada no scieloe atualização no scielo)
"""
import argparse
import logging
import codecs
import datetime

import xylose.scielodocument

import utils
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

        self._ratchet = utils.ratchet_server()
        self._articlemeta = utils.articlemeta_server()
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
        header.append("document publishing ID (PID SciELO)")
        header.append("document publishing year")
        header.append("document type")
        header.append("document is citable")
        header.append("document submitted at")
        header.append("document submitted at year")
        header.append("document submitted at month")
        header.append("document submitted at day")
        header.append("document accepted at")
        header.append("document accepted at year")
        header.append("document accepted at month")
        header.append("document accepted at day")
        header.append("document reviewed at")
        header.append("document reviewed at year")
        header.append("document reviewed at month")
        header.append("document reviewed at day")
        header.append("document published as ahead of print at")
        header.append("document published as ahead of print at year")
        header.append("document published as ahead of print at month")
        header.append("document published as ahead of print at day")
        header.append("document published at")
        header.append("document published at year")
        header.append("document published at month")
        header.append("document published at day")
        header.append("document published in SciELO at")
        header.append("document published in SciELO at year")
        header.append("document published in SciELO at month")
        header.append("document published in SciELO at day")
        header.append("document updated in SciELO at")
        header.append("document updated in SciELO at year")
        header.append("document updated in SciELO at month")
        header.append("document updated in SciELO at day")

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
            for data in self._articlemeta.documents(collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                yield self.fmt_csv(data)

    def fmt_csv(self, data):
        document_publication_date = (
            data.document_publication_date or
            data.creation_date or
            data.update_date or
            ''
        )
        document_publication_date_splitted = utils.split_date(
            document_publication_date)

        issue_publication_date = data.issue_publication_date
        issue_publication_date_splitted = utils.split_date(
            issue_publication_date)

        issns = []
        if data.journal.print_issn:
            issns.append(data.journal.print_issn)
        if data.journal.electronic_issn:
            issns.append(data.journal.electronic_issn)

        line = []
        line.append(datetime.datetime.now().isoformat()[0:10])
        line.append('document')
        line.append(data.collection_acronym)
        line.append(data.journal.scielo_issn)
        line.append(';'.join(issns))
        line.append(data.journal.title)
        line.append(';'.join(data.journal.subject_areas or []))
        for area in choices.THEMATIC_AREAS:
            if area.lower() in [i.lower() for i in data.journal.subject_areas or []]:
                line.append('1')
            else:
                line.append('0')
        line.append('1' if len(data.journal.subject_areas or []) > 2 else '0')
        line.append(data.journal.current_status)
        line.append(data.publisher_id)
        line.append(document_publication_date_splitted[0])
        line.append(data.document_type)
        line.append('1' if data.document_type.lower() in choices.CITABLE_DOCUMENT_TYPES else '0')
        line.append(data.receive_date or '')
        receive_splited = utils.split_date(data.receive_date or '')
        line.append(receive_splited[0])  # year
        line.append(receive_splited[1])  # month
        line.append(receive_splited[2])  # day
        line.append(data.acceptance_date or '')
        acceptance_splited = utils.split_date(data.acceptance_date or '')
        line.append(acceptance_splited[0])  # year
        line.append(acceptance_splited[1])  # month
        line.append(acceptance_splited[2])  # day
        line.append(data.review_date or '')
        review_splited = utils.split_date(data.review_date or '')
        line.append(review_splited[0])  # year
        line.append(review_splited[1])  # month
        line.append(review_splited[2])  # day
        
        try:
            aop_pubdate = data.ahead_publication_date or ''
        except (KeyError, xylose.scielodocument.UnavailableMetadataException):
            aop_pubdate = ''
            
        line.append(aop_pubdate)
        ahead_publication_date_splited = utils.split_date(aop_pubdate)
        line.append(ahead_publication_date_splited[0])  # year
        line.append(ahead_publication_date_splited[1])  # month
        line.append(ahead_publication_date_splited[2])  # day

        # u"document published at" (collection ou issue)
        line.append(issue_publication_date)
        line.append(issue_publication_date_splitted[0])  # year
        line.append(issue_publication_date_splitted[1])  # month
        line.append(issue_publication_date_splitted[2])  # day

        #u"document published in SciELO at" (pub, ou creation, ou last update)
        line.append(document_publication_date)
        line.append(document_publication_date_splitted[0])  # year
        line.append(document_publication_date_splitted[1])  # month
        line.append(document_publication_date_splitted[2])  # day

        line.append(data.update_date or '')
        update_splited = utils.split_date(data.update_date or '')
        line.append(update_splited[0])  # year
        line.append(update_splited[1])  # month
        line.append(update_splited[2])  # day
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
