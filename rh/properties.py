""" Custom NDB properties

This module implements custom properties for Google AppEngine NDB models. The
properties are used in RH's datastore models.

"""

from __future__ import unicode_literals, print_function

from babel import localedata
from google.appengine.ext import ndb
from google.appengine.ext import db


__all__ = ('LanguageProperty',)


class LanguageProperty(ndb.StringProperty):
    """ Property for storing Babel-compatible language codes """

    def _validate(self, val):
        if not localedata.exists(val):
            raise db.BadValueError('Not a valid locale')
