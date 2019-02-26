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

import datetime
import doctest
import os
import re
import unittest

import manuel.doctest
import manuel.footnote
import manuel.testing
import zope.testing.renormalizing

from zc.zservertracelog.fseek import FSeekTest  # noqa
from zc.zservertracelog.tracereport import seconds_difference


here = os.path.dirname(os.path.abspath(__file__))

optionflags = (
    doctest.NORMALIZE_WHITESPACE
    | doctest.ELLIPSIS
    | doctest.REPORT_ONLY_FIRST_FAILURE
)

checker = zope.testing.renormalizing.RENormalizing([
    # normalize the channel id and iso8601 timestamp
    (re.compile(r'-?\d+ \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}'),
        '23418928 2008-08-26 10:55:00.000000'),
    (re.compile(r'^usage: '), 'Usage: '),
    (re.compile(r'options:'), 'Options:'),
])


def _null_app(environ, start_response):
    pass


class FauxApplication(object):
    """Fake WSGI application.  Doesn't need to do much!"""

    app_hook = None

    def __call__(self, environ, start_response):
        app = self.app_hook or _null_app
        return app(environ, start_response)


class TestHelpers(unittest.TestCase):

    def test_seconds_difference(self):
        dt1 = datetime.datetime(2019, 2, 23, 14, 5, 54, 451)
        dt2 = dt1 + datetime.timedelta(minutes=15, seconds=3, microseconds=42)
        self.assertEqual(seconds_difference(dt2, dt1), 15 * 60 + 3 + 0.000042)


def setUp(test):
    test.globs['FauxApplication'] = FauxApplication


def analysis_setUp(test):
    test.globs['sample_log'] = here + '/samples/trace.log'


def test_suite():
    m = manuel.doctest.Manuel(
        optionflags=optionflags,
        checker=checker,
    )
    m += manuel.footnote.Manuel()
    return unittest.TestSuite([
        manuel.testing.TestSuite(m, 'README.rst', setUp=setUp),
        doctest.DocFileTest(
            'tracereport.rst',
            checker=checker,
            setUp=analysis_setUp),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ])
