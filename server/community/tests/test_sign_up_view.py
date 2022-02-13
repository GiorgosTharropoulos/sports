from django.test import TestCase

from rest_framework.test import APIRequestFactory
import faker

import community.views.authorization_views
from utils.test_utils import *
from community.models import User


class UserTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.view = community.views.authorization_views.SignUpView.as_view()
        self.fake = faker.Faker()

        self.maxDiff = None

    def test_valid_sign_up(self):
        post_request_data = {
            "username": "user",
            "email": "example@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": True,
        }

        request = self.factory.post("/api/sign-up/", data=post_request_data)

        with self.assertNumQueries(15):
            self.view(request)

        user_model = User.objects.last()

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, EmailAddress.objects.count())
        self.assertEqual(user_model.username, "user")
        self.assertEqual(user_model.email, "example@example.com")

    def test_first_name_cant_be_longer_than_150_characters(self):
        post_request_data = {
            "username": "user",
            "email": "example@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": True,
            "first_name": self.fake.pystr(151, 151),
        }

        request = self.factory.post("/api/sing-up/", data=post_request_data)

        with self.assertNumQueries(0):
            response = self.view(request)

        expected_resp = {
            "errors": {
                "display_error": "",
                "field_errors": {
                    "first_name": ["First name can not exceed 150 characters."]
                },
            }
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(expected_resp, response.data)

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, EmailAddress.objects.count())

    def test_last_name_cant_be_longer_than_150_characters(self):
        post_request_data = {
            "username": "user",
            "email": "example@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": True,
            "last_name": self.fake.pystr(151, 151),
        }

        request = self.factory.post("/api/sing-up/", data=post_request_data)

        with self.assertNumQueries(0):
            response = self.view(request)

        expected_resp = {
            "errors": {
                "display_error": "",
                "field_errors": {
                    "last_name": ["Last name can not exceed 150 characters."]
                },
            }
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(expected_resp, response.data)

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, EmailAddress.objects.count())

    def test_username_cant_be_longer_than_150_characters(self):
        post_request_data = {
            "username": self.fake.pystr(151, 151),
            "email": "example@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": True,
        }

        request = self.factory.post("/api/sing-up/", data=post_request_data)

        with self.assertNumQueries(0):
            response = self.view(request)

        expected_resp = {
            "errors": {
                "display_error": "",
                "field_errors": {
                    "username": ["Username can not exceed 150 characters."]
                },
            }
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(expected_resp, response.data)

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, EmailAddress.objects.count())

    def test_username_must_start_with_a_letter_and_contain_only_letters_numbers_underscores(
        self,
    ):
        post_request_data = {
            "username": "23ksdlf",
            "email": "example@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": True,
        }

        request = self.factory.post("/api/sing-up/", data=post_request_data)

        with self.assertNumQueries(0):
            response = self.view(request)

        expected_resp = {
            "errors": {
                "display_error": "",
                "field_errors": {
                    "username": [
                        "Username must start with a letter, and contain only letters,"
                        " numbers, and underscores."
                    ]
                },
            }
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(expected_resp, response.data)

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, EmailAddress.objects.count())

    def test_must_enter_a_valid_email(self):
        post_request_data = {
            "username": "user",
            "email": "invalidemaili.",
            "password": "pAssw0rd!",
            "terms_of_service": True,
        }

        req = self.factory.post("/api/sign-up/", data=post_request_data)

        with self.assertNumQueries(0):
            res = self.view(req)

        expected_res = {
            "errors": {
                "display_error": "",
                "field_errors": {"email": ["Not a valid email address."]},
            }
        }

        self.assertEqual(res.status_code, 422)
        self.assertEqual(expected_res, res.data)

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, EmailAddress.objects.count())

    def test_must_provide_all_required_fields(self):
        post_request_data = {}

        request = self.factory.post("api/sign-up/", data=post_request_data)

        with self.assertNumQueries(0):
            response = self.view(request)

        expected_response = {
            "errors": {
                "display_error": "",
                "field_errors": {
                    "username": [
                        "Username can not exceed 150 characters.",
                        "Username must start with a letter, and contain only letters,"
                        " numbers, and underscores.",
                    ],
                    "email": ["Not a valid email address."],
                    "terms_of_service": ["Field may not be null."],
                },
            }
        }

        self.assertEqual(expected_response, response.data)
        self.assertEqual(response.status_code, 422)

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, EmailAddress.objects.count())

    def test_must_accept_terms_of_service(self):
        post_request_data = {
            "username": "user",
            "email": "example@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": False,
        }

        request = self.factory.post("api/sign-up/", data=post_request_data)

        with self.assertNumQueries(0):
            response = self.view(request)

        expected_response = {
            "errors": {
                "display_error": "You must accept the terms of service.",
                "internal_error_code": 42901,
            }
        }

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.data, expected_response)

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, EmailAddress.objects.count())

    def test_user_cannot_create_an_account_with_a_username_that_already_exists(self):
        UserFactory(username="aoeu", email="example@example.com")

        post_request_data = {
            "username": "aoeu",
            "email": "example2@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": True,
        }

        request = self.factory.post("/api/sing-up/", data=post_request_data)

        with self.assertNumQueries(1):
            response = self.view(request)

        expected_response = {
            "errors": {
                "display_error": "An account with this username already exists.",
                "internal_error_code": 40901,
            }
        }

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data, expected_response)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, EmailAddress.objects.count())

    def test_users_with_unverified_emails_get_deleted_by_new_signups(self):
        UserFactory(username="aoeu", email="example@example.com")

        post_request_data = {
            "username": "username",
            "email": "example@example.com",
            "password": "pAssw0rd!",
            "terms_of_service": True,
        }

        request = self.factory.post("/api/sing-up/", data=post_request_data)

        with self.assertNumQueries(17):
            response = self.view(request)

        self.assertEqual(response.status_code, 201)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, EmailAddress.objects.count())
