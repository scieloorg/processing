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

DOAJ_XSD = open(os.path.dirname(__file__)+'/xsd/doaj/doajArticles.xsd', 'r').read()
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
        user=None, password=None, api_token=None, corrections_db=None, validate_schema=False):

        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.from_date = from_date
        self.user = user
        self.password = password
        self.issns = issns or [None]
        self.session = self.authenticated_session()
        self.validate_schema = validate_schema
        self.doaj_schema = self.parse_schema() if self.validate_schema else None
        self.doaj_articles = Articles(usertoken=api_token)
        self.corrections_db = corrections_db

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
                document.journal.scielo_issn,
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

        return sch

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

        if u'File uploaded and waiting to be processed' in response.text:
            logger.info('Document Sent')
            return True
        else:
            self.authenticated_session()
            logger.error('Document not Sent: %s' % response.status_code)
            return False

    def run(self):
        if not self.session:
            return None

        extra_filter = json.dumps(
            {
                'doaj_id': {'$exists': 0}
            }
        )

        for issn in self.issns:
            for document in self._articlemeta.documents(
                    collection=self.collection, issn=issn,
                    from_date=self.from_date, extra_filter=extra_filter):
                logger.info('Reading document: %s_%s' % (document.publisher_id, document.collection_acronym))

                if document.data.get('doaj_id', None):
                    logger.debug('Document already available in DOAJ: %s_%s' % (document.publisher_id, document.collection_acronym))
                    continue

                doaj_id = self._doaj_id(document)

                if doaj_id:
                    logger.debug('Document already available in DOAJ, setting id on Article Meta for: %s_%s' % (document.publisher_id, document.collection_acronym))
                    self._articlemeta.set_doaj_id(document.publisher_id, document.collection_acronym, doaj_id)
                    continue

                try:
                    xml = self._articlemeta.document(document.publisher_id, document.collection_acronym, fmt='xmldoaj')
                except Exception as e:
                    logger.exception(e)
                    logger.error('Fail to read document: %s_%s' % (document.publisher_id, document.collection_acronym))
                    xml = u''

                if self.validate_schema and not self.xml_is_valid(xml):
                    logger.error('Fail to parse xml document: %s_%s' % (document.publisher_id, document.collection_acronym))
                    continue

                logger.info('Sending document: %s_%s' % (document.publisher_id, document.collection_acronym))
                filename = '%s_%s.xml' % (document.publisher_id, document.collection_acronym)

                # aplica a correção aos ISSNs.
                if self.corrections_db is not None:
                    xml = self._fix_issns(xml)

                self.send_xml(filename, xml)

    def _get_doaj_issns(self, issn):
        corrected = self.corrections_db.find(issn)
        result = {}
        for issn in corrected.get("issns", []):
            result[issn["type"]] = issn["id"]

        return result

    def _fix_issns(self, xml_data):
        et = etree.parse(BytesIO(xml_data.encode("utf-8")))
        issns = [i.text for i in et.xpath("/records/record/issn | /records/record/eissn")]
        for issn in issns:
            try:
                issns_from_doaj = self._get_doaj_issns(issn)
            except ValueError:
                logger.info('could not find corrected issns for "%s"', issn)
                continue
            else:
                result = replace_issns(et, pissn=issns_from_doaj.get("pissn"), eissn=issns_from_doaj.get("eissn")) 
                logger.debug('the xml "%s" was replaced by "%s"', xml_data, result)
                return result
        else:
            return xml_data


def replace_issns(et, pissn=None, eissn=None):
    assert any([pissn, eissn])

    record_node = et.find("record")
    journalTitle_node = et.xpath("/records/record/journalTitle")[0]

    for node in et.xpath("/records/record/issn | /records/record/eissn"):
        del(record_node[record_node.index(node)])

    if eissn:
        new_eissn_node = etree.Element("eissn")
        new_eissn_node.text = eissn
        record_node.insert(
            record_node.index(journalTitle_node) + 1,
            new_eissn_node
        )

    if pissn:
        new_issn_node = etree.Element("issn")
        new_issn_node.text = pissn
        record_node.insert(
            record_node.index(journalTitle_node) + 1,
            new_issn_node
        )

    return etree.tostring(et, encoding="unicode", pretty_print=False)


class CorrectionsDB(object):
    def __init__(self, data):
        self._data = tuple(data)
        def _make_issn_getter(issn_type):
            def _issn_getter(item):
                for issn_data in item.get('issns', []):
                    if issn_data['type'] == issn_type:
                        return issn_data['id']

            return _issn_getter

        self._index = self._create_index(self._data, _make_issn_getter('eissn'))
        self._index.update(self._create_index(self._data, _make_issn_getter('pissn')))

    def _create_index(self, data, func):
        result = {func(item): i for i, item in enumerate(data)}
        try:
            del(result[None])
        except KeyError:
            pass
        return result

    def find(self, issn):
        pos = self._index.get(issn)
        if pos is None:
            raise ValueError
        return self._data[pos]


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

    parser.add_argument(
        '--validate_schema',
        action='store_true',
        help='Validate each document against the DOAJ Schema before submitting',
    )

    parser.add_argument(
        '--corrections_db',
        help='Path to the corrections database file',
        type=argparse.FileType("r"),
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

    if args.corrections_db:
        corrections_data = [json.loads(line) for line in args.corrections_db.readlines()]
        corrections_db = CorrectionsDB(corrections_data)
        logger.info('a database of corrections will be used to fix ISSNs before sending the data')
    else:
        corrections_db = None
        logger.info('no database of corrections was given, the processing will proceed anyway')

    dumper = Dumper(
        args.collection, issns, from_date=args.from_date, user=args.user,
        password=args.password, corrections_db=corrections_db)

    dumper.run()
