# coding: utf-8
"""
Este processamento gera uma tabulação com contagens, soma, mediana de alguns
elementos do artigo: total de autores, total de citações, total de páginas

Formato de saída:
"issn scielo","issn impresso","issn eletrônico","título","área temática","bases WOS","áreas WOS","status","ano de inclusão","licença de uso padrão"
"""

import argparse
import logging
import codecs
from datetime import date

import utils

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

    def __init__(self, collection, issns=None, output_file=None, years=5):
        self._articlemeta = utils.articlemeta_server()
        self._publicationstats = utils.publicationstats_server()
        self._analytics = Analytics()
        self.collection = collection
        self.issns = issns
        self._years = years
        self._header = []
        self._lines = []
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        self._build_header()

    def _build_header(self):

        now = date.today().year
        years_range = [i for i in range(now, now-self._years, -1)]

        self._header = [
            u"issn scielo",
            u"issn impresso",
            u"issn eletrônico",
            u"nome do publicador",
            u"título",
            u"título e subtitulo",
            u"título abreviado",
            u"título abreviado sob norma ISO",
            u"título nlm",
            u"periodicidade descritiva",
            u"periodicidade numérica (em meses)",
            u"área temática",
            u"bases WOS",
            u"áreas temáticas WOS",
            u"situação atual",
            u"ano de inclusão",
            u"ano de paralização",
            u"motivo de paralização",
            u"licença de uso padrão",
            u"data do primeiro documento",
            u"volume do primeiro documento",
            u"número do primeiro documento",
            u"data do último documento",
            u"volúme do último  documento",
            u"número do último documento",
            u"issues todos os anos"
        ]
        self._header += [u"issues em %s" % str(i) for i in years_range]
        self._header.append(u"documentos todos os anos")
        self._header += [u"documentos em %s" % str(i) for i in years_range]
        self._header.append(u"artigos originais e de revisão todos os anos")
        self._header += [u"artigos originais e de revisão em %s" % str(i) for i in years_range]
        for year in years_range:
            self._header += [
                u'documentos em português em %s ' % year,
                u'documento em espanhol em %s ' % year,
                u'documentos em inglês em %s ' % year,
                'documentos em outros idiomas em %s ' % year
            ]

        for year in years_range:
            self._header.append(u'índice de imediatez, ano base (%s)' % year)
            self._header.append(u'fator de impacto 1 ano, ano base (%s)' % year)
            self._header.append(u'fator de impacto 2 ano, ano base (%s)' % year)
            self._header.append(u'fator de impacto 3 ano, ano base (%s)' % year)
            self._header.append(u'fator de impacto 4 ano, ano base (%s)' % year)
            self._header.append(u'fator de impacto 5 ano, ano base (%s)' % year)

        self.write(','.join(['"%s"' % i.replace('"', '""') for i in self._header]))

    def _documents_languages_by_year(self, issn, collection, years=None):

        if years is None:
            years = self._years

        languages = self._publicationstats.documents_languages_by_year(
            issn, collection, years=years)

        return languages

    def _number_of_issues_by_year(self, issn, collection, years=None):

        if years is None:
            years = self._years

        issues = self._publicationstats.number_of_issues_by_year(
            issn, collection, years=years)

        return issues

    def _number_of_articles_by_year(self, issn, collection, years=None, document_types=None):

        if years is None:
            years = self._years

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

        current_year = date.today().year

        itens = {str(i): (0.0, 0.0, 0.0, 0.0, 0.0, 0.0) for i in range(
            current_year, current_year-self._years, -1)}

        impact_factor = self._analytics.impact_factor(issn, collection)

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
            self._lines.append(item)

        for item in self._lines:
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

        line = [
            data.scielo_issn,
            data.print_issn or "",
            data.electronic_issn or "",
            data.publisher_name or "",
            data.title,
            data.fulltitle,
            data.abbreviated_title or "",
            data.abbreviated_iso_title or "",
            data.title_nlm or "",
            data.periodicity or "",
            data.periodicity_in_months or "",
            ','.join(data.subject_areas or []),
            ','.join(data.wos_citation_indexes or []),
            ','.join(data.wos_subject_areas or []),
            data.current_status,
            data.creation_date[:4],
            interruption[0] if interruption else '',
            interruption[2] if interruption else ''
        ]

        if data.permissions:
            line.append(data.permissions.get('id', "") or "")
        else:
            line.append("")

        line.append(
            first_document.publication_date or '' if first_document else '')
        line.append(first_document.volume or '' if first_document else '')
        line.append(first_document.issue or '' if first_document else '')
        line.append(
            last_document.publication_date or '' if last_document else '')
        line.append(last_document.volume or '' if last_document else '')
        line.append(last_document.issue or '' if last_document else '')

        line.append(
            str(self._number_of_issues_by_year(
                data.scielo_issn, data.collection_acronym, years=0))
        )

        issues = self._number_of_issues_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=self._years
        )

        line += [str(i[1]) for i in issues]

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

        line += [str(i[1]) for i in documents]

        line.append(str(self._number_of_articles_by_year(
            data.scielo_issn,
            data.collection_acronym,
            document_types=['research-article', 'review-article'],
            years=0))
        )

        line += [str(i[1]) for i in self._number_of_articles_by_year(
            data.scielo_issn,
            data.collection_acronym,
            document_types=['research-article', 'review-article'],
            years=self._years
        )]

        languages = self._documents_languages_by_year(
            data.scielo_issn,
            data.collection_acronym,
            years=self._years
        )

        for years, values in sorted(languages.items(), reverse=True):
            line += [
                str(values['pt']),
                str(values['es']),
                str(values['en']),
                str(values['other'])
            ]

        impact_factor = self._impact_factor(
            data.scielo_issn, self.collection)

        for year, values in sorted(impact_factor.items(), reverse=True):
            line += [str(i) for i in values]

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
