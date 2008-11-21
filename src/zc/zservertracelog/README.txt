================
ZServer TraceLog
================

A tracelog is a kind of access log that records several low-level events for
each request.  Each log entry starts with a record type, a request identifier
and the time.  Some log records have additional data.

    >>> import zc.zservertracelog.tracelog
    >>> import zope.app.appsetup.interfaces

For these examples, we'll add a log handler that outputs to standard out.

    >>> import logging
    >>> import sys
    >>> stdout_handler = logging.StreamHandler(sys.stdout)

The logger's name is not the package name, but "zc.tracelog" for backward
compatability.

    >>> logger = logging.getLogger('zc.tracelog')
    >>> logger.setLevel(logging.INFO)
    >>> logger.addHandler(stdout_handler)


Server Startup
==============

There is an event handler to log when the Z server starts.

    >>> zc.zservertracelog.tracelog.started(
    ...     zope.app.appsetup.interfaces.ProcessStarting())
    S 0 2008-08-26T11:55:00


Tracing Applications
====================

The tracelog machinery is implemented as a WSGI layer, so we'll pass a fake
WSGI application to tracelog for these examples.

    >>> faux_app = FauxApplication()

Now, let's create an instance of the tracelog server.

    >>> addr, port = '127.0.0.1', 12345

    >>> trace_server = zc.zservertracelog.tracelog.Server(
    ...     faux_app, None, addr, port)

Let's also define a convenience function for processing requests.

    >>> def invokeRequest(req):
    ...     channel = trace_server.channel_class(trace_server, None, addr)
    ...     channel.received(req)

Process a simple request.

    >>> req1 = """\
    ... GET /test-req1 HTTP/1.1
    ... Host: www.example.com
    ...
    ... """

    >>> invokeRequest(req1)
    B 23423600 2008-08-27T10:54:08 GET /test-req1
    I 23423600 2008-08-27T10:54:08 0
    C 23423600 2008-08-27T10:54:08
    A 23423600 2008-08-27T10:54:08 200 ?
    E 23423600 2008-08-27T10:54:08


Application Errors
==================

The tracelog will also log application errors.  To show this, we'll set up
our test application to raise an error when called.

    >>> def app_failure(*args, **kwargs):
    ...     raise Exception('oh noes!')
    >>> faux_app.app_hook = app_failure

Invoking the request produces log entries for every trace point, and the
application error is written to the *Application End (A)* trace entry.

    >>> try:
    ...     invokeRequest(req1)
    ... except:
    ...     pass
    B 21663984 2008-09-02T11:19:26 GET /test-req1
    I 21663984 2008-09-02T11:19:26 0
    C 21663984 2008-09-02T11:19:26
    A 21663984 2008-09-02T11:19:26 Error: oh noes!
    E 21663984 2008-09-02T11:19:26


Response Errors
===============

The tracelog also handles errors that can be generated when writing to the
response.  To show this, we'll set up our test application to return a
response that produces an error when written to.

    >>> def response_of_wrong_type(*args, **kwargs):
    ...     return object()
    >>> faux_app.app_hook = response_of_wrong_type

Invoking the request produces log entries for every trace point, and the
error is written to the *Request End (E)* trace entry.

    >>> try:
    ...     invokeRequest(req1)
    ... except:
    ...     pass
    B 21651664 2008-09-02T13:59:02 GET /test-req1
    I 21651664 2008-09-02T13:59:02 0
    C 21651664 2008-09-02T13:59:02
    A 21651664 2008-09-02T13:59:02 200 ?
    E 21651664 2008-09-02T13:59:02 Error: iteration over non-sequence

Let's clean up before moving on.

    >>> faux_app.app_hook = None


Log Messages Containing Line Breaks
===================================

Messages to the tracelog that contain newline characters will not split a log
entry into multiple lines.

    >>> req2 = """\
    ... GET /test-req2/%0Aohnoes/ HTTP/1.1
    ... Host: www.example.com/linebreak
    ...
    ... """

    >>> invokeRequest(req2)
    B 21598352 2008-09-12T11:40:27 GET /test-req2/\nohnoes/
    I 21598352 2008-09-12T11:40:27 0
    C 21598352 2008-09-12T11:40:27
    A 21598352 2008-09-12T11:40:27 200 ?
    E 21598352 2008-09-12T11:40:27


Request Query Strings
=====================

The tracelog preserves request query strings.

    >>> req3 = """\
    ... GET /test-req3/?creature=unicorn HTTP/1.1
    ... Host: www.example.com/query-string
    ...
    ... """

    >>> invokeRequest(req3)
    B 21598352 2008-09-12T11:40:27 GET /test-req3/?creature=unicorn
    I 21598352 2008-09-12T11:40:27 0
    C 21598352 2008-09-12T11:40:27
    A 21598352 2008-09-12T11:40:27 200 ?
    E 21598352 2008-09-12T11:40:27

Empty query strings are also preserved.

    >>> req4 = """\
    ... GET /test-req4/? HTTP/1.1
    ... Host: www.example.com/empty-query-string
    ...
    ... """

    >>> invokeRequest(req4)
    B 21598352 2008-09-12T11:40:27 GET /test-req4/?
    I 21598352 2008-09-12T11:40:27 0
    C 21598352 2008-09-12T11:40:27
    A 21598352 2008-09-12T11:40:27 200 ?
    E 21598352 2008-09-12T11:40:27


Adding Additional Entries to the Trace Log
==========================================

A tracelog object is added to the WSGI environment on each request.  This
object implements ``ITraceLog`` and provides applications a method to add
custom entries to the log.

Here is an example application that adds a custom entry to the tracelog.

    >>> def noisy_app(environ, start_response):
    ...     logger = environ['zc.zservertracelog.interfaces.ITraceLog']
    ...     logger.log('beep! beep!')
    >>> faux_app.app_hook = noisy_app

    >>> invokeRequest(req1)
    B 21569456 2008-09-12T15:51:05 GET /test-req1
    I 21569456 2008-09-12T15:51:05 0
    C 21569456 2008-09-12T15:51:05
    - 21569456 2008-09-12T15:51:05 beep! beep!
    A 21569456 2008-09-12T15:51:05 200 ?
    E 21569456 2008-09-12T15:51:05
