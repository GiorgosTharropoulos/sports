from rest_framework.response import Response
import marshmallow

from errors.domain_errors import IBusinessError


def get_validation_error_response(
    validation_error: marshmallow.ValidationError,
    http_status_code: int,
    display_error="",
) -> Response:
    resp = {
        "errors": {
            "display_error": display_error,
            "field_errors": validation_error.normalized_messages(),
        }
    }

    return Response(data=resp, status=http_status_code)


def get_business_requirement_error_messages(
    business_logic_error: IBusinessError, http_status_code: int
) -> Response:
    resp = {
        "errors": {
            "display_error": business_logic_error.message,
            "internal_error_code": business_logic_error.internal_code,
        }
    }

    return Response(data=resp, status=http_status_code)
