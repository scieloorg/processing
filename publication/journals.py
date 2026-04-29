# coding: utf-8
"""
Este processamento gera uma tabulação com contagens, soma, mediana de alguns
elementos do artigo: total de autores, total de citações, total de páginas
"""

import argparse
import logging
import codecs
import datetime

import utils
import choices

from clients.analytics import Analytics
from scieloh5m5 import h5m5

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


def interruption_status(history):

    if not history:
        return None

    if len(history) == 0:
        return None

    last = history[-1]

    if not last[1] in ['suspended', 'deceased']:
        return None

    return tuple(last)


class Dumper(object):

    def __init__(self, collection, issns=None, output_file=None, years=6):
        self._articlemeta = utils.articlemeta_server()
        self._publicationstats = utils.publicationstats_server()
        self._analytics = Analytics()
        self.collection = collection
        self.issns = issns
        self._years = years
        self._lines = []
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        now = datetime.date.today().year
        self.years_range = [i for i in range(now, now-self._years, -1)]
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
        header.append("title + subtitle SciELO")
        header.append("short title SciELO")
        header.append("short title ISO")
        header.append("title PubMed")
        header.append("publisher name")
        header.append("use license")
        header.append("alpha frequency")
        header.append("numeric frequency (in months)")
        header.append("inclusion year at SciELO")
        header.append("stopping year at SciELO")
        header.append("stopping reason")
        header.append("date of the first document")
        header.append("volume of the first document")
        header.append("issue of the first document")
        header.append("date of the last document")
        header.append("volume of the last document")
        header.append("issue of the last document")
        header.append("total of issues")
        header += ["issues at %s" % str(i) for i in self.years_range]
        header.append("total of regular issues")
        header += ["regular issues at %s" % str(i) for i in self.years_range]
        header.append("total of documents")
        header += ["documents at %s" % str(i) for i in self.years_range]
        header.append("citable documents")
        header += ["citable documents at %s" % str(i) for i in self.years_range]
        for year in self.years_range:
            header.append('portuguese documents at %s ' % year)
        for year in self.years_range:
            header.append('spanish documents at %s ' % year)
        for year in self.years_range:
            header.append('english documents at %s ' % year)
        for year in self.years_range:
            header.append('other language documents at %s ' % year)
        for year in self.years_range:
            header.append('google scholar h5 %s ' % year)
        for year in self.years_range:
            header.append('google scholar m5 %s ' % year)

        self.write(','.join(['"%s"' % i.replace('"', '""') for i in header]))

    def _documents_languages_by_year(self, issn, collection, years=None):

        years = self._years if years == None else years

        languages = self._publicationstats.documents_languages_by_year(
            issn, collection, years=years)

        return languages

    def _number_of_issues_by_year(self, issn, collection, years=None, type=None):

        years = self._years if years == None else years

        issues = self._publicationstats.number_of_issues_by_year(
            issn, collection, years=years, type=type)

        return issues

    def _number_of_articles_by_year(self, issn, collection, years=None, document_types=None):

        years = self._years if years == None else years

        issues = self._publicationstats.number_of_articles_by_year(
            issn, collection, document_types=document_types, years=years)

        return issues

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

    def _impact_factor(self, issn, collection):

        current_year = datetime.date.today().year

        itens = {str(i): (0.0, 0.0, 0.0, 0.0, 0.0, 0.0) for i in range(
            current_year, current_year-self._years, -1)}

        impact_factor = self._analytics.impact_factor(issn, collection)

        if impact_factor:
            for item in impact_factor:
                if item[0] in itens:
                    itens[item[0]] = tuple(item[1:])

        return itens

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
            for data in self._articlemeta.journals(
                    collection=self.collection, issn=issn):
                yield self.fmt_csv(data)

    def fmt_csv(self, data):
        first_document = self._first_included_document_by_journal(
            data.scielo_issn, data.collection_acronym)
        last_document = self._last_included_document_by_journal(
            data.scielo_issn, data.collection_acronym)

        interruption = interruption_status(data.status_history)

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
        line.append(';'.join(data.subject_areas or []))
        for area in choices.THEMATIC_AREAS:
            if area.lower() in [i.lower() for i in data.subject_areas or []]:
                line.append('1')
            else:
                line.append('0')
        line.append('1' if len(data.subject_areas or []) > 2 else '0')
        line.append(utils.get_metadata_value(data, 'current_status'))
        line.append(' '.join([data.title or '', data.subtitle or '']))
        line.append(data.abbreviated_title or '')
        line.append(data.abbreviated_iso_title or '')
        line.append(data.title_nlm or '')
        line.append('; '.join(data.publisher_name or []))
        line.append(data.permissions.get('id', '') if data.permissions else '')
        line.append(data.periodicity[1] or '')
        line.append(data.periodicity_in_months or '')
        line.append(data.creation_date[:4])
        line.append(interruption[0][:4] if interruption else '')
        line.append(interruption[2][:4] if interruption else '')
        line.append(first_document.publication_date or '' if first_document else '')
        line.append(first_document.issue.volume or '' if first_document and first_document.issue else '')
        line.append(first_document.issue.number or '' if first_document and first_document.issue else '')
        line.append(last_document.publication_date or '' if last_document else '')
        line.append(last_document.issue.volume or '' if last_document and last_document.issue else '')
        line.append(last_document.issue.number or '' if last_document and last_document.issue else '')

        line.append(str(self._number_of_issues_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=0
            ))
        )

        issues = self._number_of_issues_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=self._years
        )

        for issue in issues:
            line.append(str(issue[1]))

        line.append(str(self._number_of_issues_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=0,
            type='regular'
            ))
        )

        regular_issues = self._number_of_issues_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=self._years,
            type='regular'
        )

        for issue in regular_issues:
            line.append(str(issue[1]))

        line.append(str(self._number_of_articles_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=0))
        )

        documents = self._number_of_articles_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=self._years
        )

        for document in documents:
            line.append(str(document[1]))

        line.append(str(self._number_of_articles_by_year(
            data.scielo_issn,
            data.collection_acronym,
            document_types=choices.CITABLE_DOCUMENT_TYPES,
            years=0))
        )

        documents = [str(i[1]) for i in self._number_of_articles_by_year(
            data.scielo_issn,
            data.collection_acronym,
            document_types=choices.CITABLE_DOCUMENT_TYPES,
            years=self._years
        )]

        for document in documents:
            line.append(str(document))

        languages = self._documents_languages_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=self._years
        )

        for years, values in sorted(list(languages.items()), reverse=True):
            line.append(str(values['pt']))
        for years, values in sorted(list(languages.items()), reverse=True):
            line.append(str(values['es']))
        for years, values in sorted(list(languages.items()), reverse=True):
            line.append(str(values['en']))
        for years, values in sorted(list(languages.items()), reverse=True):
            line.append(str(values['other']))

        for year in self.years_range:
            h5 = h5m5.get(data.scielo_issn, str(year))
            h5 = h5.get('h5', None) if h5 else None
            line.append(h5 or '')

        for year in self.years_range:
            m5 = h5m5.get(data.scielo_issn, str(year))
            m5 = m5.get('m5', None) if m5 else None
            line.append(m5 or '')

        joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])

        return joined_line


def main():

    parser = argparse.ArgumentParser(
        description='Dump general journals indicators'
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
