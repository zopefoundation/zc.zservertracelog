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
"""tracelog interfaces
"""
__docformat__ = "reStructuredText"

import zope.interface


class ITraceLog(zope.interface.Interface):
    """Logs records from writers."""

    def log(msg=None, timestamp=None):
        """Write a message to the trace log."""


class ITracer(zope.interface.Interface):
    """Enters trace points."""

    def __call__(logger, trace_point):
        """Record an entry in the trace log."""


class ITraceRequestStart(ITracer):
    """Enters the *Request Start* trace point."""


class ITraceInputAcquired(ITracer):
    """Enters the *Request Input Acquired* trace point."""


class ITraceApplicationStart(ITracer):
    """Enters the *Application Start* trace point."""


class ITraceApplicationEnd(ITracer):
    """Enters the *Application End* trace point."""


class ITraceRequestEnd(ITracer):
    """Enters the *Request End* trace point."""
