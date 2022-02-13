from typing import TYPE_CHECKING, TypedDict, Any

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken


from community.models import EmailAddress
from community.schemas.user_validators import UserCreationValidator, UserUpdateValidator
from errors import domain_errors

if TYPE_CHECKING:
    from community.models import User


class TokenResponse(TypedDict):
    refresh: str
    access: str


class UserService:
    def update_or_create_email_address(
        self, user_model: "User", email: str, is_primary: bool, is_verified: bool
    ) -> None:
        with transaction.atomic():

            (
                email_address_model,
                _,
            ) = EmailAddress.objects.select_for_update().get_or_create(
                email=email, defaults={"user_model": user_model}
            )

            if (
                email_address_model.is_verified
                and email_address_model.user_model.id != user_model.id
            ):
                raise domain_errors.EmailAddressAlreadyExistsError()

            email_address_model.user_model = user_model
            email_address_model.email = email
            email_address_model.is_verified = is_verified
            email_address_model.is_primary = is_primary
            email_address_model.save()

            # If a user successfully adds a linked email address, delete other users
            # who have it as an email address
            get_user_model().objects.filter(email=email).exclude(
                id=user_model.id
            ).delete()

    def create_user(
        self,
        safe_username: str,
        unsafe_password: str,
        safe_email: str,
        safe_terms_of_service: bool,
        safe_first_name: str = "",
        safe_last_name: str = "",
    ) -> tuple["User", str]:
        fields_to_validate_dict = {
            "first_name": safe_first_name,
            "last_name": safe_last_name,
            "username": safe_username,
            "password": unsafe_password,
            "email": safe_email,
            "terms_of_service": safe_terms_of_service,
        }

        UserCreationValidator().load(fields_to_validate_dict)

        if not safe_terms_of_service:
            raise domain_errors.TermsNotAcceptedError()

        if get_user_model().objects.filter(username=safe_username).exists():
            raise domain_errors.UsernameAlreadyExistsError()

        if EmailAddress.objects.filter(email=safe_email, is_verified=True).exists():
            raise domain_errors.EmailAddressAlreadyExistsError()

        with transaction.atomic():
            user_model: "User" = get_user_model().objects.create_user(
                username=safe_username,
                email=safe_email,
                password=unsafe_password,
                first_name=safe_first_name,
                last_name=safe_last_name,
            )
            user_model.full_clean()
            user_model.save()

            self.update_or_create_email_address(
                user_model, safe_email, is_primary=True, is_verified=False
            )

        access_token = self.create_access_token(user_model)["access"]
        return (user_model, access_token)

    def create_access_token(self, user_model: "User") -> TokenResponse:
        refresh = RefreshToken.for_user(user_model)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def remove_user(self, user_id: int) -> None:
        if not self.does_user_exists(user_id):
            raise domain_errors.UserDoesNotExistsError()

        with transaction.atomic():
            user_model: "User" = (
                get_user_model().objects.select_for_update().get(pk=user_id)
            )
            user_model.delete()

    def get_user_profile(self, user_model: "User") -> dict[str, Any]:
        return {
            "first_name": user_model.first_name,
            "last_name": user_model.last_name,
            "username": user_model.username,
            "email": user_model.email,
            "date_joined": user_model.date_joined.isoformat(),
        }

    def update_user_profile_by_id(
        self,
        user_id: int,
        safe_username: str,
        safe_first_name: str,
        safe_last_name: str,
    ) -> "User":

        fields_to_validate = {
            "username": safe_username,
            "first_name": safe_first_name,
            "last_name": safe_last_name,
        }

        UserUpdateValidator().load(fields_to_validate, partial=("username",))

        if not self.does_user_exists(user_id):
            raise domain_errors.UserDoesNotExistsError()

        if get_user_model().objects.filter(username=safe_username).exclude(id=user_id):
            raise domain_errors.UsernameAlreadyExistsError()

        with transaction.atomic():
            db_user_model: "User" = (
                get_user_model().objects.select_for_update().get(pk=user_id)
            )
            if len(safe_username) > 0:
                db_user_model.username = safe_username
            if len(safe_first_name) > 0:
                db_user_model.first_name = safe_first_name
            if len(safe_last_name) > 0:
                db_user_model.last_name = safe_last_name
            db_user_model.full_clean(exclude=["username"])
            db_user_model.save(update_fields=["username", "first_name", "last_name"])

        return db_user_model

    def does_user_exists(self, user_id: int) -> bool:
        return get_user_model().objects.filter(id=user_id).exists()

    def get(self, user_id: int) -> "User":
        if not self.does_user_exists(user_id=user_id):
            raise domain_errors.UserDoesNotExistsError()

        return get_user_model().objects.get(id=user_id)


user_service = UserService()
