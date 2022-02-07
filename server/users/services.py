from django.contrib.auth import get_user_model

from .models import User
from .serializers import UserDTO, UserIn, UserSerializer


class UserService:
    model: User = get_user_model()
    serializer: UserSerializer

    def create(self, data: UserIn) -> UserDTO:
        serialized = UserSerializer(data=data)
        if serialized.is_valid(raise_exception=True):
            user: User = self.model.objects.create_user(**serialized.data)
            return UserSerializer(instance=user).data


user_service = UserService()
