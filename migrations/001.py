""" Migration: Add revisions to requests

This module implements a migration endpoint that updates existing request
entities that do not have revisions to contain revisions. The module implements
a model that is compliant with the older version of the Request model.

The implementation uses a single blank Expando model named 'Request' (the same
as the model we are updating) and uses the NDB Datastore API to perform the
necessary modifications manually.

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

from rh.db import Revision, RequestConstants
from . import Migration

MIGRATION = '001'

class Request(ndb.Expando):
    """ Expando model that will be used to query the datastore """

    # Adaptor information
    adaptor_name = ndb.StringProperty(required=True)
    adaptor_source = ndb.StringProperty(required=True)
    adaptor_trusted = ndb.BooleanProperty(default=False)

    # Content
    content_type = ndb.IntegerProperty(required=True,
                                       choices=RequestConstants.TYPES)
    content_format = ndb.StringProperty(required=True,
                                        choices=RequestConstants.FORMATS)
    binary_content = ndb.BlobProperty(indexed=False, compressed=True)

    # Metadata
    world = ndb.IntegerProperty(choices=RequestConstants.WORLDS)

    # Timestamps
    posted = ndb.DateTimeProperty(required=True)
    processed = ndb.DateTimeProperty(required=True)
    edited = ndb.DateTimeProperty()
    recorded = ndb.DateTimeProperty(required=True, auto_now_add=True)

    # Workflow
    has_suggestions = ndb.BooleanProperty(default=False)
    broadcast = ndb.BooleanProperty(default=False)
    current_revision = ndb.IntegerProperty()
    revisions = ndb.StructuredProperty(Revision, repeated=True)


app = Flask(__name__)


@app.route('/migrations/%s' % MIGRATION)
def update_requests():
    """ Update all requests to the new format

    Note that this handler assumes that there aren't that many requests in the
    datastore (less than 1000).
    """

    if Migration.has_run(MIGRATION):
        return 'Migration %s has already run' % MIGRATION

    old = Request.query().fetch(1000)
    new = []
    for e in old:
        if len(e.revisions):
            # Skip entities that use the new format
            continue
        entity_dict = e.to_dict()
        r = Revision()
        for k in ['text_content', 'content_language', 'topic', 'language']:
            val = entity_dict.get(k)
            if val is None:
                print('Skipping key %s' % k)
                continue
            print('Setting key %s to %s' % (k, val))
            setattr(r, k, val)
            delattr(e, k)
        e.current_revision = 0
        e.revisions = [r]
        new.append(e)
    ndb.put_multi(new)
    Migration.create(MIGRATION)
    return 'Requests migrated: %s' % new
