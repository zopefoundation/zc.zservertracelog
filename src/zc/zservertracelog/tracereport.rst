===================
Analyzing Tracelogs
===================

`tracereport.py` provides a basic means to analyze a tracelog and generate a
report.

    >>> import os
    >>> os.environ['COLUMNS'] = '70'
    >>> import zc.zservertracelog.tracereport
    >>> import sys
    >>> sys.argv[0] = 'tracereport'

The '--help' option displays the following usage information:

    >>> try:
    ...     zc.zservertracelog.tracereport.main(['--help'])
    ... except SystemExit:
    ...     pass
    ... # doctest: +REPORT_NDIFF, +NORMALIZE_WHITESPACE
    Usage: tracereport [options] trace_log_file
    <BLANKLINE>
    Output trace log data showing:
    <BLANKLINE>
    - number of active requests,
    - number of input requests (requests gathering input),
    - number of application requests,
    - number of output requests,
    - number of requests completed in the minute shown,
    - mean seconds per request and
    - mean application seconds per request.
    <BLANKLINE>
    Note that we don't seem to be logging when a connection to the client
    is broken, so the number of active requests, and especially the number
    of outputing requests tends to grow over time. This is spurious.
    <BLANKLINE>
    Also, note that, unfortunately, application requests include requests
    that are running in application threads and requests waiting to get an
    application thread.
    <BLANKLINE>
    When application threads get above the app request threshold, then we
    show the requests that have been waiting the longest.
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    Options:
      -h, --help            show this help message and exit
      -a APPS, --app-request-threshold=APPS
                            Number of pending application requests at
                            which detailed request information if
                            printed.
      -r APP_REQUESTS, --app-requests=APP_REQUESTS
                            How many requests to show when the maximum
                            number of pending apps is exceeded.
      -o OLD_REQUESTS, --old-requests=OLD_REQUESTS
                            Number of seconds beyond which a request is
                            considered old.
      -e EVENT_LOG, --event-log=EVENT_LOG
                            The name of an event log that goes with the
                            trace log.  This is used to determine when
                            the server is restarted, so that the running
                            trace data structures can be reinitialized.
      --html                Generate HTML output.
      --remove-prefix=REMOVE_PREFIX
                            A prefix to be removed from URLS.
      --summary-only        Only output summary lines.
      --summary-lines=SUMMARY_LINES
                            The number of summary lines to show
      -d DATESPEC, --date=DATESPEC
                            Only consider events in the specified date
                            range.  Syntax: "YYYY-MM[-DD
                            [HH[:MM[:SS]]]][ +/-[days=N][, hours=N][,
                            minutes=N][, seconds=N]]".  E.g. -d 2015-04
                            would select the entire month, -d 2015-04-20
                            would select the entire day, -d "2015-04-20
                            14" would select one hour, -d "2015-04-20
                            14:00 +hours=2" would select two hours, and
                            -d "2015-04-20 16:00 -hours=2" would select
                            the same two hours.

Here, we display the summarized report for a sample trace log.

    >>> zc.zservertracelog.tracereport.main(
    ...     ['--summary-only', '--app-request-threshold', '0', sample_log])
    <BLANKLINE>
    URL statistics:
       Impact count    min median   mean    max hangs
    ========= ===== ====== ====== ====== ====== =====
         62.4     1  62.42  62.42  62.42  62.42     0 /constellations/andromeda.html
         61.5     1  61.50  61.50  61.50  61.50     0 /stars/alpha-centauri.html
         60.3     2   0.13  30.13  30.13  60.13     0 /favicon.png
         60.0     2   0.00  30.00  30.00  60.00     0 /space-travel/plans/supplies.txt
          9.7     1   9.69   9.69   9.69   9.69     0 /planets/saturn.html
          8.3     1   8.30   8.30   8.30   8.30     0 /moons/io.html
          7.3     1   7.34   7.34   7.34   7.34     0 /planets/jupiter.html
          0.9     1   0.88   0.88   0.88   0.88     0 /stories/aliens-posing-as-humans.html
          0.6     1   0.64   0.64   0.64   0.64     0 /columns/t-jansen
          0.4     2   0.18   0.19   0.19   0.19     0 /faqs/how-to-recognize-lazer-fire.html
          0.4     1   0.35   0.35   0.35   0.35     0 /faqs/how-to-charge-lazers.html
          0.3     1   0.32   0.32   0.32   0.32     0 /space-travel/ships/tardis.html
          0.3     1   0.25   0.25   0.25   0.25     0 /approve-photo
          0.2     1   0.18   0.18   0.18   0.18     0 /ufo-sightings/report
          0.1     1   0.14   0.14   0.14   0.14     0 /space-travel/ships/soyuz.html
          0.0     3   0.02   0.02   0.02   0.02     0 /space-travelers/famous/kirk.jpg
          0.0     1   0.02   0.02   0.02   0.02     0 /space-travelers/famous/spock.jpg
          0.0     1   0.02   0.02   0.02   0.02     0 /login
          0.0     3   0.00   0.00   0.00   0.00     0 /space-travel/plans/signals.html
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/launchpad.html
          0.0     1   0.00   0.00   0.00   0.00     1 /space-travel/plans/orbit.html
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-logs.txt
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/moon-base.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/moon-buggy.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-diary.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /js/photo.js
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/visor.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/lunar-cycles.html
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/cryostasis.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-suit.jpg
                  0                                 1 /submit-photo

