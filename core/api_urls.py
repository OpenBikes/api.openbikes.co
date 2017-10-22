from rest_framework.routers import DefaultRouter

from . import api_views


router = DefaultRouter()

router.register(r'cities', api_views.CityViewSet, base_name='users')

urlpatterns = router.urls
