from mock import patch, Mock

from rh.adaptors import CronJobHandlerMixin
from rh.exceptions import RequestDataError

from tests.dbunit import DatastoreTestCase


class CronHandlerTestCase(DatastoreTestCase):
    """ Test cron job handler mixin """

    def test_calls_adaptor(self):
        """ Should instantiate adaptor """
        CronJobHandlerMixin.adaptor_class = self.Adaptor
        c = CronJobHandlerMixin()
        c.run_job()
        self.Adaptor.assert_called_once()

    def test_gets_requests(self):
        """ Should get requests for given adaptor """
        CronJobHandlerMixin.adaptor_class = self.Adaptor
        c = CronJobHandlerMixin()
        c.run_job()
        self.adaptor.get_requests.assert_called_once()

    def test_checks_each_request(self):
        """ Should call check() on all requests """
        CronJobHandlerMixin.adaptor_class = self.Adaptor
        c = CronJobHandlerMixin()
        c.run_job()
        self.good_request.check.assert_called_once()

    def test_prepares_each_request(self):
        """ Should call prepare() on all requests """
        CronJobHandlerMixin.adaptor_class = self.Adaptor
        c = CronJobHandlerMixin()
        c.run_job()
        self.good_request.prepare.assert_called_once()

    def test_logs_error_on_request_validation_error(self):
        """ Should log validation errors """
        self.adaptor.get_requests.return_value = [self.bad_request]
        CronJobHandlerMixin.adaptor_class = self.Adaptor
        c = CronJobHandlerMixin()
        c.run_job()
        self.logging.exception.assert_called_once_with(
            'Error processing request: foo')

    def test_logs_on_missing_class(self):
        """ Should log error on missing adaptor class """
        c = CronJobHandlerMixin()
        c.run_job()
        self.logging.error.assert_called_once()

    @patch('rh.adaptors.ndb.put_multi')
    def test_put_good_requests(self, pm):
        """ Should put() only good requests """
        requests = [self.bad_request, self.good_request, self.good_request]
        self.adaptor.get_requests.return_value = requests
        CronJobHandlerMixin.adaptor_class = self.Adaptor
        c = CronJobHandlerMixin()
        c.run_job()
        pm.assert_called_once_with([
            self.good_request.prepare.return_value,
            self.good_request.prepare.return_value
        ])

    def test_logs_number_of_puts(self):
        """ Should log number of successful puts """
        requests = [self.bad_request, self.good_request, self.good_request]
        self.adaptor.get_requests.return_value = requests
        CronJobHandlerMixin.adaptor_class = self.Adaptor
        c = CronJobHandlerMixin()
        c.run_job()
        self.logging.info.called_once_with('Saved 2 requests')

    @patch('rh.adaptors.Response')
    def test_ok_method(self, Resp):
        """ Should return response object with content of 'OK' and 200 code """
        r = CronJobHandlerMixin.ok()
        Resp.assert_called_once_with('OK', 200)
        self.assertEqual(r, Resp.return_value)

    @patch('rh.adaptors.CronJobHandlerMixin.run_job')
    @patch('rh.adaptors.CronJobHandlerMixin.ok')
    def test_GET_method(self, ok, run_job):
        """ GET() method should call run_job() and ok() methods """
        c = CronJobHandlerMixin()
        c.GET()
        run_job.assert_called_once()
        ok.assert_called_once()

    def setUp(self):
        super(CronHandlerTestCase, self).setUp()
        # Create mock adaptor class and instance
        def se():
            raise RequestDataError('foo')

        # Create request, adaptor object, and adaptor class mocks
        self.good_request = Mock(name='good_request')
        self.bad_request = Mock(name='bad_request')
        self.bad_request.check.side_effect = se
        mock_adaptor = Mock(name='adaptor')
        mock_adaptor.name = 'foo'
        mock_adaptor.get_requests.return_value = [self.good_request]
        self.Adaptor = MockAdaptor = Mock(name='Adaptor')
        self.Adaptor.return_value = self.adaptor = mock_adaptor

        # Patch the harvest history model
        self.hh_patcher = patch('rh.adaptors.HarvestHistory')
        self.HarvestHistory = self.hh_patcher.start()

        # Patch the logger
        self.logging_patcher = patch('rh.adaptors.logging')
        self.logging = self.logging_patcher.start()

        CronJobHandlerMixin.adaptor_class = None

    def tearDown(self):
        self.hh_patcher.stop()
        self.logging_patcher.stop()
        super(CronHandlerTestCase, self).tearDown()

