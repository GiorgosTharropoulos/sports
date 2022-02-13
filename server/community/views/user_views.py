import marshmallow
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from community.services import user_service
from errors import domain_errors
from errors.domain_errors import UserDoesNotExistsError
from permissions import IsAdminOrOwner
from utils.error_utils import (
    get_business_requirement_error_messages,
    get_validation_error_response,
)
from utils import viewset_utils
from utils.sanitization_utils import strip_xss


class UserViewSet(viewset_utils.ViewSetActionPermissionMixin, ViewSet):
    permission_action_classes = {
        "get": [IsAuthenticated],
        "delete": [IsAdminUser],
        "update": [IsAuthenticated, IsAdminOrOwner],
    }

    def get(self, request, pk):
        try:
            user_model = user_service.get(user_id=pk)
        except domain_errors.UserDoesNotExistsError as e:
            return get_business_requirement_error_messages(e, status.HTTP_404_NOT_FOUND)

        resp = user_service.get_user_profile(user_model)

        return Response(data={"data": resp}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # If the user tries to delete themselves raise an error.
        if request.user.id == pk:
            return get_business_requirement_error_messages(
                domain_errors.YouCannotDeleteYourselfError(),
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_service.remove_user(pk)
        except UserDoesNotExistsError as e:
            return get_business_requirement_error_messages(e, status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        try:
            user_model = user_service.get(user_id=pk)

            self.check_object_permissions(request, user_model)

            unsafe_username = request.data.get("username", user_model.username)
            unsafe_first_name = request.data.get("first_name", user_model.first_name)
            unsafe_last_name = request.data.get("last_name", user_model.last_name)

            safe_username = strip_xss(unsafe_username)
            safe_first_name = strip_xss(unsafe_first_name)
            safe_last_name = strip_xss(unsafe_last_name)

            user_service.update_user_profile_by_id(
                pk, safe_username, safe_first_name, safe_last_name
            )
        except marshmallow.ValidationError as e:
            return get_validation_error_response(
                e, status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except domain_errors.UserDoesNotExistsError as e:
            return get_business_requirement_error_messages(e, status.HTTP_404_NOT_FOUND)
        except domain_errors.CannotEditUserError as e:
            return get_business_requirement_error_messages(e, status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GetMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_model = request.user

        resp = user_service.get_user_profile(user_model)

        return Response(data={"data": resp}, status=status.HTTP_200_OK)
