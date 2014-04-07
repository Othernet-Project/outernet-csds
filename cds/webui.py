""" Content Discovery Subsystem web interface

This module implements the CDS web interface. The interface exposes requests to
community members so content suggestions can be made.

"""

from __future__ import unicode_literals, print_function

from google.appengine.ext import ndb
from utils.routes import HtmlRoute, FormRoute

from rh.db import Request, Content

from .forms import ContentForm


class WebUIList(HtmlRoute):
    name = 'cds_webui_list'
    path = '/cds/'
    template_name = 'cds/list.html'

    def get_context(self):
        ctx = super(WebUIList, self).get_context()
        ctx['requests'] = Request.fetch_cds_requests()
        return ctx


class WebUIRequest(FormRoute):
    name = 'cds_webui_request'
    path = '/cds/<int:request_id>'
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
        content = Content(url=url, parent=self.req.key)
        content.put()
        return super(WebUIRequest, self).form_valid()

    def get_context(self):
        ctx = super(WebUIRequest, self).get_context()
        ctx['req'] = self.req
        contents = Content.query(ancestor=self.req.key).order(
            -Content.submitted).fetch()
        ctx['contents'] = contents
        ctx['count'] = len(contents)
        return ctx

