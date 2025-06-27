from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer


class BorrowingListView(generics.ListAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Borrowing.objects.filter(user=self.request.user)


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Borrowing.objects.filter(user=self.request.user)
