""" Migration: Add content to request

This module implements a migration endpoint that migrates standalone
``Content`` entities to ``Request`` entities' ``content_suggestion``
properties.

"""

from __future__ import unicode_literals, print_function

from os.path import abspath, join, dirname
import sys
import logging

PROJECT_PATH = dirname(dirname(__file__))
PROJECT_DIR = abspath(dirname(dirname(__file__)))
VENDOR_DIR = join(PROJECT_DIR, 'vendor')

sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, VENDOR_DIR)

from google.appengine.ext import ndb
from flask import Flask

from rh.db import Content, Request
from . import Migration

MIGRATION = '002'

app = Flask(__name__)

@app.route('/migrations/%s' % MIGRATION)
def update_requests():
    """ Move all Content entities to Request entities

    This migration assumes there are less than 1000 entities in the datastore,
    and therefore does things quite inefficiently.

    """

    if Migration.has_run(MIGRATION):
        return 'Migration %s has already run' % MIGRATION

    content = Content.query().fetch(1000)
    count = 0
    for c in content:
        req = c.key.parent().get()
        if req is None:
            # This is a marformed content, so we disregard it
            continue
        try:
            req.suggest_url(c.url)
        except req.DuplicateSuggestionError:
            # Suggestion alrady exists so we leave it intact
            continue
        req.content_suggestions[-1].submitted = c.submitted
        req.content_suggestions[-1].votes = c.votes
        req.put()
        count += 1
    Migration.create(MIGRATION)
    return 'Migrated %s content suggestions' % count
