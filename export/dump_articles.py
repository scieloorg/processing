# coding: utf-8
"""
This scripts uses the Article Meta API to harvest all SciELO Network Documents
They are stored into a zip file.
This processing always harvest the entire database to garantee that all the
documents are up to date.
"""
import os
import logging
import zipfile
import datetime
import argparse
from lxml import etree

import requests
from articlemeta.client import ThriftClient

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

trans_acronym = {'scl': 'bra'}


def getschema():

    try:
        xsd = requests.get('https://raw.githubusercontent.com/scieloorg/articles_meta/master/tests/xsd/scielo_sci/ThomsonReuters_publishing.xsd').text
        logger.debug('Schema download')
        return xsd
    except:
        logger.error('Schema download fail')


class Dumper(object):

    def __init__(self, collection, issns=None, xml_format='xmlwos', zip_name='file.zip'):
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.zip_name = zip_name
        self.xml_format = xml_format

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for document in self._articlemeta.documents(collection=self.collection, issn=issn, only_identifiers=True):
                xml = self._articlemeta.document(code=document.code, collection=document.collection, fmt=self.xml_format)
                yield (document.code, document.collection, xml)

    def run(self):

        client = ThriftClient()

        logger.info('Creating zip file: %s', self.zip_name)
        logger.info('XML Format: %s', self.xml_format)

        with zipfile.ZipFile(self.zip_name, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as thezip:
            for pid, collection, document in self.items():
                logger.debug('Loading XML file for %s', '_'.join([collection, pid]))
                collection = trans_acronym.get(collection, collection)
                issn = pid[1:10]
                xml_file = '{0}/{1}/{2}.xml'.format(collection, issn, pid)
                thezip.writestr(xml_file, bytes(document.encode('utf-8')))

            readmef = open(os.path.dirname(__file__)+'/templates/dumparticle_readme.txt', 'r').read()
            readme = '{0}\r\n* Documents updated at: {1}\r\n'.format(readmef, datetime.datetime.now().isoformat())

            thezip.writestr("README.txt", bytes(readme.encode('utf-8')))

            if self.xml_format == 'xmlwos':
                xsd = getschema()
                if xsd:
                    thezip.writestr("schema/ThomsonReuters_publishing.xsd", bytes(xsd.encode('utf-8')))

        logger.info('Zip created: %s', self.zip_name)
        logger.info('Processing finished')


def main():

    parser = argparse.ArgumentParser(
        description="Dump SciELO Network metadata"
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
        '--zip_file',
        '-f',
        default='dumpdata.zip',
        help='Full path to the zip file that will receive the documents'
    )

    parser.add_argument(
        '--xml_format',
        '-x',
        default='xmlwos',
        choices=['xmlwos', 'xmlrsps'],
        help='XML output format'
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

    dumper = Dumper(
        args.collection,
        issns,
        args.xml_format,
        args.zip_file
    )

    dumper.run()
