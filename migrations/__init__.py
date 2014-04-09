""" Helper tools for writing migrations """

from google.appengine.ext import ndb


class Migration(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def has_run(cls, migration_number):
        k = ndb.Key('Migration', migration_number)
        return k.get() is not None

    @classmethod
    def create(cls, migration_number):
        cls(id=migration_number).put()

