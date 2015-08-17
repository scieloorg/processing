#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'thriftpy==0.3.1',
    'xylose',
    'packtools'
]

tests_require = []

setup(
    name="processing",
    version ="0.1.20",
    description="SciELO processing modules for analytics, access statistics, etc",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    maintainer="Fabio Batalha",
    maintainer_email="fabio.batalha@scielo.org",
    url="http://github.com/scieloorg/processing",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
    ],
    dependency_links=[
        "git+https://git@github.com/scieloorg/xylose.git@v0.30#egg=xylose"
    ],
    tests_require=tests_require,
    test_suite='tests',
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    processing_accesses_dumpdata=accesses.dumpdata:main
    processing_publication_languages=publication.languages:main
    processing_publication_affiliations=publication.affiliations:main
    processing_publication_authors=publication.authors:main
    processing_publication_counts=publication.counts:main
    processing_publication_journals=publication.journals:main
    processing_publication_licenses=publication.licenses:main
    processing_publication_all=publication.dumper:main
    processing_export_xmlrsps=export.xml_rsps:main
    processing_export_normalize_affiliations=export.normalize_affiliations:main
    processing_export_natural_keys=export.natural_keys:main
    processing_export_doaj=export.doaj:main
    """
)
