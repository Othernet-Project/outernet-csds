""" Outernet Facebook Page Adaptor

This adaptor collects requests from the Outernet Facebook Page dedicated to
content requests.

The module contains a single adaptor class: ``OuternetFacebookAdaptor``.

"""

from __future__ import unicode_literals, print_function

import datetime
import calendar

import facebook
from flask import current_app as app
from utils.routes import Route

from rh.adaptors import Adaptor, CronJobHandlerMixin
from rh.requests import Request

__all__ = ('OuternetFacebookAdaptor', 'OuternetFacebookCronJob')


class OuternetFacebookAdaptor(Adaptor):
    """ Outernet Facebook Page Adaptor

    This adaptor collects direct wall posts on the Outernet Adaptor app's
    Facebook page. It is currently limited to collecting only the messages and
    times the messages were posted and does not impose any limitation on the
    message format.
    """

    name = 'outernet-fb-page'
    source = 'Outernet Facebook Page'
    contact = 'hello@outernet.com'
    trusted = True

    def __init__(self):
        self.app_id = app.config['OFB_APP_ID']
        self.app_secret = app.config['OFB_APP_SECRET']
        self.page_id = app.config['OFB_PAGE_ID']

    def get_requests(self, last_access):
        """ Collect messages from the Facebook page and return the list """
        data = self.get_posts(last_access)
        requests = []
        for post in data:
            r = self.process_post(post)
            if r is not None:
                requests.append(r)
        return requests

    def process_post(self, post):
        if not post['message']:
            return
        return Request(
            adaptor=self,
            content=post['message'],
            timestamp=datetime.datetime.fromtimestamp(
                int(post['created_time'])),
            content_format=Request.TEXT,
        )

    def get_posts(self, last_access):
        """ Obtain all posts made by other users on a wall """
        access_token = facebook.get_app_access_token(self.app_id,
                                                     self.app_secret)
        timestamp = calendar.timegm(last_access.timetuple())
        graph = facebook.GraphAPI(access_token)
        query = ('SELECT actor_id, message, created_time FROM stream '
                 'WHERE type < 0 AND source_id=%s '
                 'AND created_time >= %s' % (self.page_id, timestamp))
        return graph.fql(query)


class OuternetFacebookCronJob(CronJobHandlerMixin, Route):
    """ Outernet Facebook adaptor quarter-daily harvest cron job """
    name = 'rh_harvest_facebook'
    path = '/rh/harvests/facebook'
    adaptor_class = OuternetFacebookAdaptor

