""" Content Selection Subsystem web interface

This module implements the CSS's web interface. The interface exposes endpoints
for voting on requests and displaying voting results.
"""

from __future__ import unicode_literals, print_function

from google.appengine.ext import ndb
from utils.routes import RedirectMixin, Route
from werkzeug.urls import url_unquote_plus


class WebUIVote(RedirectMixin, Route):
    name = 'css_webui_vote'
    path = '/requests/<int:request_id>/suggestions/<url>/votes'

    def get_redirect_url(self):
        return self.url_for('cds_webui_request',
                            request_id=self.kwargs['request_id'])

    def PUT(self, request_id, url):
        url = url_unquote_plus(url)
        self.content = ndb.Key('Request', request_id, 'Content', url).get()
        if self.content is None:
            self.abort(404, 'No such content')
        self.content.votes += 1
        self.content.put()
        return self.redirect()
