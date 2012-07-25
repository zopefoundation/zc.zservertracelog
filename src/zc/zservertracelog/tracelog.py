##############################################################################
#
# Copyright (c) 2005, 2008 Zope Foundation and Contributors.
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
"""Crude Tracelog Hack for ZServer
"""
from zope.app.server import servertype
from zope.app.wsgi import WSGIPublisherApplication
from zope.server.http import wsgihttpserver
from zope.server.http.commonaccesslogger import CommonAccessLogger

# Gaaaa, these have moved:
try:
    from zope.publisher.interfaces import BeforeTraverseEvent
    from zope.publisher.interfaces import EndRequestEvent
except ImportError:
    from zope.app.publication.interfaces import BeforeTraverseEvent
    from zope.app.publication.interfaces import EndRequestEvent


import datetime
import logging
import re
import zc.zservertracelog.interfaces
import zope.app.appsetup.interfaces
import zope.component
import zope.app.publication.interfaces
import zope.server.http.httprequestparser
import zope.server.http.httpserverchannel

tracelog = logging.getLogger('zc.tracelog')


def _log(channel_id, trace_code='-', msg=None, timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now()

    entry = '%s %s %s' % (trace_code, channel_id, timestamp)

    if msg:
        entry += ' %s' % repr(msg)[1:-1]

    tracelog.info(entry)


@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zc.zservertracelog.interfaces.ITraceLog)
def get(request):
    return request['zc.zservertracelog.interfaces.ITraceLog']


class TraceLog(object):
    zope.interface.implements(zc.zservertracelog.interfaces.ITraceLog)

    def __init__(self, channel_id):
        self.channel_id = channel_id

    def log(self, msg=None, code='-'):
        _log(self.channel_id, code, msg)


class Parser(zope.server.http.httprequestparser.HTTPRequestParser):

    def __init__(self, x):
        self._Channel__B = datetime.datetime.now()
        zope.server.http.httprequestparser.HTTPRequestParser.__init__(self, x)


class Channel(zope.server.http.httpserverchannel.HTTPServerChannel):
    parser_class = Parser

    def handle_request(self, parser):
        full_path = parser.path
        # If parser.query == '' we want full_path with a trailing '?'
        if parser.query is not None:
            full_path += '?%s' % parser.query

        cid = id(self)
        _log(cid, 'B', '%s %s' % (parser.command, full_path), parser.__B)
        _log(cid, 'I', str(parser.content_length))

        zope.server.http.httpserverchannel.HTTPServerChannel.handle_request(
            self, parser)


status_match = re.compile('(\d+) (.*)').match
class Server(wsgihttpserver.WSGIHTTPServer):

    channel_class = Channel

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

    def executeRequest(self, task):
        """Overrides HTTPServer.executeRequest()."""
        cid = id(task.channel)
        _log(cid, 'C')
        env = self._constructWSGIEnvironment(task)
        env['zc.zservertracelog.interfaces.ITraceLog'] = TraceLog(cid)
        if 'wsgi.logging_info' in env:
            task.setAuthUserName(env['wsgi.logging_info'])

        # Call the application to handle the request and write a response
        try:
            response = self.application(
                env, wsgihttpserver.curriedStartResponse(task))
        except Exception, v:
            _log(cid, 'A', 'Error: %s' % v)
            _log(cid, 'E')
            raise
        else:
            accumulated_headers = getattr(task, 'accumulated_headers') or ()
            length = [h.split(': ')[1].strip()
                      for h in accumulated_headers
                      if h.lower().startswith('content-length: ')]
            if length:
                length = length[0]
            else:
                length = '?'

            _log(cid, 'A', '%s %s' % (getattr(task, 'status', '?'), length))

            try:
                for value in response:
                    task.write(value)
            except Exception, v:
                _log(cid, 'E', 'Error: %s' % v)
                raise
            else:
                _log(cid, 'E')


http = servertype.ServerType(
    Server,
    WSGIPublisherApplication,
    CommonAccessLogger,
    8080, True)


pmhttp = servertype.ServerType(
    wsgihttpserver.PMDBWSGIHTTPServer,
    WSGIPublisherApplication,
    CommonAccessLogger,
    8013, True)


@zope.component.adapter(zope.app.appsetup.interfaces.IProcessStartingEvent)
def started(event):
    tracelog.info('S 0 %s', datetime.datetime.now())

@zope.component.adapter(BeforeTraverseEvent)
def before_traverse(event):
    request = event.request
    tl = request.get('zc.zservertracelog.interfaces.ITraceLog')
    if tl is None:
        return
    if getattr(tl, 'transfer_counts', None) is None:
        connection = request.annotations.get('ZODB.interfaces.IConnection')
        # Not all requests have a ZODB connection; consider /++etc++process
        if connection is None:
            return
        tl.transfer_counts = dict(
            (name, connection.get_connection(name).getTransferCounts())
            for name in connection.db().databases)

@zope.component.adapter(EndRequestEvent)
def request_ended(event):
    request = event.request
    tl = request.get('zc.zservertracelog.interfaces.ITraceLog')
    if tl is None:
        return
    initial_counts = getattr(tl, 'transfer_counts', None)
    if not initial_counts:
        return
    tl.transfer_counts = None           # Reset in case of conflict
    connection = request.annotations.get('ZODB.interfaces.IConnection')
    if connection is None:
        return
    data = []
    for name in connection.db().databases:
        conn = connection.get_connection(name)
        r, w = conn.getTransferCounts()
        ir, iw = initial_counts[name]
        r -= ir
        w -= iw
        if r or w:
            data.append((name, r, w))
    msg = ' '.join(' '.join(map(str, r)) for r in sorted(data))
    tl.log(msg.strip(), 'D')
