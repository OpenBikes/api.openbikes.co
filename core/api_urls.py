from rest_framework.routers import DefaultRouter

from . import api_views


router = DefaultRouter()

router.register(r'cities', api_views.CityViewSet, basename='cities')
router.register(r'countries', api_views.CountryViewSet, basename='countries')
router.register(r'providers', api_views.ProviderViewSet, basename='providers')

urlpatterns = router.urls
