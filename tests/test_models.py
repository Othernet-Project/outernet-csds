import datetime

from mock import patch, Mock
from google.appengine.ext import ndb

from rh.db import *

from tests.dbunit import DatastoreTestCase


class RemoteAdaptorTestCase(DatastoreTestCase):
    """ Tests related to RemoteAdaptor model """

    def test_renew_key(self):
        """ A new API key should be added """
        ra = RemoteAdaptor()
        with patch('os.urandom') as urandom:
            urandom.return_value = 'a'
            ra.renew_key()
            self.assertEqual(ra.api_key, 'ra_86f7e437faa5a7fce15d')

    def test_key_renews_on_put(self):
        """ New entities' keys are automatically renewed """
        ra = RemoteAdaptor(name='foo', source='bar', contact='baz')
        with patch('os.urandom') as urandom:
            urandom.return_value = 'a'
            ra.put()
            self.assertEqual(ra.api_key, 'ra_86f7e437faa5a7fce15d')


class RequestTestCase(DatastoreTestCase):
    """ Tests methods for fetching requests """

    def tearDown(self):
        for k in Request.query().fetch(keys_only=True):
            k.delete()

    @staticmethod
    def request(adaptor_name='foo', adaptor_source='bar',
                adaptor_trusted=False,
                content_type=RequestConstants.TRANSCRIBED,
                content_format=RequestConstants.TEXT,
                text_content='We need content',
                content_language='en',
                world=RequestConstants.OFFLINE,
                language='fr',
                topic=RequestConstants.TOPICS[0],
                posted=datetime.datetime(2014, 4, 1),
                processed=datetime.datetime(2014, 4, 1),
                broadcast=False):
        """ Factory method to generate request entities """
        return Request(**locals())

    def test_cds_broadcast_flag(self):
        """ Should fetch entities without broadcast flag """
        # Create test data
        n = 4
        d = [self.request() for i in range(n)]
        d += [self.request(broadcast=True) for i in range(n)]
        ndb.put_multi(d)
        # Test method
        r = Request.fetch_cds_requests()
        self.assertEqual(len(r), n)

    def test_cds_sorting(self):
        """ Should sort reverse chronologically by posted timestamp """
        # Create test data
        d = [self.request(posted=datetime.datetime(2014, 4, i + 1))
             for i in range(4)]
        ndb.put_multi(d)
        # Test method
        r = Request.fetch_cds_requests()
        self.assertEqual(r[0].posted.day, 4)
        self.assertEqual(r[1].posted.day, 3)
        self.assertEqual(r[2].posted.day, 2)
        self.assertEqual(r[3].posted.day, 1)


class ContentTestCase(DatastoreTestCase):
    """ Tests related to content suggestion model """

    def test_url_quoting(self):
        c = Content(url='http://test.com/')
        self.assertEqual(c.quoted_url, 'http%3A%2F%2Ftest.com%2F')


class HarvestHistoryTestCase(DatastoreTestCase):
    """ Tests related to harvest history data """

    def adaptor(self, name='foo'):
        """ Factory for mock adaptors """
        adp = Mock()
        adp.name = name
        return adp

    @patch('google.appengine.ext.ndb.model.DateTimeProperty._now')
    def test_record_timestamp(self, now):
        """ Should update timestamp on put """
        now.return_value = datetime.datetime(2014, 4, 1)
        a = self.adaptor()
        h = HarvestHistory.record(a)
        self.assertEqual(h.timestamp, now.return_value)

    @patch('google.appengine.ext.ndb.model.DateTimeProperty._now')
    def test_adaptor_name(self, now):
        """ Should use adaptor name as id """
        now.return_value = datetime.datetime(2014, 4, 1)
        a = self.adaptor()
        h = HarvestHistory.record(a)
        self.assertEqual(h.key, ndb.Key('HarvestHistory', a.name))


    @patch('google.appengine.ext.ndb.model.DateTimeProperty._now')
    def test_get_timestamp(self, now):
        """ Should return a timestamp for a given adaptor """
        now.return_value = datetime.datetime(2014, 4, 1)
        a = self.adaptor('bar')
        h = HarvestHistory.record(a)
        t = HarvestHistory.get_timestamp(a)
        self.assertEqual(h.timestamp, t)

    @patch('google.appengine.ext.ndb.model.DateTimeProperty._now')
    def test_get_timestamp_for_nonexistent(self, now):
        """ Should return UTC unix epoch for nonexistent adaptor """
        now.return_value = datetime.datetime(2014, 4, 1)
        t = HarvestHistory.get_timestamp(self.adaptor('baz'))
        self.assertEqual(t, datetime.datetime.utcfromtimestamp(0))


