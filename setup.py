#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import pyactors

from setuptools import setup

setup(
    name="pyactors",
    version=pyactors.__version__,
    author=re.sub(r'\s+<.*', r'', open('README.md').read()),
    author_email='ownport@gmail.com',
    url='https://github.com/ownport/pyactors',
    description='Simple implementation actors on python',
    long_description=open('README.md').read(),
    license="BSD",
    keywords="actors",
    packages=['pyactors', 'docs', 'tests', 'pyactors/inbox'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
