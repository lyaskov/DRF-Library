from datetime import timedelta, date

from django.urls import reverse
from rest_framework import status

from books.models import Book
from borrowings.models import Borrowing
from books.tests.base import AuthenticatedAPITestCase  # твой базовый класс
from borrowings.serializers import BorrowingReadSerializer

BORROWINGS_URL = reverse("borrowings:borrowing-list")


class BorrowingCreateTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.authenticate_normal_user()

        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover="HARD",
            inventory=3,
            daily_fee="1.50",
        )

    def test_create_borrowing_and_check_in_list(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": (date.today() + timedelta(days=5)).isoformat(),
        }

        res = self.client.post(BORROWINGS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res_list = self.client.get(BORROWINGS_URL)
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)

        borrowings = Borrowing.objects.select_related("book", "user").all()
        serializer = BorrowingReadSerializer(borrowings, many=True)

        self.assertEqual(res_list.data, serializer.data)

    def test_create_borrowing_fails_if_inventory_is_zero(self):
        self.book.inventory = 0
        self.book.save()

        payload = {
            "book": self.book.id,
            "expected_return_date": (date.today() + timedelta(days=3)).isoformat(),
        }

        res = self.client.post(BORROWINGS_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Book is not available", str(res.data))

    def test_create_borrowing_fails_with_past_return_date(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": (date.today() - timedelta(days=1)).isoformat(),
        }

        res = self.client.post(BORROWINGS_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Expected return date cannot be in the past", str(res.data))

    def test_user_is_automatically_attached(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": (date.today() + timedelta(days=5)).isoformat(),
        }

        res = self.client.post(BORROWINGS_URL, payload, format="json")
        self.assertEqual(res.status_code, 201)

        borrowing_id = res.data["id"]
        borrowing = Borrowing.objects.get(id=borrowing_id)

        self.assertEqual(borrowing.user.email, self.payload_normal_user["email"])
