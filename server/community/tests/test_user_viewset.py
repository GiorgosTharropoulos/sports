from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate
import faker

import community.views.user_views
from utils.test_utils import *
from community.models import User


class UserTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.delete_view = community.views.user_views.UserViewSet.as_view(
            {"delete": "delete"}
        )
        self.update_view = community.views.user_views.UserViewSet.as_view(
            {"put": "update"}
        )
        self.get_view = community.views.user_views.UserViewSet.as_view({"get": "get"})
        self.fake = faker.Faker()

        self.maxDiff = None

    def test_admin_can_delete_user(self):
        admin = UserFactory(
            username="aoeu", email="example@example.com", is_admin=True, is_staff=True
        )
        UserFactory(username="todelete", email="delete@example.com")

        user_id = User.objects.last().id

        request = self.factory.delete(f"/api/users/{user_id}/")
        force_authenticate(request, admin)

        with self.assertNumQueries(9):
            response = self.delete_view(request, user_id)

        self.assertEqual(response.status_code, 204)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, EmailAddress.objects.count())

    def test_admin_cannot_delete_user_that_does_not_exists(self):
        admin = UserFactory(
            username="admin", email="example@example.com", is_admin=True, is_staff=True
        )

        request = self.factory.delete("/api/users/10000/")
        force_authenticate(request, admin)

        with self.assertNumQueries(1):
            response = self.delete_view(request, 10000)

        expected_response = {
            "errors": {
                "display_error": "User does not exists.",
                "internal_error_code": 40401,
            }
        }

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, expected_response)

    def test_only_admins_can_delete_users(self):
        non_admin = UserFactory(username="noadmin", email="email@example.com")
        to_delete = UserFactory(username="delete", email="delete@example.com")

        request = self.factory.delete(f"/api/users/{to_delete.id}/")
        force_authenticate(request, non_admin)

        with self.assertNumQueries(0):
            response = self.delete_view(request, to_delete.id)

        expected_response = {
            "detail": "You do not have permission to perform this action."
        }

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, expected_response)

        self.assertEqual(2, User.objects.count())
        self.assertEqual(2, EmailAddress.objects.count())

    def test_only_authenticated_users_can_delete_users(self):
        to_delete = UserFactory(username="delete", email="delete@example.com")

        request = self.factory.delete(f"/api/users/{to_delete.id}/")

        with self.assertNumQueries(0):
            response = self.delete_view(request, to_delete.id)

        expected_response = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, expected_response)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, EmailAddress.objects.count())

    def test_admins_cant_delete_themselves(self):
        admin_model = UserFactory(
            username="admin", email="example@example.com", is_admin=True, is_staff=True
        )

        request = self.factory.delete(f"/api/users/{admin_model.id}/")
        force_authenticate(request, admin_model)

        with self.assertNumQueries(0):
            response = self.delete_view(request, admin_model.id)

        expected_response = {
            "errors": {
                "display_error": "You can not delete yourself.",
                "internal_error_code": 40001,
            }
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_response)

    def test_successfully_update_user_profile(self):
        UserFactory(username=self.fake.user_name(), email=self.fake.email())

        user_model = User.objects.last()

        put_request_data = {
            "username": "changed",
            "first_name": "Jeff",
            "last_name": "Maxwell",
        }

        request = self.factory.put(f"api/users/{user_model.id}", data=put_request_data)
        force_authenticate(request, user_model)

        with self.assertNumQueries(8):
            response = self.update_view(request, user_model.id)

        user_model.refresh_from_db()

        self.assertEqual(response.status_code, 204)

        user_model.refresh_from_db()

        self.assertEqual(user_model.username, "changed")
        self.assertEqual(user_model.first_name, "Jeff")
        self.assertEqual(user_model.last_name, "Maxwell")

    def test_successfully_partially_update_user_profile(self):
        UserFactory(
            username="username",
            email="example@example.com",
            first_name="Jeff",
            last_name="Maxwell",
        )

        put_request_data = {
            "first_name": "Josh",
        }

        user_model = User.objects.last()

        request = self.factory.put(f"api/users/{user_model.id}", data=put_request_data)
        force_authenticate(request, user_model)

        with self.assertNumQueries(8):
            response = self.update_view(request, user_model.id)

        user_model.refresh_from_db()

        self.assertEqual(response.status_code, 204)

        self.assertEqual(user_model.username, "username")
        self.assertEqual(user_model.first_name, "Josh")
        self.assertEqual(user_model.last_name, "Maxwell")

    def test_user_cant_update_others_user_profile(self):
        UserFactory(
            username="jeff",
            email="example@example.com",
            first_name="Jeff",
            last_name="Maxwell",
        )
        UserFactory(
            username="josh",
            email="example2@example.com",
            first_name="Josh",
            last_name="Maxwell",
        )

        jeff = User.objects.get(username="jeff")
        josh = User.objects.get(username="josh")

        put_request_data = {
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
        }

        request = self.factory.put(f"api/users/{josh.id}", data=put_request_data)
        force_authenticate(request, jeff)

        expected_response = {
            "detail": "You do not have permission to perform this action."
        }

        with self.assertNumQueries(2):
            response = self.update_view(request, josh.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, expected_response)

    def test_admins_can_update_other_user_profile(self):
        admin_user_model = UserFactory(
            username="admin",
            email="admin@example.com",
            first_name="Jeff",
            last_name="Maxwell",
            is_superuser=True,
        )
        UserFactory(
            username="josh",
            email="example2@example.com",
            first_name="Josh",
            last_name="Maxwell",
        )

        user_model = User.objects.last()

        put_request_data = {
            "first_name": "changed_first_name",
            "last_name": "changed_last_name",
            "username": "changed_username",
        }

        request = self.factory.put(f"api/users/{user_model.id}", data=put_request_data)
        force_authenticate(request, admin_user_model)

        with self.assertNumQueries(8):
            response = self.update_view(request, user_model.id)

        user_model.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(user_model.first_name, "changed_first_name")
        self.assertEqual(user_model.last_name, "changed_last_name")
        self.assertEqual(user_model.username, "changed_username")

    def test_can_retrieve_user_profile_successfully(self):
        UserFactory(
            username="josh",
            email="josh@example.com",
            first_name="Josh",
            last_name="Maxwell",
        )

        user_model = User.objects.last()

        request = self.factory.get(f"api/users/{user_model.id}")
        force_authenticate(request, user_model)

        with self.assertNumQueries(2):
            response = self.get_view(request, user_model.id)

        expected_response = {
            "data": {
                "username": "josh",
                "first_name": "Josh",
                "last_name": "Maxwell",
                "email": "josh@example.com",
            }
        }

        response.data["data"].pop("date_joined")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_can_retrieve_others_user_profile(self):
        UserFactory(
            username="josh",
            email="josh@example.com",
            first_name="Josh",
            last_name="Maxwell",
        )
        UserFactory(
            username="john",
            email="john@example.com",
            first_name="John",
            last_name="Maxwell",
        )

        user_model = User.objects.last()
        user_model_to_retrieve = User.objects.get(username="josh")

        request = self.factory.get(f"api/users/{user_model_to_retrieve.id}")
        force_authenticate(request, user_model)

        with self.assertNumQueries(2):
            response = self.get_view(request, user_model_to_retrieve.id)

        expected_response = {
            "data": {
                "username": "josh",
                "first_name": "Josh",
                "last_name": "Maxwell",
                "email": "josh@example.com",
            }
        }

        response.data["data"].pop("date_joined")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_cant_retrive_user_that_does_not_exists(self):
        UserFactory(
            username="josh",
            email="josh@example.com",
            first_name="Josh",
            last_name="Maxwell",
        )

        user_model = User.objects.last()

        request = self.factory.get("api/users/10000")
        force_authenticate(request, user_model)

        with self.assertNumQueries(1):
            response = self.get_view(request, 10000)

        expected_response = {
            "errors": {
                "display_error": "User does not exists.",
                "internal_error_code": 40401,
            }
        }

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, expected_response)
