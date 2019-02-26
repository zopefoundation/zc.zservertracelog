##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
from setuptools import setup, find_packages


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(
    name='zc.zservertracelog',
    version='2.0.0',
    url='https://github.com/zopefoundation/zc.zservertracelog',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    description='Zope 3 tracelog implementation for zserver',
    long_description=(
        read('README.rst')
        + '\n\n'
        + read('CHANGES.rst')
    ),
    license='ZPL 2.1',
    keywords='zope3',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    packages=find_packages('src'),
    namespace_packages=['zc'],
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'six',
        'zope.app.appsetup',
        'zope.app.server',
        'zope.app.wsgi',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.server',
    ],
    extras_require=dict(
        test=[
            'manuel',
        ],
    ),
    include_package_data=True,
    zip_safe=False,
    entry_points=dict(
        console_scripts=[
            "tracereport = zc.zservertracelog.tracereport:main",
        ],
    ),
)
