""" Datastore models

This module implements GAE datastore models using NDB API.

These models are used to persist data which is used by adaptors and the hub.

"""

from __future__ import unicode_literals, print_function

from google.appengine.ext import ndb

from .keys import generate_api_key

ADAPTOR_KEY_PREFIX = 'ra'


class RemoteAdaptor(ndb.Model):
    """ Model for persisting remote adaptor information """

    name = ndb.StringProperty(required=True, indexed=False)
    source = ndb.StringProperty(required=True, indexed=False)
    contact = ndb.StringProperty(required=True)
    trusted = ndb.BooleanProperty(default=False, required=True)
    api_key = ndb.StringProperty(required=True)

    def renew_key(self):
        self.api_key = generate_api_key('ra')

    def _pre_put_hook(self):
        self.renew_key()

