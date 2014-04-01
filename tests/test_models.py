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

