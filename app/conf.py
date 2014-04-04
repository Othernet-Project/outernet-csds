""" CSDS application configuration

This module contains configuration settings for the CSDS components.

"""


class AdaptorsSettings(object):
    """ Configuration for the Request Hub Adaptors """

    # Outernet Facebook Adaptor
    OFB_APP_ID = ''
    OFB_APP_SECRET = ''
    OFB_PAGE_ID = '208511276012855'  # https://www.facebook.com/OuternetForAll


class Base(AdaptorsSettings, object):
    """ Base configuration """
    DEBUG = False
    TeSTING = False


class Testing(Base):
    """ Testing configuration """
    TESTING = True


class Development(Base):
    """ Local development configuration """
    DEBUG = True


class Production(Base):
    """ Production configuration """
    pass
