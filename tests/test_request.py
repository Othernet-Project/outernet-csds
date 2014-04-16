import unittest
import datetime
import os
import base64

from mock import Mock, patch

from rh.requests import Request
from rh.db import Request as RequestModel

from tests.dbunit import DatastoreTestCase

img_path = lambda p: os.path.join(os.path.dirname(__file__), p)


TEST_NONIMAGE = 'bm90IGFuIGltYWdl'
TEST_IMAGE_PATH = img_path('test_image.png')
TEST_IMAGE_BIN = open(TEST_IMAGE_PATH, 'rb').read()
TEST_IMAGE_B64 = base64.b64encode(TEST_IMAGE_BIN)
TEST_TIFF_PATH = img_path('test_image.tif')
TEST_TIFF_BIN = open(TEST_TIFF_PATH, 'rb').read()
TEST_TIFF_B64 = base64.b64encode(TEST_TIFF_BIN)

TEST_TIMESTAMP = datetime.datetime(2014, 4, 1)


class RequestTestMixin(object):
    """ Mixin with factory methods """

    def adaptor(self, name='foo', source='bar', trusted=False):
        """ Build mock adaptor object """
        a = Mock()
        a.name = name
        a.source = source
        a.trusted = trusted
        return a

    def request(self, adaptor=None, content='test', timestamp=None,
                content_format=Request.TEXT, **kwargs):
        """ Build test request object """
        adaptor = adaptor or self.adaptor()
        timestamp = timestamp or TEST_TIMESTAMP
        return Request(adaptor, content, timestamp, content_format,
                       **kwargs)


class RequestObjectTestCase(RequestTestMixin, unittest.TestCase):
    """ Tests the ``Request`` API """

    def test_adaptor_arg(self):
        """ Should assign adaptor properties based on adaptor object """
        a1 = self.adaptor('foo', 'bar', False)
        a2 = self.adaptor('bar', 'foo', True)

        r = self.request(a1)
        self.assertEqual(r.adaptor_name, 'foo')
        self.assertEqual(r.adaptor_source, 'bar')
        self.assertEqual(r.adaptor_trusted, False)

        r = self.request(a2)
        self.assertEqual(r.adaptor_name, 'bar')
        self.assertEqual(r.adaptor_source, 'foo')
        self.assertEqual(r.adaptor_trusted, True)

    @patch('datetime.datetime')
    def test_auto_timestamp(self, dt):
        """ Should assign current timestamp to ``processed`` property """
        r = self.request()
        self.assertEqual(r.processed, dt.now.return_value)

    def test_check_adaptor(self):
        """ Should check all adaptor properties """
        a1 = self.adaptor(None, 'bar', False)
        self.assertAdaptorInvalid(a1, 'Missing adaptor name')

        a2 = self.adaptor('foo', None, False)
        self.assertAdaptorInvalid(a2, 'Missing adaptor source name')

        a3 = self.adaptor('foo', 'bar', None)
        self.assertAdaptorInvalid(a3, 'Missing adaptor trusted flag')

    def test_check_timestamp(self):
        """ Should check timestamp object type """
        r = self.request(timestamp='not a timestamp')
        with self.assertRaises(Request.RequestDataError) as ctx:
            r.check_timestamp()
        self.assertEqual(ctx.exception.message,
                         'Timestamp must be a datetime object')

    def test_check_missing_content(self):
        r = self.request(content=None)
        self.assertRequestContentInvalid(r, 'Missing request content')

        r = self.request(content_format='bogus')
        self.assertRequestContentInvalid(r, 'Invalid content format')

    def test_wrong_data_for_text(self):
        r = self.request(content=TEST_IMAGE_B64, content_format=Request.TEXT)
        self.assertRequestContentInvalid(r, 'Binary data as text')

    def test_check_text_content_data(self):
        r = self.request(content='text')
        r.check_content_data()
        self.assertEqual(r.processed_content, 'text')

    def test_check_invalid_text_content_format(self):
        r = self.request(content='text', content_format='image/png')
        self.assertRequestContentDataInvalid(r,
                                             'Cannot load image from string')

    def test_check_invalid_image_content_data(self):
        r = self.request(content=TEST_NONIMAGE, content_format=Request.PNG)
        with self.assertRaises(Request.ImageDecodeError) as ctx:
            r.check_content_data()
        self.assertEqual(ctx.exception.message,
                         'Cannot load image from string')

    def test_check_image_content_data(self):
        r = self.request(content=TEST_IMAGE_B64, content_format=Request.PNG)
        r.check_content_data()
        self.assertEqual(r.processed_content, TEST_IMAGE_BIN)

    def test_check_wrong_image_format(self):
        r = self.request(content=TEST_IMAGE_B64, content_format=Request.JPG)
        self.assertImageInvalid(r, 'Image format png does not match content '
                                'format image/jpg')

    def test_check_unsupported_format(self):
        r = self.request(content=TEST_TIFF_B64, content_format='image/png')
        self.assertImageInvalid(r, 'Image format -4 not supported')

    @patch('rh.requests.Request.check_adaptor')
    @patch('rh.requests.Request.check_timestamp')
    @patch('rh.requests.Request.check_content_format')
    @patch('rh.requests.Request.check_content_data')
    @patch('rh.requests.Request.check_request_meta')
    def test_check_calls_all_check_methods(self, e, d, c, b, a):
        r = self.request()
        r.check()
        a.assert_called_once()
        b.assert_called_once()
        c.assert_called_once()
        d.assert_called_once()
        e.assert_called_once()

    def assertAdaptorInvalid(self, a, msg):
        """ Make assertion about adaptor validation """
        r = self.request(a)
        with self.assertRaises(Request.RequestDataError) as ctx:
            r.check_adaptor()
        self.assertEqual(ctx.exception.message, msg)

    def assertRequestContentInvalid(self, r, msg):
        """ Make assertion about request content validation """
        with self.assertRaises(Request.RequestDataError) as ctx:
            r.check_content_format()
        self.assertEqual(ctx.exception.message, msg)

    def assertRequestContentDataInvalid(self, r, msg):
        with self.assertRaises(Request.ImageDecodeError) as ctx:
            r.check_content_data()
        self.assertEqual(ctx.exception.message, msg)

    def assertImageInvalid(self, r, msg):
        with self.assertRaises(Request.ImageFormatError) as ctx:
            r.check_content_data()
        self.assertEqual(ctx.exception.message, msg)

    def assertMetaInvalid(self, r, msg):
        with self.assertRaises(Request.RequestDataError) as ctx:
            r.check_request_meta()
        self.assertEqual(ctx.exception.message, msg)


class RequestPersistTestCase(RequestTestMixin, DatastoreTestCase):
    """ Test for the Request object's persist() method """

    def test_persist(self):
        """ Can persist in the database using persist() method """
        r = self.request()
        r.check()
        r.persist()

        r1 = RequestModel.query().get()
        for prop in ['adaptor_name', 'adaptor_source', 'adaptor_trusted',
                     'content_type', 'content_format', 'content_language',
                     'language', 'topic', 'posted']:
            self.assertEqual(getattr(r, prop), getattr(r1, prop))

    def test_persist_error(self):
        """ Should throw exception if request is not processed """
        r = self.request()

        with self.assertRaises(Request.RequestError):
            r.persist()




