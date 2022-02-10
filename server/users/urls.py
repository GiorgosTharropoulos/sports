from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LogInView, SignUpView

urlpatterns = [
    path("token/", LogInView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
]
