from __future__ import unicode_literals, print_function

import unittest
import datetime

from mock import patch, call
from flask import Flask

from ra.email import *


class OuternetEmailRATestCase(unittest.TestCase):
    """ Tests related to Outernet email RA

    Testing requires a mock Flask application context for configuration
    purposes.
    """

    mock_msg = """
    [{
      "ts": 1396310400,
      "msg": {
        "text": "Message body"
      }
    }]
    """

    timestamp = datetime.datetime.fromtimestamp(1396310400)

    def setUp(self):
        super(OuternetEmailRATestCase, self).setUp()
        self.app = Flask(__name__)
        self.app.config.update({
            'EML_API_ID': '$EML_UNAME',
            'EML_API_KEY': '$EML_KEY',
            'EML_API_SIGNATURE': '$EML_SIGN',
            'EML_ADDRESS': 'request@csds.outernet.is',
            'TESTING': True
        })

    def test_init_data(self):
        """ Should accept data as constructor param """
        with self.app.app_context():
            a = OuternetEmailAdaptor(self.mock_msg)
        self.assertEqual(
            a.data,
            [{'ts': 1396310400, 'msg': {'text': 'Message body'}}])

    @patch('ra.email.app')
    def test_strip_sigs_with_no_sig(self, app):
        """ Should keep messages without sigs intact """
        app.config = {'EML_API_ID': '', 'EML_API_KEY': ''}
        a = OuternetEmailAdaptor('{}')
        self.assertEqual(a.strip_sig('Foo bar baz'), 'Foo bar baz')

    @patch('ra.email.app')
    def test_strip_sigs_with_classic_sig(self, app):
        """ Should strip out classic sig starting with '--' """
        app.config = {'EML_API_ID': '', 'EML_API_KEY': ''}
        a = OuternetEmailAdaptor('{}')
        self.assertEqual(a.strip_sig("""Message body

        --
        John Doe
        john.doe@example.com
        """), 'Message body')

    @patch('ra.email.app')
    def test_strip_sigs_with_sent_from_phone(self, app):
        """ Should strip out phone sig starting with 'Sent from' """
        app.config = {'EML_API_ID': '', 'EML_API_KEY': ''}
        a = OuternetEmailAdaptor('{}')
        self.assertEqual(a.strip_sig("""Message body

        Sent from my iPhone
        """), 'Message body')
        self.assertEqual(a.strip_sig("""Message body

        Sent from my BlackBerry
        """), 'Message body')

    @patch('ra.email.app')
    def test_strips_whitespace(self, app):
        """ Should strip leading and tailing whitespace from message """
        app.config = {'EML_API_ID': '', 'EML_API_KEY': ''}
        a = OuternetEmailAdaptor('{}')
        self.assertEqual(a.strip_sig(' Message body \n\n'), 'Message body')

    @patch('ra.email.app')
    @patch('ra.email.Request')
    def test_process_message(self, Req, app):
        """ Should return a Request instance """
        app.config = {'EML_API_ID': '', 'EML_API_KEY': ''}
        a = OuternetEmailAdaptor(self.mock_msg)
        ret = a.process_message(a.data[0])
        Req.assert_called_once_with(adaptor=a,
                                    content='Message body',
                                    timestamp=self.timestamp,
                                    content_format=Req.TEXT)

