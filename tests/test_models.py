from mock import patch

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

