from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentSerializer
from books.tests.base import AuthenticatedAPITestCase


PAYMENTS_URL = reverse("payments:payment-list")


def detail_url(payment_id):
    return reverse("payments:payment-detail", args=[payment_id])


class PaymentEndpointsTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()

        self.book = Book.objects.create(
            title="Payment Test Book",
            author="Author",
            cover="HARD",
            inventory=2,
            daily_fee="1.50",
        )

        self.authenticate_normal_user()
        self.user = self.get_normal_user()
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )
        self.payment1 = Payment.objects.create(
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://example.com/session1",
            session_id="sess_1",
            money_to_pay=10.0,
        )
        self.payment2 = Payment.objects.create(
            status=Payment.Status.PAID,
            type=Payment.Type.FINE,
            borrowing=self.borrowing,
            session_url="https://example.com/session2",
            session_id="sess_2",
            money_to_pay=5.0,
        )

        self.other_user = self.User.objects.create_user(
            email="other@example.com", password="otherpass"
        )
        self.other_borrowing = Borrowing.objects.create(
            user=self.other_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=5),
        )
        self.other_payment = Payment.objects.create(
            status=Payment.Status.PAID,
            type=Payment.Type.PAYMENT,
            borrowing=self.other_borrowing,
            session_url="https://example.com/other",
            session_id="sess_other",
            money_to_pay=20.0,
        )

    def test_user_can_list_only_their_payments(self):
        res = self.client.get(PAYMENTS_URL)
        payments = Payment.objects.filter(borrowing__user=self.user)
        serializer = PaymentSerializer(payments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_can_retrieve_their_payment_detail(self):
        url = detail_url(self.payment1.id)
        res = self.client.get(url)

        serializer = PaymentSerializer(self.payment1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_cannot_see_other_users_payment(self):
        url = detail_url(self.other_payment.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_see_all_payments(self):
        self.authenticate_staff_user()
        res = self.client.get(PAYMENTS_URL)

        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_can_retrieve_any_payment(self):
        self.authenticate_staff_user()
        url = detail_url(self.other_payment.id)
        res = self.client.get(url)

        serializer = PaymentSerializer(self.other_payment)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
