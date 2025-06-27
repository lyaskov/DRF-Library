from django.core.exceptions import ValidationError
from django.test import TestCase
from datetime import date, timedelta
from books.models import Book
from borrowings.models import Borrowing
from django.contrib.auth import get_user_model

User = get_user_model()


class BorrowingModelValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="123456"
        )
        self.book = Book.objects.create(
            title="Valid Book",
            author="Author",
            cover="SOFT",
            inventory=2,
            daily_fee="1.00",
        )

    def test_expected_return_date_cannot_be_in_the_past(self):
        borrowing = Borrowing(
            user=self.user,
            book=self.book,
            borrow_date=date.today(),
            expected_return_date=date.today() - timedelta(days=1),
        )
        with self.assertRaises(ValidationError) as ctx:
            borrowing.full_clean()
        self.assertIn("Expected return date cannot be in the past.", str(ctx.exception))
