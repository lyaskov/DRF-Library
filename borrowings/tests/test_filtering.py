from datetime import date, timedelta

from django.urls import reverse

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer
from books.models import Book
from books.tests.base import AuthenticatedAPITestCase

BORROWINGS_URL = reverse("borrowings:borrowing-list")


class BorrowingFilterTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover="HARD",
            inventory=3,
            daily_fee="1.50",
        )
        self.normal_user = self.get_normal_user()
        self.staff_user = self.get_staff_user()

        self.borrowing1 = Borrowing.objects.create(
            user=self.normal_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
            actual_return_date=None,
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.normal_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=5),
            actual_return_date=date.today(),
        )
        self.borrowing3 = Borrowing.objects.create(
            user=self.staff_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=2),
        )

    def test_non_admin_sees_only_own_borrowings(self):
        self.authenticate_normal_user()
        res = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.filter(user=self.normal_user)
        serializer = BorrowingReadSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_admin_sees_all_borrowings(self):
        self.authenticate_staff_user()
        res = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingReadSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_filter_is_active_true(self):
        self.authenticate_normal_user()
        res = self.client.get(BORROWINGS_URL + "?is_active=true")

        borrowings = Borrowing.objects.filter(
            user=self.normal_user, actual_return_date__isnull=True
        )
        serializer = BorrowingReadSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_filter_is_active_false(self):
        self.authenticate_normal_user()
        res = self.client.get(BORROWINGS_URL + "?is_active=false")

        borrowings = Borrowing.objects.filter(
            user=self.normal_user, actual_return_date__isnull=False
        )
        serializer = BorrowingReadSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_admin_filter_by_user_id(self):
        self.authenticate_staff_user()
        res = self.client.get(BORROWINGS_URL + f"?user_id={self.normal_user.id}")

        borrowings = Borrowing.objects.filter(user=self.normal_user)
        serializer = BorrowingReadSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_non_admin_cannot_filter_by_user_id(self):
        self.authenticate_normal_user()
        res = self.client.get(BORROWINGS_URL + f"?user_id={self.staff_user.id}")

        borrowings = Borrowing.objects.filter(user=self.normal_user)
        serializer = BorrowingReadSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)
