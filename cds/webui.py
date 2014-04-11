""" Content Discovery Subsystem web interface

This module implements the CDS web interface. The interface exposes requests to
community members so content suggestions can be made.

"""

from __future__ import unicode_literals, print_function

import urllib2

from google.appengine.ext import ndb
from utils.routes import HtmlRoute, FormRoute

from rh.db import Request, Content

from .forms import ContentForm


class WebUIList(HtmlRoute):
    name = 'cds_webui_list'
    path = '/requests/'
    template_name = 'cds/list.html'

    def get_context(self):
        ctx = super(WebUIList, self).get_context()
        ctx['requests'] = Request.fetch_cds_requests()
        return ctx


class WebUIRequest(FormRoute):
    name = 'cds_webui_request'
    path = '/requests/<int:request_id>'
    template_name = 'cds/request.html'
    form_class = ContentForm

    def on_dispatch(self):
        key = ndb.Key('Request', int(self.kwargs['request_id']))
        req = key.get()
        if not req:
            self.abort(404, details='Request not found')
        self.req = req

    def get_redirect_url(self):
        return self.url_for('cds_webui_request', request_id=self.req.key.id())

    def form_valid(self):
        url = self.form.valid_data['url']

        try:
            self.req.suggest_url(url)
        except self.req.DuplicateSuggestionError:
            self.form.errors['url'] = ('This page has already been '
                'suggested.')
            return self.form_invalid()

        try:
            urllib2.urlopen(url, timeout=10)
        except urllib2.HTTPError:
            self.form.errors['url'] = ('This URL could not be opened.')
            return self.form_invalid()

        self.req.put()
        return super(WebUIRequest, self).form_valid()

    def get_context(self):
        ctx = super(WebUIRequest, self).get_context()
        ctx['req'] = self.req
        contents = Content.query(ancestor=self.req.key).order(
            -Content.votes, -Content.submitted).fetch()
        ctx['contents'] = contents
        ctx['count'] = len(contents)
        try:
            rev = int(self.request.args.get('rev'))
        except TypeError, ValueError:
            rev = None
        ctx['rev'] = rev
        if rev is None:
            ctx['content'] = self.req.content
        else:
            ctx['content'] = self.req.get_rev(rev)
        return ctx

