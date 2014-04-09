from unittest import TestCase

from google.appengine.ext import ndb
from google.appengine.ext import db
from rh.properties import *


class TestModel(ndb.Model):
    lang = LanguageProperty()


class LanguagePropertyTestCase(TestCase):
    """ Test related to custom LanguageProperty property """

    def test_validation(self):
        with self.assertRaises(db.BadValueError) as err:
            TestModel(lang='not a locale')
        self.assertEqual(err.exception.message, 'Not a valid locale')

    def test_valid_language(self):
        try:
            TestModel(lang='en')
        except db.BadValueError:
            self.assertFalse(True, 'Should not raise an exception')
