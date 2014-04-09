""" Datastore models

This module implements GAE datastore models using NDB API.

These models are used to persist data which is used by adaptors and the hub.

"""

from __future__ import unicode_literals, print_function

import datetime

from google.appengine.ext import ndb
from google.appengine.api import images
from werkzeug.urls import url_quote_plus
import babel

from .keys import generate_api_key
from .properties import LanguageProperty

ADAPTOR_KEY_PREFIX = 'ra'

__all__ = ('RemoteAdaptor', 'Request', 'RequestConstants', 'Content',
           'HarvestHistory')


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


class Revision(ndb.Model):
    """ Model used for repeated structured property in Request model

    This model persists the data related to revisions.

    """

    timestamp = ndb.DateTimeProperty()
    text_content = ndb.TextProperty()
    content_language = LanguageProperty()
    language = LanguageProperty()
    topic = ndb.StringProperty(choices=RequestConstants.TOPICS)


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

    # Computed content properties (derived from revision)
    text_content = ndb.ComputedProperty(lambda s: s._rev_field('text_content'))
    content_language = ndb.ComputedProperty(
        lambda s: s._rev_field('content_language'))

    # Broadcast information (derived from revision)
    language = ndb.ComputedProperty(lambda s: s._rev_field('language'))
    topic = ndb.ComputedProperty(lambda s: s._rev_field('topic'))

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

    def _rev_field(self, field_name, rev=None):
        try:
            rev = self.revisions[rev or self.current_revision or 0]
        except IndexError:
            return None
        return getattr(rev, field_name)

    @property
    def content_language_name(self):
        try:
            return babel.Locale(self.content_language).get_language_name()
        except babel.UnknownLocaleError:
            return None

    @property
    def language_name(self):
        try:
            return babel.Locale(self.language).get_langauge_name()
        except babel.UnknownLocaleError:
            return None

    def set_content(self, text_content=None, content_language=None,
                    language=None, topic=None):
        """ Save an edit into revisions """

        if not any([text_content, content_language, language, topic]):
            # Nothing to do
            return

        rev = Revision(
            timestamp=datetime.datetime.utcnow(),
            text_content=text_content or self.text_content,
            content_language=content_language or self.content_language,
            language=language or self.language,
            topic=topic or self.topic
        )
        self.revisions.append(rev)
        if self.current_revision is None:
            self.current_revision = 0
        else:
            self.current_revision = len(self.revisions) - 1

    @property
    def content(self):
        try:
            return self.revisions[self.current_revision]
        except IndexError:
            return None

    def revert(self):
        """ Reverts to previous revision """
        self.current_revision = max(0, self.current_revision - 1)

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


class Content(ndb.Model):
    """ Model to persist content suggestions """

    url = ndb.StringProperty(required=True)
    submitted = ndb.DateTimeProperty(auto_now_add=True)
    votes = ndb.IntegerProperty(default=0)

    @property
    def quoted_url(self):
        return url_quote_plus(self.url)


class HarvestHistory(ndb.Model):
    """ Model to persist cron-based harvesting history """

    timestamp = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_timestamp(cls, adaptor):
        k = cls.get_key(adaptor)
        h = k.get()
        if not h:
            # If there's no timestamp, return the beginning of UNIX epoch
            return datetime.datetime.utcfromtimestamp(0)
        return h.timestamp

    @classmethod
    def record(cls, adaptor):
        h = cls(id=adaptor.name)
        h.put()
        return h

    @staticmethod
    def get_key(adaptor):
        return ndb.Key('HarvestHistory', adaptor.name)

