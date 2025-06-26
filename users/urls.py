from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import RegisterUserView, MeView

app_name = "user"

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="user_register"),
    path("me/", MeView.as_view(), name="user_me"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
