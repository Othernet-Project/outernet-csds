""" Content Selection Subsystem web interface

This module implements the CSS's web interface. The interface exposes endpoints
for voting on requests and displaying voting results.
"""

from __future__ import unicode_literals, print_function

from google.appengine.ext import ndb
from utils.routes import RedirectMixin, Route, HtmlRoute
from werkzeug.urls import url_unquote_plus


class WebUIVote(RedirectMixin, Route):
    """ Handler that facilitates content suggestion voting """
    name = 'css_webui_vote'
    path = '/requests/<int:request_id>/suggestions/<url>'

    def get_redirect_url(self):
        return self.url_for('cds_webui_request',
                            request_id=self.kwargs['request_id'])

    def PATCH(self, request_id, url):
        url = url_unquote_plus(url)
        self.req = ndb.Key('Request', request_id).get()
        if self.req is None:
            self.abort(404, 'No such request')
        for c in self.req.content_suggestions:
            if url == c.url:
                c.votes += 1
                self.req.put()
                return self.redirect()
        self.abort(404, 'No such content suggestion')

