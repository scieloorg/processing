#coding: utf-8
import os
import weakref
import datetime
import re
import unicodedata
import logging
import string

from thrift import clients

try:
    from configparser import ConfigParser
except:
    from ConfigParser import ConfigParser

logger = logging.getLogger(__name__)

REGEX_ISSN = re.compile(r"^[0-9]{4}-[0-9]{3}[0-9xX]$")
TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


def cleanup_string(text):

    try:
        nfd_form = unicodedata.normalize('NFD', text.strip().lower())
    except TypeError:
        nfd_form = unicodedata.normalize('NFD', unicode(text.strip().lower()))

    cleaned_str = u''.join(x for x in nfd_form if x in string.ascii_letters or x == ' ')

    return remove_tags(cleaned_str).lower()


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = force_text(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
        value = re.sub(r'[^\w\s-]', '', value, flags=re.U).strip().lower()
        return mark_safe(re.sub(r'[-\s]+', '-', value, flags=re.U))
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()

    return mark_safe(re.sub(r'[-\s]+', '-', value))


class SingletonMixin(object):
    """
    Adds a singleton behaviour to an existing class.

    weakrefs are used in order to keep a low memory footprint.
    As a result, args and kwargs passed to classes initializers
    must be of weakly refereable types.
    """
    _instances = weakref.WeakValueDictionary()

    def __new__(cls, *args, **kwargs):
        key = (cls, args, tuple(kwargs.items()))

        if key in cls._instances:
            return cls._instances[key]

        try:
            new_instance = super(type(cls), cls).__new__(cls, *args, **kwargs)
        except TypeError:
            new_instance = super(type(cls), cls).__new__(cls, **kwargs)

        cls._instances[key] = new_instance

        return new_instance


class Configuration(SingletonMixin):
    """
    Acts as a proxy to the ConfigParser module
    """
    def __init__(self, fp, parser_dep=ConfigParser):
        self.conf = parser_dep()

        try:
            self.conf.read_file(fp)
        except AttributeError:
            self.conf.readfp(fp)

    @classmethod
    def from_env(cls):
        try:
            filepath =  os.environ['PROCESSING_SETTINGS_FILE']
        except KeyError:
            raise ValueError('missing env variable PROCESSING_SETTINGS_FILE')

        return cls.from_file(filepath)

    @classmethod
    def from_file(cls, filepath):
        """
        Returns an instance of Configuration

        ``filepath`` is a text string.
        """
        fp = open(filepath, 'r')

        return cls(fp)

    def __getattr__(self, attr):
        return getattr(self.conf, attr)

    def items(self):
        """Settings as key-value pair.
        """
        return [(section, dict(self.conf.items(section, raw=True))) for \
            section in [section for section in self.conf.sections()]]


config = Configuration.from_env()
settings = dict(config.items())


def publicationstats_server():
    try:
        server = settings['app:main']['publicationstats_thriftserver'].split(':')
        host = server[0]
        port = int(server[1])
    except:
        logger.warning('Error defining PublicationStats thrift server, assuming default server publicationstats.scielo.org:11620')
        host = 'publication.scielo.org'
        port = 11620

    return clients.PublicationStats(host, port)


def citedby_server():
    try:
        server = settings['app:main'].get('citedby_thriftserver', 'citedby.scielo.org:11610')
    except:
        logger.warning('Error defining Citedby thrift server, assuming default server citedby.scielo.org:11610')
        server = 'citedby.scielo.org:11610'

    return clients.Citedby(domain=server)


def ratchet_server():
    try:
        server = settings['app:main']['ratchet_thriftserver'].split(':')
        host = server[0]
        port = int(server[1])
    except:
        logger.warning('Error defining Ratchet thrift server, assuming default server ratchet.scielo.org:11630')
        host = 'ratchet.scielo.org'
        port = 11630

    return clients.Ratchet(host, port)


def articlemeta_server():
    try:
        server = settings['app:main'].get('articlemeta_thriftserver', 'articlemeta.scielo.org:11620')
    except:
        logger.warning('Error defining Article Meta thrift server, assuming default server articlemeta.scielo.org:11720')
        server = 'articlemeta.scielo.org:11620'

    return clients.ArticleMeta(domain=server)


def accessstats_server():
    try:
        server = settings['app:main']['accessesstats_thriftserver'].split(':')
        host = server[0]
        port = int(server[1])
    except:
        logger.warning('Error defining Access Stats thrift server, assuming default server accessstats.scielo.org:11660')
        host = 'ratchet.scielo.org'
        port = 11660

    return clients.AccessStats(host, port)


def is_valid_date(value):

    try:
        datetime.datetime.strptime(value, '%Y-%m-%d')
    except:
        try:
            datetime.datetime.strptime(value, '%Y-%m')
        except:
            try:
                datetime.datetime.strptime(value, '%Y')
            except:
                return False

    return True


def split_date(value):
    """
        This method splits a date in a tuple.
        value: valid iso date

        ex:
        2016-01-31: ('2016','01','01')
        2016-01: ('2016','01','')
        2016: ('2016','','')
    """
    if not is_valid_date(value):
        return ('', '', '')

    splited = value.split('-')

    try:
        year = splited[0]
    except IndexError:
        year = ''

    try:
        month = splited[1]
    except IndexError:
        month = ''

    try:
        day = splited[2]
    except IndexError:
        day = ''

    return (year, month, day)


def ckeck_given_issns(issns):
    valid_issns = []

    for issn in issns:
        if not REGEX_ISSN.match(issn):
            continue
        valid_issns.append(issn)

    return valid_issns
