from rest_framework import routers

from community.views import SportViewSet

router = routers.SimpleRouter()
router.register(r"sports", SportViewSet, basename="sport")
urlpatterns = router.urls
