# coding: utf-8
"""
Este processamento gera uma tabulação de citações de cada artigo da
coleção SciELO.
"""
import argparse
import logging
import codecs
import datetime

import utils
import choices

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

    def __init__(self, collection, issns=None, output_file=None):

        self._ratchet = utils.ratchet_server()
        self._articlemeta = utils.articlemeta_server()
        self.collection = collection
        self.issns = issns
        self.output_file = codecs.open(output_file, 'w', encoding='utf-8') if output_file else output_file
        header = []
        header.append(u"pid")
        header.append(u"scielo_issn")
        header.append(u"publication_year")
        header.append(u"volume")
        header.append(u"source")
        header.append(u"doi")
        header.append(u"publication_type")
        header.append(u"number_or_suppl")
        header.append(u"reference_pid")
        header.append(u"part_title")

        self.write(u','.join([u'"%s"' % i.replace(u'"', u'""') for i in header]))

    def write(self, lines):

        if isinstance(lines, unicode):
            lines = [lines]

        for line in lines:
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
                for item in self.fmt_csv(data):
                    yield item

    def join_line(self, line):
        return ','.join(['"%s"' % i.replace('"', '""') for i in line])

    def fmt_csv(self, data):
        """
        Format citation data into CSV rows.
        
        Columns:
        - pid: Document PID
        - scielo_issn: SciELO ISSN from the document's journal
        - publication_year: Citation publication year
        - volume: Citation volume
        - source: Citation source (journal title, book title, thesis title, etc.)
        - doi: Citation DOI
        - publication_type: Citation publication type
        - number_or_suppl: Citation issue/number or supplement
        - reference_pid: Citation PID (v880)
        - part_title: Citation article_title or chapter_title
        """
        
        # If there are no citations, yield a single empty row for the document
        if not data.citations:
            line = []
            line.append(data.publisher_id or u'')
            line.append(data.journal.scielo_issn or u'')
            line.append(u'')
            line.append(u'')
            line.append(u'')
            line.append(u'')
            line.append(u'')
            line.append(u'')
            line.append(u'')
            line.append(u'')
            yield self.join_line(line)
            return
        
        # Process each citation
        for citation in data.citations:
            line = []
            
            # pid - Document PID
            line.append(data.publisher_id or u'')
            
            # scielo_issn - SciELO ISSN from the document's journal
            line.append(data.journal.scielo_issn or u'')
            
            # publication_year - Citation publication year
            pub_year = u''
            if citation.publication_date:
                try:
                    pub_year = unicode(citation.publication_date[0:4])
                except (TypeError, ValueError, AttributeError):
                    pass
            # Fallback to v64 if publication_date doesn't work
            if not pub_year and 'v64' in citation.data:
                pub_year = citation.data['v64'][0].get('_', u'')
            line.append(pub_year)
            
            # volume - Citation volume
            line.append(citation.volume or u'')
            
            # source - Citation source (journal title, book title, thesis title, etc.)
            line.append(citation.source or u'')
            
            # doi - Citation DOI
            line.append(citation.doi or u'')
            
            # publication_type - Citation publication type
            line.append(citation.publication_type or u'')
            
            # number_or_suppl - Citation issue/number
            issue = u''
            if citation.issue:
                issue = citation.issue
            # Check for supplement info in v882
            elif 'v882' in citation.data:
                v882_data = citation.data['v882'][0]
                if 'n' in v882_data:
                    issue = v882_data['n']
                elif 's' in v882_data:
                    issue = v882_data['s']
            line.append(issue)
            
            # reference_pid - Citation PID from v880
            ref_pid = u''
            if 'v880' in citation.data:
                ref_pid = citation.data['v880'][0].get('_', u'')
            line.append(ref_pid)
            
            # part_title - Citation article_title or chapter_title
            part_title = u''
            if citation.article_title:
                part_title = citation.article_title
            elif citation.chapter_title:
                part_title = citation.chapter_title
            line.append(part_title)
            
            yield self.join_line(line)


def main():

    parser = argparse.ArgumentParser(
        description='Dump citations distribution by article'
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
