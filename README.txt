=======================
Zope 3/ZServer tracelog
=======================

This package implements a Zope2-style (extended) tracelog.  A tracelog
is a kind of access log that records several low-level events for each
request.  Each log entry starts with a record type, a request
identifier and the time.  Some log records have additional data.

To create a trace log, you need to:

- Include the zc.zservertracelog configuration in your site zcml file::

    <include package="zc.zservertracelog" />

- Define where messages to the 'zc.tracelog' logger should go. In your
  zope.conf file, use something like::

    <logger>
      name zc.tracelog
      propagate false

      <logfile>
        format %(message)s
        path /home/jim/p/zc.zservertracelog/dev/trace.log
      </logfile>

    </logger>


The analysis script, tracereport, can be used to analyze the trace
log. I recommend the html output option.

Trace log records
=================

- Request begins:

  B -1214390740 2007-04-27T20:16:55.582940 GET /

  Includes the request method and path.

- Got request input:

  I -1214390740 2007-04-27T20:16:55.605791 0

  Includes the request content length.

- Entered application thread:

  C -1214390740 2007-04-27T20:16:55.703829

- Database activity


  D -1223774356 2007-04-27T20:16:55.890371 42 0 x 2 1

  The data includes objects loaded and saved for each database except
  databases for which there was no activity.  Note that it's common
  for the main database to be unnamed, and the data often starts with
  objects loaded and saved for the main database.

  In the example above, 42 objects were loaded from the unnamed
  database. Two objects were loaded from and one saved to the database
  named 'x'.

  If requests are retried due to conflict errors, then there will be
  multiple 'D' records.

- Application done:

  A -1223774356 2007-04-27T20:16:55.890371 500 84

  Includes the response content length.

- Request done:

  E -1223774356 2007-04-27T20:16:55.913855

In addition, application startup is logged with an 'S' record:

  S 0 2007-04-27T20:24:29.013922

Tracelog extension records are prefixed with a '-':

  - -1223774356 2008-09-12T15:51:05.559302 zc.example.extension message
