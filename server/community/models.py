from datetime import datetime
from typing import Sequence
from uuid import UUID, uuid4

from django.db import models
from django_extensions.db.models import TitleSlugDescriptionModel

from users.models import User


# Create your models here.
class Athlete(models.Model):
    id: UUID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created: datetime = models.DateTimeField(auto_now_add=True)
    updated: datetime = models.DateTimeField(auto_now=True)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.get_full_name()


class Sport(TitleSlugDescriptionModel, models.Model):
    id: UUID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    athletes: Sequence[Athlete] = models.ManyToManyField(Athlete, through="Progress")

    def __str__(self) -> str:
        return self.title


class Progress(models.Model):
    athlete: Athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    sport: Sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    date_started = models.DateField(auto_now_add=True)
