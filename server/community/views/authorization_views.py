import marshmallow
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView


from community.serializers import TokenSerializer
from utils.sanitization_utils import strip_xss, string_to_boolean
from utils.error_utils import (
    get_business_requirement_error_messages,
    get_validation_error_response,
)
from errors import domain_errors
from community.services import user_service


class LogInView(TokenObtainPairView):
    serializer_class = TokenSerializer


class SignUpView(APIView):
    def post(self, request: Request) -> Response:
        unsafe_first_name = request.data.get("first_name", "")
        unsafe_last_name = request.data.get("last_name", "")
        unsafe_username = request.data.get("username", "")
        unsafe_email = request.data.get("email", "")
        unsafe_terms_of_service = request.data.get("terms_of_service", None)
        unsafe_password = request.data.get("password", "")

        safe_first_name = strip_xss(unsafe_first_name)
        safe_last_name = strip_xss(unsafe_last_name)
        safe_username = strip_xss(unsafe_username)
        safe_email = strip_xss(unsafe_email)
        safe_terms_of_service = string_to_boolean(unsafe_terms_of_service)

        try:
            user_model, auth_token = user_service.create_user(
                safe_username=safe_username,
                unsafe_password=unsafe_password,
                safe_email=safe_email,
                safe_terms_of_service=safe_terms_of_service,
                safe_first_name=safe_first_name,
                safe_last_name=safe_last_name,
            )
        except marshmallow.ValidationError as e:
            return get_validation_error_response(
                validation_error=e,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except domain_errors.UsernameAlreadyExistsError as e:
            return get_business_requirement_error_messages(e, status.HTTP_409_CONFLICT)
        except domain_errors.EmailAddressAlreadyExistsError as e:
            return get_business_requirement_error_messages(e, status.HTTP_409_CONFLICT)
        except domain_errors.TermsNotAcceptedError as e:
            return get_business_requirement_error_messages(
                e, status.HTTP_429_TOO_MANY_REQUESTS
            )

        resp = {"data": {"auth_token": auth_token, "user_id": user_model.id}}
        return Response(data=resp, status=status.HTTP_201_CREATED)
