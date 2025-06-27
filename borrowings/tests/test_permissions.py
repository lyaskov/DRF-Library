from books.tests.base import AuthenticatedAPITestCase
from books.models import Book
from borrowings.models import Borrowing
from django.urls import reverse
from datetime import timedelta, date
from rest_framework import status

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def detail_url(pk):
    return reverse("borrowings:borrowing-detail", args=[pk])


class BorrowingPermissionsTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.user = self.get_normal_user()
        self.other_user = self.get_staff_user()

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="SOFT",
            inventory=3,
            daily_fee="1.99",
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=5),
        )

        self.other_borrowing = Borrowing.objects.create(
            user=self.other_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=10),
        )

    def test_unauthenticated_user_cannot_access_borrowings(self):
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_get_other_user_borrowing(self):
        self.authenticate_normal_user()
        res = self.client.get(detail_url(self.other_borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_get_detail(self):
        res = self.client.get(detail_url(self.borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
