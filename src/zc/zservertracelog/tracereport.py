#!/usr/local/bin/python2.4
##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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
"""Yet another trace log analysis tool
"""
import datetime
import optparse
import sys
import os.path

from zc.zservertracelog.fseek import fseek


# Date format and default offset.
DATE_FORMATS = (
    ('%Y-%m-%d %H:%M:%S', ''),
    ('%Y-%m-%d %H:%M', 'seconds=59'),
    ('%Y-%m-%d %H', 'minutes=59, seconds=59'),
    ('%Y-%m-%d', 'hours=23, minutes=59, seconds=59'),
    ('%Y-%m', 'days=31, hours=23, minutes=59, seconds=59'),
)

OFFSET_VALID_KEYS = ('days', 'minutes', 'seconds')


class Request(object):

    output_bytes = '-'

    def __init__(self, start, method, url):
        self.method = method
        self.url = url
        self.start = start
        self.state = 'input'

    def I(self, input_time, input_bytes):
        self.input_time = input_time
        self.input_bytes = input_bytes
        self.state = 'wait'

    def C(self, start_app_time):
        self.start_app_time = start_app_time
        self.state = 'app'

    def A(self, app_time, response, output_bytes):
        self.app_time = app_time
        self.response = response
        self.output_bytes = output_bytes
        self.state = 'output'

    def E(self, end):
        self.end = end

    @property
    def app_seconds(self):
        return seconds_difference(self.app_time, self.start_app_time)

    @property
    def total_seconds(self):
        return seconds_difference(self.end, self.start)


class Times(object):

    tid = 1l

    def __init__(self):
        self.times = []
        self.hangs = 0
        Times.tid += 1
        self.tid = Times.tid # generate a unique id

    def finished(self, request):
        self.times.append(request.app_seconds)

    def hung(self):
        self.hangs += 1

    def impact(self):
        times = self.times
        if not times:
            self.median = self.mean = self.impact = 0
            return 0
        self.times.sort()
        n = len(times)
        if n % 2:
            m = times[(n+1)/2-1]
        else:
            m = .5 * (times[n/2]+times[n/2-1])
        self.median = m
        self.mean = float(sum(times))/n
        self.impact = self.mean * (n+self.hangs)
        return self.impact

    def __str__(self):
        times = self.times
        if not times:
            return "              0                             %5d" % (
                self.hangs)

        n = len(times)
        m = self.median
        return "%9.1f %5d %6.2f %6.2f %6.2f %6.2f %5d" % (
            self.impact, n, times[0], m, self.mean, times[-1], self.hangs)

    def html(self):
        times = self.times
        if not times:
            impact = '<a name="u%s">&nbsp;</a>' % self.tid
            print td(
                impact, 0, '&nbsp;', '&nbsp;', '&nbsp;', '&nbsp;', self.hangs)
        else:
            impact = '<a name="u%s">%s</a>' % (self.tid, self.impact)
            n = len(times)
            m = self.median
            print td(impact, n, times[0], m, self.mean, times[-1],
                     self.hangs)

    def __add__(self, other):
        result = Times()
        result.times = self.times + other.times
        result.hangs = self.hangs + other.hangs
        return result


def seconds_difference(dt1, dt2):
    delta = dt1 - dt2
    micros = float('0.' + str(delta.microseconds))
    return delta.seconds + micros


def parse_line(line):
    parts = line.split(' ', 4)
    code, rid, rdate, rtime = parts[:4]
    if len(parts) > 4:
        msg = parts[4]
    else:
        msg = ''
    return (code, rid, rdate + ' ' + rtime, msg)


def parse_datetime(s):
    # XXX this chokes on tracelogs with the 'T' time separator.
    date, t = s.split(' ')
    try:
        h_m_s, ms = t.split('.')
    except ValueError:
        h_m_s = t.strip()
        ms = '0'
    args = [int(arg) for arg in (date.split('-') + h_m_s.split(':') + [ms])]
    return datetime.datetime(*args)


def parse_offset(offset):
    offset = offset.replace(' ', '')
    if offset:
        items = []
        for item in offset.split(','):
            key, val = item.split('=')
            items.append((key, int(val)))
        kwargs = dict(items)
    else:
        kwargs = dict()
    kwargs['microseconds'] = 999999
    return datetime.timedelta(**kwargs)


