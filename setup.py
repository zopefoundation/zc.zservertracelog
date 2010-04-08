##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

name = 'zc.zservertracelog'

entry_points = """
[console_scripts]
tracereport = zc.zservertracelog.tracereport:main
"""

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version='1.3.0',
    url='http://pypi.python.org/pypi/' + name,
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    description='Zope 3 tracelog implementation for zserver',
    long_description=(
        read('README.txt')
        + '\n\n'
        + '\n\n'
        + read('CHANGES.txt')
    ),
    license='ZPL 2.1',
    keywords='zope3',
    packages=find_packages('src'),
    namespace_packages=['zc'],
    package_dir={'': 'src'},
    install_requires=[
            'setuptools',
            'zope.app.appsetup',
            'zope.app.server',
            'zope.app.wsgi',
            'zope.server',
            ],
    extras_require=dict(
        test=[
            'zope.testing',
            ]),
    include_package_data=True,
    zip_safe=False,
    entry_points=entry_points,
    )
