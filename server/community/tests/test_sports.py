from uuid import uuid4
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from community.models import Sport


def create_sport(
    title="Football", description="The most popular sport in the world"
) -> Sport:
    return Sport.objects.create(title=title, description=description)


class SportTest(APITestCase):
    def test_sport_can_be_obtained(self):
        sport = create_sport()
        response = self.client.get(reverse("sport-detail", kwargs={"pk": sport.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(sport.id))
        self.assertEqual(response.data["title"], sport.title)
        self.assertEqual(response.data["description"], sport.description)
        self.assertEqual(response.data["slug"], sport.slug)

    def tets_sports_can_be_listed(self):
        sport1 = create_sport()
        sport2 = create_sport(
            title="Basketball", description="The 2nd most popular sport in the world"
        )

        response = self.client.get(reverse("sport-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sport_can_be_created(self):
        response = self.client.post(
            reverse("sport-list"),
            data={
                "title": "Footbal",
                "description": "The most popular sport in the world",
            },
        )

        sport: Sport = Sport.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], str(sport.id))
        self.assertEqual(response.data["title"], sport.title)
        self.assertEqual(response.data["description"], sport.description)
        self.assertEqual(response.data["slug"], sport.slug)

    def test_sport_can_be_updated(self):
        sport = create_sport()

        response = self.client.put(
            reverse("sport-detail", kwargs={"pk": sport.id}),
            data={"title": "Basketball", "description": "The 2nd most popular"},
        )

        updated: Sport = Sport.objects.get(pk=sport.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(updated.title, "Basketball")
        self.assertEqual(updated.description, "The 2nd most popular")
        self.assertEqual(updated.id, sport.id)

    def test_sport_can_be_partial_updated(self):
        sport = create_sport()

        response = self.client.put(
            reverse("sport-detail", kwargs={"pk": sport.id}),
            data={"title": "Basketball"},
        )

        updated: Sport = Sport.objects.get(pk=sport.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(updated.title, "Basketball")
        self.assertEqual(updated.description, "The most popular sport in the world")
        self.assertEqual(updated.id, sport.id)

    def test_sport_that_does_not_exist_cannot_be_updated(self):
        response = self.client.put(
            reverse("sport-detail", kwargs={"pk": uuid4()}),
            data={"title": "Basketball"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_sport_can_be_deleted(self):
        sport = create_sport()

        response = self.client.delete(reverse("sport-detail", kwargs={"pk": sport.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Sport.DoesNotExist):
            Sport.objects.get(pk=sport.id)

    def test_sport_that_does_not_exist_raises_404(self):
        response = self.client.delete(reverse("sport-detail", kwargs={"pk": uuid4()}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
