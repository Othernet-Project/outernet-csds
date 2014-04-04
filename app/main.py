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

from flask import Flask
from utils.routes import register_module

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config.from_object('app.conf.%s' % ENV)

# Cron job handlers
register_module(app, 'ra.outernet_facebook')
