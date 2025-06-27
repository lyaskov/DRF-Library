from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from books.models import Book
from library_service import settings


class Borrowing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} borrowed {self.book.title}"

    def clean(self):
        if self.expected_return_date < date.today():
            raise ValidationError("Expected return date cannot be in the past.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
