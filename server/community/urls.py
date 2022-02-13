from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import SimpleRouter


from community.views.authorization_views import LogInView, SignUpView
from community.views.user_views import UserViewSet, GetMeView

router = SimpleRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("token/", LogInView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("users/me/", GetMeView.as_view(), name="me"),
]

urlpatterns += router.urls
