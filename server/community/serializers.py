from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from rest_framework import serializers

from users.serializers import UserDTO, UserSerializer

from .models import Athlete, Sport


class AthleteSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Athlete
        fields = "__all__"


@dataclass
class AthleteDTO:
    id: UUID
    created: datetime
    updated: datetime
    user: UserDTO


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ("id", "title", "description", "slug")
        read_only_fields = ("id",)


@dataclass
class SportDTO:
    id: UUID
    title: str
    description: str
    slug: str
