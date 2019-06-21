"""
operatorcourier.errors

Defines custom operator-courier exceptions.
"""
from requests import RequestException


class OpCourierError(Exception):
    """Base class for all operator-courier exceptions"""
    pass


class OpCourierValueError(OpCourierError, ValueError):
    """Base class for exceptions that need to inherit from ValueError
    for backwards compatibility
    """
    pass


class OpCourierBadYaml(OpCourierValueError):
    """Invalid yaml file"""
    pass


class OpCourierBadBundle(OpCourierValueError):
    """Invalid bundle (e.g. missing CSV/CRD/Package).
    Contains the info collected during validation of the bundle.
    """
    def __init__(self, msg, validation_info):
        """
        :param msg: the message of this exception
        :param validation_info: info collected during validation of bundle
        """
        super().__init__(msg)
        self.validation_info = validation_info


class OpCourierQuayError(OpCourierError):
    """An error occurred while pushing bundle to Quay.io"""
    pass


class OpCourierQuayCommunicationError(OpCourierQuayError, RequestException):
    """Communication with Quay.io failed"""
    pass


class OpCourierQuayErrorResponse(OpCourierQuayError, OpCourierValueError):
    """Quay.io responded with an error"""
    def __init__(self, msg, code, error_response):
        """
        :param msg: the message of this exception
        :param code: http status code returned by response
        :param error_response: error json taken from response
        """
        super().__init__(msg)
        self.code = code
        self.error_response = error_response
