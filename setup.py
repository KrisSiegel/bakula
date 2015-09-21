#!/usr/bin/env python

from setuptools import setup

setup(
    name='Bakula',
    version='0.0.1',
    description='Bakula reactive programming engine',
    author='Immuta',
    author_email='soup@immuta.com',
    url='https://github.com/immuta/bakula',
    test_suite='nose.collector',
    tests_require=['nose'],
    setup_requires=['setuptools-pep8']
)
