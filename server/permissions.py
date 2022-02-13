from django.db import models

from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission


class IsAdminOrOwner(BasePermission):
    """
    The admin or the owner has access.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: models.Model):
        if request.user.is_superuser:
            return True

        if hasattr(obj, "user_model"):
            if obj.user_model == request.user:
                return True

        if obj == request.user:
            return True

        return False
