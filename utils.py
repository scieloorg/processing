#coding: utf-8
import os
import weakref

from configparser import ConfigParser


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

        self.conf.read_file(fp)

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