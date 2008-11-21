=======================
Zope 3/ZServer tracelog
=======================

This package implements a Zope2-style (extended) tracelog.  A tracelog
is a kind of access log that records several low-level events for each
request.  Each log entry starts with a record type, a request
identifier and the time.  Some log records have additional data.


Trace Codes
===========

- Request begins:

  B -1214390740 2007-04-27T20:16:55 GET /

  Includes the request method and path.

- Got request input:

  I -1214390740 2007-04-27T20:16:55 0

  Includes the request content length.

- Entered application thread:

  C -1214390740 2007-04-27T20:16:55

- Application done:

  A -1223774356 2007-04-27T20:16:55 500 84

  Includes the response content length.

- Request done:

  E -1223774356 2007-04-27T20:16:55

In addition, application startup is logged with an 'S' record:

  S 0 2007-04-27T20:24:29

Tracelog extension records are prefixed with a '-':

  - -1223774356 2008-09-12T15:51:05 zc.example.extension message

To create a trace log, include the zc.zservertracelog package in your
site ZCML configuration.  Also, define a logger section in zope.conf::

  <logger>
    name zc.zservertracelog
    propagate false

    <logfile>
      format %(message)s
      path /home/jim/p/zc.zservertracelog/dev/trace.log
    </logfile>

  </logger>

Where, of course, you'll need to specify a log file path.

The analysis script, tracereport, can be used to analyze the trace
log. I recommend the html output option.
