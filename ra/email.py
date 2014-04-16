""" Outernet Email adaptor

This adaptor collects requests from emails sent to request@csds.outernet.is
using Mandrill Webhook.

Because this is a hook-based adaptor, it has no cron job. It stores requests
one by one as they are received.

"""

from __future__ import unicode_literals, print_function

import datetime
import json
import collections
import base64
import hmac
from hashlib import sha1
import re

from google.appengine.ext import ndb
from flask import current_app as app
from utils.routes import Route

from rh.adaptors import Adaptor
from rh.requests import Request
from rh.db import HarvestHistory


class OuternetEmailAdaptor(Adaptor):
    """ Outernet Email Adaptor

    This adaptor collects messages sent to request@csds.outernet.is and
    persists them as requests.

    """

    name = 'outernet-email'
    source = 'request@csds.outernet.is'
    contact = 'hello@outernet.com'
    trusted = True

    # Lines that signfiy beginnings for signatures
    SIG_LINES = (
        re.compile(r'\s*---*\s*$', re.M), # Classic -- sig
        re.compile(r'\s*Sent from [a-zA-Z ]*\s*$', re.M), # iPhone and similar
    )

    def __init__(self, data):
        self.api_id = app.config['EML_API_ID']
        self.api_key = app.config['EML_API_KEY']
        self.data = json.loads(data)

    def get_requests(self, last_access=None):
        # TODO: Accept image attachments as well. The attachments are stored in
        # attachments key, and has the following structure:
        #
        #     {
        #       'name':    (string) filename
        #       'type':    (string) mime type
        #       'content': (string) content of the attachment
        #       'base64':  (bool) whether attachment is base-64-encoded (this
        #                  includes non-UTF-8 characters
        #     }
        #
        # More about the inbound hook format: http://bit.ly/1kpcYlt
        requests = []
        for d in self.data:
            timestamp = d['ts']
            # TODO: We currently only handle text portion of the message body. The
            # message may be HTML-only, although we assume this is rare. This case
            # should be checked and HTML message extracted and converted to text.
            # The HTML message is stored in ``message['html']``.
            body = self.strip_sig(d['msg']['text'])
            requests.append(Request(
                adaptor=self,
                content=body,
                timestamp=datetime.datetime.fromtimestamp(timestamp),
                content_format=Request.TEXT,
                world=Request.ONLINE
            ))
        return requests

    def strip_sig(self, msg):
        """ Strip signature from plain-text emails

        This is a (currently) very crude method for stripping signatures. It
        basically strips out any text below and including two or more dashes.

        It also strips lines below 'Sent from' followed by any number of
        letters and spaces, including the line.

        """
        for s in self.SIG_LINES:
            msg = ''.join(s.split(msg)[0:-1])
        return msg


class EmailHook(Route):
    name = 'rh_hook_email'
    path = '/rh/hooks/email'

    def get_adaptor(self):
        """ Get an adaptor instance """
        return OuternetEmailAdaptor(self.request.form['mandrill_events'])

    def hmac_b64(self, s):
        """ Create Base-64-encoded HMAC-SHA1 digest of given string """
        key = self.app.config['EML_API_SIGNATURE']
        binary = hmac.new(key, s, sha1)
        return base64.b64encode(binary.digest())

    def verify_signature(self):
        """ Verifies the mandrill signature

        You can find out more about how this works from here:
        http://bit.ly/1hO6Cqe
        """

        signature = self.request.headers.get('X-Mandrill-Signature')
        self.log.debug('Checking signature %s' % signature)
        # Get full request URL that was used
        url = self.request.url
        # Add all parameters to the URL
        params = sorted(self.request.form.items())
        for param in params:
            url += param[0]
            url += param[1]
        hmac_b64 = self.hmac_b64(url)
        self.log.debug('Generated signature %s' % hmac_b64)
        return hmac_b64 == signature

    def POST(self):
        if not self.verify_signature():
            self.log.debug('Signature verification failed')
            # Request isn't coming from Mandrill, so we just pretent it
            # succeeded.
            return 'OK'
        self.log.debug('Signature verification passed')
        adaptor = self.get_adaptor()
        requests = adaptor.get_requests()
        clean = []
        for r in requests:
            try:
                r.check()
                clean.append(r.prepare())
            except r.RequestError as err:
                self.log.exception('Request error: %s' % err)
        self.log.info('Prepared %s email reqeusts' % len(clean))
        ndb.put_multi(clean)
        return 'OK'

