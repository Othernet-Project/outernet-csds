""" Request hub exceptions

This module contains exceptions raised by the request hub system.

"""


class RequestHubError(Exception):
    """ Generic request hub error """
    pass


class RequestError(RequestHubError):
    """ Generic request error """
    pass


class RequestDataError(RequestError):
    """ Exception raised when request data is not valid """
    pass


class BinaryDecodeError(RequestError):
    """ Exception raised when binary data cannot be decoded """
    pass


class ImageDecodeError(RequestError):
    """ Exception raised when image data cannot be loaded from string """
    pass


class ImageFormatError(RequestError):
    """ Raised if image file is invalid or not in supported format """
    pass


class DuplicateSuggestionError(RequestHubError):
    """ Raised if duplicate content suggestion is made """
    pass
