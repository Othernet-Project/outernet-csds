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
                world=RequestConstants.OFFLINE,
                posted=datetime.datetime(2014, 4, 1),
                processed=datetime.datetime(2014, 4, 1),
                broadcast=False):
        """ Factory method to generate request entities """
        return Request(**locals())

    @staticmethod
    def set_content(request,
                    text_content='We need content',
                    content_language='en',
                    language='fr',
                    topic=RequestConstants.TOPICS[0]):
        """ Set the content for a request """
        kwargs = locals()
        r = kwargs.pop('request')
        r.set_content(**kwargs)
        return r

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

    def test_create_revision(self):
        """ Should add a new revision """
        r = self.request()
        self.set_content(r)
        self.assertEqual(r.current_revision, 0)
        self.assertEqual(r.revisions[0].text_content, 'We need content')

    def test_add_new_revision(self):
        """ Should update current revision and append revision data """
        r = self.request()
        self.set_content(r)
        r.set_content(text_content='foo')
        self.assertEqual(r.current_revision, 1)
        self.assertEqual(r.revisions[1].text_content, 'foo')
        self.assertEqual(r.revisions[1].text_content, r.text_content)

    def test_content_properties(self):
        """ Content properties should be computed from revisions """
        r = self.request()
        self.set_content(r)
        self.assertEqual(r.text_content, 'We need content')
        r.set_content(text_content='foo')
        self.assertEqual(r.text_content, 'foo')

    def test_setting_no_value_uses_original(self):
        """ Should reuse original values for unspecified properties """
        r = self.request()
        self.set_content(r)
        r.set_content(language='pt_BR')
        # These should be reused
        self.assertEqual(r.revisions[1].text_content,
                         r.revisions[0].text_content)
        self.assertEqual(r.revisions[1].content_language,
                         r.revisions[0].content_language)
        self.assertEqual(r.revisions[1].topic,
                         r.revisions[0].topic)
        # These shoould be updated
        self.assertNotEqual(r.revisions[1].language,
                            r.revisions[0].language)

    def test_passing_no_arguments(self):
        """ Setting content with no arguments should be a no-op """
        r = self.request()
        self.set_content(r)
        r.set_content()
        self.assertEqual(r.current_revision, 0)
        self.assertEqual(len(r.revisions), 1)

    def test_get_current_revision(self):
        """ The ``content`` prop should return the current revision """
        r = self.request()
        self.set_content(r)
        r.set_content(text_content='foo')
        self.assertEqual(r.content, r.revisions[1])
        r.current_revision = 0
        self.assertEqual(r.content, r.revisions[0])

    def test_revert(self):
        """ Should revert to previous revision until there are no more """
        r = self.request()
        self.set_content(r)
        r.set_content(text_content='foo')
        r.set_content(language='pt_BR')
        r.revert()
        self.assertEqual(r.current_revision, 1)
        r.revert()
        self.assertEqual(r.current_revision, 0)
        self.assertEqual(len(r.revisions), 3)
        self.assertEqual(r.text_content, 'We need content')
        self.assertEqual(r.language, 'fr')


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


