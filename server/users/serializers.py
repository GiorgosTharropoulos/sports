import datetime
from typing import TypedDict

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenPair(TypedDict):
    access: str
    refresh: str


class UserDTO(TypedDict):
    username: str
    first_name: str
    last_name: str
    email: str
    is_staff: bool
    email: str
    is_active: bool
    date_joined: datetime.datetime


class UserIn(UserDTO):
    password1: str
    password2: str


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data: UserIn) -> UserIn:
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match.")
        return data

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "password1", "password2", "first_name", "last_name")
        read_only_fields = ("id",)


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token: TokenPair = super().get_token(user)
        user_data: UserDTO = UserSerializer(user).data
        for key, value in user_data.items():
            if key != "id":
                token[key] = value
        return token
