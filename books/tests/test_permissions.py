from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from books.tests.base import AuthenticatedAPITestCase

BOOKS_URL = reverse("books:book-list")
User = get_user_model()


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class BookPermissionsTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.staff_user = self.get_staff_user()
        self.normal_user = self.get_normal_user()
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="SOFT",
            inventory=3,
            daily_fee="1.99",
        )

    def test_unauthenticated_user_can_list_books(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_create_book(self):
        res = self.client.post(
            BOOKS_URL,
            {
                "title": "New Book",
                "author": "Someone",
                "cover": "HARD",
                "inventory": 5,
                "daily_fee": "2.00",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_staff_user_cannot_create_book(self):
        self.authenticate_normal_user()
        res = self.client.post(
            BOOKS_URL,
            {
                "title": "Another Book",
                "author": "Author",
                "cover": "HARD",
                "inventory": 2,
                "daily_fee": "3.00",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_staff_user_can_create_book(self):
        self.authenticate_staff_user()
        res = self.client.post(
            BOOKS_URL,
            {
                "title": "Allowed Book",
                "author": "Admin Author",
                "cover": "SOFT",
                "inventory": 1,
                "daily_fee": "4.50",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_authenticated_staff_user_can_update_book(self):
        self.authenticate_staff_user()
        url = detail_url(self.book.id)
        res = self.client.patch(url, {"inventory": 10}, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 10)

    def test_non_staff_user_cannot_update_book(self):
        self.authenticate_normal_user()
        url = detail_url(self.book.id)
        res = self.client.patch(url, {"inventory": 999}, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.book.refresh_from_db()
        self.assertNotEqual(self.book.inventory, 999)

    def test_non_staff_user_cannot_delete_book(self):
        self.authenticate_normal_user()
        url = detail_url(self.book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_user_can_delete_book(self):
        self.authenticate_staff_user()
        url = detail_url(self.book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
