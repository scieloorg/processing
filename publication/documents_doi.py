# coding: utf-8
"""
Este processamento gera uma tabulação de DOIs e suas línguas correspondentes
para cada artigo da coleção SciELO.
"""
import argparse
import logging
import codecs
import datetime
import re

import utils

logger = logging.getLogger(__name__)

# DOI regex pattern to validate DOI format
DOI_REGEX = re.compile(r'10\.\d{4,}(?:\.\d+)?\/\S+')


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


def get_doi_and_lang(document):
    """
    This method retrieves the lang and DOI pairs from a document.
    Based on xylose's doi_and_lang property.
    """
    items = []
    
    # Try to get v337 field from document data
    try:
        raw_doi = document.data.get('article', {}).get('v337')
        for item in raw_doi or []:
            lang = item.get("l")
            doi = item.get("d")
            if lang and doi:
                # Check if lang and doi are swapped
                if len(DOI_REGEX.findall(lang)) == 1 and len(doi) == 2:
                    lang, doi = doi, lang
                if len(DOI_REGEX.findall(doi)) == 1 and len(lang) == 2:
                    items.append((lang, doi))
    except (AttributeError, KeyError):
        pass
    
    # Add the main DOI with original language if available
    if document.doi:
        try:
            original_lang = document.original_language()
        except (AttributeError, KeyError):
            # Try to get the first language from languages() method
            try:
                languages = document.languages()
                original_lang = languages[0] if languages else None
            except (AttributeError, KeyError, IndexError):
                original_lang = None
        
        item = (original_lang, document.doi)
        if all(item) and item not in items:
            items.insert(0, item)
    
    return items


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
        header.append(u"document publishing ID (PID SciELO)")
        header.append(u"document language")
        header.append(u"doi corresponding language")

        self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

    def write(self, line):
        if not self.output_file:
            print(line.encode('utf-8'))
        else:
            self.output_file.write('%s\r\n' % line)

    def run(self):
        for item in self.items():
            self.write(item)
        logger.info('Export finished')

    def items(self):

        if not self.issns:
            self.issns = [None]

        for issn in self.issns:
            for data in self._articlemeta.documents(collection=self.collection, issn=issn):
                logger.debug('Reading document: %s' % data.publisher_id)
                for line in self.fmt_csv(data):
                    yield line

    def fmt_csv(self, data):
        """
        Returns a list of CSV lines, one for each DOI/language pair.
        """
        lines = []
        doi_lang_pairs = get_doi_and_lang(data)
        
        # If no DOI information is available, skip this document
        if not doi_lang_pairs:
            return lines
        
        extraction_date = datetime.datetime.now().isoformat()[0:10]
        
        for lang, doi in doi_lang_pairs:
            line = []
            line.append(extraction_date)
            line.append(u'document')
            line.append(data.collection_acronym)
            line.append(data.publisher_id)
            line.append(lang or u'')
            line.append(doi or u'')
            
            joined_line = ','.join(['"%s"' % i.replace('"', '""') for i in line])
            lines.append(joined_line)
        
        return lines


def main():

    parser = argparse.ArgumentParser(
        description='Dump DOI and language pairs by article'
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
        help='Logging level'
    )

    args = parser.parse_args()
    _config_logging(args.logging_level, args.logging_file)
    logger.info('Dumping data for: %s' % args.collection)

    issns = None
    if len(args.issns) > 0:
        issns = utils.ckeck_given_issns(args.issns)

    dumper = Dumper(args.collection, issns, args.output_file)

    dumper.run()
