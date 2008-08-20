##############################################################################
#
# Copyright (c) 2005, 2008 Zope Corporation and Contributors.
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
import datetime, re, logging

import zope.component

from zope.server.http.commonaccesslogger import CommonAccessLogger
from zope.server.http import wsgihttpserver
import zope.server.http.httprequestparser

import zope.server.http.httpserverchannel
from zope.app.server import servertype

from zope.app.wsgi import WSGIPublisherApplication

import zope.app.appsetup.interfaces

logger = logging.getLogger('zc.tracelog')

def now():
    return datetime.datetime.now().replace(microsecond=0).isoformat()

class Parser(zope.server.http.httprequestparser.HTTPRequestParser):

    def __init__(self, x):
        self._Channel__B = now()
        zope.server.http.httprequestparser.HTTPRequestParser.__init__(self, x)

class Channel(zope.server.http.httpserverchannel.HTTPServerChannel):
    parser_class = Parser

    def handle_request(self, parser):
        logger.info("B %s %s %s %s", id(self), parser.__B,
                    parser.command, parser.path)
        logger.info("I %s %s %s", id(self), now(),
                    parser.content_length)
        zope.server.http.httpserverchannel.HTTPServerChannel.handle_request(
            self, parser)


status_match = re.compile('(\d+) (.*)').match
class Server(wsgihttpserver.WSGIHTTPServer):

    channel_class = Channel
    
    def executeRequest(self, task):
        """Overrides HTTPServer.executeRequest()."""
        logger.info("C %s %s", id(task.channel), now())
        env = task.getCGIEnvironment()
        env['wsgi.input'] = task.request_data.getBodyStream()

        def start_response(status, headers):
            # Prepare the headers for output
            status, reason = status_match(status).groups()
            task.setResponseStatus(status, reason)
            task.appendResponseHeaders(['%s: %s' % i for i in headers])

            # Return the write method used to write the response data.
            return wsgihttpserver.fakeWrite

        # Call the application to handle the request and write a response
        try:
            response = self.application(env, start_response)
        except Exception, v:
            logger.info("A %s %s Error: %s", id(task.channel), now(), v)
            logger.info("E %s %s", id(task.channel), now())
            raise
        else:
            length = [h.split(': ')[1].strip()
                      for h in getattr(task, 'accumulated_headers', ())
                      if h.lower().startswith('content-length: ')]
            if length:
                length = length[0]
            else:
                length = '?'
            logger.info("A %s %s %s %s", id(task.channel), now(),
                        getattr(task, 'status', '?'), length)
            try:
                task.write(response)
            except Exception, v:
                logger.info("E %s %s Error: %s", id(task.channel), now(), v)
                raise
            else:
                logger.info("E %s %s", id(task.channel), now())

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
    logger.info("S 0 %s", now())
