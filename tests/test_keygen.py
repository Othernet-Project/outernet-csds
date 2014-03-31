from unittest import TestCase

from mock import patch

from rh.keys import generate_api_key


class KeygenTestCase(TestCase):
    """ Test related to API key generation """

    def test_prefix(self):
        """ Should accept a prefix which is prepended to the key """
        s = generate_api_key('pfx')
        self.assertTrue(s.startswith('pfx_'))

    def test_should_contain_hexdigest(self):
        """ The prefix is followed by a SHA-1 hexdigest truncated to 20 chr """
        with patch('os.urandom') as urandom:
            urandom.return_value = 'a'
            s = generate_api_key('pfx')
            self.assertEqual(s, 'pfx_86f7e437faa5a7fce15d')