This can also be displayed as HTML.

    >>> zc.zservertracelog.tracereport.main(
    ...     ['--summary-only', '--html', '--app-request-threshold', '0', sample_log])
    <html title="trace log statistics"><body>
    <BLANKLINE>
    URL statistics:
    <table border="1">
    <tr><th>Impact</th><th>count</th><th>min</th>
    <th>median</th><th>mean</th><th>max</th><th>hangs</th></tr>
    <tr>
    <td><a name="u37">62.4</a></td><td>1</td><td>62.418</td><td>62.418</td><td>62.418</td><td>62.418</td><td>0</td>
    <td>/constellations/andromeda.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u53">61.5</a></td><td>1</td><td>61.502</td><td>61.502</td><td>61.502</td><td>61.502</td><td>0</td>
    <td>/stars/alpha-centauri.html</td>
    </tr>
    <tr>
    <td><a name="u44">60.3</a></td><td>2</td><td>0.133</td><td>30.134</td><td>30.134</td><td>60.134</td><td>0</td>
    <td>/favicon.png</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u34">60.0</a></td><td>2</td><td>0.003</td><td>30.003</td><td>30.003</td><td>60.003</td><td>0</td>
    <td>/space-travel/plans/supplies.txt</td>
    </tr>
    <tr>
    <td><a name="u48">9.7</a></td><td>1</td><td>9.694</td><td>9.694</td><td>9.694</td><td>9.694</td><td>0</td>
    <td>/planets/saturn.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u51">8.3</a></td><td>1</td><td>8.300</td><td>8.300</td><td>8.300</td><td>8.300</td><td>0</td>
    <td>/moons/io.html</td>
    </tr>
    <tr>
    <td><a name="u55">7.3</a></td><td>1</td><td>7.340</td><td>7.340</td><td>7.340</td><td>7.340</td><td>0</td>
    <td>/planets/jupiter.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u60">0.9</a></td><td>1</td><td>0.880</td><td>0.880</td><td>0.880</td><td>0.880</td><td>0</td>
    <td>/stories/aliens-posing-as-humans.html</td>
    </tr>
    <tr>
    <td><a name="u33">0.6</a></td><td>1</td><td>0.638</td><td>0.638</td><td>0.638</td><td>0.638</td><td>0</td>
    <td>/columns/t-jansen</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u41">0.4</a></td><td>2</td><td>0.184</td><td>0.187</td><td>0.187</td><td>0.190</td><td>0</td>
    <td>/faqs/how-to-recognize-lazer-fire.html</td>
    </tr>
    <tr>
    <td><a name="u54">0.4</a></td><td>1</td><td>0.351</td><td>0.351</td><td>0.351</td><td>0.351</td><td>0</td>
    <td>/faqs/how-to-charge-lazers.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u50">0.3</a></td><td>1</td><td>0.320</td><td>0.320</td><td>0.320</td><td>0.320</td><td>0</td>
    <td>/space-travel/ships/tardis.html</td>
    </tr>
    <tr>
    <td><a name="u39">0.3</a></td><td>1</td><td>0.253</td><td>0.253</td><td>0.253</td><td>0.253</td><td>0</td>
    <td>/approve-photo</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u57">0.2</a></td><td>1</td><td>0.182</td><td>0.182</td><td>0.182</td><td>0.182</td><td>0</td>
    <td>/ufo-sightings/report</td>
    </tr>
    <tr>
    <td><a name="u61">0.1</a></td><td>1</td><td>0.138</td><td>0.138</td><td>0.138</td><td>0.138</td><td>0</td>
    <td>/space-travel/ships/soyuz.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u45">0.0</a></td><td>3</td><td>0.015</td><td>0.016</td><td>0.016</td><td>0.018</td><td>0</td>
    <td>/space-travelers/famous/kirk.jpg</td>
    </tr>
    <tr>
    <td><a name="u59">0.0</a></td><td>1</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0</td>
    <td>/space-travelers/famous/spock.jpg</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u43">0.0</a></td><td>1</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0</td>
    <td>/login</td>
    </tr>
    <tr>
    <td><a name="u56">0.0</a></td><td>3</td><td>0.003</td><td>0.004</td><td>0.003</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/signals.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u36">0.0</a></td><td>2</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/launchpad.html</td>
    </tr>
    <tr>
    <td><a name="u62">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>1</td>
    <td>/space-travel/plans/orbit.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u38">0.0</a></td><td>2</td><td>0.003</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/space-logs.txt</td>
    </tr>
    <tr>
    <td><a name="u35">0.0</a></td><td>2</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/moon-base.jpg</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u46">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/moon-buggy.jpg</td>
    </tr>
    <tr>
    <td><a name="u49">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/space-diary.txt</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u58">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/js/photo.js</td>
    </tr>
    <tr>
    <td><a name="u63">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/visor.jpg</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u52">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/lunar-cycles.html</td>
    </tr>
    <tr>
    <td><a name="u40">0.0</a></td><td>1</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0</td>
    <td>/space-travel/plans/cryostasis.txt</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u47">0.0</a></td><td>1</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0</td>
    <td>/space-travel/plans/space-suit.jpg</td>
    </tr>
    <tr>
    <td><a name="u42">&nbsp;</a></td><td>0</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>1</td>
    <td>/submit-photo</td>
    </tr>
    </table>
    </body></html>

