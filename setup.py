#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'thriftpy==0.3.1',
    'packtools',
    'requests>=2.11.1',
    'lxml>=3.4.4',
    'doaj_client',
    'scieloh5m5>=1.5.4',
    'xylose>=1.16.5',
    'articlemetaapi>=1.5.10',
    'citedbyapi>=1.3.7'
]

tests_require = []

setup(
    name="processing",
    version="1.11.5",
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
        "git+https://github.com/fabiobatalha/doaj_client@0.2#egg=doaj_client"
    ],
    tests_require=tests_require,
    test_suite='tests',
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    processing_accesses_dumpdata=accesses.dumpdata:main
    processing_accesses_documents_by_journals=accesses.documents_by_journals:main
    processing_publication_documents_languages=publication.documents_languages:main
    processing_publication_documents_affiliations=publication.documents_affiliations:main
    processing_publication_documents_authors=publication.documents_authors:main
    processing_publication_documents_counts=publication.documents_counts:main
    processing_publication_documents_licenses=publication.documents_licenses:main
    processing_publication_documents_dates=publication.documents_dates:main
    processing_publication_journals=publication.journals:main
    processing_publication_journals_status_changes=publication.journals_status_changes:main
    processing_publication_journals_indicators=publication.journals_indicators:main
    processing_publication_all=publication.dumper:main
    processing_evaluation_altmetrics=evaluation.altmetrics:main
    processing_export_xmlrsps=export.xml_rsps:main
    processing_export_normalize_affiliations=export.normalize_affiliations:main
    processing_export_natural_keys=export.natural_keys:main
    processing_export_doaj=export.exdoaj:main
    processing_export_doaj_journals=export.doaj_journals:main
    processing_export_kbart=export.kbart:main
    processing_export_search_update_indicators=export.search_update_indicators:main
    processing_bibliometric_citedby_document=bibliometric.citedby_document:main
    processing_bibliometric_citedby_journal=bibliometric.citedby_journal:main
    processing_bibliometric_impact_factor=bibliometric.impact_factor:main
    """
)
