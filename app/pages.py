""" Misc pages

This module implements handlers for miscellaneous pages that aren't part of
web-based interfaces of other CSDS components.

"""

from __future__ import unicode_literals, print_function

from utils.routes import HtmlRoute


class Homepage(HtmlRoute):
    path = '/'
    template_name = 'home.html'

