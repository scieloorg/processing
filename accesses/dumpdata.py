# conding: utf-8
"""
Esse processamento condença os metadados de documentos com os dados de acessos.
"""
import sys
import argparse
import logging
import re
import json

from thrift import clients
import choices

__version__ = 0.1

logger = logging.getLogger(__name__)

ratchet = clients.Ratchet('ratchet.scielo.org', 11630)
articlemeta = clients.ArticleMeta('articlemeta.scielo.org', 11720)
REGEX_ISSN = re.compile(r"^[0-9]{4}-[0-9]{3}[0-9xX]$")
REGEX_PDF_PATH = re.compile(r'/pdf.*\.pdf$')
collections_acronym = [i.code for i in articlemeta.collections()]
DAYLY_GRANULARITY = False

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

def ckeck_given_issns(issns):
    valid_issns = []

    for issn in issns:
        if not REGEX_ISSN.match(issn):
            logger.info('Skiping Invalid ISSN: %s' % issn)
            continue
        valid_issns.append(issn)

    return valid_issns

def pdf_keys(fulltexts):

    keys = []

    if not 'pdf' in fulltexts:
        return keys

    for language, url in fulltexts['pdf'].items():
        path = REGEX_PDF_PATH.search(url)
        if path:
            keys.append(path.group().upper())

    return keys

def fbpe_key(code):
    """
    input:
        'S0102-67202009000300001'
    output:
        'S0102-6720(09)000300001'
    """

    begin = code[0:10]
    year = code[12:14]
    end = code[14:]

    return '%s(%s)%s' % (begin, year, end)

def eligible_match_keys(document):
    keys = []

    keys.append(document.publisher_id)
    keys.append(fbpe_key(document.publisher_id))
    keys += pdf_keys(document.fulltexts())

    return keys

def join_accesses(unique_id, accesses, dayly_granularity=DAYLY_GRANULARITY):
    """
    Esse metodo recebe 1 ou mais chaves para um documento em específico para que
    os acessos sejam recuperados no Ratchet e consolidados em um unico id.
    Esse processo é necessário pois os acessos de um documento podem ser registrados
    para os seguintes ID's (PID, PID FBPE, Path PDF).
    PID: Id original do SciELO ex: S0102-67202009000300001
    PID FBPE: Id antigo do SciELO ex: S0102-6720(09)000300001
    Path PDF: Quando o acesso é feito diretamente para o arquivo PDF no FS do
    servidor ex: /pdf/rsp/v12n10/v12n10.pdf
    """

    joined_data = {}
    listed_data = []
    def joining_monthly(joined_data, atype, data):
        del(data['total'])
        for year, months in data.items():
            del(months['total'])
            for month in months:
                dt = '%s-%s' % (year[1:], month[1:])
                joined_data.setdefault(dt, {})
                joined_data[dt].setdefault(atype, 0)
                joined_data[dt][atype] += data[year][month]['total']

        return joined_data

    def joining_dayly(joined_data, atype, data):

        del(data['total'])
        for year, months in data.items():
            del(months['total'])
            for month, days in months.items():
                del(days['total'])
                for day in days:
                    dt = '%s-%s-%s' % (year[1:], month[1:], day[1:])
                    joined_data.setdefault(dt, {})
                    joined_data[dt].setdefault(atype, 0)
                    joined_data[dt][atype] += data[year][month][day]

        return joined_data

    joining = joining_monthly
    if dayly_granularity:
        joining = joining_dayly

    for data in accesses:
        for key, value in data.items():
            if not key in ['abstract', 'html', 'pdf', 'epdf']:
                continue
            joined_data = joining(joined_data, key, value)

    return joined_data

def country(country):
    if country in choices.ISO_3166:
        return country
    if country in choices.ISO_3166_COUNTRY_AS_KEY:
        return choices.ISO_3166_COUNTRY_AS_KEY[country]
    return 'undefined'