The full report shows the request activity per minute.

    >>> zc.zservertracelog.tracereport.main(
    ...     ['--app-request-threshold', '0', sample_log])
    <BLANKLINE>
              minute   req input  wait   app output
    ================ ===== ===== ===== ===== ======
    2009-07-30 15:47     1 I=  0 W=  0 A=  1 O=   0 N=   1       0.64       0.64
    60.004106 /space-travel/plans/supplies.txt
    2009-07-30 15:48     2 I=  0 W=  1 A=  1 O=   0 N=   3      20.00      20.00
    60.791825 /constellations/andromeda.html
    2009-07-30 15:49     0 I=  0 W=  0 A=  0 O=   0 N=   4      31.69      15.67
    2009-07-30 15:50     2 I=  0 W=  0 A=  2 O=   0 N=   2       0.34       0.10
    60.62335 /submit-photo
    60.209388 /favicon.png
    2009-07-30 15:51     3 I=  0 W=  1 A=  1 O=   1 N=   5      12.08      12.07
    121.301024 /submit-photo
    2009-07-30 15:52     3 I=  0 W=  1 A=  2 O=   0 N=   8      20.45       2.29
    200.494494 /submit-photo
    68.09801 /stars/alpha-centauri.html
    2009-07-30 15:53     3 I=  0 W=  2 A=  1 O=   0 N=  11      14.39       6.39
    270.622261 /submit-photo
    Left over:
    271.214443 /submit-photo
    <BLANKLINE>
    <BLANKLINE>
    URL statistics:
       Impact count    min median   mean    max hangs
    ========= ===== ====== ====== ====== ====== =====
         62.4     1  62.42  62.42  62.42  62.42     0 /constellations/andromeda.html
         61.5     1  61.50  61.50  61.50  61.50     0 /stars/alpha-centauri.html
         60.3     2   0.13  30.13  30.13  60.13     0 /favicon.png
         60.0     2   0.00  30.00  30.00  60.00     0 /space-travel/plans/supplies.txt
          9.7     1   9.69   9.69   9.69   9.69     0 /planets/saturn.html
          8.3     1   8.30   8.30   8.30   8.30     0 /moons/io.html
          7.3     1   7.34   7.34   7.34   7.34     0 /planets/jupiter.html
          0.9     1   0.88   0.88   0.88   0.88     0 /stories/aliens-posing-as-humans.html
          0.6     1   0.64   0.64   0.64   0.64     0 /columns/t-jansen
          0.4     2   0.18   0.19   0.19   0.19     0 /faqs/how-to-recognize-lazer-fire.html
          0.4     1   0.35   0.35   0.35   0.35     0 /faqs/how-to-charge-lazers.html
          0.3     1   0.32   0.32   0.32   0.32     0 /space-travel/ships/tardis.html
          0.3     1   0.25   0.25   0.25   0.25     0 /approve-photo
          0.2     1   0.18   0.18   0.18   0.18     0 /ufo-sightings/report
          0.1     1   0.14   0.14   0.14   0.14     0 /space-travel/ships/soyuz.html
          0.0     3   0.02   0.02   0.02   0.02     0 /space-travelers/famous/kirk.jpg
          0.0     1   0.02   0.02   0.02   0.02     0 /space-travelers/famous/spock.jpg
          0.0     1   0.02   0.02   0.02   0.02     0 /login
          0.0     3   0.00   0.00   0.00   0.00     0 /space-travel/plans/signals.html
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/launchpad.html
          0.0     1   0.00   0.00   0.00   0.00     1 /space-travel/plans/orbit.html
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-logs.txt
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/moon-base.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/moon-buggy.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-diary.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /js/photo.js
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/visor.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/lunar-cycles.html
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/cryostasis.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-suit.jpg
                  0                                 1 /submit-photo

