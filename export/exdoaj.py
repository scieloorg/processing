# coding: utf-8
"""
Este processamento realiza a exportação de registros SciELO para o DOAJ
"""
import os
import argparse
import logging
import codecs
import json
import requests
from io import BytesIO, StringIO
from datetime import datetime, timedelta

from lxml import etree

from doaj.articles import Articles

import utils

FROM = datetime.now() - timedelta(days=30)
FROM = FROM.isoformat()[:10]

DOAJ_XSD = open(os.path.dirname(__file__)+'/xsd/doajArticles.xsd', 'r').read()
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

    def __init__(self, collection, issns=None, output_file=None, from_date=FROM, 
        user=None, password=None, api_token=None):

        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.from_date = from_date
        self.user = user
        self.password = password
        self.issns = issns or [None]
        self.session = self.authenticated_session()
        self.parse_schema()
        self.doaj_articles = Articles(usertoken=api_token)


    def _doaj_id_by_meta(self, issn, publication_year, title):
        ### Query by metadata

        escaped_title = ''

        for char in title:
            if char in ['+','-','&','|','!','(',')','{','}','[',']','^','"','~','*','?',':','\\']:
                escaped_title += u'\\'+char
                continue
            escaped_title += char

        query = 'issn:%s AND year:%s AND title:%s' % (
            issn,
            publication_year,
            escaped_title
        )

        result = []

        try:
            result = [i for i in self.doaj_articles.search(query)]
        except:
            logger.debug('Fail to query DOAJ API using metadata: %s' % query)

        if len(result) == 1:
            return result[0].get('id', None)

    def _doaj_id_by_doi(self, doi):
        ### Query by doi
        query = 'doi:%s' % (doi)

        result = []
        try:
            result = [i for i in self.doaj_articles.search(query)]
        except:
            logger.debug('Fail to query DOAJ API using DOI: %s' % query)

        if len(result) == 1:
            return result[0].get('id', None)

    def _doaj_id(self, document):

        doaj_id = None

        if document.original_title():
            doaj_id = self._doaj_id_by_meta(
                document.scielo_issn,
                document.publication_date[0:4],
                document.original_title()
            )

        if doaj_id:
            return doaj_id

        if document.doi:
            return self._doaj_id_by_doi(document.doi)

    def parse_schema(self):
        xsd = BytesIO(DOAJ_XSD.encode('utf-8'))
        try:
            sch_doc = etree.parse(xsd)
            sch = etree.XMLSchema(sch_doc)
        except Exception as e:
            logger.exception(e)
            logger.error('Fail to parse XML')
            return False
        
        self.doaj_schema = sch

    def authenticated_session(self):
        auth_url = 'https://doaj.org/account/login'
        login = {'username': self.user, 'password': self.password}

        session = requests.Session()
        try:
            request = session.post(auth_url, data=login)
        except requests.exceptions.SSLError:
            logger.debug('Authentication without SSL validation')
            request = session.post(auth_url, data=login, verify=False)

        if request.status_code != 200:
            logger.debug('Authentication attempt done')
            return None

        if u'Incorrect' in request.text:
            logger.debug('Incorrect username or password')
            return None

        logger.debug('Authenticated successfully')

        return session

    def xml_is_valid(self, xml):
        
        try: 
            xml = StringIO(xml)
            xml_doc = etree.parse(xml)
            logger.debug('XML is well formed')
        except Exception as e:
            logger.exception(e)
            logger.error('Fail to parse XML')
            return False

        try:
            result = self.doaj_schema.assertValid(xml_doc)
            logger.debug('XML is valid')
            return True
        except Exception as e:
            logger.exception(e)
            logger.error('Fail to parse XML')
            return False

    def send_xml(self, file_name, file_data):
        files = {'file': (file_name, file_data)}

        try:
            response = self.session.post(
                'https://doaj.org/publisher/uploadfile',
                data={'schema': 'doaj'},
                files=files
            )
        except requests.ConnectionError:
            logger.debug('Fail to send document to DOAJ')
            return False

        if u'successfully uploaded' in response.text:
            logger.debug('Document Sent')
            return True

    def run(self):
        if not self.session:
            return None

        for issn in self.issns:
            for document in self._articlemeta.documents(collection=self.collection, issn=issn, from_date=self.from_date):
                logger.debug('Reading document: %s_%s' % (document.publisher_id, document.collection_acronym))

                if document.data.get('doaj_id', None):
                    logger.debug('Document already available in DOAJ: %s_%s' % (document.publisher_id, document.collection_acronym))
                    continue

                doaj_id = self._doaj_id(document)

                if doaj_id:
                    self._articlemeta.set_doaj_id(document.publisher_id, document.collection_acronym, doaj_id)
                    continue

                try:
                    xml = self._articlemeta.document(document.publisher_id, document.collection_acronym, fmt='xmldoaj')
                except Exception as e:
                    logger.exception(e)
                    logger.error('Fail to read document: %s_%s' % (document.publisher_id, document.collection_acronym))
                    xml = u''

                if not self.xml_is_valid(xml):
                    logger.error('Fail to parse xml document: %s_%s' % (document.publisher_id, document.collection_acronym))
                    continue

                logger.debug('Sending document: %s_%s' % (document.publisher_id, document.collection_acronym))
                filename = '%s_%s.xml' % (document.publisher_id, document.collection_acronym)

                self.send_xml(filename, xml)

def main():

    parser = argparse.ArgumentParser(
        description='Load documents into DOAJ'
    )

    parser.add_argument(
        'issns',
        nargs='*',
        help='ISSN\'s separated by spaces'
    )

    parser.add_argument(
        '--issns_file',
        '-i',
        default=None,
        help='Full path to a txt file within a list of ISSNs to be exported'
    )    

    parser.add_argument(
        '--user',
        '-u',
        required=True,
        help='DOAJ Publisher account name'
    )

    parser.add_argument(
        '--password',
        '-p',
        required=True,
        help='DOAJ Publisher account password'
    )

    parser.add_argument(
        '--collection',
        '-c',
        help='Collection Acronym'
    )

    parser.add_argument(
        '--from_date',
        '-f',
        default=FROM,
        help='ISO date like %s' % FROM
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

    issns_from_file = None
    if args.issns_file:
        with open(args.issns_file, 'r') as f:
            issns_from_file = utils.ckeck_given_issns([i.strip() for i in f])

    if issns:
        issns += issns_from_file if issns_from_file else []
    else:
        issns = issns_from_file if issns_from_file else []

    dumper = Dumper(
        args.collection, issns, from_date=args.from_date, user=args.user,
        password=args.password)

    dumper.run()
