# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import sys
import dash
import logging
#from io import StringIO


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


class DashLoggerHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.queue = []

    def emit(self, record):
        msg = self.format(record)
        self.queue.append(msg)


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename="out.log",
    filemode='a',
    #stream=sys.stdout,
)
logger = logging.getLogger('aaa')
dashLoggerHandler = DashLoggerHandler()
logger.addHandler(dashLoggerHandler)

#sys.stdout = StreamToLogger(logger, logging.INFO)
#sys.stderr = StreamToLogger(logger, logging.ERROR)
#
# logging.StreamHandler(sys.stdout)
# logging.StreamHandler(sys.stderr)


external_stylesheets = [{
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
                update_title=None)
server = app.server
