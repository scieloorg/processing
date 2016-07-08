# coding: utf-8
"""
Este processamento realiza a exportação de registros SciELO para o formato RSPS
"""

import os
import argparse
import logging
import json
import threading
import multiprocessing
from io import StringIO
import itertools

import packtools
from packtools.catalogs import XML_CATALOG
from lxml.etree import XMLSyntaxError
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

    summary['dtd_is_valid'] = dtd_is_valid
    summary['sps_is_valid'] = sps_is_valid
    summary['is_valid'] = bool(dtd_is_valid and sps_is_valid)

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
        summary['dtd_errors'] = []
        summary['sps_errors'] = []
        return summary
    except XMLSyntaxError as e:
        logger.exception(e)
        summary = {}
        summary['dtd_is_valid'] = False
        summary['sps_is_valid'] = False
        summary['is_valid'] = False
        summary['parsing_error'] = True
        summary['dtd_errors'] = [e.message]
        summary['sps_errors'] = []
        return summary
    else:
        summary = summarize(xml)

        return summary


class ThreadSafeIter(object):
    """Wraps an iterable for safe use in a threaded environment.
    """
    def __init__(self, it):
        self.it = iter(it)
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.it)

    next = __next__


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
        fmt['journal'] = data.journal.title
        fmt['issn'] = data.journal.scielo_issn
        fmt['issue_label'] = data.issue.label
        fmt['subject_areas'] = data.journal.subject_areas
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

    def _worker(self, docs, t):
        for doc in docs:
            logger.debug('Running thread %s' % t)
            self.summaryze_xml_validation(doc['code'], doc['collection'], doc)

    def run(self, processes):
        max_threads = multiprocessing.cpu_count() * processes

        def _gen_iterdocs():
            """Produz um gerador de geradores de documentos.
            """
            for issn in self.issns:
                iterdocs = (self.fmt_json(doc)
                            for doc in self._articlemeta.documents(
                                collection=self.collection, issn=issn))
                yield iterdocs

        iterdocs = itertools.chain.from_iterable(_gen_iterdocs())
        safe_iterdocs = ThreadSafeIter(iterdocs)

        jobs = []
        for t in range(max_threads):
            thread = threading.Thread(target=self._worker,
                                      args=(safe_iterdocs, t))
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
        '--processes',
        '-p',
        type=int,
        default=1,
        help='Number of processes per CPU'
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

    dumper.run(args.processes)
