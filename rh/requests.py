""" Request

This module contains the ``Request`` class which represents a single request.

"""

from __future__ import unicode_literals, print_function

import base64
import StringIO
import datetime
import re

from google.appengine.api.images import Image, NotImageError

from .db import Request as RequestModel, RequestConstants
from .exceptions import *

__all__ = ('Request',)

# The following regexp will only match the standard Base64-encoded strings
# using + and / for non-alphanumeric characters.
BASE64_RE = re.compile(r'^([A-Za-z0-9+/]{4})*'  # normal base-64 blocks
                       r'('
                       r'[A-Za-z0-9+/]{4}'      # Non-padded block
                       r'|[A-Za-z0-9+/]{3}='    # Padded block with 1 pad
                       r'|[A-Za-z0-9+/]{2}=='   # Padded block with 2 pads
                       r')$')


class Request(RequestConstants):
    """ Content requests

    The ``Request`` class represents content requests and provides methods for
    working with them. Among other things, it can be used to clean and persist
    incoming requests.

    """

    # Exception classes provided for convenient access
    RequestError = RequestError
    RequestDataError = RequestDataError
    BinaryDecodeError = BinaryDecodeError
    ImageDecodeError = ImageDecodeError
    ImageFormatError = ImageFormatError

    def __init__(self, adaptor, content, timestamp, content_format,
                 language=None, content_language=None, topic=None,
                 location=None):

        # Adaptor information
        self.adaptor_name = adaptor.name
        self.adaptor_source = adaptor.source
        self.adaptor_trusted = adaptor.trusted

        # Timestamps
        self.posted = timestamp
        self.processed = datetime.datetime.now()

        # Request content information
        self.raw_content = content
        self.processed_content = None
        self.content_format = content_format
        self.content_type = self.CONTENT_TYPES.get(self.content_format)
        self.content_language = content_language
        self.location = location

        # Broadcast content information
        self.topic = topic
        self.language = language

    def check_adaptor(self):
        """ Check adaptor attributes """
        if not self.adaptor_name:
            raise RequestDataError('Missing adaptor name')
        if not self.adaptor_source:
            raise RequestDataError('Missing adaptor source name')
        if self.adaptor_trusted is None:
            raise RequestDataError('Missing adaptor trusted flag')

    def check_timestamp(self):
        """ Check timestamp format """
        if not isinstance(self.posted, datetime.datetime):
            raise RequestDataError('Timestamp must be a datetime object')

    def check_content_format(self):
        """ Check content format """
        if not self.raw_content:
            raise RequestDataError('Missing request content')
        if self.content_format not in self.FORMATS:
            raise RequestDataError('Invalid content format')
        if all([self.content_type == self.TRANSCRIBED,
                len(self.raw_content) > 40,
                BASE64_RE.match(self.raw_content)]):
            raise RequestDataError('Binary data as text')

    def check_content_data(self):
        """ Check content data """
        if self.content_format == self.TEXT:
            self.processed_content = unicode(self.raw_content)
        elif self.content_format in self.IMAGE:
            # Check that image data can be safely decoded
            decoded = self.decode_binary()
            img = self.image_from_string(decoded)
            # Check if image is broken
            fmt = img.format
            if fmt not in self.PIL_FORMATS:
                raise ImageFormatError('Image format %s not supported' % fmt)
            fmt = self.PIL_FORMAT_MAPPINGS[fmt]
            # Check if image format matches the declared content format
            dfmt = self.content_format.split('/')[1]
            if fmt != dfmt:
                raise ImageFormatError('Image format %s does not match '
                                       'content format %s' % (
                                           fmt, self.content_format))

            self.processed_content = decoded

    def check_request_meta(self):
        """ Check miscellanous request information """

    def check(self):
        """ Check request data and raise exception if invalid """
        self.check_adaptor()
        self.check_timestamp()
        self.check_request_meta()
        self.check_content_format()
        self.check_content_data()
        return self

    def prepare(self):
        """ Return an unsaved entity """
        if not self.processed_content:
            raise RequestError('Cannot persist unprocessed request')
        r = RequestModel(
            adaptor_name=self.adaptor_name,
            adaptor_source=self.adaptor_source,
            adaptor_trusted=self.adaptor_trusted,
            content_type=self.content_type,
            content_format=self.content_format,
            posted=self.posted,
            processed=self.processed,
        )
        if self.content_type == self.TRANSCRIBED:
            r.set_content(
                text_content=self.processed_content,
                language=self.language,
                content_language=self.content_language,
                topic=self.topic,
            )
        else:
            r.binary_content = self.processed_content
            r.set_content(
                text_content=None,
                language=self.language,
                content_language=self.content_language,
                topic=self.topic,
            )
        return r

    def persist(self):
        r = self.prepare()
        r.put()
        return r

    def decode_binary(self):
        """ Decodes binary data """
        try:
            decoded = base64.b64decode(self.raw_content)
        except TypeError:
            raise BinaryDecodeError('Unable to decode binary data')
        return decoded

    @staticmethod
    def image_from_string(s):
        """ Converts a string to PIL's Image object """
        try:
            img = Image(image_data=s)
            img.format  # Access the `format` attrib to trigger the exception
        except NotImageError:
            raise ImageDecodeError('Cannot load image from string')
        return img



