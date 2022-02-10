from typing import Sequence
from uuid import UUID
from django.contrib.auth import get_user_model

from .models import User
from .serializers import UserDTO, UserIn, UserInSerializer


class UserService:
    model: User = get_user_model()
    serializer: UserInSerializer

    def create(self, data: UserIn) -> UserDTO | None:
        serialized = UserInSerializer(data=data)
        if serialized.is_valid(raise_exception=True):
            user: User = self.model.objects.create_user(**serialized.data)
            return UserInSerializer(instance=user).data
        return None

    def get(
        self,
        *,
        pk: str | UUID | None = None,
        username: str | None = None,
    ) -> User | None:
        if (pk is None) and (username is None):
            raise TypeError("Both the primary key and the username was set to None")

        if pk is not None:
            try:
                user_obj: User = self.model.objects.get(pk=pk)
                return user_obj
            except self.model.DoesNotExist:
                return None

        if username is not None:
            users: Sequence[User] = self.model.objects.filter(username=username)
            if not users:
                return None

            return users[0]

        # This return statement will never be reached, Mypy is expecting a return
        # statement nevertheless
        return None


user_service = UserService()
