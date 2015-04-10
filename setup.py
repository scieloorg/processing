#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'thriftpy>=0.2.0',
    'xylose>=0.5b'
]

tests_require = []

setup(
    name="processing-scielo",
    version="0.1",
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
    ],
    dependency_links=[
        "git+ssh://git@github.com/scieloorg/xylose.git#egg=xylose"
    ],
    tests_require=tests_require,
    test_suite='tests',
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    processing_accesses_dumpdata=accesses.dumpdata:main
    """
)
