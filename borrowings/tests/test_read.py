from books.tests.base import AuthenticatedAPITestCase
from books.models import Book
from borrowings.models import Borrowing
from django.urls import reverse
from datetime import timedelta, date
from rest_framework import status

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def detail_url(pk):
    return reverse("borrowings:borrowing-detail", args=[pk])


class BorrowingReadTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.user = self.get_normal_user()
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

    def test_authenticated_user_can_list_own_borrowings(self):
        self.authenticate_normal_user()
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["book"]["title"], self.book.title)

    def test_authenticated_user_can_get_their_borrowing_detail(self):
        self.authenticate_normal_user()
        res = self.client.get(detail_url(self.borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["book"]["title"], self.book.title)
