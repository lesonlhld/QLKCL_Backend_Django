from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('country', views.CountryAPI, basename='country')
# router.register('city', views.CityAPI, basename='city')

urlpatterns = router.urls