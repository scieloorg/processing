#coding: utf-8
import os
import weakref
import datetime
import re
import unicodedata
import logging
import string

from configparser import ConfigParser

logger = logging.getLogger(__name__)

REGEX_ISSN = re.compile(r"^[0-9]{4}-[0-9]{3}[0-9xX]$")
TAG_RE = re.compile(r'<[^>]+>')
ENV_SETTINGS = {
    'ARTICLEMETA_THRIFTSERVER': 'articlemeta_thriftserver',
    'ARTICLEMETA_ADMINTOKEN': 'articlemeta_admintoken',
    'RATCHET_THRIFTSERVER': 'ratchet_thriftserver',
    'ACCESSSTATS_THRIFTSERVER': 'accessstats_thriftserver',
    'CITEDBY_THRIFTSERVER': 'citedby_thriftserver',
    'PUBLICATIONSTATS_THRIFTSERVER': 'publicationstats_thriftserver',
    'SOLR_SEARCH_SCIELO_ORG': 'solr_search_scielo_org',
    'SOLR_SEARCH_SCIELO_ORG_INDEX': 'solr_search_scielo_org_index',
}


def remove_tags(text):
    return TAG_RE.sub('', text)


def cleanup_string(text):

    if not isinstance(text, str):
        text = str(text)
    nfd_form = unicodedata.normalize('NFD', text.strip().lower())

    cleaned_str = ''.join(x for x in nfd_form if x in string.ascii_letters or x == ' ')

    return remove_tags(cleaned_str).lower()


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()

    return re.sub(r'[-\s]+', '-', value)


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
            filepath = os.environ['PROCESSING_SETTINGS_FILE']
        except KeyError:
            raise ValueError('missing env variable PROCESSING_SETTINGS_FILE')

        return cls.from_file(filepath)

    @classmethod
    def from_file(cls, filepath):
        """
        Returns an instance of Configuration

        ``filepath`` is a text string.
        """
        with open(filepath, 'r') as fp:
            return cls(fp)

    def __getattr__(self, attr):
        return getattr(self.conf, attr)

    def items(self):
        """Settings as key-value pair.
        """
        return [(section, dict(self.conf.items(section, raw=True))) for \
            section in [section for section in self.conf.sections()]]


def get_settings():
    settings = {'app:main': {}}

    filepath = os.environ.get('PROCESSING_SETTINGS_FILE')
    if filepath:
        settings.update(dict(Configuration.from_file(filepath).items()))

    for env_name, setting_name in ENV_SETTINGS.items():
        value = os.environ.get(env_name)
        if value is not None:
            settings['app:main'][setting_name] = value

    if not settings['app:main']:
        raise ValueError(
            'missing PROCESSING_SETTINGS_FILE or service environment variables'
        )

    return settings


def get_metadata_value(obj, attr, default=''):
    try:
        return getattr(obj, attr)
    except (AttributeError, IndexError, KeyError):
        return default


def get_service_setting(settings, name, aliases=None):
    aliases = aliases or []
    app_settings = settings['app:main']
    for key in [name] + aliases:
        value = app_settings.get(key)
        if value:
            return value
    raise ValueError('missing required setting: %s' % name)


def publicationstats_server():
    from thrift import clients

    settings = get_settings()
    server = get_service_setting(settings, 'publicationstats_thriftserver')
    return clients.PublicationStats(server)


def citedby_server():
    from thrift import clients

    settings = get_settings()
    server = get_service_setting(settings, 'citedby_thriftserver')
    return clients.Citedby(domain=server)


def ratchet_server():
    from thrift import clients

    settings = get_settings()
    server = get_service_setting(settings, 'ratchet_thriftserver').split(':')
    host = server[0]
    port = int(server[1])
    return clients.Ratchet(host, port)


def articlemeta_server():
    from thrift import clients

    settings = get_settings()
    server = get_service_setting(settings, 'articlemeta_thriftserver')
    admintoken = settings['app:main'].get('articlemeta_admintoken', None)
    return clients.ArticleMeta(domain=server, admintoken=admintoken)


def accessstats_server():
    from thrift import clients

    settings = get_settings()
    server = get_service_setting(
        settings,
        'accessstats_thriftserver',
        aliases=['accessesstats_thriftserver']
    )
    return clients.AccessStats(server)


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
