from factory.django import DjangoModelFactory
from community.services import user_service
from community.models import *


class UserFactory(DjangoModelFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        username = kwargs.pop("username")
        email = kwargs.pop("email")
        password = kwargs.pop("password", "1234567a")
        terms_of_service_accepted = kwargs.pop("terms_of_service_accepted", True)

        user_model, _ = user_service.create_user(
            safe_username=username,
            safe_email=email,
            unsafe_password=password,
            safe_terms_of_service=terms_of_service_accepted,
        )

        if kwargs:
            for kwarg, value in kwargs.items():
                setattr(user_model, kwarg, value)

        user_model.save()

        return user_model

    class Meta:
        model = User


class EmailAddressFactory(DjangoModelFactory):
    class Meta:
        model = EmailAddress
