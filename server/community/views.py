from rest_framework.viewsets import ViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions

from community.serializers import SportSerializer

from .services import sports_service


class SportViewSet(ViewSet):
    serializer_class = SportSerializer

    def list(self, request: Request) -> Response:
        sports = sports_service.get_all()
        return Response(data=sports, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk=None) -> Response:
        sport = sports_service.get(pk)
        return Response(data=sport, status=status.HTTP_200_OK)

    def create(self, request: Request) -> Response:
        sport = sports_service.create(request.data)
        return Response(data=sport, status=status.HTTP_201_CREATED)

    def update(self, request: Request, pk=None) -> Response:
        sports_service.update(request.data, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request: Request, pk=None) -> Response:
        sports_service.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
