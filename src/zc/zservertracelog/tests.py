##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""tracelog tests
"""
__docformat__ = "reStructuredText"

from zope.testing import doctest
import os
import re
import unittest
import zope.testing.renormalizing

from zc.zservertracelog.fseek import FSeekTest

here = os.path.dirname(os.path.abspath(__file__))

checker = zope.testing.renormalizing.RENormalizing([
    # normalize the channel id and iso8601 timestamp
    (re.compile(r'-?\d+ \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}'),
        '23418928 2008-08-26 10:55:00.000000'),
    (re.compile(r'^usage: '), 'Usage: '),
    (re.compile(r'options:'), 'Options:'),
    ])

_null_app = lambda environ, start_response: ""


class FauxApplication(object):
    """Fake WSGI application.  Doesn't need to do much!"""

    app_hook = None

    def __call__(self, environ, start_response):
        app = self.app_hook or _null_app
        return app(environ, start_response)


def setUp(test):
    test.globs['FauxApplication'] = FauxApplication


def analysis_setUp(test):
    test.globs['sample_log'] = here + '/samples/trace.log'


def test_suite():
    tests = [
        doctest.DocFileTest(
            'README.txt',
            optionflags=(
                doctest.NORMALIZE_WHITESPACE
                | doctest.ELLIPSIS
                | doctest.INTERPRET_FOOTNOTES),
            checker=checker,
            setUp=setUp,
            ),
        doctest.DocFileTest(
            'tracereport.txt',
            checker=checker,
            setUp=analysis_setUp),
        unittest.makeSuite(FSeekTest),
    ]

    return unittest.TestSuite(tests)
