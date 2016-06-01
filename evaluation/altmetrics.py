# coding: utf-8
"""
Este processamento gera uma tabulação com scores do altimetrics para documentos SciELO
"""

import argparse
import logging
import codecs
import requests
import urlparse
import datetime

import utils
import choices

logger = logging.getLogger(__name__)

ALTMETRICS_API_URL = 'http://api.altmetric.com/v1/citations/at'
ALTMETRICS_KEY = '8f87ca8cd778d4140b1ef713afa4008d'


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


def get_doi_from_url(url):

    if 'http://dx.doi.org/' in url:
        return url.lower().replace('http://dx.doi.org/', '')

    return None


class Dumper(object):

    def __init__(self, collection, issns=None, output_file=None):

        self._ratchet = utils.ratchet_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
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
        header.append(u"document publishing ID (PID SciELO)")
        header.append(u"document publishing year")
        header.append(u"document type")
        header.append(u"document is citable")
        header.append(u"score")
        header.append(u'altmetrics url')

        self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

    def write(self, line):
        if not self.output_file:
            print(line.encode('utf-8'))
        else:
            self.output_file.write('%s\r\n' % line)

    def run(self):
        for item in self.items():
            self.write(item)

    def altmetrics_items_by_journals(self, issn):

        payload = {
            'num_results': 100,
            'key': ALTMETRICS_KEY
        }
        payload['issns'] = issn
        page = 0
        while True:
            page += 1
            payload['page'] = page
            try:
                logger.debug('Requesting data to altmetrics %s' % str(payload))
                response = requests.get(ALTMETRICS_API_URL, params=payload, timeout=10)
            except Exception as e:
                logger.error('Could not retrieve data from altmetrics %s' % str(payload))
                continue

            if response.status_code == 404:  # fim de paginacao
                raise StopIteration

            try:
                data = response.json()
            except:
                logger.debug('Invalid JSON data retrieved for %s' % response.url)
                continue

            if data == 'Not Found':
                raise StopIteration

            for item in data.get('results', []):
                yield item

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.journals(collection=self.collection, issn=issn):
                for altmetrics_item in self.altmetrics_items_by_journals(data.scielo_issn):
                    yield self.fmt_csv(data, altmetrics_item)

    def fmt_csv(self, data, altmetrics):
        article = None
        url = altmetrics.get('url', None)
        title = altmetrics.get('title', '').replace('\n', '')
        doi = altmetrics.get('doi', get_doi_from_url(url))
        details_url = altmetrics.get('details_url', None)
        pid = urlparse.parse_qs(urlparse.urlparse(url).query).get('pid', None) if url else None

        if doi:
            article = self._articlemeta.document(doi.upper(), self.collection)

        publication_date = article.publication_date if article else u'not defined'
        publisher_id = article.publisher_id if article else u'not defined'
        document_type = article.document_type if article else u'not defined'
        score = altmetrics.get('score', None)

        issns = []
        if data.print_issn:
            issns.append(data.print_issn)
        if data.electronic_issn:
            issns.append(data.electronic_issn)

        line = []
        line.append(datetime.datetime.now().isoformat()[0:10])
        line.append(u'document')
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
        line.append(publisher_id)
        if publication_date == u'not define':
            line.append(document_type)
        else:
            line.append(publication_date[0:4])
        line.append(document_type)
        if document_type == u'not define':
            line.append(document_type)
        else:
            line.append(u'1' if document_type.lower() in choices.CITABLE_DOCUMENT_TYPES else u'0')
        line.append(str(score) or u'0')
        line.append(details_url or u'not defined')

        return u','.join([u'"%s"' % i.replace(u'"', u'""') for i in line])


def main():

    parser = argparse.ArgumentParser(
        description='Dump Altmetrics Score'
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