def parse_date_interval(interval_string):
    # Get offset
    offset = ''
    negative_offset = False
    if ' +' in interval_string:
        date_string, offset = interval_string.split(' +')
    elif ' -' in interval_string:
        date_string, offset = interval_string.split(' -')
        negative_offset = True
    else:
        date_string = interval_string

    # Get datetime
    date = None
    date_string = date_string.strip()
    for date_format, date_format_offset in DATE_FORMATS:
        try:
            date = datetime.datetime.strptime(date_string, date_format)
        except (ValueError, OverflowError):
            pass
        else:
            break
    if date is None:
        raise TypeError("Unknown date format of '%s'." % interval_string)

    # Return datetime interval tuple
    offset = offset or date_format_offset
    offset = parse_offset(offset)
    if negative_offset:
        return (date - offset, date)
    else:
        return (date, date + offset)


def time_from_line(line):
    x, x, strtime, x = parse_line(line)
    return parse_datetime(strtime)


def iterlog(file, date_interval=None):
    size = 0
    if file == '-':
        file = sys.stdin
    else:
        size = os.path.getsize(file)
        file = open(file)

    date_from, date_to = date_interval or (None, None)
    if date_from and size:
        fseek(file, size, date_from, time_from_line)

    for line in file:
        typ, rid, strtime, msg = parse_line(line)
        dt = parse_datetime(strtime)
        if date_to and date_to < dt:
            break
        elif date_from and date_from > dt:
            continue
        else:
            yield line, dt, typ, rid, strtime, msg


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    options, args = parser.parse_args(args)

    if options.date:
        date_interval = parse_date_interval(options.date)
    else:
        date_interval = None

    if options.event_log:
        restarts = find_restarts(options.event_log)
    else:
        restarts = []

    restarts.append(datetime.datetime.utcnow()+datetime.timedelta(1000))

    if options.html:
        print_app_requests = print_app_requests_html
        output_minute = output_minute_html
        output_stats = output_stats_html
        minutes_header = minutes_header_html
        minutes_footer = minutes_footer_html
        print '<html title="trace log statistics"><body>'
    else:
        print_app_requests = print_app_requests_text
        output_minute = output_minute_text
        output_stats = output_stats_text
        minutes_header = minutes_header_text
        minutes_footer = minutes_footer_text

    if options.summary_only:
        print_app_requests = output_minute = lambda *a, **kw: None
        minutes_footer = minutes_header = lambda *a, **kw: None


    urls = {}
    [file] = args
    lmin = ldt = None
    requests = {}
    input = apps = output = n = wait = 0
    spr = spa = 0.0
    restart = restarts.pop(0)
    minutes_header()
    remove_prefix = options.remove_prefix
    dt = None

    for record, dt, typ, rid, strtime, msg in iterlog(file, date_interval):
        min = strtime.split('.')[0]
        min = min[:-3]
        if dt == restart:
            continue
        while dt > restart:
            print_app_requests(requests, ldt,
                               options.old_requests,
                               options.app_requests,
                               urls,
                               "\nLeft over:")
            record_hung(urls, requests)
            requests = {}
            input = apps = output = n = wait = 0
            spr = spa = 0.0
            restart = restarts.pop(0)
        ldt = dt

        if min != lmin:
            if lmin is not None:
                output_minute(lmin, requests, input, wait, apps, output,
                              n, spr, spa)
                if apps > options.apps:
                    print_app_requests(requests, dt,
                                       options.old_requests,
                                       options.app_requests,
                                       urls,
                                       )
            lmin = min
            spr = 0.0
            spa = 0.0
            n = 0

        if typ == 'B':
            if rid in requests:
                request = requests[rid]
                if request.state == 'output':
                    output -= 1
                elif request.state == 'app':
                    apps -= 1
                else:
                    input -= 1

            input += 1
            method, url = msg.split(' ', 1)
            request = Request(dt, method, url.strip())
            if remove_prefix and request.url.startswith(remove_prefix):
                request.url = request.url[len(remove_prefix):]
            requests[rid] = request
            times = urls.get(request.url)
            if times is None:
                times = urls[request.url] = Times()
        elif typ == 'I':
            if rid in requests:
                input -= 1
                wait += 1
                requests[rid].I(dt, record[3])
        elif typ == 'C':
            if rid in requests:
                wait -= 1
                apps += 1
                requests[rid].C(dt)
        elif typ == 'A':
            if rid in requests:
                apps -= 1
                output += 1
                try:
                    response_code, bytes_len = msg.split()
                except ValueError:
                    response_code = '500'
                    bytes_len = len(msg)
                requests[rid].A(dt, response_code, bytes_len)
        elif typ == 'E':
            if rid in requests:
                output -= 1
                request = requests.pop(rid)
                request.E(dt)
                spr += request.total_seconds
                spa += request.app_seconds
                n += 1
                times = urls[request.url]
                times.finished(request)

        elif typ in 'SX':
            print_app_requests(requests, ldt,
                               options.old_requests,
                               options.app_requests,
                               urls,
                               "\nLeft over:")
            record_hung(urls, requests)
            requests = {}
            input = apps = output = n = wait = 0
            spr = spa = 0.0
        elif typ == 'D':
            pass # ignore db stats for now
        else:
            print 'WTF', record

    record_hung(urls, requests)
    if dt:
        print_app_requests(requests, dt,
                           options.old_requests,
                           options.app_requests,
                           urls,
                           "Left over:")

    minutes_footer()

    output_stats(urls, lines=options.summary_lines)

    if options.html:
        print '</body></html>'

