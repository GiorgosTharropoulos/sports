from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate
import faker

import community.views.user_views
from utils.test_utils import *


class UserTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.get_view = community.views.user_views.GetMeView.as_view()
        self.fake = faker.Faker()

        self.maxDiff = None

    def test_valid_request(self):
        user_model = UserFactory(
            username=self.fake.user_name(), email=self.fake.email()
        )

        request = self.factory.get("api/users/me/")
        force_authenticate(request, user_model)

        with self.assertNumQueries(0):
            response = self.get_view(request)

        expected_response = {
            "data": {
                "first_name": user_model.first_name,
                "last_name": user_model.last_name,
                "username": user_model.username,
                "email": user_model.email,
                "date_joined": user_model.date_joined.isoformat(),
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_user_must_be_authenticated_to_view_their_profile(self):
        request = self.factory.get("api/users/me/")

        with self.assertNumQueries(0):
            response = self.get_view(request)

        expected_response = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, expected_response)
