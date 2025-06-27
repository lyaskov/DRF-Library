from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse

User = get_user_model()


class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        self.payload_staff_user = {
            "email": "admin@example.com",
            "password": "adminpass",
            "is_staff": True,
        }
        self.payload_normal_user = {
            "email": "user@example.com",
            "password": "userpass",
            "is_staff": False,
        }

    def get_normal_user(self):
        user, created = User.objects.get_or_create(
            email=self.payload_normal_user["email"],
            defaults={"is_staff": self.payload_normal_user["is_staff"]},
        )
        if created:
            user.set_password(self.payload_normal_user["password"])
            user.save()
        return user

    def get_staff_user(self):
        user, created = User.objects.get_or_create(
            email=self.payload_staff_user["email"],
            defaults={"is_staff": self.payload_staff_user["is_staff"]},
        )
        if created:
            user.set_password(self.payload_staff_user["password"])
            user.save()
        return user

    def authenticate(self, email, password):
        token_url = reverse("user:token_obtain_pair")
        response = self.client.post(
            token_url, {"email": email, "password": password}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZE=f"Bearer {token}")

    def authenticate_normal_user(self):
        user = self.get_normal_user()
        self.authenticate(
            email=self.payload_normal_user["email"],
            password=self.payload_normal_user["password"],
        )

    def authenticate_staff_user(self):
        user = self.get_staff_user()
        self.authenticate(
            email=self.payload_staff_user["email"],
            password=self.payload_staff_user["password"],
        )
