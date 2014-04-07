""" CDS forms

This module implements classes for working with content-related forms.

"""

from __future__ import unicode_literals, print_function

from utils.forms import Form


class ContentForm(Form):
    """ Handles validation and rendering of the content form """

    template_name = 'cds/_content_form.html'
