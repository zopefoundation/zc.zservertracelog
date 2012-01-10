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
compatibility.

    >>> logger = logging.getLogger('zc.tracelog')
    >>> logger.setLevel(logging.INFO)
    >>> logger.addHandler(stdout_handler)


Server Startup
==============

There is an event handler to log when the Z server starts.

    >>> zc.zservertracelog.tracelog.started(
    ...     zope.app.appsetup.interfaces.ProcessStarting())
    S 0 2008-08-26 11:55:00.000000


Tracing Applications
====================

The tracelog machinery is primarily implemented as an extension to the
zope.server WSGI server.  To test the tracelog machinery, we'll create
our own application.

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
    B 23423600 2008-08-27 10:54:08.000000 GET /test-req1
    I 23423600 2008-08-27 10:54:08.000000 0
    C 23423600 2008-08-27 10:54:08.000000
    A 23423600 2008-08-27 10:54:08.000000 200 ?
    E 23423600 2008-08-27 10:54:08.000000

Here we get records for each stage in the request:

B
   The request began

I
   Input was read.

C
   An application thread began processing the request.

A
   The response was computed.

E
   The request ended.

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
    B 21663984 2008-09-02 11:19:26.000000 GET /test-req1
    I 21663984 2008-09-02 11:19:26.000000 0
    C 21663984 2008-09-02 11:19:26.000000
    A 21663984 2008-09-02 11:19:26.000000 Error: oh noes!
    E 21663984 2008-09-02 11:19:26.000000


Response Errors
===============

The tracelog also handles errors that can be generated when writing to the
response.  To show this, we'll set up our test application to return a
response that produces an error when written to.

    >>> def response_of_wrong_type(*args, **kwargs):
    ...     def f():
    ...         if 0:
    ...             yield 1
    ...         raise ValueError("sample error")
    ...     return f()
    >>> faux_app.app_hook = response_of_wrong_type

Invoking the request produces log entries for every trace point, and the
error is written to the *Request End (E)* trace entry.

    >>> try:
    ...     invokeRequest(req1)
    ... except:
    ...     pass
    B 21651664 2008-09-02 13:59:02.000000 GET /test-req1
    I 21651664 2008-09-02 13:59:02.000000 0
    C 21651664 2008-09-02 13:59:02.000000
    A 21651664 2008-09-02 13:59:02.000000 200 ?
    E 21651664 2008-09-02 13:59:02.000000 Error: sample error

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
    B 21598352 2008-09-12 11:40:27.000000 GET /test-req2/\nohnoes/
    I 21598352 2008-09-12 11:40:27.000000 0
    C 21598352 2008-09-12 11:40:27.000000
    A 21598352 2008-09-12 11:40:27.000000 200 ?
    E 21598352 2008-09-12 11:40:27.000000


Request Query Strings
=====================

The tracelog preserves request query strings.

    >>> req3 = """\
    ... GET /test-req3/?creature=unicorn HTTP/1.1
    ... Host: www.example.com/query-string
    ...
    ... """

    >>> invokeRequest(req3)
    B 21598352 2008-09-12 11:40:27.000000 GET /test-req3/?creature=unicorn
    I 21598352 2008-09-12 11:40:27.000000 0
    C 21598352 2008-09-12 11:40:27.000000
    A 21598352 2008-09-12 11:40:27.000000 200 ?
    E 21598352 2008-09-12 11:40:27.000000


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
    B 21569456 2008-09-12 15:51:05.000000 GET /test-req1
    I 21569456 2008-09-12 15:51:05.000000 0
    C 21569456 2008-09-12 15:51:05.000000
    - 21569456 2008-09-12 15:51:05.000000 beep! beep!
    A 21569456 2008-09-12 15:51:05.000000 200 ?
    E 21569456 2008-09-12 15:51:05.000000


Database statistics
===================

zc.zservertracelog provides event subscribers that gather statistics
about database usage in a request.  It assumes that requests have
'ZODB.interfaces.IConnection' annotations that are ZODB database
connections. To demonstrate how this works, we'll create a number of
stubs:

    >>> class Connection:
    ...     reads = writes = 0
    ...     db = lambda self: self
    ...     getTransferCounts = lambda self: (self.reads, self.writes)
    ...     def __init__(self, environ, *names):
    ...         self.get = environ.get
    ...         self.databases = names
    ...         self._connections = dict((name, Connection(environ))
    ...                                  for name in names)
    ...         self.get_connection = self._connections.get
    ...     request = property(lambda self: self)
    ...     @property
    ...     def annotations(self):
    ...         return {'ZODB.interfaces.IConnection': self}
    ...     def update(self, name, reads=0, writes=0):
    ...         c = self._connections[name]
    ...         c.reads, c.writes = reads, writes

The Connection stub is kind of heinous. :) It actually stubs out
zope.app.publisher request events, requests, connections, and
databases.

We simulate a request that calls the traversal hooks a couple of
times, does some database activity and redoes requests due to conflicts.

    >>> def dbapp1(environ, start_response):
    ...     conn = Connection(environ, '', 'x', 'y')
    ...     conn.update('', 1, 1)
    ...     conn.update('x', 2, 2)
    ...     zc.zservertracelog.tracelog.before_traverse(conn)
    ...     conn.update('', 3, 1)
    ...     zc.zservertracelog.tracelog.before_traverse(conn)
    ...     conn.update('', 5, 3)
    ...     conn.update('y', 1, 0)
    ...     zc.zservertracelog.tracelog.request_ended(conn)
    ...     zc.zservertracelog.tracelog.before_traverse(conn)
    ...     conn.update('', 6, 3)
    ...     zc.zservertracelog.tracelog.before_traverse(conn)
    ...     conn.update('', 7, 4)
    ...     conn.update('y', 3, 0)
    ...     zc.zservertracelog.tracelog.request_ended(conn)

    >>> faux_app.app_hook = dbapp1

    >>> invokeRequest(req1)
    B 49234448 2010-04-07 17:03:41.229648 GET /test-req1
    I 49234448 2010-04-07 17:03:41.229811 0
    C 49234448 2010-04-07 17:03:41.229943
    D 49234448 2010-04-07 17:03:41.230131 4 2 y 1 0
    D 49234448 2010-04-07 17:03:41.230264 2 1 y 2 0
    A 49234448 2010-04-07 17:03:41.230364 200 ?
    E 23418928 2008-08-26 10:55:00.000000

Here we got multiple D records due to (simulated) conflicts. We show
database activity for those databases for which there was any. The
databases are sorted by name, with the unnamed database coming first.
For each database, the number of object's loaded and saved are
provided.

Since not all requests necessarily have a ZODB connection in their annotations
(consider, e.g. ``GET /++etc++process``), let's make sure this works too

    >>> class Request:
    ...     def __init__(self, environ):
    ...         self.get = environ.get
    ...         self.annotations = {}
    ...     # let this stub pretend to be a RequestEvent too
    ...     request = property(lambda self: self)

    >>> def dbapp2(environ, start_response):
    ...     req = Request(environ)
    ...     zc.zservertracelog.tracelog.before_traverse(req)
    ...     zc.zservertracelog.tracelog.before_traverse(req)
    ...     zc.zservertracelog.tracelog.request_ended(req)

    >>> faux_app.app_hook = dbapp2

    >>> invokeRequest(req1)
    B 146419788 2012-01-10 03:10:05.501841 GET /test-req1
    I 146419788 2012-01-10 03:10:05.502148 0
    C 146419788 2012-01-10 03:10:05.502370
    A 146419788 2012-01-10 03:10:05.502579 200 ?
    E 146419788 2012-01-10 03:10:05.502782

