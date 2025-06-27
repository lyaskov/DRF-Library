from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from borrowings.models import Borrowing
from books.models import Book

from books.tests.base import AuthenticatedAPITestCase

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def return_url(borrowing_id):
    return reverse("borrowings:borrowing-return-borrowing", args=[borrowing_id])


class ReturnBorrowingTest(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.authenticate_normal_user()
        self.book = Book.objects.create(
            title="Return Test",
            author="Tester",
            cover="HARD",
            inventory=3,
            daily_fee="1.00",
        )
        self.borrowing = Borrowing.objects.create(
            user=self.get_normal_user(),
            book=self.book,
            expected_return_date=(date.today() + timedelta(days=3)),
        )

    def test_successful_return(self):
        url = return_url(self.borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.borrowing.actual_return_date, date.today())
        self.assertEqual(self.book.inventory, 4)

    def test_cannot_return_twice(self):
        url = return_url(self.borrowing.id)
        self.client.post(url)  # First return

        res = self.client.post(url)  # Second return
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been returned", str(res.data))

    def test_user_cannot_return_not_their_borrowing(self):
        # Создаём другого обычного пользователя
        other_user_payload = {
            "email": "otheruser@example.com",
            "password": "otherpass",
            "is_staff": False,
        }
        other_user, _ = get_user_model().objects.get_or_create(
            email=other_user_payload["email"], defaults={"is_staff": False}
        )
        other_user.set_password(other_user_payload["password"])
        other_user.save()

        self.authenticate(
            email=other_user_payload["email"], password=other_user_payload["password"]
        )

        url = return_url(self.borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_return(self):
        self.client.credentials()
        url = return_url(self.borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
