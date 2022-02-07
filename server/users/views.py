from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import TokenSerializer, UserSerializer
from .services import user_service


class LogInView(TokenObtainPairView):
    serializer_class = TokenSerializer


class SignUpView(APIView):
    serializer_class = UserSerializer

    def post(self, request: Request) -> Response:
        user = user_service.create(request.data)
        return Response(data=user, status=status.HTTP_201_CREATED)
