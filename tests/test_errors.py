import pytest
from requests import RequestException

from operatorcourier.errors import (
    OpCourierError,
    OpCourierValueError,

    OpCourierBadYaml,
    OpCourierBadBundle,

    OpCourierQuayError,
    OpCourierQuayCommunicationError,
    OpCourierQuayErrorResponse
)


@pytest.mark.parametrize('op_courier_exception', [
    OpCourierValueError,

    OpCourierBadYaml,
    OpCourierBadBundle,

    OpCourierQuayErrorResponse
])
def test_value_error_compatibility(op_courier_exception):
    """Test that exceptions replacing ValueError are backwards compatible."""
    assert issubclass(op_courier_exception, ValueError)


@pytest.mark.parametrize('op_courier_exception', [
    OpCourierQuayCommunicationError
])
def test_request_exception_compatibility(op_courier_exception):
    """Test that exceptions replacing RequestException are backwards compatible"""
    assert (
        issubclass(op_courier_exception, RequestException)
        and not issubclass(op_courier_exception, ValueError)
    )


@pytest.mark.parametrize('op_courier_exception', [
    OpCourierValueError,

    OpCourierBadYaml,
    OpCourierBadBundle,

    OpCourierQuayError,
    OpCourierQuayCommunicationError,
    OpCourierQuayErrorResponse
])
def test_base_exception_inheritance(op_courier_exception):
    """Test that all exceptions are subclasses of the base exception"""
    assert issubclass(op_courier_exception, OpCourierError)


@pytest.mark.parametrize('op_courier_exception', [
    OpCourierQuayCommunicationError,
    OpCourierQuayErrorResponse
])
def test_quay_exception_inheritance(op_courier_exception):
    """Test that quay exceptions are subclasses of the base quay exception"""
    assert issubclass(op_courier_exception, OpCourierQuayError)


def test_create_quay_error_response():
    """Test that creation of quay error responses is working as intended"""
    e = OpCourierQuayErrorResponse('oh no', 500, {'error': 'uh oh'})
    assert str(e) == 'oh no'
    assert e.code == 500
    assert e.error_response == {'error': 'uh oh'}
