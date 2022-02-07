import uuid

from django.db import models

from django_extensions.db.models import TitleSlugDescriptionModel


# Create your models here.
class Athlete(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.get_full_name()


class Sport(TitleSlugDescriptionModel, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athletes = models.ManyToManyField(Athlete, through="Progress")

    def __str__(self) -> str:
        return self.title


class Progress(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    date_started = models.DateField(auto_now_add=True)
