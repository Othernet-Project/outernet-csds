from __future__ import unicode_literals, print_function

import unittest
import datetime

from mock import patch, call
from flask import Flask

from ra.outernet_facebook import *


class OuternetFacebookRATestCase(unittest.TestCase):
    """ Tests related to Outernet Facebook page RA

    Testing requires a mock Flask application context for configuration
    purposes.
    """

    def setUp(self):
        super(OuternetFacebookRATestCase, self).setUp()
        self.app = Flask(__name__)
        self.app.config.update({
            'OFB_APP_ID': '123',
            'OFB_APP_SECRET': '123',
            'OFB_PAGE_ID': '123',
            'TESTING': True
        })

    @patch('facebook.GraphAPI')
    @patch('facebook.get_app_access_token')
    def test_get_posts(self, gacc, gapi):
        """ Should initiate GQL query with page ID and timestamp """
        ts = datetime.datetime(2014, 4, 1)
        with self.app.app_context():
            a = OuternetFacebookAdaptor()
            ret = a.get_posts(ts)
            gapi.assert_called_once_with(gacc.return_value)
            gapi.return_value.fql.assert_called_once_with(
                'SELECT actor_id, message, created_time FROM stream '
                'WHERE type < 0 AND source_id=123 '
                'AND created_time >= 1396310400')
            self.assertEqual(gapi.return_value.fql.return_value, ret)

    @patch('ra.outernet_facebook.OuternetFacebookAdaptor.get_posts')
    @patch('ra.outernet_facebook.OuternetFacebookAdaptor.process_post')
    def test_get_requests(self, pp, gp):
        """ Should return a list of requests """
        ts = datetime.datetime(2014, 4, 1)
        gp.return_value = [1, 2, 3]
        with self.app.app_context():
            a = OuternetFacebookAdaptor()
            ret = a.get_requests(ts)
        self.assertEqual(pp.mock_calls, [call(1), call(2), call(3)])
        self.assertEqual(ret, [pp.return_value, pp.return_value,
                               pp.return_value])

    @patch('ra.outernet_facebook.Request')
    def test_process_post(self, Req):
        """ Should return a Request object """
        its = 1396310400
        ts = datetime.datetime.fromtimestamp(its)
        mock_post = {
            'message': 'foo',
            'created_time': unicode(its),
        }
        with self.app.app_context():
            a = OuternetFacebookAdaptor()
            ret = a.process_post(mock_post)
        Req.assert_called_once_with(adaptor=a, content='foo', timestamp=ts,
                                    content_format=Req.TEXT)
        self.assertEqual(ret, Req.return_value)

    @patch('ra.outernet_facebook.Request')
    def test_process_post_with_no_message(self, Req):
        """ Should return None is message is empty """
        its = 1396310400
        ts = datetime.datetime.fromtimestamp(its)
        mock_post = {
            'message': '',
            'created_time': unicode(its),
        }
        with self.app.app_context():
            a = OuternetFacebookAdaptor()
            ret = a.process_post(mock_post)
        Req.assert_not_called()
        self.assertEqual(ret, None)
