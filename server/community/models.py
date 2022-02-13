from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class EmailAddress(models.Model):
    user_model = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.email)

    class Meta:
        unique_together = (("user_model", "is_primary"),)
