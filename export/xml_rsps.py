# coding: utf-8
"""
Este processamento realiza a exportação de registros SciELO para o formato RSPS
"""

import os
import argparse
import logging
import codecs
import json
import threading
import multiprocessing
from Queue import Queue, Empty
from io import StringIO

import packtools
from packtools.catalogs import XML_CATALOG

import utils

os.environ['XML_CATALOG_FILES'] = XML_CATALOG
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


def summarize(validator):

    def _make_err_message(err):
        """ An error message is comprised of the message itself and the
        element sourceline.
        """
        err_msg = {'message': err.message}

        try:
            err_element = err.get_apparent_element(validator.lxml)
        except ValueError:
            logger.info('Could not locate the element name in: %s' % err.message)
            err_element = None

        if err_element is not None:
            err_msg['apparent_line'] = err_element.sourceline
        else:
            err_msg['apparent_line'] = None

        return err_msg

    dtd_is_valid, dtd_errors = validator.validate()
    sps_is_valid, sps_errors = validator.validate_style()

    summary = {
        'dtd_errors': [_make_err_message(err) for err in dtd_errors],
        'sps_errors': [_make_err_message(err) for err in sps_errors],
    }

    summary['dtd_is_valid'] = validator.validate()[0]
    summary['sps_is_valid'] = validator.validate_style()[0]
    summary['is_valid'] = bool(validator.validate()[0] and validator.validate_style()[0])

    return summary


def analyze_xml(xml):
    """Analyzes `file` against packtools' XMLValidator.
    """

    f = StringIO(xml)

    try:
        xml = packtools.XMLValidator.parse(f, sps_version='sps-1.1')
    except packtools.exceptions.PacktoolsError as e:
        logger.exception(e)
        summary = {}
        summary['dtd_is_valid'] = False
        summary['sps_is_valid'] = False
        summary['is_valid'] = False
        summary['parsing_error'] = True
        return summary
    else:
        summary = summarize(xml)

        return summary


class Dumper(object):

    def __init__(self, collection, issns=None):

        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns or [None]

    def fmt_json(self, data):

        fmt = {}

        fmt['code'] = data.publisher_id
        fmt['collection'] = data.collection_acronym
        fmt['id'] = '_'.join([data.collection_acronym, data.publisher_id])
        fmt['document_type'] = data.document_type
        fmt['publication_year'] = data.publication_date[0:4]
        fmt['document_type'] = data.document_type
        fmt['data_version'] = 'legacy' if data.data_model_version == 'html' else 'xml'

        return fmt

    def prepare_queue(self, issn, q):

        for document in self._articlemeta.documents(collection=self.collection, issn=issn):
            q.put(self.fmt_json(document))

    def summaryze_xml_validation(self, pid, collection_acronym, output_format):

        try:
            xml = self._articlemeta.document(pid, collection_acronym, fmt='xmlrsps')
        except Exception as e:
            logger.exception(e)
            logger.error('Fail to read document: %s_%s' % (pid, collection_acronym))
            xml = u''

        logger.debug('Reading document: %s' % pid)

        output_format.update(analyze_xml(xml))

        print(json.dumps(output_format))

    def _worker(self, q, t):

        while True:

            try:
                doc = q.get(timeout=0.5)
            except Empty:
                return

            logger.debug('Running thread %s' % t)
            self.summaryze_xml_validation(doc['code'], doc['collection'], doc)

    def run(self):

        job_queue = Queue()

        for issn in self.issns:

            self.prepare_queue(issn, job_queue)

            jobs = []

            max_threads = multiprocessing.cpu_count() * 2

            for t in range(max_threads):
                thread = threading.Thread(target=self._worker, args=(job_queue, t))
                jobs.append(thread)
                thread.start()
                logger.info('Thread running %s' % thread)

        for job in jobs:
            job.join()


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
        '--issns_file',
        '-i',
        default=None,
        help='Full path to a txt file within a list of ISSNs to be exported'
    )

    parser.add_argument(
        '--collection',
        '-c',
        help='Collection Acronym'
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

    dumper = Dumper(args.collection, issns)

    dumper.run()