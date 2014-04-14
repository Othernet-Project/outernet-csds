""" CSDS application configuration

This module contains configuration settings for the CSDS components.

"""


class AdaptorsSettings(object):
    """ Configuration for the Request Hub Adaptors """

    # Outernet Facebook Adaptor
    OFB_APP_ID = '$FB_APP_ID'
    OFB_APP_SECRET = '$FB_APP_SECRET'
    OFB_PAGE_ID = '208511276012855'  # https://www.facebook.com/OuternetForAll
    EML_API_ID = '$EML_UNAME'
    EML_API_KEY = '$EML_KEY'
    EML_API_SIGNATURE = '$EML_SIGN'
    EML_ADDRESS = 'request@csds.outernet.is'


class Base(AdaptorsSettings, object):
    """ Base configuration """
    DEBUG = False
    TESTING = False
    SECRET = '$SECRET'


class Testing(Base):
    """ Testing configuration """
    TESTING = True


class Development(Base):
    """ Local development configuration """
    DEBUG = True


class Production(Base):
    """ Production configuration """
    pass
