# coding: utf-8
"""
Este processamento gera uma tabulação de afiliações para normalização.
Formato de saída:
"coleção","PID","ano de publicação","tipo de documento","título","número","normalizado","id de afiliação","instituição original","paises original","instituição normalizada","país normalizado ISO-3661","código de país normalizado ISO-3166","estado normalizado ISO-3166","código de estado normalizado ISO-3166"
"""
import argparse
import logging
import codecs
import utils
from choices import ISO_3166_COUNTRY_AS_KEY

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

    def __init__(self, collection, issns=None, output_file=None, not_normalized=True):

        self._ratchet = utils.ratchet_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.output_file = output_file
        self.not_normalized = not_normalized

    def run(self):

        header = [u"coleção", u"PID", u"ano de publicação", u"tipo de documento",u"título", u"número", u"normalizado", u"id de afiliação", u"instituição original", u"paises original", u"instituição normalizada", u"país normalizado ISO-3661", u"código de país normalizado ISO-3166", u"estado normalizado ISO-3166", u"código de estado normalizado ISO-3166"]

        if not self.issns:
            self.issns = [None]

        if not self.output_file:
            print('%s\r\n' % ','.join(header))
            for issn in self.issns:
                for data in self.get_data(issn=issn):
                    for item in self.fmt_csv(data):
                        print(item)
            exit()

        with codecs.open(self.output_file, 'w', encoding='utf-8') as f:
            f.write('%s\r\n' % ','.join(header))
            for issn in self.issns:
                for data in self.get_data(issn=issn):
                    for item in self.fmt_csv(data):
                        f.write('%s\r\n' % item)

    def fmt_csv(self, data):

        line = [
            data.collection_acronym,
            data.publisher_id,
            data.publication_date[0:4],
            data.document_type,
            data.journal.title,
            data.issue_label or ''
        ]

        if len(data.mixed_affiliations) == 0:
            joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line+['0']])
            yield joined_line

        original_aff = {aff['index']:aff for aff in data.affiliations or []}
        normalized_aff = {aff['index']:aff for aff in data.normalized_affiliations or []}

        for mx_aff in data.mixed_affiliations:
            aff_line = []

            status = '1' if mx_aff['normalized'] else '0'

            normalized_institution = normalized_aff.get(mx_aff['index'], {}).get('institution', '')
            normalized_country = normalized_aff.get(mx_aff['index'], {}).get('country', '')
            normalized_state = normalized_aff.get(mx_aff['index'], {}).get('state', '')
            original_institution = original_aff.get(mx_aff['index'], {}).get('institution', '')
            original_country = original_aff.get(mx_aff['index'], {}).get('country', '')

            if normalized_institution == '' or normalized_country == '' or ISO_3166_COUNTRY_AS_KEY.get(normalized_country, '') == '':
                status = '0'

            if self.not_normalized and status == '1':
                continue

            aff_line = [
                status,
                mx_aff['index'],
                original_institution,
                original_country,
                normalized_institution,
                normalized_country,
                ISO_3166_COUNTRY_AS_KEY.get(normalized_country, ''),
                normalized_state
            ]

            joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line+aff_line])
            yield joined_line

    def get_data(self, issn):
        for document in self._articlemeta.documents(collection=self.collection, issn=issn):
            logger.debug('Reading document: %s' % document.publisher_id)
            yield document


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
        '--not_normalized',
        '-n',
        action='store_true',
        help='Dump only not normalized affiliations'
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

    dumper = Dumper(args.collection, issns, args.output_file, args.not_normalized)

    dumper.run()
