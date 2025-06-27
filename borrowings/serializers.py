from datetime import date

from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("book", "expected_return_date")

    def validate(self, attrs):
        book = attrs["book"]

        if book.inventory < 1:
            raise serializers.ValidationError("Book is not available for borrowing.")

        if attrs["expected_return_date"] < date.today():
            raise serializers.ValidationError(
                "Expected return date cannot be in the past."
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]

        book.inventory -= 1
        book.save()

        return Borrowing.objects.create(user=user, **validated_data)
