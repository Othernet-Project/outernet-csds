""" Datastore models

This module implements GAE datastore models using NDB API.

These models are used to persist data which is used by adaptors and the hub.

"""

from __future__ import unicode_literals, print_function

from google.appengine.ext import ndb

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

    # PIL-related constants
    PIL_PNG = 'PNG'
    PIL_JPG = 'JPEG'
    PIL_GIF = 'GIF'
    PIL_FORMATS = [PIL_PNG, PIL_JPG, PIL_GIF]

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
    text_content = ndb.TextProperty(indexed=False)
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