def join_metadata_with_accesses(document, accesses_date, accesses):

    data = {}
    data['id'] = '_'.join([document.collection_acronym, document.publisher_id])
    data['pid'] = document.publisher_id
    data['issn'] = document.journal.scielo_issn
    data['journal_title'] = document.journal.title
    data['issue'] = document.publisher_id[0:18]
    data['publication_date'] = document.publication_date
    data['publication_year'] = document.publication_date[0:4]
    data['subject_areas'] = [i for i in document.journal.subject_areas]
    data['collection'] = document.collection_acronym
    data['document_type'] = document.document_type
    data['languages'] = list(set([i for i in document.languages()]+[document.original_language() or 'undefined']))
    data['aff_countries'] = ['undefined']
    if document.mixed_affiliations:
        data['aff_countries'] = list(set([country(aff.get('country', 'undefined')) for aff in document.mixed_affiliations]))
    data['access_date'] = accesses_date
    data['access_year'] = accesses_date[:4]
    data['access_month'] = accesses_date[5:7]
    data['access_day'] = accesses_date[8:]
    data['access_abstract'] = accesses.get('abstract', 0)
    data['access_html'] = accesses.get('html', 0)
    data['access_pdf'] = accesses.get('pdf', 0)
    data['access_epdf'] = accesses.get('epdf', 0)
    data['access_total'] = sum([v for i, v in accesses.items()])

    return data

def get_accesses(collection, issn=None, dayly_granularity=DAYLY_GRANULARITY):
    for document in articlemeta.documents(collection=collection, issn=issn):
        accesses = []
        keys = eligible_match_keys(document)
        for key in keys:
            data = ratchet.document(key)
            jdata = json.loads(data)
            if 'objects' in jdata and len(jdata['objects']) > 0:
                accesses.append(jdata['objects'][0])
        joined_accesses = join_accesses(document.publisher_id, accesses, dayly_granularity=dayly_granularity)

        for adate, adata in joined_accesses.items():
            yield join_metadata_with_accesses(document, adate, adata)

def fmt_json(data):
    return json.dumps(data)

def fmt_csv(data):

    line = [
        data['collection'],
        data['pid'],
        data['issn'],
        data['issue'],
        data['journal_title'],
        data['publication_date'],
        data['publication_year'],
        data['document_type'],
        ', '.join(data['subject_areas']),
        ', '.join(data['languages']),
        ', '.join(data['aff_countries']),
        data['access_date'],
        data['access_date'][:4],
        data['access_date'][5:7],
        data['access_date'][8:],
        data.get('access_abstract', 0),
        data.get('access_html', 0),
        data.get('access_pdf', 0),
        data.get('access_epdf', 0),
        data['access_total']
    ]

    return ';'.join(['"%s"' % i for i in line])

def run(collection, issns=None, dayly_granularity=False, fmt=fmt_csv, output_file=None):

    if not issns:
        issns = [None]

    if not output_file:
        for issn in issns:
            for data in get_accesses(collection, issn=issn, dayly_granularity=dayly_granularity):
                print(fmt(data))
        exit()

    with open(output_file, 'w') as f:
        for issn in issns:
            for data in get_accesses(collection, issn=issn, dayly_granularity=dayly_granularity):
                f.write('%s\r\n' % fmt(data))

def main():
    parser = argparse.ArgumentParser(
        description='Dump accesses'
    )

    parser.add_argument(
        'issns',
        nargs='*',
        help='ISSN\'s separated by spaces'
    )

    parser.add_argument(
        '--collection',
        '-c',
        choices=collections_acronym,
        help='Collection Acronym'
    )

    parser.add_argument(
        '--dayly_granularity',
        '-d',
        action='store_true',
        help='Accesses granularity default will be monthly if not specified'
    )

    parser.add_argument(
        '--output_format',
        '-f',
        choices=['json', 'csv'],
        default='csv',
        help='Output format'
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
        issns = ckeck_given_issns(args.issns)

    output_format = fmt_csv
    if args.output_format == 'json':
        output_format = fmt_json

    run(args.collection, issns, args.dayly_granularity, output_format, args.output_file)
