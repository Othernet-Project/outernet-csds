""" Request hub adaptors (RAs)

This module implements interfaces for Request hub adaptors (RAs).

All remote adaptors are expected to be registered and registration information
must be persisted in the database. This module provides tools for retrieving
information about persisted adaptor registration information, and checking
incoming requests for adaptor credentials.

The interfaces in this module also provide a consistent way of invoking adaptor
actions (such as harvesting requests from a remote source), which is used by
the hub to collect data.

"""

import logging

from flask import Response
from google.appengine.ext import ndb

from .db import HarvestHistory
from .exceptions import RequestError


class Adaptor(object):
    """ Basic adaptor metadata and behavior

    Every adaptor has a name, which is a unique, a source identifier, which is
    a string that identifies a source from which adaptor receives/obtains
    requests, and a ``trusted`` flag, which tells the RH whether the adaptor is
    truested or not.

    It also provides an interface for fetching requests.

    Each adaptor must subclass this class.
    """

    name = None
    source = None
    contact = None
    trusted = False

    def get_requests(self, last_run):
        """ Return request objects

        This method is a no-op by default. It is expected that each subclass
        will implement the method to do something useful.

        The requests can be harvested at any time including the moment this
        method is called. The only requirement for this method is that it
        returns an interable containing all gathered requests.

        The single argument, ``last_run``, is passed to this method. This
        argument is a datetime object representing the last time
        ``get_request()`` was called.

        The adaptor object may do its own time-tracking, but it is generally
        not necessary.

        """

        return []

    def sign_request(self, request):
        """ Adds information about the adaptor to the request """
        request.adaptor = self.name
        request.source = self.source


class CronJobHandlerMixin(object):
    """ Mixin class for creating Flask route handlers for cron jobs """

    # Set this to a proper Adaptor subclass
    adaptor_class = None

    def GET(self):
        """ Harvest the requests from Outernet Facebook page """
        self.run_job()
        return self.ok()

    def run_job(self):
        """ Run the cron job in a generic way """
        if not self.adaptor_class:
            logging.error('No adaptor class')
            return
        self.adaptor = self.adaptor_class()
        requests = self.get_requests()
        clean = self.check_requests(requests)
        res = self.persist_requests(clean)
        logging.info('Saved %s requests' % len(res))
        HarvestHistory.record(self.adaptor)

    def get_requests(self):
        """ Instantiate the adaptor object and obtain requests """
        last_run = HarvestHistory.get_timestamp(self.adaptor)
        return self.adaptor.get_requests(last_run)

    @staticmethod
    def check_requests(requests):
        """ Check each request, and compile a list of valid requests """
        clean = []
        for request in requests:
            try:
                request.check()
                clean.append(request.prepare())
            except RequestError as err:
                logging.exception('Error processing request: %s' % err)
        return clean

    @staticmethod
    def persist_requests(requests):
        """ Store all requests in datastore """
        if not requests:
            return []
        res = []
        try:
            res = ndb.put_multi(requests)
        except Exception as err:
            logging.exception('Error saving requests: %s' %  err)
        return res

    @staticmethod
    def ok():
        """ Return 200 OK response """
        return Response('OK', 200)
