import base64
import json
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..models import User

PASSWORD = "pAssw0rd!"


class AuthenticationTest(APITestCase):
    def test_user_can_sign_upp(self):
        response = self.client.post(
            reverse("sign_up"),
            data={
                "username": "user@example.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
                "first_name": "User",
                "last_name": "Test",
            },
        )

        user: User = get_user_model().objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], user.id)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["first_name"], user.first_name)
        self.assertEqual(response.data["last_name"], user.last_name)

    def test_user_can_login(self):
        user: User = get_user_model().objects.create_user(
            username="test@test.com",
            first_name="test",
            last_name="user",
            password=PASSWORD,
        )

        response = self.client.post(
            reverse("login"), data={"username": user.username, "password": PASSWORD}
        )

        access = response.data["access"]
        _, access, _ = access.split(".")
        decoded_payload = base64.b64decode(f"{access}==")
        payload_json = json.loads(decoded_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertEqual(payload_json["id"], user.id)
        self.assertEqual(payload_json["username"], user.username)
        self.assertEqual(payload_json["first_name"], user.first_name)
        self.assertEqual(payload_json["last_name"], user.last_name)
