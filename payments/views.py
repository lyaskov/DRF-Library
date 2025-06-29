from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.select_related("borrowing__user")
        if user.is_staff:
            return queryset.all()

        return queryset.filter(borrowing__user=user)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.select_related("borrowing__user")
        if user.is_staff:
            return queryset.all()
        return queryset.filter(borrowing__user=user)
