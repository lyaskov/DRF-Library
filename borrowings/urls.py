from django.urls import path

from borrowings.views import BorrowingListView, BorrowingDetailView

app_name = "borrowings"

urlpatterns = [
    path("borrowings/", BorrowingListView.as_view(), name="borrowing-list"),
    path(
        "borrowings/<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"
    ),
]