def output_stats_text(urls, lines):
    print
    print 'URL statistics:'
    print "   Impact count    min median   mean    max hangs"
    print "========= ===== ====== ====== ====== ====== ====="
    urls = [(times.impact(), url, times)
            for (url, times) in urls.iteritems()
            ]
    urls.sort()
    urls.reverse()
    line = 0
    for (_, url, times) in urls:
        if times.impact > 0 or times.hangs:
            print times, url
            line += 1
            if line > lines:
                break

def output_stats_html(urls, lines):
    print
    print 'URL statistics:'
    print '<table border="1">'
    print '<tr><th>Impact</th><th>count</th><th>min</th>'
    print     '<th>median</th><th>mean</th><th>max</th><th>hangs</th></tr>'
    urls = [(times.impact(), url, times)
            for (url, times) in urls.iteritems()
            ]
    urls.sort()
    urls.reverse()
    line = 0
    for (_, url, times) in urls:
        if times.impact > 0 or times.hangs:
            if line%2:
                print '<tr style="background: lightgrey;">'
            else:
                print '<tr>'
            times.html()
            print td(url)
            print '</tr>'
            line += 1
            if line > lines:
                break
    print '</table>'

def minutes_header_text():
    print
    print "          minute   req input  wait   app output"
    print "================ ===== ===== ===== ===== ======"

def minutes_footer_text():
    print

def minutes_header_html():
    print '<table border="2">'
    print "<tr>"
    print '<th>Minute</th>'
    print '<th>Requests</th>'
    print '<th>Requests inputing</th>'
    print '<th>Requests waiting</th>'
    print '<th>Requests executing</th>'
    print '<th>Requests outputing</th>'
    print '<th>Requests completed</th>'
    print '<th>Mean Seconds Per Request Total</th>'
    print '<th>Mean Seconds Per Request in App</th>'
    print "</tr>"

def minutes_footer_html():
    print '</table>'

def output_minute_text(lmin, requests, input, wait, apps, output, n, spr, spa):
    print lmin, "%5d I=%3d W=%3d A=%3d O=%4d" % (
        len(requests), input, wait, apps, output),
    if n:
        print "N=%4d %10.2f %10.2f" % (n, spr/n, spa/n)
    else:
        print

def td(*values):
    return ''.join([("<td>%s</td>" % s) for s in values])

output_minute_count = 0
def output_minute_html(lmin, requests, input, wait, apps, output, n, spr, spa):
    global output_minute_count
    output_minute_count += 1
    if output_minute_count%2:
        print '<tr style="background: lightgrey">'
    else:
        print '<tr>'
    apps = '<font size="+2"><strong>%s</strong></font>' % apps
    print td(lmin, len(requests), input, wait, apps, output)
    if n:
        print td(n, "%10.2f" % (spr/n), "%10.2f" % (spa/n))
    else:
        print td(n, '&nbsp;', '&nbsp;')
    print '</tr>'

