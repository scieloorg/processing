# coding: utf-8
"""
Este processamento realiza a exportação de registros SciELO para o formato RSPS
"""

import os
import argparse
import logging
import codecs
import json
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

def analyze_xml(xml, document):
    """Analyzes `file` against packtools' XMLValidator.
    """

    f = StringIO(xml)

    try:
        xml = packtools.XMLValidator(f)
    except:
        logger.error('Could not read file %s' % document.publisher_id)
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

    def fmt_json(self, data, xml_result):

        fmt = {}

        fmt['code'] = data.publisher_id
        fmt['collection'] =  data.collection_acronym
        fmt['id'] = '_'.join([data.collection_acronym, data.publisher_id])
        fmt['document_type'] = data.document_type
        fmt['publication_year'] = data.publication_date[0:4]
        fmt['document_type'] = data.document_type
        fmt['data_version'] = 'legacy' if data.data_model_version == 'html' else 'xml'
        fmt.update(xml_result)
        return json.dumps(fmt)

    def run(self):
        for issn in self.issns:
            for document in self._articlemeta.documents(collection=self.collection, issn=issn):
                try:
                    xml = self._articlemeta.document(document.publisher_id, document.collection_acronym, fmt='xmlrsps')
                except Exception as e:
                    logger.exception(e)
                    logger.error('Fail to read document: %s_%s' % (document.publisher_id, document.collection_acronym))
                    xml = u''
                logger.debug('Reading document: %s' % document.publisher_id)
                validation_result = analyze_xml(xml, document)
                print(self.fmt_json(document, validation_result))


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

    dumper = Dumper(args.collection, issns)

    dumper.run()