Again, this report is also available in HTML form.

    >>> zc.zservertracelog.tracereport.main(
    ...     ['--html', '--app-request-threshold', '0', sample_log])
    <html title="trace log statistics"><body>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    <tr style="background: lightgrey">
    <td>2009-07-30 15:47</td><td>1</td><td>0</td><td>0</td><td><font size="+2"><strong>1</strong></font></td><td>0</td>
    <td>1</td><td>      0.64</td><td>      0.64</td>
    </tr>
    </table>
    <table border="1">
    <tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>
    <tr>
    <td>60</td><td></td><td><a href="#u96">/space-travel/plans/supplies.txt</a></td><td>app</td>
    </tr>
    </table>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    <tr>
    <td>2009-07-30 15:48</td><td>2</td><td>0</td><td>1</td><td><font size="+2"><strong>1</strong></font></td><td>0</td>
    <td>3</td><td>     20.00</td><td>     20.00</td>
    </tr>
    </table>
    <table border="1">
    <tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>
    <tr>
    <td>60</td><td></td><td><a href="#u99">/constellations/andromeda.html</a></td><td>app</td>
    </tr>
    </table>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    <tr style="background: lightgrey">
    <td>2009-07-30 15:49</td><td>0</td><td>0</td><td>0</td><td><font size="+2"><strong>0</strong></font></td><td>0</td>
    <td>4</td><td>     31.69</td><td>     15.67</td>
    </tr>
    <tr>
    <td>2009-07-30 15:50</td><td>2</td><td>0</td><td>0</td><td><font size="+2"><strong>2</strong></font></td><td>0</td>
    <td>2</td><td>      0.34</td><td>      0.10</td>
    </tr>
    </table>
    <table border="1">
    <tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>
    <tr>
    <td>60</td><td></td><td><a href="#u104">/submit-photo</a></td><td>app</td>
    </tr>
    <tr>
    <td>60</td><td></td><td><a href="#u106">/favicon.png</a></td><td>app</td>
    </tr>
    </table>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    <tr style="background: lightgrey">
    <td>2009-07-30 15:51</td><td>3</td><td>0</td><td>1</td><td><font size="+2"><strong>1</strong></font></td><td>1</td>
    <td>5</td><td>     12.08</td><td>     12.07</td>
    </tr>
    </table>
    <table border="1">
    <tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>
    <tr>
    <td>121</td><td></td><td><a href="#u104">/submit-photo</a></td><td>app</td>
    </tr>
    </table>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    <tr>
    <td>2009-07-30 15:52</td><td>3</td><td>0</td><td>1</td><td><font size="+2"><strong>2</strong></font></td><td>0</td>
    <td>8</td><td>     20.45</td><td>      2.29</td>
    </tr>
    </table>
    <table border="1">
    <tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>
    <tr>
    <td>200</td><td></td><td><a href="#u104">/submit-photo</a></td><td>app</td>
    </tr>
    <tr>
    <td>68</td><td></td><td><a href="#u115">/stars/alpha-centauri.html</a></td><td>app</td>
    </tr>
    </table>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    <tr style="background: lightgrey">
    <td>2009-07-30 15:53</td><td>3</td><td>0</td><td>2</td><td><font size="+2"><strong>1</strong></font></td><td>0</td>
    <td>11</td><td>     14.39</td><td>      6.39</td>
    </tr>
    </table>
    <table border="1">
    <tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>
    <tr>
    <td>270</td><td></td><td><a href="#u104">/submit-photo</a></td><td>app</td>
    </tr>
    </table>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    Left over:
    </table>
    <table border="1">
    <tr><th>age</th><th>R</th><th>url</th><th>state</th></tr>
    <tr>
    <td>271</td><td></td><td><a href="#u104">/submit-photo</a></td><td>app</td>
    </tr>
    </table>
    <table border="2">
    <tr>
    <th>Minute</th>
    <th>Requests</th>
    <th>Requests inputing</th>
    <th>Requests waiting</th>
    <th>Requests executing</th>
    <th>Requests outputing</th>
    <th>Requests completed</th>
    <th>Mean Seconds Per Request Total</th>
    <th>Mean Seconds Per Request in App</th>
    </tr>
    </table>
    <BLANKLINE>
    URL statistics:
    <table border="1">
    <tr><th>Impact</th><th>count</th><th>min</th>
    <th>median</th><th>mean</th><th>max</th><th>hangs</th></tr>
    <tr>
    <td><a name="u99">62.4</a></td><td>1</td><td>62.418</td><td>62.418</td><td>62.418</td><td>62.418</td><td>0</td>
    <td>/constellations/andromeda.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u115">61.5</a></td><td>1</td><td>61.502</td><td>61.502</td><td>61.502</td><td>61.502</td><td>0</td>
    <td>/stars/alpha-centauri.html</td>
    </tr>
    <tr>
    <td><a name="u106">60.3</a></td><td>2</td><td>0.133</td><td>30.134</td><td>30.134</td><td>60.134</td><td>0</td>
    <td>/favicon.png</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u96">60.0</a></td><td>2</td><td>0.003</td><td>30.003</td><td>30.003</td><td>60.003</td><td>0</td>
    <td>/space-travel/plans/supplies.txt</td>
    </tr>
    <tr>
    <td><a name="u110">9.7</a></td><td>1</td><td>9.694</td><td>9.694</td><td>9.694</td><td>9.694</td><td>0</td>
    <td>/planets/saturn.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u113">8.3</a></td><td>1</td><td>8.300</td><td>8.300</td><td>8.300</td><td>8.300</td><td>0</td>
    <td>/moons/io.html</td>
    </tr>
    <tr>
    <td><a name="u117">7.3</a></td><td>1</td><td>7.340</td><td>7.340</td><td>7.340</td><td>7.340</td><td>0</td>
    <td>/planets/jupiter.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u122">0.9</a></td><td>1</td><td>0.880</td><td>0.880</td><td>0.880</td><td>0.880</td><td>0</td>
    <td>/stories/aliens-posing-as-humans.html</td>
    </tr>
    <tr>
    <td><a name="u95">0.6</a></td><td>1</td><td>0.638</td><td>0.638</td><td>0.638</td><td>0.638</td><td>0</td>
    <td>/columns/t-jansen</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u103">0.4</a></td><td>2</td><td>0.184</td><td>0.187</td><td>0.187</td><td>0.190</td><td>0</td>
    <td>/faqs/how-to-recognize-lazer-fire.html</td>
    </tr>
    <tr>
    <td><a name="u116">0.4</a></td><td>1</td><td>0.351</td><td>0.351</td><td>0.351</td><td>0.351</td><td>0</td>
    <td>/faqs/how-to-charge-lazers.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u112">0.3</a></td><td>1</td><td>0.320</td><td>0.320</td><td>0.320</td><td>0.320</td><td>0</td>
    <td>/space-travel/ships/tardis.html</td>
    </tr>
    <tr>
    <td><a name="u101">0.3</a></td><td>1</td><td>0.253</td><td>0.253</td><td>0.253</td><td>0.253</td><td>0</td>
    <td>/approve-photo</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u119">0.2</a></td><td>1</td><td>0.182</td><td>0.182</td><td>0.182</td><td>0.182</td><td>0</td>
    <td>/ufo-sightings/report</td>
    </tr>
    <tr>
    <td><a name="u123">0.1</a></td><td>1</td><td>0.138</td><td>0.138</td><td>0.138</td><td>0.138</td><td>0</td>
    <td>/space-travel/ships/soyuz.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u107">0.0</a></td><td>3</td><td>0.015</td><td>0.016</td><td>0.016</td><td>0.018</td><td>0</td>
    <td>/space-travelers/famous/kirk.jpg</td>
    </tr>
    <tr>
    <td><a name="u121">0.0</a></td><td>1</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0</td>
    <td>/space-travelers/famous/spock.jpg</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u105">0.0</a></td><td>1</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0.016</td><td>0</td>
    <td>/login</td>
    </tr>
    <tr>
    <td><a name="u118">0.0</a></td><td>3</td><td>0.003</td><td>0.004</td><td>0.003</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/signals.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u98">0.0</a></td><td>2</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/launchpad.html</td>
    </tr>
    <tr>
    <td><a name="u124">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>1</td>
    <td>/space-travel/plans/orbit.html</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u100">0.0</a></td><td>2</td><td>0.003</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/space-logs.txt</td>
    </tr>
    <tr>
    <td><a name="u97">0.0</a></td><td>2</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/moon-base.jpg</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u108">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/moon-buggy.jpg</td>
    </tr>
    <tr>
    <td><a name="u111">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/space-diary.txt</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u120">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/js/photo.js</td>
    </tr>
    <tr>
    <td><a name="u125">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/visor.jpg</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u114">0.0</a></td><td>1</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0.004</td><td>0</td>
    <td>/space-travel/plans/lunar-cycles.html</td>
    </tr>
    <tr>
    <td><a name="u102">0.0</a></td><td>1</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0</td>
    <td>/space-travel/plans/cryostasis.txt</td>
    </tr>
    <tr style="background: lightgrey;">
    <td><a name="u109">0.0</a></td><td>1</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0.003</td><td>0</td>
    <td>/space-travel/plans/space-suit.jpg</td>
    </tr>
    <tr>
    <td><a name="u104">&nbsp;</a></td><td>0</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>1</td>
    <td>/submit-photo</td>
    </tr>
    </table>
    </body></html>

