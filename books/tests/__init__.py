from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class BookAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.book = Book.objects.create(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            cover="SOFT",
            inventory=5,
            daily_fee="1.50",
        )

    def test_create_book_and_check_in_list(self):
        payload = {
            "title": "Inception of Code",
            "author": "Ada Lovelace",
            "cover": "HARD",
            "inventory": 3,
            "daily_fee": "2.99",
        }

        res = self.client.post(BOOKS_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title="Inception of Code").exists())

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertIn(res.data, serializer.data)

    def test_list_books(self):
        Book.objects.create(
            title="1984",
            author="George Orwell",
            cover="HARD",
            inventory=4,
            daily_fee="1.20",
        )

        res = self.client.get(BOOKS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        url = detail_url(self.book.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = BookSerializer(self.book)
        self.assertEqual(res.data, serializer.data)

    def test_update_book_partial(self):
        url = detail_url(self.book.id)
        payload = {"inventory": 10}

        res = self.client.patch(url, payload, format="json")
        self.book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book.inventory, 10)

    def test_delete_book(self):
        url = detail_url(self.book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
