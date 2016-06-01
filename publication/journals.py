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
        years_range = [i for i in range(now, now-self._years, -1)]
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
        header.append(u"title current status")
        header.append(u"title + subtitle SciELO")
        header.append(u"short title SciELO")
        header.append(u"short title ISO")
        header.append(u"title PubMed")
        header.append(u"publisher name")
        header.append(u"use license")
        header.append(u"alpha frequency")
        header.append(u"numeric frequency (in months)")
        header.append(u"inclusion year at SciELO")
        header.append(u"stopping year at SciELO")
        header.append(u"stopping reason")
        header.append(u"date of the first document")
        header.append(u"volume of the first document")
        header.append(u"issue of the first document")
        header.append(u"date of the last document")
        header.append(u"volume of the last document")
        header.append(u"issue of the last document")
        header.append(u"total of issues")
        header += [u"issues at %s" % str(i) for i in years_range]
        header.append(u"total of regular issues")
        header += [u"regular issues at %s" % str(i) for i in years_range]
        header.append(u"total of documents")
        header += [u"documents at %s" % str(i) for i in years_range]
        header.append(u"citable documents")
        header += [u"citable documents at %s" % str(i) for i in years_range]
        for year in years_range:
            header.append(u'portuguese documents at %s ' % year)
        for year in years_range:
            header.append(u'spanish documents at %s ' % year)
        for year in years_range:
            header.append(u'english documents at %s ' % year)
        for year in years_range:
            header.append(u'other language documents at %s ' % year)

        self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

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

        return document

    def _last_included_document_by_journal(self, issn, collection):

        lid = self._publicationstats.last_included_document_by_journal(
            issn, collection)

        if not lid:
            return None

        document = self._articlemeta.document(lid['pid'], lid['collection'])

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
        line.append(data.current_status)
        line.append(u' '.join([data.title or u'', data.subtitle or u'']))
        line.append(data.abbreviated_title or u'')
        line.append(data.abbreviated_iso_title or u'')
        line.append(data.title_nlm or u'')
        line.append(u'; '.join(data.publisher_name or []))
        line.append(data.permissions.get('id', u'') if data.permissions else u'')
        line.append(data.periodicity[1] or u'')
        line.append(data.periodicity_in_months or u'')
        line.append(data.creation_date[:4])
        line.append(interruption[0][:4] if interruption else u'')
        line.append(interruption[2][:4] if interruption else u'')
        line.append(first_document.publication_date or u'' if first_document else u'')
        line.append(first_document.issue.volume or u'' if first_document else u'')
        line.append(first_document.issue.number or u'' if first_document else u'')
        line.append(last_document.publication_date or u'' if last_document else u'')
        line.append(last_document.issue.volume or u'' if last_document else u'')
        line.append(last_document.issue.number or u'' if last_document else u'')

        line.append(unicode(self._number_of_issues_by_year(
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
            line.append(unicode(issue[1]))

        line.append(unicode(self._number_of_issues_by_year(
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
            line.append(unicode(issue[1]))

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
            line.append(unicode(document[1]))

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
            line.append(unicode(document))

        languages = self._documents_languages_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=self._years
        )

        for years, values in sorted(languages.items(), reverse=True):
            line.append(unicode(values['pt']))
        for years, values in sorted(languages.items(), reverse=True):
            line.append(unicode(values['es']))
        for years, values in sorted(languages.items(), reverse=True):
            line.append(unicode(values['en']))
        for years, values in sorted(languages.items(), reverse=True):
            line.append(unicode(values['other']))

        joined_line = u','.join([u'"%s"' % i.replace(u'"', u'""') for i in line])

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