Report by given time interval.

    >>> zc.zservertracelog.tracereport.main(
    ...     ['--date', '2009-07-30 15:48 +minutes=5', sample_log])
    <BLANKLINE>
              minute   req input  wait   app output
    ================ ===== ===== ===== ===== ======
    2009-07-30 15:48     2 I=  0 W=  1 A=  1 O=   0 N=   2       0.00       0.00
    2009-07-30 15:49     0 I=  0 W=  0 A=  0 O=   0 N=   4      31.69      15.67
    2009-07-30 15:50     2 I=  0 W=  0 A=  2 O=   0 N=   2       0.34       0.10
    2009-07-30 15:51     3 I=  0 W=  1 A=  1 O=   1 N=   5      12.08      12.07
    Left over:
    140.094385 /submit-photo
    <BLANKLINE>
    <BLANKLINE>
    URL statistics:
       Impact count    min median   mean    max hangs
    ========= ===== ====== ====== ====== ====== =====
         62.4     1  62.42  62.42  62.42  62.42     0 /constellations/andromeda.html
         60.1     1  60.13  60.13  60.13  60.13     0 /favicon.png
          9.7     1   9.69   9.69   9.69   9.69     0 /planets/saturn.html
          8.3     1   8.30   8.30   8.30   8.30     0 /moons/io.html
          0.4     2   0.18   0.19   0.19   0.19     0 /faqs/how-to-recognize-lazer-fire.html
          0.3     1   0.32   0.32   0.32   0.32     0 /space-travel/ships/tardis.html
          0.3     1   0.25   0.25   0.25   0.25     0 /approve-photo
          0.0     1   0.02   0.02   0.02   0.02     0 /space-travelers/famous/kirk.jpg
          0.0     1   0.02   0.02   0.02   0.02     0 /login
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/launchpad.html
          0.0     2   0.00   0.00   0.00   0.00     0 /space-travel/plans/moon-base.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/moon-buggy.jpg
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-logs.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-diary.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/lunar-cycles.html
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/supplies.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/cryostasis.txt
          0.0     1   0.00   0.00   0.00   0.00     0 /space-travel/plans/space-suit.jpg
                  0                                 1 /submit-photo
                  0                                 1 /stars/alpha-centauri.html
                  0                                 1 /faqs/how-to-charge-lazers.html
