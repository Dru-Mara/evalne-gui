#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021
# Run this app with `python evalne_gui` and
# visit http://127.0.0.1:8050/ in your web browser.

import os
import logging
import webbrowser

from threading import Timer
from evalne_gui import index
from evalne_gui.app import app


# Log only UI errors to stdout
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# Remove the Flask development warning
os.environ.setdefault('FLASK_ENV', 'development')


def open_browser():
    port = 8050
    webbrowser.open_new("http://localhost:{}".format(port))


def main():
    Timer(1, open_browser).start()
    app.run_server(debug=False, port=8050, host='localhost', use_reloader=False)


if __name__ == '__main__':
    main()
