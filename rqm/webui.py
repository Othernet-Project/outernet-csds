""" Request Query Manager web interface

This module implements the RQM web interface. The interface exposes forms for
modifying requests.

"""

from __future__ import unicode_literals, print_function

from google.appengine.ext import ndb
from utils.routes import FormRoute

from .forms import ProofForm


class WebUIProof(FormRoute):
    name = 'rqm_webui_proof'
    path = '/requests/<int:request_id>/proof'
    form_class = ProofForm
    template_name = 'rqm/proof.html'

    def PATCH(self, request_id):
        revision = self.request.form['revision']
        try:
            revision = int(revision)
        except ValueError:
            self.abort(400, 'Invalid revision number')
        if 0 > revision > self.req.current_revision:
            self.abort(400, 'Revision number out of bounds')
        self.req.current_revision = revision
        self.req.put()
        return self.redirect()

    def get_form_defaults(self):
        try:
            return self.req.content.to_dict()
        except AttributeError:
            # Most likely missing content, so we return empty dict instead
            return {}

    def on_dispatch(self):
        self.req = ndb.Key('Request', int(self.kwargs['request_id'])).get()
        if not self.req:
            self.abort(404)

    def get_context(self):
        ctx = super(WebUIProof, self).get_context()
        ctx['req'] = self.req
        return ctx

    def get_redirect_url(self):
        return self.url_for('cds_webui_request',
                            request_id=self.req.key.id())

    def form_valid(self):
        content = self.form.valid_data.copy()
        content.pop('_csrf_token')
        print(content)
        self.req.set_content(**content)
        self.req.put()
        return super(WebUIProof, self).form_valid()
