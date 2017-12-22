

import argparse
import logging
import codecs

import utils

from publication import (
    documents_counts,
    documents_affiliations,
    documents_affiliations_nationality,
    documents_languages,
    documents_licenses,
    documents_authors,
    documents_dates
)


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

    def __init__(self, collection, home_nationality=None, issns=None):

        self._ratchet = utils.ratchet_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.home_nationality = home_nationality
        self.documents_counts = documents_counts.Dumper(collection, output_file='documents_counts.csv')
        self.documents_affiliations = documents_affiliations.Dumper(collection, output_file='documents_affiliations.csv')
        self.documents_languages = documents_languages.Dumper(collection, output_file='documents_languages.csv')
        self.documents_licenses = documents_licenses.Dumper(collection, output_file='documents_licenses.csv')
        self.documents_authors = documents_authors.Dumper(collection, output_file='documents_authors.csv')
        self.documents_dates = documents_dates.Dumper(collection, output_file='documents_dates.csv')
        if self.home_nationality:
            self.documents_affiliations_nationality = documents_affiliations_nationality.Dumper(home_nationality, collection, output_file='documents_affiliation_nationality.csv')

    def run(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.documents(collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                self.documents_counts.write(self.documents_counts.fmt_csv(data))
                self.documents_affiliations.write(self.documents_affiliations.fmt_csv(data))
                self.documents_languages.write(self.documents_languages.fmt_csv(data))
                self.documents_licenses.write(self.documents_licenses.fmt_csv(data))
                self.documents_authors.write(self.documents_authors.fmt_csv(data))
                self.documents_dates.write(self.documents_dates.fmt_csv(data))
                if self.home_nationality:
                    self.documents_affiliations_nationality.write(self.documents_affiliations_nationality.fmt_csv(data))

        logger.info('Export finished')


def main():

    parser = argparse.ArgumentParser(
        description='Dump SciELO tabs'
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
        '--home_nationality',
        '-n',
        help='ISO 3166 two letters country code which will be considered as the home nationality.'
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

    dumper = Dumper(args.collection, home_nationality=args.home_nationality, issns=issns)

    dumper.run()
