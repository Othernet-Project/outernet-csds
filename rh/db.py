""" Datastore models

This module implements GAE datastore models using NDB API.

These models are used to persist data which is used by adaptors and the hub.

"""

from __future__ import unicode_literals, print_function

from google.appengine.ext import ndb
from google.appengine.api import images

from .keys import generate_api_key

ADAPTOR_KEY_PREFIX = 'ra'

__all__ = ('RemoteAdaptor', 'Request', 'RequestConstants')


class RequestConstants(object):
    """ Holds constants shared between request-related classes """

    # Request worlds
    ONLINE = 1
    OFFLINE = 0
    WORLDS = [ONLINE, OFFLINE]

    # Request types
    TRANSCRIBED = 1
    NONTRANSCRIBED = 0
    TYPES = [TRANSCRIBED, NONTRANSCRIBED]

    # Request formats
    TEXT = 'text/plain'
    PNG = 'image/png'
    JPG = 'image/jpg'
    GIF = 'image/gif'
    IMAGE = [PNG, JPG, GIF]
    FORMATS = [TEXT, PNG, JPG, GIF]

    # Mapping between formats and types
    CONTENT_TYPES = {
        TEXT: TRANSCRIBED,
        PNG: NONTRANSCRIBED,
        JPG: NONTRANSCRIBED,
        GIF: NONTRANSCRIBED,
    }

    # GAE-Images-API-related constants
    PIL_PNG = images.PNG
    PIL_JPG = images.JPEG
    PIL_GIF = images.GIF
    PIL_FORMATS = [PIL_PNG, PIL_JPG, PIL_GIF]
    PIL_FORMAT_MAPPINGS = {
        PIL_PNG: 'png',
        PIL_JPG: 'jpg',
        PIL_GIF: 'gif',
    }

    # Request topics
    TOPICS = [
        'agriculture',
        'arts',
        'business',
        'computers',
        'economy',
        'education',
        'health',
        'home',
        'kids',
        'nature',
        'news',
        'society',
        'sports',
        'sports',
        'technology',
    ]


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


class Request(RequestConstants, ndb.Model):
    """ Model for persisting requests """

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
    text_content = ndb.TextProperty()
    content_language = ndb.StringProperty()

    # Metadata
    world = ndb.IntegerProperty(choices=RequestConstants.WORLDS)

    # Broadcast information
    language = ndb.StringProperty()
    topic = ndb.StringProperty(choices=RequestConstants.TOPICS)

    # Timestamps
    posted = ndb.DateTimeProperty(required=True)
    processed = ndb.DateTimeProperty(required=True)
    recorded = ndb.DateTimeProperty(required=True, auto_now_add=True)

    # Workflow
    broadcast = ndb.BooleanProperty(default=False)

    @classmethod
    def fetch_cds_requests(cls):
        """ Fetches all requests for display in CDS

        The result set only includes items that have not been broadcast yet.

        The result set is sorted by post date (latest first) and may include a
        maximum of 1000 items (GAE limit). Paging may be allowed in future
        iterations.
        """

        return cls.query(
            cls.broadcast == False
        ).order(-cls.posted).fetch()


class HarvestHistory(ndb.Model):
    """ Model to persist cron-based harvesting history """

    timestamp = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_timestamp(cls, adaptor):
        k = cls.get_key(adaptor)
        h = k.get()
        if not h:
            return
        return h.timestamp

    @classmethod
    def record(cls, adaptor):
        h = cls(id=adaptor.name)
        h.put()

    @staticmethod
    def get_key(adaptor):
        return ndb.Key('HarvestHistory', adaptor.name)