def find_restarts(event_log):
    result = []
    for l in open(event_log):
        if l.strip().endswith("Zope Ready to handle requests"):
            result.append(parsedt(l.split()[0]))
    return result

def record_hung(urls, requests):
    for request in requests.itervalues():
        times = urls.get(request.url)
        if times is None:
            times = urls[request.url] = Times()
        times.hung()

def print_app_requests_text(requests, dt, min_seconds, max_requests, allurls,
                       label=''):
    requests = [
        (seconds_difference(dt, request.start), request)
        for request in requests.values()
        if request.state == 'app'
    ]

    urls = {}
    for s, request in requests:
        urls[request.url] = urls.get(request.url, 0) + 1

    requests.sort()
    requests.reverse()
    for s, request in requests[:max_requests]:
        if s < min_seconds:
            continue
        if label:
            print label
            label = ''
        url = request.url
        repeat = urls[url]
        if repeat > 1:
            print s, "R=%d" % repeat, url
        else:
            print s, url

def print_app_requests_html(requests, dt, min_seconds, max_requests, allurls,
                            label=''):
    requests = [
        ((dt-request.start).seconds, request.url, request)
        for request in requests.values()
        if request.state == 'app'
    ]

    urls = {}
    for s, url, request in requests:
        urls[url] = urls.get(url, 0) + 1

    requests.sort()
    requests.reverse()
    printed = False
    for s, url, request in requests[:max_requests]:
        if s < min_seconds:
            continue
        if label:
            print label
            label = ''
        if not printed:
            print '</table>'
            print '<table border="1">'
            print '<tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>'
            printed = True
        repeat = urls[url]
        print '<tr>'
        if repeat <= 1:
            repeat = ''
        url = '<a href="#u%s">%s</a>' % (allurls[url].tid, url)
        print td(s, repeat, url, request.state)
        print '</tr>'

    if printed:
        print '</table>'
        minutes_header_html()

parser = optparse.OptionParser("""%prog [options] trace_log_file

Output trace log data showing:

- number of active requests,
- number of input requests (requests gathering input),
- number of application requests,
- number of output requests,
- number of requests completed in the minute shown,
- mean seconds per request and
- mean application seconds per request.

Note that we don't seem to be logging when a connection to the client
is broken, so the number of active requests, and especially the number
of outputing requests tends to grow over time. This is spurious.

Also, note that, unfortunately, application requests include requests
that are running in application threads and requests waiting to get an
application thread.

When application threads get above the app request threshold, then we
show the requests that have been waiting the longest.

""")

parser.add_option("--app-request-threshold", "-a", dest='apps',
                  type="int", default=10,
                  help="""
Number of pending application requests at which detailed request information
if printed.
""")
parser.add_option("--app-requests", "-r", dest='app_requests',
                  type="int", default=10,
                  help="""
How many requests to show when the maximum number of pending
apps is exceeded.
""")
parser.add_option("--old-requests", "-o", dest='old_requests',
                  type="int", default=10,
                  help="""
Number of seconds beyond which a request is considered old.
""")
parser.add_option("--event-log", "-e", dest='event_log',
                  help="""
The name of an event log that goes with the trace log.  This is used
to determine when the server is restarted, so that the running trace data structures can be reinitialized.
""")
parser.add_option("--html", dest='html', action='store_true',
                  help="""
Generate HTML output.
""")
parser.add_option("--remove-prefix", dest='remove_prefix',
                  help="""
A prefex to be removed from URLS.
""")
parser.add_option("--summary-only", dest='summary_only', action='store_true',
                  help="""
Only output summary lines.
""")
parser.add_option("--summary-lines", dest='summary_lines',
                  type="int", default=999999999,
                  help="""The number of summary lines to show""")
parser.add_option("--date", "-d", dest='date', default=None,
                  help="""Date range that will be parsed from log""")



if __name__ == '__main__':
    main()
