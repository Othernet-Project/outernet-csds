""" RQM forms

This module implements classes for Request Query Manager forms.


"""

from __future__ import unicode_literals, print_function

from operator import itemgetter
import locale

from babel import localedata, Locale
from utils.forms import Form
from utils.schemabuilder import DEFAULT_VALIDATORS
import formencode

from rh.db import RequestConstants

locale.setlocale(locale.LC_ALL, '')

LOCALES = localedata.locale_identifiers()
LANGUAGES = [(l, Locale(l).get_language_name()) for l in LOCALES
             if Locale(l).get_language_name() is not None]
LANGUAGES.sort(key=itemgetter(1), cmp=locale.strcoll)
TOPICS = RequestConstants.TOPICS


class Enumerated(formencode.validators.FancyValidator):
    """ Generic validator that rejects values not found in specified list """

    messages = {'invalid': '%(val)s is not a valid option'}
    choices = []

    def _validate_other(self, value, state):
        value = unicode(value)
        if value not in self.choices:
            raise formencode.Invalid(self.message('invalid', state, val=value),
                                     value, state)

    _validate_python = _validate_other



class Locale(Enumerated):
    """ Locale validator """
    messages = {'invalid': '%(val)s is not a recognized locale'}
    choices = LOCALES


class Topic(Enumerated):
    """ Topic validator """
    messages = {'invalid': '%(val)s is not a valid topic'}
    choices = TOPICS


validators = DEFAULT_VALIDATORS.copy()
validators.update({
    'locale': Locale,
    'topic': Topic
})


class ProofForm(Form):

    extras = {
        'languages': LANGUAGES,
        'topics': [(t, t) for t in TOPICS]
    }
    validators = validators
    template_name = 'rqm/_proof_form.html'

