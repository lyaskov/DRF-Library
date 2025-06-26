from django.urls import reverse
from rest_framework.test import APITestCase

from users.models import User

REGISTER_URL = reverse("user_register")
ME_URL = reverse("user_me")
TOKEN_URL = reverse("token_obtain_pair")


class UserTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
