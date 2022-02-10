from typing import Sequence
from uuid import UUID

from django.shortcuts import get_object_or_404

from community.models import Sport
from community.serializers import SportDTO, SportSerializer


class SportsService:
    def get_all(self) -> list[SportDTO]:
        sport_objs: Sequence[Sport] = Sport.objects.all()
        serializer = SportSerializer(instance=sport_objs, many=True)
        return serializer.data

    def get(self, pk: UUID) -> SportDTO:
        sport_obj: Sport = get_object_or_404(Sport, pk=pk)
        return SportSerializer(instance=sport_obj).data

    def create(self, data: dict[str, str]) -> SportDTO:
        serializer = SportSerializer(data=data)
        if serializer.is_valid(True):
            serializer.save()
        return serializer.data

    def delete(self, pk: UUID) -> None:
        sport: Sport = get_object_or_404(Sport, pk=pk)
        sport.delete()
        return

    def update(self, data: dict[str, str], pk: str | UUID) -> None:
        sport: Sport = get_object_or_404(Sport, pk=pk)
        serializer = SportSerializer(data=data, partial=True)
        serializer.update(sport, data)
        if not serializer.is_valid(True):
            return
        serializer.save()
        return None


sports_service = SportsService()
