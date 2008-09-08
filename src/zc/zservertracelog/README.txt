==================
 ZServer TraceLog
==================

A tracelog is a kind of access log that records several low-level events for
each request.  Each log entry starts with a record type, a request identifier
and the time.  Some log records have additional data.

    >>> import zc.zservertracelog.tracelog
    >>> import zope.app.appsetup.interfaces

For these examples, we'll add a log handler that outputs to standard out.

    >>> import logging
    >>> import sys
    >>> stdout_handler = logging.StreamHandler(sys.stdout)

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


Tracelog Extensions
===================

Additional information can be written to the trace log through the use of
extensions.  Extensions can be registered as named-utilities for any of the
trace points mentioned above.

    >>> import zc.zservertracelog.interfaces
    >>> import zope.component
    >>> import zope.interface

    >>> site_manager = zope.component.getSiteManager()

Extensions implement one or more of the sub-interfaces of ``ITracer``.  Here,
we'll define a simple extension that just logs how many times it's been
called.

    >>> class CountTracer(object):
    ...
    ...     count = 0
    ...
    ...     def __call__(self, logger, trace_point):
    ...         self.count += 1
    ...         logger.log('count: %s' % self.count)


    >>> count_tracer = CountTracer()
    >>> site_manager.registerUtility(
    ...     count_tracer,
    ...     zc.zservertracelog.interfaces.ITraceRequestStart,
    ...     'example.Tracer')

Extensions appear in the log with the *X* prefix immediately after any trace
point they are registered for.

    >>> invokeRequest(req1)
    B 17954544 2008-09-05T09:47:00 GET /test-req1
    X 17954544 2008-09-05T09:47:00 example.Tracer count: 1
    I 17954544 2008-09-05T09:47:00 0
    C 17954544 2008-09-05T09:47:00
    A 17954544 2008-09-05T09:47:00 200 ?
    E 17954544 2008-09-05T09:47:00

Unnamed extension registrations are not allowed and will result in a
`ValueError` if present during execution.

    >>> site_manager.registerUtility(
    ...     count_tracer, zc.zservertracelog.interfaces.ITraceRequestStart)

    >>> invokeRequest(req1)
    Traceback (most recent call last):
    ...
    ValueError: Unnamed Tracelog Extension

To fix the problem, we'll just remove the extension.  Since extensions are
just utilities, removing an extension is accomplished simply by unregistering
it.

    >>> site_manager.unregisterUtility(
    ...     count_tracer, zc.zservertracelog.interfaces.ITraceRequestStart)
    True

    >>> invokeRequest(req1)
    B 21714736 2008-09-05T13:45:44 GET /test-req1
    X 23418928 2008-08-26T10:55:00 example.Tracer count: 3
    I 21714736 2008-09-05T13:45:44 0
    C 21714736 2008-09-05T13:45:44
    A 21714736 2008-09-05T13:45:44 200 ?
    E 21714736 2008-09-05T13:45:44

So far, we've only added extensions for the *Request Start* trace point, and
adding extensions for other trace points is done in almost the exact same
way.  The only difference is the interface which an extension is registered
for.

Here, we'll register the tracer component in the previous examples for the
other trace points.

    >>> site_manager.registerUtility(
    ...     count_tracer,
    ...     zc.zservertracelog.interfaces.ITraceInputAcquired,
    ...     'example.Tracer')

    >>> site_manager.registerUtility(
    ...     count_tracer,
    ...     zc.zservertracelog.interfaces.ITraceApplicationStart,
    ...     'example.Tracer')

    >>> site_manager.registerUtility(
    ...     count_tracer,
    ...     zc.zservertracelog.interfaces.ITraceApplicationEnd,
    ...     'example.Tracer')

    >>> site_manager.registerUtility(
    ...     count_tracer,
    ...     zc.zservertracelog.interfaces.ITraceRequestEnd,
    ...     'example.Tracer')

Now, that extension is fired at every trace point.

    >>> invokeRequest(req1)
    B 21930320 2008-09-05T15:53:47 GET /test-req1
    X 21930320 2008-09-05T15:53:47 example.Tracer count: 4
    I 21930320 2008-09-05T15:53:47 0
    X 21930320 2008-09-05T15:53:47 example.Tracer count: 5
    C 21930320 2008-09-05T15:53:47
    X 21930320 2008-09-05T15:53:47 example.Tracer count: 6
    A 21930320 2008-09-05T15:53:47 200 ?
    X 21930320 2008-09-05T15:53:47 example.Tracer count: 7
    E 21930320 2008-09-05T15:53:47
    X 21930320 2008-09-05T15:53:47 example.Tracer count: 8


Overriding Extensions
---------------------

One extension can be overriden with another just by registering the new
extension with the same name.

Let's add a new extension to demonstrate this.

    >>> class StreetLightTracer(object):
    ...
    ...     light = 0
    ...     colors = ['green', 'yellow', 'red']
    ...
    ...     def __call__(self, logger, trace_point):
    ...         self.light = self.light + 1 % 3
    ...         logger.log('color: %s' % self.colors[self.light])

    >>> street_light_tracer = StreetLightTracer()

    >>> site_manager.registerUtility(
    ...     street_light_tracer,
    ...     zc.zservertracelog.interfaces.ITraceRequestStart,
    ...     'example.Tracer')

Now, we see output from the new extension.

    >>> invokeRequest(req1)
    B 23418928 2008-08-26T10:55:00 GET /test-req1
    X 23418928 2008-08-26T10:55:00 example.Tracer color: yellow
    I 23418928 2008-08-26T10:55:00 0
    X 23418928 2008-08-26T10:55:00 example.Tracer count: 9
    C 23418928 2008-08-26T10:55:00
    X 23418928 2008-08-26T10:55:00 example.Tracer count: 10
    A 23418928 2008-08-26T10:55:00 200 ?
    X 23418928 2008-08-26T10:55:00 example.Tracer count: 11
    E 23418928 2008-08-26T10:55:00
    X 23418928 2008-08-26T10:55:00 example.Tracer count: 12
