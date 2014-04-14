""" This module brings together various web-based components of CSDS """

from __future__ import unicode_literals, print_function

import os
from os.path import abspath, dirname, join
import sys

PROJECT_DIR = abspath(dirname(dirname(__file__)))
TEMPLATE_DIR = join(PROJECT_DIR, 'templates')
VENDOR_DIR = join(PROJECT_DIR, 'vendor')
ENV = os.environ.get('ENV', 'Development')

sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, VENDOR_DIR)

from flask import Flask, url_for
from utils.routes import register_module
from utils.middlewares import csrf

# App instance
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config.from_object('app.conf.%s' % ENV)

# Middlewares and request-response processors
csrf(app, excluded_paths=['/rh/hooks/email'])

# Web interface handlers
register_module(app, 'cds.webui')
register_module(app, 'css.webui')
register_module(app, 'rqm.webui')

# Cron job handlers
register_module(app, 'ra.outernet_facebook')

# Web hook RAs
register_module(app, 'ra.email')

# Misc handlers
register_module(app, 'app.pages')

