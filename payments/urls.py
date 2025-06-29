from django.urls import path

from payments.views import PaymentListView, PaymentDetailView

app_name = "payments"

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
]
