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
        data = self.get_posts(self.page_id, last_access)
        requests = []
        print(data)
        for post in data:
            if not post['message']:
                continue
            # TODO: First check if post is an image and do things differently
            # for them.
            requests.append(Request(
                adaptor=self,
                content=post['message'],
                timestamp=datetime.datetime.fromtimestamp(
                    int(post['created_time'])),
                content_format=Request.TEXT,
                world=Request.ONLINE,
            ))
        return requests

    def get_posts(self, page_id, last_access):
        """ Obtain all posts made by other users on a wall """
        access_token = facebook.get_app_access_token(self.app_id,
                                                     self.app_secret)
        timestamp = calendar.timegm(last_access.timetuple())
        graph = facebook.GraphAPI(access_token)
        query = ('SELECT actor_id, message, created_time FROM stream '
                 'WHERE type < 0 AND source_id=%s '
                 'AND created_time >= %s' % (page_id, timestamp))
        return graph.fql(query)

    def get_location(self, page_id):
        """ Obtain current location of the specified profile (user) """
        graph = facebook.GraphAPI('%s|%s' % (self.app_id, self.app_secret))
        query = 'SELECT current_location FROM user WHERE uid = %s' % page_id
        return graph.fql(query)


class OuternetFacebookCronJob(CronJobHandlerMixin, Route):
    """ Outernet Facebook adaptor quarter-daily harvest cron job """
    name = 'rh_harvest_facebook'
    path = '/rh/harvests/facebook'
    adaptor_class = OuternetFacebookAdaptor

