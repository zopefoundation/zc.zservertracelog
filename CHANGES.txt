Changes
=======

1.3.2 (2012-03-20)
------------------

- Slight refactoring to allow alternative tracelog implementations.

1.3.1 (2012-03-20)
------------------

- Fix KeyError: 'ZODB.interfaces.IConnection' on requests that do not have
  a ZODB connection in annotations (e.g. GET /++etc++process).


1.3.0 (2010-04-08)
------------------

- Added 'D' records providing database transfer counts.
  This is somewhat experimental. The tracereport script ignores D
  records.

1.2.1 (2010-01-27)
------------------

- fix reST headings so PyPI page renders properly
- add a warning about the strange logger name


1.2.0 (2009-08-31)
------------------

- tracereport improvements:
  - fix parsing bugs.
  - add basic tests.
  - report time with microsecond resolution.


1.1.5 (2009-04-01)
------------------

- new key for user name in environ (refactoring in zope.app.wsgi)


1.1.4 (2009-03-25)
------------------

- put user names in access log


1.1.3 (2009-03-25)
------------------

- sub-second resolution in timestamps


1.1.1 (2008-11-21)
------------------

- switch back to logger name zc.tracelog to maintain backward compatibility.


1.1.0 (2008-10-31)
------------------

- fixed tracelog extension format so that it doesn't conflict with the Zope2
  trace code for server shutdown.

- added *summary-only* and *summary-lines* options to tracereport.

- added shading of alternating rows in tracereport table output.

- fixed a documentation error for loghandler configuration.


0.4 (2008-10-09)
----------------

- added automated tests.

- fixed bug where log entries could be split by messages containing newline
  characters.

- added request query strings to log.

- added the tracelog to the WSGI environment.
