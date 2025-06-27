from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User

REGISTER_URL = reverse("user:user_register")
ME_URL = reverse("user:user_me")
TOKEN_URL = reverse("user:token_obtain_pair")


class UserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_payload = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }
        self.user = get_user_model().objects.create_user(
            email=self.user_payload["email"],
            password=self.user_payload["password"],
            first_name=self.user_payload["first_name"],
            last_name=self.user_payload["last_name"],
        )

    def test_register_user(self):
        payload = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "first_name": "New",
            "last_name": "User",
        }

        res = self.client.post(REGISTER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            get_user_model().objects.filter(email=payload["email"]).exists()
        )

    def test_login_and_get_token(self):
        payload = {
            "email": self.user_payload["email"],
            "password": self.user_payload["password"],
        }

        res = self.client.post(TOKEN_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_get_user_profile_authenticated(self):
        payload = {
            "email": self.user_payload["email"],
            "password": self.user_payload["password"],
        }
        token_res = self.client.post(TOKEN_URL, payload)
        token = token_res.data["access"]

        self.client.credentials(HTTP_AUTHORIZE=f"Bearer {token}")
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], payload["email"])

    def test_update_user_profile(self):
        payload = {
            "email": self.user_payload["email"],
            "password": self.user_payload["password"],
        }
        token_res = self.client.post(TOKEN_URL, payload)
        token = token_res.data["access"]

        self.client.credentials(HTTP_AUTHORIZE=f"Bearer {token}")
        payload = {"first_name": "Updated", "last_name": "Name"}
        res = self.client.patch(ME_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_get_user_profile_unauthenticated(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
